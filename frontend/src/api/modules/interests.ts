import { request } from '@/utils/request';
import type { TopicRequest } from '@/types/topics';

/**
 * 分析用户兴趣
 * @param data 主题请求参数
 */
export function analyzeInterests(data: TopicRequest) {
  // 添加时间戳参数，避免缓存
  const timestamp = new Date().getTime();
  return request<any>({
    url: `/interests/analyze?_t=${timestamp}`,
    method: 'post',
    data,
    headers: {
      'Cache-Control': 'no-cache',
      'Pragma': 'no-cache'
    }
  }).then(response => {
    // 打印响应数据以进行调试
    console.log('兴趣分析原始响应数据:', response);
    return response;
  });
}
