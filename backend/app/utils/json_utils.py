"""
JSON 工具函数，用于安全地序列化对象
"""
import json
from typing import Any, Dict, List, Union, Optional
import logging

logger = logging.getLogger(__name__)

def safe_dumps(obj: Any, ensure_ascii: bool = False, default_value: str = "null", max_length: Optional[int] = None) -> str:
    """
    安全地将对象序列化为 JSON 字符串
    
    Args:
        obj: 要序列化的对象
        ensure_ascii: 是否确保 ASCII 编码
        default_value: 序列化失败时返回的默认值
        max_length: 返回字符串的最大长度，如果为 None 则不限制
        
    Returns:
        序列化后的 JSON 字符串
    """
    try:
        # 尝试直接序列化
        result = json.dumps(obj, ensure_ascii=ensure_ascii)
        
        # 如果指定了最大长度，截断字符串
        if max_length is not None and len(result) > max_length:
            result = result[:max_length]
            
        return result
    except (TypeError, OverflowError) as e:
        # 如果是复杂对象，尝试转换为可序列化的形式
        logger.warning(f"对象序列化失败，尝试转换: {str(e)}")
        try:
            serializable_obj = _convert_to_serializable(obj)
            result = json.dumps(serializable_obj, ensure_ascii=ensure_ascii)
            
            # 如果指定了最大长度，截断字符串
            if max_length is not None and len(result) > max_length:
                result = result[:max_length]
                
            return result
        except Exception as e:
            logger.error(f"对象序列化失败: {str(e)}")
            return default_value

def _convert_to_serializable(obj: Any) -> Any:
    """
    将对象转换为可序列化的形式
    
    Args:
        obj: 要转换的对象
        
    Returns:
        可序列化的对象
    """
    if obj is None:
        return None
    elif isinstance(obj, (str, int, float, bool)):
        return obj
    elif isinstance(obj, dict):
        return {k: _convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_convert_to_serializable(item) for item in obj]
    elif isinstance(obj, tuple):
        return [_convert_to_serializable(item) for item in obj]
    elif isinstance(obj, set):
        return [_convert_to_serializable(item) for item in obj]
    elif hasattr(obj, '__dict__'):
        # 对于自定义对象，尝试转换其 __dict__
        try:
            return _convert_to_serializable(obj.__dict__)
        except:
            return str(obj)
    else:
        # 对于其他类型，转换为字符串
        return str(obj)

def safe_loads(json_str: str, default_value: Any = None) -> Any:
    """
    安全地将 JSON 字符串反序列化为对象
    
    Args:
        json_str: 要反序列化的 JSON 字符串
        default_value: 反序列化失败时返回的默认值
        
    Returns:
        反序列化后的对象
    """
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error(f"JSON 反序列化失败: {str(e)}")
        return default_value
