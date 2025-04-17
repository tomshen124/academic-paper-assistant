import { request } from '@/utils/request';
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
  // 添加时间戳参数，避免缓存
  const timestamp = new Date().getTime();
  return request<TopicResponse[]>({
    url: `/topics/recommend?_t=${timestamp}`,
    method: 'post',
    data,
    headers: {
      'Cache-Control': 'no-cache',
      'Pragma': 'no-cache'
    }
  }).then(response => {
    // 打印响应数据以进行调试
    console.log('主题推荐原始响应数据:', response);

    // 检查响应数据是否有效
    if (!response) {
      console.error('响应数据为空');
      return [];
    }

    // 确保响应数据是数组
    const topics = Array.isArray(response) ? response : [response];
    console.log('处理后的主题数据:', topics);
    console.log('主题数量:', topics.length);

    // 验证每个主题对象是否完整
    const validatedTopics = topics.map(topic => {
      // 确保每个主题都有必要的字段
      return {
        title: topic.title || '未命名主题',
        research_question: topic.research_question || '无研究问题',
        feasibility: topic.feasibility || '未评估',
        innovation: topic.innovation || '无创新点',
        methodology: topic.methodology || '无研究方法',
        resources: topic.resources || '无资源需求',
        expected_outcomes: topic.expected_outcomes || '无预期成果',
        keywords: Array.isArray(topic.keywords) ? topic.keywords : []
      } as TopicResponse;
    });

    console.log('验证后的主题数据:', validatedTopics);
    return validatedTopics;
  }).catch(error => {
    console.error('获取主题推荐失败:', error);
    throw error;
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
