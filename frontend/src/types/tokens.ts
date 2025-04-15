/**
 * Token使用记录
 */
export interface TokenUsageRecord {
  /** 时间戳 */
  timestamp: string;
  /** 日期 */
  day: string;
  /** 模型 */
  model: string;
  /** 服务 */
  service: string;
  /** 任务 */
  task: string;
  /** 输入tokens */
  prompt_tokens: number;
  /** 输出tokens */
  completion_tokens: number;
  /** 总tokens */
  total_tokens: number;
  /** 估算成本 */
  estimated_cost: number;
}

/**
 * Token使用统计
 */
export interface TokenUsageStatistics {
  /** 输入tokens */
  prompt_tokens: number;
  /** 输出tokens */
  completion_tokens: number;
  /** 总tokens */
  total_tokens: number;
  /** 估算成本 */
  estimated_cost: number;
  /** 请求数 */
  requests: number;
}

/**
 * Token使用平均值
 */
export interface TokenUsageAverages {
  /** 每请求tokens */
  tokens_per_request: number;
  /** 每请求成本 */
  cost_per_request: number;
  /** 每小时tokens */
  tokens_per_hour: number;
  /** 每小时成本 */
  cost_per_hour: number;
}

/**
 * Token使用摘要
 */
export interface TokenUsageSummary {
  /** 总使用量 */
  total_usage: TokenUsageStatistics;
  /** 平均值 */
  averages: TokenUsageAverages;
  /** 按模型统计 */
  by_model: Record<string, TokenUsageStatistics>;
  /** 按服务统计 */
  by_service: Record<string, TokenUsageStatistics>;
  /** 按日期统计 */
  by_day: Record<string, TokenUsageStatistics>;
  /** 运行时间(秒) */
  uptime_seconds: number;
  /** 运行时间(小时) */
  uptime_hours: number;
}

/**
 * Token使用响应
 */
export interface TokenUsageResponse {
  /** 使用摘要 */
  summary: TokenUsageSummary;
  /** 最近记录 */
  recent_records?: TokenUsageRecord[];
}

/**
 * Token使用导出请求
 */
export interface TokenUsageExportRequest {
  /** 导出格式 */
  format?: string;
}

/**
 * Token使用导出响应
 */
export interface TokenUsageExportResponse {
  /** 导出数据 */
  data: string;
  /** 数据格式 */
  format: string;
}

/**
 * Token使用重置响应
 */
export interface TokenUsageResetResponse {
  /** 消息 */
  message: string;
  /** 之前的摘要 */
  previous_summary: TokenUsageSummary;
}
