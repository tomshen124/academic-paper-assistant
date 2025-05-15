"""
阿里云千问适配器，处理阿里云千问API调用
"""

from typing import Dict, List, Any, Optional, Union, AsyncGenerator
import litellm
from app.core.logger import get_llm_logger
from app.services.llm.base_adapter import BaseLLMAdapter

logger = get_llm_logger("qwen_adapter")

class QwenAdapter(BaseLLMAdapter):
    """阿里云千问适配器，处理阿里云千问API调用"""
    
    def __init__(self, api_key: str, api_base: Optional[str] = None):
        self.api_key = api_key
        self.api_base = api_base
        
    async def acompletion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """异步调用阿里云千问补全"""
        try:
            logger.info(f"阿里云千问异步调用: 模型={model}, 消息数={len(messages)}")
            
            # 阿里云千问使用OpenAI兼容API，所以使用gpt-3.5-turbo或gpt-4作为模型路径
            if model == "qwen-turbo":
                model_path = "openai/gpt-3.5-turbo"
            elif model == "qwen-plus":
                model_path = "openai/gpt-4"
            else:
                model_path = f"openai/{model}"
            
            # 调用LiteLLM
            response = await litellm.acompletion(
                model=model_path,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                api_key=self.api_key,
                api_base=self.api_base,
                custom_llm_provider="openai",  # 使用OpenAI兼容API
                **kwargs
            )
            
            return response
        except Exception as e:
            logger.error(f"阿里云千问调用失败: {str(e)}")
            raise
    
    def completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """同步调用阿里云千问补全"""
        try:
            logger.info(f"阿里云千问同步调用: 模型={model}, 消息数={len(messages)}")
            
            # 阿里云千问使用OpenAI兼容API，所以使用gpt-3.5-turbo或gpt-4作为模型路径
            if model == "qwen-turbo":
                model_path = "openai/gpt-3.5-turbo"
            elif model == "qwen-plus":
                model_path = "openai/gpt-4"
            else:
                model_path = f"openai/{model}"
            
            # 调用LiteLLM
            response = litellm.completion(
                model=model_path,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                api_key=self.api_key,
                api_base=self.api_base,
                custom_llm_provider="openai",  # 使用OpenAI兼容API
                **kwargs
            )
            
            return response
        except Exception as e:
            logger.error(f"阿里云千问调用失败: {str(e)}")
            raise
    
    async def acompletion_streaming(
        self,
        model: str,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """异步流式阿里云千问调用，返回一个异步生成器"""
        try:
            logger.info(f"阿里云千问流式调用: 模型={model}, 消息数={len(messages)}")
            
            # 阿里云千问使用OpenAI兼容API，所以使用gpt-3.5-turbo或gpt-4作为模型路径
            if model == "qwen-turbo":
                model_path = "openai/gpt-3.5-turbo"
            elif model == "qwen-plus":
                model_path = "openai/gpt-4"
            else:
                model_path = f"openai/{model}"
            
            # 调用LiteLLM
            response = await litellm.acompletion(
                model=model_path,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                api_key=self.api_key,
                api_base=self.api_base,
                custom_llm_provider="openai",  # 使用OpenAI兼容API
                stream=True,
                **kwargs
            )
            
            async for chunk in response:
                yield chunk
                
        except Exception as e:
            logger.error(f"阿里云千问流式调用失败: {str(e)}")
            raise
    
    def get_token_usage(self, response: Dict[str, Any]) -> Dict[str, int]:
        """从阿里云千问响应中提取token使用情况"""
        token_usage = response.get("usage", {})
        return {
            "prompt_tokens": token_usage.get('prompt_tokens', 0),
            "completion_tokens": token_usage.get('completion_tokens', 0),
            "total_tokens": token_usage.get('total_tokens', 0)
        }
