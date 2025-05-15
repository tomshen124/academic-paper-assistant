"""
兴趣分析服务，用于分析用户兴趣并生成初步的主题方向
"""
from typing import List, Dict, Any
import json
import logging
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)

class InterestAnalysisService:
    """兴趣分析服务，用于分析用户兴趣并生成初步的主题方向"""

    async def analyze_interests(
        self,
        user_interests: str,
        academic_field: str,
        academic_level: str = "undergraduate"
    ) -> Dict[str, Any]:
        """
        分析用户兴趣并生成初步的主题方向

        Args:
            user_interests: 用户研究兴趣
            academic_field: 学术领域
            academic_level: 学术级别

        Returns:
            包含分析结果的字典，包括关键概念、研究方向等
        """
        try:
            logger.info(f"分析用户兴趣: 兴趣={user_interests}, 领域={academic_field}, 级别={academic_level}")

            # 构建提示
            system_prompt = f"""你是一个学术研究兴趣分析专家。你的任务是分析用户的研究兴趣，并提取关键概念和潜在的研究方向。

用户信息:
- 研究兴趣: {user_interests}
- 学术领域: {academic_field}
- 学术级别: {academic_level}

请分析用户的研究兴趣，并提供以下信息:
1. 关键概念: 从用户兴趣中提取的核心概念和关键词
2. 研究方向: 基于用户兴趣可能的研究方向
3. 相关领域: 与用户兴趣相关的交叉学科领域
4. 研究趋势: 该领域当前的研究趋势和热点
5. 建议关键词: 用于学术搜索的关键词

请以JSON格式返回结果，格式如下:
{{
  "key_concepts": ["概念1", "概念2", ...],
  "research_directions": ["方向1", "方向2", ...],
  "related_fields": ["相关领域1", "相关领域2", ...],
  "research_trends": ["趋势1", "趋势2", ...],
  "suggested_keywords": ["关键词1", "关键词2", ...]
}}

请确保你的分析是深入的、有见解的，并且与用户的学术级别相匹配。"""

            # 调用LLM
            # 构建消息列表，确保最后一条是用户消息
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"请分析我的研究兴趣: {user_interests}"}
            ]

            logger.info(f"发送到LLM的消息格式: {messages}")

            response = await llm_service.acompletion(
                messages=messages,
                max_tokens=1500,
                temperature=0.3
            )

            # 解析响应
            content = response.choices[0].message.content

            # 记录原始响应以便调试
            logger.info(f"原始 LLM 响应(兴趣分析): {content[:200]}...")

            # 处理可能的Markdown代码块
            cleaned_content = self._clean_json_response(content)

            # 尝试解析JSON
            try:
                result = json.loads(cleaned_content)
                logger.info(f"成功解析JSON并分析用户兴趣")
                return result
            except json.JSONDecodeError as e:
                logger.error(f"无法解析LLM响应为JSON: {str(e)}")

                # 尝试修复可能的JSON格式问题
                try:
                    fixed_content = cleaned_content.replace("''", '"').replace("'", '"')
                    result = json.loads(fixed_content)
                    logger.info(f"修复后成功解析JSON并分析用户兴趣")
                    return result
                except json.JSONDecodeError:
                    # 如果仍然失败，尝试从原始内容中提取并解析
                    import re
                    json_match = re.search(r'({[\s\S]*})', content)
                    if json_match:
                        try:
                            result = json.loads(json_match.group(1))
                            logger.info(f"成功从文本中提取用户兴趣分析")
                            return result
                        except:
                            pass

                # 如果所有尝试都失败，返回空字典
                logger.error("所有解析尝试均失败，返回空字典")
                return {}

        except Exception as e:
            logger.error(f"分析用户兴趣失败: {str(e)}")
            return {}

    def _clean_json_response(self, content: str) -> str:
        """清理LLM响应中的Markdown代码块标记"""
        # 移除可能的Markdown代码块标记
        import re

        # 首先尝试匹配```json和```之间的内容
        json_block_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', content)
        if json_block_match:
            # 返回代码块内的内容
            return json_block_match.group(1).strip()

        # 如果没有找到代码块，尝试匹配整个JSON对象
        # 匹配从第一个{开始到最后一个}结束的内容
        json_obj_match = re.search(r'(\{[\s\S]*\})', content)
        if json_obj_match:
            return json_obj_match.group(1).strip()

        # 如果以上都失败，返回原始内容
        return content.strip()

# 创建全局兴趣分析服务实例
interest_analysis_service = InterestAnalysisService()
