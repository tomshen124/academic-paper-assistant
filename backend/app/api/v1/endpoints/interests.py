from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.schemas.topic import TopicRequest
from app.services.interest_analysis_service import interest_analysis_service
from app.api.deps import get_db, get_current_active_user
from app.models.user import User

router = APIRouter()

@router.post("/analyze", response_model=Dict[str, Any])
async def analyze_interests(
    request: TopicRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """分析用户兴趣并生成初步的主题方向"""
    try:
        # 使用兴趣分析服务分析用户兴趣
        analysis_result = await interest_analysis_service.analyze_interests(
            user_interests=request.user_interests,
            academic_field=request.academic_field,
            academic_level=request.academic_level
        )
        
        return analysis_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析用户兴趣失败: {str(e)}")
