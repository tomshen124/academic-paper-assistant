from sqlalchemy.orm import Session
from app.core.logger import get_logger
from app.db.base import Base
from app.db.session import engine
from app.models.user import User
from app.core.security import get_password_hash

logger = get_logger("db_init")

# 创建初始超级用户
FIRST_SUPERUSER = "admin"
FIRST_SUPERUSER_EMAIL = "admin@example.com"
FIRST_SUPERUSER_PASSWORD = "admin123"

def init_db(db: Session) -> None:
    """初始化数据库"""
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    # 创建初始超级用户
    create_first_superuser(db)

def create_first_superuser(db: Session) -> None:
    """创建初始超级用户"""
    # 检查是否已存在超级用户
    user = db.query(User).filter(User.email == FIRST_SUPERUSER_EMAIL).first()
    if not user:
        user = User(
            email=FIRST_SUPERUSER_EMAIL,
            username=FIRST_SUPERUSER,
            hashed_password=get_password_hash(FIRST_SUPERUSER_PASSWORD),
            is_superuser=True,
            is_active=True
        )
        db.add(user)
        db.commit()
        logger.info(f"创建初始超级用户: {FIRST_SUPERUSER}")
    else:
        logger.info(f"超级用户已存在: {FIRST_SUPERUSER}")
