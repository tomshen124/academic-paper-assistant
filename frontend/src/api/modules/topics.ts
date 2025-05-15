import { request } from '@/utils/request';
import type {
  TopicRequest,
  TopicResponse,
  TopicFeasibilityRequest,
  TopicFeasibilityResponse,
  TopicRefinementRequest,
  TopicRefinementResponse,
  UserTopicsResponse
} from '@/types/topics';
import type { StreamEventHandler } from '@/types/stream';

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

/**
 * 流式推荐论文主题
 * @param data 主题请求参数
 * @param eventHandlers 事件处理函数
 */
/**
 * 获取用户主题列表
 */
export function getUserTopics(skip: number = 0, limit: number = 100) {
  return request<UserTopicsResponse>({
    url: `/topics?skip=${skip}&limit=${limit}`,
    method: 'get'
  });
}

/**
 * 根据ID获取主题
 * @param id 主题ID
 */
export function getTopicById(id: number) {
  return request<TopicResponse>({
    url: `/topics/${id}`,
    method: 'get'
  });
}

export function recommendTopicsStream(data: TopicRequest, eventHandlers: StreamEventHandler) {
  // 添加时间戳参数，避免缓存
  const timestamp = new Date().getTime();
  const baseURL = import.meta.env.VITE_APP_API_BASE_URL || 'http://localhost:8000/api/v1';

  // 将请求参数编码到URL中
  const params = new URLSearchParams();
  params.append('user_interests', data.user_interests);
  params.append('academic_field', data.academic_field);
  if (data.academic_level) params.append('academic_level', data.academic_level);
  if (data.topic_count) params.append('topic_count', data.topic_count.toString());
  params.append('_t', timestamp.toString());

  // 构建URL
  const url = `${baseURL}/topics/recommend/stream?${params.toString()}`;

  console.log('创建SSE连接:', url);

  // 获取认证令牌
  const token = localStorage.getItem('token');

  if (!token) {
    console.error('未找到认证令牌，无法创建SSE连接');
    if (eventHandlers.onError) {
      eventHandlers.onError('未登录或会话已过期，请重新登录');
    }
    return () => {};
  }

  // 构建EventSource URL，包含认证令牌
  const eventSourceUrl = `${url}&token=${encodeURIComponent(token)}`;

  console.log('创建SSE连接，带有认证信息:', eventSourceUrl);

  // 创建EventSource对象
  // 注意：EventSource的withCredentials选项不会发送Authorization头，所以我们在URL中包含了token
  const eventSource = new EventSource(eventSourceUrl, { withCredentials: true });

  console.log('SSE连接创建成功，带有认证信息:', !!token);

  // 处理连接打开
  eventSource.onopen = (event) => {
    console.log('SSE连接已打开:', event);
    if (eventHandlers.onStatus) {
      eventHandlers.onStatus('连接已建立，等待数据...');
    }
  };

  // 处理消息事件
  eventSource.onmessage = (event) => {
    try {
      console.log('收到原始SSE数据:', event.data);
      const data = JSON.parse(event.data);
      console.log('解析后的流式数据:', data);

      // 根据消息类型调用相应的处理函数
      switch (data.type) {
        case 'status':
          if (eventHandlers.onStatus) {
            eventHandlers.onStatus(data.message);
          }
          break;
        case 'interest_analysis':
          if (eventHandlers.onInterestAnalysis) {
            eventHandlers.onInterestAnalysis(data.data);
          }
          break;
        case 'topic':
          if (eventHandlers.onTopic) {
            // 验证主题对象
            const topic = {
              title: data.data.title || '未命名主题',
              research_question: data.data.research_question || '无研究问题',
              feasibility: data.data.feasibility || '未评估',
              innovation: data.data.innovation || '无创新点',
              methodology: data.data.methodology || '无研究方法',
              resources: data.data.resources || '无资源需求',
              expected_outcomes: data.data.expected_outcomes || '无预期成果',
              keywords: Array.isArray(data.data.keywords) ? data.data.keywords : []
            } as TopicResponse;

            eventHandlers.onTopic(topic);
          }
          break;
        case 'complete':
          if (eventHandlers.onComplete) {
            eventHandlers.onComplete(data.message);
          }
          // 关闭EventSource
          eventSource.close();
          break;
        case 'error':
          if (eventHandlers.onError) {
            eventHandlers.onError(data.message);
          }
          // 关闭EventSource
          eventSource.close();
          break;
        default:
          console.warn('未知的消息类型:', data.type);
      }
    } catch (error) {
      console.error('解析流式数据失败:', error, event.data);
      if (eventHandlers.onError) {
        eventHandlers.onError('解析数据失败');
      }
    }
  };

  // 处理错误
  eventSource.onerror = (error) => {
    console.error('流式连接错误:', error);
    if (eventHandlers.onError) {
      eventHandlers.onError('流式连接错误，请检查网络或登录状态');
    }
    // 关闭EventSource
    eventSource.close();
  };

  // 返回关闭EventSource的函数
  return () => {
    console.log('关闭SSE连接');
    eventSource.close();
  };
}
