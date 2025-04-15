from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class AgentTaskRequest(BaseModel):
    """智能体任务请求"""
    agent_id: str = Field(..., description="智能体ID")
    task: str = Field(..., description="任务描述")
    context: Optional[Dict[str, Any]] = Field(None, description="任务上下文")

class AgentTaskResponse(BaseModel):
    """智能体任务响应"""
    result: Dict[str, Any] = Field(..., description="任务结果")

class WorkflowStep(BaseModel):
    """工作流步骤"""
    agent: str = Field(..., description="智能体ID")
    task: str = Field(..., description="任务描述")

class WorkflowRequest(BaseModel):
    """工作流请求"""
    workflow: List[WorkflowStep] = Field(..., description="工作流步骤")
    context: Optional[Dict[str, Any]] = Field(None, description="初始上下文")

class WorkflowStepResult(BaseModel):
    """工作流步骤结果"""
    agent: str = Field(..., description="智能体ID")
    task: str = Field(..., description="任务描述")
    result: Dict[str, Any] = Field(..., description="步骤结果")

class WorkflowResponse(BaseModel):
    """工作流响应"""
    workflow_results: List[WorkflowStepResult] = Field(..., description="工作流结果")
    final_context: Dict[str, Any] = Field(..., description="最终上下文")

class PlanRequest(BaseModel):
    """规划请求"""
    goal: str = Field(..., description="目标描述")
    context: Optional[Dict[str, Any]] = Field(None, description="初始上下文")

class PlanResponse(BaseModel):
    """规划响应"""
    workflow: List[WorkflowStep] = Field(..., description="生成的工作流")

class PlanAndExecuteRequest(BaseModel):
    """规划并执行请求"""
    goal: str = Field(..., description="目标描述")
    context: Optional[Dict[str, Any]] = Field(None, description="初始上下文")

class PlanAndExecuteResponse(BaseModel):
    """规划并执行响应"""
    workflow_results: List[WorkflowStepResult] = Field(..., description="工作流结果")
    final_context: Dict[str, Any] = Field(..., description="最终上下文")
