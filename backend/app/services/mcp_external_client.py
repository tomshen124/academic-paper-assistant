"""
MCP (Model Context Protocol) 外部客户端
用于连接外部MCP服务器的客户端
"""

from typing import Dict, List, Any, Optional, Tuple, Callable, Awaitable
import asyncio
import json
import os
from contextlib import asynccontextmanager

try:
    from mcp import ClientSession, StdioServerParameters, types
    from mcp.client.stdio import stdio_client
    from mcp.client.streamable_http import streamablehttp_client
    MCP_SDK_AVAILABLE = True
except ImportError:
    MCP_SDK_AVAILABLE = False

from app.core.logger import get_logger
from app.core.config import settings

logger = get_logger("mcp_external_client")

class MCPExternalClient:
    """MCP外部客户端，用于连接外部MCP服务器"""
    
    def __init__(self, enabled: bool = True):
        """初始化MCP外部客户端
        
        Args:
            enabled: 是否启用MCP客户端
        """
        self.enabled = enabled and MCP_SDK_AVAILABLE
        self.session = None
        self.server_info = None
        self.tools_cache = {}
        self.resources_cache = {}
        self.prompts_cache = {}
        
        if not MCP_SDK_AVAILABLE:
            logger.warning("MCP SDK未安装，MCP功能将不可用")
            logger.warning("请安装MCP SDK: pip install mcp[cli]")
    
    async def connect_to_server(self, server_type: str = None, **kwargs) -> bool:
        """连接到外部MCP服务器
        
        Args:
            server_type: 服务器类型，支持'stdio'、'http'、'claude'
            **kwargs: 连接参数
            
        Returns:
            连接是否成功
        """
        if not self.enabled:
            logger.info("MCP客户端未启用")
            return False
        
        # 获取服务器类型
        server_type = server_type or settings.get('mcp.server_type', 'stdio')
        
        if server_type == 'stdio':
            # 通过stdio连接到外部MCP服务器
            command = kwargs.get('command') or settings.get('mcp.command')
            args = kwargs.get('args') or settings.get('mcp.args', [])
            env = kwargs.get('env') or settings.get('mcp.env', {})
            
            if not command:
                logger.error("未指定MCP服务器命令")
                return False
                
            return await self._connect_stdio(command, args, env)
            
        elif server_type == 'http':
            # 通过HTTP连接到外部MCP服务器
            url = kwargs.get('url') or settings.get('mcp.url')
            
            if not url:
                logger.error("未指定MCP服务器URL")
                return False
                
            return await self._connect_http(url)
            
        elif server_type == 'claude':
            # 连接到Claude Desktop的MCP服务器
            return await self._connect_claude()
            
        else:
            logger.error(f"不支持的服务器类型: {server_type}")
            return False
    
    async def _connect_stdio(self, command: str, args: List[str] = None, env: Dict[str, str] = None) -> bool:
        """通过stdio连接到外部MCP服务器
        
        Args:
            command: 服务器命令
            args: 命令行参数
            env: 环境变量
            
        Returns:
            连接是否成功
        """
        try:
            logger.info(f"通过stdio连接到MCP服务器: {command} {' '.join(args or [])}")
            
            # 创建服务器参数
            server_params = StdioServerParameters(
                command=command,
                args=args or [],
                env=env or {}
            )
            
            # 连接到服务器
            read_stream, write_stream = await stdio_client(server_params)
            
            # 创建会话
            self.session = ClientSession(read_stream, write_stream)
            
            # 初始化连接
            self.server_info = await self.session.initialize()
            
            logger.info(f"成功连接到MCP服务器: {self.server_info.server_name} v{self.server_info.server_version}")
            return True
            
        except Exception as e:
            logger.error(f"通过stdio连接MCP服务器失败: {str(e)}")
            self.session = None
            return False
    
    async def _connect_http(self, url: str) -> bool:
        """通过HTTP连接到外部MCP服务器
        
        Args:
            url: 服务器URL
            
        Returns:
            连接是否成功
        """
        try:
            logger.info(f"通过HTTP连接到MCP服务器: {url}")
            
            # 连接到服务器
            read_stream, write_stream, _ = await streamablehttp_client(url)
            
            # 创建会话
            self.session = ClientSession(read_stream, write_stream)
            
            # 初始化连接
            self.server_info = await self.session.initialize()
            
            logger.info(f"成功连接到MCP服务器: {self.server_info.server_name} v{self.server_info.server_version}")
            return True
            
        except Exception as e:
            logger.error(f"通过HTTP连接MCP服务器失败: {str(e)}")
            self.session = None
            return False
    
    async def _connect_claude(self) -> bool:
        """连接到Claude Desktop的MCP服务器
        
        Returns:
            连接是否成功
        """
        try:
            from mcp.client.claude import claude_client
            
            logger.info("连接到Claude Desktop的MCP服务器")
            
            # 连接到Claude Desktop
            read_stream, write_stream = await claude_client()
            
            # 创建会话
            self.session = ClientSession(read_stream, write_stream)
            
            # 初始化连接
            self.server_info = await self.session.initialize()
            
            logger.info(f"成功连接到Claude Desktop的MCP服务器: {self.server_info.server_name} v{self.server_info.server_version}")
            return True
            
        except ImportError:
            logger.error("无法导入claude_client，请确保安装了最新版本的MCP SDK")
            return False
        except Exception as e:
            logger.error(f"连接Claude Desktop的MCP服务器失败: {str(e)}")
            self.session = None
            return False
    
    async def disconnect(self) -> None:
        """断开与MCP服务器的连接"""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("已断开与MCP服务器的连接")
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """列出可用的工具
        
        Returns:
            工具列表
        """
        if not self.session:
            logger.error("未连接到MCP服务器")
            return []
            
        try:
            tools = await self.session.list_tools()
            self.tools_cache = {tool.name: tool for tool in tools}
            return [tool.model_dump() for tool in tools]
        except Exception as e:
            logger.error(f"列出工具失败: {str(e)}")
            return []
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """调用工具
        
        Args:
            name: 工具名称
            arguments: 工具参数
            
        Returns:
            工具执行结果
        """
        if not self.session:
            logger.error("未连接到MCP服务器")
            return {"error": "未连接到MCP服务器"}
            
        try:
            result = await self.session.call_tool(name, arguments)
            return result
        except Exception as e:
            logger.error(f"调用工具 {name} 失败: {str(e)}")
            return {"error": str(e)}
    
    async def list_resources(self) -> List[Dict[str, Any]]:
        """列出可用的资源
        
        Returns:
            资源列表
        """
        if not self.session:
            logger.error("未连接到MCP服务器")
            return []
            
        try:
            resources = await self.session.list_resources()
            self.resources_cache = {resource.uri_template: resource for resource in resources}
            return [resource.model_dump() for resource in resources]
        except Exception as e:
            logger.error(f"列出资源失败: {str(e)}")
            return []
    
    async def read_resource(self, uri: str) -> Tuple[bytes, str]:
        """读取资源
        
        Args:
            uri: 资源URI
            
        Returns:
            资源内容和MIME类型
        """
        if not self.session:
            logger.error("未连接到MCP服务器")
            return b"", "text/plain"
            
        try:
            content, mime_type = await self.session.read_resource(uri)
            return content, mime_type
        except Exception as e:
            logger.error(f"读取资源 {uri} 失败: {str(e)}")
            return b"", "text/plain"
    
    async def list_prompts(self) -> List[Dict[str, Any]]:
        """列出可用的提示模板
        
        Returns:
            提示模板列表
        """
        if not self.session:
            logger.error("未连接到MCP服务器")
            return []
            
        try:
            prompts = await self.session.list_prompts()
            self.prompts_cache = {prompt.name: prompt for prompt in prompts}
            return [prompt.model_dump() for prompt in prompts]
        except Exception as e:
            logger.error(f"列出提示模板失败: {str(e)}")
            return []
    
    async def get_prompt(self, name: str, arguments: Dict[str, str] = None) -> Dict[str, Any]:
        """获取提示模板
        
        Args:
            name: 提示模板名称
            arguments: 提示模板参数
            
        Returns:
            提示模板内容
        """
        if not self.session:
            logger.error("未连接到MCP服务器")
            return {"error": "未连接到MCP服务器"}
            
        try:
            prompt = await self.session.get_prompt(name, arguments or {})
            return prompt.model_dump()
        except Exception as e:
            logger.error(f"获取提示模板 {name} 失败: {str(e)}")
            return {"error": str(e)}

# 创建全局MCP外部客户端实例
mcp_external_client = MCPExternalClient(enabled=settings.get('mcp.enabled', False))
