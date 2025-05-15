from typing import Any, Dict, Optional, Callable, Awaitable
import json
import hashlib
import time
import asyncio
from functools import wraps
from app.core.logger import get_logger

logger = get_logger("cache")

class CacheService:
    """简单的内存缓存服务"""

    def __init__(self, default_ttl: int = 3600):
        """
        初始化缓存服务

        Args:
            default_ttl: 默认缓存过期时间（秒）
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
        logger.info(f"缓存服务初始化完成，默认TTL: {default_ttl}秒")

    def _generate_key(self, prefix: str, args: tuple, kwargs: dict) -> str:
        """生成缓存键"""
        # 将参数转换为字符串，跳过不可序列化的对象
        try:
            # 处理args，跳过第一个参数（通常是self）
            if len(args) > 0:
                serializable_args = args[1:] if len(args) > 1 else ()
            else:
                serializable_args = ()

            # 尝试序列化
            args_str = json.dumps(serializable_args, sort_keys=True)
        except TypeError:
            # 如果序列化失败，使用参数的字符串表示
            args_str = str(hash(str(serializable_args)))
            logger.warning(f"无法序列化args参数，使用哈希值: {args_str}")

        try:
            # 处理kwargs
            serializable_kwargs = {k: v for k, v in kwargs.items() if self._is_serializable(v)}
            kwargs_str = json.dumps(serializable_kwargs, sort_keys=True)
        except TypeError:
            # 如果序列化失败，使用参数的字符串表示
            kwargs_str = str(hash(str(kwargs)))
            logger.warning(f"无法序列化kwargs参数，使用哈希值: {kwargs_str}")

        # 生成哈希
        key = f"{prefix}:{args_str}:{kwargs_str}"
        hashed_key = hashlib.md5(key.encode()).hexdigest()
        return hashed_key

    def _is_serializable(self, obj: Any) -> bool:
        """检查对象是否可序列化为JSON"""
        try:
            json.dumps(obj)
            return True
        except (TypeError, OverflowError):
            return False

    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if key not in self.cache:
            return None

        cache_item = self.cache[key]
        # 检查是否过期
        if cache_item["expires_at"] < time.time():
            # 过期，删除缓存
            del self.cache[key]
            return None

        logger.debug(f"缓存命中: {key}")
        return cache_item["value"]

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """设置缓存值"""
        if ttl is None:
            ttl = self.default_ttl

        expires_at = time.time() + ttl
        self.cache[key] = {
            "value": value,
            "expires_at": expires_at
        }
        logger.debug(f"缓存设置: {key}, TTL: {ttl}秒")

    async def delete(self, key: str) -> None:
        """删除缓存值"""
        if key in self.cache:
            del self.cache[key]
            logger.debug(f"缓存删除: {key}")

    async def clear(self) -> None:
        """清空缓存"""
        self.cache.clear()
        logger.info("缓存已清空")

    def cached(self, prefix: str, ttl: Optional[int] = None):
        """
        缓存装饰器，用于缓存异步函数的结果

        Args:
            prefix: 缓存键前缀
            ttl: 缓存过期时间（秒）
        """
        def decorator(func: Callable[..., Awaitable[Any]]):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    # 生成缓存键
                    cache_key = self._generate_key(prefix, args, kwargs)

                    # 尝试从缓存获取
                    cached_value = await self.get(cache_key)
                    if cached_value is not None:
                        logger.debug(f"缓存命中: {func.__name__}")
                        return cached_value

                    # 执行原函数
                    result = await func(*args, **kwargs)

                    # 检查结果是否可序列化
                    if self._is_serializable(result):
                        # 缓存结果
                        await self.set(cache_key, result, ttl)
                        logger.debug(f"缓存设置: {func.__name__}")
                    else:
                        logger.warning(f"函数 {func.__name__} 的结果不可序列化，跳过缓存")

                    return result
                except Exception as e:
                    # 如果缓存过程中出现任何错误，记录日志并继续执行原函数
                    logger.error(f"缓存过程出错: {str(e)}")
                    return await func(*args, **kwargs)
            return wrapper
        return decorator

# 创建全局缓存服务实例
cache_service = CacheService()
