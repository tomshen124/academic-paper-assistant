import { request } from '@/utils/request';
import type {
  SearchRequest,
  SearchResponse,
  PaperDetailRequest,
  PaperDetailResponse,
  TrendRequest,
  TrendResponse
} from '@/types/search';

/**
 * 搜索学术文献
 * @param data 搜索请求参数
 */
export function searchLiterature(data: SearchRequest) {
  return request<SearchResponse>({
    url: '/search/literature',
    method: 'post',
    data
  });
}

/**
 * 获取论文详情
 * @param data 论文详情请求参数
 */
export function getPaperDetails(data: PaperDetailRequest) {
  return request<PaperDetailResponse>({
    url: '/search/paper',
    method: 'post',
    data
  });
}

/**
 * 获取研究趋势
 * @param data 研究趋势请求参数
 */
export function getResearchTrends(data: TrendRequest) {
  return request<TrendResponse>({
    url: '/search/trends',
    method: 'post',
    data
  });
}
