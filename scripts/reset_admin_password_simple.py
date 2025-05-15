#!/usr/bin/env python3
"""
重置管理员密码的简单脚本，直接使用SQL
"""

import sqlite3
import bcrypt
import logging
import os
from pathlib import Path

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 数据库路径
DB_PATH = Path("/edu-kg/backend/app.db")

def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    # 将密码编码为字节
    password_bytes = password.encode('utf-8')
    # 生成盐值
    salt = bcrypt.gensalt()
    # 哈希密码
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    # 将哈希结果转换为字符串
    return hashed_bytes.decode('utf-8')

def reset_admin_password(new_password: str = "admin123"):
    """重置管理员密码"""
    if not DB_PATH.exists():
        logger.error(f"数据库文件不存在: {DB_PATH}")
        return
    
    # 生成新的密码哈希
    hashed_password = get_password_hash(new_password)
    logger.info(f"生成的密码哈希: {hashed_password[:20]}...")
    
    try:
        # 连接到数据库
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        # 检查用户表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user'")
        if not cursor.fetchone():
            logger.error("用户表不存在")
            return
        
        # 检查管理员用户是否存在
        cursor.execute("SELECT id, username FROM user WHERE username = 'admin'")
        admin = cursor.fetchone()
        
        if not admin:
            logger.info("管理员用户不存在，创建新管理员用户")
            cursor.execute(
                "INSERT INTO user (username, email, hashed_password, is_active, is_superuser) VALUES (?, ?, ?, ?, ?)",
                ("admin", "admin@example.com", hashed_password, 1, 1)
            )
        else:
            logger.info(f"找到管理员用户: {admin[1]}, ID: {admin[0]}")
            # 更新密码
            cursor.execute(
                "UPDATE user SET hashed_password = ? WHERE username = 'admin'",
                (hashed_password,)
            )
        
        # 提交更改
        conn.commit()
        logger.info(f"管理员密码已重置为: {new_password}")
        
        # 验证更新
        cursor.execute("SELECT hashed_password FROM user WHERE username = 'admin'")
        updated_hash = cursor.fetchone()[0]
        logger.info(f"更新后的密码哈希: {updated_hash[:20]}...")
        
    except Exception as e:
        logger.error(f"重置密码时出错: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    import sys
    
    # 如果提供了命令行参数，使用它作为新密码
    if len(sys.argv) > 1:
        new_password = sys.argv[1]
        reset_admin_password(new_password)
    else:
        # 否则使用默认密码
        reset_admin_password()
