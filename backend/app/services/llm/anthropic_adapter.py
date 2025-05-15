"""
Anthropic适配器，处理Anthropic API调用
"""

from typing import Dict, List, Any, Optional, Union, AsyncGenerator
import litellm
from app.core.logger import get_llm_logger
from app.services.llm.base_adapter import BaseLLMAdapter

logger = get_llm_logger("anthropic_adapter")

class AnthropicAdapter(BaseLLMAdapter):
    """Anthropic适配器，处理Anthropic API调用"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        
    async def acompletion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """异步调用Anthropic补全"""
        try:
            logger.info(f"Anthropic异步调用: 模型={model}, 消息数={len(messages)}")
            
            # 构建模型路径
            model_path = f"anthropic/{model}"
            
            # 调用LiteLLM
            response = await litellm.acompletion(
                model=model_path,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                api_key=self.api_key,
                custom_llm_provider="anthropic",
                **kwargs
            )
            
            return response
        except Exception as e:
            logger.error(f"Anthropic调用失败: {str(e)}")
            raise
    
    def completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """同步调用Anthropic补全"""
        try:
            logger.info(f"Anthropic同步调用: 模型={model}, 消息数={len(messages)}")
            
            # 构建模型路径
            model_path = f"anthropic/{model}"
            
            # 调用LiteLLM
            response = litellm.completion(
                model=model_path,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                api_key=self.api_key,
                custom_llm_provider="anthropic",
                **kwargs
            )
            
            return response
        except Exception as e:
            logger.error(f"Anthropic调用失败: {str(e)}")
            raise
    
    async def acompletion_streaming(
        self,
        model: str,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """异步流式Anthropic调用，返回一个异步生成器"""
        try:
            logger.info(f"Anthropic流式调用: 模型={model}, 消息数={len(messages)}")
            
            # 构建模型路径
            model_path = f"anthropic/{model}"
            
            # 调用LiteLLM
            response = await litellm.acompletion(
                model=model_path,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                api_key=self.api_key,
                custom_llm_provider="anthropic",
                stream=True,
                **kwargs
            )
            
            async for chunk in response:
                yield chunk
                
        except Exception as e:
            logger.error(f"Anthropic流式调用失败: {str(e)}")
            raise
    
    def get_token_usage(self, response: Dict[str, Any]) -> Dict[str, int]:
        """从Anthropic响应中提取token使用情况"""
        token_usage = response.get("usage", {})
        return {
            "prompt_tokens": token_usage.get('prompt_tokens', 0),
            "completion_tokens": token_usage.get('completion_tokens', 0),
            "total_tokens": token_usage.get('total_tokens', 0)
        }
