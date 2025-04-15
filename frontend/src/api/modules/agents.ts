import request from '@/utils/request';
import type {
  AgentTaskRequest,
  AgentTaskResponse,
  WorkflowRequest,
  WorkflowResponse,
  PlanRequest,
  PlanResponse,
  PlanAndExecuteRequest,
  PlanAndExecuteResponse
} from '@/types/agents';

/**
 * 执行智能体任务
 * @param data 智能体任务请求参数
 */
export function executeAgentTask(data: AgentTaskRequest) {
  return request<AgentTaskResponse>({
    url: '/agents/task',
    method: 'post',
    data
  });
}

/**
 * 执行工作流
 * @param data 工作流请求参数
 */
export function executeWorkflow(data: WorkflowRequest) {
  return request<WorkflowResponse>({
    url: '/agents/workflow',
    method: 'post',
    data
  });
}

/**
 * 生成任务计划
 * @param data 规划请求参数
 */
export function generatePlan(data: PlanRequest) {
  return request<PlanResponse>({
    url: '/agents/plan',
    method: 'post',
    data
  });
}

/**
 * 规划并执行任务
 * @param data 规划并执行请求参数
 */
export function planAndExecute(data: PlanAndExecuteRequest) {
  return request<PlanAndExecuteResponse>({
    url: '/agents/plan-and-execute',
    method: 'post',
    data
  });
}
