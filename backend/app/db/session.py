from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.config["database"]["pool_size"],
    max_overflow=settings.config["database"]["max_overflow"],
    pool_timeout=settings.config["database"]["pool_timeout"],
    pool_recycle=settings.config["database"]["pool_recycle"]
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