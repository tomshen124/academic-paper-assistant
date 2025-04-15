from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any

from app.schemas.token import (
    TokenUsageResponse,
    TokenUsageExportRequest,
    TokenUsageExportResponse,
    TokenUsageResetResponse
)
from app.services.token_service import TokenService
from app.api.deps import get_token_service

router = APIRouter()

@router.get("/usage", response_model=TokenUsageResponse)
async def get_token_usage(
    include_recent: bool = False,
    recent_limit: int = 10,
    token_service: TokenService = Depends(get_token_service)
):
    """获取token使用情况"""
    try:
        summary = token_service.get_usage_summary()
        
        response = {
            "summary": summary
        }
        
        if include_recent:
            recent_records = token_service.get_recent_usage(limit=recent_limit)
            response["recent_records"] = recent_records
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取token使用情况失败: {str(e)}")

@router.post("/export", response_model=TokenUsageExportResponse)
async def export_token_usage(
    request: TokenUsageExportRequest,
    token_service: TokenService = Depends(get_token_service)
):
    """导出token使用数据"""
    try:
        data = token_service.export_usage_data(format=request.format)
        return {
            "data": data,
            "format": request.format
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出token使用数据失败: {str(e)}")

@router.post("/reset", response_model=TokenUsageResetResponse)
async def reset_token_usage(
    token_service: TokenService = Depends(get_token_service)
):
    """重置token使用数据"""
    try:
        result = token_service.reset_usage_data()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重置token使用数据失败: {str(e)}")
