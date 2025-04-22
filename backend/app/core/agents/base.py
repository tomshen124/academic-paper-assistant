"""
多智能体系统的基础模块
提供智能体基类、协调器基类和通信协议
"""
from typing import Dict, List, Any, Optional, Callable, Awaitable
from pydantic import BaseModel, Field
from datetime import datetime
import uuid
import json
import asyncio
from app.core.logger import get_logger

logger = get_logger()

class AgentMessage(BaseModel):
    """智能体间通信的消息格式"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender: str
    receiver: str
    content: Any
    timestamp: datetime = Field(default_factory=datetime.now)
    type: str = "text"  # text, json, action, error
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        result = self.dict()
        result["timestamp"] = self.timestamp.isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict) -> "AgentMessage":
        """从字典创建消息"""
        if isinstance(data["timestamp"], str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)

class AgentContext(BaseModel):
    """智能体上下文"""
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conversation_history: List[AgentMessage] = []
    shared_memory: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}
    
    def add_message(self, message: AgentMessage):
        """添加消息到历史记录"""
        self.conversation_history.append(message)
    
    def get_messages_for_agent(self, agent_id: str) -> List[AgentMessage]:
        """获取与特定智能体相关的消息"""
        return [
            msg for msg in self.conversation_history 
            if msg.sender == agent_id or msg.receiver == agent_id
        ]
    
    def set_shared_memory(self, key: str, value: Any):
        """设置共享内存"""
        self.shared_memory[key] = value
    
    def get_shared_memory(self, key: str, default: Any = None) -> Any:
        """获取共享内存"""
        return self.shared_memory.get(key, default)

class BaseAgent:
    """智能体基类"""
    
    def __init__(self, agent_id: str, name: str, role: str, llm_service=None):
        """初始化智能体"""
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.llm_service = llm_service
        self.tools = {}
        self.system_prompt = f"你是{name}，一个{role}。"
        logger.info(f"创建智能体: {agent_id}, 名称: {name}, 角色: {role}")
    
    def register_tool(self, tool_name: str, tool_func: Callable):
        """注册工具"""
        self.tools[tool_name] = tool_func
        logger.info(f"智能体 {self.agent_id} 注册工具: {tool_name}")
    
    async def process_message(self, message: AgentMessage, context: AgentContext) -> AgentMessage:
        """处理接收到的消息并生成响应"""
        # 基类实现简单的消息处理逻辑
        response_content = f"收到消息: {message.content}"
        
        return AgentMessage(
            sender=self.agent_id,
            receiver=message.sender,
            content=response_content,
            type="text"
        )
    
    async def execute_task(self, task: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """执行任务"""
        logger.info(f"智能体 {self.agent_id} 执行任务: {task.get('task_type', 'unknown')}")
        
        # 基类实现简单的任务执行逻辑
        return {
            "status": "completed",
            "result": f"任务由 {self.name} 执行完成",
            "agent_id": self.agent_id
        }
    
    async def call_tool(self, tool_name: str, **kwargs) -> Any:
        """调用工具"""
        if tool_name not in self.tools:
            raise ValueError(f"工具 {tool_name} 未注册")
        
        logger.info(f"智能体 {self.agent_id} 调用工具: {tool_name}")
        return await self.tools[tool_name](**kwargs)

class AgentRegistry:
    """智能体注册表"""
    
    def __init__(self):
        """初始化注册表"""
        self.agents = {}
    
    def register(self, agent: BaseAgent):
        """注册智能体"""
        self.agents[agent.agent_id] = agent
        logger.info(f"注册智能体: {agent.agent_id}")
    
    def unregister(self, agent_id: str):
        """注销智能体"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            logger.info(f"注销智能体: {agent_id}")
    
    def get(self, agent_id: str) -> Optional[BaseAgent]:
        """获取智能体"""
        return self.agents.get(agent_id)
    
    def list_agents(self) -> List[str]:
        """列出所有智能体ID"""
        return list(self.agents.keys())

