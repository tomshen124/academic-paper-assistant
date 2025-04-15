class LiteratureSearchService:
    def __init__(self, search_engines: List[str]):
        self.engines = search_engines  # Google Scholar, CNKI, Web of Science等
        
    async def search_references(self, outline: Dict) -> Dict[str, List]:
        """按章节搜索相关文献"""
        references = {}
        for section in outline['sections']:
            papers = await self._search_multi_engines(section['keywords'])
            references[section['id']] = await self._filter_and_rank(papers)
        return references
        
    async def generate_citations(self, papers: List[Dict], style: str) -> List[str]:
        """生成引用格式"""
        return [self._format_citation(paper, style) for paper in papers]