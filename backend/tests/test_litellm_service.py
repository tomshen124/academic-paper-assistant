import asyncio
import os
import pytest
from app.services.litellm_service import litellm_service
from app.core.config import settings

# 测试异步调用
@pytest.mark.asyncio
@pytest.mark.skipif(not settings.OPENAI_API_KEY, reason="需要OpenAI API密钥")
async def test_acompletion():
    """测试异步调用"""
    messages = [{"role": "user", "content": "Hello, world!"}]
    
    # 测试OpenAI模型
    response = await litellm_service.acompletion(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=10,
        temperature=0.7
    )
    
    assert "choices" in response
    assert "usage" in response
    assert response["choices"][0]["message"]["content"]
    
    # 测试token使用记录
    assert response["usage"]["prompt_tokens"] > 0
    assert response["usage"]["completion_tokens"] > 0
    assert response["usage"]["total_tokens"] > 0

# 测试同步调用
@pytest.mark.skipif(not settings.OPENAI_API_KEY, reason="需要OpenAI API密钥")
def test_completion():
    """测试同步调用"""
    messages = [{"role": "user", "content": "Hello, world!"}]
    
    # 测试OpenAI模型
    response = litellm_service.completion(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=10,
        temperature=0.7
    )
    
    assert "choices" in response
    assert "usage" in response
    assert response["choices"][0]["message"]["content"]
    
    # 测试token使用记录
    assert response["usage"]["prompt_tokens"] > 0
    assert response["usage"]["completion_tokens"] > 0
    assert response["usage"]["total_tokens"] > 0

# 测试DeepSeek模型
@pytest.mark.asyncio
@pytest.mark.skipif(not settings.DEEPSEEK_API_KEY, reason="需要DeepSeek API密钥")
async def test_deepseek():
    """测试DeepSeek模型"""
    messages = [{"role": "user", "content": "Hello, world!"}]
    
    # 测试DeepSeek模型
    response = await litellm_service.acompletion(
        model="deepseek-chat",
        messages=messages,
        max_tokens=10,
        temperature=0.7
    )
    
    assert "choices" in response
    assert "usage" in response
    assert response["choices"][0]["message"]["content"]

# 测试SiliconFlow模型
@pytest.mark.asyncio
@pytest.mark.skipif(not settings.SILICONFLOW_API_KEY, reason="需要SiliconFlow API密钥")
async def test_siliconflow():
    """测试SiliconFlow模型"""
    messages = [{"role": "user", "content": "Hello, world!"}]
    
    # 测试SiliconFlow模型
    response = await litellm_service.acompletion(
        model="Qwen/QwQ-32B",
        messages=messages,
        max_tokens=10,
        temperature=0.7
    )
    
    assert "choices" in response
    assert "usage" in response
    assert response["choices"][0]["message"]["content"]

# 测试回退机制
@pytest.mark.asyncio
async def test_fallbacks():
    """测试回退机制"""
    messages = [{"role": "user", "content": "Hello, world!"}]
    
    # 修改默认模型为不存在的模型，触发回退
    original_model = settings.DEFAULT_MODEL
    settings.DEFAULT_MODEL = "non-existent-model"
    
    try:
        # 测试回退机制
        response = await litellm_service.acompletion_with_fallbacks(
            messages=messages,
            max_tokens=10,
            temperature=0.7
        )
        
        # 如果没有抛出异常，说明回退成功
        assert "choices" in response
        assert "usage" in response
        assert response["choices"][0]["message"]["content"]
    except Exception as e:
        # 如果所有回退都失败，会抛出异常
        assert "所有LLM模型调用都失败" in str(e)
    finally:
        # 恢复默认模型
        settings.DEFAULT_MODEL = original_model

# 手动测试
if __name__ == "__main__":
    # 设置API密钥
    if not settings.OPENAI_API_KEY:
        print("请设置OPENAI_API_KEY环境变量")
        exit(1)
    
    # 测试异步调用
    async def test():
        messages = [{"role": "user", "content": "Hello, world!"}]
        
        # 测试OpenAI模型
        response = await litellm_service.acompletion(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=10,
            temperature=0.7
        )
        
        print("响应:", response)
        print("内容:", response["choices"][0]["message"]["content"])
        print("使用tokens:", response["usage"])
    
    asyncio.run(test())
