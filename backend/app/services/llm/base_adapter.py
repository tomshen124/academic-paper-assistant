"""
LLM适配器基类，定义所有适配器必须实现的接口
"""

from typing import Dict, List, Any, Optional, Union, AsyncGenerator
from abc import ABC, abstractmethod

class BaseLLMAdapter(ABC):
    """LLM适配器基类，定义所有适配器必须实现的接口"""
    
    @abstractmethod
    async def acompletion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """异步调用LLM补全"""
        pass
    
    @abstractmethod
    def completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """同步调用LLM补全"""
        pass
    
    @abstractmethod
    async def acompletion_streaming(
        self,
        model: str,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """异步流式LLM调用，返回一个异步生成器"""
        pass
    
    @abstractmethod
    def get_token_usage(self, response: Dict[str, Any]) -> Dict[str, int]:
        """从响应中提取token使用情况"""
        pass
