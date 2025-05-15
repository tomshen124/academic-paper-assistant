from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.schemas.token import (
    TokenUsageResponse,
    TokenUsageExportRequest,
    TokenUsageExportResponse
)
from app.services.token_service import TokenService
from app.api.deps import get_token_service, get_db, get_current_active_user, get_current_active_superuser
from app.models.user import User
from app.models.token_usage import TokenUsage

router = APIRouter()

@router.get("/usage", response_model=TokenUsageResponse)
async def get_token_usage(
    include_recent: bool = False,
    recent_limit: int = 10,
    start_date: Optional[str] = Query(None, description="开始日期（YYYY-MM-DD）"),
    end_date: Optional[str] = Query(None, description="结束日期（YYYY-MM-DD）"),
    db: Session = Depends(get_db),
    token_service: TokenService = Depends(get_token_service),
    _: User = Depends(get_current_active_superuser)  # 只允许超级管理员访问
):
    """获取所有token使用情况（管理员专用）"""
    try:
        # 解析日期
        start_datetime = None
        end_datetime = None

        if start_date:
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)  # 包含结束日期

        # 获取摘要
        summary = token_service.get_usage_summary(db=db, start_date=start_datetime, end_date=end_datetime)

        response = {
            "summary": summary
        }

        # 如果需要最近记录
        if include_recent:
            recent_records = token_service.get_recent_usage(db=db, limit=recent_limit)
            response["recent_records"] = recent_records

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取token使用情况失败: {str(e)}")

@router.post("/export", response_model=TokenUsageExportResponse)
async def export_token_usage(
    request: TokenUsageExportRequest,
    start_date: Optional[str] = Query(None, description="开始日期（YYYY-MM-DD）"),
    end_date: Optional[str] = Query(None, description="结束日期（YYYY-MM-DD）"),
    db: Session = Depends(get_db),
    token_service: TokenService = Depends(get_token_service),
    _: User = Depends(get_current_active_superuser)  # 只允许超级管理员访问
):
    """导出token使用数据（管理员专用）"""
    try:
        # 解析日期
        start_datetime = None
        end_datetime = None

        if start_date:
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)  # 包含结束日期

        # 导出数据
        data = token_service.export_usage_data(
            db=db,
            format=request.format,
            start_date=start_datetime,
            end_date=end_datetime
        )

        return {
            "data": data,
            "format": request.format
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出token使用数据失败: {str(e)}")

@router.get("/user-usage", response_model=List[Dict[str, Any]])
async def get_user_token_usage(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[str] = Query(None, description="开始日期（YYYY-MM-DD）"),
    end_date: Optional[str] = Query(None, description="结束日期（YYYY-MM-DD）"),
    model: Optional[str] = Query(None, description="模型名称过滤"),
    service: Optional[str] = Query(None, description="服务名称过滤"),
    task: Optional[str] = Query(None, description="任务名称过滤")
):
    """获取用户的token使用记录"""
    try:
        # 解析日期
        start_datetime = None
        end_datetime = None

        if start_date:
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)  # 包含结束日期

        # 构建基础查询
        query = db.query(TokenUsage).filter(TokenUsage.user_id == current_user.id)

        # 添加过滤条件
        if start_datetime:
            query = query.filter(TokenUsage.timestamp >= start_datetime)
        if end_datetime:
            query = query.filter(TokenUsage.timestamp <= end_datetime)
        if model:
            query = query.filter(TokenUsage.model == model)
        if service:
            query = query.filter(TokenUsage.service == service)
        if task:
            query = query.filter(TokenUsage.task == task)

        # 执行查询
        records = query.order_by(TokenUsage.timestamp.desc()).offset(skip).limit(limit).all()

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
            "timestamp": record.timestamp.isoformat()
        } for record in records]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户token使用记录失败: {str(e)}")

