"""
DeepSeek适配器，处理DeepSeek API调用
"""

from typing import Dict, List, Any, Optional, Union, AsyncGenerator
import litellm
from app.core.logger import get_llm_logger
from app.services.llm.base_adapter import BaseLLMAdapter

logger = get_llm_logger("deepseek_adapter")

class DeepSeekAdapter(BaseLLMAdapter):
    """DeepSeek适配器，处理DeepSeek API调用"""
    
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
        """异步调用DeepSeek补全"""
        try:
            logger.info(f"DeepSeek异步调用: 模型={model}, 消息数={len(messages)}")
            
            # 构建模型路径
            model_path = f"deepseek/{model}"
            
            # 处理DeepSeek模型的特殊要求
            if "deepseek-reasoner" in model:
                # 确保最后一条消息是用户消息
                if messages and messages[-1]["role"] != "user":
                    # 如果最后一条消息不是用户消息，添加一条空的用户消息
                    logger.info(f"DeepSeek模型要求最后一条消息是用户消息，添加空用户消息")
                    messages.append({"role": "user", "content": "请根据上上下文生成内容"})
                
                # 添加额外的参数
                kwargs["prefix_messages"] = True
                logger.info(f"为DeepSeek模型启用prefix_messages模式")
            
            # 调用LiteLLM
            response = await litellm.acompletion(
                model=model_path,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                api_key=self.api_key,
                api_base=self.api_base,
                custom_llm_provider="deepseek",
                **kwargs
            )
            
            return response
        except Exception as e:
            logger.error(f"DeepSeek调用失败: {str(e)}")
            raise
    
    def completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """同步调用DeepSeek补全"""
        try:
            logger.info(f"DeepSeek同步调用: 模型={model}, 消息数={len(messages)}")
            
            # 构建模型路径
            model_path = f"deepseek/{model}"
            
            # 处理DeepSeek模型的特殊要求
            if "deepseek-reasoner" in model:
                # 确保最后一条消息是用户消息
                if messages and messages[-1]["role"] != "user":
                    # 如果最后一条消息不是用户消息，添加一条空的用户消息
                    logger.info(f"DeepSeek模型要求最后一条消息是用户消息，添加空用户消息")
                    messages.append({"role": "user", "content": "请根据上上下文生成内容"})
                
                # 添加额外的参数
                kwargs["prefix_messages"] = True
                logger.info(f"为DeepSeek模型启用prefix_messages模式")
            
            # 调用LiteLLM
            response = litellm.completion(
                model=model_path,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                api_key=self.api_key,
                api_base=self.api_base,
                custom_llm_provider="deepseek",
                **kwargs
            )
            
            return response
        except Exception as e:
            logger.error(f"DeepSeek调用失败: {str(e)}")
            raise
    
    async def acompletion_streaming(
        self,
        model: str,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """异步流式DeepSeek调用，返回一个异步生成器"""
        try:
            logger.info(f"DeepSeek流式调用: 模型={model}, 消息数={len(messages)}")
            
            # 构建模型路径
            model_path = f"deepseek/{model}"
            
            # 处理DeepSeek模型的特殊要求
            if "deepseek-reasoner" in model:
                # 确保最后一条消息是用户消息
                if messages and messages[-1]["role"] != "user":
                    # 如果最后一条消息不是用户消息，添加一条空的用户消息
                    logger.info(f"DeepSeek模型要求最后一条消息是用户消息，添加空用户消息")
                    messages.append({"role": "user", "content": "请根据上上下文生成内容"})
                
                # 添加额外的参数
                kwargs["prefix_messages"] = True
                logger.info(f"为DeepSeek模型启用prefix_messages模式")
            
            # 调用LiteLLM
            response = await litellm.acompletion(
                model=model_path,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                api_key=self.api_key,
                api_base=self.api_base,
                custom_llm_provider="deepseek",
                stream=True,
                **kwargs
            )
            
            async for chunk in response:
                yield chunk
                
        except Exception as e:
            logger.error(f"DeepSeek流式调用失败: {str(e)}")
            raise
    
    def get_token_usage(self, response: Dict[str, Any]) -> Dict[str, int]:
        """从DeepSeek响应中提取token使用情况"""
        token_usage = response.get("usage", {})
        return {
            "prompt_tokens": token_usage.get('prompt_tokens', 0),
            "completion_tokens": token_usage.get('completion_tokens', 0),
            "total_tokens": token_usage.get('total_tokens', 0)
        }
