"""
MCP (Model Context Protocol) 服务适配器
将现有服务与MCP集成
"""

from typing import Dict, List, Any, Optional, Callable
import asyncio
from app.services.mcp_client import mcp_client
from app.services.topic_service import topic_service
from app.services.outline_service import outline_service
from app.services.paper_service import paper_service
from app.services.citation_service import citation_service
from app.services.academic_search_service import academic_search_service
from app.core.logger import get_logger

logger = get_logger("mcp_adapter")

class MCPAdapter:
    """MCP服务适配器"""

    def __init__(self):
        """初始化MCP适配器"""
        self.mcp_client = mcp_client
        logger.info("MCP适配器初始化完成")

    async def initialize(self):
        """初始化MCP适配器"""
        if not self.mcp_client.enabled:
            logger.info("MCP未启用，跳过初始化")
            return False

        try:
            # 连接到MCP服务器
            if hasattr(self.mcp_client, 'connect'):
                connected = await self.mcp_client.connect()
                if not connected:
                    logger.error("连接MCP服务器失败")
                    return False

                # 注册工具
                await self.register_tools()

                logger.info("MCP适配器初始化成功")
                return True
            else:
                logger.warning("MCP客户端不支持连接方法")
                return False
        except Exception as e:
            logger.error(f"MCP适配器初始化失败: {str(e)}")
            return False

    async def register_tools(self):
        """注册工具"""
        # 学术搜索工具
        await self.mcp_client.register_tool("academic_search", {
            "name": "academic_search",
            "description": "搜索学术文献",
            "parameters": {
                "query": {
                    "type": "string",
                    "description": "搜索查询"
                },
                "limit": {
                    "type": "integer",
                    "description": "结果数量",
                    "default": 5
                }
            },
            "handler": self._handle_academic_search
        })

        # 主题推荐工具
        await self.mcp_client.register_tool("topic_recommend", {
            "name": "topic_recommend",
            "description": "推荐论文主题",
            "parameters": {
                "user_interests": {
                    "type": "string",
                    "description": "用户兴趣"
                },
                "academic_field": {
                    "type": "string",
                    "description": "学术领域"
                },
                "academic_level": {
                    "type": "string",
                    "description": "学术级别",
                    "enum": ["undergraduate", "master", "phd", "professional"]
                }
            },
            "handler": self._handle_topic_recommend
        })

        # 提纲生成工具
        await self.mcp_client.register_tool("outline_generate", {
            "name": "outline_generate",
            "description": "生成论文提纲",
            "parameters": {
                "topic": {
                    "type": "string",
                    "description": "论文主题"
                },
                "academic_field": {
                    "type": "string",
                    "description": "学术领域"
                },
                "paper_type": {
                    "type": "string",
                    "description": "论文类型",
                    "enum": ["research", "review", "thesis", "essay"]
                }
            },
            "handler": self._handle_outline_generate
        })

        # 论文生成工具
        await self.mcp_client.register_tool("paper_generate", {
            "name": "paper_generate",
            "description": "生成论文内容",
            "parameters": {
                "outline": {
                    "type": "object",
                    "description": "论文提纲"
                },
                "section": {
                    "type": "string",
                    "description": "要生成的章节"
                }
            },
            "handler": self._handle_paper_generate
        })

        # 引用生成工具
        await self.mcp_client.register_tool("citation_generate", {
            "name": "citation_generate",
            "description": "生成引用",
            "parameters": {
                "references": {
                    "type": "array",
                    "description": "参考文献列表"
                },
                "citation_style": {
                    "type": "string",
                    "description": "引用样式",
                    "enum": ["APA", "MLA", "Chicago", "Harvard"]
                }
            },
            "handler": self._handle_citation_generate
        })

    async def _handle_academic_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理学术搜索工具调用"""
        try:
            query = params.get("query", "")
            limit = params.get("limit", 5)

            results = await academic_search_service.search_academic_papers(query, limit)
            return {"status": "success", "results": results}
        except Exception as e:
            logger.error(f"学术搜索失败: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def _handle_topic_recommend(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理主题推荐工具调用"""
        try:
            user_interests = params.get("user_interests", "")
            academic_field = params.get("academic_field", "")
            academic_level = params.get("academic_level", "master")

            topics = await topic_service.recommend_topics(
                user_interests=user_interests,
                academic_field=academic_field,
                academic_level=academic_level
            )
            return {"status": "success", "topics": topics}
        except Exception as e:
            logger.error(f"主题推荐失败: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def _handle_outline_generate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理提纲生成工具调用"""
        try:
            topic = params.get("topic", "")
            academic_field = params.get("academic_field", "")
            paper_type = params.get("paper_type", "research")

            outline = await outline_service.generate_outline(
                topic=topic,
                academic_field=academic_field,
                paper_type=paper_type
            )
            return {"status": "success", "outline": outline}
        except Exception as e:
            logger.error(f"提纲生成失败: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def _handle_paper_generate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理论文生成工具调用"""
        try:
            outline = params.get("outline", {})
            section = params.get("section", "")

            content = await paper_service.generate_section(
                outline=outline,
                section=section
            )
            return {"status": "success", "content": content}
        except Exception as e:
            logger.error(f"论文生成失败: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def _handle_citation_generate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理引用生成工具调用"""
        try:
            references = params.get("references", [])
            citation_style = params.get("citation_style", "APA")

            citations = await citation_service.format_citations(
                references=references,
                style=citation_style
            )
            return {"status": "success", "citations": citations}
        except Exception as e:
            logger.error(f"引用生成失败: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def create_paper_context(self, topic: str, academic_field: str) -> Dict[str, Any]:
        """创建论文上下文"""
        if not self.mcp_client.enabled:
            logger.info("MCP未启用，跳过创建论文上下文")
            return {"status": "skipped", "message": "MCP not enabled"}

        # 创建上下文
        context = await self.mcp_client.create_context({
            "name": f"论文: {topic}",
            "description": f"关于 {topic} 的学术论文",
            "metadata": {
                "topic": topic,
                "academic_field": academic_field,
                "created_at": asyncio.get_event_loop().time()
            }
        })

        if "context_id" not in context:
            logger.error("创建论文上下文失败")
            return {"status": "error", "message": "Failed to create context"}

        logger.info(f"成功创建论文上下文: {context['context_id']}")
        return context

    async def execute_paper_workflow(self, context_id: str, topic: str, academic_field: str) -> Dict[str, Any]:
        """执行论文工作流"""
        if not self.mcp_client.enabled:
            logger.info("MCP未启用，跳过执行论文工作流")
            return {"status": "skipped", "message": "MCP not enabled"}

        # 1. 推荐主题
        topic_result = await self.mcp_client.execute_tool(
            context_id=context_id,
            tool_name="topic_recommend",
            tool_params={
                "user_interests": topic,
                "academic_field": academic_field,
                "academic_level": "master"
            }
        )

        if topic_result.get("status") != "success":
            logger.error(f"主题推荐失败: {topic_result.get('message')}")
            return {"status": "error", "message": "Topic recommendation failed"}

        # 2. 生成提纲
        outline_result = await self.mcp_client.execute_tool(
            context_id=context_id,
            tool_name="outline_generate",
            tool_params={
                "topic": topic,
                "academic_field": academic_field,
                "paper_type": "research"
            }
        )

        if outline_result.get("status") != "success":
            logger.error(f"提纲生成失败: {outline_result.get('message')}")
            return {"status": "error", "message": "Outline generation failed"}

        # 3. 生成论文各部分
        outline = outline_result.get("outline", {})
        sections = outline.get("sections", [])

        section_contents = {}
        for section in sections:
            section_name = section.get("title", "")
            if not section_name:
                continue

            section_result = await self.mcp_client.execute_tool(
                context_id=context_id,
                tool_name="paper_generate",
                tool_params={
                    "outline": outline,
                    "section": section_name
                }
            )

            if section_result.get("status") == "success":
                section_contents[section_name] = section_result.get("content", "")
            else:
                logger.warning(f"生成章节 '{section_name}' 失败: {section_result.get('message')}")

        # 4. 生成引用
        citation_result = await self.mcp_client.execute_tool(
            context_id=context_id,
            tool_name="citation_generate",
            tool_params={
                "references": outline.get("references", []),
                "citation_style": "APA"
            }
        )

        # 5. 返回结果
        return {
            "status": "success",
            "context_id": context_id,
            "topic": topic,
            "outline": outline,
            "sections": section_contents,
            "citations": citation_result.get("citations", []) if citation_result.get("status") == "success" else []
        }

# 创建全局MCP适配器实例
mcp_adapter = MCPAdapter()
