/**
 * 引用
 */
export interface Citation {
  /** 引用ID */
  id: string;
  /** 格式化的引用文本 */
  formatted_citation: string;
  /** 原始引用文本 */
  original_text: string;
}

/**
 * 引用格式化请求
 */
export interface CitationFormatRequest {
  /** 内容 */
  content: string;
  /** 文献列表 */
  literature: Record<string, any>[];
  /** 引用样式 */
  style?: string;
}

/**
 * 引用格式化响应
 */
export interface CitationFormatResponse {
  /** 格式化后的内容 */
  formatted_content: string;
  /** 引用列表 */
  references: Citation[];
  /** 参考文献列表 */
  bibliography: string[];
}

/**
 * 引用提取请求
 */
export interface CitationExtractRequest {
  /** 内容 */
  content: string;
}

/**
 * 提取的引用
 */
export interface ExtractedCitation {
  /** 引用文本 */
  text: string;
  /** 引用位置 */
  position: string;
  /** 可能的作者 */
  author?: string;
  /** 可能的年份 */
  year?: string;
}

/**
 * 引用提取响应
 */
export interface CitationExtractResponse {
  /** 提取的引用 */
  citations: ExtractedCitation[];
  /** 引用总数 */
  total_count: number;
}

/**
 * 参考文献生成请求
 */
export interface BibliographyRequest {
  /** 文献列表 */
  literature: Record<string, any>[];
  /** 引用样式 */
  style?: string;
}

/**
 * 参考文献生成响应
 */
export interface BibliographyResponse {
  /** 参考文献列表 */
  bibliography: string[];
}

/**
 * 引用样式响应
 */
export interface CitationStylesResponse {
  /** 支持的引用样式 */
  styles: Record<string, string>;
}
