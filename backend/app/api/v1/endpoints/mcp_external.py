"""
外部MCP服务器API端点
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import Dict, List, Any, Optional
from pydantic import BaseModel

from app.services.mcp_external_client import mcp_external_client
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger("mcp_external_api")

router = APIRouter()

class ConnectRequest(BaseModel):
    """连接请求"""
    server_type: str
    command: Optional[str] = None
    args: Optional[List[str]] = None
    url: Optional[str] = None

class ConnectResponse(BaseModel):
    """连接响应"""
    connected: bool
    server_name: Optional[str] = None
    server_version: Optional[str] = None
    message: Optional[str] = None

class ToolRequest(BaseModel):
    """工具请求"""
    tool_name: str
    arguments: Dict[str, Any]

class ResourceRequest(BaseModel):
    """资源请求"""
    uri: str

class PromptRequest(BaseModel):
    """提示模板请求"""
    name: str
    arguments: Optional[Dict[str, str]] = None

@router.post("/connect", response_model=ConnectResponse)
async def connect_to_server(request: ConnectRequest):
    """连接到外部MCP服务器"""
    if not settings.get('mcp.enabled', False):
        raise HTTPException(status_code=400, detail="MCP功能未启用")
    
    try:
        kwargs = {}
        if request.server_type == "stdio" and request.command:
            kwargs["command"] = request.command
            if request.args:
                kwargs["args"] = request.args
        elif request.server_type == "http" and request.url:
            kwargs["url"] = request.url
        
        connected = await mcp_external_client.connect_to_server(request.server_type, **kwargs)
        
        if not connected:
            return ConnectResponse(
                connected=False,
                message="连接到外部MCP服务器失败"
            )
        
        return ConnectResponse(
            connected=True,
            server_name=mcp_external_client.server_info.server_name,
            server_version=mcp_external_client.server_info.server_version,
            message="连接成功"
        )
    except Exception as e:
        logger.error(f"连接到外部MCP服务器失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"连接到外部MCP服务器失败: {str(e)}")

@router.post("/disconnect")
async def disconnect_from_server():
    """断开与外部MCP服务器的连接"""
    if not settings.get('mcp.enabled', False):
        raise HTTPException(status_code=400, detail="MCP功能未启用")
    
    try:
        await mcp_external_client.disconnect()
        return {"status": "success", "message": "已断开与外部MCP服务器的连接"}
    except Exception as e:
        logger.error(f"断开与外部MCP服务器的连接失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"断开与外部MCP服务器的连接失败: {str(e)}")

@router.get("/tools")
async def list_tools():
    """列出可用的工具"""
    if not settings.get('mcp.enabled', False):
        raise HTTPException(status_code=400, detail="MCP功能未启用")
    
    if not mcp_external_client.session:
        raise HTTPException(status_code=400, detail="未连接到外部MCP服务器")
    
    try:
        tools = await mcp_external_client.list_tools()
        return {"tools": tools}
    except Exception as e:
        logger.error(f"列出工具失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"列出工具失败: {str(e)}")

@router.post("/tools/call")
async def call_tool(request: ToolRequest):
    """调用工具"""
    if not settings.get('mcp.enabled', False):
        raise HTTPException(status_code=400, detail="MCP功能未启用")
    
    if not mcp_external_client.session:
        raise HTTPException(status_code=400, detail="未连接到外部MCP服务器")
    
    try:
        result = await mcp_external_client.call_tool(request.tool_name, request.arguments)
        return {"result": result}
    except Exception as e:
        logger.error(f"调用工具失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"调用工具失败: {str(e)}")

@router.get("/resources")
async def list_resources():
    """列出可用的资源"""
    if not settings.get('mcp.enabled', False):
        raise HTTPException(status_code=400, detail="MCP功能未启用")
    
    if not mcp_external_client.session:
        raise HTTPException(status_code=400, detail="未连接到外部MCP服务器")
    
    try:
        resources = await mcp_external_client.list_resources()
        return {"resources": resources}
    except Exception as e:
        logger.error(f"列出资源失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"列出资源失败: {str(e)}")

@router.post("/resources/read")
async def read_resource(request: ResourceRequest):
    """读取资源"""
    if not settings.get('mcp.enabled', False):
        raise HTTPException(status_code=400, detail="MCP功能未启用")
    
    if not mcp_external_client.session:
        raise HTTPException(status_code=400, detail="未连接到外部MCP服务器")
    
    try:
        content, mime_type = await mcp_external_client.read_resource(request.uri)
        return {
            "content": content.decode("utf-8", errors="ignore"),
            "mime_type": mime_type
        }
    except Exception as e:
        logger.error(f"读取资源失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"读取资源失败: {str(e)}")

@router.get("/prompts")
async def list_prompts():
    """列出可用的提示模板"""
    if not settings.get('mcp.enabled', False):
        raise HTTPException(status_code=400, detail="MCP功能未启用")
    
    if not mcp_external_client.session:
        raise HTTPException(status_code=400, detail="未连接到外部MCP服务器")
    
    try:
        prompts = await mcp_external_client.list_prompts()
        return {"prompts": prompts}
    except Exception as e:
        logger.error(f"列出提示模板失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"列出提示模板失败: {str(e)}")

@router.post("/prompts/get")
async def get_prompt(request: PromptRequest):
    """获取提示模板"""
    if not settings.get('mcp.enabled', False):
        raise HTTPException(status_code=400, detail="MCP功能未启用")
    
    if not mcp_external_client.session:
        raise HTTPException(status_code=400, detail="未连接到外部MCP服务器")
    
    try:
        prompt = await mcp_external_client.get_prompt(request.name, request.arguments)
        return {"prompt": prompt}
    except Exception as e:
        logger.error(f"获取提示模板失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取提示模板失败: {str(e)}")
