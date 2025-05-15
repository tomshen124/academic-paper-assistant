import { request } from '@/utils/request';

/**
 * 翻译请求参数
 */
export interface TranslationRequest {
  content: string;
  source_lang?: string;
  target_lang?: string;
  is_academic?: boolean;
}

/**
 * 翻译响应
 */
export interface TranslationResponse {
  translated_content: string;
  source_lang: string;
  target_lang: string;
}

/**
 * 批量翻译请求参数
 */
export interface BatchTranslationRequest {
  items: any[];
  content_key: string;
  source_lang?: string;
  target_lang?: string;
  is_academic?: boolean;
}

/**
 * 批量翻译响应
 */
export interface BatchTranslationResponse {
  translated_items: any[];
  source_lang: string;
  target_lang: string;
}

/**
 * 翻译内容
 * @param data 翻译请求参数
 */
export function translateContent(data: TranslationRequest) {
  return request<TranslationResponse>({
    url: '/translation',
    method: 'post',
    data
  });
}

/**
 * 批量翻译内容
 * @param data 批量翻译请求参数
 */
export function batchTranslateContent(data: BatchTranslationRequest) {
  return request<BatchTranslationResponse>({
    url: '/translation/batch',
    method: 'post',
    data
  });
}
