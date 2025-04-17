from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.schemas.token import (
    TokenUsageResponse,
    TokenUsageExportRequest,
    TokenUsageExportResponse,
    TokenUsageResetResponse
)
from app.services.token_service import TokenService
from app.api.deps import get_token_service, get_db, get_current_active_user
from app.models.user import User
from app.models.token_usage import TokenUsage

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

@router.get("/user-usage", response_model=List[Dict[str, Any]])
async def get_user_token_usage(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100
):
    """获取用户的token使用记录"""
    try:
        # 查询用户的token使用记录
        records = db.query(TokenUsage).filter(
            TokenUsage.user_id == current_user.id
        ).order_by(TokenUsage.timestamp.desc()).offset(skip).limit(limit).all()

        # 返回结果
        return [{
            "id": record.id,
            "model": record.model,
            "service": record.service,
            "task": record.task,
            "prompt_tokens": record.prompt_tokens,
            "completion_tokens": record.completion_tokens,
            "total_tokens": record.total_tokens,
            "estimated_cost": record.estimated_cost,
            "timestamp": record.timestamp
        } for record in records]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户token使用记录失败: {str(e)}")

@router.get("/user-summary", response_model=Dict[str, Any])
async def get_user_token_usage_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取用户的token使用汇总"""
    try:
        # 查询用户的token使用汇总
        result = db.query(
            func.sum(TokenUsage.prompt_tokens).label("prompt_tokens"),
            func.sum(TokenUsage.completion_tokens).label("completion_tokens"),
            func.sum(TokenUsage.total_tokens).label("total_tokens"),
            func.sum(TokenUsage.estimated_cost).label("estimated_cost"),
            func.count(TokenUsage.id).label("requests")
        ).filter(TokenUsage.user_id == current_user.id).first()

        # 按模型分组统计
        by_model = db.query(
            TokenUsage.model,
            func.sum(TokenUsage.total_tokens).label("total_tokens"),
            func.sum(TokenUsage.estimated_cost).label("estimated_cost"),
            func.count(TokenUsage.id).label("requests")
        ).filter(TokenUsage.user_id == current_user.id).group_by(TokenUsage.model).all()

        # 按服务分组统计
        by_service = db.query(
            TokenUsage.service,
            func.sum(TokenUsage.total_tokens).label("total_tokens"),
            func.sum(TokenUsage.estimated_cost).label("estimated_cost"),
            func.count(TokenUsage.id).label("requests")
        ).filter(TokenUsage.user_id == current_user.id).group_by(TokenUsage.service).all()

        # 返回结果
        return {
            "total_usage": {
                "prompt_tokens": result.prompt_tokens or 0,
                "completion_tokens": result.completion_tokens or 0,
                "total_tokens": result.total_tokens or 0,
                "estimated_cost": result.estimated_cost or 0,
                "requests": result.requests or 0
            },
            "by_model": {
                model[0]: {
                    "total_tokens": model[1] or 0,
                    "estimated_cost": model[2] or 0,
                    "requests": model[3] or 0
                } for model in by_model
            },
            "by_service": {
                service[0]: {
                    "total_tokens": service[1] or 0,
                    "estimated_cost": service[2] or 0,
                    "requests": service[3] or 0
                } for service in by_service
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户token使用汇总失败: {str(e)}")
