"""
提纲相关提示词
包含提纲生成和优化的提示词模板
"""

# 提纲生成提示词
OUTLINE_GENERATION_PROMPT = """请根据以下信息，生成一个详细的学术论文提纲：

论文主题: {topic}
论文类型: {paper_type}
学术领域: {academic_field}
学术水平: {academic_level}
论文长度: {length}

请生成一个结构完整、逻辑清晰的学术论文提纲，包括：
1. 标题
2. 摘要结构
3. 关键词建议
4. 章节结构（包括引言、文献综述、方法、结果、讨论、结论等）
5. 每个章节的子部分
6. 每个部分的主要内容和要点

请以JSON格式返回：
{
    "title": "论文标题",
    "abstract_structure": ["摘要要点1", "摘要要点2"],
    "keywords": ["关键词1", "关键词2"],
    "sections": [
        {
            "id": "1",
            "title": "章节标题",
            "content": "章节主要内容描述",
            "subsections": [
                {
                    "id": "1.1",
                    "title": "子章节标题",
                    "content": "子章节主要内容描述"
                }
            ]
        }
    ],
    "references_suggestion": "参考文献建议"
}
"""

# 提纲优化提示词
OUTLINE_OPTIMIZATION_PROMPT = """请根据以下信息，优化学术论文提纲：

原提纲:
{outline}

用户反馈:
{feedback}

请优化提纲，使其更加完善、逻辑更加清晰。优化应包括：
1. 结构调整建议
2. 内容补充建议
3. 逻辑优化建议
4. 表达改进建议

请以与原提纲相同的JSON格式返回优化后的完整提纲，并添加一个"optimization_notes"字段说明优化内容。
"""

# 提纲验证提示词
OUTLINE_VALIDATION_PROMPT = """请验证以下学术论文提纲的逻辑结构：

提纲:
{outline}

请从以下几个方面验证提纲的逻辑结构：
1. 结构完整性：是否包含所有必要的章节
2. 逻辑连贯性：各章节之间的逻辑关系是否清晰
3. 内容平衡性：各章节内容是否平衡
4. 研究问题覆盖度：是否充分覆盖研究问题
5. 方法论适当性：研究方法是否适合研究问题

请以JSON格式返回：
{
    "structure_completeness": {
        "score": 0-10,
        "issues": ["问题1", "问题2"],
        "suggestions": ["建议1", "建议2"]
    },
    "logical_coherence": {
        "score": 0-10,
        "issues": ["问题1", "问题2"],
        "suggestions": ["建议1", "建议2"]
    },
    "content_balance": {
        "score": 0-10,
        "issues": ["问题1", "问题2"],
        "suggestions": ["建议1", "建议2"]
    },
    "research_question_coverage": {
        "score": 0-10,
        "issues": ["问题1", "问题2"],
        "suggestions": ["建议1", "建议2"]
    },
    "methodology_appropriateness": {
        "score": 0-10,
        "issues": ["问题1", "问题2"],
        "suggestions": ["建议1", "建议2"]
    },
    "overall_assessment": "总体评估",
    "overall_score": 0-10
}
"""
