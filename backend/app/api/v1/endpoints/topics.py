from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.schemas.topic import (
    TopicRequest,
    TopicResponse,
    TopicFeasibilityRequest,
    TopicFeasibilityResponse,
    TopicRefinementRequest,
    TopicRefinementResponse
)
from app.services.topic_service import TopicService
from app.api.deps import get_topic_service, get_db, get_current_active_user
from app.models.user import User
from app.models.topic import Topic

router = APIRouter()

@router.post("/recommend", response_model=List[TopicResponse])
async def recommend_topics(
    request: TopicRequest,
    topic_service: TopicService = Depends(get_topic_service),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """推荐论文主题"""
    try:
        # 使用服务生成推荐主题
        topics = await topic_service.recommend_topics(
            user_interests=request.user_interests,
            academic_field=request.academic_field,
            academic_level=request.academic_level,
            topic_count=request.topic_count,
            interest_analysis=request.interest_analysis
        )

        # 将推荐的主题保存到数据库
        for topic_data in topics:
            # 检查topic_data是否为字典类型
            if isinstance(topic_data, dict):
                db_topic = Topic(
                    user_id=current_user.id,
                    title=topic_data.get('title', ''),
                    research_question=topic_data.get('research_question', ''),
                    feasibility=topic_data.get('feasibility', ''),
                    innovation=topic_data.get('innovation', ''),
                    methodology=topic_data.get('methodology', ''),
                    resources=topic_data.get('resources', ''),
                    expected_outcomes=topic_data.get('expected_outcomes', ''),
                    academic_field=request.academic_field,
                    academic_level=request.academic_level,
                    keywords=topic_data.get('keywords', [])
                )
            else:
                # 如果不是字典，尝试将其作为对象处理
                try:
                    db_topic = Topic(
                        user_id=current_user.id,
                        title=topic_data.title,
                        academic_field=request.academic_field,
                        academic_level=request.academic_level,
                        keywords=topic_data.keywords
                    )
                except Exception as e:
                    # 如果出错，记录错误并跳过这个主题
                    import logging
                    logging.error(f"处理主题数据失败: {str(e)}, 数据: {topic_data}")
                    continue

            db.add(db_topic)

        db.commit()
        return topics
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"推荐主题失败: {str(e)}")

@router.post("/analyze", response_model=TopicFeasibilityResponse)
async def analyze_topic_feasibility(
    request: TopicFeasibilityRequest,
    topic_service: TopicService = Depends(get_topic_service),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """分析主题可行性"""
    try:
        # 分析主题可行性
        analysis = await topic_service.analyze_topic_feasibility(
            topic=request.topic,
            academic_field=request.academic_field,
            academic_level=request.academic_level
        )

        # 查找或创建主题记录
        db_topic = db.query(Topic).filter(
            Topic.user_id == current_user.id,
            Topic.title == request.topic
        ).first()

        if not db_topic:
            db_topic = Topic(
                user_id=current_user.id,
                title=request.topic,
                academic_field=request.academic_field,
                academic_level=request.academic_level
            )
            db.add(db_topic)

        # 更新可行性分析结果
        db_topic.feasibility = analysis.feasibility
        db_topic.innovation = analysis.innovation
        db_topic.methodology = analysis.methodology
        db_topic.resources = analysis.resources
        db_topic.expected_outcomes = analysis.expected_outcomes

        db.commit()
        return analysis
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"分析主题可行性失败: {str(e)}")

@router.post("/refine", response_model=TopicRefinementResponse)
async def refine_topic(
    request: TopicRefinementRequest,
    topic_service: TopicService = Depends(get_topic_service),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """优化论文主题"""
    try:
        # 优化主题
        refined_topic = await topic_service.refine_topic(
            topic=request.topic,
            feedback=request.feedback,
            academic_field=request.academic_field,
            academic_level=request.academic_level
        )

        # 将优化后的主题保存到数据库
        db_topic = Topic(
            user_id=current_user.id,
            title=refined_topic.refined_title,
            research_question=refined_topic.research_question,
            academic_field=request.academic_field,
            academic_level=request.academic_level,
            keywords=refined_topic.keywords
        )
        db.add(db_topic)
        db.commit()

        return refined_topic
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"优化主题失败: {str(e)}")

@router.get("/", response_model=List[dict])
async def get_user_topics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100
):
    """获取用户的所有主题"""
    try:
        topics = db.query(Topic).filter(Topic.user_id == current_user.id).offset(skip).limit(limit).all()
        return [{
            "id": topic.id,
            "title": topic.title,
            "academic_field": topic.academic_field,
            "academic_level": topic.academic_level,
            "research_question": topic.research_question,
            "feasibility": topic.feasibility,
            "keywords": topic.keywords,
            "created_at": topic.created_at
        } for topic in topics]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取主题列表失败: {str(e)}")

@router.get("/{topic_id}", response_model=dict)
async def get_topic_by_id(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """根据ID获取主题"""
    try:
        topic = db.query(Topic).filter(Topic.id == topic_id, Topic.user_id == current_user.id).first()
        if not topic:
            raise HTTPException(status_code=404, detail="主题不存在")

        return {
            "id": topic.id,
            "title": topic.title,
            "academic_field": topic.academic_field,
            "academic_level": topic.academic_level,
            "research_question": topic.research_question,
            "feasibility": topic.feasibility,
            "innovation": topic.innovation,
            "methodology": topic.methodology,
            "resources": topic.resources,
            "expected_outcomes": topic.expected_outcomes,
            "keywords": topic.keywords,
            "created_at": topic.created_at,
            "updated_at": topic.updated_at
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取主题失败: {str(e)}")
