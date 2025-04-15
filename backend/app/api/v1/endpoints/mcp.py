"""
MCP (Model Context Protocol) API 端点
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Dict, List, Any, Optional
from pydantic import BaseModel

from app.services.mcp_adapter import mcp_adapter
from app.core.config import settings

router = APIRouter()

class ContextRequest(BaseModel):
    """上下文请求"""
    name: str
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ContextResponse(BaseModel):
    """上下文响应"""
    context_id: str
    name: str
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    status: str

class ToolRequest(BaseModel):
    """工具请求"""
    context_id: str
    tool_name: str
    tool_params: Dict[str, Any]

class ToolResponse(BaseModel):
    """工具响应"""
    context_id: str
    tool_name: str
    result: Dict[str, Any]
    status: str

class PaperWorkflowRequest(BaseModel):
    """论文工作流请求"""
    topic: str
    academic_field: str

class PaperWorkflowResponse(BaseModel):
    """论文工作流响应"""
    context_id: str
    topic: str
    outline: Dict[str, Any]
    sections: Dict[str, str]
    citations: List[Dict[str, Any]]
    status: str

@router.post("/contexts", response_model=ContextResponse)
async def create_context(request: ContextRequest):
    """创建上下文"""
    if not settings.get('mcp.enabled', False):
        raise HTTPException(status_code=400, detail="MCP功能未启用")
        
    try:
        result = await mcp_adapter.mcp_client.create_context(request.dict())
        if "context_id" not in result:
            raise HTTPException(status_code=500, detail=f"创建上下文失败: {result.get('message', '未知错误')}")
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建上下文失败: {str(e)}")

@router.get("/contexts/{context_id}", response_model=ContextResponse)
async def get_context(context_id: str):
    """获取上下文信息"""
    if not settings.get('mcp.enabled', False):
        raise HTTPException(status_code=400, detail="MCP功能未启用")
        
    try:
        result = await mcp_adapter.mcp_client.get_context(context_id)
        if "context_id" not in result:
            raise HTTPException(status_code=404, detail=f"上下文不存在: {context_id}")
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取上下文失败: {str(e)}")

@router.delete("/contexts/{context_id}")
async def delete_context(context_id: str):
    """删除上下文"""
    if not settings.get('mcp.enabled', False):
        raise HTTPException(status_code=400, detail="MCP功能未启用")
        
    try:
        result = await mcp_adapter.mcp_client.delete_context(context_id)
        if result.get("status") != "success":
            raise HTTPException(status_code=500, detail=f"删除上下文失败: {result.get('message', '未知错误')}")
            
        return {"status": "success", "message": f"成功删除上下文: {context_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除上下文失败: {str(e)}")

@router.post("/tools/execute", response_model=ToolResponse)
async def execute_tool(request: ToolRequest):
    """执行工具"""
    if not settings.get('mcp.enabled', False):
        raise HTTPException(status_code=400, detail="MCP功能未启用")
        
    try:
        result = await mcp_adapter.mcp_client.execute_tool(
            context_id=request.context_id,
            tool_name=request.tool_name,
            tool_params=request.tool_params
        )
        
        return {
            "context_id": request.context_id,
            "tool_name": request.tool_name,
            "result": result,
            "status": "success" if result.get("status") != "error" else "error"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"执行工具失败: {str(e)}")

@router.post("/paper/workflow", response_model=PaperWorkflowResponse)
async def execute_paper_workflow(request: PaperWorkflowRequest, background_tasks: BackgroundTasks):
    """执行论文工作流"""
    if not settings.get('mcp.enabled', False):
        raise HTTPException(status_code=400, detail="MCP功能未启用")
        
    try:
        # 创建上下文
        context_result = await mcp_adapter.create_paper_context(
            topic=request.topic,
            academic_field=request.academic_field
        )
        
        if "context_id" not in context_result:
            raise HTTPException(status_code=500, detail=f"创建论文上下文失败: {context_result.get('message', '未知错误')}")
            
        context_id = context_result["context_id"]
        
        # 在后台执行工作流
        background_tasks.add_task(
            mcp_adapter.execute_paper_workflow,
            context_id=context_id,
            topic=request.topic,
            academic_field=request.academic_field
        )
        
        return {
            "context_id": context_id,
            "topic": request.topic,
            "outline": {},
            "sections": {},
            "citations": [],
            "status": "processing"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"执行论文工作流失败: {str(e)}")

@router.get("/paper/workflow/{context_id}", response_model=PaperWorkflowResponse)
async def get_paper_workflow(context_id: str):
    """获取论文工作流状态"""
    if not settings.get('mcp.enabled', False):
        raise HTTPException(status_code=400, detail="MCP功能未启用")
        
    try:
        # 获取上下文
        context_result = await mcp_adapter.mcp_client.get_context(context_id)
        if "context_id" not in context_result:
            raise HTTPException(status_code=404, detail=f"上下文不存在: {context_id}")
            
        # 获取上下文中的工作流状态
        metadata = context_result.get("metadata", {})
        topic = metadata.get("topic", "")
        academic_field = metadata.get("academic_field", "")
        
        # 获取工作流结果
        workflow_result = metadata.get("workflow_result", {})
        
        return {
            "context_id": context_id,
            "topic": topic,
            "outline": workflow_result.get("outline", {}),
            "sections": workflow_result.get("sections", {}),
            "citations": workflow_result.get("citations", []),
            "status": workflow_result.get("status", "processing")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取论文工作流状态失败: {str(e)}")

@router.post("/initialize")
async def initialize_mcp():
    """初始化MCP"""
    if not settings.get('mcp.enabled', False):
        raise HTTPException(status_code=400, detail="MCP功能未启用")
        
    try:
        success = await mcp_adapter.initialize()
        if not success:
            raise HTTPException(status_code=500, detail="初始化MCP失败")
            
        return {"status": "success", "message": "成功初始化MCP"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"初始化MCP失败: {str(e)}")
