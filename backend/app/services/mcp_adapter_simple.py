"""
MCP (Model Context Protocol) 适配器
简化版MCP适配器，用于连接MCP客户端和服务器
"""

from typing import Dict, List, Any, Optional, Tuple
import asyncio
import json
import os
from contextlib import asynccontextmanager

from app.services.mcp_client import mcp_client
from app.services.mcp_server import run_mcp_server, MCP_SDK_AVAILABLE
from app.core.logger import get_logger
from app.core.config import settings

logger = get_logger("mcp_adapter_simple")

class MCPAdapterSimple:
    """MCP适配器，用于连接MCP客户端和服务器"""
    
    def __init__(self):
        """初始化MCP适配器"""
        self.mcp_client = mcp_client
        self.server_process = None
        self.initialized = False
        
    async def initialize(self) -> bool:
        """初始化MCP适配器
        
        Returns:
            初始化是否成功
        """
        if self.initialized:
            logger.info("MCP适配器已初始化")
            return True
            
        if not self.mcp_client.enabled:
            logger.warning("MCP客户端未启用，跳过初始化")
            return False
            
        # 启动MCP服务器进程
        if settings.get('mcp.start_server', True):
            await self._start_server()
            
        # 连接到MCP服务器
        connected = await self.mcp_client.connect()
        if not connected:
            logger.error("连接MCP服务器失败")
            return False
            
        self.initialized = True
        logger.info("MCP适配器初始化成功")
        return True
        
    async def _start_server(self) -> None:
        """启动MCP服务器进程"""
        if not MCP_SDK_AVAILABLE:
            logger.error("MCP SDK未安装，无法启动MCP服务器")
            return
            
        try:
            # 获取服务器命令
            server_script = settings.get('mcp.server_script', 'app/services/mcp_server.py')
            python_executable = settings.get('mcp.python_executable', 'python')
            
            # 启动服务器进程
            import subprocess
            import sys
            
            logger.info(f"启动MCP服务器: {python_executable} {server_script}")
            
            # 使用subprocess启动服务器进程
            self.server_process = subprocess.Popen(
                [python_executable, server_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 等待服务器启动
            await asyncio.sleep(2)
            
            if self.server_process.poll() is not None:
                # 进程已退出
                stdout, stderr = self.server_process.communicate()
                logger.error(f"MCP服务器启动失败: {stderr}")
                self.server_process = None
            else:
                logger.info("MCP服务器启动成功")
                
        except Exception as e:
            logger.error(f"启动MCP服务器时出错: {str(e)}")
            self.server_process = None
            
    async def shutdown(self) -> None:
        """关闭MCP适配器"""
        if self.mcp_client.session:
            await self.mcp_client.disconnect()
            
        if self.server_process:
            logger.info("关闭MCP服务器进程")
            self.server_process.terminate()
            self.server_process = None
            
        self.initialized = False
        logger.info("MCP适配器已关闭")
        
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """调用工具
        
        Args:
            tool_name: 工具名称
            arguments: 工具参数
            
        Returns:
            工具执行结果
        """
        if not self.initialized:
            success = await self.initialize()
            if not success:
                return {"status": "error", "message": "MCP适配器初始化失败"}
                
        return await self.mcp_client.call_tool(tool_name, arguments)
        
    async def read_resource(self, uri: str) -> Tuple[bytes, str]:
        """读取资源
        
        Args:
            uri: 资源URI
            
        Returns:
            资源内容和MIME类型
        """
        if not self.initialized:
            success = await self.initialize()
            if not success:
                return b"", "text/plain"
                
        return await self.mcp_client.read_resource(uri)
        
    async def get_prompt(self, name: str, arguments: Dict[str, str] = None) -> Dict[str, Any]:
        """获取提示模板
        
        Args:
            name: 提示模板名称
            arguments: 提示模板参数
            
        Returns:
            提示模板内容
        """
        if not self.initialized:
            success = await self.initialize()
            if not success:
                return {"error": "MCP适配器初始化失败"}
                
        return await self.mcp_client.get_prompt(name, arguments)
        
    async def recommend_topics(self, user_interests: str, academic_field: str, academic_level: str = "master") -> List[Dict[str, Any]]:
        """推荐论文主题
        
        Args:
            user_interests: 用户兴趣
            academic_field: 学术领域
            academic_level: 学术级别
            
        Returns:
            推荐的主题列表
        """
        result = await self.call_tool("topic_recommend", {
            "user_interests": user_interests,
            "academic_field": academic_field,
            "academic_level": academic_level
        })
        
        if result.get("status") == "success":
            return result.get("topics", [])
        else:
            logger.error(f"推荐主题失败: {result.get('message')}")
            return []
            
    async def generate_outline(self, topic: str, academic_field: str, paper_type: str = "research", academic_level: str = "master") -> Dict[str, Any]:
        """生成论文提纲
        
        Args:
            topic: 论文主题
            academic_field: 学术领域
            paper_type: 论文类型
            academic_level: 学术级别
            
        Returns:
            生成的提纲
        """
        result = await self.call_tool("outline_generate", {
            "topic": topic,
            "academic_field": academic_field,
            "paper_type": paper_type,
            "academic_level": academic_level
        })
        
        if result.get("status") == "success":
            return result.get("outline", {})
        else:
            logger.error(f"生成提纲失败: {result.get('message')}")
            return {}

# 创建全局MCP适配器实例
mcp_adapter_simple = MCPAdapterSimple()
