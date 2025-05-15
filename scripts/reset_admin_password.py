#!/usr/bin/env python3
"""
重置管理员密码的脚本
"""

import sys
import os
import logging
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 创建数据库连接
SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 导入用户模型和安全函数
sys.path.append("/edu-kg/backend")
from app.models.user import User
from app.core.security import get_password_hash

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def reset_admin_password(new_password: str = "admin123"):
    """重置管理员密码"""
    # 确保数据库表存在
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # 查找管理员用户
        admin = db.query(User).filter(User.username == "admin").first()

        if not admin:
            logger.error("管理员用户不存在，创建新管理员用户")
            admin = User(
                username="admin",
                email="admin@example.com",
                is_active=True,
                is_superuser=True,
                hashed_password=get_password_hash(new_password)
            )
            db.add(admin)
        else:
            logger.info(f"找到管理员用户: {admin.username}, ID: {admin.id}")
            # 更新密码
            admin.hashed_password = get_password_hash(new_password)

        db.commit()
        logger.info(f"管理员密码已重置为: {new_password}")

        # 验证更新
        admin = db.query(User).filter(User.username == "admin").first()
        logger.info(f"管理员密码哈希: {admin.hashed_password[:20]}...")

    except Exception as e:
        logger.error(f"重置密码时出错: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    # 如果提供了命令行参数，使用它作为新密码
    if len(sys.argv) > 1:
        new_password = sys.argv[1]
        reset_admin_password(new_password)
    else:
        # 否则使用默认密码
        reset_admin_password()