class AgentCoordinator:
    """智能体协调器"""
    
    def __init__(self, registry: AgentRegistry):
        """初始化协调器"""
        self.registry = registry
        self.contexts = {}  # 任务上下文映射
        logger.info("创建智能体协调器")
    
    def create_context(self, task_id: str = None) -> AgentContext:
        """创建新的任务上下文"""
        context = AgentContext(task_id=task_id or str(uuid.uuid4()))
        self.contexts[context.task_id] = context
        return context
    
    def get_context(self, task_id: str) -> Optional[AgentContext]:
        """获取任务上下文"""
        return self.contexts.get(task_id)
    
    async def send_message(
        self, 
        sender_id: str, 
        receiver_id: str, 
        content: Any, 
        context: AgentContext,
        message_type: str = "text"
    ) -> AgentMessage:
        """发送消息"""
        # 检查发送者和接收者是否存在
        sender = self.registry.get(sender_id)
        receiver = self.registry.get(receiver_id)
        
        if not sender:
            raise ValueError(f"发送者 {sender_id} 不存在")
        
        if not receiver:
            raise ValueError(f"接收者 {receiver_id} 不存在")
        
        # 创建消息
        message = AgentMessage(
            sender=sender_id,
            receiver=receiver_id,
            content=content,
            type=message_type
        )
        
        # 添加到上下文
        context.add_message(message)
        
        # 处理消息
        response = await receiver.process_message(message, context)
        
        # 添加响应到上下文
        context.add_message(response)
        
        return response
    
    async def execute_workflow(
        self, 
        workflow: List[Dict[str, Any]], 
        context: AgentContext = None
    ) -> Dict[str, Any]:
        """执行工作流"""
        if context is None:
            context = self.create_context()
        
        results = []
        
        for step in workflow:
            agent_id = step["agent_id"]
            task = step["task"]
            
            agent = self.registry.get(agent_id)
            if not agent:
                raise ValueError(f"智能体 {agent_id} 不存在")
            
            # 执行任务
            result = await agent.execute_task(task, context)
            
            # 保存结果
            results.append({
                "step": step,
                "result": result
            })
            
            # 更新共享内存
            context.set_shared_memory(f"step_{len(results)}_result", result)
        
        return {
            "task_id": context.task_id,
            "results": results,
            "context": context
        }
    
    async def collaborative_task(
        self, 
        task: Dict[str, Any], 
        agent_ids: List[str],
        context: AgentContext = None
    ) -> Dict[str, Any]:
        """协作任务执行"""
        if context is None:
            context = self.create_context()
        
        # 创建控制者消息
        controller_message = AgentMessage(
            sender="system",
            receiver=agent_ids[0],  # 第一个智能体作为起点
            content=task,
            type="task"
        )
        
        context.add_message(controller_message)
        
        # 初始化结果
        results = []
        current_agent_idx = 0
        
        # 协作循环
        max_turns = 10  # 防止无限循环
        for _ in range(max_turns):
            current_agent_id = agent_ids[current_agent_idx]
            current_agent = self.registry.get(current_agent_id)
            
            # 获取最新消息
            latest_messages = context.conversation_history[-3:]  # 获取最近的几条消息
            
            # 执行当前智能体的任务
            result = await current_agent.execute_task({
                "task_type": "collaborative",
                "messages": latest_messages,
                "context": context.shared_memory
            }, context)
            
            # 保存结果
            results.append({
                "agent_id": current_agent_id,
                "result": result
            })
            
            # 检查是否完成
            if result.get("status") == "completed":
                break
            
            # 轮换到下一个智能体
            current_agent_idx = (current_agent_idx + 1) % len(agent_ids)
        
        return {
            "task_id": context.task_id,
            "results": results,
            "context": context
        }

# 全局注册表和协调器
agent_registry = AgentRegistry()
agent_coordinator = AgentCoordinator(agent_registry)