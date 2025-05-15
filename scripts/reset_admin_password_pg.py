#!/usr/bin/env python3
"""
重置管理员密码的脚本，支持PostgreSQL数据库
"""

import os
import sys
import logging
import bcrypt
import psycopg2
from pathlib import Path
from dotenv import load_dotenv

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 加载环境变量
env_path = Path("/edu-kg/config/.env")
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    logger.info(f"已加载环境变量: {env_path}")
else:
    logger.warning(f"环境变量文件不存在: {env_path}")

# 数据库连接信息
DB_HOST = os.getenv("DATABASE_HOST", "localhost")
DB_PORT = os.getenv("DATABASE_PORT", "5432")
DB_NAME = os.getenv("DATABASE_NAME", "edukg")
DB_USER = os.getenv("DATABASE_USER", "postgres")
DB_PASSWORD = os.getenv("DATABASE_PASSWORD", "postgres")

def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    # 将密码编码为字节
    password_bytes = password.encode('utf-8')
    # 生成盐值
    salt = bcrypt.gensalt()
    # 哈希密码
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    # 将哈希结果转换为字符串
    hashed_str = hashed_bytes.decode('utf-8')
    logger.debug(f"生成密码哈希: {hashed_str[:20]}...")
    return hashed_str

def reset_admin_password(new_password: str = "admin123"):
    """重置管理员密码"""
    # 生成新的密码哈希
    hashed_password = get_password_hash(new_password)
    logger.info(f"生成的密码哈希: {hashed_password[:20]}...")

    # 连接字符串
    conn_string = f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"
    logger.info(f"连接到数据库: {DB_HOST}:{DB_PORT}/{DB_NAME}")

    conn = None
    try:
        # 连接到数据库
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()

        # 检查用户表是否存在
        cursor.execute("SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'users')")
        if not cursor.fetchone()[0]:
            logger.error("用户表不存在")
            return

        # 检查管理员用户是否存在
        cursor.execute("SELECT id, username FROM users WHERE username = 'admin'")
        admin = cursor.fetchone()

        if not admin:
            logger.info("管理员用户不存在，创建新管理员用户")
            cursor.execute(
                "INSERT INTO users (username, email, hashed_password, is_active, is_superuser) VALUES (%s, %s, %s, %s, %s)",
                ("admin", "admin@example.com", hashed_password, True, True)
            )
        else:
            logger.info(f"找到管理员用户: {admin[1]}, ID: {admin[0]}")
            # 更新密码
            cursor.execute(
                "UPDATE users SET hashed_password = %s WHERE username = 'admin'",
                (hashed_password,)
            )

        # 提交更改
        conn.commit()
        logger.info(f"管理员密码已重置为: {new_password}")

        # 验证更新
        cursor.execute("SELECT hashed_password FROM users WHERE username = 'admin'")
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
    # 如果提供了命令行参数，使用它作为新密码
    if len(sys.argv) > 1:
        new_password = sys.argv[1]
        reset_admin_password(new_password)
    else:
        # 否则使用默认密码
        reset_admin_password()
