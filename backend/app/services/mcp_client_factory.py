"""
MCP (Model Context Protocol) 客户端工厂
根据可用的依赖和配置创建适当的MCP客户端
"""

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger("mcp_client_factory")

def create_mcp_client():
    """创建MCP客户端"""
    # 检查MCP是否启用
    if not settings.get('mcp.enabled', False):
        # 如果MCP未启用，返回存根实现
        from app.services.mcp_client_stub import MCPClientStub
        logger.info("MCP未启用，使用存根实现")
        return MCPClientStub()
    
    # 检查连接类型
    connection_type = settings.get('mcp.connection_type', 'stdio')
    
    # 如果连接类型是SSE，需要检查httpx是否可用
    if connection_type == 'sse':
        try:
            import httpx
        except ImportError:
            logger.error("无法导入httpx模块，SSE连接不可用")
            logger.warning("请安装httpx模块以使用SSE连接方式: pip install httpx")
            from app.services.mcp_client_stub import MCPClientStub
            return MCPClientStub()
    
    # 如果连接类型是WebSocket，需要检查websockets是否可用
    if connection_type == 'websocket':
        try:
            import websockets
        except ImportError:
            logger.error("无法导入websockets模块，WebSocket连接不可用")
            logger.warning("请安装websockets模块以使用WebSocket连接方式: pip install websockets")
            from app.services.mcp_client_stub import MCPClientStub
            return MCPClientStub()
    
    # 所有依赖都可用，返回真实实现
    try:
        from app.services.mcp_client_impl import MCPClient
        logger.info(f"MCP已启用，使用{connection_type}连接")
        return MCPClient()
    except ImportError as e:
        logger.error(f"无法导入MCP客户端实现: {str(e)}")
        from app.services.mcp_client_stub import MCPClientStub
        return MCPClientStub()
