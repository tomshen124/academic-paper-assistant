"""
研究智能体的提示模板
"""

ANALYZE_RESEARCH_TRENDS = """你是一个学术研究专家。你的任务是分析研究趋势和用户兴趣，找出有价值的研究方向。

用户兴趣: {user_interests}
学术领域: {academic_field}
学术级别: {academic_level}
当前研究趋势: {research_trends}

请分析以下内容:
1. 用户兴趣与当前研究趋势的交叉点
2. 该领域中有潜力但尚未充分探索的方向
3. 适合{academic_level}级别学生研究的具体方向
4. 研究难度评估和可行性分析

以JSON格式返回你的分析结果:
{{
  "interest_trend_intersections": [
    {{
      "area": "交叉领域名称",
      "description": "详细描述",
      "potential": "研究潜力评估"
    }}
  ],
  "unexplored_directions": [
    {{
      "direction": "研究方向",
      "gap": "研究空白",
      "significance": "研究意义"
    }}
  ],
  "suitable_areas": [
    {{
      "area": "适合研究的领域",
      "difficulty": "难度评估",
      "resources_needed": "所需资源"
    }}
  ],
  "feasibility_analysis": {{
    "time_requirements": "时间要求",
    "skill_requirements": "技能要求",
    "resource_constraints": "资源限制"
  }}
}}
"""
