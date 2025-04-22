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
logger = get_llm_logger("llm_service")

class LLMService:
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

        logger.info(f"LLM服务初始化完成，可用模型: {self.available_models}")
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
            # 检查模型是否在MODEL_MAPPINGS中
            if model in MODEL_MAPPINGS:
                model_config = MODEL_MAPPINGS[model].get("litellm_params", {})
                provider = model_config.get("custom_llm_provider")
                model_path = model_config.get("model")

                # 处理DeepSeek模型的特殊要求
                if provider == "deepseek" and "deepseek-reasoner" in model_path:
                    # 确保最后一条消息是用户消息
                    if messages and messages[-1]["role"] != "user":
                        # 如果最后一条消息不是用户消息，添加一条空的用户消息
                        logger.info(f"DeepSeek模型要求最后一条消息是用户消息，添加空用户消息")
                        messages.append({"role": "user", "content": "请根据上上下文生成内容"})

                    # 添加额外的参数
                    kwargs["prefix_messages"] = True
                    logger.info(f"为DeepSeek模型启用prefix_messages模式")

                if provider and model_path:
                    logger.info(f"使用完整模型配置调用LLM: 提供商={provider}, 模型={model_path}")
                    # 使用完整模型路径调用
                    response = await acompletion(
                        model=model_path,
                        messages=messages,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        custom_llm_provider=provider,
                        **kwargs
                    )
                else:
                    logger.warning(f"模型{model}的配置不完整，使用默认调用方式")
                    response = await acompletion(
                        model=model,
                        messages=messages,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        **kwargs
                    )
            else:
                # 直接使用模型名称
                logger.warning(f"模型{model}不在配置中，使用默认调用方式")
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
                task=kwargs.get("task", "acompletion"),
                task_type=kwargs.get("task_type", "default"),
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
            # 检查模型是否在MODEL_MAPPINGS中
            if model in MODEL_MAPPINGS:
                model_config = MODEL_MAPPINGS[model].get("litellm_params", {})
                provider = model_config.get("custom_llm_provider")
                model_path = model_config.get("model")

                # 处理DeepSeek模型的特殊要求
                if provider == "deepseek" and "deepseek-reasoner" in model_path:
                    # 确保最后一条消息是用户消息
                    if messages and messages[-1]["role"] != "user":
                        # 如果最后一条消息不是用户消息，添加一条空的用户消息
                        logger.info(f"DeepSeek模型要求最后一条消息是用户消息，添加空用户消息")
                        messages.append({"role": "user", "content": "请根据上上下文生成内容"})

                    # 添加额外的参数
                    kwargs["prefix_messages"] = True
                    logger.info(f"为DeepSeek模型启用prefix_messages模式")

                if provider and model_path:
                    logger.info(f"使用完整模型配置调用LLM: 提供商={provider}, 模型={model_path}")
                    # 使用完整模型路径调用
                    response = completion(
                        model=model_path,
                        messages=messages,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        custom_llm_provider=provider,
                        **kwargs
                    )
                else:
                    logger.warning(f"模型{model}的配置不完整，使用默认调用方式")
                    response = completion(
                        model=model,
                        messages=messages,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        **kwargs
                    )
            else:
                # 直接使用模型名称
                logger.warning(f"模型{model}不在配置中，使用默认调用方式")
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
                task=kwargs.get("task", "completion"),
                task_type=kwargs.get("task_type", "default"),
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

    async def acompletion_streaming(
        self,
        model: str = None,
        messages: List[Dict[str, str]] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ):
        """异步流式LLM调用，返回一个异步生成器"""
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
            logger.info(f"LLM流式请求: 模型={model}, 消息数={len(messages)}")

            # 检查模型是否在MODEL_MAPPINGS中
            if model in MODEL_MAPPINGS:
                model_config = MODEL_MAPPINGS[model].get("litellm_params", {})
                provider = model_config.get("custom_llm_provider")
                model_path = model_config.get("model")

                # 处理DeepSeek模型的特殊要求
                if provider == "deepseek" and "deepseek-reasoner" in model_path:
                    # 确保最后一条消息是用户消息
                    if messages and messages[-1]["role"] != "user":
                        # 如果最后一条消息不是用户消息，添加一条空的用户消息
                        logger.info(f"DeepSeek模型要求最后一条消息是用户消息，添加空用户消息")
                        messages.append({"role": "user", "content": "请根据上上下文生成内容"})

                    # 添加额外的参数
                    kwargs["prefix_messages"] = True
                    logger.info(f"为DeepSeek模型启用prefix_messages模式")

                if provider and model_path:
                    logger.info(f"使用完整模型配置调用流式LLM: 提供商={provider}, 模型={model_path}")
                    # 使用litellm的流式调用
                    response = await litellm.acompletion(
                        model=model_path,
                        messages=messages,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        custom_llm_provider=provider,
                        stream=True,  # 启用流式输出
                        **kwargs
                    )
                else:
                    logger.warning(f"模型{model}的配置不完整，使用默认调用方式")
                    response = await litellm.acompletion(
                        model=model,
                        messages=messages,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        stream=True,  # 启用流式输出
                        **kwargs
                    )
            else:
                # 直接使用模型名称
                logger.warning(f"模型{model}不在配置中，使用默认调用方式")
                response = await litellm.acompletion(
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stream=True,  # 启用流式输出
                    **kwargs
                )

            # 返回流式响应
            async for chunk in response:
                yield chunk

            # 记录token使用
            # 注意：流式调用的token统计需要在完成后进行
            # 这里只是一个简化的实现
            token_service.record_usage(
                model=model,
                prompt_tokens=len(str(messages)) // 4,  # 粗略估计
                completion_tokens=1000,  # 粗略估计
                service="llm_service",
                task=kwargs.get("task", "acompletion_streaming"),
                task_type=kwargs.get("task_type", "default"),
                user_id=get_current_user_id()
            )

        except Exception as e:
            logger.error(f"LLM流式调用失败: {str(e)}")
            raise

# 创建全局LLM服务实例
llm_service = LLMService()
