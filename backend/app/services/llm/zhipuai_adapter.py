"""
智谱AI适配器，用于调用智谱GLM模型
"""

from typing import Dict, List, Any, Optional, Union, AsyncGenerator
import json
import httpx
import asyncio
from app.core.logger import get_llm_logger
from app.services.llm.base_adapter import BaseLLMAdapter

logger = get_llm_logger("zhipuai_adapter")

class ZhipuAIAdapter(BaseLLMAdapter):
    """智谱AI适配器，用于调用智谱GLM模型"""
    
    def __init__(self, api_key: str, api_base: str = "https://open.bigmodel.cn/api/paas/v4/chat/completions"):
        """初始化智谱AI适配器"""
        self.api_key = api_key
        self.api_base = api_base
        self.client = httpx.AsyncClient(timeout=60.0)
        logger.info("智谱AI适配器初始化完成")
    
    async def acompletion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """异步调用智谱AI补全"""
        try:
            # 构建请求
            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": False
            }
            
            # 添加其他参数
            for key, value in kwargs.items():
                if key not in ["model", "messages", "max_tokens", "temperature", "stream"]:
                    payload[key] = value
            
            # 构建请求头
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # 发送请求
            response = await self.client.post(
                self.api_base,
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            # 解析响应
            result = response.json()
            
            # 转换为标准格式
            standardized_response = {
                "id": result.get("id", ""),
                "object": "chat.completion",
                "created": result.get("created", 0),
                "model": result.get("model", model),
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": result.get("choices", [{}])[0].get("message", {}).get("content", "")
                        },
                        "finish_reason": result.get("choices", [{}])[0].get("finish_reason", "stop")
                    }
                ],
                "usage": result.get("usage", {})
            }
            
            return standardized_response
            
        except Exception as e:
            logger.error(f"智谱AI调用失败: {str(e)}")
            raise
    
    def completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """同步调用智谱AI补全"""
        # 使用asyncio运行异步方法
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self.acompletion(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
        )
    
    async def acompletion_streaming(
        self,
        model: str,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """异步流式智谱AI调用，返回一个异步生成器"""
        try:
            # 构建请求
            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": True
            }
            
            # 添加其他参数
            for key, value in kwargs.items():
                if key not in ["model", "messages", "max_tokens", "temperature", "stream"]:
                    payload[key] = value
            
            # 构建请求头
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # 发送请求
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream(
                    "POST",
                    self.api_base,
                    headers=headers,
                    json=payload
                ) as response:
                    response.raise_for_status()
                    
                    # 处理流式响应
                    async for line in response.aiter_lines():
                        if not line.strip():
                            continue
                        
                        if line.startswith("data: "):
                            line = line[6:]  # 移除 "data: " 前缀
                        
                        if line == "[DONE]":
                            break
                        
                        try:
                            chunk = json.loads(line)
                            
                            # 转换为标准格式
                            standardized_chunk = {
                                "id": chunk.get("id", ""),
                                "object": "chat.completion.chunk",
                                "created": chunk.get("created", 0),
                                "model": chunk.get("model", model),
                                "choices": [
                                    {
                                        "index": 0,
                                        "delta": {
                                            "role": "assistant" if "role" in chunk.get("choices", [{}])[0].get("delta", {}) else None,
                                            "content": chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                                        },
                                        "finish_reason": chunk.get("choices", [{}])[0].get("finish_reason", None)
                                    }
                                ]
                            }
                            
                            yield standardized_chunk
                            
                        except json.JSONDecodeError:
                            logger.warning(f"无法解析流式响应行: {line}")
                            continue
                        
        except Exception as e:
            logger.error(f"智谱AI流式调用失败: {str(e)}")
            raise
    
    def get_token_usage(self, response: Dict[str, Any]) -> Dict[str, int]:
        """从响应中提取token使用情况"""
        usage = response.get("usage", {})
        return {
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0)
        }
