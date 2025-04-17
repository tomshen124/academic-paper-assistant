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

    def _clean_json_response(self, content: str) -> str:
        """清理LLM响应中的Markdown代码块标记"""
        # 移除可能的Markdown代码块标记
        import re

        # 记录原始内容
        logger.debug(f"原始内容: {content[:200]}...")

        # 首先尝试匹配```json和```之间的内容
        json_block_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', content)
        if json_block_match:
            # 返回代码块内的内容
            cleaned = json_block_match.group(1).strip()
            logger.debug(f"从代码块提取的内容: {cleaned[:200]}...")
            return cleaned

        # 如果没有找到代码块，尝试匹配整个JSON对象
        # 匹配从第一个{开始到最后一个}结束的内容
        json_obj_match = re.search(r'(\{[\s\S]*\})', content)
        if json_obj_match:
            cleaned = json_obj_match.group(1).strip()
            logger.debug(f"从文本提取的JSON对象: {cleaned[:200]}...")
            return cleaned

        # 尝试匹配包含"topics"关键字的JSON对象
        topics_match = re.search(r'\{\s*"topics"\s*:\s*\[[\s\S]*?\]\s*\}', content)
        if topics_match:
            cleaned = topics_match.group(0).strip()
            logger.debug(f"从文本提取的topics对象: {cleaned[:200]}...")
            return cleaned

        # 如果以上都失败，返回原始内容
        logger.debug("所有提取尝试失败，返回原始内容")
        return content.strip()

    async def recommend_topics(
        self,
        user_interests: str,
        academic_field: str,
        academic_level: str = "undergraduate",
        topic_count: int = 3,
        interest_analysis: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """推荐论文主题"""
        try:
            logger.info(f"推荐论文主题: 兴趣={user_interests}, 领域={academic_field}, 级别={academic_level}")

            # 获取研究趋势
            trends = await self.academic_search_service.get_research_trends(academic_field)

            # 使用智能体协调器进行多智能体协作
            from app.services.agent_service import agent_coordinator

            logger.info("开始多智能体协作推荐主题")

            # 1. 研究智能体分析研究趋势和用户兴趣
            logger.info("第一步: 研究智能体分析研究趋势和用户兴趣")
            research_analysis = await agent_coordinator.run_agent(
                "research",
                "analyze_research_trends",
                {
                    "user_interests": user_interests,
                    "academic_field": academic_field,
                    "academic_level": academic_level,
                    "research_trends": json.dumps(trends, ensure_ascii=False)
                }
            )

            if not research_analysis:
                logger.error("研究智能体分析失败")
                # 如果智能体协作失败，回退到原始方法
                return await self._fallback_recommend_topics(user_interests, academic_field, academic_level, trends, topic_count, interest_analysis)

            logger.info(f"研究分析完成: {json.dumps(research_analysis, ensure_ascii=False)[:100]}...")

            # 2. 写作智能体生成主题建议
            logger.info("第二步: 写作智能体生成主题建议")
            topic_suggestions = await agent_coordinator.run_agent(
                "writing",
                "generate_topic_suggestions",
                {
                    "research_analysis": json.dumps(research_analysis, ensure_ascii=False),
                    "user_interests": user_interests,
                    "academic_field": academic_field,
                    "academic_level": academic_level
                }
            )

            if not topic_suggestions or "topic_suggestions" not in topic_suggestions:
                logger.error("写作智能体生成主题建议失败")
                # 如果智能体协作失败，回退到原始方法
                return await self._fallback_recommend_topics(user_interests, academic_field, academic_level, trends, topic_count, interest_analysis)

            logger.info(f"生成了 {len(topic_suggestions.get('topic_suggestions', []))} 个主题建议")

            # 3. 编辑智能体评估和优化主题
            logger.info("第三步: 编辑智能体评估和优化主题")
            final_topics_result = await agent_coordinator.run_agent(
                "editing",
                "refine_topics",
                {
                    "topic_suggestions": json.dumps(topic_suggestions, ensure_ascii=False),
                    "user_interests": user_interests,
                    "academic_field": academic_field,
                    "academic_level": academic_level
                }
            )

            if not final_topics_result or "topics" not in final_topics_result:
                logger.error("编辑智能体评估和优化主题失败")
                # 如果智能体协作失败，回退到原始方法
                return await self._fallback_recommend_topics(user_interests, academic_field, academic_level, trends, topic_count, interest_analysis)

            final_topics = final_topics_result.get("topics", [])
            logger.info(f"最终生成了 {len(final_topics)} 个优化主题")

            return final_topics

        except Exception as e:
            logger.error(f"推荐主题失败: {str(e)}")
            # 如果发生异常，回退到原始方法
            return await self._fallback_recommend_topics(user_interests, academic_field, academic_level, trends, topic_count, interest_analysis)

    async def _fallback_recommend_topics(
        self,
        user_interests: str,
        academic_field: str,
        academic_level: str,
        trends: List[Dict[str, Any]],
        topic_count: int = 3,
        interest_analysis: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """备用的主题推荐方法，当多智能体协作失败时使用"""
        logger.info("使用备用方法推荐主题")

        try:
            # 构建提示
            interest_analysis_text = ""
            if interest_analysis:
                # 如果有兴趣分析结果，将其添加到提示中
                interest_analysis_text = f"""
兴趣分析结果:
- 关键概念: {json.dumps(interest_analysis.get('key_concepts', []), ensure_ascii=False)}
- 研究方向: {json.dumps(interest_analysis.get('research_directions', []), ensure_ascii=False)}
- 相关领域: {json.dumps(interest_analysis.get('related_fields', []), ensure_ascii=False)}
- 研究趋势: {json.dumps(interest_analysis.get('research_trends', []), ensure_ascii=False)}
- 建议关键词: {json.dumps(interest_analysis.get('suggested_keywords', []), ensure_ascii=False)}
"""

            system_prompt = f"""你是一个学术论文主题推荐专家。你的任务是为{academic_level}级别的学生推荐合适的论文主题。

请基于以下信息推荐{topic_count}个具体的论文主题：
1. 学生兴趣: {user_interests}
2. 学术领域: {academic_field}
3. 学术级别: {academic_level}
4. 当前研究趋势: {json.dumps(trends, ensure_ascii=False)}
{interest_analysis_text}

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

注意：
1. 请确保你的推荐是具体的、可行的，并且与学生的兴趣和学术水平相匹配。
2. 请保持每个字段的描述简洁明确，不要超过100个字符。
3. 请仅返回JSON格式的内容，不要添加其他解释或标记。"""

            # 调用LLM
            response = await self.llm_service.acompletion(
                messages=[{"role": "system", "content": system_prompt}],
                max_tokens=3000,  # 增加token限制，确保有足够空间生成完整的JSON
                temperature=0.7
            )

            # 解析响应
            content = response.choices[0].message.content

            # 记录原始响应以便调试
            logger.info(f"原始 LLM 响应: {content[:200]}...")

            # 处理可能的Markdown代码块
            cleaned_content = self._clean_json_response(content)
            logger.info(f"清理后的响应: {cleaned_content[:200]}...")

            # 尝试解析JSON
            try:
                result = json.loads(cleaned_content)
                topics = result.get("topics", [])
                logger.info(f"成功解析JSON并推荐 {len(topics)} 个主题")

                # 确保每个主题都有必要的字段
                validated_topics = []
                for topic in topics:
                    if not isinstance(topic, dict):
                        logger.warning(f"主题不是字典格式: {topic}")
                        continue

                    # 确保所有必要字段存在
                    if 'title' not in topic:
                        logger.warning(f"主题缺少title字段: {topic}")
                        continue

                    # 补充缺失的字段
                    validated_topic = {
                        'title': topic.get('title', ''),
                        'research_question': topic.get('research_question', ''),
                        'feasibility': topic.get('feasibility', ''),
                        'innovation': topic.get('innovation', ''),
                        'methodology': topic.get('methodology', ''),
                        'resources': topic.get('resources', ''),
                        'expected_outcomes': topic.get('expected_outcomes', ''),
                        'keywords': topic.get('keywords', [])
                    }
                    validated_topics.append(validated_topic)

                logger.info(f"验证后的主题数量: {len(validated_topics)}")
                return validated_topics

            except json.JSONDecodeError as e:
                logger.error(f"无法解析LLM响应为JSON: {str(e)}")
                logger.error(f"内容: {cleaned_content}")

                # 尝试直接从原始内容中提取JSON对象
                try:
                    # 尝试修复可能的JSON格式问题
                    fixed_content = cleaned_content.replace("''", '"').replace("'", '"')
                    result = json.loads(fixed_content)
                    topics = result.get("topics", [])
                    logger.info(f"修复后成功解析JSON并推荐 {len(topics)} 个主题")
                    return topics
                except json.JSONDecodeError:
                    # 如果仍然失败，尝试从原始内容中提取并解析
                    logger.info(f"尝试从原始内容中提取JSON")

                    # 尝试直接从原始内容中提取主题列表
                    import re

                    # 尝试提取完整的topics数组
                    topics_array_match = re.search(r'"topics"\s*:\s*\[(.*?)\]', content, re.DOTALL)
                    if topics_array_match:
                        try:
                            # 尝试将提取的数组包装成完整的JSON
                            topics_array = topics_array_match.group(1).strip()
                            topics_json = '{"topics":[' + topics_array + ']}'
                            # 修复可能的JSON格式问题
                            fixed_json = topics_json.replace("''", '"').replace("'", '"')
                            result = json.loads(fixed_json)
                            topics = result.get("topics", [])
                            logger.info(f"成功从文本中提取topics数组，共 {len(topics)} 个主题")
                            return topics
                        except json.JSONDecodeError as e:
                            logger.error(f"解析topics数组失败: {str(e)}")

                    # 如果上面的方法失败，尝试提取单个主题
                    topics_match = re.findall(r'\{\s*"title"[\s\S]*?\}', content)
                    if topics_match:
                        topics = []
                        for topic_str in topics_match:
                            try:
                                # 尝试修复并解析单个主题
                                fixed_topic_str = topic_str.replace("''", '"').replace("'", '"')
                                topic = json.loads(fixed_topic_str)
                                topics.append(topic)
                            except json.JSONDecodeError as e:
                                logger.error(f"解析单个主题失败: {str(e)}, 内容: {topic_str[:100]}...")

                        if topics:
                            logger.info(f"成功从文本中提取并推荐 {len(topics)} 个主题")
                            return topics

                    # 尝试使用正则表达式提取主题标题和其他字段
                    title_matches = re.findall(r'"title"\s*:\s*"([^"]+)"', content)
                    if title_matches:
                        # 如果至少能提取到标题，就创建简单的主题对象
                        topics = []
                        for title in title_matches:
                            # 尝试为每个标题提取相关字段
                            topic = {"title": title}

                            # 尝试提取研究问题
                            research_match = re.search(f'"{title}"[\s\S]{{0,200}}"research_question"\s*:\s*"([^"]+)"', content)
                            if research_match:
                                topic["research_question"] = research_match.group(1)

                            # 添加默认字段
                            topic.setdefault("research_question", "无研究问题")
                            topic.setdefault("feasibility", "中等可行性")
                            topic.setdefault("innovation", "创新点待补充")
                            topic.setdefault("methodology", "待定研究方法")
                            topic.setdefault("resources", "基本研究资源")
                            topic.setdefault("expected_outcomes", "预期成果待定义")
                            topic.setdefault("keywords", [title.split()[0] if title.split() else title])

                            topics.append(topic)

                        if topics:
                            logger.info(f"成功从文本中提取主题标题，共 {len(topics)} 个主题")
                            return topics

                # 如果仍然失败，返回空列表
                logger.error("所有解析尝试均失败，返回空列表")
                return []

        except Exception as e:
            logger.error(f"备用方法推荐主题失败: {str(e)}")
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

            # 记录原始响应以便调试
            logger.info(f"原始 LLM 响应(可行性分析): {content[:200]}...")

            # 处理可能的Markdown代码块
            cleaned_content = self._clean_json_response(content)
            logger.info(f"清理后的响应: {cleaned_content[:200]}...")

            # 尝试解析JSON
            try:
                result = json.loads(cleaned_content)
                logger.info(f"成功解析JSON并分析主题可行性，评分: {result.get('overall_score', 'N/A')}")

                # 确保结果包含所有必要字段
                validated_result = {
                    'difficulty': result.get('difficulty', ''),
                    'resources': result.get('resources', ''),
                    'time_estimate': result.get('time_estimate', ''),
                    'research_gaps': result.get('research_gaps', ''),
                    'challenges': result.get('challenges', ''),
                    'suggestions': result.get('suggestions', ''),
                    'overall_score': result.get('overall_score', 5),  # 默认中等评分
                    'recommendation': result.get('recommendation', '')
                }

                return validated_result

            except json.JSONDecodeError as e:
                logger.error(f"无法解析LLM响应为JSON: {str(e)}")
                logger.error(f"内容: {cleaned_content}")

                # 尝试修复可能的JSON格式问题
                try:
                    fixed_content = cleaned_content.replace("''", '"').replace("'", '"')
                    result = json.loads(fixed_content)
                    logger.info(f"修复后成功解析JSON并分析主题可行性")
                    return result
                except json.JSONDecodeError:
                    # 如果仍然失败，尝试从原始内容中提取并解析
                    import re
                    json_match = re.search(r'({[\s\S]*})', content)
                    if json_match:
                        try:
                            result = json.loads(json_match.group(1))
                            logger.info(f"成功从文本中提取主题可行性分析")
                            return result
                        except json.JSONDecodeError:
                            # 尝试修复提取的JSON
                            try:
                                fixed_json = json_match.group(1).replace("''", '"').replace("'", '"')
                                result = json.loads(fixed_json)
                                logger.info(f"修复后成功从文本中提取主题可行性分析")
                                return result
                            except:
                                pass

                # 如果仍然失败，返回默认结果
                logger.error("所有解析尝试均失败，返回默认可行性分析")
                return {
                    'difficulty': '适中',
                    'resources': '需要基本的研究资源',
                    'time_estimate': '3-6个月',
                    'research_gaps': '存在一定的研究空白',
                    'challenges': '可能面临一定的技术挑战',
                    'suggestions': '建议缩小研究范围，明确研究目标',
                    'overall_score': 5,  # 默认中等评分
                    'recommendation': '在有指导的情况下可行'
                }

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

            # 记录原始响应以便调试
            logger.info(f"原始 LLM 响应(主题优化): {content[:200]}...")

            # 处理可能的Markdown代码块
            cleaned_content = self._clean_json_response(content)
            logger.info(f"清理后的响应: {cleaned_content[:200]}...")

            # 尝试解析JSON
            try:
                result = json.loads(cleaned_content)
                logger.info(f"成功解析JSON并优化主题: {result.get('refined_title', 'N/A')}")

                # 确保结果包含所有必要字段
                validated_result = {
                    'refined_title': result.get('refined_title', ''),
                    'research_question': result.get('research_question', ''),
                    'scope': result.get('scope', ''),
                    'methodology': result.get('methodology', ''),
                    'keywords': result.get('keywords', []),
                    'improvements': result.get('improvements', '')
                }

                return validated_result

            except json.JSONDecodeError as e:
                logger.error(f"无法解析LLM响应为JSON: {str(e)}")
                logger.error(f"内容: {cleaned_content}")

                # 尝试修复可能的JSON格式问题
                try:
                    fixed_content = cleaned_content.replace("''", '"').replace("'", '"')
                    result = json.loads(fixed_content)
                    logger.info(f"修复后成功解析JSON并优化主题")
                    return result
                except json.JSONDecodeError:
                    # 如果仍然失败，尝试从原始内容中提取并解析
                    import re
                    json_match = re.search(r'({[\s\S]*})', content)
                    if json_match:
                        try:
                            result = json.loads(json_match.group(1))
                            logger.info(f"成功从文本中提取优化主题")
                            return result
                        except json.JSONDecodeError:
                            # 尝试修复提取的JSON
                            try:
                                fixed_json = json_match.group(1).replace("''", '"').replace("'", '"')
                                result = json.loads(fixed_json)
                                logger.info(f"修复后成功从文本中提取优化主题")
                                return result
                            except:
                                pass

                # 如果仍然失败，返回空字典
                logger.error("所有解析尝试均失败，返回空字典")
                return {}

        except Exception as e:
            logger.error(f"优化主题失败: {str(e)}")
            return {}

# 创建全局主题服务实例
topic_service = TopicService()
