from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class TokenUsageRecord(BaseModel):
    """Token使用记录"""
    timestamp: str = Field(..., description="时间戳")
    day: str = Field(..., description="日期")
    model: str = Field(..., description="模型")
    service: str = Field(..., description="服务")
    task: str = Field(..., description="任务")
    task_type: str = Field("default", description="任务类型，如 'default', 'translation' 等")
    prompt_tokens: int = Field(..., description="输入tokens")
    completion_tokens: int = Field(..., description="输出tokens")
    total_tokens: int = Field(..., description="总tokens")
    estimated_cost: float = Field(..., description="估算成本")

class TokenUsageStatistics(BaseModel):
    """Token使用统计"""
    prompt_tokens: int = Field(..., description="输入tokens")
    completion_tokens: int = Field(..., description="输出tokens")
    total_tokens: int = Field(..., description="总tokens")
    estimated_cost: float = Field(..., description="估算成本")
    requests: int = Field(..., description="请求数")

class TokenUsageAverages(BaseModel):
    """Token使用平均值"""
    tokens_per_request: float = Field(..., description="每请求tokens")
    cost_per_request: float = Field(..., description="每请求成本")
    tokens_per_hour: float = Field(..., description="每小时tokens")
    cost_per_hour: float = Field(..., description="每小时成本")

class TokenUsageSummary(BaseModel):
    """Token使用摘要"""
    total_usage: TokenUsageStatistics = Field(..., description="总使用量")
    averages: TokenUsageAverages = Field(..., description="平均值")
    by_model: Dict[str, TokenUsageStatistics] = Field(..., description="按模型统计")
    by_service: Dict[str, TokenUsageStatistics] = Field(..., description="按服务统计")
    by_task_type: Dict[str, TokenUsageStatistics] = Field(..., description="按任务类型统计")
    by_day: Dict[str, TokenUsageStatistics] = Field(..., description="按日期统计")
    uptime_seconds: float = Field(..., description="运行时间(秒)")
    uptime_hours: float = Field(..., description="运行时间(小时)")

class TokenUsageResponse(BaseModel):
    """Token使用响应"""
    summary: TokenUsageSummary = Field(..., description="使用摘要")
    recent_records: Optional[List[TokenUsageRecord]] = Field(None, description="最近记录")

class TokenUsageExportRequest(BaseModel):
    """Token使用导出请求"""
    format: str = Field("json", description="导出格式")

class TokenUsageExportResponse(BaseModel):
    """Token使用导出响应"""
    data: str = Field(..., description="导出数据")
    format: str = Field(..., description="数据格式")

class TokenUsageResetResponse(BaseModel):
    """Token使用重置响应"""
    message: str = Field(..., description="消息")
    previous_summary: TokenUsageSummary = Field(..., description="之前的摘要")
