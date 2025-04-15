from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any

from app.schemas.outline import (
    OutlineRequest,
    OutlineResponse,
    OutlineOptimizationRequest,
    OutlineTemplateRequest,
    OutlineTemplate,
    OutlineValidationRequest,
    OutlineValidationResponse
)
from app.services.outline_service import OutlineService
from app.api.deps import get_outline_service

router = APIRouter()

@router.post("/generate", response_model=OutlineResponse)
async def generate_outline(
    request: OutlineRequest,
    outline_service: OutlineService = Depends(get_outline_service)
):
    """生成论文提纲"""
    try:
        outline = await outline_service.generate_outline(
            topic=request.topic,
            paper_type=request.paper_type,
            academic_field=request.academic_field,
            academic_level=request.academic_level,
            length=request.length
        )
        return outline
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成提纲失败: {str(e)}")

@router.post("/optimize", response_model=OutlineResponse)
async def optimize_outline(
    request: OutlineOptimizationRequest,
    outline_service: OutlineService = Depends(get_outline_service)
):
    """优化论文提纲"""
    try:
        optimized_outline = await outline_service.optimize_outline(
            outline=request.outline,
            feedback=request.feedback
        )
        return optimized_outline
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"优化提纲失败: {str(e)}")

@router.post("/templates", response_model=List[OutlineTemplate])
async def get_outline_templates(
    request: OutlineTemplateRequest,
    outline_service: OutlineService = Depends(get_outline_service)
):
    """获取提纲模板"""
    try:
        templates = await outline_service.get_outline_templates(
            paper_type=request.paper_type,
            academic_field=request.academic_field
        )
        return templates
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取提纲模板失败: {str(e)}")

@router.post("/validate", response_model=OutlineValidationResponse)
async def validate_outline(
    request: OutlineValidationRequest,
    outline_service: OutlineService = Depends(get_outline_service)
):
    """验证提纲逻辑"""
    try:
        validation = await outline_service.validate_outline_logic(
            outline=request.outline
        )
        return validation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"验证提纲失败: {str(e)}")
