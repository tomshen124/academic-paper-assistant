from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any

from app.schemas.agent import (
    AgentTaskRequest,
    AgentTaskResponse,
    WorkflowRequest,
    WorkflowResponse,
    PlanRequest,
    PlanResponse,
    PlanAndExecuteRequest,
    PlanAndExecuteResponse
)
from app.services.agent_service import AgentCoordinator
from app.api.deps import get_agent_coordinator

router = APIRouter()

@router.post("/task", response_model=AgentTaskResponse)
async def execute_agent_task(
    request: AgentTaskRequest,
    agent_coordinator: AgentCoordinator = Depends(get_agent_coordinator)
):
    """执行智能体任务"""
    try:
        result = await agent_coordinator.delegate_task(
            agent_id=request.agent_id,
            task=request.task,
            context=request.context
        )
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"执行智能体任务失败: {str(e)}")

@router.post("/workflow", response_model=WorkflowResponse)
async def execute_workflow(
    request: WorkflowRequest,
    agent_coordinator: AgentCoordinator = Depends(get_agent_coordinator)
):
    """执行工作流"""
    try:
        workflow = [{"agent": step.agent, "task": step.task} for step in request.workflow]
        result = await agent_coordinator.execute_workflow(
            workflow=workflow,
            initial_context=request.context
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"执行工作流失败: {str(e)}")

@router.post("/plan", response_model=PlanResponse)
async def generate_plan(
    request: PlanRequest,
    agent_coordinator: AgentCoordinator = Depends(get_agent_coordinator)
):
    """生成任务计划"""
    try:
        workflow = await agent_coordinator._generate_workflow(
            goal=request.goal,
            context=request.context
        )
        return {"workflow": workflow}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成任务计划失败: {str(e)}")

@router.post("/plan-and-execute", response_model=PlanAndExecuteResponse)
async def plan_and_execute(
    request: PlanAndExecuteRequest,
    agent_coordinator: AgentCoordinator = Depends(get_agent_coordinator)
):
    """规划并执行任务"""
    try:
        result = await agent_coordinator.plan_and_execute(
            goal=request.goal,
            context=request.context
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"规划并执行任务失败: {str(e)}")
