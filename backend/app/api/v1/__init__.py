from fastapi import APIRouter
from .endpoints import topics, outlines, papers, citations, search, agents, tokens, mcp

api_router = APIRouter()

# 添加API版本的默认路由
@api_router.get("/")
async def api_root():
    return {
        "message": "Academic Paper Assistant API v1",
        "endpoints": {
            "topics": "/topics",
            "outlines": "/outlines",
            "papers": "/papers",
            "citations": "/citations",
            "search": "/search",
            "agents": "/agents",
            "tokens": "/tokens",
            "mcp": "/mcp"
        }
    }

# 主题相关路由
api_router.include_router(topics.router, prefix="/topics", tags=["topics"])

# 提纲相关路由
api_router.include_router(outlines.router, prefix="/outlines", tags=["outlines"])

# 论文相关路由
api_router.include_router(papers.router, prefix="/papers", tags=["papers"])

# 引用相关路由
api_router.include_router(citations.router, prefix="/citations", tags=["citations"])

# 搜索相关路由
api_router.include_router(search.router, prefix="/search", tags=["search"])

# 智能体相关路由
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])

# Token相关路由
api_router.include_router(tokens.router, prefix="/tokens", tags=["tokens"])

# MCP相关路由
api_router.include_router(mcp.router, prefix="/mcp", tags=["mcp"])

# 导出路由器供主应用使用
__all__ = ["api_router"]