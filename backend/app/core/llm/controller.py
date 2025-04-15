from typing import Dict, List, Any
from datetime import datetime
from app.core.logger import get_logger
from .base import LLMProvider, LLMMessage
from .token_counter import count_tokens, estimate_cost

logger = get_logger()

class ControllerAgent:
    """主控Agent,负责任务分发和协调"""
    
    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider
        self.token_usage = {
            "total_tokens": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0
        }
        self._init_system_prompt()
    
    def _init_system_prompt(self):
        """初始化系统提示词"""
        self.system_prompt = """你是一个智能写作系统的主控制器。你的职责是:
1. 理解用户的写作需求
2. 将任务分解为子任务
3. 决定调用哪些专门的Agent
4. 协调各个Agent的工作
5. 整合最终结果

你需要以JSON格式返回任务分配方案,包含:
- task_type: 任务类型
- sub_tasks: 子任务列表
- assigned_agents: 分配的agent
- execution_order: 执行顺序
- expected_tokens: 预估token使用量"""
    
    async def plan_task(self, task: Dict) -> Dict:
        """规划任务执行方案"""
        messages = [
            LLMMessage(role="system", content=self.system_prompt),
            LLMMessage(role="user", content=str(task))
        ]
        
        # 记录开始时间
        start_time = datetime.now()
        logger.info(f"开始规划任务: {task.get('title', 'Untitled')}")
        
        try:
            response = await self.llm.chat_completion(
                messages=messages,
                model="gpt-4",  # 使用高级模型来做决策
                temperature=0.3
            )
            
            # 更新token使用统计
            self._update_token_usage(response.usage)
            
            # 解析执行方案
            plan = self._parse_plan(response.content)
            
            # 估算成本
            estimated_cost = estimate_cost(plan["expected_tokens"])
            
            logger.info(f"任务规划完成,预估token: {plan['expected_tokens']}, 成本: ${estimated_cost:.4f}")
            
            return {
                "plan": plan,
                "estimated_cost": estimated_cost,
                "execution_time": (datetime.now() - start_time).total_seconds()
            }
            
        except Exception as e:
            logger.error(f"任务规划失败: {str(e)}")
            raise
    
    async def execute_plan(self, plan: Dict, agents: Dict[str, Any]) -> Dict:
        """执行任务计划"""
        results = {}
        start_time = datetime.now()
        
        try:
            for step in plan["execution_order"]:
                agent_name = step["agent"]
                task = step["task"]
                
                logger.info(f"执行步骤: {task}, 使用Agent: {agent_name}")
                
                if agent_name not in agents:
                    raise ValueError(f"未找到Agent: {agent_name}")
                
                # 执行任务并记录token使用
                result = await agents[agent_name].execute(task)
                self._update_token_usage(result["usage"])
                
                results[task] = result["content"]
                
            return {
                "results": results,
                "token_usage": self.token_usage,
                "execution_time": (datetime.now() - start_time).total_seconds()
            }
            
        except Exception as e:
            logger.error(f"计划执行失败: {str(e)}")
            raise
    
    def _update_token_usage(self, usage: Dict):
        """更新token使用统计"""
        for key in usage:
            self.token_usage[key] = self.token_usage.get(key, 0) + usage[key]