/**
 * 学术搜索请求
 */
export interface SearchRequest {
  /** 搜索查询 */
  query: string;
  /** 结果数量限制 */
  limit?: number;
}

/**
 * 学术论文
 */
export interface Paper {
  /** 标题 */
  title: string;
  /** 作者 */
  authors: string[];
  /** 年份 */
  year?: string;
  /** 摘要 */
  abstract?: string;
  /** URL */
  url?: string;
  /** 发表期刊/会议 */
  venue?: string;
  /** 引用次数 */
  citations?: number;
  /** 来源 */
  source: string;
}

/**
 * 学术搜索响应
 */
export interface SearchResponse {
  /** 搜索结果 */
  results: Paper[];
  /** 总结果数 */
  total: number;
  /** 搜索查询 */
  query: string;
}

/**
 * 论文详情请求
 */
export interface PaperDetailRequest {
  /** 论文ID */
  paper_id: string;
  /** 来源 */
  source: string;
}

/**
 * 论文详情响应
 */
export interface PaperDetailResponse {
  /** 标题 */
  title: string;
  /** 作者 */
  authors: string[];
  /** 年份 */
  year?: string;
  /** 摘要 */
  abstract: string;
  /** URL */
  url: string;
  /** 发表期刊/会议 */
  venue?: string;
  /** 引用次数 */
  citations?: number;
  /** 参考文献 */
  references?: Record<string, any>[];
  /** 来源 */
  source: string;
}

/**
 * 研究趋势请求
 */
export interface TrendRequest {
  /** 学术领域 */
  field: string;
}

/**
 * 研究趋势
 */
export interface Trend {
  /** 标题 */
  title: string;
  /** 摘要 */
  abstract: string;
  /** 年份 */
  year: string;
  /** URL */
  url: string;
  /** 引用次数 */
  citations: number;
}

/**
 * 研究趋势响应
 */
export interface TrendResponse {
  /** 研究趋势 */
  trends: Trend[];
  /** 学术领域 */
  field: string;
}
