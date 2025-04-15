from typing import Dict, Union
import tiktoken

# 模型价格配置(每1k tokens的价格)
MODEL_PRICES = {
    "gpt-4": {"prompt": 0.03, "completion": 0.06},
    "gpt-3.5-turbo": {"prompt": 0.0015, "completion": 0.002},
    "claude-2": {"prompt": 0.008, "completion": 0.024},
}

def count_tokens(text: str, model: str = "gpt-4") -> int:
    """计算文本的token数量"""
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except Exception:
        # 如果无法获取特定模型的编码,使用默认编码
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))

def estimate_cost(
    tokens: Union[int, Dict[str, int]], 
    model: str = "gpt-4"
) -> float:
    """估算token使用成本"""
    if isinstance(tokens, int):
        # 如果只提供总token数,假设按3:1的比例分配prompt和completion
        prompt_tokens = tokens * 0.75
        completion_tokens = tokens * 0.25
    else:
        prompt_tokens = tokens.get("prompt_tokens", 0)
        completion_tokens = tokens.get("completion_tokens", 0)
    
    prices = MODEL_PRICES.get(model, MODEL_PRICES["gpt-4"])
    
    cost = (
        (prompt_tokens * prices["prompt"] / 1000) +
        (completion_tokens * prices["completion"] / 1000)
    )
    
    return round(cost, 6)