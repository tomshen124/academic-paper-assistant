from typing import List, Dict, Any
from pathlib import Path
from app.core.settings import settings
from app.utils.logger import logger
from .llm import llm_service
from .embedding import embedding_service

class PaperAnalysisAgent:
    """论文分析Agent"""
    
    def __init__(self):
        self.config = settings.ai_config['agents']['paper_analysis']
        self.tasks = self.config['tasks']
        self._load_prompts()
        
    def _load_prompts(self):
        """加载prompt模板"""
        self.prompts = {}
        for task in self.tasks:
            template_path = Path(task['prompt_template'])
            if not template_path.exists():
                raise FileNotFoundError(f"Prompt template not found: {template_path}")
            
            with open(template_path) as f:
                self.prompts[task['name']] = f.read()
    
    async def analyze_paper(self, paper_content: str) -> Dict[str, Any]:
        """分析论文内容"""
        try:
            results = {}
            
            # 1. 提取元数据
            metadata = await self._run_task(
                "metadata_extraction",
                paper_content
            )
            results['metadata'] = metadata
            
            # 2. 分析主要内容
            content_analysis = await self._run_task(
                "content_analysis",
                paper_content,
                context=metadata
            )
            results['content_analysis'] = content_analysis
            
            # 3. 识别创新点
            innovation_points = await self._run_task(
                "innovation_points",
                paper_content,
                context=content_analysis
            )
            results['innovation_points'] = innovation_points
            
            # 4. 分析相关工作
            related_works = await self._run_task(
                "related_works",
                paper_content,
                context=content_analysis
            )
            results['related_works'] = related_works
            
            return {
                'success': True,
                'data': results
            }
            
        except Exception as e:
            logger.error(f"Paper analysis failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _run_task(
        self,
        task_name: str,
        content: str,
        context: Dict[str, Any] = None
    ) -> Any:
        """执行单个分析任务"""
        prompt_template = self.prompts[task_name]
        
        # 构建prompt
        prompt = prompt_template.format(
            content=content,
            **(context or {})
        )
        
        # 调用LLM
        response = await llm_service.generate(
            prompt=prompt,
            temperature=0.3  # 分析任务使用较低的temperature
        )
        
        if not response.success:
            raise Exception(f"Task {task_name} failed: {response.message}")
            
        return response.data
    
    async def get_similar_papers(
        self,
        paper_content: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """查找相似论文"""
        # 获取论文的向量表示
        embedding = await embedding_service.get_embedding(paper_content)
        
        # 在向量数据库中查找相似论文
        similar_papers = await embedding_service.search_similar(
            embedding,
            limit=limit
        )
        
        return similar_papers

# 全局Agent实例
paper_agent = PaperAnalysisAgent()