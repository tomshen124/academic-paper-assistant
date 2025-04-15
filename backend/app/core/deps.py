from typing import Generator
from redis import Redis
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal

def get_db() -> Generator[Session, None, None]:
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_redis() -> Generator[Redis, None, None]:
    """获取Redis连接"""
    redis = Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        password=settings.REDIS_PASSWORD,
        decode_responses=True
    )
    try:
        yield redis
    finally:
        redis.close() 