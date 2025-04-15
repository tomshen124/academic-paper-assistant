"""
MCP (Model Context Protocol) 客户端存根实现
当无法导入必要的依赖时使用此存根实现
"""

from typing import Dict, List, Any, Optional, Callable
from enum import Enum
from app.core.logger import get_logger

logger = get_logger("mcp_client_stub")

class ConnectionType(str, Enum):
    """MCP连接类型"""
    STDIO = "stdio"  # 标准输入/输出
    SSE = "sse"      # Server-Sent Events

class MCPClientStub:
    """MCP服务器客户端存根实现"""
    
    def __init__(self, **kwargs):
        """初始化MCP客户端存根"""
        self.enabled = False
        logger.warning("使用MCP客户端存根实现，MCP功能将不可用")
    
    async def connect(self):
        """连接到MCP服务器"""
        logger.warning("MCP客户端存根不支持连接")
        return False
    
    async def create_context(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """创建上下文"""
        logger.warning("MCP客户端存根不支持创建上下文")
        return {"status": "skipped", "message": "MCP not available"}
    
    async def update_context(self, context_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """更新上下文"""
        logger.warning("MCP客户端存根不支持更新上下文")
        return {"status": "skipped", "message": "MCP not available"}
    
    async def get_context(self, context_id: str) -> Dict[str, Any]:
        """获取上下文"""
        logger.warning("MCP客户端存根不支持获取上下文")
        return {"status": "skipped", "message": "MCP not available"}
    
    async def delete_context(self, context_id: str) -> Dict[str, Any]:
        """删除上下文"""
        logger.warning("MCP客户端存根不支持删除上下文")
        return {"status": "skipped", "message": "MCP not available"}
    
    async def execute_tool(self, context_id: str, tool_name: str, tool_params: Dict[str, Any]) -> Dict[str, Any]:
        """执行工具"""
        logger.warning("MCP客户端存根不支持执行工具")
        return {"status": "skipped", "message": "MCP not available"}
    
    async def register_tool(self, tool_name: str, tool_config: Dict[str, Any]) -> Dict[str, Any]:
        """注册工具"""
        logger.warning("MCP客户端存根不支持注册工具")
        return {"status": "skipped", "message": "MCP not available"}
    
    async def register_context_handler(self, context_id: str, handler: Callable[[Dict[str, Any]], None]) -> bool:
        """注册上下文消息处理器"""
        logger.warning("MCP客户端存根不支持注册上下文消息处理器")
        return False
    
    async def close(self):
        """关闭连接"""
        logger.warning("MCP客户端存根不支持关闭连接")
        return
