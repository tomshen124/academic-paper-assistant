class DraftGeneratorService:
    def __init__(self, llm_service, literature_service):
        self.llm = llm_service
        self.literature = literature_service
        
    async def generate_draft(self, outline: Dict, references: Dict) -> Dict:
        """生成论文初稿"""
        # 按章节生成内容
        sections = {}
        for section in outline['sections']:
            content = await self._generate_section_content(
                section,
                references[section['id']]
            )
            sections[section['id']] = content
            
        # 生成摘要和关键词
        abstract = await self.llm.generate_abstract(sections)
        
        return {
            'abstract': abstract,
            'sections': sections,
            'references': await self.literature.generate_citations(references)
        }
        
    async def _generate_section_content(self, section: Dict, refs: List) -> str:
        """生成单个章节的内容"""
        # 提取参考文献的关键信息
        ref_points = await self.llm.extract_key_points(refs)
        # 组织和生成内容
        return await self.llm.generate_content(section['outline'], ref_points)