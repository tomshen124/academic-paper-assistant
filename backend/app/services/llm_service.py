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

# 创建LLM日志器
logger = get_llm_logger("llm_service")

class LLMService:
    """LLM服务，使用LiteLLM支持多种模型"""

    def __init__(self):
        """初始化LLM服务"""
        # 设置API密钥
        if settings.OPENAI_API_KEY:
            os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
        if settings.OPENAI_API_BASE:
            os.environ["OPENAI_API_BASE"] = settings.OPENAI_API_BASE
        if settings.ANTHROPIC_API_KEY:
            os.environ["ANTHROPIC_API_KEY"] = settings.ANTHROPIC_API_KEY
        if settings.DEEPSEEK_API_KEY:
            os.environ["DEEPSEEK_API_KEY"] = settings.DEEPSEEK_API_KEY

        # 配置LiteLLM
        litellm.set_verbose = True

        # 启用缓存
        # 注释掉缓存代码，因为当前版本的litellm不支持
        # if settings.LITELLM_CACHE_ENABLE:
        #     cache_dir = Path(settings.LITELLM_CACHE_FOLDER)
        #     cache_dir.mkdir(parents=True, exist_ok=True)
        #     litellm.cache = litellm.Cache(type="disk", cache_path=str(cache_dir))

        # 设置回退模型
        self.fallback_models = [
            {"model": "gpt-3.5-turbo"},
            {"model": settings.DEEPSEEK_MODEL, "api_base": settings.DEEPSEEK_API_URL}
        ]

        logger.info("LLM服务初始化完成")

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

            # 记录请求
            logger.info(f"LLM请求: 模型={model}, 消息数={len(messages)}")

            # 调用LLM
            response = await acompletion(
                model=model,
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
                service="llm_service",
                task=kwargs.get("task", "acompletion")
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

            # 记录请求
            logger.info(f"LLM请求: 模型={model}, 消息数={len(messages)}")

            # 调用LLM
            response = completion(
                model=model,
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
                service="llm_service",
                task=kwargs.get("task", "completion")
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
        # 尝试主模型
        try:
            return await self.acompletion(
                model=settings.DEFAULT_MODEL,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
        except Exception as e:
            logger.warning(f"主模型调用失败，尝试回退: {str(e)}")

            # 尝试回退模型
            for fallback in self.fallback_models:
                try:
                    return await self.acompletion(
                        model=fallback["model"],
                        messages=messages,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        api_base=fallback.get("api_base"),
                        **kwargs
                    )
                except Exception as e:
                    logger.warning(f"回退模型 {fallback['model']} 调用失败: {str(e)}")

            # 所有模型都失败
            raise Exception("所有LLM模型调用都失败")

# 创建全局LLM服务实例
llm_service = LLMService()
