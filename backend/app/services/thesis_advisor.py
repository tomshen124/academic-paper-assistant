class ThesisAdvisorService:
    def __init__(self, llm_service, academic_search_service):
        self.llm = llm_service
        self.search = academic_search_service
        
    async def suggest_topics(self, field: str, keywords: List[str]) -> List[Dict]:
        """生成选题建议"""
        # 搜索近期相关研究热点
        recent_papers = await self.search.search_recent_papers(field, keywords)
        # 分析研究趋势
        trends = await self.llm.analyze_research_trends(recent_papers)
        # 生成选题建议
        return await self.llm.generate_topic_suggestions(trends)
        
    async def evaluate_topic(self, topic: str) -> Dict:
        """评估选题可行性"""
        # 分析选题难度、创新性、资料可得性等
        return await self.llm.evaluate_research_topic(topic)