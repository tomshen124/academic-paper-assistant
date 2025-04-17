"""
上下文管理模块，用于在请求处理过程中存储和获取上下文信息
"""
import contextvars
from typing import Optional, Any

# 创建上下文变量
current_user_id = contextvars.ContextVar('current_user_id', default=None)

def set_current_user_id(user_id: int) -> None:
    """设置当前用户ID"""
    current_user_id.set(user_id)

def get_current_user_id() -> Optional[int]:
    """获取当前用户ID"""
    return current_user_id.get()

def reset_current_user_id() -> None:
    """重置当前用户ID"""
    current_user_id.set(None)
