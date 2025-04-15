from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any

from app.schemas.topic import (
    TopicRequest,
    TopicResponse,
    TopicFeasibilityRequest,
    TopicFeasibilityResponse,
    TopicRefinementRequest,
    TopicRefinementResponse
)
from app.services.topic_service import TopicService
from app.api.deps import get_topic_service

router = APIRouter()

@router.post("/recommend", response_model=List[TopicResponse])
async def recommend_topics(
    request: TopicRequest,
    topic_service: TopicService = Depends(get_topic_service)
):
    """推荐论文主题"""
    try:
        topics = await topic_service.recommend_topics(
            user_interests=request.user_interests,
            academic_field=request.academic_field,
            academic_level=request.academic_level
        )
        return topics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"推荐主题失败: {str(e)}")

@router.post("/analyze", response_model=TopicFeasibilityResponse)
async def analyze_topic_feasibility(
    request: TopicFeasibilityRequest,
    topic_service: TopicService = Depends(get_topic_service)
):
    """分析主题可行性"""
    try:
        analysis = await topic_service.analyze_topic_feasibility(
            topic=request.topic,
            academic_field=request.academic_field,
            academic_level=request.academic_level
        )
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析主题可行性失败: {str(e)}")

@router.post("/refine", response_model=TopicRefinementResponse)
async def refine_topic(
    request: TopicRefinementRequest,
    topic_service: TopicService = Depends(get_topic_service)
):
    """优化论文主题"""
    try:
        refined_topic = await topic_service.refine_topic(
            topic=request.topic,
            feedback=request.feedback,
            academic_field=request.academic_field,
            academic_level=request.academic_level
        )
        return refined_topic
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"优化主题失败: {str(e)}")
