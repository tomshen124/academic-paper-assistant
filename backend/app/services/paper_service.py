from typing import List, Dict, Any, Optional
import asyncio
import json
from app.core.logger import get_logger
from app.services.llm_service import llm_service
from app.services.academic_search_service import academic_search_service
from app.utils.json_utils import safe_dumps

# 创建日志器
logger = get_logger("paper_service")

class PaperService:
    """论文生成服务"""

    def __init__(self):
        """初始化论文生成服务"""
        self.llm_service = llm_service
        self.academic_search_service = academic_search_service
        logger.info("论文生成服务初始化完成")

    async def generate_paper_section(
        self,
        topic: str,
        outline: Dict[str, Any],
        section_id: str,
        literature: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """生成论文章节"""
        try:
            logger.info(f"生成论文章节: 主题={topic}, 章节ID={section_id}")

            # 如果没有提供文献，则搜索相关文献
            if not literature:
                try:
                    # 获取章节标题
                    section_title = None
                    for section in outline.get("sections", []):
                        if section.get("id") == section_id:
                            section_title = section.get("title")
                            break
                        for subsection in section.get("subsections", []):
                            if subsection.get("id") == section_id:
                                section_title = subsection.get("title")
                                break

                    # 构建搜索查询
                    search_query = f"{topic} {section_title}" if section_title else topic

                    # 搜索相关文献
                    literature = await self.academic_search_service.search_academic_papers(search_query, limit=3)

                    # 验证literature是否是可序列化的对象
                    if not isinstance(literature, dict):
                        logger.warning(f"搜索结果不是字典格式: {type(literature)}, 将使用空字典代替")
                        literature = {"results": [], "total": 0, "query": search_query}
                except Exception as e:
                    logger.error(f"搜索相关文献失败: {str(e)}")
                    literature = {"results": [], "total": 0, "query": topic}

            # 找到对应的章节信息
            section_info = None
            for section in outline.get("sections", []):
                if section.get("id") == section_id:
                    section_info = section
                    break
                for subsection in section.get("subsections", []):
                    if subsection.get("id") == section_id:
                        section_info = subsection
                        break

            if not section_info:
                logger.error(f"未找到章节信息: {section_id}")
                return {"content": "未找到章节信息"}

            # 构建提示
            # 尝试将literature转换为JSON字符串
            literature_json = safe_dumps(literature, ensure_ascii=False, max_length=1500, default_value="[]")
            logger.info(f"成功序列化相关文献")

            # 尝试将内容要点转换为JSON字符串
            content_points_json = safe_dumps(section_info.get('content_points', []), ensure_ascii=False, default_value="[]")
            logger.info(f"成功序列化内容要点")

            system_prompt = f"""你是一个学术论文写作专家。你的任务是为以下论文主题和章节生成高质量的学术内容。

论文主题: {topic}
论文标题: {outline.get('title', topic)}
章节ID: {section_id}
章节标题: {section_info.get('title', '')}
章节目的: {section_info.get('purpose', '')}
内容要点: {content_points_json}
预期长度: {section_info.get('expected_length', '')}

相关文献:
{literature_json}

请生成该章节的完整内容，要求:
1. 内容符合学术写作规范，语言专业、准确
2. 适当引用相关文献，使用(作者, 年份)的引用格式
3. 内容要点全面覆盖，逻辑清晰
4. 长度符合预期要求
5. 如有必要，可以包含小标题划分内容
6. 如果是方法或结果章节，可以描述适当的图表（但不需要实际创建图表）

请直接返回章节内容，不需要额外的解释或格式。"""

            # 调用LLM
            response = await self.llm_service.acompletion(
                messages=[{"role": "system", "content": system_prompt}],
                max_tokens=2500,
                temperature=0.4
            )

            # 获取响应内容
            content = response.choices[0].message.content

            # 记录token使用
            token_usage = response.usage
            logger.info(
                f"章节生成完成: ID={section_id}, "
                f"输入tokens={token_usage.prompt_tokens}, "
                f"输出tokens={token_usage.completion_tokens}, "
                f"总tokens={token_usage.total_tokens}"
            )

            return {
                "section_id": section_id,
                "title": section_info.get("title", ""),
                "content": content,
                "token_usage": {
                    "prompt_tokens": token_usage.prompt_tokens,
                    "completion_tokens": token_usage.completion_tokens,
                    "total_tokens": token_usage.total_tokens
                }
            }

        except Exception as e:
            logger.error(f"生成论文章节失败: {str(e)}")
            return {
                "section_id": section_id,
                "title": section_info.get("title", "") if section_info else "",
                "content": f"生成失败: {str(e)}",
                "token_usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            }

    async def generate_full_paper(
        self,
        topic: str,
        outline: Dict[str, Any],
        literature: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """生成完整论文"""
        try:
            logger.info(f"生成完整论文: 主题={topic}")

            # 如果没有提供文献，则搜索相关文献
            if not literature:
                try:
                    literature = await self.academic_search_service.search_academic_papers(topic, limit=10)

                    # 验证literature是否是可序列化的对象
                    if not isinstance(literature, dict):
                        logger.warning(f"搜索结果不是字典格式: {type(literature)}, 将使用空字典代替")
                        literature = {"results": [], "total": 0, "query": topic}
                except Exception as e:
                    logger.error(f"搜索相关文献失败: {str(e)}")
                    literature = {"results": [], "total": 0, "query": topic}

            # 获取所有章节ID
            section_ids = []
            for section in outline.get("sections", []):
                section_ids.append(section.get("id"))
                for subsection in section.get("subsections", []):
                    section_ids.append(subsection.get("id"))

            # 并行生成所有章节
            tasks = []
            for section_id in section_ids:
                task = self.generate_paper_section(topic, outline, section_id, literature)
                tasks.append(task)

            # 等待所有任务完成
            sections_results = await asyncio.gather(*tasks, return_exceptions=True)

            # 处理结果
            sections = {}
            total_tokens = 0

            for result in sections_results:
                if isinstance(result, Exception):
                    logger.error(f"章节生成异常: {str(result)}")
                    continue

                section_id = result.get("section_id")
                sections[section_id] = {
                    "title": result.get("title", ""),
                    "content": result.get("content", "")
                }

                # 累计token使用
                token_usage = result.get("token_usage", {})
                total_tokens += token_usage.get("total_tokens", 0)

            # 生成摘要
            abstract = await self.generate_abstract(topic, outline, sections)

            # 构建完整论文
            paper = {
                "title": outline.get("title", topic),
                "abstract": abstract,
                "keywords": outline.get("keywords", []),
                "sections": sections,
                "token_usage": total_tokens
            }

            logger.info(f"论文生成完成: 标题={paper['title']}, 总tokens={total_tokens}")
            return paper

        except Exception as e:
            logger.error(f"生成完整论文失败: {str(e)}")
            return {"title": topic, "error": str(e)}

    async def generate_abstract(
        self,
        topic: str,
        outline: Dict[str, Any],
        sections: Dict[str, Dict[str, Any]]
    ) -> str:
        """生成论文摘要"""
        try:
            logger.info(f"生成论文摘要: 主题={topic}")

            # 提取各章节的前100个字符作为摘要输入
            sections_preview = {}
            for section_id, section in sections.items():
                content = section.get("content", "")
                preview = content[:200] + "..." if len(content) > 200 else content
                sections_preview[section_id] = {
                    "title": section.get("title", ""),
                    "preview": preview
                }

            # 尝试将sections_preview转换为JSON字符串
            sections_preview_json = safe_dumps(sections_preview, ensure_ascii=False, max_length=1500, default_value="{}")
            logger.info(f"成功序列化章节概览")

            # 构建提示
            system_prompt = f"""你是一个学术论文摘要生成专家。你的任务是为以下论文生成一个简洁、全面的摘要。

论文主题: {topic}
论文标题: {outline.get('title', topic)}
论文章节概览: {sections_preview_json}

请生成一个200-300字的学术摘要，要求:
1. 简明扼要地概述研究目的、方法、结果和结论
2. 突出研究的创新点和贡献
3. 语言专业、准确，符合学术写作规范
4. 不包含引用

请直接返回摘要内容，不需要额外的解释或格式。"""

            # 调用LLM
            response = await self.llm_service.acompletion(
                messages=[{"role": "system", "content": system_prompt}],
                max_tokens=500,
                temperature=0.3
            )

            # 获取响应内容
            abstract = response.choices[0].message.content

            logger.info(f"摘要生成完成: 长度={len(abstract)}")
            return abstract

        except Exception as e:
            logger.error(f"生成摘要失败: {str(e)}")
            return "摘要生成失败"

    async def improve_section(
        self,
        topic: str,
        section_id: str,
        current_content: str,
        feedback: str,
        literature: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """改进论文章节"""
        try:
            logger.info(f"改进论文章节: 主题={topic}, 章节ID={section_id}, 反馈={feedback}")

            # 如果没有提供文献，则搜索相关文献
            if not literature:
                try:
                    literature = await self.academic_search_service.search_academic_papers(topic, limit=3)

                    # 验证literature是否是可序列化的对象
                    if not isinstance(literature, dict):
                        logger.warning(f"搜索结果不是字典格式: {type(literature)}, 将使用空字典代替")
                        literature = {"results": [], "total": 0, "query": topic}
                except Exception as e:
                    logger.error(f"搜索相关文献失败: {str(e)}")
                    literature = {"results": [], "total": 0, "query": topic}

            # 尝试将literature转换为JSON字符串
            literature_json = safe_dumps(literature, ensure_ascii=False, max_length=1000, default_value="[]")
            logger.info(f"成功序列化相关文献")

            # 构建提示
            system_prompt = f"""你是一个学术论文编辑专家。你的任务是根据反馈改进以下论文章节。

论文主题: {topic}
章节ID: {section_id}
当前内容:
{current_content}

用户反馈:
{feedback}

相关文献:
{literature_json}

请根据用户的反馈改进章节内容，要求:
1. 保持学术写作风格和专业性
2. 针对性地解决用户提出的问题
3. 适当引用相关文献支持论点
4. 保持内容的逻辑性和连贯性

请直接返回改进后的章节内容，不需要额外的解释或格式。"""

            # 调用LLM
            response = await self.llm_service.acompletion(
                messages=[{"role": "system", "content": system_prompt}],
                max_tokens=2500,
                temperature=0.3
            )

            # 获取响应内容
            improved_content = response.choices[0].message.content

            # 记录token使用
            token_usage = response.usage
            logger.info(
                f"章节改进完成: ID={section_id}, "
                f"输入tokens={token_usage.prompt_tokens}, "
                f"输出tokens={token_usage.completion_tokens}, "
                f"总tokens={token_usage.total_tokens}"
            )

            return {
                "section_id": section_id,
                "improved_content": improved_content,
                "token_usage": {
                    "prompt_tokens": token_usage.prompt_tokens,
                    "completion_tokens": token_usage.completion_tokens,
                    "total_tokens": token_usage.total_tokens
                }
            }

        except Exception as e:
            logger.error(f"改进论文章节失败: {str(e)}")
            return {"section_id": section_id, "error": str(e)}

# 创建全局论文服务实例
paper_service = PaperService()
