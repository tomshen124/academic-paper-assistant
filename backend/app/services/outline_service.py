from typing import List, Dict, Any, Optional
import asyncio
import json
from app.core.logger import get_logger
from app.services.llm_service import llm_service
from app.services.academic_search_service import academic_search_service

# 创建日志器
logger = get_logger("outline_service")

class OutlineService:
    """论文提纲生成服务"""
    
    def __init__(self):
        """初始化提纲生成服务"""
        self.llm_service = llm_service
        self.academic_search_service = academic_search_service
        logger.info("提纲生成服务初始化完成")
    
    async def generate_outline(
        self, 
        topic: str, 
        paper_type: str, 
        academic_field: str, 
        academic_level: str = "undergraduate",
        length: str = "3000words"
    ) -> Dict[str, Any]:
        """生成论文提纲"""
        try:
            logger.info(f"生成论文提纲: 主题={topic}, 类型={paper_type}, 领域={academic_field}, 长度={length}")
            
            # 搜索相关文献
            papers = await self.academic_search_service.search_academic_papers(topic, limit=5)
            
            # 构建系统提示
            system_prompt = "你是一个学术论文提纲生成专家。你的任务是为以下论文主题生成详细的提纲。\n\n"
            system_prompt += f"论文主题: {topic}\n"
            system_prompt += f"论文类型: {paper_type}\n"
            system_prompt += f"学术领域: {academic_field}\n"
            system_prompt += f"学术级别: {academic_level}\n"
            system_prompt += f"预期长度: {length}\n\n"
            system_prompt += f"相关文献:\n{json.dumps(papers, ensure_ascii=False)[:1500]}\n\n"
            system_prompt += """请生成一个详细的论文提纲，包括以下部分:
1. 标题：具体且能反映研究内容的标题
2. 摘要：概述论文的主要内容和贡献
3. 关键词：5-8个相关关键词
4. 章节结构：详细的章节和子章节结构，包括:
   - 引言（研究背景、问题陈述、研究目的、研究意义）
   - 文献综述（相关研究回顾）
   - 研究方法（数据收集、分析方法）
   - 结果分析（主要发现）
   - 讨论（结果解释、与现有研究的关系）
   - 结论（总结、局限性、未来研究方向）
   - 参考文献

对于每个章节和子章节，请提供:
- 章节标题
- 章节目的
- 建议内容要点（3-5点）
- 预期长度（字数或段落数）

请以JSON格式返回结果，格式如下:
{
  "title": "论文标题",
  "abstract": "摘要内容",
  "keywords": ["关键词1", "关键词2", ...],
  "sections": [
    {
      "id": "1",
      "title": "章节标题",
      "purpose": "章节目的",
      "content_points": ["要点1", "要点2", ...],
      "expected_length": "预期长度",
      "subsections": [
        {
          "id": "1.1",
          "title": "子章节标题",
          "purpose": "子章节目的",
          "content_points": ["要点1", "要点2", ...],
          "expected_length": "预期长度"
        },
        ...
      ]
    },
    ...
  ]
}
"""
            system_prompt += f"\n确保提纲结构逻辑清晰，内容全面，符合{academic_field}领域的学术规范。"

            # 调用LLM
            response = await self.llm_service.acompletion(
                messages=[{"role": "system", "content": system_prompt}],
                max_tokens=2500,
                temperature=0.4
            )
            
            # 解析响应
            content = response.choices[0].message.content
            
            # 尝试解析JSON
            try:
                result = json.loads(content)
                logger.info(f"成功生成提纲: {result.get('title', 'N/A')}")
                return result
            except json.JSONDecodeError:
                logger.error(f"无法解析LLM响应为JSON: {content}")
                # 尝试提取JSON部分
                import re
                json_match = re.search(r'({[\s\S]*})', content)
                if json_match:
                    try:
                        result = json.loads(json_match.group(1))
                        logger.info(f"成功从文本中提取提纲: {result.get('title', 'N/A')}")
                        return result
                    except:
                        pass
                
                # 如果仍然失败，返回空字典
                return {}
                
        except Exception as e:
            logger.error(f"生成提纲失败: {str(e)}")
            return {}
    
    async def optimize_outline(
        self, 
        outline: Dict[str, Any], 
        feedback: str
    ) -> Dict[str, Any]:
        """优化论文提纲"""
        try:
            logger.info(f"优化论文提纲: 反馈={feedback}")
            
            # 构建系统提示
            system_prompt = "你是一个学术论文提纲优化专家。你的任务是根据反馈优化以下论文提纲。\n\n"
            system_prompt += f"原始提纲:\n{json.dumps(outline, ensure_ascii=False)}\n\n"
            system_prompt += f"用户反馈:\n{feedback}\n\n"
            system_prompt += "请根据用户的反馈优化提纲，可以调整章节结构、内容要点、预期长度等。保持JSON格式不变，但内容要根据反馈进行改进。\n\n"
            system_prompt += "请以与原始提纲相同的JSON格式返回优化后的提纲。"

            # 调用LLM
            response = await self.llm_service.acompletion(
                messages=[{"role": "system", "content": system_prompt}],
                max_tokens=2500,
                temperature=0.3
            )
            
            # 解析响应
            content = response.choices[0].message.content
            
            # 尝试解析JSON
            try:
                result = json.loads(content)
                logger.info(f"成功优化提纲: {result.get('title', 'N/A')}")
                return result
            except json.JSONDecodeError:
                logger.error(f"无法解析LLM响应为JSON: {content}")
                # 尝试提取JSON部分
                import re
                json_match = re.search(r'({[\s\S]*})', content)
                if json_match:
                    try:
                        result = json.loads(json_match.group(1))
                        logger.info(f"成功从文本中提取优化提纲: {result.get('title', 'N/A')}")
                        return result
                    except:
                        pass
                
                # 如果仍然失败，返回原始提纲
                return outline
                
        except Exception as e:
            logger.error(f"优化提纲失败: {str(e)}")
            return outline
    
    async def get_outline_templates(
        self, 
        paper_type: str, 
        academic_field: str
    ) -> List[Dict[str, Any]]:
        """获取提纲模板"""
        try:
            logger.info(f"获取提纲模板: 类型={paper_type}, 领域={academic_field}")
            
            # 构建系统提示
            system_prompt = "你是一个学术论文提纲模板专家。你的任务是为以下论文类型和学术领域提供3个提纲模板。\n\n"
            system_prompt += f"论文类型: {paper_type}\n"
            system_prompt += f"学术领域: {academic_field}\n\n"
            system_prompt += """请提供3个不同的提纲模板，每个模板包括:
1. 模板名称：简洁描述模板特点
2. 适用场景：该模板最适合的研究类型
3. 章节结构：主要章节和子章节
4. 特点：该模板的主要特点和优势

请以JSON格式返回结果，格式如下:
{
  "templates": [
    {
      "name": "模板名称",
      "suitable_for": "适用场景",
      "structure": [
        {
          "title": "章节标题",
          "subsections": ["子章节1", "子章节2", ...]
        },
        ...
      ],
      "features": ["特点1", "特点2", ...]
    },
    ...
  ]
}"""

            # 调用LLM
            response = await self.llm_service.acompletion(
                messages=[{"role": "system", "content": system_prompt}],
                max_tokens=1500,
                temperature=0.5
            )
            
            # 解析响应
            content = response.choices[0].message.content
            
            # 尝试解析JSON
            try:
                result = json.loads(content)
                templates = result.get("templates", [])
                logger.info(f"成功获取 {len(templates)} 个提纲模板")
                return templates
            except json.JSONDecodeError:
                logger.error(f"无法解析LLM响应为JSON: {content}")
                # 尝试提取JSON部分
                import re
                json_match = re.search(r'({[\s\S]*})', content)
                if json_match:
                    try:
                        result = json.loads(json_match.group(1))
                        templates = result.get("templates", [])
                        logger.info(f"成功从文本中提取 {len(templates)} 个提纲模板")
                        return templates
                    except:
                        pass
                
                # 如果仍然失败，返回空列表
                return []
                
        except Exception as e:
            logger.error(f"获取提纲模板失败: {str(e)}")
            return []
    
    async def validate_outline_logic(
        self, 
        outline: Dict[str, Any]
    ) -> Dict[str, Any]:
        """验证提纲逻辑"""
        try:
            logger.info(f"验证提纲逻辑: {outline.get('title', 'N/A')}")
            
            # 构建系统提示
            system_prompt = "你是一个学术论文提纲逻辑分析专家。你的任务是分析以下论文提纲的逻辑结构，找出潜在问题并提供改进建议。\n\n"
            system_prompt += f"提纲:\n{json.dumps(outline, ensure_ascii=False)}\n\n"
            system_prompt += """请分析以下几个方面:
1. 结构完整性：是否包含所有必要的章节
2. 逻辑连贯性：章节之间的逻辑关系是否清晰
3. 内容平衡性：各章节内容是否平衡
4. 研究方法适当性：研究方法是否适合研究问题
5. 潜在问题：可能存在的逻辑漏洞或结构问题
6. 改进建议：如何改进提纲结构和逻辑

请以JSON格式返回结果，格式如下:
{
  "completeness": {
    "score": 评分(1-10),
    "issues": ["问题1", "问题2", ...],
    "suggestions": ["建议1", "建议2", ...]
  },
  "coherence": {
    "score": 评分(1-10),
    "issues": ["问题1", "问题2", ...],
    "suggestions": ["建议1", "建议2", ...]
  },
  "balance": {
    "score": 评分(1-10),
    "issues": ["问题1", "问题2", ...],
    "suggestions": ["建议1", "建议2", ...]
  },
  "methodology": {
    "score": 评分(1-10),
    "issues": ["问题1", "问题2", ...],
    "suggestions": ["建议1", "建议2", ...]
  },
  "overall_assessment": "总体评价",
  "overall_score": 总评分(1-10)
}"""

            # 调用LLM
            response = await self.llm_service.acompletion(
                messages=[{"role": "system", "content": system_prompt}],
                max_tokens=1500,
                temperature=0.3
            )
            
            # 解析响应
            content = response.choices[0].message.content
            
            # 尝试解析JSON
            try:
                result = json.loads(content)
                logger.info(f"成功验证提纲逻辑，总评分: {result.get('overall_score', 'N/A')}")
                return result
            except json.JSONDecodeError:
                logger.error(f"无法解析LLM响应为JSON: {content}")
                # 尝试提取JSON部分
                import re
                json_match = re.search(r'({[\s\S]*})', content)
                if json_match:
                    try:
                        result = json.loads(json_match.group(1))
                        logger.info(f"成功从文本中提取提纲逻辑验证，总评分: {result.get('overall_score', 'N/A')}")
                        return result
                    except:
                        pass
                
                # 如果仍然失败，返回空字典
                return {}
                
        except Exception as e:
            logger.error(f"验证提纲逻辑失败: {str(e)}")
            return {}

# 创建全局提纲服务实例
outline_service = OutlineService()
