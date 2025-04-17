from typing import Dict, Any, List
import os
import litellm
from app.core.config import settings
from app.core.logger import get_llm_logger

logger = get_llm_logger("litellm_config")

def configure_litellm():
    """配置LiteLLM，设置模型映射和提供商配置"""

    # 设置API密钥
    if settings.OPENAI_API_KEY:
        os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
    if settings.OPENAI_API_BASE:
        os.environ["OPENAI_API_BASE"] = settings.OPENAI_API_BASE
    if settings.ANTHROPIC_API_KEY:
        os.environ["ANTHROPIC_API_KEY"] = settings.ANTHROPIC_API_KEY
    if settings.DEEPSEEK_API_KEY:
        os.environ["DEEPSEEK_API_KEY"] = settings.DEEPSEEK_API_KEY
    if settings.SILICONFLOW_API_KEY:
        os.environ["SILICONFLOW_API_KEY"] = settings.SILICONFLOW_API_KEY

    # 启用详细日志
    litellm.set_verbose = True

    # 配置模型映射
    model_mappings = {}

    # OpenAI模型 (如果配置了API密钥)
    if settings.OPENAI_API_KEY:
        model_mappings.update({
            "gpt-3.5-turbo": {
                "litellm_params": {
                    "model": "openai/gpt-3.5-turbo",
                    "api_key": settings.OPENAI_API_KEY,
                    "api_base": settings.OPENAI_API_BASE or "https://api.openai.com/v1"
                }
            },
            "gpt-4": {
                "litellm_params": {
                    "model": "openai/gpt-4",
                    "api_key": settings.OPENAI_API_KEY,
                    "api_base": settings.OPENAI_API_BASE or "https://api.openai.com/v1"
                }
            }
        })

    # DeepSeek模型 (如果配置了API密钥)
    if settings.DEEPSEEK_API_KEY:
        model_mappings.update({
            "deepseek-chat": {
                "litellm_params": {
                    "model": "deepseek/deepseek-chat",
                    "api_key": settings.DEEPSEEK_API_KEY,
                    "api_base": settings.DEEPSEEK_API_URL
                }
            },
            "deepseek-reasoner": {
                "litellm_params": {
                    "model": "deepseek/deepseek-reasoner",
                    "api_key": settings.DEEPSEEK_API_KEY,
                    "api_base": settings.DEEPSEEK_API_URL
                }
            }
        })

    # Anthropic模型 (如果配置了API密钥)
    if settings.ANTHROPIC_API_KEY:
        model_mappings.update({
            "claude-2": {
                "litellm_params": {
                    "model": "anthropic/claude-2",
                    "api_key": settings.ANTHROPIC_API_KEY
                }
            }
        })

    # SiliconFlow模型 (如果配置了API密钥)
    if settings.SILICONFLOW_API_KEY:
        model_mappings.update({
            "Qwen/QwQ-32B": {
                "litellm_params": {
                    "model": "openai/gpt-3.5-turbo",  # 使用OpenAI兼容格式
                    "api_key": settings.SILICONFLOW_API_KEY,
                    "api_base": settings.SILICONFLOW_API_URL,
                    "custom_llm_provider": "openai"  # 指定使用OpenAI兼容API
                }
            }
        })

    # 阿里云模型 (如果配置了API密钥)
    if hasattr(settings, 'ALIYUN_API_KEY') and settings.ALIYUN_API_KEY:
        model_mappings.update({
            "qwen-turbo": {
                "litellm_params": {
                    "model": "openai/gpt-3.5-turbo",  # 使用OpenAI兼容格式
                    "api_key": settings.ALIYUN_API_KEY,
                    "api_base": settings.ALIYUN_API_URL,
                    "custom_llm_provider": "openai"  # 指定使用OpenAI兼容API
                }
            },
            "qwen-plus": {
                "litellm_params": {
                    "model": "openai/gpt-4",  # 使用OpenAI兼容格式
                    "api_key": settings.ALIYUN_API_KEY,
                    "api_base": settings.ALIYUN_API_URL,
                    "custom_llm_provider": "openai"  # 指定使用OpenAI兼容API
                }
            }
        })

    # 注册模型映射
    for model_name, config in model_mappings.items():
        try:
            # 构建符合litellm.register_model要求的模型成本字典
            model_cost_dict = {
                model_name: {
                    "litellm_provider": config.get("litellm_params", {}).get("custom_llm_provider", "openai"),
                    "mode": "chat",  # 默认使用chat模式
                    # 可以在这里添加其他必要的参数，如max_tokens, input_cost_per_token, output_cost_per_token
                }
            }
            # 注册模型
            litellm.register_model(model_cost_dict)
            logger.info(f"成功注册模型: {model_name}")
        except Exception as e:
            logger.error(f"注册模型 {model_name} 失败: {str(e)}")

    if not model_mappings:
        logger.warning("没有配置任何模型，请检查API密钥配置")
    else:
        logger.info(f"LiteLLM配置完成，已注册 {len(model_mappings)} 个模型")

    return model_mappings

# 默认配置
MODEL_MAPPINGS = configure_litellm()
