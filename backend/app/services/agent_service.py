from typing import List, Dict, Any, Optional, Callable
import asyncio
import json
import importlib
import re
from app.core.logger import get_logger
from app.services.llm_service import llm_service
import app.core.prompts as prompts

# 创建日志器
logger = get_logger("agent_service")

class Agent:
    """智能体基类"""

    def __init__(self, name: str, role: str, llm_service=None):
        """初始化智能体"""
        self.name = name
        self.role = role
        self.llm_service = llm_service
        self.memory = []
        logger.info(f"创建智能体: {name}, 角色: {role}")

    async def act(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """执行任务"""
        raise NotImplementedError("子类必须实现act方法")

    def add_to_memory(self, message: Dict[str, Any]):
        """添加消息到记忆"""
        self.memory.append(message)
        # 限制记忆大小
        if len(self.memory) > 10:
            self.memory.pop(0)

class ResearchAgent(Agent):
    """研究智能体，负责文献搜索和分析"""

    def __init__(self, llm_service=None):
        super().__init__("Research Agent", "academic_researcher", llm_service)

    async def act(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """执行研究任务"""
        context = context or {}

        # 构建提示
        system_prompt = f"""你是一个学术研究专家。你的任务是分析以下研究任务并提供详细的研究计划。

任务: {task}

背景信息:
{json.dumps(context, ensure_ascii=False)}

请提供以下内容:
1. 研究问题的明确定义
2. 关键搜索词和短语
3. 需要探索的主要研究领域
4. 可能的研究方法
5. 预期的研究成果

请以JSON格式返回结果:
{{
  "research_question": "研究问题",
  "search_terms": ["关键词1", "关键词2", ...],
  "research_areas": ["领域1", "领域2", ...],
  "methodology": "研究方法",
  "expected_outcomes": "预期成果"
}}"""

        # 调用LLM
        response = await self.llm_service.acompletion(
            messages=[{"role": "system", "content": system_prompt}],
            max_tokens=1000,
            temperature=0.4
        )

        # 解析响应
        content = response.choices[0].message.content

        # 尝试解析JSON
        try:
            result = json.loads(content)
            logger.info(f"研究智能体完成任务: {task[:50]}...")

            # 添加到记忆
            self.add_to_memory({
                "task": task,
                "result": result
            })

            return result
        except json.JSONDecodeError:
            logger.error(f"无法解析LLM响应为JSON: {content}")
            # 尝试提取JSON部分
            import re
            json_match = re.search(r'({[\s\S]*})', content)
            if json_match:
                try:
                    result = json.loads(json_match.group(1))
                    logger.info(f"研究智能体完成任务: {task[:50]}...")

                    # 添加到记忆
                    self.add_to_memory({
                        "task": task,
                        "result": result
                    })

                    return result
                except:
                    pass

            # 如果仍然失败，返回原始内容
            return {"content": content}

class WritingAgent(Agent):
    """写作智能体，负责内容生成"""

    def __init__(self, llm_service=None):
        super().__init__("Writing Agent", "academic_writer", llm_service)

    async def act(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """执行写作任务"""
        context = context or {}

        # 构建提示
        system_prompt = f"""你是一个学术写作专家。你的任务是根据以下要求生成高质量的学术内容。

任务: {task}

背景信息:
{json.dumps(context, ensure_ascii=False)}

请生成符合学术标准的内容，要求:
1. 语言专业、准确
2. 结构清晰、逻辑严密
3. 适当引用相关文献
4. 符合学术写作规范

请直接返回生成的内容，不需要额外的解释或格式。"""

        # 调用LLM
        response = await self.llm_service.acompletion(
            messages=[{"role": "system", "content": system_prompt}],
            max_tokens=2000,
            temperature=0.3
        )

        # 获取响应内容
        content = response.choices[0].message.content

        logger.info(f"写作智能体完成任务: {task[:50]}...")

        # 添加到记忆
        self.add_to_memory({
            "task": task,
            "content": content[:100] + "..."
        })

        return {"content": content}

class EditingAgent(Agent):
    """编辑智能体，负责内容优化"""

    def __init__(self, llm_service=None):
        super().__init__("Editing Agent", "academic_editor", llm_service)

    async def act(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """执行编辑任务"""
        context = context or {}
        content = context.get("content", "")

        # 构建提示
        system_prompt = f"""你是一个学术编辑专家。你的任务是优化以下学术内容。

任务: {task}

原始内容:
{content}

请优化内容，要求:
1. 改进语言表达，使其更加专业、准确
2. 确保逻辑连贯，结构清晰
3. 修正语法、拼写和标点错误
4. 保持学术风格和专业性

请直接返回优化后的内容，不需要额外的解释或格式。"""

        # 调用LLM
        response = await self.llm_service.acompletion(
            messages=[{"role": "system", "content": system_prompt}],
            max_tokens=2000,
            temperature=0.2
        )

        # 获取响应内容
        improved_content = response.choices[0].message.content

        logger.info(f"编辑智能体完成任务: {task[:50]}...")

        # 添加到记忆
        self.add_to_memory({
            "task": task,
            "original_length": len(content),
            "improved_length": len(improved_content)
        })

        return {"content": improved_content}

class AgentCoordinator:
    """智能体协调器，负责协调多个智能体的工作"""

    def __init__(self):
        """初始化协调器"""
        self.agents = {}
        self.llm_service = llm_service
        logger.info("创建智能体协调器")

        # 注册默认智能体
        self.register_agent("research", ResearchAgent(llm_service))
        self.register_agent("writing", WritingAgent(llm_service))
        self.register_agent("editing", EditingAgent(llm_service))

    def register_agent(self, agent_id: str, agent: Agent):
        """注册智能体"""
        self.agents[agent_id] = agent
        logger.info(f"注册智能体: {agent_id}, 名称: {agent.name}")

    def _clean_json_response(self, content: str) -> str:
        """清理LLM响应中的Markdown代码块标记"""
        # 移除可能的Markdown代码块标记
        # 匹配```json和```之间的内容
        json_block_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', content)
        if json_block_match:
            # 返回代码块内的内容
            return json_block_match.group(1).strip()
        # 如果没有代码块标记，返回原始内容
        return content

    def _get_prompt_template(self, agent_id: str, task: str) -> str:
        """获取提示模板"""
        try:
            # 根据智能体ID和任务名称构建提示模板变量名
            if agent_id == "research":
                module_name = "research_agent_prompts"
            elif agent_id == "writing":
                module_name = "writing_agent_prompts"
            elif agent_id == "editing":
                module_name = "editing_agent_prompts"
            else:
                logger.error(f"未知的智能体ID: {agent_id}")
                return ""

            # 获取提示模板
            module = importlib.import_module(f"app.core.prompts.{module_name}")
            template_name = task.upper()
            if hasattr(module, template_name):
                return getattr(module, template_name)
            else:
                logger.error(f"未找到提示模板: {template_name}")
                return ""
        except Exception as e:
            logger.error(f"获取提示模板失败: {str(e)}")
            return ""

    async def run_agent(self, agent_id: str, task: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """运行指定智能体的任务"""
        if agent_id not in self.agents:
            raise ValueError(f"未找到智能体: {agent_id}")

        agent = self.agents[agent_id]
        logger.info(f"运行智能体 {agent.name} 执行任务: {task}")

        # 根据任务获取提示模板
        prompt_template = self._get_prompt_template(agent_id, task)
        if not prompt_template:
            logger.error(f"未找到提示模板: {agent_id}.{task}")
            return {}

        # 填充提示模板
        try:
            prompt = prompt_template.format(**params)
        except KeyError as e:
            logger.error(f"填充提示模板失败，缺少参数: {str(e)}")
            return {}

        # 调用LLM
        response = await self.llm_service.acompletion(
            messages=[
                {"role": "system", "content": f"你是一个{agent.role}。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.5
        )

        # 解析响应
        content = response.choices[0].message.content

        # 处理可能的Markdown代码块
        content = self._clean_json_response(content)

        # 解析JSON
        try:
            result = json.loads(content)
            logger.info(f"智能体 {agent.name} 成功完成任务: {task}")
            return result
        except json.JSONDecodeError:
            logger.error(f"无法解析智能体响应为JSON: {content}")
            # 尝试提取JSON部分
            json_match = re.search(r'({[\s\S]*})', content)
            if json_match:
                try:
                    result = json.loads(json_match.group(1))
                    logger.info(f"成功从文本中提取智能体响应")
                    return result
                except:
                    pass

            # 如果仍然失败，返回空字典
            return {}

    async def delegate_task(self, agent_id: str, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """委派任务给指定智能体"""
        if agent_id not in self.agents:
            logger.error(f"未找到智能体: {agent_id}")
            return {"error": f"未找到智能体: {agent_id}"}

        logger.info(f"委派任务给智能体 {agent_id}: {task[:50]}...")
        return await self.agents[agent_id].act(task, context)

    async def execute_workflow(self, workflow: List[Dict[str, Any]], initial_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """执行工作流"""
        context = initial_context or {}
        results = []

        for step in workflow:
            agent_id = step.get("agent")
            task = step.get("task")

            if not agent_id or not task:
                logger.error("工作流步骤缺少agent或task")
                continue

            # 执行任务
            step_result = await self.delegate_task(agent_id, task, context)

            # 更新上下文
            context.update(step_result)

            # 记录结果
            results.append({
                "agent": agent_id,
                "task": task,
                "result": step_result
            })

        return {
            "workflow_results": results,
            "final_context": context
        }

    async def plan_and_execute(self, goal: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """规划并执行任务"""
        # 首先使用LLM生成工作流
        workflow = await self._generate_workflow(goal, context)

        # 然后执行工作流
        return await self.execute_workflow(workflow, context)

    async def _generate_workflow(self, goal: str, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """生成工作流"""
        context = context or {}

        # 构建提示
        system_prompt = f"""你是一个任务规划专家。你的任务是为以下目标生成一个工作流。

目标: {goal}

背景信息:
{json.dumps(context, ensure_ascii=False)}

可用的智能体:
1. research - 研究智能体，擅长文献搜索和分析
2. writing - 写作智能体，擅长内容生成
3. editing - 编辑智能体，擅长内容优化

请生成一个工作流，包含多个步骤，每个步骤指定使用哪个智能体执行什么任务。

请以JSON格式返回结果:
{{
  "workflow": [
    {{
      "agent": "智能体ID",
      "task": "任务描述"
    }},
    ...
  ]
}}"""

        # 调用LLM
        response = await self.llm_service.acompletion(
            messages=[{"role": "system", "content": system_prompt}],
            max_tokens=1000,
            temperature=0.4
        )

        # 解析响应
        content = response.choices[0].message.content

        # 尝试解析JSON
        try:
            result = json.loads(content)
            workflow = result.get("workflow", [])
            logger.info(f"生成工作流: {len(workflow)} 个步骤")
            return workflow
        except json.JSONDecodeError:
            logger.error(f"无法解析LLM响应为JSON: {content}")
            # 尝试提取JSON部分
            import re
            json_match = re.search(r'({[\s\S]*})', content)
            if json_match:
                try:
                    result = json.loads(json_match.group(1))
                    workflow = result.get("workflow", [])
                    logger.info(f"生成工作流: {len(workflow)} 个步骤")
                    return workflow
                except:
                    pass

            # 如果仍然失败，返回空工作流
            logger.warning("无法生成工作流，返回默认工作流")
            return [
                {"agent": "research", "task": f"研究: {goal}"},
                {"agent": "writing", "task": f"写作: {goal}"},
                {"agent": "editing", "task": f"编辑: {goal}"}
            ]

# 创建全局智能体协调器实例
agent_coordinator = AgentCoordinator()
