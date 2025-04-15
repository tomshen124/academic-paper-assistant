"""
提示词配置文件 (兼容层)
为了保持向后兼容性，从新的模块化提示词导入所有提示词
"""

# 从新的模块化提示词导入所有提示词
from app.core.prompts.topic_prompts import *
from app.core.prompts.outline_prompts import *
from app.core.prompts.paper_prompts import *
from app.core.prompts.citation_prompts import *
from app.core.prompts.search_prompts import *
from app.core.prompts.agent_prompts import *

# 警告信息
import warnings
warnings.warn(
    "直接导入 app.core.prompts 已弃用，请使用 app.core.prompts.* 模块",
    DeprecationWarning,
    stacklevel=2
)
