from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class SubSection(BaseModel):
    """论文子章节"""
    id: str = Field(..., description="子章节ID")
    title: str = Field(..., description="子章节标题")
    purpose: str = Field(..., description="子章节目的")
    content_points: List[str] = Field(..., description="内容要点")
    expected_length: str = Field(..., description="预期长度")

class Section(BaseModel):
    """论文章节"""
    id: str = Field(..., description="章节ID")
    title: str = Field(..., description="章节标题")
    purpose: str = Field(..., description="章节目的")
    content_points: List[str] = Field(..., description="内容要点")
    expected_length: str = Field(..., description="预期长度")
    subsections: Optional[List[SubSection]] = Field(None, description="子章节")

class OutlineRequest(BaseModel):
    """论文提纲请求"""
    topic: str = Field(..., description="论文主题")
    paper_type: str = Field(..., description="论文类型")
    academic_field: str = Field(..., description="学术领域")
    academic_level: str = Field("undergraduate", description="学术级别")
    length: str = Field("3000words", description="预期长度")

class OutlineResponse(BaseModel):
    """论文提纲响应"""
    title: str = Field(..., description="论文标题")
    abstract: str = Field(..., description="摘要")
    keywords: List[str] = Field(..., description="关键词")
    sections: List[Section] = Field(..., description="章节")

class OutlineOptimizationRequest(BaseModel):
    """提纲优化请求"""
    outline: Dict[str, Any] = Field(..., description="原始提纲")
    feedback: str = Field(..., description="用户反馈")

class OutlineTemplateRequest(BaseModel):
    """提纲模板请求"""
    paper_type: str = Field(..., description="论文类型")
    academic_field: str = Field(..., description="学术领域")

class OutlineTemplate(BaseModel):
    """提纲模板"""
    name: str = Field(..., description="模板名称")
    suitable_for: str = Field(..., description="适用场景")
    structure: List[Dict[str, Any]] = Field(..., description="结构")
    features: List[str] = Field(..., description="特点")

class OutlineValidationRequest(BaseModel):
    """提纲验证请求"""
    outline: Dict[str, Any] = Field(..., description="提纲")

class ValidationCategory(BaseModel):
    """验证类别"""
    score: int = Field(..., description="评分")
    issues: List[str] = Field(..., description="问题")
    suggestions: List[str] = Field(..., description="建议")

class OutlineValidationResponse(BaseModel):
    """提纲验证响应"""
    completeness: ValidationCategory = Field(..., description="完整性")
    coherence: ValidationCategory = Field(..., description="连贯性")
    balance: ValidationCategory = Field(..., description="平衡性")
    methodology: ValidationCategory = Field(..., description="方法适当性")
    overall_assessment: str = Field(..., description="总体评价")
    overall_score: int = Field(..., description="总评分")
