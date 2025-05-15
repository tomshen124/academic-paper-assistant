import { request } from '@/utils/request';
import type {
  TokenUsageResponse,
  TokenUsageExportRequest,
  TokenUsageExportResponse,
  UserTokenUsageRecord,
  UserTokenUsageSummary,
  TokenFilterOptions
} from '@/types/tokens';

/**
 * 获取token使用情况
 * @param params 查询参数
 */
export function getTokenUsage(params: {
  include_recent?: boolean;
  recent_limit?: number;
  start_date?: string;
  end_date?: string;
} = {}) {
  return request<TokenUsageResponse>({
    url: '/tokens/usage',
    method: 'get',
    params
  });
}

/**
 * 导出token使用数据
 * @param data 导出请求参数
 * @param params 查询参数
 */
export function exportTokenUsage(
  data: TokenUsageExportRequest,
  params: {
    start_date?: string;
    end_date?: string;
  } = {}
) {
  return request<TokenUsageExportResponse>({
    url: '/tokens/export',
    method: 'post',
    data,
    params
  });
}

/**
 * 获取用户token使用记录
 * @param params 查询参数
 */
export function getUserTokenUsage(params: {
  skip?: number;
  limit?: number;
  start_date?: string;
  end_date?: string;
  model?: string;
  service?: string;
  task?: string;
} = {}) {
  return request<UserTokenUsageRecord[]>({
    url: '/tokens/user-usage',
    method: 'get',
    params
  });
}

/**
 * 获取用户token使用摘要
 * @param params 查询参数
 */
export function getUserTokenUsageSummary(params: {
  start_date?: string;
  end_date?: string;
} = {}) {
  return request<UserTokenUsageSummary>({
    url: '/tokens/user-summary',
    method: 'get',
    params
  });
}

/**
 * 获取token使用过滤选项
 */
export function getTokenFilterOptions() {
  return request<TokenFilterOptions>({
    url: '/tokens/filter-options',
    method: 'get'
  });
}

/**
 * 重置token使用数据
 */
export function resetTokenUsage() {
  return request({
    url: '/tokens/reset',
    method: 'post'
  });
}
