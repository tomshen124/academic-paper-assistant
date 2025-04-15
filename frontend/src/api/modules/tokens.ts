import request from '@/utils/request';
import type {
  TokenUsageResponse,
  TokenUsageExportRequest,
  TokenUsageExportResponse,
  TokenUsageResetResponse
} from '@/types/tokens';

/**
 * 获取token使用情况
 * @param params 查询参数
 */
export function getTokenUsage(params: { include_recent?: boolean; recent_limit?: number } = {}) {
  return request<TokenUsageResponse>({
    url: '/tokens/usage',
    method: 'get',
    params
  });
}

/**
 * 导出token使用数据
 * @param data 导出请求参数
 */
export function exportTokenUsage(data: TokenUsageExportRequest) {
  return request<TokenUsageExportResponse>({
    url: '/tokens/export',
    method: 'post',
    data
  });
}

/**
 * 重置token使用数据
 */
export function resetTokenUsage() {
  return request<TokenUsageResetResponse>({
    url: '/tokens/reset',
    method: 'post'
  });
}
