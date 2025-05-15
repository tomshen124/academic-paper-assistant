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
        # 使用全局服务实例
        logger.info("论文生成服务初始化完成")

    async def generate_paper_section(
        self,
        topic: str,
        outline: Dict[str, Any],
        section_id: str,
        literature: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """生成论文章节"""
        try:
            logger.info(f"生成论文章节: 主题={topic}, 章节ID={section_id}")

            # 处理相关文献
            literature_data = None
            try:
                # 如果传入了文献，直接使用
                if literature:
                    logger.info(f"使用传入的文献数据，共{len(literature)}篇")
                    literature_data = {
                        "results": literature,
                        "total": len(literature),
                        "query": topic
                    }
                else:
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
                    logger.info(f"搜索相关文献: {search_query}")
                    try:
                        # 优先使用arXiv搜索，不需要API密钥
                        literature_data = await academic_search_service.search_academic_papers(
                            query=search_query,
                            limit=3,
                            sources=["arxiv"]  # 明确指定使用arXiv
                        )
                        # 确保返回的是字典类型
                        if not isinstance(literature_data, dict):
                            logger.warning(f"搜索结果不是字典类型: {type(literature_data)}, 将使用空字典代替")
                            literature_data = {"results": [], "total": 0, "query": search_query}
                    except Exception as e:
                        logger.error(f"搜索相关文献失败: {str(e)}")
                        literature_data = {"results": [], "total": 0, "query": search_query}

                # 验证literature是否是可序列化的对象
                if literature_data is None or not isinstance(literature_data, dict):
                    logger.warning(f"搜索结果为None或不是字典格式: {type(literature_data)}, 将使用空字典代替")
                    literature_data = {"results": [], "total": 0, "query": search_query if 'search_query' in locals() else topic}
                else:
                    # 创建一个新的可序列化字典，避免引用可能包含不可序列化对象的原始字典
                    serializable_data = {
                        "results": [],
                        "total": literature_data.get("total", 0),
                        "query": literature_data.get("query", search_query if 'search_query' in locals() else topic)
                    }

                    # 确保结果列表中的每个论文对象都是可序列化的
                    results = literature_data.get("results", [])
                    if results and isinstance(results, list):
                        for paper in results[:3]:  # 只使用前3篇文章
                            if not isinstance(paper, dict):
                                logger.warning(f"论文对象不是字典格式: {type(paper)}, 跳过")
                                continue

                            serializable_paper = {
                                "title": str(paper.get("title", "")) if paper.get("title") is not None else "",
                                "authors": paper.get("authors", []) if isinstance(paper.get("authors"), list) else [],
                                "year": str(paper.get("year", "")) if paper.get("year") is not None else "",
                                "abstract": str(paper.get("abstract", ""))[:300] if paper.get("abstract") is not None else "",  # 限制摘要长度
                                "url": str(paper.get("url", "")) if paper.get("url") is not None else "",
                                "source": str(paper.get("source", "arxiv")) if paper.get("source") is not None else "arxiv"
                            }
                            serializable_data["results"].append(serializable_paper)
                    else:
                        logger.warning(f"搜索结果列表为空或不是列表类型: {type(results)}")

                    literature_data = serializable_data
            except Exception as e:
                logger.error(f"处理相关文献失败: {str(e)}")
                literature_data = {"results": [], "total": 0, "query": topic}

            # 找到对应的章节信息
            section_info = None
            # 检查是否是子章节ID（包含'-'符号）
            if '-' in section_id:
                # 解析父章节ID和子章节ID
                parent_id, sub_id = section_id.split('-', 1)
                # 先找到父章节
                for section in outline.get("sections", []):
                    if section.get("id") == parent_id:
                        # 在父章节的子章节中查找
                        subsections = section.get("subsections", [])
                        if not subsections:
                            logger.warning(f"父章节 {parent_id} 没有子章节")
                            # 创建一个基本的章节信息
                            section_info = {
                                "id": section_id,
                                "title": f"子章节 {sub_id}",
                                "content_points": ["自动生成的内容"]
                            }
                            break

                        for subsection in subsections:
                            if subsection.get("id") == section_id:
                                section_info = subsection
                                break

                        # 如果没找到匹配的子章节ID，但找到了父章节，创建一个基本的子章节信息
                        if not section_info:
                            logger.warning(f"在父章节 {parent_id} 中未找到子章节 {section_id}")
                            section_info = {
                                "id": section_id,
                                "title": f"子章节 {sub_id}",
                                "content_points": ["自动生成的内容"]
                            }
                        break
            else:
                # 常规章节查找
                for section in outline.get("sections", []):
                    if section.get("id") == section_id:
                        section_info = section
                        break
                    # 也在子章节中查找
                    for subsection in section.get("subsections", []):
                        if subsection.get("id") == section_id:
                            section_info = subsection
                            break
                    if section_info:
                        break

            # 如果仍然没有找到章节信息，创建一个基本的章节信息
            if not section_info:
                logger.error(f"未找到章节信息: {section_id}")
                section_info = {
                    "id": section_id,
                    "title": f"章节 {section_id}",
                    "content_points": ["自动生成的内容"]
                }

            # 构建提示
            # 尝试将literature_data转换为JSON字符串
            literature_json = safe_dumps(literature_data, ensure_ascii=False, max_length=1500, default_value="[]")
            logger.info(f"成功序列化相关文献")

            # 确保section_info有content_points字段
            if 'content_points' not in section_info or not section_info['content_points']:
                section_info['content_points'] = ["自动生成的内容"]

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

            # 使用智能体协调器生成章节内容
            from app.services.agent_service import agent_coordinator

            logger.info("使用智能体协调器生成章节内容")

            # 使用预设工作流
            workflow_result = await agent_coordinator.execute_predefined_workflow(
                "paper_section_generation",
                {
                    "topic": topic,
                    "outline": outline,
                    "section_id": section_id,
                    "papers": literature_data.get("results", []) if literature_data else []
                }
            )

            # 检查工作流执行结果
            if "error" in workflow_result:
                logger.error(f"工作流执行失败: {workflow_result['error']}")
                # 如果工作流执行失败，回退到原始方法
                response = await llm_service.generate_text(prompt, agent_type="writing")
            else:
                # 从最终上下文中获取章节内容
                final_context = workflow_result.get("final_context", {})

                # 尝试从不同的可能位置获取章节内容
                if "section_content" in final_context:
                    response = final_context["section_content"]
                elif "polish_section_result" in final_context and "content" in final_context["polish_section_result"]:
                    response = final_context["polish_section_result"]["content"]
                elif "write_section_result" in final_context and "content" in final_context["write_section_result"]:
                    response = final_context["write_section_result"]["content"]
                else:
                    logger.error("无法从工作流结果中获取章节内容，使用备用方法")
                    # 如果无法获取章节内容，回退到原始方法
                    response = await llm_service.generate_text(prompt, agent_type="writing")

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
        outline: Dict[str, Any],
        literature: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """生成完整论文"""
        try:
            logger.info(f"生成完整论文: 主题={topic}")

            # 处理相关文献
            literature_data = None
            try:
                # 如果传入了文献，直接使用
                if literature:
                    logger.info(f"使用传入的文献数据，共{len(literature)}篇")
                    literature_data = {
                        "results": literature,
                        "total": len(literature),
                        "query": topic
                    }
                else:
                    # 搜索学术论文
                    logger.info(f"搜索相关文献: {topic}")
                    try:
                        # 优先使用arXiv搜索，不需要API密钥
                        search_results = await academic_search_service.search_academic_papers(
                            query=topic,
                            limit=10,
                            sources=["arxiv"]  # 明确指定使用arXiv
                        )
                        # 确保返回的是字典类型
                        if not isinstance(search_results, dict):
                            logger.warning(f"搜索结果不是字典类型: {type(search_results)}, 将使用空字典代替")
                            search_results = {"results": [], "total": 0, "query": topic}
                    except Exception as e:
                        logger.error(f"搜索相关文献失败: {str(e)}")
                        search_results = {"results": [], "total": 0, "query": topic}

                    # 验证结果是否是可序列化的对象
                    if search_results is None or not isinstance(search_results, dict):
                        logger.warning(f"搜索结果为None或不是字典格式: {type(search_results)}, 将使用空字典代替")
                        literature_data = {"results": [], "total": 0, "query": topic}
                    else:
                        # 创建一个新的可序列化字典，避免引用可能包含不可序列化对象的原始字典
                        literature_data = {
                            "results": [],
                            "total": search_results.get("total", 0),
                            "query": search_results.get("query", topic)
                        }

                        # 确保结果列表中的每个论文对象都是可序列化的
                        results = search_results.get("results", [])
                        if results and isinstance(results, list):
                            for paper in results[:10]:  # 只使用前10篇文章
                                if not isinstance(paper, dict):
                                    logger.warning(f"论文对象不是字典格式: {type(paper)}, 跳过")
                                    continue

                                serializable_paper = {
                                    "title": str(paper.get("title", "")) if paper.get("title") is not None else "",
                                    "authors": paper.get("authors", []) if isinstance(paper.get("authors"), list) else [],
                                    "year": str(paper.get("year", "")) if paper.get("year") is not None else "",
                                    "abstract": str(paper.get("abstract", ""))[:300] if paper.get("abstract") is not None else "",  # 限制摘要长度
                                    "url": str(paper.get("url", "")) if paper.get("url") is not None else "",
                                    "source": str(paper.get("source", "arxiv")) if paper.get("source") is not None else "arxiv"
                                }
                                literature_data["results"].append(serializable_paper)
                        else:
                            logger.warning(f"搜索结果列表为空或不是列表类型: {type(results)}")
            except Exception as e:
                logger.error(f"处理相关文献失败: {str(e)}")
                literature_data = {"results": [], "total": 0, "query": topic}

            # 获取所有章节ID
            section_ids = []
            for section in outline.get("sections", []):
                section_ids.append(section.get("id"))
                for subsection in section.get("subsections", []):
                    section_ids.append(subsection.get("id"))

            # 并行生成所有章节
            tasks = []
            for section_id in section_ids:
                # 确保section_id是有效的
                if not section_id:
                    logger.warning(f"跳过无效的章节ID: {section_id}")
                    continue

                # 传递literature_data对象
                literature_results = []
                if literature_data and isinstance(literature_data, dict):
                    results = literature_data.get("results", [])
                    if isinstance(results, list):
                        literature_results = results

                task = self.generate_paper_section(
                    topic=topic,
                    outline=outline,
                    section_id=section_id,
                    literature=literature_results
                )
                tasks.append(task)

            # 如果没有有效的任务，返回空结果
            if not tasks:
                logger.warning("没有有效的章节ID，无法生成论文")
                return {
                    "title": outline.get("title", topic),
                    "abstract": "无法生成论文，没有有效的章节",
                    "keywords": outline.get("keywords", []),
                    "sections": {},
                    "token_usage": 0
                }

            # 等待所有任务完成
            sections_results = await asyncio.gather(*tasks, return_exceptions=True)

            # 处理结果
            sections = {}
            total_tokens = 0

            for result in sections_results:
                if isinstance(result, Exception):
                    logger.error(f"章节生成异常: {str(result)}")
                    continue

                if not isinstance(result, dict):
                    logger.error(f"章节生成结果不是字典类型: {type(result)}")
                    continue

                section_id = result.get("section_id")
                if not section_id:
                    logger.error("章节生成结果缺少section_id字段")
                    continue

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

            # 调用LLM生成摘要，使用写作智能体
            abstract = await llm_service.generate_text(prompt, agent_type="writing")

            logger.info(f"摘要生成完成: 长度={len(abstract)}")
            return abstract

        except Exception as e:
            logger.error(f"生成摘要异常: {str(e)}")
            return f"摘要生成失败: {str(e)}"

    async def improve_section(
        self,
        topic: str,
        section_id: str,
        current_content: str,
        feedback: str,
        literature: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """改进论文章节"""
        try:
            logger.info(f"改进论文章节: 主题={topic}, 章节ID={section_id}, 反馈={feedback}")

            # 处理相关文献
            literature_data = None
            try:
                # 如果传入了文献，直接使用
                if literature:
                    logger.info(f"使用传入的文献数据，共{len(literature)}篇")
                    literature_data = {
                        "results": literature,
                        "total": len(literature),
                        "query": topic
                    }
                else:
                    # 搜索相关文献
                    logger.info(f"搜索相关文献: {topic}")
                    try:
                        # 优先使用arXiv搜索，不需要API密钥
                        literature_data = await academic_search_service.search_academic_papers(
                            query=topic,
                            limit=3,
                            sources=["arxiv"]  # 明确指定使用arXiv
                        )
                        # 确保返回的是字典类型
                        if not isinstance(literature_data, dict):
                            logger.warning(f"搜索结果不是字典类型: {type(literature_data)}, 将使用空字典代替")
                            literature_data = {"results": [], "total": 0, "query": topic}
                    except Exception as e:
                        logger.error(f"搜索相关文献失败: {str(e)}")
                        literature_data = {"results": [], "total": 0, "query": topic}

                # 验证literature是否是可序列化的对象
                if literature_data is None or not isinstance(literature_data, dict):
                    logger.warning(f"搜索结果为None或不是字典格式: {type(literature_data)}, 将使用空字典代替")
                    literature_data = {"results": [], "total": 0, "query": topic}
                else:
                    # 创建一个新的可序列化字典，避免引用可能包含不可序列化对象的原始字典
                    serializable_data = {
                        "results": [],
                        "total": literature_data.get("total", 0),
                        "query": literature_data.get("query", topic)
                    }

                    # 确保结果列表中的每个论文对象都是可序列化的
                    results = literature_data.get("results", [])
                    if results and isinstance(results, list):
                        for paper in results[:3]:  # 只使用前3篇文章
                            if not isinstance(paper, dict):
                                logger.warning(f"论文对象不是字典格式: {type(paper)}, 跳过")
                                continue

                            serializable_paper = {
                                "title": str(paper.get("title", "")) if paper.get("title") is not None else "",
                                "authors": paper.get("authors", []) if isinstance(paper.get("authors"), list) else [],
                                "year": str(paper.get("year", "")) if paper.get("year") is not None else "",
                                "abstract": str(paper.get("abstract", ""))[:300] if paper.get("abstract") is not None else "",  # 限制摘要长度
                                "url": str(paper.get("url", "")) if paper.get("url") is not None else "",
                                "source": str(paper.get("source", "arxiv")) if paper.get("source") is not None else "arxiv"
                            }
                            serializable_data["results"].append(serializable_paper)
                    else:
                        logger.warning(f"搜索结果列表为空或不是列表类型: {type(results)}")

                    literature_data = serializable_data
            except Exception as e:
                logger.error(f"处理相关文献失败: {str(e)}")
                literature_data = {"results": [], "total": 0, "query": topic}

            # 尝试将literature_data转换为JSON字符串
            literature_json = safe_dumps(literature_data, ensure_ascii=False, max_length=1500, default_value="[]")
            logger.info(f"成功序列化相关文献")

            # 构建提示
            prompt = f"""
            你是一位专业的学术论文撰写助手，现在需要你改进一篇论文的章节内容。

            论文主题：{topic}
            章节ID：{section_id}

            当前内容：
            {current_content}

            用户反馈：
            {feedback}

            相关文献：{literature_json}

            请根据用户的反馈和相关文献，改进这个章节的内容。改进后的内容应当：
            1. 解决用户反馈中提出的问题
            2. 保持学术风格严谨，用词专业
            3. 确保逻辑结构清晰，有论证和分析
            4. 适当引用相关文献支持论点
            5. 保持适当长度（约800-1200字）

            仅返回改进后的完整章节内容，不需要包含标题或解释。
            """

            # 使用智能体协调器改进章节内容
            from app.services.agent_service import agent_coordinator

            logger.info("使用智能体协调器改进章节内容")

            # 使用预设工作流
            workflow_result = await agent_coordinator.execute_predefined_workflow(
                "paper_section_generation",
                {
                    "topic": topic,
                    "section_id": section_id,
                    "content": current_content,
                    "feedback": feedback,
                    "papers": literature_data.get("results", []) if literature_data else []
                }
            )

            # 检查工作流执行结果
            if "error" in workflow_result:
                logger.error(f"工作流执行失败: {workflow_result['error']}")
                # 如果工作流执行失败，回退到原始方法
                improved_content = await llm_service.generate_text(prompt, agent_type="writing")
            else:
                # 从最终上下文中获取改进后的章节内容
                final_context = workflow_result.get("final_context", {})

                # 尝试从不同的可能位置获取章节内容
                if "improved_content" in final_context:
                    improved_content = final_context["improved_content"]
                elif "polish_section_result" in final_context and "content" in final_context["polish_section_result"]:
                    improved_content = final_context["polish_section_result"]["content"]
                else:
                    logger.error("无法从工作流结果中获取改进后的章节内容，使用备用方法")
                    # 如果无法获取章节内容，回退到原始方法
                    improved_content = await llm_service.generate_text(prompt, agent_type="writing")

            # 计算token使用情况
            token_usage = {
                "prompt_tokens": len(prompt) // 4,  # 粗略估计
                "completion_tokens": len(improved_content) // 4,  # 粗略估计
                "total_tokens": (len(prompt) + len(improved_content)) // 4  # 粗略估计
            }

            result = {
                "section_id": section_id,
                "improved_content": improved_content,
                "token_usage": token_usage
            }

            logger.info(f"章节改进完成: ID={section_id}")
            return result

        except Exception as e:
            logger.error(f"改进章节异常: {str(e)}")
            return {
                "section_id": section_id,
                "improved_content": f"改进内容时发生错误: {str(e)}",
                "token_usage": {"total_tokens": 0}
            }


# 创建单例实例
paper_service = PaperService()
