"""
MCP (Model Context Protocol) 客户端
支持通过 stdio 和 SSE 两种方式连接 MCP 服务器
"""

from typing import Dict, List, Any, Optional, Callable, Union
import json
import asyncio
import httpx
import websockets
from enum import Enum
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger("mcp_client")

class ConnectionType(str, Enum):
    """MCP连接类型"""
    STDIO = "stdio"  # 标准输入/输出
    SSE = "sse"      # Server-Sent Events

class MCPClient:
    """MCP服务器客户端"""

    def __init__(self,
                 base_url: Optional[str] = None,
                 api_key: Optional[str] = None,
                 connection_type: Optional[ConnectionType] = None):
        """初始化MCP客户端"""
        self.base_url = base_url or settings.get('mcp.base_url')
        self.api_key = api_key or settings.get('mcp.api_key')
        self.connection_type = connection_type or ConnectionType(settings.get('mcp.connection_type', 'http'))
        self.enabled = settings.get('mcp.enabled', False)

        # HTTP客户端
        self.http_client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"}
        )

        # WebSocket连接
        self.ws_connection = None
        self.ws_callbacks = {}

        logger.info(f"MCP客户端初始化完成, 启用状态: {self.enabled}, 连接类型: {self.connection_type}")

    async def connect_websocket(self):
        """连接WebSocket"""
        if not self.enabled or self.connection_type != ConnectionType.WEBSOCKET:
            return

        if not WEBSOCKETS_AVAILABLE:
            logger.error("WebSocket连接失败: websockets模块未安装")
            logger.warning("请安装websockets模块以使用WebSocket连接方式: pip install websockets")
            return False

        try:
            ws_url = f"{self.base_url.replace('http', 'ws')}/ws?api_key={self.api_key}"
            self.ws_connection = await websockets.connect(ws_url)
            logger.info("WebSocket连接成功")

            # 启动监听任务
            asyncio.create_task(self._listen_websocket())
            return True
        except Exception as e:
            logger.error(f"WebSocket连接失败: {str(e)}")
            self.ws_connection = None
            return False

    async def _listen_websocket(self):
        """监听WebSocket消息"""
        if not self.ws_connection:
            return

        try:
            async for message in self.ws_connection:
                data = json.loads(message)
                message_type = data.get("type")
                message_id = data.get("id")

                # 处理回调
                callback_key = f"{message_type}:{message_id}" if message_id else message_type
                if callback_key in self.ws_callbacks:
                    callback = self.ws_callbacks[callback_key]
                    asyncio.create_task(callback(data))

                # 处理系统消息
                if message_type == "system":
                    logger.info(f"收到系统消息: {data.get('content')}")
        except Exception as e:
            logger.error(f"WebSocket监听错误: {str(e)}")
        finally:
            # 重新连接
            if self.enabled and self.connection_type == ConnectionType.WEBSOCKET:
                logger.info("尝试重新连接WebSocket...")
                await asyncio.sleep(5)
                await self.connect_websocket()

    async def register_agent(self, agent_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """注册智能体"""
        if not self.enabled:
            logger.info(f"MCP未启用，跳过注册智能体: {agent_id}")
            return {"status": "skipped", "message": "MCP not enabled"}

        if self.connection_type == ConnectionType.HTTP:
            return await self._http_register_agent(agent_id, config)
        else:
            return await self._ws_register_agent(agent_id, config)

    async def _http_register_agent(self, agent_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """通过HTTP注册智能体"""
        try:
            response = await self.http_client.post(f"/agents/{agent_id}", json=config)
            response.raise_for_status()
            logger.info(f"成功注册智能体: {agent_id}")
            return response.json()
        except Exception as e:
            logger.error(f"注册智能体失败: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def _ws_register_agent(self, agent_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """通过WebSocket注册智能体"""
        if not self.ws_connection:
            await self.connect_websocket()
            if not self.ws_connection:
                return {"status": "error", "message": "WebSocket连接失败"}

        try:
            message_id = f"register_agent_{agent_id}"
            message = {
                "type": "register_agent",
                "id": message_id,
                "agent_id": agent_id,
                "config": config
            }

            # 创建Future用于等待响应
            future = asyncio.Future()

            # 注册回调
            self.ws_callbacks[f"register_agent_response:{message_id}"] = lambda data: future.set_result(data)

            # 发送消息
            await self.ws_connection.send(json.dumps(message))

            # 等待响应
            try:
                response = await asyncio.wait_for(future, timeout=10.0)
                logger.info(f"成功注册智能体: {agent_id}")
                return response.get("data", {})
            except asyncio.TimeoutError:
                logger.error(f"注册智能体超时: {agent_id}")
                return {"status": "error", "message": "Registration timeout"}
            finally:
                # 清理回调
                self.ws_callbacks.pop(f"register_agent_response:{message_id}", None)

        except Exception as e:
            logger.error(f"通过WebSocket注册智能体失败: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def register_tool(self, tool_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """注册工具"""
        if not self.enabled:
            logger.info(f"MCP未启用，跳过注册工具: {tool_id}")
            return {"status": "skipped", "message": "MCP not enabled"}

        if self.connection_type == ConnectionType.HTTP:
            return await self._http_register_tool(tool_id, config)
        else:
            return await self._ws_register_tool(tool_id, config)

    async def _http_register_tool(self, tool_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """通过HTTP注册工具"""
        try:
            response = await self.http_client.post(f"/tools/{tool_id}", json=config)
            response.raise_for_status()
            logger.info(f"成功注册工具: {tool_id}")
            return response.json()
        except Exception as e:
            logger.error(f"注册工具失败: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def _ws_register_tool(self, tool_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """通过WebSocket注册工具"""
        if not self.ws_connection:
            await self.connect_websocket()
            if not self.ws_connection:
                return {"status": "error", "message": "WebSocket连接失败"}

        try:
            message_id = f"register_tool_{tool_id}"
            message = {
                "type": "register_tool",
                "id": message_id,
                "tool_id": tool_id,
                "config": config
            }

            # 创建Future用于等待响应
            future = asyncio.Future()

            # 注册回调
            self.ws_callbacks[f"register_tool_response:{message_id}"] = lambda data: future.set_result(data)

            # 发送消息
            await self.ws_connection.send(json.dumps(message))

            # 等待响应
            try:
                response = await asyncio.wait_for(future, timeout=10.0)
                logger.info(f"成功注册工具: {tool_id}")
                return response.get("data", {})
            except asyncio.TimeoutError:
                logger.error(f"注册工具超时: {tool_id}")
                return {"status": "error", "message": "Registration timeout"}
            finally:
                # 清理回调
                self.ws_callbacks.pop(f"register_tool_response:{message_id}", None)

        except Exception as e:
            logger.error(f"通过WebSocket注册工具失败: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def start_conversation(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """启动会话"""
        if not self.enabled:
            logger.info("MCP未启用，跳过启动会话")
            return {"status": "skipped", "message": "MCP not enabled"}

        if self.connection_type == ConnectionType.HTTP:
            return await self._http_start_conversation(config)
        else:
            return await self._ws_start_conversation(config)

    async def _http_start_conversation(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """通过HTTP启动会话"""
        try:
            response = await self.http_client.post("/conversations", json=config)
            response.raise_for_status()
            result = response.json()
            logger.info(f"成功启动会话: {result.get('conversation_id')}")
            return result
        except Exception as e:
            logger.error(f"启动会话失败: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def _ws_start_conversation(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """通过WebSocket启动会话"""
        if not self.ws_connection:
            await self.connect_websocket()
            if not self.ws_connection:
                return {"status": "error", "message": "WebSocket连接失败"}

        try:
            message_id = f"start_conversation_{config.get('topic', 'unknown')}"
            message = {
                "type": "start_conversation",
                "id": message_id,
                "config": config
            }

            # 创建Future用于等待响应
            future = asyncio.Future()

            # 注册回调
            self.ws_callbacks[f"conversation_started:{message_id}"] = lambda data: future.set_result(data)

            # 发送消息
            await self.ws_connection.send(json.dumps(message))

            # 等待响应
            try:
                response = await asyncio.wait_for(future, timeout=10.0)
                conversation_id = response.get("conversation_id")
                logger.info(f"成功启动会话: {conversation_id}")
                return response
            except asyncio.TimeoutError:
                logger.error("启动会话超时")
                return {"status": "error", "message": "Conversation start timeout"}
            finally:
                # 清理回调
                self.ws_callbacks.pop(f"conversation_started:{message_id}", None)

        except Exception as e:
            logger.error(f"通过WebSocket启动会话失败: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def get_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """获取会话信息"""
        if not self.enabled:
            logger.info(f"MCP未启用，跳过获取会话: {conversation_id}")
            return {"status": "skipped", "message": "MCP not enabled"}

        if self.connection_type == ConnectionType.HTTP:
            return await self._http_get_conversation(conversation_id)
        else:
            return await self._ws_get_conversation(conversation_id)

    async def _http_get_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """通过HTTP获取会话信息"""
        try:
            response = await self.http_client.get(f"/conversations/{conversation_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"获取会话信息失败: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def _ws_get_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """通过WebSocket获取会话信息"""
        if not self.ws_connection:
            await self.connect_websocket()
            if not self.ws_connection:
                return {"status": "error", "message": "WebSocket连接失败"}

        try:
            message_id = f"get_conversation_{conversation_id}"
            message = {
                "type": "get_conversation",
                "id": message_id,
                "conversation_id": conversation_id
            }

            # 创建Future用于等待响应
            future = asyncio.Future()

            # 注册回调
            self.ws_callbacks[f"conversation_info:{message_id}"] = lambda data: future.set_result(data)

            # 发送消息
            await self.ws_connection.send(json.dumps(message))

            # 等待响应
            try:
                response = await asyncio.wait_for(future, timeout=10.0)
                return response.get("data", {})
            except asyncio.TimeoutError:
                logger.error(f"获取会话信息超时: {conversation_id}")
                return {"status": "error", "message": "Get conversation timeout"}
            finally:
                # 清理回调
                self.ws_callbacks.pop(f"conversation_info:{message_id}", None)

        except Exception as e:
            logger.error(f"通过WebSocket获取会话信息失败: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def send_message(self, conversation_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """发送消息到会话"""
        if not self.enabled:
            logger.info(f"MCP未启用，跳过发送消息到会话: {conversation_id}")
            return {"status": "skipped", "message": "MCP not enabled"}

        if self.connection_type == ConnectionType.HTTP:
            return await self._http_send_message(conversation_id, message)
        else:
            return await self._ws_send_message(conversation_id, message)

    async def _http_send_message(self, conversation_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """通过HTTP发送消息"""
        try:
            response = await self.http_client.post(f"/conversations/{conversation_id}/messages", json=message)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"发送消息失败: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def _ws_send_message(self, conversation_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """通过WebSocket发送消息"""
        if not self.ws_connection:
            await self.connect_websocket()
            if not self.ws_connection:
                return {"status": "error", "message": "WebSocket连接失败"}

        try:
            message_id = f"send_message_{conversation_id}_{message.get('id', 'unknown')}"
            ws_message = {
                "type": "send_message",
                "id": message_id,
                "conversation_id": conversation_id,
                "message": message
            }

            # 创建Future用于等待响应
            future = asyncio.Future()

            # 注册回调
            self.ws_callbacks[f"message_sent:{message_id}"] = lambda data: future.set_result(data)

            # 发送消息
            await self.ws_connection.send(json.dumps(ws_message))

            # 等待响应
            try:
                response = await asyncio.wait_for(future, timeout=10.0)
                return response.get("data", {})
            except asyncio.TimeoutError:
                logger.error(f"发送消息超时: {conversation_id}")
                return {"status": "error", "message": "Send message timeout"}
            finally:
                # 清理回调
                self.ws_callbacks.pop(f"message_sent:{message_id}", None)

        except Exception as e:
            logger.error(f"通过WebSocket发送消息失败: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def register_message_handler(self, conversation_id: str, handler: Callable[[Dict[str, Any]], None]) -> bool:
        """注册消息处理器"""
        if not self.enabled or self.connection_type != ConnectionType.WEBSOCKET:
            return False

        if not self.ws_connection:
            await self.connect_websocket()
            if not self.ws_connection:
                return False

        # 注册回调
        self.ws_callbacks[f"message:{conversation_id}"] = handler
        return True

    async def close(self):
        """关闭连接"""
        if self.http_client:
            await self.http_client.aclose()

        if self.ws_connection:
            await self.ws_connection.close()
            self.ws_connection = None

# 创建全局MCP客户端实例
mcp_client = MCPClient()
