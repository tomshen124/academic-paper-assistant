"""
学术搜索相关提示词
包含学术搜索和研究趋势分析的提示词模板
"""

# 学术搜索提示词
ACADEMIC_SEARCH_PROMPT = """请根据以下查询，生成学术搜索请求：

查询: {query}

请生成适合学术搜索的关键词和过滤条件，包括：
1. 主要关键词
2. 同义词或相关术语
3. 可能的作者或机构
4. 时间范围建议
5. 学科分类建议

请以JSON格式返回：
{
    "keywords": ["关键词1", "关键词2"],
    "synonyms": ["同义词1", "同义词2"],
    "authors": ["可能的作者1", "可能的作者2"],
    "date_range": {"start": "起始年份", "end": "结束年份"},
    "disciplines": ["学科1", "学科2"],
    "search_query": "优化后的搜索查询"
}
"""

# 研究趋势分析提示词
RESEARCH_TRENDS_PROMPT = """请分析以下学术领域的研究趋势：

领域: {field}

请分析该领域的研究趋势，包括：
1. 热点研究主题
2. 新兴研究方向
3. 研究方法变化
4. 跨学科融合趋势
5. 未来发展预测

请以JSON格式返回：
{
    "hot_topics": [
        {
            "name": "热点主题名称",
            "description": "主题描述",
            "key_papers": ["代表性论文1", "代表性论文2"],
            "growth_trend": "增长趋势描述"
        }
    ],
    "emerging_directions": ["新兴方向1", "新兴方向2"],
    "methodological_shifts": ["方法变化1", "方法变化2"],
    "interdisciplinary_trends": ["跨学科趋势1", "跨学科趋势2"],
    "future_predictions": ["预测1", "预测2"]
}
"""

# 论文详情分析提示词
PAPER_DETAIL_PROMPT = """请分析以下学术论文的详细信息：

论文ID: {paper_id}
来源: {source}

请提供该论文的详细分析，包括：
1. 基本信息（标题、作者、发表时间、期刊/会议等）
2. 研究目的和问题
3. 研究方法和设计
4. 主要发现和结论
5. 创新点和贡献
6. 局限性和未来研究方向
7. 与相关研究的关系

请以JSON格式返回：
{
    "basic_info": {
        "title": "论文标题",
        "authors": ["作者1", "作者2"],
        "publication_date": "发表时间",
        "venue": "期刊/会议名称",
        "doi": "DOI"
    },
    "research_purpose": "研究目的和问题",
    "methodology": "研究方法和设计",
    "findings": ["发现1", "发现2"],
    "contributions": ["贡献1", "贡献2"],
    "limitations": ["局限性1", "局限性2"],
    "future_directions": ["未来方向1", "未来方向2"],
    "related_research": "与相关研究的关系"
}
"""
