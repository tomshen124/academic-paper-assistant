"""
LLM适配器工厂，负责创建适当的适配器
"""

from typing import Dict, Any, Optional
from app.core.config import settings
from app.core.logger import get_llm_logger
from app.services.llm.base_adapter import BaseLLMAdapter
from app.services.llm.openai_adapter import OpenAIAdapter
from app.services.llm.deepseek_adapter import DeepSeekAdapter
from app.services.llm.anthropic_adapter import AnthropicAdapter
from app.services.llm.qwen_adapter import QwenAdapter
from app.services.llm.siliconflow_adapter import SiliconFlowAdapter
from app.services.llm.zhipuai_adapter import ZhipuAIAdapter

logger = get_llm_logger("adapter_factory")

class LLMAdapterFactory:
    """LLM适配器工厂，负责创建适当的适配器"""

    @staticmethod
    def create_adapter(provider: str, config: Dict[str, Any]) -> Optional[BaseLLMAdapter]:
        """创建适配器"""
        try:
            logger.info(f"创建适配器: 提供商={provider}")

            if provider == "openai":
                return OpenAIAdapter(
                    api_key=config.get("api_key", settings.OPENAI_API_KEY),
                    api_base=config.get("api_base", settings.OPENAI_API_BASE)
                )
            elif provider == "deepseek":
                return DeepSeekAdapter(
                    api_key=config.get("api_key", settings.DEEPSEEK_API_KEY),
                    api_base=config.get("api_base", settings.DEEPSEEK_API_URL)
                )
            elif provider == "anthropic":
                return AnthropicAdapter(
                    api_key=config.get("api_key", settings.ANTHROPIC_API_KEY)
                )
            elif provider == "qwen" or (provider == "openai" and "qwen" in config.get("model", "")):
                return QwenAdapter(
                    api_key=config.get("api_key", settings.ALIYUN_API_KEY),
                    api_base=config.get("api_base", settings.ALIYUN_API_URL)
                )
            elif provider == "siliconflow" or (provider == "openai" and "siliconflow" in config.get("model", "").lower()):
                return SiliconFlowAdapter(
                    api_key=config.get("api_key", settings.SILICONFLOW_API_KEY),
                    api_base=config.get("api_base", settings.SILICONFLOW_API_URL)
                )
            elif provider == "zhipuai" or (provider == "openai" and "glm" in config.get("model", "").lower()):
                return ZhipuAIAdapter(
                    api_key=config.get("api_key", settings.ZHIPUAI_API_KEY),
                    api_base=config.get("api_base", settings.ZHIPUAI_API_URL)
                )
            else:
                logger.warning(f"未知的提供商: {provider}")
                return None
        except Exception as e:
            logger.error(f"创建适配器失败: {str(e)}")
            return None
