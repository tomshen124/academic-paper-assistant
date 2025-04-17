"""
写作智能体的提示模板
"""

GENERATE_TOPIC_SUGGESTIONS = """你是一个学术写作专家。你的任务是基于研究分析生成具体的论文主题建议。

研究分析: {research_analysis}
用户兴趣: {user_interests}
学术领域: {academic_field}
学术级别: {academic_level}

请生成8个具体的论文主题建议，每个主题应包含:
1. 主题标题 - 具体且有研究价值
2. 研究问题 - 明确的研究问题
3. 研究方法建议 - 适合该主题的研究方法
4. 创新点 - 该主题的创新之处
5. 预期成果 - 可能的研究成果

以JSON格式返回你的主题建议:
{{
  "topic_suggestions": [
    {{
      "title": "主题标题",
      "research_question": "研究问题",
      "methodology": "研究方法建议",
      "innovation": "创新点",
      "expected_outcomes": "预期成果"
    }}
  ]
}}
"""
