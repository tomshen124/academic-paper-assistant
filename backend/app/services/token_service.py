from typing import Dict, List, Any, Optional
import time
import json
from datetime import datetime
from sqlalchemy.orm import Session
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
        self.usage_records = []
        self.usage_by_model = {}
        self.usage_by_service = {}
        self.usage_by_day = {}
        self.start_time = time.time()
        logger.info("Token服务初始化完成")

    def record_usage(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        service: str = "unknown",
        task: str = "unknown",
        user_id: int = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """记录token使用情况"""
        try:
            # 计算总token
            total_tokens = prompt_tokens + completion_tokens

            # 估算成本
            cost = token_counter.estimate_cost(prompt_tokens, completion_tokens, model)

            # 创建记录
            timestamp = datetime.now().isoformat()
            day = datetime.now().strftime("%Y-%m-%d")

            record = {
                "timestamp": timestamp,
                "day": day,
                "model": model,
                "service": service,
                "task": task,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "estimated_cost": cost
            }

            # 添加到记录列表
            self.usage_records.append(record)

            # 更新按模型统计
            if model not in self.usage_by_model:
                self.usage_by_model[model] = {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                    "estimated_cost": 0,
                    "requests": 0
                }

            self.usage_by_model[model]["prompt_tokens"] += prompt_tokens
            self.usage_by_model[model]["completion_tokens"] += completion_tokens
            self.usage_by_model[model]["total_tokens"] += total_tokens
            self.usage_by_model[model]["estimated_cost"] += cost
            self.usage_by_model[model]["requests"] += 1

            # 更新按服务统计
            if service not in self.usage_by_service:
                self.usage_by_service[service] = {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                    "estimated_cost": 0,
                    "requests": 0
                }

            self.usage_by_service[service]["prompt_tokens"] += prompt_tokens
            self.usage_by_service[service]["completion_tokens"] += completion_tokens
            self.usage_by_service[service]["total_tokens"] += total_tokens
            self.usage_by_service[service]["estimated_cost"] += cost
            self.usage_by_service[service]["requests"] += 1

            # 更新按日期统计
            if day not in self.usage_by_day:
                self.usage_by_day[day] = {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                    "estimated_cost": 0,
                    "requests": 0
                }

            self.usage_by_day[day]["prompt_tokens"] += prompt_tokens
            self.usage_by_day[day]["completion_tokens"] += completion_tokens
            self.usage_by_day[day]["total_tokens"] += total_tokens
            self.usage_by_day[day]["estimated_cost"] += cost
            self.usage_by_day[day]["requests"] += 1

            # 记录日志
            logger.info(
                f"Token使用: 模型={model}, 服务={service}, "
                f"输入={prompt_tokens}, 输出={completion_tokens}, "
                f"总计={total_tokens}, 成本=${cost:.4f}"
            )

            # 如果提供了用户ID，将记录保存到数据库
            if user_id is not None:
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
                        prompt_tokens=prompt_tokens,
                        completion_tokens=completion_tokens,
                        total_tokens=total_tokens,
                        estimated_cost=cost
                    )

                    # 添加并提交
                    db.add(db_record)
                    db.commit()

                    logger.info(f"Token使用记录已保存到数据库，ID: {db_record.id}")

                    # 如果是我们创建的会话，关闭它
                    if close_db:
                        db.close()
                except Exception as e:
                    logger.error(f"保存Token使用记录到数据库失败: {str(e)}")
                    # 如果是我们创建的会话，回滚并关闭
                    if close_db and db is not None:
                        db.rollback()
                        db.close()

            return record

        except Exception as e:
            logger.error(f"记录token使用失败: {str(e)}")
            return {
                "error": str(e),
                "model": model,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens
            }

    def get_usage_summary(self) -> Dict[str, Any]:
        """获取token使用摘要"""
        try:
            # 计算总使用量
            total_prompt_tokens = sum(record["prompt_tokens"] for record in self.usage_records)
            total_completion_tokens = sum(record["completion_tokens"] for record in self.usage_records)
            total_tokens = total_prompt_tokens + total_completion_tokens
            total_cost = sum(record["estimated_cost"] for record in self.usage_records)
            total_requests = len(self.usage_records)

            # 计算运行时间
            uptime_seconds = time.time() - self.start_time
            uptime_hours = uptime_seconds / 3600

            # 计算平均值
            avg_tokens_per_request = total_tokens / total_requests if total_requests > 0 else 0
            avg_cost_per_request = total_cost / total_requests if total_requests > 0 else 0
            avg_tokens_per_hour = total_tokens / uptime_hours if uptime_hours > 0 else 0
            avg_cost_per_hour = total_cost / uptime_hours if uptime_hours > 0 else 0

            return {
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
                "by_model": self.usage_by_model,
                "by_service": self.usage_by_service,
                "by_day": self.usage_by_day,
                "uptime_seconds": uptime_seconds,
                "uptime_hours": uptime_hours
            }

        except Exception as e:
            logger.error(f"获取token使用摘要失败: {str(e)}")
            return {"error": str(e)}

    def get_recent_usage(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最近的token使用记录"""
        try:
            # 返回最近的记录
            return self.usage_records[-limit:] if self.usage_records else []
        except Exception as e:
            logger.error(f"获取最近token使用记录失败: {str(e)}")
            return []

    def export_usage_data(self, format: str = "json") -> str:
        """导出token使用数据"""
        try:
            data = {
                "summary": self.get_usage_summary(),
                "records": self.usage_records
            }

            if format.lower() == "json":
                return json.dumps(data, indent=2)
            else:
                # 默认返回JSON
                return json.dumps(data, indent=2)

        except Exception as e:
            logger.error(f"导出token使用数据失败: {str(e)}")
            return json.dumps({"error": str(e)})

    def reset_usage_data(self) -> Dict[str, Any]:
        """重置token使用数据"""
        try:
            # 保存摘要
            summary = self.get_usage_summary()

            # 重置数据
            self.usage_records = []
            self.usage_by_model = {}
            self.usage_by_service = {}
            self.usage_by_day = {}
            self.start_time = time.time()

            logger.info("Token使用数据已重置")

            return {
                "message": "Token使用数据已重置",
                "previous_summary": summary
            }

        except Exception as e:
            logger.error(f"重置token使用数据失败: {str(e)}")
            return {"error": str(e)}

# 创建全局Token服务实例
token_service = TokenService()
