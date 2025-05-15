from typing import List, Dict, Any, Optional, Callable
import asyncio
import json
import importlib
import re
import time
from app.core.logger import get_logger
from app.services.llm_service import llm_service
from app.services.llm.token_counter import estimate_cost

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


class LiteratureAgent(Agent):
    """文献智能体，负责文献分析"""

    def __init__(self, llm_service=None):
        super().__init__("Literature Agent", "literature_researcher", llm_service)

    async def act(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """执行文献分析任务"""
        context = context or {}
        papers = context.get("papers", [])

        # 构建提示
        system_prompt = f"""你是一个学术文献分析专家。你的任务是分析以下学术文献。

任务: {task}

文献列表:
{json.dumps(papers, ensure_ascii=False)}

请提供以下分析:
1. 主要研究主题和趋势
2. 关键发现和结论
3. 研究方法和数据来源
4. 研究差距和未来方向
5. 文献之间的关系和矛盾

请以JSON格式返回结果:
{{
  "main_themes": ["主题1", "主题2", ...],
  "key_findings": ["发现1", "发现2", ...],
  "methodologies": ["方法1", "方法2", ...],
  "research_gaps": ["差距1", "差距2", ...],
  "relationships": "文献关系分析",
  "summary": "总体分析摘要"
}}"""

        # 调用LLM
        response = await self.llm_service.acompletion(
            messages=[{"role": "system", "content": system_prompt}],
            max_tokens=2000,
            temperature=0.4
        )

        # 解析响应
        content = response.choices[0].message.content

        # 尝试解析JSON
        try:
            result = json.loads(content)
            logger.info(f"文献智能体完成任务: {task[:50]}...")

            # 添加到记忆
            self.add_to_memory({
                "task": task,
                "papers_count": len(papers),
                "analysis": result
            })

            return result
        except json.JSONDecodeError:
            logger.error(f"无法解析LLM响应为JSON: {content}")
            # 尝试提取JSON部分
            json_match = re.search(r'({[\s\S]*})', content)
            if json_match:
                try:
                    result = json.loads(json_match.group(1))
                    logger.info(f"文献智能体完成任务: {task[:50]}...")
                    return result
                except:
                    pass

            # 如果仍然失败，返回原始内容
            return {"content": content}


class ReviewAgent(Agent):
    """审阅智能体，负责内容审阅"""

    def __init__(self, llm_service=None):
        super().__init__("Review Agent", "academic_reviewer", llm_service)

    async def act(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """执行审阅任务"""
        context = context or {}
        content = context.get("content", "")
        requirements = context.get("requirements", {})

        # 构建提示
        system_prompt = f"""你是一个学术审阅专家。你的任务是审阅以下学术内容。

任务: {task}

审阅内容:
{content}

审阅要求:
{json.dumps(requirements, ensure_ascii=False)}

请提供以下审阅结果:
1. 内容质量评分(1-10)
2. 主要优点
3. 主要问题
4. 改进建议
5. 是否需要修改(true/false)

请以JSON格式返回结果:
{{
  "quality_score": 评分,
  "strengths": ["优点1", "优点2", ...],
  "issues": ["问题1", "问题2", ...],
  "suggestions": ["建议1", "建议2", ...],
  "needs_revision": true/false,
  "overall_assessment": "总体评价"
}}"""

        # 调用LLM
        response = await self.llm_service.acompletion(
            messages=[{"role": "system", "content": system_prompt}],
            max_tokens=1500,
            temperature=0.3
        )

        # 解析响应
        content = response.choices[0].message.content

        # 尝试解析JSON
        try:
            result = json.loads(content)
            logger.info(f"审阅智能体完成任务: {task[:50]}...")

            # 添加到记忆
            self.add_to_memory({
                "task": task,
                "quality_score": result.get("quality_score", 0),
                "needs_revision": result.get("needs_revision", False)
            })

            return result
        except json.JSONDecodeError:
            logger.error(f"无法解析LLM响应为JSON: {content}")
            # 尝试提取JSON部分
            json_match = re.search(r'({[\s\S]*})', content)
            if json_match:
                try:
                    result = json.loads(json_match.group(1))
                    logger.info(f"审阅智能体完成任务: {task[:50]}...")
                    return result
                except:
                    pass

            # 如果仍然失败，返回原始内容
            return {"content": content}


class OutlineAgent(Agent):
    """提纲智能体，负责生成论文提纲"""

    def __init__(self, llm_service=None):
        super().__init__("Outline Agent", "outline_expert", llm_service)

    async def act(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """执行提纲生成任务"""
        context = context or {}
        topic = context.get("topic", "")
        academic_field = context.get("academic_field", "")
        academic_level = context.get("academic_level", "undergraduate")
        paper_type = context.get("paper_type", "research")
        length = context.get("length", "medium")

        # 构建提示
        system_prompt = f"""你是一个学术提纲专家。你的任务是为以下论文主题生成详细的提纲。

任务: {task}

论文主题: {topic}
学术领域: {academic_field}
学术水平: {academic_level}
论文类型: {paper_type}
论文长度: {length}

请生成一个结构完整、逻辑清晰的学术论文提纲，包括：
1. 标题
2. 摘要结构
3. 关键词建议
4. 章节结构（包括引言、文献综述、方法、结果、讨论、结论等）
5. 每个章节的子部分
6. 每个部分的主要内容和要点

请以JSON格式返回：
{{
    "title": "论文标题",
    "abstract_structure": ["摘要要点1", "摘要要点2"],
    "keywords": ["关键词1", "关键词2"],
    "sections": [
        {{
            "id": "1",
            "title": "章节标题",
            "content": "章节主要内容描述",
            "subsections": [
                {{
                    "id": "1.1",
                    "title": "子章节标题",
                    "content": "子章节主要内容描述"
                }}
            ]
        }}
    ],
    "references_suggestion": "参考文献建议"
}}"""

        # 调用LLM
        response = await self.llm_service.acompletion(
            messages=[{"role": "system", "content": system_prompt}],
            max_tokens=2500,
            temperature=0.4,
            agent_type="outline"  # 使用提纲智能体配置
        )

        # 解析响应
        content = response.choices[0].message.content

        # 尝试解析JSON
        try:
            result = json.loads(content)
            logger.info(f"提纲智能体完成任务: {task[:50]}...")

            # 添加到记忆
            self.add_to_memory({
                "task": task,
                "topic": topic,
                "sections_count": len(result.get("sections", []))
            })

            return result
        except json.JSONDecodeError:
            logger.error(f"无法解析LLM响应为JSON: {content}")
            # 尝试提取JSON部分
            json_match = re.search(r'({[\s\S]*})', content)
            if json_match:
                try:
                    result = json.loads(json_match.group(1))
                    logger.info(f"提纲智能体完成任务: {task[:50]}...")
                    return result
                except:
                    pass

            # 如果仍然失败，返回原始内容
            return {"content": content}


class PaperAgent(Agent):
    """论文智能体，负责生成论文内容"""

    def __init__(self, llm_service=None):
        super().__init__("Paper Agent", "paper_writer", llm_service)

    async def act(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """执行论文生成任务"""
        context = context or {}
        topic = context.get("topic", "")
        outline = context.get("outline", {})
        section_id = context.get("section_id", "")
        literature = context.get("literature", [])

        # 构建提示
        system_prompt = f"""你是一个学术论文写作专家。你的任务是根据以下信息生成论文内容。

任务: {task}

论文主题: {topic}
论文提纲: {json.dumps(outline, ensure_ascii=False)}
章节ID: {section_id}
相关文献: {json.dumps(literature, ensure_ascii=False)}

请生成该章节的完整内容，要求：
1. 学术风格严谨，表达专业
2. 内容充实，论证有力
3. 适当引用相关文献
4. 与整体提纲保持一致
5. 符合学术写作规范

生成内容应包括：
1. 章节标题
2. 章节正文（包括必要的子标题）
3. 引用标记（采用作者-年份格式，如(Smith, 2020)）

请以JSON格式返回：
{{
    "section_id": "章节ID",
    "title": "章节标题",
    "content": "章节完整内容",
    "citations": ["引用1", "引用2"]
}}"""

        # 调用LLM
        response = await self.llm_service.acompletion(
            messages=[{"role": "system", "content": system_prompt}],
            max_tokens=3000,
            temperature=0.3,
            agent_type="writing"  # 使用写作智能体配置
        )

        # 解析响应
        content = response.choices[0].message.content

        # 尝试解析JSON
        try:
            result = json.loads(content)
            logger.info(f"论文智能体完成任务: {task[:50]}...")

            # 添加到记忆
            self.add_to_memory({
                "task": task,
                "section_id": section_id,
                "content_length": len(result.get("content", ""))
            })

            return result
        except json.JSONDecodeError:
            logger.error(f"无法解析LLM响应为JSON: {content}")
            # 尝试提取JSON部分
            json_match = re.search(r'({[\s\S]*})', content)
            if json_match:
                try:
                    result = json.loads(json_match.group(1))
                    logger.info(f"论文智能体完成任务: {task[:50]}...")
                    return result
                except:
                    pass

            # 如果仍然失败，返回原始内容
            return {"content": content}

class AgentCoordinator:
    """智能体协调器，负责协调多个智能体的工作"""

    def __init__(self):
        """初始化协调器"""
        self.agents = {}
        self.llm_service = llm_service
        self.execution_history = []
        self.token_usage = {
            "total_tokens": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0
        }
        logger.info("创建智能体协调器")

        # 注册默认智能体
        self.register_agent("research", ResearchAgent(llm_service))
        self.register_agent("writing", WritingAgent(llm_service))
        self.register_agent("editing", EditingAgent(llm_service))

        # 注册额外的智能体
        self.register_agent("literature", LiteratureAgent(llm_service))
        self.register_agent("review", ReviewAgent(llm_service))
        self.register_agent("outline", OutlineAgent(llm_service))
        self.register_agent("paper", PaperAgent(llm_service))

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
            # 尝试从不同的模块获取提示模板
            module_names = [
                f"{agent_id}_agent_prompts",  # 例如：research_agent_prompts
                f"{agent_id}_prompts",        # 例如：research_prompts
                "agent_prompts"               # 通用智能体提示
            ]

            # 尝试不同的模板名称格式
            template_names = [
                task.upper(),                 # 例如：ANALYZE_RESEARCH_TRENDS
                f"{agent_id.upper()}_{task.upper()}",  # 例如：RESEARCH_ANALYZE_RESEARCH_TRENDS
                task                          # 原始任务名称
            ]

            # 尝试从不同的模块和不同的名称获取提示模板
            for module_name in module_names:
                try:
                    module = importlib.import_module(f"app.core.prompts.{module_name}")

                    for template_name in template_names:
                        if hasattr(module, template_name):
                            logger.info(f"找到提示模板: {module_name}.{template_name}")
                            return getattr(module, template_name)
                except ImportError:
                    continue

            # 如果没有找到提示模板，尝试从默认提示模板中获取
            try:
                default_module = importlib.import_module("app.core.prompts.default_prompts")
                default_template_name = "DEFAULT_PROMPT"

                if hasattr(default_module, default_template_name):
                    logger.warning(f"使用默认提示模板: {default_template_name}")
                    return getattr(default_module, default_template_name)
            except ImportError:
                pass

            logger.error(f"未找到提示模板: {agent_id}.{task}")
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

        # 记录开始时间
        start_time = time.time()

        # 根据任务获取提示模板
        prompt_template = self._get_prompt_template(agent_id, task)
        if not prompt_template:
            logger.warning(f"未找到提示模板: {agent_id}.{task}，使用默认提示")
            # 使用默认提示
            prompt = f"执行任务: {task}\n\n参数: {json.dumps(params, ensure_ascii=False)}"
        else:
            # 填充提示模板
            try:
                prompt = prompt_template.format(**params)
            except KeyError as e:
                logger.error(f"填充提示模板失败，缺少参数: {str(e)}")
                # 使用默认提示
                prompt = f"执行任务: {task}\n\n参数: {json.dumps(params, ensure_ascii=False)}"

        # 调用LLM
        response = await self.llm_service.acompletion(
            messages=[
                {"role": "system", "content": f"你是一个{agent.role}。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.5,
            agent_type=agent_id  # 使用智能体ID作为agent_type
        )

        # 更新token使用统计
        token_usage = response.get("usage", {})
        for key in token_usage:
            self.token_usage[key] = self.token_usage.get(key, 0) + token_usage.get(key, 0)

        # 解析响应
        content = response.choices[0].message.content

        # 处理可能的Markdown代码块
        content = self._clean_json_response(content)

        # 计算执行时间
        execution_time = time.time() - start_time

        # 记录执行历史
        execution_record = {
            "agent_id": agent_id,
            "task": task,
            "params": params,
            "execution_time": execution_time,
            "token_usage": token_usage
        }

        # 解析JSON
        try:
            result = json.loads(content)
            logger.info(f"智能体 {agent.name} 成功完成任务: {task}，耗时: {execution_time:.2f}秒")

            # 添加结果到执行记录
            execution_record["result"] = result
            execution_record["status"] = "success"
            self.execution_history.append(execution_record)

            return result
        except json.JSONDecodeError:
            logger.error(f"无法解析智能体响应为JSON: {content}")
            # 尝试提取JSON部分
            json_match = re.search(r'({[\s\S]*})', content)
            if json_match:
                try:
                    result = json.loads(json_match.group(1))
                    logger.info(f"成功从文本中提取智能体响应")

                    # 添加结果到执行记录
                    execution_record["result"] = result
                    execution_record["status"] = "partial_success"
                    self.execution_history.append(execution_record)

                    return result
                except:
                    pass

            # 如果仍然失败，记录失败并返回空字典
            execution_record["content"] = content
            execution_record["status"] = "failed"
            self.execution_history.append(execution_record)

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

        # 记录开始时间
        start_time = time.time()
        logger.info(f"开始执行工作流: {len(workflow)} 个步骤")

        for i, step in enumerate(workflow):
            agent_id = step.get("agent")
            task = step.get("task")
            params = step.get("params", {})

            if not agent_id or not task:
                logger.error("工作流步骤缺少agent或task")
                continue

            logger.info(f"执行工作流步骤 {i+1}/{len(workflow)}: {agent_id}.{task}")

            # 处理参数中的变量引用
            processed_params = {}
            for key, value in params.items():
                if isinstance(value, str) and value.startswith("$"):
                    # 从上下文中获取变量值
                    var_name = value[1:]
                    if var_name in context:
                        processed_params[key] = context[var_name]
                    else:
                        logger.warning(f"未找到变量: {var_name}")
                        processed_params[key] = value
                else:
                    processed_params[key] = value

            # 合并上下文和处理后的参数
            step_context = {**context, **processed_params}

            # 执行任务
            step_result = await self.delegate_task(agent_id, task, step_context)

            # 更新上下文
            # 使用任务名称作为结果的键
            result_key = f"{task}_result"
            context[result_key] = step_result

            # 同时将结果的各个字段添加到上下文中
            if isinstance(step_result, dict):
                for key, value in step_result.items():
                    context[key] = value

            # 记录结果
            results.append({
                "agent": agent_id,
                "task": task,
                "params": params,
                "result": step_result,
                "execution_time": time.time() - start_time
            })

            # 记录执行历史
            self.execution_history.append({
                "workflow_step": i+1,
                "agent_id": agent_id,
                "task": task,
                "params": params,
                "result_summary": self._get_result_summary(step_result),
                "execution_time": time.time() - start_time
            })

        # 计算总执行时间
        total_execution_time = time.time() - start_time
        logger.info(f"工作流执行完成，耗时: {total_execution_time:.2f}秒")

        return {
            "workflow_results": results,
            "final_context": context,
            "execution_time": total_execution_time
        }

    def _get_result_summary(self, result: Any) -> Dict[str, Any]:
        """获取结果摘要，用于记录执行历史"""
        if isinstance(result, dict):
            summary = {}
            # 提取关键字段
            for key in ["status", "title", "content", "quality_score", "sections_count"]:
                if key in result:
                    if key == "content" and isinstance(result[key], str) and len(result[key]) > 100:
                        # 对于长文本，只保留前100个字符
                        summary[key] = result[key][:100] + "..."
                    else:
                        summary[key] = result[key]
            return summary
        elif isinstance(result, str):
            return {"content": result[:100] + "..." if len(result) > 100 else result}
        else:
            return {"result": str(result)[:100] + "..." if len(str(result)) > 100 else str(result)}

    async def execute_predefined_workflow(self, workflow_type: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """执行预定义的工作流"""
        # 获取预定义工作流
        workflow = self.get_predefined_workflow(workflow_type, params)

        if not workflow:
            logger.error(f"未找到预定义工作流: {workflow_type}")
            return {"error": f"未找到预定义工作流: {workflow_type}"}

        # 执行工作流
        return await self.execute_workflow(workflow, params)

    async def plan_and_execute(self, goal: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """规划并执行任务"""
        # 首先使用LLM生成工作流
        workflow = await self._generate_workflow(goal, context)

        # 然后执行工作流
        return await self.execute_workflow(workflow, context)

    def get_token_usage(self) -> Dict[str, int]:
        """获取token使用情况"""
        return self.token_usage

    def get_execution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取执行历史"""
        return self.execution_history[-limit:] if limit > 0 else self.execution_history

    def reset_token_usage(self):
        """重置token使用统计"""
        self.token_usage = {
            "total_tokens": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0
        }

    def reset_execution_history(self):
        """重置执行历史"""
        self.execution_history = []

    def get_predefined_workflow(self, workflow_type: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """获取预定义的工作流"""
        params = params or {}

        # 主题推荐工作流
        if workflow_type == "topic_recommendation":
            return [
                {
                    "agent": "research",
                    "task": "analyze_research_trends",
                    "params": {
                        "user_interests": params.get("user_interests", ""),
                        "academic_field": params.get("academic_field", ""),
                        "academic_level": params.get("academic_level", "undergraduate"),
                        "research_trends": params.get("research_trends", [])
                    }
                },
                {
                    "agent": "writing",
                    "task": "generate_topic_suggestions",
                    "params": {
                        "research_analysis": "$research_result",
                        "user_interests": params.get("user_interests", ""),
                        "academic_field": params.get("academic_field", ""),
                        "academic_level": params.get("academic_level", "undergraduate")
                    }
                },
                {
                    "agent": "editing",
                    "task": "refine_topics",
                    "params": {
                        "topic_suggestions": "$topic_suggestions",
                        "user_interests": params.get("user_interests", ""),
                        "academic_field": params.get("academic_field", ""),
                        "academic_level": params.get("academic_level", "undergraduate")
                    }
                }
            ]

        # 提纲生成工作流
        elif workflow_type == "outline_generation":
            return [
                {
                    "agent": "outline",
                    "task": "generate_outline",
                    "params": {
                        "topic": params.get("topic", ""),
                        "academic_field": params.get("academic_field", ""),
                        "academic_level": params.get("academic_level", "undergraduate"),
                        "paper_type": params.get("paper_type", "research"),
                        "length": params.get("length", "medium")
                    }
                },
                {
                    "agent": "review",
                    "task": "review_outline",
                    "params": {
                        "content": "$outline_result",
                        "requirements": {
                            "focus_on": "structure",
                            "criteria": ["completeness", "logic", "relevance"]
                        }
                    }
                },
                {
                    "agent": "editing",
                    "task": "refine_outline",
                    "params": {
                        "content": "$outline_result",
                        "review_result": "$review_result"
                    }
                }
            ]

        # 论文章节生成工作流
        elif workflow_type == "paper_section_generation":
            return [
                {
                    "agent": "literature",
                    "task": "analyze_papers",
                    "params": {
                        "papers": params.get("papers", []),
                        "topic": params.get("topic", ""),
                        "section_id": params.get("section_id", "")
                    }
                },
                {
                    "agent": "paper",
                    "task": "write_section",
                    "params": {
                        "topic": params.get("topic", ""),
                        "outline": params.get("outline", {}),
                        "section_id": params.get("section_id", ""),
                        "literature": "$literature_analysis"
                    }
                },
                {
                    "agent": "review",
                    "task": "review_section",
                    "params": {
                        "content": "$section_content",
                        "requirements": {
                            "focus_on": "content",
                            "criteria": ["accuracy", "clarity", "coherence", "citations"]
                        }
                    }
                },
                {
                    "agent": "editing",
                    "task": "polish_section",
                    "params": {
                        "content": "$section_content",
                        "review_result": "$review_result"
                    }
                }
            ]

        # 如果没有匹配的工作流类型，返回空列表
        logger.warning(f"未找到预定义工作流: {workflow_type}")
        return []

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
