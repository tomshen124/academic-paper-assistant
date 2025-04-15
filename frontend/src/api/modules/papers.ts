import request from '@/utils/request';
import type {
  PaperSectionRequest,
  PaperSectionResponse,
  FullPaperRequest,
  FullPaperResponse,
  SectionImprovementRequest,
  SectionImprovementResponse
} from '@/types/papers';

/**
 * 生成论文章节
 * @param data 章节生成请求参数
 */
export function generatePaperSection(data: PaperSectionRequest) {
  return request<PaperSectionResponse>({
    url: '/papers/sections',
    method: 'post',
    data
  });
}

/**
 * 生成完整论文
 * @param data 完整论文生成请求参数
 */
export function generateFullPaper(data: FullPaperRequest) {
  return request<FullPaperResponse>({
    url: '/papers/generate',
    method: 'post',
    data
  });
}

/**
 * 改进论文章节
 * @param data 章节改进请求参数
 */
export function improveSection(data: SectionImprovementRequest) {
  return request<SectionImprovementResponse>({
    url: '/papers/improve',
    method: 'post',
    data
  });
}
