from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class TopicRequest(BaseModel):
    """论文主题请求"""
    user_interests: str = Field(..., description="用户研究兴趣")
    academic_field: str = Field(..., description="学术领域")
    academic_level: str = Field("undergraduate", description="学术级别")

class TopicResponse(BaseModel):
    """论文主题响应"""
    title: str = Field(..., description="主题标题")
    research_question: str = Field(..., description="研究问题")
    feasibility: str = Field(..., description="可行性")
    innovation: str = Field(..., description="创新点")
    methodology: str = Field(..., description="研究方法")
    resources: str = Field(..., description="所需资源")
    expected_outcomes: str = Field(..., description="预期成果")
    keywords: List[str] = Field(..., description="关键词")

class TopicFeasibilityRequest(BaseModel):
    """主题可行性分析请求"""
    topic: str = Field(..., description="论文主题")
    academic_field: str = Field(..., description="学术领域")
    academic_level: str = Field("undergraduate", description="学术级别")

class TopicFeasibilityResponse(BaseModel):
    """主题可行性分析响应"""
    difficulty: str = Field(..., description="难度评估")
    resources: str = Field(..., description="资源需求")
    time_estimate: str = Field(..., description="时间估计")
    research_gaps: str = Field(..., description="研究空白")
    challenges: str = Field(..., description="潜在挑战")
    suggestions: str = Field(..., description="改进建议")
    overall_score: int = Field(..., description="总体评分")
    recommendation: str = Field(..., description="最终建议")

class TopicRefinementRequest(BaseModel):
    """主题优化请求"""
    topic: str = Field(..., description="原始主题")
    feedback: str = Field(..., description="用户反馈")
    academic_field: str = Field(..., description="学术领域")
    academic_level: str = Field("undergraduate", description="学术级别")

class TopicRefinementResponse(BaseModel):
    """主题优化响应"""
    refined_title: str = Field(..., description="优化后的主题标题")
    research_question: str = Field(..., description="明确的研究问题")
    scope: str = Field(..., description="研究范围")
    methodology: str = Field(..., description="建议的研究方法")
    keywords: List[str] = Field(..., description="关键词")
    improvements: str = Field(..., description="相比原主题的改进之处")
