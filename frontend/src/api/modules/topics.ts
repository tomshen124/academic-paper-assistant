import request from '@/utils/request';
import type {
  TopicRequest,
  TopicResponse,
  TopicFeasibilityRequest,
  TopicFeasibilityResponse,
  TopicRefinementRequest,
  TopicRefinementResponse
} from '@/types/topics';

/**
 * 推荐论文主题
 * @param data 主题请求参数
 */
export function recommendTopics(data: TopicRequest) {
  return request<TopicResponse[]>({
    url: '/topics/recommend',
    method: 'post',
    data
  });
}

/**
 * 分析主题可行性
 * @param data 可行性分析请求参数
 */
export function analyzeTopicFeasibility(data: TopicFeasibilityRequest) {
  return request<TopicFeasibilityResponse>({
    url: '/topics/analyze',
    method: 'post',
    data
  });
}

/**
 * 优化论文主题
 * @param data 主题优化请求参数
 */
export function refineTopic(data: TopicRefinementRequest) {
  return request<TopicRefinementResponse>({
    url: '/topics/refine',
    method: 'post',
    data
  });
}
