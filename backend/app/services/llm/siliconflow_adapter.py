"""
SiliconFlow适配器，处理SiliconFlow API调用

SiliconFlow是一个聚合的LLM API提供平台，使用OpenAI兼容API
"""

from typing import Dict, List, Any, Optional, Union, AsyncGenerator
import litellm
from app.core.logger import get_llm_logger
from app.services.llm.base_adapter import BaseLLMAdapter

logger = get_llm_logger("siliconflow_adapter")

class SiliconFlowAdapter(BaseLLMAdapter):
    """SiliconFlow适配器，处理SiliconFlow API调用"""
    
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
        """异步调用SiliconFlow补全"""
        try:
            logger.info(f"SiliconFlow异步调用: 模型={model}, 消息数={len(messages)}")
            
            # SiliconFlow使用OpenAI兼容API，但需要指定实际模型名称
            # 例如：Qwen/QwQ-32B
            
            # 构建模型路径 - 使用OpenAI兼容格式
            model_path = "openai/gpt-3.5-turbo"  # 使用OpenAI兼容格式
            
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
            logger.error(f"SiliconFlow调用失败: {str(e)}")
            raise
    
    def completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """同步调用SiliconFlow补全"""
        try:
            logger.info(f"SiliconFlow同步调用: 模型={model}, 消息数={len(messages)}")
            
            # SiliconFlow使用OpenAI兼容API，但需要指定实际模型名称
            # 例如：Qwen/QwQ-32B
            
            # 构建模型路径 - 使用OpenAI兼容格式
            model_path = "openai/gpt-3.5-turbo"  # 使用OpenAI兼容格式
            
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
            logger.error(f"SiliconFlow调用失败: {str(e)}")
            raise
    
    async def acompletion_streaming(
        self,
        model: str,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """异步流式SiliconFlow调用，返回一个异步生成器"""
        try:
            logger.info(f"SiliconFlow流式调用: 模型={model}, 消息数={len(messages)}")
            
            # SiliconFlow使用OpenAI兼容API，但需要指定实际模型名称
            # 例如：Qwen/QwQ-32B
            
            # 构建模型路径 - 使用OpenAI兼容格式
            model_path = "openai/gpt-3.5-turbo"  # 使用OpenAI兼容格式
            
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
            logger.error(f"SiliconFlow流式调用失败: {str(e)}")
            raise
    
    def get_token_usage(self, response: Dict[str, Any]) -> Dict[str, int]:
        """从SiliconFlow响应中提取token使用情况"""
        token_usage = response.get("usage", {})
        return {
            "prompt_tokens": token_usage.get('prompt_tokens', 0),
            "completion_tokens": token_usage.get('completion_tokens', 0),
            "total_tokens": token_usage.get('total_tokens', 0)
        }
