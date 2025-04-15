"""
引用相关提示词
包含引用格式化、提取和参考文献生成的提示词模板
"""

# 引用格式化提示词
CITATION_FORMATTING_PROMPT = """请根据以下信息，格式化学术引用：

文本内容:
{content}

文献信息:
{literature}

引用样式: {style}

请完成以下任务：
1. 识别文本中的引用标记
2. 根据提供的文献信息，将引用标记格式化为指定的引用样式
3. 生成规范的参考文献列表

请以JSON格式返回：
{
    "formatted_content": "格式化后的内容",
    "bibliography": ["参考文献1", "参考文献2"],
    "citations_count": 引用数量
}
"""

# 引用提取提示词
CITATION_EXTRACTION_PROMPT = """请从以下文本中提取引用信息：

{content}

请识别并提取文本中的所有引用，包括：
1. 直接引用（使用引号的文本）
2. 间接引用（提及他人观点但未使用引号）
3. 引用标记（如括号中的作者-年份格式）

请以JSON格式返回：
{
    "citations": [
        {
            "text": "引用文本",
            "position": "在原文中的位置",
            "type": "直接引用/间接引用",
            "author": "可能的作者（如有）",
            "year": "可能的年份（如有）"
        }
    ],
    "total_count": 引用总数
}
"""

# 参考文献生成提示词
BIBLIOGRAPHY_GENERATION_PROMPT = """请根据以下文献信息，生成参考文献列表：

文献信息:
{literature}

引用样式: {style}

请按照指定的引用样式，为每篇文献生成规范的参考文献条目。

请以JSON格式返回：
{
    "bibliography": [
        {
            "id": "文献ID",
            "formatted_reference": "格式化的参考文献条目"
        }
    ],
    "style_guide": "所用引用样式的简要说明"
}
"""
