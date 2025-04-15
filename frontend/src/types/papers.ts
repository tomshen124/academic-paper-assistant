/**
 * 论文章节生成请求
 */
export interface PaperSectionRequest {
  /** 论文主题 */
  topic: string;
  /** 论文提纲 */
  outline: Record<string, any>;
  /** 章节ID */
  section_id: string;
  /** 相关文献 */
  literature?: Record<string, any>[];
}

/**
 * 论文章节生成响应
 */
export interface PaperSectionResponse {
  /** 章节ID */
  section_id: string;
  /** 章节标题 */
  title: string;
  /** 章节内容 */
  content: string;
  /** Token使用情况 */
  token_usage: Record<string, number>;
}

/**
 * 完整论文生成请求
 */
export interface FullPaperRequest {
  /** 论文主题 */
  topic: string;
  /** 论文提纲 */
  outline: Record<string, any>;
  /** 相关文献 */
  literature?: Record<string, any>[];
}

/**
 * 完整论文生成响应
 */
export interface FullPaperResponse {
  /** 论文标题 */
  title: string;
  /** 摘要 */
  abstract: string;
  /** 关键词 */
  keywords: string[];
  /** 章节内容 */
  sections: Record<string, Record<string, string>>;
  /** 总Token使用量 */
  token_usage: number;
}

/**
 * 章节改进请求
 */
export interface SectionImprovementRequest {
  /** 论文主题 */
  topic: string;
  /** 章节ID */
  section_id: string;
  /** 当前内容 */
  current_content: string;
  /** 用户反馈 */
  feedback: string;
  /** 相关文献 */
  literature?: Record<string, any>[];
}

/**
 * 章节改进响应
 */
export interface SectionImprovementResponse {
  /** 章节ID */
  section_id: string;
  /** 改进后的内容 */
  improved_content: string;
  /** Token使用情况 */
  token_usage: Record<string, number>;
}
