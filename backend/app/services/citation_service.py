from typing import List, Dict, Any, Optional
import asyncio
import json
import re
from app.core.logger import get_logger
from app.services.llm_service import llm_service

# 创建日志器
logger = get_logger("citation_service")

class CitationService:
    """引用服务"""
    
    def __init__(self):
        """初始化引用服务"""
        self.llm_service = llm_service
        self.citation_styles = {
            "apa": "APA (American Psychological Association) 第7版",
            "mla": "MLA (Modern Language Association) 第8版",
            "chicago": "Chicago 第17版",
            "harvard": "Harvard 引用格式",
            "ieee": "IEEE 引用格式",
            "vancouver": "Vancouver 引用格式"
        }
        logger.info("引用服务初始化完成")
    
    async def format_citations(
        self, 
        content: str, 
        literature: List[Dict[str, Any]], 
        style: str = "apa"
    ) -> Dict[str, Any]:
        """格式化引用"""
        try:
            logger.info(f"格式化引用: 样式={style}, 文献数量={len(literature)}")
            
            # 获取引用样式
            citation_style = self.citation_styles.get(style.lower(), self.citation_styles["apa"])
            
            # 构建提示
            system_prompt = f"""你是一个学术引用格式化专家。你的任务是识别文本中的引用并按照指定格式规范化。

引用样式: {citation_style}

文本内容:
{content}

可用文献:
{json.dumps(literature, ensure_ascii=False)}

请执行以下任务:
1. 识别文本中的引用（通常是作者名和年份的组合，如"Smith (2020)"或"(Smith, 2020)"）
2. 将这些引用与提供的文献列表匹配
3. 确保所有引用都符合{citation_style}格式
4. 生成规范的参考文献列表

请返回以下JSON格式:
{{
  "formatted_content": "格式化后的内容",
  "references": [
    {{
      "id": "引用ID",
      "formatted_citation": "格式化的引用文本",
      "original_text": "原始引用文本"
    }},
    ...
  ],
  "bibliography": [
    "参考文献1",
    "参考文献2",
    ...
  ]
}}"""

            # 调用LLM
            response = await self.llm_service.acompletion(
                messages=[{"role": "system", "content": system_prompt}],
                max_tokens=2000,
                temperature=0.3
            )
            
            # 解析响应
            content = response.choices[0].message.content
            
            # 尝试解析JSON
            try:
                result = json.loads(content)
                logger.info(f"成功格式化引用，识别到 {len(result.get('references', []))} 个引用")
                return result
            except json.JSONDecodeError:
                logger.error(f"无法解析LLM响应为JSON: {content}")
                # 尝试提取JSON部分
                import re
                json_match = re.search(r'({[\s\S]*})', content)
                if json_match:
                    try:
                        result = json.loads(json_match.group(1))
                        logger.info(f"成功从文本中提取格式化引用，识别到 {len(result.get('references', []))} 个引用")
                        return result
                    except:
                        pass
                
                # 如果仍然失败，返回原始内容
                return {
                    "formatted_content": content,
                    "references": [],
                    "bibliography": []
                }
                
        except Exception as e:
            logger.error(f"格式化引用失败: {str(e)}")
            return {
                "formatted_content": content,
                "references": [],
                "bibliography": [],
                "error": str(e)
            }
    
    async def extract_citations(
        self, 
        content: str
    ) -> List[Dict[str, Any]]:
        """从内容中提取引用"""
        try:
            logger.info(f"从内容中提取引用")
            
            # 构建提示
            system_prompt = f"""你是一个学术引用提取专家。你的任务是从文本中识别并提取所有引用。

文本内容:
{content}

请识别文本中的所有引用，包括:
1. 作者-年份格式的引用，如"Smith (2020)"或"(Smith, 2020)"
2. 数字格式的引用，如"[1]"或"[1,2]"
3. 脚注格式的引用，如上标数字或符号

对于每个识别到的引用，请提取:
1. 引用文本：原始引用的完整文本
2. 引用位置：引用在文本中的大致位置（开头、中间、结尾）
3. 可能的作者：如果能识别，提取作者名
4. 可能的年份：如果能识别，提取发表年份

请以JSON格式返回结果:
{{
  "citations": [
    {{
      "text": "引用文本",
      "position": "引用位置",
      "author": "可能的作者",
      "year": "可能的年份"
    }},
    ...
  ],
  "total_count": 引用总数
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
                citations = result.get("citations", [])
                logger.info(f"成功提取引用，共 {len(citations)} 个")
                return citations
            except json.JSONDecodeError:
                logger.error(f"无法解析LLM响应为JSON: {content}")
                # 尝试提取JSON部分
                import re
                json_match = re.search(r'({[\s\S]*})', content)
                if json_match:
                    try:
                        result = json.loads(json_match.group(1))
                        citations = result.get("citations", [])
                        logger.info(f"成功从文本中提取引用，共 {len(citations)} 个")
                        return citations
                    except:
                        pass
                
                # 如果仍然失败，返回空列表
                return []
                
        except Exception as e:
            logger.error(f"提取引用失败: {str(e)}")
            return []
    
    async def generate_bibliography(
        self, 
        literature: List[Dict[str, Any]], 
        style: str = "apa"
    ) -> List[str]:
        """生成参考文献列表"""
        try:
            logger.info(f"生成参考文献列表: 样式={style}, 文献数量={len(literature)}")
            
            # 获取引用样式
            citation_style = self.citation_styles.get(style.lower(), self.citation_styles["apa"])
            
            # 构建提示
            system_prompt = f"""你是一个学术参考文献格式化专家。你的任务是将提供的文献信息格式化为规范的参考文献列表。

引用样式: {citation_style}

文献列表:
{json.dumps(literature, ensure_ascii=False)}

请将每篇文献格式化为{citation_style}格式的参考文献。对于每篇文献，请考虑以下信息（如果可用）:
1. 作者
2. 标题
3. 出版年份
4. 期刊/出版物名称
5. 卷号和期号
6. 页码
7. DOI或URL
8. 其他相关信息

请以JSON格式返回结果:
{{
  "bibliography": [
    "参考文献1",
    "参考文献2",
    ...
  ]
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
                bibliography = result.get("bibliography", [])
                logger.info(f"成功生成参考文献列表，共 {len(bibliography)} 条")
                return bibliography
            except json.JSONDecodeError:
                logger.error(f"无法解析LLM响应为JSON: {content}")
                # 尝试提取JSON部分
                import re
                json_match = re.search(r'({[\s\S]*})', content)
                if json_match:
                    try:
                        result = json.loads(json_match.group(1))
                        bibliography = result.get("bibliography", [])
                        logger.info(f"成功从文本中提取参考文献列表，共 {len(bibliography)} 条")
                        return bibliography
                    except:
                        pass
                
                # 如果仍然失败，尝试直接提取每行作为一个参考文献
                lines = content.strip().split("\n")
                filtered_lines = [line for line in lines if line.strip() and not line.startswith("{") and not line.startswith("}")]
                if filtered_lines:
                    logger.info(f"通过行分割提取参考文献列表，共 {len(filtered_lines)} 条")
                    return filtered_lines
                
                # 如果仍然失败，返回空列表
                return []
                
        except Exception as e:
            logger.error(f"生成参考文献列表失败: {str(e)}")
            return []
    
    def get_citation_styles(self) -> Dict[str, str]:
        """获取支持的引用样式"""
        return self.citation_styles

# 创建全局引用服务实例
citation_service = CitationService()
