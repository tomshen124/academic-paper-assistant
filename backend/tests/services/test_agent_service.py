import pytest
from unittest.mock import patch, MagicMock, AsyncMock, ANY as any
from app.services.agent_service import (
    Agent,
    ResearchAgent,
    WritingAgent,
    EditingAgent,
    AgentCoordinator
)

@pytest.fixture
def mock_llm_service():
    """模拟LLM服务"""
    mock = MagicMock()
    # 创建异步模拟对象
    mock_async_response = AsyncMock()
    mock_async_response.return_value = MagicMock(
        choices=[
            MagicMock(
                message=MagicMock(
                    content='{"result": "模拟结果"}'
                )
            )
        ]
    )
    mock.acompletion = mock_async_response
    return mock

@pytest.mark.asyncio
async def test_research_agent(mock_llm_service):
    """测试研究智能体"""
    # 创建研究智能体
    agent = ResearchAgent(mock_llm_service)

    # 执行任务
    result = await agent.act("测试任务", {"key": "value"})

    # 验证结果
    assert "result" in result
    assert result["result"] == "模拟结果"

    # 验证LLM调用
    mock_llm_service.acompletion.assert_called_once()
    args, kwargs = mock_llm_service.acompletion.call_args
    assert "测试任务" in kwargs["messages"][0]["content"]
    assert "value" in kwargs["messages"][0]["content"]

@pytest.mark.asyncio
async def test_writing_agent(mock_llm_service):
    """测试写作智能体"""
    # 创建写作智能体
    agent = WritingAgent(mock_llm_service)

    # 设置模拟响应
    mock_async_response = AsyncMock()
    mock_async_response.return_value = MagicMock(
        choices=[
            MagicMock(
                message=MagicMock(
                    content="模拟写作内容"
                )
            )
        ]
    )
    mock_llm_service.acompletion = mock_async_response

    # 执行任务
    result = await agent.act("写作任务", {"key": "value"})

    # 验证结果
    assert "content" in result
    assert result["content"] == "模拟写作内容"

    # 验证LLM调用
    mock_llm_service.acompletion.assert_called_once()
    args, kwargs = mock_llm_service.acompletion.call_args
    assert "写作任务" in kwargs["messages"][0]["content"]
    assert "value" in kwargs["messages"][0]["content"]

@pytest.mark.asyncio
async def test_editing_agent(mock_llm_service):
    """测试编辑智能体"""
    # 创建编辑智能体
    agent = EditingAgent(mock_llm_service)

    # 设置模拟响应
    mock_async_response = AsyncMock()
    mock_async_response.return_value = MagicMock(
        choices=[
            MagicMock(
                message=MagicMock(
                    content="模拟编辑内容"
                )
            )
        ]
    )
    mock_llm_service.acompletion = mock_async_response

    # 执行任务
    result = await agent.act("编辑任务", {"content": "原始内容"})

    # 验证结果
    assert "content" in result
    assert result["content"] == "模拟编辑内容"

    # 验证LLM调用
    mock_llm_service.acompletion.assert_called_once()
    args, kwargs = mock_llm_service.acompletion.call_args
    assert "编辑任务" in kwargs["messages"][0]["content"]
    assert "原始内容" in kwargs["messages"][0]["content"]

@pytest.mark.asyncio
async def test_agent_coordinator_delegate_task():
    """测试智能体协调器委派任务"""
    # 创建模拟智能体
    mock_agent = MagicMock()
    mock_async_act = AsyncMock()
    mock_async_act.return_value = {"result": "模拟结果"}
    mock_agent.act = mock_async_act

    # 创建协调器
    coordinator = AgentCoordinator()

    # 注册模拟智能体
    coordinator.register_agent("mock", mock_agent)

    # 委派任务
    result = await coordinator.delegate_task("mock", "测试任务", {"key": "value"})

    # 验证结果
    assert result["result"] == "模拟结果"

    # 验证智能体调用
    mock_agent.act.assert_called_once_with("测试任务", {"key": "value"})

@pytest.mark.asyncio
async def test_agent_coordinator_execute_workflow():
    """测试智能体协调器执行工作流"""
    # 创建模拟智能体
    mock_research = MagicMock()
    mock_research_act = AsyncMock()
    mock_research_act.return_value = {"research_result": "模拟研究结果"}
    mock_research.act = mock_research_act

    mock_writing = MagicMock()
    mock_writing_act = AsyncMock()
    mock_writing_act.return_value = {"content": "模拟写作内容"}
    mock_writing.act = mock_writing_act

    # 创建协调器
    coordinator = AgentCoordinator()

    # 注册模拟智能体
    coordinator.register_agent("research", mock_research)
    coordinator.register_agent("writing", mock_writing)

    # 创建工作流
    workflow = [
        {"agent": "research", "task": "研究任务"},
        {"agent": "writing", "task": "写作任务"}
    ]

    # 执行工作流
    result = await coordinator.execute_workflow(workflow, {"initial": "context"})

    # 验证结果
    assert "workflow_results" in result
    assert "final_context" in result
    assert len(result["workflow_results"]) == 2
    assert result["workflow_results"][0]["agent"] == "research"
    assert result["workflow_results"][1]["agent"] == "writing"
    assert "research_result" in result["final_context"]
    assert "content" in result["final_context"]

    # 验证智能体调用
    # 使用ANY匹配任何上下文参数
    mock_research.act.assert_called_once_with("研究任务", any)
    mock_writing.act.assert_called_once()
