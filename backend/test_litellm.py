#!/usr/bin/env python
"""
测试LiteLLM配置和服务

此脚本用于测试LiteLLM配置和服务是否能够正确处理不同的模型。
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from app.services.litellm_config import MODEL_MAPPINGS
from app.services.litellm_service import litellm_service
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger()

async def test_litellm():
    """测试LiteLLM配置和服务"""
    # 打印可用模型
    print("可用模型:", MODEL_MAPPINGS.keys())
    print("回退模型:", [m["model"] for m in litellm_service.fallback_models])
    print("默认模型:", settings.DEFAULT_MODEL)
    
    # 如果没有可用模型，退出
    if not MODEL_MAPPINGS:
        print("没有可用模型，请检查API密钥配置")
        return
    
    # 测试消息
    messages = [{"role": "user", "content": "你好，请用简短的一句话介绍一下自己。"}]
    
    # 测试默认模型
    try:
        print(f"\n测试默认模型: {settings.DEFAULT_MODEL}")
        response = await litellm_service.acompletion(
            messages=messages,
            max_tokens=100,
            temperature=0.7
        )
        print("响应:", response["choices"][0]["message"]["content"])
        print("使用tokens:", response["usage"])
    except Exception as e:
        print(f"默认模型调用失败: {str(e)}")
    
    # 测试每个可用模型
    for model_name in MODEL_MAPPINGS.keys():
        try:
            print(f"\n测试模型: {model_name}")
            response = await litellm_service.acompletion(
                model=model_name,
                messages=messages,
                max_tokens=100,
                temperature=0.7
            )
            print("响应:", response["choices"][0]["message"]["content"])
            print("使用tokens:", response["usage"])
        except Exception as e:
            print(f"模型 {model_name} 调用失败: {str(e)}")
    
    # 测试回退机制
    try:
        print("\n测试回退机制")
        response = await litellm_service.acompletion_with_fallbacks(
            messages=messages,
            max_tokens=100,
            temperature=0.7
        )
        print("响应:", response["choices"][0]["message"]["content"])
        print("使用tokens:", response["usage"])
    except Exception as e:
        print(f"回退机制测试失败: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_litellm())
