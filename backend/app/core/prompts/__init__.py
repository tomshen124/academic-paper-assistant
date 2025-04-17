"""
提示词模块
导出所有提示词模板，保持向后兼容性
"""

# 导入所有提示词
from .topic_prompts import *
from .outline_prompts import *
from .paper_prompts import *
from .citation_prompts import *
from .search_prompts import *
from .agent_prompts import *
from .research_agent_prompts import *
from .writing_agent_prompts import *
from .editing_agent_prompts import *

# 为了向后兼容，可以在这里添加一些别名
# 例如，如果之前有代码使用了旧的提示词名称，可以在这里添加别名

__all__ = [
    # 主题相关提示词
    'TOPIC_RECOMMENDATION_PROMPT',
    'TOPIC_FEASIBILITY_PROMPT',
    'TOPIC_REFINEMENT_PROMPT',

    # 提纲相关提示词
    'OUTLINE_GENERATION_PROMPT',
    'OUTLINE_OPTIMIZATION_PROMPT',
    'OUTLINE_VALIDATION_PROMPT',

    # 论文生成相关提示词
    'PAPER_SECTION_GENERATION_PROMPT',
    'SECTION_IMPROVEMENT_PROMPT',
    'FULL_PAPER_GENERATION_PROMPT',

    # 引用相关提示词
    'CITATION_FORMATTING_PROMPT',
    'CITATION_EXTRACTION_PROMPT',
    'BIBLIOGRAPHY_GENERATION_PROMPT',

    # 学术搜索相关提示词
    'ACADEMIC_SEARCH_PROMPT',
    'RESEARCH_TRENDS_PROMPT',
    'PAPER_DETAIL_PROMPT',

    # 智能体系统提示词
    'RESEARCH_AGENT_SYSTEM_PROMPT',
    'WRITING_AGENT_SYSTEM_PROMPT',
    'EDITING_AGENT_SYSTEM_PROMPT',
    'WORKFLOW_PLANNING_PROMPT',
    'TASK_EXECUTION_PROMPT',

    # 智能体任务提示词
    'ANALYZE_RESEARCH_TRENDS',
    'GENERATE_TOPIC_SUGGESTIONS',
    'REFINE_TOPICS'
]
