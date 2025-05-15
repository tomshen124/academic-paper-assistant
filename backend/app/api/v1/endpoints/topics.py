from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any, AsyncGenerator, Optional
from sqlalchemy.orm import Session
import json
import asyncio

from app.schemas.topic import (
    TopicRequest,
    TopicResponse,
    TopicFeasibilityRequest,
    TopicFeasibilityResponse,
    TopicRefinementRequest,
    TopicRefinementResponse
)
from app.services.topic_service import TopicService
from app.api.deps import get_topic_service, get_db, get_current_active_user, get_current_active_superuser, optional_oauth2_scheme
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
        # 添加日志
        import logging
        logger = logging.getLogger("app")
        logger.info(f"用户 {current_user.username} (ID: {current_user.id}) 获取主题列表")

        topics = db.query(Topic).filter(Topic.user_id == current_user.id).offset(skip).limit(limit).all()
        result = [{
            "id": topic.id,
            "title": topic.title,
            "academic_field": topic.academic_field,
            "academic_level": topic.academic_level,
            "research_question": topic.research_question,
            "feasibility": topic.feasibility,
            "keywords": topic.keywords,
            "created_at": topic.created_at
        } for topic in topics]

        logger.info(f"找到 {len(result)} 条主题记录")
        return result
    except Exception as e:
        import logging
        logger = logging.getLogger("app")
        logger.error(f"获取主题列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取主题列表失败: {str(e)}")

@router.get("/admin/all", response_model=List[dict])
async def get_all_topics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None
):
    """获取所有用户的主题（仅超级管理员可用）"""
    try:
        # 添加日志
        import logging
        logger = logging.getLogger("app")
        logger.info(f"超级管理员 {current_user.username} (ID: {current_user.id}) 获取所有主题列表")

        # 构建查询
        query = db.query(Topic)
        if user_id:
            query = query.filter(Topic.user_id == user_id)

        # 执行查询
        topics = query.order_by(Topic.created_at.desc()).offset(skip).limit(limit).all()

        # 获取用户信息
        user_ids = set(topic.user_id for topic in topics)
        users = {user.id: user for user in db.query(User).filter(User.id.in_(user_ids)).all()}

        result = [{
            "id": topic.id,
            "user_id": topic.user_id,
            "username": users.get(topic.user_id).username if topic.user_id in users else "Unknown",
            "title": topic.title,
            "academic_field": topic.academic_field,
            "academic_level": topic.academic_level,
            "research_question": topic.research_question,
            "feasibility": topic.feasibility,
            "keywords": topic.keywords,
            "created_at": topic.created_at,
            "updated_at": topic.updated_at
        } for topic in topics]

        logger.info(f"找到 {len(result)} 条主题记录")
        return result
    except Exception as e:
        import logging
        logger = logging.getLogger("app")
        logger.error(f"获取所有主题列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取所有主题列表失败: {str(e)}")

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

@router.get("/recommend/stream")
async def recommend_topics_stream(
    request: Request,
    user_interests: str,
    academic_field: str,
    academic_level: str = "undergraduate",
    topic_count: int = 3,
    topic_service: TopicService = Depends(get_topic_service),
    db: Session = Depends(get_db)
):
    """流式推荐论文主题"""
    # 添加调试日志
    import logging
    from app.core.security import decode_access_token, SECRET_KEY, ALGORITHM
    from jose import jwt, JWTError
    logger = logging.getLogger("app")
    logger.info(f"SSE请求参数: user_interests={user_interests}, academic_field={academic_field}, academic_level={academic_level}, topic_count={topic_count}")

    # 从URL参数获取token
    token = request.query_params.get("token")
    if not token:
        logger.warning("URL参数中没有token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.info(f"从URL参数获取到token: {token[:10]}...")

    # 验证token
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            logger.warning("令牌中没有用户名")
            raise credentials_exception
        logger.info(f"令牌验证成功，用户名: {username}")

        # 获取用户信息
        current_user = db.query(User).filter(User.username == username).first()
        if current_user is None:
            raise credentials_exception

        user_id = current_user.id
        username = current_user.username
        user_info = f"用户: {username} (ID: {user_id})"
    except JWTError as e:
        logger.error(f"令牌验证失败: {str(e)}")
        raise credentials_exception

    logger.info(f"SSE请求用户: {user_info}")

    # 创建一个列表来存储生成的主题，以便在流式生成完成后保存到数据库
    generated_topics = []

    async def generate_stream() -> AsyncGenerator[bytes, None]:
        try:
            # 第一步：分析用户兴趣
            status_msg = json.dumps({"type": "status", "message": "正在分析用户兴趣..."})
            yield f"data: {status_msg}\n\n".encode('utf-8')

            # 异步分析用户兴趣
            interest_analysis = await topic_service.analyze_interests_streaming(
                user_interests=user_interests,
                academic_field=academic_field,
                academic_level=academic_level
            )

            # 将分析结果发送给前端
            analysis_msg = json.dumps({"type": "interest_analysis", "data": interest_analysis})
            yield f"data: {analysis_msg}\n\n".encode('utf-8')

            # 第二步：生成主题推荐
            recommend_msg = json.dumps({"type": "status", "message": "正在生成主题推荐..."})
            yield f"data: {recommend_msg}\n\n".encode('utf-8')

            # 流式生成主题
            async for topic in topic_service.recommend_topics_streaming(
                user_interests=user_interests,
                academic_field=academic_field,
                academic_level=academic_level,
                topic_count=topic_count,
                interest_analysis=interest_analysis
            ):
                # 将生成的主题添加到列表中，以便后续保存到数据库
                generated_topics.append(topic)

                # 将每个生成的主题发送给前端
                topic_msg = json.dumps({"type": "topic", "data": topic})
                yield f"data: {topic_msg}\n\n".encode('utf-8')

                # 模拟一些延迟，使前端可以看到渐进式生成
                await asyncio.sleep(0.5)

            # 将生成的主题保存到数据库
            try:
                logger.info(f"将 {len(generated_topics)} 个主题保存到数据库")
                for topic_data in generated_topics:
                    db_topic = Topic(
                        user_id=user_id,
                        title=topic_data.get('title', ''),
                        research_question=topic_data.get('research_question', ''),
                        feasibility=topic_data.get('feasibility', ''),
                        innovation=topic_data.get('innovation', ''),
                        methodology=topic_data.get('methodology', ''),
                        resources=topic_data.get('resources', ''),
                        expected_outcomes=topic_data.get('expected_outcomes', ''),
                        academic_field=academic_field,
                        academic_level=academic_level,
                        keywords=topic_data.get('keywords', [])
                    )
                    db.add(db_topic)

                db.commit()
                logger.info("主题成功保存到数据库")
            except Exception as e:
                db.rollback()
                logger.error(f"保存主题到数据库失败: {str(e)}")

            # 完成信号
            complete_msg = json.dumps({"type": "complete", "message": "主题生成完成"})
            yield f"data: {complete_msg}\n\n".encode('utf-8')

        except Exception as e:
            # 发送错误信息
            error_msg = json.dumps({"type": "error", "message": f"生成主题失败: {str(e)}"})
            yield f"data: {error_msg}\n\n".encode('utf-8')

    # 创建一个异步生成器包装器，在生成完成后关闭数据库连接
    async def wrapped_generator():
        try:
            async for chunk in generate_stream():
                yield chunk
        finally:
            # 无论生成是否成功或失败，都关闭数据库连接
            db.close()
            logger.info("数据库连接已关闭")

    # 创建流式响应
    return StreamingResponse(
        wrapped_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
