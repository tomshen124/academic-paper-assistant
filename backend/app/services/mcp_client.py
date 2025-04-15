"""
MCP (Model Context Protocol) 客户端
这是一个入口点文件，用于导出MCP客户端实例
"""

from app.services.mcp_client_factory import create_mcp_client

# 创建MCP客户端实例
mcp_client = create_mcp_client()
