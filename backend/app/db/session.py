from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.config.get("database", {}).get("pool_size", 20),
    max_overflow=settings.config.get("database", {}).get("max_overflow", 10),
    pool_timeout=settings.config.get("database", {}).get("pool_timeout", 30),
    pool_recycle=settings.config.get("database", {}).get("pool_recycle", 1800)
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()