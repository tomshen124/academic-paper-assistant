import request from '@/utils/request';
import type {
  CitationFormatRequest,
  CitationFormatResponse,
  CitationExtractRequest,
  CitationExtractResponse,
  BibliographyRequest,
  BibliographyResponse,
  CitationStylesResponse
} from '@/types/citations';

/**
 * 格式化引用
 * @param data 引用格式化请求参数
 */
export function formatCitations(data: CitationFormatRequest) {
  return request<CitationFormatResponse>({
    url: '/citations/format',
    method: 'post',
    data
  });
}

/**
 * 提取引用
 * @param data 引用提取请求参数
 */
export function extractCitations(data: CitationExtractRequest) {
  return request<CitationExtractResponse>({
    url: '/citations/extract',
    method: 'post',
    data
  });
}

/**
 * 生成参考文献列表
 * @param data 参考文献生成请求参数
 */
export function generateBibliography(data: BibliographyRequest) {
  return request<BibliographyResponse>({
    url: '/citations/bibliography',
    method: 'post',
    data
  });
}

/**
 * 获取支持的引用样式
 */
export function getCitationStyles() {
  return request<CitationStylesResponse>({
    url: '/citations/styles',
    method: 'get'
  });
}
