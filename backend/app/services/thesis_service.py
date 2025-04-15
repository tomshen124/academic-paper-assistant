from app.core.llm.controller import ControllerAgent
from app.core.llm.agents import WritingAgent, ReviewAgent, LiteratureAgent
from app.core.logger import get_logger

logger = get_logger()

class ThesisService:
    def __init__(self, llm_provider):
        self.controller = ControllerAgent(llm_provider)
        
        # 初始化专门的agents
        self.agents = {
            "writing": WritingAgent(llm_provider),
            "review": ReviewAgent(llm_provider),
            "literature": LiteratureAgent(llm_provider)
        }
    
    async def generate_thesis_section(self, request: Dict) -> Dict:
        """生成论文章节"""
        try:
            # 1. 规划任务
            plan_result = await self.controller.plan_task({
                "title": request.get("title"),
                "type": request.get("section_type"),
                "requirements": request.get("requirements"),
                "references": request.get("references")
            })
            
            # 2. 检查成本是否在预算范围内
            if plan_result["estimated_cost"] > request.get("max_cost", float("inf")):
                raise ValueError(f"预估成本 ${plan_result['estimated_cost']} 超出预算")
            
            # 3. 执行计划
            result = await self.controller.execute_plan(
                plan_result["plan"],
                self.agents
            )
            
            # 4. 记录执行情况
            logger.info(
                f"任务完成: {request.get('title')} - "
                f"Token使用: {result['token_usage']['total_tokens']}, "
                f"耗时: {result['execution_time']}秒"
            )
            
            return {
                "content": result["results"],
                "metrics": {
                    "token_usage": result["token_usage"],
                    "execution_time": result["execution_time"],
                    "cost": estimate_cost(result["token_usage"])
                }
            }
            
        except Exception as e:
            logger.error(f"生成论文章节失败: {str(e)}")
            raise