"""
重置管理员密码脚本
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash
from app.core.logger import get_logger

logger = get_logger("password_reset")

# 超级用户信息
ADMIN_USERNAME = "admin"
NEW_PASSWORD = "admin123"  # 新密码

def reset_admin_password():
    """重置管理员密码"""
    db = SessionLocal()
    try:
        # 查找管理员用户
        admin = db.query(User).filter(User.username == ADMIN_USERNAME).first()
        
        if not admin:
            logger.error(f"未找到用户名为 {ADMIN_USERNAME} 的用户")
            return
        
        # 更新密码
        admin.hashed_password = get_password_hash(NEW_PASSWORD)
        db.commit()
        
        logger.info(f"已成功重置用户 {ADMIN_USERNAME} 的密码")
        print(f"已成功重置用户 {ADMIN_USERNAME} 的密码为: {NEW_PASSWORD}")
    except Exception as e:
        logger.error(f"重置密码时发生错误: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_admin_password()
