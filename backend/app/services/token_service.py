from typing import Dict, List, Any, Optional
import time
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.logger import get_logger
from app.utils.token_counter import token_counter
from app.db.session import SessionLocal
from app.models.token_usage import TokenUsage

# 创建日志器
logger = get_logger("token_service")

class TokenService:
    """Token使用追踪服务，用于监控和管理LLM的token使用情况"""

    def __init__(self):
        """初始化Token服务"""
        self.start_time = time.time()
        logger.info("Token服务初始化完成")

    def record_usage(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        service: str = "unknown",
        task: str = "unknown",
        task_type: str = "default",
        user_id: int = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """记录token使用情况"""
        try:
            # 计算总token
            total_tokens = prompt_tokens + completion_tokens

            # 估算成本
            cost = token_counter.estimate_cost(prompt_tokens, completion_tokens, model)

            # 记录日志
            logger.info(
                f"Token使用: 模型={model}, 服务={service}, "
                f"输入={prompt_tokens}, 输出={completion_tokens}, "
                f"总计={total_tokens}, 成本=${cost:.4f}"
            )

            # 必须提供用户ID才能保存记录
            if user_id is None:
                logger.warning("未提供用户ID，无法保存Token使用记录到数据库")
                return {
                    "timestamp": datetime.now().isoformat(),
                    "model": model,
                    "service": service,
                    "task": task,
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens,
                    "estimated_cost": cost,
                    "warning": "未保存到数据库"
                }

            try:
                # 如果没有提供数据库会话，创建一个新的
                close_db = False
                if db is None:
                    db = SessionLocal()
                    close_db = True

                # 创建数据库记录
                db_record = TokenUsage(
                    user_id=user_id,
                    model=model,
                    service=service,
                    task=task,
                    task_type=task_type,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens,
                    estimated_cost=cost
                )

                # 添加并提交
                db.add(db_record)
                db.commit()
                db.refresh(db_record)

                logger.info(f"Token使用记录已保存到数据库，ID: {db_record.id}")

                # 构建返回记录
                record = {
                    "id": db_record.id,
                    "timestamp": db_record.timestamp.isoformat(),
                    "model": db_record.model,
                    "service": db_record.service,
                    "task": db_record.task,
                    "task_type": db_record.task_type,
                    "prompt_tokens": db_record.prompt_tokens,
                    "completion_tokens": db_record.completion_tokens,
                    "total_tokens": db_record.total_tokens,
                    "estimated_cost": db_record.estimated_cost
                }

                # 如果是我们创建的会话，关闭它
                if close_db:
                    db.close()

                return record

            except Exception as e:
                logger.error(f"保存Token使用记录到数据库失败: {str(e)}")
                # 如果是我们创建的会话，回滚并关闭
                if close_db and db is not None:
                    db.rollback()
                    db.close()
                raise

        except Exception as e:
            logger.error(f"记录token使用失败: {str(e)}")
            return {
                "error": str(e),
                "model": model,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens
            }

    def get_usage_summary(self, db: Session = None, start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
        """从数据库获取token使用摘要

        Args:
            db: 数据库会话
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）
        """
        try:
            # 如果没有提供数据库会话，创建一个新的
            close_db = False
            if db is None:
                db = SessionLocal()
                close_db = True

            try:
                # 构建基础查询
                base_query = db.query(TokenUsage)

                # 添加日期过滤条件
                if start_date:
                    base_query = base_query.filter(TokenUsage.timestamp >= start_date)
                if end_date:
                    base_query = base_query.filter(TokenUsage.timestamp <= end_date)

                # 计算总使用量
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

                # 按任务类型分组统计
                by_task_type = base_query.with_entities(
                    TokenUsage.task_type,
                    func.sum(TokenUsage.prompt_tokens).label("prompt_tokens"),
                    func.sum(TokenUsage.completion_tokens).label("completion_tokens"),
                    func.sum(TokenUsage.total_tokens).label("total_tokens"),
                    func.sum(TokenUsage.estimated_cost).label("estimated_cost"),
                    func.count(TokenUsage.id).label("requests")
                ).group_by(TokenUsage.task_type).all()

                # 按日期分组统计
                by_day = base_query.with_entities(
                    func.date(TokenUsage.timestamp).label("day"),
                    func.sum(TokenUsage.prompt_tokens).label("prompt_tokens"),
                    func.sum(TokenUsage.completion_tokens).label("completion_tokens"),
                    func.sum(TokenUsage.total_tokens).label("total_tokens"),
                    func.sum(TokenUsage.estimated_cost).label("estimated_cost"),
                    func.count(TokenUsage.id).label("requests")
                ).group_by(func.date(TokenUsage.timestamp)).all()

                # 计算运行时间
                uptime_seconds = time.time() - self.start_time
                uptime_hours = uptime_seconds / 3600

                # 提取统计数据
                total_prompt_tokens = result.prompt_tokens or 0
                total_completion_tokens = result.completion_tokens or 0
                total_tokens = result.total_tokens or 0
                total_cost = result.estimated_cost or 0
                total_requests = result.requests or 0

                # 计算平均值
                avg_tokens_per_request = total_tokens / total_requests if total_requests > 0 else 0
                avg_cost_per_request = total_cost / total_requests if total_requests > 0 else 0
                avg_tokens_per_hour = total_tokens / uptime_hours if uptime_hours > 0 else 0
                avg_cost_per_hour = total_cost / uptime_hours if uptime_hours > 0 else 0

                # 构建结果
                summary = {
                    "total_usage": {
                        "prompt_tokens": total_prompt_tokens,
                        "completion_tokens": total_completion_tokens,
                        "total_tokens": total_tokens,
                        "estimated_cost": total_cost,
                        "requests": total_requests
                    },
                    "averages": {
                        "tokens_per_request": avg_tokens_per_request,
                        "cost_per_request": avg_cost_per_request,
                        "tokens_per_hour": avg_tokens_per_hour,
                        "cost_per_hour": avg_cost_per_hour
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
                    "by_task_type": {
                        item.task_type: {
                            "prompt_tokens": item.prompt_tokens or 0,
                            "completion_tokens": item.completion_tokens or 0,
                            "total_tokens": item.total_tokens or 0,
                            "estimated_cost": item.estimated_cost or 0,
                            "requests": item.requests or 0
                        } for item in by_task_type
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
                    "uptime_seconds": uptime_seconds,
                    "uptime_hours": uptime_hours
                }

                return summary

            finally:
                # 如果是我们创建的会话，关闭它
                if close_db:
                    db.close()

        except Exception as e:
            logger.error(f"获取token使用摘要失败: {str(e)}")
            # 返回一个空的摘要对象，而不是错误对象
            return {
                "total_usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                    "estimated_cost": 0,
                    "requests": 0
                },
                "averages": {
                    "tokens_per_request": 0,
                    "cost_per_request": 0,
                    "tokens_per_hour": 0,
                    "cost_per_hour": 0
                },
                "by_model": {},
                "by_service": {},
                "by_task": {},
                "by_task_type": {},
                "by_day": {},
                "uptime_seconds": 0,
                "uptime_hours": 0
            }

    def get_recent_usage(self, db: Session = None, limit: int = 10) -> List[Dict[str, Any]]:
        """从数据库获取最近的token使用记录"""
        try:
            # 如果没有提供数据库会话，创建一个新的
            close_db = False
            if db is None:
                db = SessionLocal()
                close_db = True

            try:
                # 查询最近的记录
                records = db.query(TokenUsage).order_by(TokenUsage.timestamp.desc()).limit(limit).all()

                # 转换为字典列表
                result = [{
                    "id": record.id,
                    "timestamp": record.timestamp.isoformat(),
                    "day": record.timestamp.strftime("%Y-%m-%d"),  # 添加缺少的day字段
                    "model": record.model,
                    "service": record.service,
                    "task": record.task,
                    "task_type": record.task_type,
                    "prompt_tokens": record.prompt_tokens,
                    "completion_tokens": record.completion_tokens,
                    "total_tokens": record.total_tokens,
                    "estimated_cost": record.estimated_cost,
                    "user_id": record.user_id
                } for record in records]

                return result

            finally:
                # 如果是我们创建的会话，关闭它
                if close_db:
                    db.close()

        except Exception as e:
            logger.error(f"获取最近token使用记录失败: {str(e)}")
            return []

    def export_usage_data(self, db: Session = None, format: str = "json", start_date: datetime = None, end_date: datetime = None) -> str:
        """从数据库导出token使用数据"""
        try:
            # 获取摘要和记录
            summary = self.get_usage_summary(db=db, start_date=start_date, end_date=end_date)

            # 如果没有提供数据库会话，创建一个新的
            close_db = False
            if db is None:
                db = SessionLocal()
                close_db = True

            try:
                # 构建查询
                query = db.query(TokenUsage)

                # 添加日期过滤条件
                if start_date:
                    query = query.filter(TokenUsage.timestamp >= start_date)
                if end_date:
                    query = query.filter(TokenUsage.timestamp <= end_date)

                # 获取所有记录
                records = query.order_by(TokenUsage.timestamp.desc()).all()

                # 转换为字典列表
                records_data = [{
                    "id": record.id,
                    "timestamp": record.timestamp.isoformat(),
                    "day": record.timestamp.strftime("%Y-%m-%d"),  # 添加缺少的day字段
                    "model": record.model,
                    "service": record.service,
                    "task": record.task,
                    "task_type": record.task_type,
                    "prompt_tokens": record.prompt_tokens,
                    "completion_tokens": record.completion_tokens,
                    "total_tokens": record.total_tokens,
                    "estimated_cost": record.estimated_cost,
                    "user_id": record.user_id
                } for record in records]

                # 构建导出数据
                data = {
                    "summary": summary,
                    "records": records_data,
                    "export_time": datetime.now().isoformat(),
                    "filter": {
                        "start_date": start_date.isoformat() if start_date else None,
                        "end_date": end_date.isoformat() if end_date else None
                    }
                }

                # 转换为JSON
                if format.lower() == "json":
                    return json.dumps(data, indent=2, ensure_ascii=False)
                else:
                    # 默认返回JSON
                    return json.dumps(data, indent=2, ensure_ascii=False)

            finally:
                # 如果是我们创建的会话，关闭它
                if close_db:
                    db.close()

        except Exception as e:
            logger.error(f"导出token使用数据失败: {str(e)}")
            return json.dumps({"error": str(e)}, ensure_ascii=False)

# 创建全局Token服务实例
token_service = TokenService()
