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

    # 从配置文件中获取模型提供商映射
    model_providers = settings.config.get("llm", {}).get("model_providers", {})
    logger.info(f"从配置文件加载模型提供商映射: {model_providers}")

    # 配置模型映射
    model_mappings = {}

    # OpenAI模型 (如果配置了API密钥)
    if settings.OPENAI_API_KEY:
        openai_models = {
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
        }

        # 从配置文件中获取提供商类型
        for model_name, model_config in openai_models.items():
            provider = model_providers.get(model_name, "openai")
            model_config["litellm_params"]["custom_llm_provider"] = provider
            logger.info(f"模型 {model_name} 使用提供商: {provider}")

        model_mappings.update(openai_models)

    # DeepSeek模型 (如果配置了API密钥)
    if settings.DEEPSEEK_API_KEY:
        deepseek_models = {
            "deepseek-chat": {
                "litellm_params": {
                    "model": "deepseek/deepseek-chat",
                    "api_key": settings.DEEPSEEK_API_KEY,
                    "api_base": settings.DEEPSEEK_API_URL,
                }
            },
            "deepseek-reasoner": {
                "litellm_params": {
                    "model": "deepseek/deepseek-reasoner",
                    "api_key": settings.DEEPSEEK_API_KEY,
                    "api_base": settings.DEEPSEEK_API_URL,
                }
            }
        }

        # 从配置文件中获取提供商类型
        for model_name, model_config in deepseek_models.items():
            provider = model_providers.get(model_name, "deepseek")
            model_config["litellm_params"]["custom_llm_provider"] = provider
            logger.info(f"模型 {model_name} 使用提供商: {provider}")

        model_mappings.update(deepseek_models)

    # Anthropic模型 (如果配置了API密钥)
    if settings.ANTHROPIC_API_KEY:
        anthropic_models = {
            "claude-2": {
                "litellm_params": {
                    "model": "anthropic/claude-2",
                    "api_key": settings.ANTHROPIC_API_KEY
                }
            }
        }

        # 从配置文件中获取提供商类型
        for model_name, model_config in anthropic_models.items():
            provider = model_providers.get(model_name, "anthropic")
            model_config["litellm_params"]["custom_llm_provider"] = provider
            logger.info(f"模型 {model_name} 使用提供商: {provider}")

        model_mappings.update(anthropic_models)

    # SiliconFlow模型 (如果配置了API密钥)
    if settings.SILICONFLOW_API_KEY:
        siliconflow_models = {
            "Qwen/QwQ-32B": {
                "litellm_params": {
                    "model": "openai/gpt-3.5-turbo",  # 使用OpenAI兼容格式
                    "api_key": settings.SILICONFLOW_API_KEY,
                    "api_base": settings.SILICONFLOW_API_URL
                }
            }
        }

        # 从配置文件中获取提供商类型
        for model_name, model_config in siliconflow_models.items():
            provider = model_providers.get(model_name, "openai")  # 默认使用OpenAI兼容API
            model_config["litellm_params"]["custom_llm_provider"] = provider
            logger.info(f"模型 {model_name} 使用提供商: {provider}")

        model_mappings.update(siliconflow_models)

    # 阿里云模型 (如果配置了API密钥)
    if hasattr(settings, 'ALIYUN_API_KEY') and settings.ALIYUN_API_KEY:
        aliyun_models = {
            "qwen-turbo": {
                "litellm_params": {
                    "model": "openai/gpt-3.5-turbo",  # 使用OpenAI兼容格式
                    "api_key": settings.ALIYUN_API_KEY,
                    "api_base": settings.ALIYUN_API_URL
                }
            },
            "qwen-plus": {
                "litellm_params": {
                    "model": "openai/gpt-4",  # 使用OpenAI兼容格式
                    "api_key": settings.ALIYUN_API_KEY,
                    "api_base": settings.ALIYUN_API_URL
                }
            }
        }

        # 从配置文件中获取提供商类型
        for model_name, model_config in aliyun_models.items():
            provider = model_providers.get(model_name, "openai")  # 默认使用OpenAI兼容API
            model_config["litellm_params"]["custom_llm_provider"] = provider
            logger.info(f"模型 {model_name} 使用提供商: {provider}")

        model_mappings.update(aliyun_models)

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
