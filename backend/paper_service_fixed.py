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
        section_id: str
    ) -> Dict[str, Any]:
        """生成论文章节"""
        try:
            logger.info(f"生成论文章节: 主题={topic}, 章节ID={section_id}")

            # 搜索相关文献
            literature = None
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

            # 构建提示
            prompt = f"""
            你是一位专业的学术论文撰写助手，现在需要你生成一篇论文的一个章节。
            
            论文主题：{topic}
            章节标题：{section_info.get('title', '未知章节')}
            
            章节内容要点：{content_points_json}
            
            相关文献：{literature_json}
            
            请生成这个章节的详细内容，内容应当：
            1. 学术风格严谨，用词专业
            2. 逻辑结构清晰，有论证和分析
            3. 适当引用相关文献支持论点
            4. 符合章节内容要点的要求
            5. 适当长度（约800-1200字）
            
            仅返回章节内容，不需要包含标题。
            """

            # 调用LLM生成章节内容
            response = await self.llm_service.generate_text(prompt)
            
            # 计算token使用情况
            token_usage = {
                "prompt_tokens": len(prompt) // 4,  # 粗略估计
                "completion_tokens": len(response) // 4,  # 粗略估计
                "total_tokens": (len(prompt) + len(response)) // 4  # 粗略估计
            }
            
            result = {
                "section_id": section_id,
                "title": section_info.get('title', '未知章节'),
                "content": response,
                "token_usage": token_usage
            }
            
            logger.info(f"章节生成完成: ID={section_id}, 标题={result['title']}")
            return result
            
        except Exception as e:
            logger.error(f"生成章节异常: {str(e)}")
            return {
                "section_id": section_id,
                "title": "生成失败",
                "content": f"生成内容时发生错误: {str(e)}",
                "token_usage": {"total_tokens": 0}
            }

    async def generate_full_paper(
        self,
        topic: str,
        outline: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成完整论文"""
        try:
            logger.info(f"生成完整论文: 主题={topic}")

            # 搜索相关文献
            literature = None
            try:
                # 搜索学术论文
                search_results = await self.academic_search_service.search_academic_papers(topic, limit=10)

                # 验证结果是否是可序列化的对象
                if not isinstance(search_results, dict):
                    logger.warning(f"搜索结果不是字典格式: {type(search_results)}, 将使用空字典代替")
                    literature = {"results": [], "total": 0, "query": topic}
                else:
                    # 创建一个可序列化的版本
                    literature = {
                        "results": [{
                            "title": p.get("title", ""),
                            "authors": p.get("authors", []),
                            "year": p.get("year", ""),
                            "abstract": p.get("abstract", "")[:300] if p.get("abstract") else "",  # 限制摘要长度
                            "url": p.get("url", ""),
                            "source": p.get("source", "")
                        } for p in search_results.get("results", [])[:5]],  # 只使用前5篇文章
                        "total": search_results.get("total", 0),
                        "query": search_results.get("query", topic)
                    }
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
                # 不传递literature对象，而是在每个section中重新搜索
                task = self.generate_paper_section(topic, outline, section_id)
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
            # 确保出错时也返回所有必需的字段
            return {
                "title": topic, 
                "error": str(e),
                "abstract": "",
                "keywords": [],
                "sections": {},
                "token_usage": 0
            }

    async def generate_abstract(
        self,
        topic: str,
        outline: Dict[str, Any],
        sections: Dict[str, Any]
    ) -> str:
        """生成论文摘要"""
        try:
            logger.info(f"生成论文摘要: 主题={topic}")
            
            # 提取各章节内容的前100个字符
            sections_preview = []
            for section_id, section_data in sections.items():
                sections_preview.append(f"{section_data.get('title')}: {section_data.get('content', '')[:100]}...")
            
            # 将章节预览转换为字符串
            sections_preview_text = "\n".join(sections_preview)
            
            # 构建提示
            prompt = f"""
            你是一位专业的学术论文撰写助手，现在需要你为一篇论文生成摘要。
            
            论文主题：{topic}
            论文标题：{outline.get('title', topic)}
            论文关键词：{', '.join(outline.get('keywords', []))}
            
            论文内容预览：
            {sections_preview_text}
            
            请生成一个简洁但全面的学术摘要，摘要应当：
            1. 包含研究目的、方法、主要发现和结论
            2. 格式规范，语言精炼
            3. 长度适中（约150-250字）
            
            仅返回摘要内容。
            """
            
            # 调用LLM生成摘要
            abstract = await self.llm_service.generate_text(prompt)
            
            logger.info(f"摘要生成完成: 长度={len(abstract)}")
            return abstract
            
        except Exception as e:
            logger.error(f"生成摘要异常: {str(e)}")
            return f"摘要生成失败: {str(e)}"


# 创建单例实例
paper_service = PaperService()
