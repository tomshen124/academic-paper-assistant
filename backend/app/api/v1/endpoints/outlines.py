from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

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
from app.api.deps import get_outline_service, get_db, get_current_active_user, get_current_active_superuser
from app.models.user import User
from app.models.topic import Topic
from app.models.outline import Outline
from app.core.logger import get_logger

# 创建日志器
logger = get_logger("outlines_api")

router = APIRouter()

@router.post("/generate", response_model=OutlineResponse)
async def generate_outline(
    request: OutlineRequest,
    outline_service: OutlineService = Depends(get_outline_service),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """生成论文提纲"""
    try:
        # 生成提纲
        outline = await outline_service.generate_outline(
            topic=request.topic,
            paper_type=request.paper_type,
            academic_field=request.academic_field,
            academic_level=request.academic_level,
            length=request.length
        )

        # 查找主题
        topic = db.query(Topic).filter(
            Topic.user_id == current_user.id,
            Topic.title == request.topic
        ).first()

        # 如果主题不存在，创建一个新主题
        if not topic:
            logger.info(f"为用户 {current_user.id} 创建新主题: {request.topic}")
            topic = Topic(
                user_id=current_user.id,
                title=request.topic,
                academic_field=request.academic_field,
                academic_level=request.academic_level
            )
            db.add(topic)
            db.flush()  # 获取主题ID

        # 保存提纲到数据库
        logger.info(f"为用户 {current_user.id} 保存提纲: {outline.get('title', 'N/A')}")
        db_outline = Outline(
            user_id=current_user.id,
            topic_id=topic.id,
            title=outline.get('title', request.topic),
            abstract=outline.get('abstract', ''),
            keywords=outline.get('keywords', []),
            sections=outline.get('sections', []),
            paper_type=request.paper_type,
            academic_field=request.academic_field,
            academic_level=request.academic_level,
            length=request.length
        )
        db.add(db_outline)
        db.commit()

        return outline
    except Exception as e:
        db.rollback()
        logger.error(f"生成提纲失败: {str(e)}")
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

@router.get("/")
async def get_user_outlines(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100
):
    """获取用户的提纲列表"""
    try:
        # 添加日志
        logger.info(f"用户 {current_user.username} (ID: {current_user.id}) 获取提纲列表")

        # 查询用户的提纲
        outlines = db.query(Outline).filter(
            Outline.user_id == current_user.id
        ).order_by(Outline.created_at.desc()).offset(skip).limit(limit).all()

        # 格式化响应
        result = []
        for outline in outlines:
            # 获取相关主题
            topic = db.query(Topic).filter(Topic.id == outline.topic_id).first()
            topic_title = topic.title if topic else "未知主题"

            result.append({
                "id": outline.id,
                "title": outline.title,
                "topic": topic_title,
                "topic_id": outline.topic_id,
                "abstract": outline.abstract,
                "keywords": outline.keywords,
                "paper_type": outline.paper_type,
                "academic_field": outline.academic_field,
                "academic_level": outline.academic_level,
                "created_at": outline.created_at,
                "updated_at": outline.updated_at
            })

        logger.info(f"找到 {len(result)} 条提纲记录")
        return {"outlines": result, "total": len(result)}
    except Exception as e:
        logger.error(f"获取用户提纲列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取用户提纲列表失败: {str(e)}")

@router.get("/admin/all")
async def get_all_outlines(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None
):
    """获取所有用户的提纲（仅超级管理员可用）"""
    try:
        # 添加日志
        logger.info(f"超级管理员 {current_user.username} (ID: {current_user.id}) 获取所有提纲列表")

        # 构建查询
        query = db.query(Outline)
        if user_id:
            query = query.filter(Outline.user_id == user_id)

        # 执行查询
        outlines = query.order_by(Outline.created_at.desc()).offset(skip).limit(limit).all()

        # 获取用户信息
        user_ids = set(outline.user_id for outline in outlines)
        users = {user.id: user for user in db.query(User).filter(User.id.in_(user_ids)).all()}

        # 获取主题信息
        topic_ids = set(outline.topic_id for outline in outlines)
        topics = {topic.id: topic for topic in db.query(Topic).filter(Topic.id.in_(topic_ids)).all()}

        result = []
        for outline in outlines:
            # 获取相关主题
            topic = topics.get(outline.topic_id)
            topic_title = topic.title if topic else "未知主题"

            # 获取用户信息
            user = users.get(outline.user_id)
            username = user.username if user else "未知用户"

            result.append({
                "id": outline.id,
                "user_id": outline.user_id,
                "username": username,
                "title": outline.title,
                "topic": topic_title,
                "topic_id": outline.topic_id,
                "abstract": outline.abstract,
                "keywords": outline.keywords,
                "paper_type": outline.paper_type,
                "academic_field": outline.academic_field,
                "academic_level": outline.academic_level,
                "created_at": outline.created_at,
                "updated_at": outline.updated_at
            })

        logger.info(f"找到 {len(result)} 条提纲记录")
        return {"outlines": result, "total": len(result)}
    except Exception as e:
        logger.error(f"获取所有提纲列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取所有提纲列表失败: {str(e)}")

@router.get("/{outline_id}")
async def get_outline_by_id(
    outline_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """根据ID获取提纲"""
    try:
        # 查询提纲
        outline = db.query(Outline).filter(
            Outline.id == outline_id,
            Outline.user_id == current_user.id
        ).first()

        if not outline:
            raise HTTPException(status_code=404, detail="提纲不存在")

        # 获取相关主题
        topic = db.query(Topic).filter(Topic.id == outline.topic_id).first()
        topic_title = topic.title if topic else "未知主题"

        return {
            "id": outline.id,
            "title": outline.title,
            "topic": topic_title,
            "topic_id": outline.topic_id,
            "abstract": outline.abstract,
            "keywords": outline.keywords,
            "sections": outline.sections,
            "paper_type": outline.paper_type,
            "academic_field": outline.academic_field,
            "academic_level": outline.academic_level,
            "length": outline.length,
            "created_at": outline.created_at,
            "updated_at": outline.updated_at
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取提纲失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取提纲失败: {str(e)}")
