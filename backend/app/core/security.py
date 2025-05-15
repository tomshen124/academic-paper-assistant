from datetime import datetime, timedelta, timezone
from typing import Any, Union, Optional
from jose import jwt
import bcrypt
from app.core.config import settings
import os
import logging

# 设置日志记录器
logger = logging.getLogger(__name__)

# 直接使用bcrypt库，避免passlib的兼容性问题

# JWT相关配置
SECRET_KEY = os.environ.get("SECRET_KEY", "your_secret_key_here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """创建访问令牌"""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    try:
        # 将明文密码编码为字节
        password_bytes = plain_password.encode('utf-8')
        # 将哈希密码编码为字节
        hashed_bytes = hashed_password.encode('utf-8')

        logger.info(f"验证密码: 哈希密码长度={len(hashed_bytes)}, 格式={hashed_bytes[:7]}")

        # 使用bcrypt验证密码
        result = bcrypt.checkpw(password_bytes, hashed_bytes)
        logger.info(f"密码验证结果: {result}")
        return result
    except Exception as e:
        logger.error(f"密码验证错误: {str(e)}")
        logger.error(f"密码验证详细信息: 明文密码长度={len(plain_password)}, 哈希密码长度={len(hashed_password)}")

        # 尝试使用另一种方式验证
        try:
            # 有时哈希密码可能已经是字节类型
            if isinstance(hashed_password, bytes):
                hashed_bytes = hashed_password

            result = bcrypt.checkpw(password_bytes, hashed_bytes)
            logger.info(f"第二次尝试密码验证结果: {result}")
            return result
        except Exception as e2:
            logger.error(f"第二次尝试密码验证错误: {str(e2)}")
            # 如果出现任何错误，返回False
            return False

def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    try:
        # 将密码编码为字节
        password_bytes = password.encode('utf-8')
        # 生成盐值
        salt = bcrypt.gensalt()
        # 哈希密码
        hashed_bytes = bcrypt.hashpw(password_bytes, salt)
        # 将哈希结果转换为字符串
        hashed_str = hashed_bytes.decode('utf-8')

        logger.debug(f"生成密码哈希: 长度={len(hashed_str)}, 格式={hashed_str[:10]}...")

        return hashed_str
    except Exception as e:
        logger.error(f"生成密码哈希错误: {e}", exc_info=True)
        raise

def decode_access_token(token: str) -> dict:
    """解码访问令牌"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.JWTError:
        return {}
