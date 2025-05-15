"""
LLM服务，使用适配器模式支持多种模型
"""

from typing import Dict, List, Any, Optional, Union, AsyncGenerator
import os
import json
from pathlib import Path
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.core.config import settings
from app.core.logger import get_llm_logger
from app.services.token_service import token_service
from app.utils.token_counter import token_counter
from app.core.context import get_current_user_id
from app.services.llm.adapter_factory import LLMAdapterFactory
from app.services.llm.base_adapter import BaseLLMAdapter

# 创建LLM日志器
logger = get_llm_logger("llm_service")

class LLMService:
    """LLM服务，使用适配器模式支持多种模型"""

    def __init__(self):
        """初始化LLM服务"""
        # 加载模型配置
        self.model_configs = self._load_model_configs()

        # 获取可用模型列表
        self.available_models = list(self.model_configs.keys())

        # 创建适配器缓存
        self.adapters = {}

        # 设置回退模型
        self.fallback_models = []

        # 初始化token使用统计
        self.token_usage = {
            "total_tokens": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0
        }

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

    def _load_model_configs(self) -> Dict[str, Dict[str, Any]]:
        """加载模型配置"""
        model_configs = {}

        # 从配置文件中获取模型提供商映射
        model_providers = settings.config.get("llm", {}).get("model_providers", {})

        # OpenAI模型 (如果配置了API密钥)
        if settings.OPENAI_API_KEY:
            openai_models = {
                "gpt-3.5-turbo": {
                    "provider": model_providers.get("gpt-3.5-turbo", "openai"),
                    "config": {
                        "api_key": settings.OPENAI_API_KEY,
                        "api_base": settings.OPENAI_API_BASE,
                        "model": "gpt-3.5-turbo"
                    }
                },
                "gpt-4": {
                    "provider": model_providers.get("gpt-4", "openai"),
                    "config": {
                        "api_key": settings.OPENAI_API_KEY,
                        "api_base": settings.OPENAI_API_BASE,
                        "model": "gpt-4"
                    }
                }
            }
            model_configs.update(openai_models)

        # DeepSeek模型 (如果配置了API密钥)
        if settings.DEEPSEEK_API_KEY:
            deepseek_models = {
                "deepseek-chat": {
                    "provider": model_providers.get("deepseek-chat", "deepseek"),
                    "config": {
                        "api_key": settings.DEEPSEEK_API_KEY,
                        "api_base": settings.DEEPSEEK_API_URL,
                        "model": "deepseek-chat"
                    }
                },
                "deepseek-reasoner": {
                    "provider": model_providers.get("deepseek-reasoner", "deepseek"),
                    "config": {
                        "api_key": settings.DEEPSEEK_API_KEY,
                        "api_base": settings.DEEPSEEK_API_URL,
                        "model": "deepseek-reasoner"
                    }
                }
            }
            model_configs.update(deepseek_models)

        # Anthropic模型 (如果配置了API密钥)
        if settings.ANTHROPIC_API_KEY:
            anthropic_models = {
                "claude-2": {
                    "provider": model_providers.get("claude-2", "anthropic"),
                    "config": {
                        "api_key": settings.ANTHROPIC_API_KEY,
                        "model": "claude-2"
                    }
                }
            }
            model_configs.update(anthropic_models)

        # 阿里云模型 (如果配置了API密钥)
        if hasattr(settings, 'ALIYUN_API_KEY') and settings.ALIYUN_API_KEY:
            aliyun_models = {
                "qwen-turbo": {
                    "provider": model_providers.get("qwen-turbo", "openai"),
                    "config": {
                        "api_key": settings.ALIYUN_API_KEY,
                        "api_base": settings.ALIYUN_API_URL,
                        "model": "qwen-turbo"
                    }
                },
                "qwen-plus": {
                    "provider": model_providers.get("qwen-plus", "openai"),
                    "config": {
                        "api_key": settings.ALIYUN_API_KEY,
                        "api_base": settings.ALIYUN_API_URL,
                        "model": "qwen-plus"
                    }
                }
            }
            model_configs.update(aliyun_models)

        # SiliconFlow模型 (如果配置了API密钥)
        if settings.SILICONFLOW_API_KEY:
            siliconflow_models = {
                "Qwen/QwQ-32B": {
                    "provider": model_providers.get("Qwen/QwQ-32B", "siliconflow"),
                    "config": {
                        "api_key": settings.SILICONFLOW_API_KEY,
                        "api_base": settings.SILICONFLOW_API_URL,
                        "model": "Qwen/QwQ-32B"
                    }
                },
                "siliconflow": {
                    "provider": "siliconflow",
                    "config": {
                        "api_key": settings.SILICONFLOW_API_KEY,
                        "api_base": settings.SILICONFLOW_API_URL,
                        "model": "Qwen/QwQ-32B"  # 默认使用QwQ-32B模型
                    }
                }
            }
            model_configs.update(siliconflow_models)

        return model_configs

    def _get_adapter(self, model: str) -> BaseLLMAdapter:
        """获取或创建适配器"""
        if model not in self.model_configs:
            raise ValueError(f"未知的模型: {model}")

        if model not in self.adapters:
            model_config = self.model_configs[model]
            provider = model_config["provider"]
            config = model_config["config"]

            adapter = LLMAdapterFactory.create_adapter(provider, config)
            if adapter is None:
                raise ValueError(f"无法创建适配器: 提供商={provider}")

            self.adapters[model] = adapter

        return self.adapters[model]

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
        agent_type: str = None,  # 新增参数，用于指定智能体类型
        **kwargs
    ):
        """异步调用LLM补全"""
        try:
            # 如果指定了智能体类型，从配置中获取对应的模型
            if agent_type:
                agent_configs = settings.config.get("llm", {}).get("agent_configs", {})
                agent_config = agent_configs.get(agent_type, {})
                if agent_config and "model" in agent_config:
                    model = agent_config.get("model")
                    # 如果智能体配置中有温度参数，使用智能体的温度参数
                    if "temperature" in agent_config:
                        temperature = agent_config.get("temperature")
                    logger.info(f"使用智能体 {agent_type} 配置的模型: {model}, 温度: {temperature}")

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

            # 获取适配器
            adapter = self._get_adapter(model)

            # 调用适配器
            response = await adapter.acompletion(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )

            # 记录响应
            token_usage = adapter.get_token_usage(response)
            prompt_tokens = token_usage.get('prompt_tokens', 0)
            completion_tokens = token_usage.get('completion_tokens', 0)
            total_tokens = token_usage.get('total_tokens', 0)

            logger.info(
                f"LLM响应: 模型={model}, "
                f"输入tokens={prompt_tokens}, "
                f"输出tokens={completion_tokens}, "
                f"总tokens={total_tokens}"
            )

            # 更新内部token使用统计
            self.token_usage["prompt_tokens"] += prompt_tokens
            self.token_usage["completion_tokens"] += completion_tokens
            self.token_usage["total_tokens"] += total_tokens

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
        agent_type: str = None,  # 新增参数，用于指定智能体类型
        **kwargs
    ):
        """同步调用LLM补全"""
        try:
            # 如果指定了智能体类型，从配置中获取对应的模型
            if agent_type:
                agent_configs = settings.config.get("llm", {}).get("agent_configs", {})
                agent_config = agent_configs.get(agent_type, {})
                if agent_config and "model" in agent_config:
                    model = agent_config.get("model")
                    # 如果智能体配置中有温度参数，使用智能体的温度参数
                    if "temperature" in agent_config:
                        temperature = agent_config.get("temperature")
                    logger.info(f"使用智能体 {agent_type} 配置的模型: {model}, 温度: {temperature}")

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

            # 获取适配器
            adapter = self._get_adapter(model)

            # 调用适配器
            response = adapter.completion(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )

            # 记录响应
            token_usage = adapter.get_token_usage(response)
            prompt_tokens = token_usage.get('prompt_tokens', 0)
            completion_tokens = token_usage.get('completion_tokens', 0)
            total_tokens = token_usage.get('total_tokens', 0)

            logger.info(
                f"LLM响应: 模型={model}, "
                f"输入tokens={prompt_tokens}, "
                f"输出tokens={completion_tokens}, "
                f"总tokens={total_tokens}"
            )

            # 更新内部token使用统计
            self.token_usage["prompt_tokens"] += prompt_tokens
            self.token_usage["completion_tokens"] += completion_tokens
            self.token_usage["total_tokens"] += total_tokens

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

    async def generate_text(
        self,
        prompt: str,
        model: str = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        agent_type: str = None,  # 新增参数，用于指定智能体类型
        **kwargs
    ) -> str:
        """生成文本，接收单个提示字符串，返回生成的文本字符串"""
        try:
            # 将提示转换为消息格式
            messages = [{"role": "user", "content": prompt}]

            # 调用acompletion方法
            response = await self.acompletion(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                agent_type=agent_type,  # 传递智能体类型
                **kwargs
            )

            # 提取生成的文本
            if response and "choices" in response and len(response["choices"]) > 0:
                return response["choices"][0]["message"]["content"]
            else:
                logger.warning("LLM响应格式不正确或为空")
                return ""

        except Exception as e:
            logger.error(f"生成文本失败: {str(e)}")
            return f"生成失败: {str(e)}"

    async def acompletion_streaming(
        self,
        model: str = None,
        messages: List[Dict[str, str]] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        agent_type: str = None,  # 新增参数，用于指定智能体类型
        **kwargs
    ):
        """异步流式LLM调用，返回一个异步生成器"""
        try:
            # 如果指定了智能体类型，从配置中获取对应的模型
            if agent_type:
                agent_configs = settings.config.get("llm", {}).get("agent_configs", {})
                agent_config = agent_configs.get(agent_type, {})
                if agent_config and "model" in agent_config:
                    model = agent_config.get("model")
                    # 如果智能体配置中有温度参数，使用智能体的温度参数
                    if "temperature" in agent_config:
                        temperature = agent_config.get("temperature")
                    logger.info(f"使用智能体 {agent_type} 配置的模型: {model}, 温度: {temperature}")

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

            # 获取适配器
            adapter = self._get_adapter(model)

            # 调用适配器
            response = await adapter.acompletion_streaming(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )

            # 返回流式响应
            async for chunk in response:
                yield chunk

            # 记录token使用
            # 注意：流式调用的token统计需要在完成后进行
            # 这里只是一个简化的实现
            prompt_tokens = len(str(messages)) // 4  # 粗略估计
            completion_tokens = 1000  # 粗略估计
            total_tokens = prompt_tokens + completion_tokens

            # 更新内部token使用统计
            self.token_usage["prompt_tokens"] += prompt_tokens
            self.token_usage["completion_tokens"] += completion_tokens
            self.token_usage["total_tokens"] += total_tokens

            token_service.record_usage(
                model=model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                service="llm_service",
                task=kwargs.get("task", "acompletion_streaming"),
                task_type=kwargs.get("task_type", "default"),
                user_id=get_current_user_id()
            )

        except Exception as e:
            logger.error(f"LLM流式调用失败: {str(e)}")
            raise

    def get_token_usage(self) -> Dict[str, int]:
        """获取token使用情况"""
        return self.token_usage

    def reset_token_usage(self):
        """重置token使用统计"""
        self.token_usage = {
            "total_tokens": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0
        }

# 创建全局LLM服务实例
llm_service = LLMService()
