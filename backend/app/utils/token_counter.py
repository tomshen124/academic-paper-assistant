import tiktoken
from typing import List, Dict, Any, Optional, Union
from app.core.logger import get_logger

# 创建日志器
logger = get_logger("token_counter")

class TokenCounter:
    """Token计数器，用于估算LLM的token使用量"""
    
    def __init__(self):
        """初始化Token计数器"""
        # 加载编码器
        try:
            self.encoders = {
                "gpt-3.5-turbo": tiktoken.encoding_for_model("gpt-3.5-turbo"),
                "gpt-4": tiktoken.encoding_for_model("gpt-4"),
                "claude-3": tiktoken.get_encoding("cl100k_base"),  # Claude使用类似的编码
                "default": tiktoken.get_encoding("cl100k_base")
            }
            logger.info("Token计数器初始化成功")
        except Exception as e:
            logger.error(f"Token计数器初始化失败: {str(e)}")
            self.encoders = {}
    
    def count_tokens(self, text: str, model: str = "default") -> int:
        """计算文本的token数量"""
        try:
            # 获取编码器
            encoder = self.encoders.get(model, self.encoders.get("default"))
            if not encoder:
                logger.warning(f"未找到模型 {model} 的编码器，使用估算方法")
                # 如果没有编码器，使用简单估算（每4个字符约1个token）
                return len(text) // 4
            
            # 计算token
            tokens = encoder.encode(text)
            return len(tokens)
        except Exception as e:
            logger.error(f"计算token失败: {str(e)}")
            # 出错时使用简单估算
            return len(text) // 4
    
    def count_message_tokens(self, messages: List[Dict[str, str]], model: str = "default") -> int:
        """计算消息列表的token数量"""
        try:
            total_tokens = 0
            
            # 遍历消息
            for message in messages:
                # 计算角色的token
                role = message.get("role", "user")
                role_tokens = self.count_tokens(role, model)
                
                # 计算内容的token
                content = message.get("content", "")
                content_tokens = self.count_tokens(content, model)
                
                # 每条消息有固定开销
                message_overhead = 4  # 这是一个估计值，不同模型可能不同
                
                # 累加token
                total_tokens += role_tokens + content_tokens + message_overhead
            
            # 整个请求有固定开销
            request_overhead = 3  # 这是一个估计值，不同模型可能不同
            total_tokens += request_overhead
            
            return total_tokens
        except Exception as e:
            logger.error(f"计算消息token失败: {str(e)}")
            # 出错时使用简单估算
            return sum(len(m.get("content", "")) for m in messages) // 4
    
    def estimate_completion_tokens(self, prompt_tokens: int, model: str = "default") -> int:
        """估算补全的token数量"""
        # 这是一个粗略的估计，实际情况取决于模型和内容
        if "gpt-4" in model:
            # GPT-4通常生成更长的回复
            return prompt_tokens * 1.5
        else:
            # 其他模型
            return prompt_tokens
    
    def estimate_cost(self, prompt_tokens: int, completion_tokens: int, model: str = "default") -> float:
        """估算成本（美元）"""
        # 价格可能会变化，这里只是一个估计
        prices = {
            "gpt-3.5-turbo": {"prompt": 0.0015, "completion": 0.002},  # 每1000个token的价格
            "gpt-4": {"prompt": 0.03, "completion": 0.06},
            "claude-3": {"prompt": 0.01, "completion": 0.03},
            "default": {"prompt": 0.01, "completion": 0.02}
        }
        
        # 获取价格
        price = prices.get(model, prices["default"])
        
        # 计算成本
        prompt_cost = (prompt_tokens / 1000) * price["prompt"]
        completion_cost = (completion_tokens / 1000) * price["completion"]
        
        return prompt_cost + completion_cost
    
    def get_token_limit(self, model: str = "default") -> int:
        """获取模型的token限制"""
        limits = {
            "gpt-3.5-turbo": 4096,
            "gpt-3.5-turbo-16k": 16384,
            "gpt-4": 8192,
            "gpt-4-32k": 32768,
            "claude-3-opus": 200000,
            "claude-3-sonnet": 100000,
            "claude-3-haiku": 50000,
            "default": 4096
        }
        
        return limits.get(model, limits["default"])

# 创建全局Token计数器实例
token_counter = TokenCounter()
