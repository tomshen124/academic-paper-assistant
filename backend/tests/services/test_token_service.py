import pytest
from app.services.token_service import TokenService

@pytest.fixture
def token_service():
    """创建Token服务实例"""
    return TokenService()

def test_record_usage(token_service):
    """测试记录token使用"""
    # 记录使用
    record = token_service.record_usage(
        model="gpt-3.5-turbo",
        prompt_tokens=100,
        completion_tokens=50,
        service="test_service",
        task="test_task"
    )
    
    # 验证记录
    assert record["model"] == "gpt-3.5-turbo"
    assert record["prompt_tokens"] == 100
    assert record["completion_tokens"] == 50
    assert record["total_tokens"] == 150
    assert record["service"] == "test_service"
    assert record["task"] == "test_task"
    assert "timestamp" in record
    assert "day" in record
    assert "estimated_cost" in record

def test_get_usage_summary(token_service):
    """测试获取使用摘要"""
    # 记录一些使用
    token_service.record_usage(
        model="gpt-3.5-turbo",
        prompt_tokens=100,
        completion_tokens=50,
        service="test_service",
        task="test_task"
    )
    
    token_service.record_usage(
        model="gpt-4",
        prompt_tokens=200,
        completion_tokens=100,
        service="another_service",
        task="another_task"
    )
    
    # 获取摘要
    summary = token_service.get_usage_summary()
    
    # 验证摘要
    assert summary["total_usage"]["prompt_tokens"] == 300
    assert summary["total_usage"]["completion_tokens"] == 150
    assert summary["total_usage"]["total_tokens"] == 450
    assert summary["total_usage"]["total_requests"] == 2
    
    # 验证按模型统计
    assert "gpt-3.5-turbo" in summary["by_model"]
    assert "gpt-4" in summary["by_model"]
    assert summary["by_model"]["gpt-3.5-turbo"]["total_tokens"] == 150
    assert summary["by_model"]["gpt-4"]["total_tokens"] == 300
    
    # 验证按服务统计
    assert "test_service" in summary["by_service"]
    assert "another_service" in summary["by_service"]
    
    # 验证平均值
    assert summary["averages"]["tokens_per_request"] == 225  # 450 / 2

def test_get_recent_usage(token_service):
    """测试获取最近使用记录"""
    # 记录一些使用
    for i in range(5):
        token_service.record_usage(
            model=f"model-{i}",
            prompt_tokens=100,
            completion_tokens=50,
            service="test_service",
            task="test_task"
        )
    
    # 获取最近记录
    recent = token_service.get_recent_usage(limit=3)
    
    # 验证记录
    assert len(recent) == 3
    assert recent[0]["model"] == "model-2"
    assert recent[1]["model"] == "model-3"
    assert recent[2]["model"] == "model-4"

def test_reset_usage_data(token_service):
    """测试重置使用数据"""
    # 记录一些使用
    token_service.record_usage(
        model="gpt-3.5-turbo",
        prompt_tokens=100,
        completion_tokens=50,
        service="test_service",
        task="test_task"
    )
    
    # 重置数据
    result = token_service.reset_usage_data()
    
    # 验证结果
    assert "message" in result
    assert "previous_summary" in result
    assert result["previous_summary"]["total_usage"]["total_tokens"] == 150
    
    # 验证数据已重置
    summary = token_service.get_usage_summary()
    assert summary["total_usage"]["total_tokens"] == 0
    assert summary["total_usage"]["total_requests"] == 0
    assert len(token_service.usage_records) == 0
