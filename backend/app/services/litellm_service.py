from typing import Dict, List, Any, Optional, Union
import os
import json
from pathlib import Path
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import litellm
from litellm import completion, acompletion
from app.core.config import settings
from app.core.logger import get_llm_logger
from app.services.token_service import token_service
from app.utils.token_counter import token_counter
from app.core.context import get_current_user_id
from app.services.litellm_config import MODEL_MAPPINGS

# 创建LLM日志器
logger = get_llm_logger("litellm_service")

class LiteLLMService:
    """LLM服务，使用LiteLLM支持多种模型"""

    def __init__(self):
        """初始化LLM服务"""
        # 获取可用模型列表
        self.available_models = list(MODEL_MAPPINGS.keys())

        # 设置回退模型
        self.fallback_models = []

        # 添加OpenAI回退模型
        if "gpt-3.5-turbo" in self.available_models:
            self.fallback_models.append({"model": "gpt-3.5-turbo"})

        # 添加DeepSeek回退模型
        if settings.DEEPSEEK_MODEL in self.available_models:
            self.fallback_models.append({"model": settings.DEEPSEEK_MODEL})

        # 添加阿里云回退模型
        if "qwen-turbo" in self.available_models:
            self.fallback_models.append({"model": "qwen-turbo"})

        logger.info(f"LiteLLM服务初始化完成，可用模型: {self.available_models}")
        logger.info(f"回退模型: {[m['model'] for m in self.fallback_models]}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((Exception)),
        reraise=True
    )
    async def acompletion(
        self,
        model: str = None,
        messages: List[Dict[str, str]] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ):
        """异步调用LLM补全"""
        try:
            # 使用默认模型
            if model is None:
                model = settings.DEFAULT_MODEL

            # 检查模型是否可用
            if model not in self.available_models:
                available_models_str = ", ".join(self.available_models)
                logger.warning(f"模型 {model} 不可用，可用模型: {available_models_str}")

                # 如果有回退模型，使用第一个回退模型
                if self.fallback_models:
                    model = self.fallback_models[0]["model"]
                    logger.info(f"使用回退模型: {model}")
                else:
                    raise ValueError(f"模型 {model} 不可用，且没有可用的回退模型")

            # 记录请求
            logger.info(f"LLM请求: 模型={model}, 消息数={len(messages)}")

            # 调用LLM
            response = await acompletion(
                model=model,  # 直接使用模型名称，LiteLLM会通过register_model查找配置
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )

            # 记录响应
            token_usage = response.get("usage", {})
            prompt_tokens = token_usage.get('prompt_tokens', 0)
            completion_tokens = token_usage.get('completion_tokens', 0)
            total_tokens = token_usage.get('total_tokens', 0)

            logger.info(
                f"LLM响应: 模型={model}, "
                f"输入tokens={prompt_tokens}, "
                f"输出tokens={completion_tokens}, "
                f"总tokens={total_tokens}"
            )

            # 记录token使用
            token_service.record_usage(
                model=model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                service="litellm_service",
                task=kwargs.get("task", "acompletion"),
                user_id=get_current_user_id()
            )

            return response

        except Exception as e:
            logger.error(f"LLM调用失败: {str(e)}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((Exception)),
        reraise=True
    )
    def completion(
        self,
        model: str = None,
        messages: List[Dict[str, str]] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ):
        """同步调用LLM补全"""
        try:
            # 使用默认模型
            if model is None:
                model = settings.DEFAULT_MODEL

            # 检查模型是否可用
            if model not in self.available_models:
                available_models_str = ", ".join(self.available_models)
                logger.warning(f"模型 {model} 不可用，可用模型: {available_models_str}")

                # 如果有回退模型，使用第一个回退模型
                if self.fallback_models:
                    model = self.fallback_models[0]["model"]
                    logger.info(f"使用回退模型: {model}")
                else:
                    raise ValueError(f"模型 {model} 不可用，且没有可用的回退模型")

            # 记录请求
            logger.info(f"LLM请求: 模型={model}, 消息数={len(messages)}")

            # 调用LLM
            response = completion(
                model=model,  # 直接使用模型名称，LiteLLM会通过register_model查找配置
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )

            # 记录响应
            token_usage = response.get("usage", {})
            prompt_tokens = token_usage.get('prompt_tokens', 0)
            completion_tokens = token_usage.get('completion_tokens', 0)
            total_tokens = token_usage.get('total_tokens', 0)

            logger.info(
                f"LLM响应: 模型={model}, "
                f"输入tokens={prompt_tokens}, "
                f"输出tokens={completion_tokens}, "
                f"总tokens={total_tokens}"
            )

            # 记录token使用
            token_service.record_usage(
                model=model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                service="litellm_service",
                task=kwargs.get("task", "completion"),
                user_id=get_current_user_id()
            )

            return response

        except Exception as e:
            logger.error(f"LLM调用失败: {str(e)}")
            raise

    async def acompletion_with_fallbacks(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ):
        """带有回退的异步LLM调用"""
        # 检查是否有可用模型
        if not self.available_models:
            raise ValueError("没有可用的LLM模型，请检查API密钥配置")

        # 检查默认模型是否可用
        default_model = settings.DEFAULT_MODEL
        if default_model not in self.available_models:
            # 如果默认模型不可用，使用第一个可用模型
            default_model = self.available_models[0]
            logger.warning(f"默认模型 {settings.DEFAULT_MODEL} 不可用，使用 {default_model} 代替")

        # 尝试主模型
        try:
            return await self.acompletion(
                model=default_model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
        except Exception as e:
            logger.warning(f"主模型调用失败，尝试回退: {str(e)}")

            # 尝试回退模型
            for fallback in self.fallback_models:
                fallback_model = fallback["model"]
                # 跳过主模型
                if fallback_model == default_model:
                    continue
                # 跳过不可用的模型
                if fallback_model not in self.available_models:
                    continue

                try:
                    return await self.acompletion(
                        model=fallback_model,
                        messages=messages,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        **kwargs
                    )
                except Exception as e:
                    logger.warning(f"回退模型 {fallback_model} 调用失败: {str(e)}")

            # 所有模型都失败
            raise Exception("所有LLM模型调用都失败")

# 创建全局LiteLLM服务实例
litellm_service = LiteLLMService()
