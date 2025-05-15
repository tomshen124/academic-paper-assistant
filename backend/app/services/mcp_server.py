"""
MCP (Model Context Protocol) 服务器
使用官方MCP SDK实现的简化版MCP服务器
"""

from typing import Dict, List, Any, Optional, Tuple
import asyncio
import json
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

try:
    from mcp.server.fastmcp import FastMCP, Context, Image
    MCP_SDK_AVAILABLE = True
except ImportError:
    MCP_SDK_AVAILABLE = False

from app.services.topic_service import topic_service
from app.services.outline_service import outline_service
from app.services.paper_service import paper_service
from app.services.citation_service import citation_service
from app.services.academic_search_service import academic_search_service
from app.core.logger import get_logger
from app.core.config import settings

logger = get_logger("mcp_server")

# 检查MCP SDK是否可用
if not MCP_SDK_AVAILABLE:
    logger.warning("MCP SDK未安装，MCP服务器将不可用")
    logger.warning("请安装MCP SDK: pip install mcp[cli]")

# 创建MCP服务器
mcp_server = FastMCP(
    name="EduKG Academic Assistant",
    description="学术论文写作助手，提供主题推荐、提纲生成、论文写作等功能",
    dependencies=["fastapi", "pydantic", "httpx"]
) if MCP_SDK_AVAILABLE else None

# 学术搜索工具
if MCP_SDK_AVAILABLE and mcp_server is not None:
    @mcp_server.tool(description="搜索学术文献")
    async def academic_search(query: str, limit: int = 5) -> Dict[str, Any]:
        """搜索学术文献

        Args:
            query: 搜索查询
            limit: 结果数量限制

        Returns:
            搜索结果
        """
        try:
            results = await academic_search_service.search_academic_papers(query, limit)
            return {"status": "success", "results": results}
        except Exception as e:
            logger.error(f"学术搜索失败: {str(e)}")
            return {"status": "error", "message": str(e)}

# 主题推荐工具
if MCP_SDK_AVAILABLE and mcp_server is not None:
    @mcp_server.tool(description="推荐论文主题")
    async def topic_recommend(
        user_interests: str,
        academic_field: str,
        academic_level: str = "master"
    ) -> Dict[str, Any]:
        """推荐论文主题

        Args:
            user_interests: 用户兴趣
            academic_field: 学术领域
            academic_level: 学术级别

        Returns:
            推荐的主题列表
        """
        try:
            topics = await topic_service.recommend_topics(
                user_interests=user_interests,
                academic_field=academic_field,
                academic_level=academic_level
            )
            return {"status": "success", "topics": topics}
        except Exception as e:
            logger.error(f"主题推荐失败: {str(e)}")
            return {"status": "error", "message": str(e)}

# 提纲生成工具
if MCP_SDK_AVAILABLE and mcp_server is not None:
    @mcp_server.tool(description="生成论文提纲")
    async def outline_generate(
        topic: str,
        academic_field: str,
        paper_type: str = "research",
        academic_level: str = "master"
    ) -> Dict[str, Any]:
        """生成论文提纲

        Args:
            topic: 论文主题
            academic_field: 学术领域
            paper_type: 论文类型
            academic_level: 学术级别

        Returns:
            生成的提纲
        """
        try:
            outline = await outline_service.generate_outline(
                topic=topic,
                academic_field=academic_field,
                paper_type=paper_type,
                academic_level=academic_level
            )
            return {"status": "success", "outline": outline}
        except Exception as e:
            logger.error(f"提纲生成失败: {str(e)}")
            return {"status": "error", "message": str(e)}

# 论文生成工具
if MCP_SDK_AVAILABLE and mcp_server is not None:
    @mcp_server.tool(description="生成论文内容")
    async def paper_generate(
        outline: Dict[str, Any],
        section: str
    ) -> Dict[str, Any]:
        """生成论文内容

        Args:
            outline: 论文提纲
            section: 要生成的章节

        Returns:
            生成的章节内容
        """
        try:
            content = await paper_service.generate_section(
                outline=outline,
                section=section
            )
            return {"status": "success", "content": content}
        except Exception as e:
            logger.error(f"论文生成失败: {str(e)}")
            return {"status": "error", "message": str(e)}

