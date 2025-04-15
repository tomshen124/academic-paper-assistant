from typing import Any, Optional
from datetime import datetime, timedelta
import json
import pickle
from redis import Redis
from functools import wraps

from app.core.config import settings

class RedisCache:
    def __init__(self):
        self.redis = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True
        )
        self.binary_redis = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=False
        )

    def get(self, key: str) -> Optional[str]:
        """获取字符串缓存"""
        return self.redis.get(key)

    def set(
        self,
        key: str,
        value: str,
        expire: int = 3600  # 默认1小时过期
    ) -> None:
        """设置字符串缓存"""
        self.redis.set(key, value, ex=expire)

    def get_json(self, key: str) -> Optional[dict]:
        """获取JSON缓存"""
        data = self.get(key)
        if data:
            return json.loads(data)
        return None

    def set_json(
        self,
        key: str,
        value: dict,
        expire: int = 3600
    ) -> None:
        """设置JSON缓存"""
        self.set(key, json.dumps(value), expire)

    def get_object(self, key: str) -> Optional[Any]:
        """获取Python对象缓存"""
        data = self.binary_redis.get(key)
        if data:
            return pickle.loads(data)
        return None

    def set_object(
        self,
        key: str,
        value: Any,
        expire: int = 3600
    ) -> None:
        """设置Python对象缓存"""
        self.binary_redis.set(key, pickle.dumps(value), ex=expire)

    def delete(self, key: str) -> None:
        """删除缓存"""
        self.redis.delete(key)
        self.binary_redis.delete(key)

    def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        return self.redis.exists(key)

# 创建全局缓存实例
cache = RedisCache()

def cached(
    prefix: str,
    expire: int = 3600,
    json_data: bool = True,
    key_builder: Optional[callable] = None
):
    """缓存装饰器
    
    Args:
        prefix: 缓存键前缀
        expire: 过期时间（秒）
        json_data: 是否为JSON数据
        key_builder: 自定义缓存键生成函数
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            if key_builder:
                cache_key = f"{prefix}:{key_builder(*args, **kwargs)}"
            else:
                # 对于静态方法，args[0]是db参数
                key_parts = []
                if len(args) > 1:  # 如果有额外参数
                    key_parts.extend(str(arg) for arg in args[1:])
                if kwargs:
                    key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                
                cache_key = prefix
                if key_parts:
                    cache_key = f"{prefix}:{':'.join(key_parts)}"

            # 尝试获取缓存
            if json_data:
                cached_data = cache.get_json(cache_key)
            else:
                cached_data = cache.get_object(cache_key)

            if cached_data is not None:
                return cached_data

            # 执行原函数
            result = func(*args, **kwargs)

            # 设置缓存
            try:
                if json_data:
                    if isinstance(result, (list, dict)):
                        cache.set_json(cache_key, result, expire)
                else:
                    cache.set_object(cache_key, result, expire)
            except Exception as e:
                print(f"Cache error: {str(e)}")

            return result
        return wrapper
    return decorator 