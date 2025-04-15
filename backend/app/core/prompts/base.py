from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum

class PromptRole(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

@dataclass
class PromptTemplate:
    """提示词模板基类"""
    role: PromptRole
    content: str
    name: Optional[str] = None
    
    def format(self, **kwargs) -> str:
        return self.content.format(**kwargs)

@dataclass
class ConversationPrompt:
    """对话提示词组合"""
    system: PromptTemplate
    examples: List[Dict[str, PromptTemplate]] = None
    user: PromptTemplate = None
    
    def build_messages(self, **kwargs) -> List[Dict]:
        """构建完整的对话消息列表"""
        messages = [
            {"role": self.system.role.value, "content": self.system.format(**kwargs)}
        ]
        
        # 添加示例对话
        if self.examples:
            for example in self.examples:
                for role, prompt in example.items():
                    messages.append({
                        "role": role,
                        "content": prompt.format(**kwargs)
                    })
        
        # 添加用户提示词
        if self.user:
            messages.append({
                "role": self.user.role.value,
                "content": self.user.format(**kwargs)
            })
            
        return messages