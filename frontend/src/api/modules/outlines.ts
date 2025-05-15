import { request } from '@/utils/request';
import type {
  OutlineRequest,
  OutlineResponse,
  OutlineOptimizationRequest,
  OutlineTemplateRequest,
  OutlineTemplate,
  OutlineValidationRequest,
  OutlineValidationResponse,
  UserOutlinesResponse
} from '@/types/outlines';

/**
 * 生成论文提纲
 * @param data 提纲请求参数
 */
export function generateOutline(data: OutlineRequest) {
  return request<OutlineResponse>({
    url: '/outlines/generate',
    method: 'post',
    data
  });
}

/**
 * 优化论文提纲
 * @param data 提纲优化请求参数
 */
export function optimizeOutline(data: OutlineOptimizationRequest) {
  return request<OutlineResponse>({
    url: '/outlines/optimize',
    method: 'post',
    data
  });
}

/**
 * 获取提纲模板
 * @param data 提纲模板请求参数
 */
export function getOutlineTemplates(data: OutlineTemplateRequest) {
  return request<OutlineTemplate[]>({
    url: '/outlines/templates',
    method: 'post',
    data
  });
}

/**
 * 验证提纲逻辑
 * @param data 提纲验证请求参数
 */
export function validateOutline(data: OutlineValidationRequest) {
  return request<OutlineValidationResponse>({
    url: '/outlines/validate',
    method: 'post',
    data
  });
}

/**
 * 获取用户提纲列表
 * @param skip 跳过数量
 * @param limit 限制数量
 */
export function getUserOutlines(skip: number = 0, limit: number = 100) {
  return request<UserOutlinesResponse>({
    url: `/outlines?skip=${skip}&limit=${limit}`,
    method: 'get'
  });
}

/**
 * 根据ID获取提纲
 * @param id 提纲ID
 */
export function getOutlineById(id: number) {
  return request<OutlineResponse>({
    url: `/outlines/${id}`,
    method: 'get'
  });
}
