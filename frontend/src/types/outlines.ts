/**
 * 论文子章节
 */
export interface SubSection {
  /** 子章节ID */
  id: string;
  /** 子章节标题 */
  title: string;
  /** 子章节目的 */
  purpose: string;
  /** 内容要点 */
  content_points: string[];
  /** 预期长度 */
  expected_length: string;
}

/**
 * 论文章节
 */
export interface Section {
  /** 章节ID */
  id: string;
  /** 章节标题 */
  title: string;
  /** 章节目的 */
  purpose: string;
  /** 内容要点 */
  content_points: string[];
  /** 预期长度 */
  expected_length: string;
  /** 子章节 */
  subsections?: SubSection[];
}

/**
 * 论文提纲请求
 */
export interface OutlineRequest {
  /** 论文主题 */
  topic: string;
  /** 论文类型 */
  paper_type: string;
  /** 学术领域 */
  academic_field: string;
  /** 学术级别 */
  academic_level?: string;
  /** 预期长度 */
  length?: string;
}

/**
 * 论文提纲响应
 */
export interface OutlineResponse {
  /** 论文标题 */
  title: string;
  /** 摘要 */
  abstract: string;
  /** 关键词 */
  keywords: string[];
  /** 章节 */
  sections: Section[];
}

/**
 * 提纲优化请求
 */
export interface OutlineOptimizationRequest {
  /** 原始提纲 */
  outline: Record<string, any>;
  /** 用户反馈 */
  feedback: string;
}

/**
 * 提纲模板请求
 */
export interface OutlineTemplateRequest {
  /** 论文类型 */
  paper_type: string;
  /** 学术领域 */
  academic_field: string;
}

/**
 * 提纲模板
 */
export interface OutlineTemplate {
  /** 模板名称 */
  name: string;
  /** 适用场景 */
  suitable_for: string;
  /** 结构 */
  structure: Record<string, any>[];
  /** 特点 */
  features: string[];
}

/**
 * 提纲验证请求
 */
export interface OutlineValidationRequest {
  /** 提纲 */
  outline: Record<string, any>;
}

/**
 * 验证类别
 */
export interface ValidationCategory {
  /** 评分 */
  score: number;
  /** 问题 */
  issues: string[];
  /** 建议 */
  suggestions: string[];
}

/**
 * 提纲验证响应
 */
export interface OutlineValidationResponse {
  /** 完整性 */
  completeness: ValidationCategory;
  /** 连贯性 */
  coherence: ValidationCategory;
  /** 平衡性 */
  balance: ValidationCategory;
  /** 方法适当性 */
  methodology: ValidationCategory;
  /** 总体评价 */
  overall_assessment: string;
  /** 总评分 */
  overall_score: number;
}
