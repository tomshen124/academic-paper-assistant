from typing import Dict, Any
from app.core.logger import get_logger
from app.services.agent_service import agent_coordinator
from app.services.llm_service import llm_service
from app.services.llm.token_counter import estimate_cost

logger = get_logger("thesis_service")

class ThesisService:
    def __init__(self):
        """初始化论文服务"""
        self.agent_coordinator = agent_coordinator
        logger.info("论文服务初始化完成")

    async def generate_thesis_section(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """生成论文章节"""
        try:
            # 1. 使用规划智能体生成工作流
            workflow = await self.agent_coordinator.plan_and_execute(
                f"生成论文章节: {request.get('title')}",
                {
                    "title": request.get("title"),
                    "section_type": request.get("section_type"),
                    "requirements": request.get("requirements"),
                    "references": request.get("references")
                }
            )

            # 2. 获取最终结果
            final_context = workflow.get("final_context", {})
            content = final_context.get("content", "")

            # 3. 获取token使用情况
            token_usage = llm_service.get_token_usage()
            execution_time = sum([step.get("result", {}).get("execution_time", 0)
                                for step in workflow.get("workflow_results", [])])

            # 4. 记录执行情况
            logger.info(
                f"任务完成: {request.get('title')} - "
                f"Token使用: {token_usage.get('total_tokens', 0)}, "
                f"耗时: {execution_time}秒"
            )

            return {
                "content": content,
                "metrics": {
                    "token_usage": token_usage,
                    "execution_time": execution_time,
                    "cost": estimate_cost(token_usage)
                }
            }

        except Exception as e:
            logger.error(f"生成论文章节失败: {str(e)}")
            raise