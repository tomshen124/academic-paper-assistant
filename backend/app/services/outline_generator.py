class OutlineGeneratorService:
    def __init__(self, llm_service):
        self.llm = llm_service
        
    async def generate_outline(self, topic: str, requirements: Dict) -> Dict:
        """生成论文提纲"""
        # 基于主题和要求生成提纲
        base_outline = await self.llm.generate_base_outline(topic, requirements)
        # 优化提纲结构
        refined_outline = await self.llm.refine_outline(base_outline)
        # 添加每个章节的要点建议
        return await self.llm.add_section_suggestions(refined_outline)