from typing import Dict, Any
from pydantic import BaseSettings

class LLMConfig(BaseSettings):
    """LLM配置"""
    
    # 默认模型配置
    DEFAULT_MODEL: str = "gpt-4"
    DEFAULT_TEMPERATURE: float = 0.7
    DEFAULT_MAX_TOKENS: int = 2000
    
    # 模型映射配置
    MODEL_MAPPINGS: Dict[str, str] = {
        "gpt-4": "openai/gpt-4",
        "claude-2": "anthropic/claude-2",
        "chatglm": "zhipu/chatglm-turbo",
        "qwen": "qwen/qwen-14b-chat",
        "llama2": "meta/llama2-70b-chat"
    }
    
    # 智能体配置
    AGENT_CONFIGS: Dict[str, Dict[str, Any]] = {
        "writing": {
            "model": "gpt-4",
            "temperature": 0.7,
            "system_prompt": "You are an expert academic writer..."
        },
        "review": {
            "model": "claude-2",
            "temperature": 0.3,
            "system_prompt": "You are an experienced paper reviewer..."
        },
        "literature": {
            "model": "gpt-4",
            "temperature": 0.5,
            "system_prompt": "You are a literature research expert..."
        }
    }
    
    class Config:
        env_prefix = "LLM_"