@router.get("/user-summary", response_model=Dict[str, Any])
async def get_user_token_usage_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    start_date: Optional[str] = Query(None, description="开始日期（YYYY-MM-DD）"),
    end_date: Optional[str] = Query(None, description="结束日期（YYYY-MM-DD）")
):
    """获取用户的token使用汇总"""
    try:
        # 解析日期
        start_datetime = None
        end_datetime = None

        if start_date:
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)  # 包含结束日期

        # 构建基础查询
        base_query = db.query(TokenUsage).filter(TokenUsage.user_id == current_user.id)

        # 添加日期过滤条件
        if start_datetime:
            base_query = base_query.filter(TokenUsage.timestamp >= start_datetime)
        if end_datetime:
            base_query = base_query.filter(TokenUsage.timestamp <= end_datetime)

        # 查询用户的token使用汇总
        result = base_query.with_entities(
            func.sum(TokenUsage.prompt_tokens).label("prompt_tokens"),
            func.sum(TokenUsage.completion_tokens).label("completion_tokens"),
            func.sum(TokenUsage.total_tokens).label("total_tokens"),
            func.sum(TokenUsage.estimated_cost).label("estimated_cost"),
            func.count(TokenUsage.id).label("requests")
        ).first()

        # 按模型分组统计
        by_model = base_query.with_entities(
            TokenUsage.model,
            func.sum(TokenUsage.prompt_tokens).label("prompt_tokens"),
            func.sum(TokenUsage.completion_tokens).label("completion_tokens"),
            func.sum(TokenUsage.total_tokens).label("total_tokens"),
            func.sum(TokenUsage.estimated_cost).label("estimated_cost"),
            func.count(TokenUsage.id).label("requests")
        ).group_by(TokenUsage.model).all()

        # 按服务分组统计
        by_service = base_query.with_entities(
            TokenUsage.service,
            func.sum(TokenUsage.prompt_tokens).label("prompt_tokens"),
            func.sum(TokenUsage.completion_tokens).label("completion_tokens"),
            func.sum(TokenUsage.total_tokens).label("total_tokens"),
            func.sum(TokenUsage.estimated_cost).label("estimated_cost"),
            func.count(TokenUsage.id).label("requests")
        ).group_by(TokenUsage.service).all()

        # 按任务分组统计
        by_task = base_query.with_entities(
            TokenUsage.task,
            func.sum(TokenUsage.prompt_tokens).label("prompt_tokens"),
            func.sum(TokenUsage.completion_tokens).label("completion_tokens"),
            func.sum(TokenUsage.total_tokens).label("total_tokens"),
            func.sum(TokenUsage.estimated_cost).label("estimated_cost"),
            func.count(TokenUsage.id).label("requests")
        ).group_by(TokenUsage.task).all()

        # 按日期分组统计
        by_day = base_query.with_entities(
            func.date(TokenUsage.timestamp).label("day"),
            func.sum(TokenUsage.prompt_tokens).label("prompt_tokens"),
            func.sum(TokenUsage.completion_tokens).label("completion_tokens"),
            func.sum(TokenUsage.total_tokens).label("total_tokens"),
            func.sum(TokenUsage.estimated_cost).label("estimated_cost"),
            func.count(TokenUsage.id).label("requests")
        ).group_by(func.date(TokenUsage.timestamp)).all()

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
                item.model: {
                    "prompt_tokens": item.prompt_tokens or 0,
                    "completion_tokens": item.completion_tokens or 0,
                    "total_tokens": item.total_tokens or 0,
                    "estimated_cost": item.estimated_cost or 0,
                    "requests": item.requests or 0
                } for item in by_model
            },
            "by_service": {
                item.service: {
                    "prompt_tokens": item.prompt_tokens or 0,
                    "completion_tokens": item.completion_tokens or 0,
                    "total_tokens": item.total_tokens or 0,
                    "estimated_cost": item.estimated_cost or 0,
                    "requests": item.requests or 0
                } for item in by_service
            },
            "by_task": {
                item.task: {
                    "prompt_tokens": item.prompt_tokens or 0,
                    "completion_tokens": item.completion_tokens or 0,
                    "total_tokens": item.total_tokens or 0,
                    "estimated_cost": item.estimated_cost or 0,
                    "requests": item.requests or 0
                } for item in by_task
            },
            "by_day": {
                item.day.strftime("%Y-%m-%d"): {
                    "prompt_tokens": item.prompt_tokens or 0,
                    "completion_tokens": item.completion_tokens or 0,
                    "total_tokens": item.total_tokens or 0,
                    "estimated_cost": item.estimated_cost or 0,
                    "requests": item.requests or 0
                } for item in by_day
            },
            "filter": {
                "start_date": start_date,
                "end_date": end_date
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户token使用汇总失败: {str(e)}")

@router.get("/filter-options", response_model=Dict[str, List[str]])
async def get_token_usage_filter_options(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取token使用过滤选项（模型、服务、任务列表）"""
    try:
        # 查询用户的模型列表
        models = db.query(TokenUsage.model).filter(
            TokenUsage.user_id == current_user.id
        ).distinct().all()

        # 查询用户的服务列表
        services = db.query(TokenUsage.service).filter(
            TokenUsage.user_id == current_user.id
        ).distinct().all()

        # 查询用户的任务列表
        tasks = db.query(TokenUsage.task).filter(
            TokenUsage.user_id == current_user.id
        ).distinct().all()

        # 返回结果
        return {
            "models": [model[0] for model in models],
            "services": [service[0] for service in services],
            "tasks": [task[0] for task in tasks]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取token使用过滤选项失败: {str(e)}")
