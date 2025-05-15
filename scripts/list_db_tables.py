#!/usr/bin/env python3
"""
列出数据库中的所有表
"""

import os
import sys
import logging
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
DB_NAME = os.getenv("DATABASE_NAME", "academic_paper_assistant")
DB_USER = os.getenv("DATABASE_USER", "postgres")
DB_PASSWORD = os.getenv("DATABASE_PASSWORD", "postgres123")

def list_tables():
    """列出数据库中的所有表"""
    # 连接字符串
    conn_string = f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"
    logger.info(f"连接到数据库: {DB_HOST}:{DB_PORT}/{DB_NAME}")
    
    conn = None
    try:
        # 连接到数据库
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
        
        # 查询所有表
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name")
        tables = cursor.fetchall()
        
        print("数据库中的表:")
        for table in tables:
            print(f"- {table[0]}")
            
        # 如果有表，查看第一个表的结构
        if tables:
            first_table = tables[0][0]
            print(f"\n表 '{first_table}' 的结构:")
            cursor.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{first_table}' ORDER BY ordinal_position")
            columns = cursor.fetchall()
            for column in columns:
                print(f"  - {column[0]} ({column[1]})")
        
    except Exception as e:
        logger.error(f"查询数据库时出错: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    list_tables()
