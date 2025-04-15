from typing import Dict, Any, List
import httpx
import json
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger()

class LLMService:
    """大模型服务类,处理所有文本分析和知识抽取任务"""
    
    def __init__(self):
        self.api_url = settings.DEEPSEEK_API_URL
        self.api_key = settings.DEEPSEEK_API_KEY
        self.model = settings.DEEPSEEK_MODEL
        self.temperature = settings.LLM_TEMPERATURE
        self.max_tokens = settings.LLM_MAX_TOKENS

    async def analyze_text(self, text: str, task_type: str = "knowledge_extract") -> Dict[str, Any]:
        """分析文本内容"""
        try:
            # 文本分块处理
            chunks = self._split_text(text)
            logger.info(f"文本已分割为 {len(chunks)} 个块")
            
            all_results = []
            for i, chunk in enumerate(chunks):
                logger.info(f"处理第 {i+1}/{len(chunks)} 个文本块")
                try:
                    # 根据任务类型选择合适的提示词
                    system_prompt = self._get_system_prompt(task_type)
                    user_prompt = self._get_user_prompt(task_type, chunk)

                    # 调用API
                    async with httpx.AsyncClient(timeout=60.0) as client:
                        response = await client.post(
                            self.api_url,
                            headers={
                                "Authorization": f"Bearer {self.api_key}",
                                "Content-Type": "application/json"
                            },
                            json={
                                "model": self.model,
                                "messages": [
                                    {"role": "system", "content": system_prompt},
                                    {"role": "user", "content": user_prompt}
                                ],
                                "temperature": self.temperature,
                                "max_tokens": self.max_tokens
                            }
                        )

                        if response.status_code != 200:
                            logger.error(f"API调用失败: {response.text}")
                            continue

                        result = response.json()
                        content = result['choices'][0]['message']['content']

                        # 解析JSON响应
                        try:
                            chunk_result = json.loads(content)
                            all_results.append(chunk_result)
                        except json.JSONDecodeError as e:
                            logger.error(f"JSON解析失败: {str(e)}")
                            continue

                except Exception as e:
                    logger.error(f"处理文本块失败: {str(e)}")
                    continue

            # 合并所有结果
            return self._merge_results(all_results, task_type)

        except Exception as e:
            logger.error(f"文本分析失败: {str(e)}")
            return self._get_empty_result(task_type)

    def _split_text(self, text: str) -> List[str]:
        """将文本分割成小块"""
        chunk_size = settings.TEXT_CHUNK_SIZE
        overlap_size = settings.TEXT_OVERLAP_SIZE
        
        if len(text) <= chunk_size:
            return [text]
            
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            if end > len(text):
                end = len(text)
            
            # 找到合适的分割点（句号或换行符）
            if end < len(text):
                for i in range(min(end + 100, len(text)), end - 100, -1):
                    if text[i] in ['。', '\n', '.']:
                        end = i + 1
                        break
            
            chunks.append(text[start:end])
            start = end - overlap_size
            
        return chunks

    def _merge_results(self, results: List[Dict[str, Any]], task_type: str) -> Dict[str, Any]:
        """合并多个文本块的分析结果"""
        if not results:
            return self._get_empty_result(task_type)
            
        merged = {
            "entities": [],
            "relationships": [],
            "metadata": {
                "summary": "",
                "topics": []
            }
        }
        
        # 使用集合去重
        entities_set = set()
        relationships_set = set()
        topics_set = set()
        summaries = []
        
        for result in results:
            # 合并实体
            for entity in result.get("entities", []):
                entity_key = f"{entity['name']}:{entity['type']}"
                if entity_key not in entities_set:
                    entities_set.add(entity_key)
                    merged["entities"].append(entity)
            
            # 合并关系
            for rel in result.get("relationships", []):
                rel_key = f"{rel['source']}:{rel['type']}:{rel['target']}"
                if rel_key not in relationships_set:
                    relationships_set.add(rel_key)
                    merged["relationships"].append(rel)
            
            # 合并主题
            for topic in result.get("metadata", {}).get("topics", []):
                topics_set.add(topic)
            
            # 收集摘要
            summary = result.get("metadata", {}).get("summary")
            if summary:
                summaries.append(summary)
        
        # 合并主题和摘要
        merged["metadata"]["topics"] = list(topics_set)
        merged["metadata"]["summary"] = " ".join(summaries) if summaries else ""
        
        return merged

    def _get_system_prompt(self, task_type: str) -> str:
        """获取系统提示词"""
        from app.core.prompts import (
            KNOWLEDGE_EXTRACT_SYSTEM_PROMPT,
            TEXT_CLASSIFICATION_SYSTEM_PROMPT,
            RELATION_EXTRACT_SYSTEM_PROMPT,
            ENTITY_RECOGNITION_SYSTEM_PROMPT
        )
        
        prompts = {
            "knowledge_extract": KNOWLEDGE_EXTRACT_SYSTEM_PROMPT,
            "text_classification": TEXT_CLASSIFICATION_SYSTEM_PROMPT,
            "relation_extract": RELATION_EXTRACT_SYSTEM_PROMPT,
            "entity_recognition": ENTITY_RECOGNITION_SYSTEM_PROMPT
        }
        
        return prompts.get(task_type, KNOWLEDGE_EXTRACT_SYSTEM_PROMPT)

    def _get_user_prompt(self, task_type: str, text: str) -> str:
        """获取用户提示词"""
        from app.core.prompts import (
            KNOWLEDGE_EXTRACT_USER_PROMPT_TEMPLATE,
            TEXT_CLASSIFICATION_USER_PROMPT_TEMPLATE,
            RELATION_EXTRACT_USER_PROMPT_TEMPLATE,
            ENTITY_RECOGNITION_USER_PROMPT_TEMPLATE
        )
        
        templates = {
            "knowledge_extract": KNOWLEDGE_EXTRACT_USER_PROMPT_TEMPLATE,
            "text_classification": TEXT_CLASSIFICATION_USER_PROMPT_TEMPLATE,
            "relation_extract": RELATION_EXTRACT_USER_PROMPT_TEMPLATE,
            "entity_recognition": ENTITY_RECOGNITION_USER_PROMPT_TEMPLATE
        }
        
        template = templates.get(task_type, KNOWLEDGE_EXTRACT_USER_PROMPT_TEMPLATE)
        return template.format(text=text)

    def _get_empty_result(self, task_type: str) -> Dict[str, Any]:
        """获取空结果"""
        empty_results = {
            "knowledge_extract": {
                "entities": [],
                "relationships": [],
                "metadata": {"summary": "", "topics": []}
            },
            "text_classification": {
                "categories": [],
                "confidence_scores": []
            },
            "relation_extract": {
                "relations": []
            },
            "entity_recognition": {
                "entities": []
            }
        }
        
        return empty_results.get(task_type, {"error": "未知的任务类型"}) 