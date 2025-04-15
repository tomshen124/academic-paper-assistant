import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from app.services.llm_service import LLMService

@pytest.fixture
def mock_token_service():
    """模拟Token服务"""
    mock = MagicMock()
    mock.record_usage.return_value = {
        "model": "test-model",
        "prompt_tokens": 100,
        "completion_tokens": 50,
        "total_tokens": 150,
        "estimated_cost": 0.001
    }
    return mock

@pytest.fixture
def mock_litellm():
    """模拟LiteLLM"""
    mock = MagicMock()
    # 创建一个异步模拟对象
    mock_async_response = AsyncMock()
    mock_async_response.return_value = {
        "choices": [
            {
                "message": {
                    "content": "模拟响应"
                }
            }
        ],
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150
        }
    }
    mock.acompletion = mock_async_response

    mock.completion.return_value = {
        "choices": [
            {
                "message": {
                    "content": "模拟响应"
                }
            }
        ],
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150
        }
    }
    return mock

@pytest.mark.asyncio
async def test_acompletion(mock_litellm, mock_token_service):
    """测试异步补全"""
    with patch("app.services.llm_service.acompletion", mock_litellm.acompletion), \
         patch("app.services.llm_service.token_service", mock_token_service):

        # 创建LLM服务
        llm_service = LLMService()

        # 调用异步补全
        messages = [{"role": "user", "content": "测试消息"}]
        response = await llm_service.acompletion(
            model="test-model",
            messages=messages,
            max_tokens=100,
            temperature=0.7
        )

        # 验证响应
        assert response["choices"][0]["message"]["content"] == "模拟响应"
        assert response["usage"]["total_tokens"] == 150

        # 验证LiteLLM调用
        mock_litellm.acompletion.assert_called_once()

        # 验证Token服务调用
        mock_token_service.record_usage.assert_called_once_with(
            model="test-model",
            prompt_tokens=100,
            completion_tokens=50,
            service="llm_service",
            task="acompletion"
        )

def test_completion(mock_litellm, mock_token_service):
    """测试同步补全"""
    with patch("app.services.llm_service.completion", mock_litellm.completion), \
         patch("app.services.llm_service.token_service", mock_token_service):

        # 创建LLM服务
        llm_service = LLMService()

        # 调用同步补全
        messages = [{"role": "user", "content": "测试消息"}]
        response = llm_service.completion(
            model="test-model",
            messages=messages,
            max_tokens=100,
            temperature=0.7
        )

        # 验证响应
        assert response["choices"][0]["message"]["content"] == "模拟响应"
        assert response["usage"]["total_tokens"] == 150

        # 验证LiteLLM调用
        mock_litellm.completion.assert_called_once()

        # 验证Token服务调用
        mock_token_service.record_usage.assert_called_once_with(
            model="test-model",
            prompt_tokens=100,
            completion_tokens=50,
            service="llm_service",
            task="completion"
        )

@pytest.mark.asyncio
async def test_acompletion_with_fallbacks(mock_litellm, mock_token_service):
    """测试带回退的异步补全"""
    with patch("app.services.llm_service.acompletion", mock_litellm.acompletion), \
         patch("app.services.llm_service.token_service", mock_token_service):

        # 创建LLM服务
        llm_service = LLMService()

        # 模拟主模型失败
        mock_async_error = AsyncMock()
        mock_async_error.side_effect = Exception("模拟失败")

        # 设置异步调用的返回值序列
        mock_litellm.acompletion.side_effect = [
            mock_async_error(),  # 第一次调用失败
            mock_litellm.acompletion.return_value  # 第二次调用成功
        ]

        # 调用带回退的异步补全
        messages = [{"role": "user", "content": "测试消息"}]
        response = await llm_service.acompletion_with_fallbacks(
            messages=messages,
            max_tokens=100,
            temperature=0.7
        )

        # 验证响应
        assert response["choices"][0]["message"]["content"] == "模拟响应"

        # 验证LiteLLM调用次数
        assert mock_litellm.acompletion.call_count == 2
