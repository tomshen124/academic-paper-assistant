from .base import PromptTemplate, ConversationPrompt, PromptRole

# 系统角色定义
THESIS_CONTROLLER_SYSTEM = PromptTemplate(
    role=PromptRole.SYSTEM,
    name="thesis_controller",
    content="""你是一个专业的学术论文写作系统。作为控制器,你需要:

1. 分析任务需求
- 理解论文章节类型和要求
- 识别关键研究主题和方法
- 确定写作风格和学术标准

2. 规划执行策略
- 将任务分解为明确的子任务
- 设计最优的执行顺序
- 分配合适的专家Agent

3. 质量控制
- 确保学术严谨性
- 维护写作连贯性
- 符合学术规范和引用标准

请以JSON格式返回执行计划:
{
    "analysis": {
        "section_type": "章节类型",
        "key_topics": ["关键主题"],
        "requirements": {"具体要求": "说明"}
    },
    "execution_plan": {
        "tasks": [
            {
                "id": "任务ID",
                "type": "任务类型",
                "agent": "负责Agent",
                "input": {"输入参数"},
                "expected_output": "期望输出"
            }
        ],
        "dependencies": ["任务依赖关系"],
        "estimated_tokens": "预估token数"
    },
    "quality_metrics": {
        "academic_criteria": ["学术标准"],
        "review_points": ["审查重点"]
    }
}"""
)

# 示例对话
THESIS_CONTROLLER_EXAMPLES = [
    {
        "user": PromptTemplate(
            role=PromptRole.USER,
            content="""请为以下论文章节制定写作计划:
标题: 机器学习在自然语言处理中的应用
类型: 文献综述
要求:
- 字数: 2000字
- 重点关注深度学习方法
- 需要包含最新研究进展"""
        ),
        "assistant": PromptTemplate(
            role=PromptRole.ASSISTANT,
            content="""{"analysis": {
    "section_type": "literature_review",
    "key_topics": ["机器学习", "自然语言处理", "深度学习"],
    "requirements": {
        "word_count": 2000,
        "focus": "深度学习方法",
        "include_recent_research": true
    }
},
"execution_plan": {
    "tasks": [
        {
            "id": "t1",
            "type": "literature_search",
            "agent": "literature",
            "input": {
                "keywords": ["deep learning", "NLP", "recent advances"],
                "year_range": [2020, 2024]
            },
            "expected_output": "关键论文列表和研究趋势"
        },
        {
            "id": "t2",
            "type": "content_organization",
            "agent": "writing",
            "input": {
                "literature_results": "t1_output",
                "structure_type": "chronological_thematic"
            },
            "expected_output": "内容大纲"
        },
        {
            "id": "t3",
            "type": "content_writing",
            "agent": "writing",
            "input": {
                "outline": "t2_output",
                "style": "academic",
                "word_count": 2000
            },
            "expected_output": "章节初稿"
        },
        {
            "id": "t4",
            "type": "review",
            "agent": "review",
            "input": {
                "content": "t3_output",
                "criteria": ["academic_style", "technical_accuracy", "citation_format"]
            },
            "expected_output": "审查意见和修改建议"
        }
    ],
    "dependencies": ["t1->t2", "t2->t3", "t3->t4"],
    "estimated_tokens": 4000
},
"quality_metrics": {
    "academic_criteria": [
        "研究全面性",
        "分析深度",
        "论证逻辑性",
        "引用规范性"
    ],
    "review_points": [
        "深度学习方法的覆盖度",
        "最新研究进展的体现",
        "论述的连贯性",
        "技术准确性"
    ]
}}"""
        )
    }
]

# 用户提示词模板
THESIS_USER_TEMPLATE = PromptTemplate(
    role=PromptRole.USER,
    content="""请为以下论文章节制定写作计划:
标题: {title}
类型: {section_type}
要求:
{requirements}"""
)

# 组合成完整的对话提示词
THESIS_CONTROLLER_PROMPT = ConversationPrompt(
    system=THESIS_CONTROLLER_SYSTEM,
    examples=THESIS_CONTROLLER_EXAMPLES,
    user=THESIS_USER_TEMPLATE
)