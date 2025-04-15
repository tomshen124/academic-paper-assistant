from typing import List, Dict, Any, Optional
import asyncio
import json
from app.core.logger import get_logger
from app.services.llm_service import llm_service
from app.services.academic_search_service import academic_search_service

# 创建日志器
logger = get_logger("topic_service")

class TopicService:
    """论文主题推荐服务"""
    
    def __init__(self):
        """初始化主题推荐服务"""
        self.llm_service = llm_service
        self.academic_search_service = academic_search_service
        logger.info("主题推荐服务初始化完成")
    
    async def recommend_topics(
        self, 
        user_interests: str, 
        academic_field: str, 
        academic_level: str = "undergraduate"
    ) -> List[Dict[str, Any]]:
        """推荐论文主题"""
        try:
            logger.info(f"推荐论文主题: 兴趣={user_interests}, 领域={academic_field}, 级别={academic_level}")
            
            # 获取研究趋势
            trends = await self.academic_search_service.get_research_trends(academic_field)
            
            # 构建提示
            system_prompt = f"""你是一个学术论文主题推荐专家。你的任务是为{academic_level}级别的学生推荐合适的论文主题。

请基于以下信息推荐5个具体的论文主题：
1. 学生兴趣: {user_interests}
2. 学术领域: {academic_field}
3. 学术级别: {academic_level}
4. 当前研究趋势: {json.dumps(trends, ensure_ascii=False)}

对于每个推荐的主题，请提供以下信息：
1. 主题标题：具体且有研究价值的标题
2. 研究问题：该主题要解决的核心问题
3. 可行性：该主题对于{academic_level}级别学生的可行性评估（高/中/低）
4. 创新点：该主题的创新之处
5. 研究方法：建议采用的研究方法
6. 所需资源：完成该研究所需的主要资源
7. 预期成果：预期能够得出的结论或成果
8. 关键词：5-8个相关关键词

请以JSON格式返回结果，格式如下：
{{
  "topics": [
    {{
      "title": "主题标题",
      "research_question": "研究问题",
      "feasibility": "可行性",
      "innovation": "创新点",
      "methodology": "研究方法",
      "resources": "所需资源",
      "expected_outcomes": "预期成果",
      "keywords": ["关键词1", "关键词2", ...]
    }},
    ...
  ]
}}

确保你的推荐是具体的、可行的，并且与学生的兴趣和学术水平相匹配。"""

            # 调用LLM
            response = await self.llm_service.acompletion(
                messages=[{"role": "system", "content": system_prompt}],
                max_tokens=2000,
                temperature=0.7
            )
            
            # 解析响应
            content = response.choices[0].message.content
            
            # 尝试解析JSON
            try:
                result = json.loads(content)
                topics = result.get("topics", [])
                logger.info(f"成功推荐 {len(topics)} 个主题")
                return topics
            except json.JSONDecodeError:
                logger.error(f"无法解析LLM响应为JSON: {content}")
                # 尝试提取JSON部分
                import re
                json_match = re.search(r'({[\s\S]*})', content)
                if json_match:
                    try:
                        result = json.loads(json_match.group(1))
                        topics = result.get("topics", [])
                        logger.info(f"成功从文本中提取并推荐 {len(topics)} 个主题")
                        return topics
                    except:
                        pass
                
                # 如果仍然失败，返回空列表
                return []
                
        except Exception as e:
            logger.error(f"推荐主题失败: {str(e)}")
            return []
    
    async def analyze_topic_feasibility(
        self, 
        topic: str, 
        academic_field: str, 
        academic_level: str = "undergraduate"
    ) -> Dict[str, Any]:
        """分析主题可行性"""
        try:
            logger.info(f"分析主题可行性: 主题={topic}, 领域={academic_field}, 级别={academic_level}")
            
            # 搜索相关文献
            papers = await self.academic_search_service.search_academic_papers(topic, limit=5)
            
            # 构建提示
            system_prompt = f"""你是一个学术论文主题可行性分析专家。你的任务是分析以下论文主题对于{academic_level}级别学生的可行性。

主题: {topic}
学术领域: {academic_field}
学术级别: {academic_level}

相关文献:
{json.dumps(papers, ensure_ascii=False)}

请从以下几个方面分析该主题的可行性:
1. 难度评估：该主题对于{academic_level}级别学生的难度（简单/适中/困难）
2. 资源需求：完成该研究所需的主要资源
3. 时间估计：完成该研究所需的大致时间
4. 研究空白：该领域的研究空白和机会
5. 潜在挑战：可能面临的主要挑战
6. 改进建议：如何调整主题以提高可行性
7. 总体评分：总体可行性评分（1-10分）

请以JSON格式返回结果，格式如下：
{{
  "difficulty": "难度评估",
  "resources": "资源需求",
  "time_estimate": "时间估计",
  "research_gaps": "研究空白",
  "challenges": "潜在挑战",
  "suggestions": "改进建议",
  "overall_score": 评分数字,
  "recommendation": "最终建议"
}}"""

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
                logger.info(f"成功分析主题可行性，评分: {result.get('overall_score', 'N/A')}")
                return result
            except json.JSONDecodeError:
                logger.error(f"无法解析LLM响应为JSON: {content}")
                # 尝试提取JSON部分
                import re
                json_match = re.search(r'({[\s\S]*})', content)
                if json_match:
                    try:
                        result = json.loads(json_match.group(1))
                        logger.info(f"成功从文本中提取主题可行性分析，评分: {result.get('overall_score', 'N/A')}")
                        return result
                    except:
                        pass
                
                # 如果仍然失败，返回空字典
                return {}
                
        except Exception as e:
            logger.error(f"分析主题可行性失败: {str(e)}")
            return {}
    
    async def refine_topic(
        self, 
        topic: str, 
        feedback: str, 
        academic_field: str, 
        academic_level: str = "undergraduate"
    ) -> Dict[str, Any]:
        """根据反馈优化主题"""
        try:
            logger.info(f"优化主题: 主题={topic}, 反馈={feedback}")
            
            # 构建提示
            system_prompt = f"""你是一个学术论文主题优化专家。你的任务是根据反馈优化以下论文主题。

原始主题: {topic}
学术领域: {academic_field}
学术级别: {academic_level}
用户反馈: {feedback}

请优化该主题，使其更加具体、可行，并符合用户的反馈。

请以JSON格式返回结果，格式如下：
{{
  "refined_title": "优化后的主题标题",
  "research_question": "明确的研究问题",
  "scope": "研究范围",
  "methodology": "建议的研究方法",
  "keywords": ["关键词1", "关键词2", ...],
  "improvements": "相比原主题的改进之处"
}}"""

            # 调用LLM
            response = await self.llm_service.acompletion(
                messages=[{"role": "system", "content": system_prompt}],
                max_tokens=1000,
                temperature=0.5
            )
            
            # 解析响应
            content = response.choices[0].message.content
            
            # 尝试解析JSON
            try:
                result = json.loads(content)
                logger.info(f"成功优化主题: {result.get('refined_title', 'N/A')}")
                return result
            except json.JSONDecodeError:
                logger.error(f"无法解析LLM响应为JSON: {content}")
                # 尝试提取JSON部分
                import re
                json_match = re.search(r'({[\s\S]*})', content)
                if json_match:
                    try:
                        result = json.loads(json_match.group(1))
                        logger.info(f"成功从文本中提取优化主题: {result.get('refined_title', 'N/A')}")
                        return result
                    except:
                        pass
                
                # 如果仍然失败，返回空字典
                return {}
                
        except Exception as e:
            logger.error(f"优化主题失败: {str(e)}")
            return {}

# 创建全局主题服务实例
topic_service = TopicService()
