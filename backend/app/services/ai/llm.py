from typing import List, Dict, Any
from app.core.settings import settings
from app.schemas.common import BaseResponse
from app.utils.cache import cache_manager

class LLMService:
    """LLM服务"""
    
    def __init__(self):
        self.config = settings.ai_config.get('llm', {})
        self.provider = self._init_provider()
        
    def _init_provider(self):
        """初始化LLM提供者"""
        provider_name = self.config.get('provider', 'openai')
        if provider_name == 'openai':
            from .providers.openai import OpenAIProvider
            return OpenAIProvider(self.config)
        elif provider_name == 'anthropic':
            from .providers.anthropic import AnthropicProvider
            return AnthropicProvider(self.config)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider_name}")
    
    async def generate(
        self,
        prompt: str,
        temperature: float = None,
        max_tokens: int = None
    ) -> BaseResponse:
        """生成文本"""
        try:
            response = await self.provider.generate(
                prompt,
                temperature or self.config.get('temperature', 0.7),
                max_tokens or self.config.get('max_tokens', 2000)
            )
            return BaseResponse(
                success=True,
                data=response
            )
        except Exception as e:
            return BaseResponse(
                success=False,
                message=str(e)
            )
    
    @cache_manager.cached(ttl=3600)
    async def analyze_text(self, text: str) -> BaseResponse:
        """分析文本"""
        try:
            result = await self.provider.analyze(text)
            return BaseResponse(
                success=True,
                data=result
            )
        except Exception as e:
            return BaseResponse(
                success=False,
                message=str(e)
            )

# 全局LLM服务实例
llm_service = LLMService()