# 引用生成工具
if MCP_SDK_AVAILABLE and mcp_server is not None:
    @mcp_server.tool(description="生成引用")
    async def citation_generate(
        references: List[Dict[str, Any]],
        citation_style: str = "APA"
    ) -> Dict[str, Any]:
        """生成引用

        Args:
            references: 参考文献列表
            citation_style: 引用样式

        Returns:
            生成的引用
        """
        try:
            citations = await citation_service.format_citations(
                references=references,
                style=citation_style
            )
            return {"status": "success", "citations": citations}
        except Exception as e:
            logger.error(f"引用生成失败: {str(e)}")
            return {"status": "error", "message": str(e)}

# 提供论文主题资源
if MCP_SDK_AVAILABLE and mcp_server is not None:
    @mcp_server.resource("topics://{academic_field}")
    async def get_topics(academic_field: str) -> str:
        """获取特定学术领域的热门主题

        Args:
            academic_field: 学术领域

        Returns:
            热门主题列表
        """
        try:
            topics = await topic_service.get_trending_topics(academic_field)
            return json.dumps(topics, ensure_ascii=False)
        except Exception as e:
            logger.error(f"获取热门主题失败: {str(e)}")
            return json.dumps({"error": str(e)})

# 提供论文提纲模板资源
if MCP_SDK_AVAILABLE and mcp_server is not None:
    @mcp_server.resource("templates://{paper_type}")
    async def get_outline_template(paper_type: str) -> str:
        """获取特定类型论文的提纲模板

        Args:
            paper_type: 论文类型

        Returns:
            提纲模板
        """
        try:
            template = await outline_service.get_template(paper_type)
            return json.dumps(template, ensure_ascii=False)
        except Exception as e:
            logger.error(f"获取提纲模板失败: {str(e)}")
            return json.dumps({"error": str(e)})

# 创建提示模板
if MCP_SDK_AVAILABLE and mcp_server is not None:
    @mcp_server.prompt()
    def topic_brainstorm(user_interests: str, academic_field: str) -> str:
        """创建主题头脑风暴提示

        Args:
            user_interests: 用户兴趣
            academic_field: 学术领域

        Returns:
            提示模板
        """
        return f"""
        我需要在{academic_field}领域写一篇学术论文。
        我对{user_interests}特别感兴趣。
        请帮我头脑风暴5-10个可能的研究主题，并简要说明每个主题的研究价值和可行性。
        """

    @mcp_server.prompt()
    def outline_creation(topic: str, academic_field: str) -> str:
        """创建提纲生成提示

        Args:
            topic: 论文主题
            academic_field: 学术领域

        Returns:
            提示模板
        """
        return f"""
        我需要为以下论文主题创建一个详细的提纲：

        主题：{topic}
        学术领域：{academic_field}

        请提供一个包含以下部分的详细提纲：
        1. 引言（研究背景、问题陈述、研究目的）
        2. 文献综述
        3. 研究方法
        4. 预期结果
        5. 讨论
        6. 结论

        对于每个部分，请提供2-3个子部分的建议。
        """

# 运行MCP服务器的函数
def run_mcp_server():
    """运行MCP服务器"""
    if not MCP_SDK_AVAILABLE:
        logger.error("MCP SDK未安装，无法运行MCP服务器")
        return

    if mcp_server is None:
        logger.error("MCP服务器未初始化")
        return

    logger.info("启动MCP服务器...")
    try:
        # 设置传输类型
        transport = settings.get('mcp.transport', 'stdio')
        mcp_server.run(transport=transport)
    except Exception as e:
        logger.error(f"运行MCP服务器时出错: {str(e)}")

# 如果直接运行此文件，则启动MCP服务器
if __name__ == "__main__":
    run_mcp_server()
