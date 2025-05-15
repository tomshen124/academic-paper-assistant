/**
 * 论文主题请求
 */
export interface TopicRequest {
  /** 用户研究兴趣 */
  user_interests: string;
  /** 学术领域 */
  academic_field: string;
  /** 学术级别 */
  academic_level?: string;
  /** 推荐主题数量 */
  topic_count?: number;
}

/**
 * 论文主题响应
 */
export interface TopicResponse {
  /** 主题标题 */
  title: string;
  /** 研究问题 */
  research_question: string;
  /** 可行性 */
  feasibility: string;
  /** 创新点 */
  innovation: string;
  /** 研究方法 */
  methodology: string;
  /** 所需资源 */
  resources: string;
  /** 预期成果 */
  expected_outcomes: string;
  /** 关键词 */
  keywords: string[];
}

/**
 * 主题可行性分析请求
 */
export interface TopicFeasibilityRequest {
  /** 论文主题 */
  topic: string;
  /** 学术领域 */
  academic_field: string;
  /** 学术级别 */
  academic_level?: string;
}

/**
 * 主题可行性分析响应
 */
export interface TopicFeasibilityResponse {
  /** 难度评估 */
  difficulty: string;
  /** 资源需求 */
  resources: string;
  /** 时间估计 */
  time_estimate: string;
  /** 研究空白 */
  research_gaps: string;
  /** 潜在挑战 */
  challenges: string;
  /** 改进建议 */
  suggestions: string;
  /** 总体评分 */
  overall_score: number;
  /** 最终建议 */
  recommendation: string;
}

/**
 * 主题优化请求
 */
export interface TopicRefinementRequest {
  /** 原始主题 */
  topic: string;
  /** 用户反馈 */
  feedback: string;
  /** 学术领域 */
  academic_field: string;
  /** 学术级别 */
  academic_level?: string;
}

/**
 * 主题优化响应
 */
export interface TopicRefinementResponse {
  /** 优化后的主题标题 */
  refined_title: string;
  /** 明确的研究问题 */
  research_question: string;
  /** 研究范围 */
  scope: string;
  /** 建议的研究方法 */
  methodology: string;
  /** 关键词 */
  keywords: string[];
  /** 相比原主题的改进之处 */
  improvements: string;
}

/**
 * 用户主题列表响应
 */
export interface UserTopicItem {
  /** 主题ID */
  id: number;
  /** 主题标题 */
  title: string;
  /** 学术领域 */
  academic_field: string;
  /** 学术级别 */
  academic_level: string;
  /** 创建时间 */
  created_at: string;
  /** 更新时间 */
  updated_at: string;
}

/**
 * 用户主题列表响应
 */
export interface UserTopicsResponse {
  /** 主题列表 */
  topics: UserTopicItem[];
  /** 总数 */
  total: number;
}
