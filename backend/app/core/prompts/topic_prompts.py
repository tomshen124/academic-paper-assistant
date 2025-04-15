"""
主题相关提示词
包含主题推荐、分析和优化的提示词模板
"""

# 主题推荐提示词
TOPIC_RECOMMENDATION_PROMPT = """请根据以下信息，推荐适合的学术论文主题：

用户兴趣: {user_interests}
学术领域: {academic_field}
学术水平: {academic_level}

请推荐5个具体的、有研究价值的论文主题。每个主题应包含：
1. 主题标题
2. 研究问题
3. 研究价值
4. 可行性分析
5. 相关研究方向

请以JSON格式返回：
{
    "topics": [
        {
            "title": "主题标题",
            "research_question": "核心研究问题",
            "value": "研究价值和意义",
            "feasibility": "可行性分析",
            "related_areas": ["相关研究方向1", "相关研究方向2"]
        }
    ]
}
"""

# 主题可行性分析提示词
TOPIC_FEASIBILITY_PROMPT = """请分析以下学术论文主题的可行性：

主题: {topic}
学术领域: {academic_field}
学术水平: {academic_level}

请从以下几个方面进行详细分析：
1. 研究价值：该主题的学术价值和实际应用价值
2. 创新性：与现有研究的区别和创新点
3. 资源需求：完成该研究所需的时间、数据、设备等资源
4. 技术难度：研究过程中可能遇到的技术挑战
5. 研究方法：适合该主题的研究方法
6. 潜在风险：研究过程中可能遇到的问题和风险
7. 建议改进：如何调整主题以提高可行性

请以JSON格式返回：
{
    "value_score": 0-10,
    "value_analysis": "研究价值分析",
    "innovation_score": 0-10,
    "innovation_analysis": "创新性分析",
    "resource_score": 0-10,
    "resource_analysis": "资源需求分析",
    "difficulty_score": 0-10,
    "difficulty_analysis": "技术难度分析",
    "methods": ["适用的研究方法1", "适用的研究方法2"],
    "risks": ["潜在风险1", "潜在风险2"],
    "suggestions": ["改进建议1", "改进建议2"],
    "overall_score": 0-10,
    "overall_assessment": "总体评估"
}
"""

# 主题优化提示词
TOPIC_REFINEMENT_PROMPT = """请根据以下信息，优化学术论文主题：

原主题: {topic}
用户反馈: {feedback}
学术领域: {academic_field}
学术水平: {academic_level}

请提供3个优化后的主题方案，每个方案应包含：
1. 优化后的主题标题
2. 优化的核心研究问题
3. 优化点说明
4. 预期改进效果

请以JSON格式返回：
{
    "refined_topics": [
        {
            "title": "优化后的主题标题",
            "research_question": "优化后的研究问题",
            "improvements": ["优化点1", "优化点2"],
            "expected_benefits": ["预期效果1", "预期效果2"]
        }
    ],
    "analysis": "优化思路分析"
}
"""
