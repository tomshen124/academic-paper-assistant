/**
 * 智能体任务请求
 */
export interface AgentTaskRequest {
  /** 智能体ID */
  agent_id: string;
  /** 任务描述 */
  task: string;
  /** 任务上下文 */
  context?: Record<string, any>;
}

/**
 * 智能体任务响应
 */
export interface AgentTaskResponse {
  /** 任务结果 */
  result: Record<string, any>;
}

/**
 * 工作流步骤
 */
export interface WorkflowStep {
  /** 智能体ID */
  agent: string;
  /** 任务描述 */
  task: string;
}

/**
 * 工作流请求
 */
export interface WorkflowRequest {
  /** 工作流步骤 */
  workflow: WorkflowStep[];
  /** 初始上下文 */
  context?: Record<string, any>;
}

/**
 * 工作流步骤结果
 */
export interface WorkflowStepResult {
  /** 智能体ID */
  agent: string;
  /** 任务描述 */
  task: string;
  /** 步骤结果 */
  result: Record<string, any>;
}

/**
 * 工作流响应
 */
export interface WorkflowResponse {
  /** 工作流结果 */
  workflow_results: WorkflowStepResult[];
  /** 最终上下文 */
  final_context: Record<string, any>;
}

/**
 * 规划请求
 */
export interface PlanRequest {
  /** 目标描述 */
  goal: string;
  /** 初始上下文 */
  context?: Record<string, any>;
}

/**
 * 规划响应
 */
export interface PlanResponse {
  /** 生成的工作流 */
  workflow: WorkflowStep[];
}

/**
 * 规划并执行请求
 */
export interface PlanAndExecuteRequest {
  /** 目标描述 */
  goal: string;
  /** 初始上下文 */
  context?: Record<string, any>;
}

/**
 * 规划并执行响应
 */
export interface PlanAndExecuteResponse {
  /** 工作流结果 */
  workflow_results: WorkflowStepResult[];
  /** 最终上下文 */
  final_context: Record<string, any>;
}
