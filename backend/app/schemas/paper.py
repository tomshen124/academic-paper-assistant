from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class PaperSectionRequest(BaseModel):
    """论文章节生成请求"""
    topic: str = Field(..., description="论文主题")
    outline: Dict[str, Any] = Field(..., description="论文提纲")
    section_id: str = Field(..., description="章节ID")
    literature: Optional[List[Dict[str, Any]]] = Field(None, description="相关文献")

class PaperSectionResponse(BaseModel):
    """论文章节生成响应"""
    section_id: str = Field(..., description="章节ID")
    title: str = Field(..., description="章节标题")
    content: str = Field(..., description="章节内容")
    token_usage: Dict[str, int] = Field(..., description="Token使用情况")

class FullPaperRequest(BaseModel):
    """完整论文生成请求"""
    topic: str = Field(..., description="论文主题")
    outline: Dict[str, Any] = Field(..., description="论文提纲")
    literature: Optional[List[Dict[str, Any]]] = Field(None, description="相关文献")

class FullPaperResponse(BaseModel):
    """完整论文生成响应"""
    title: str = Field(..., description="论文标题")
    abstract: str = Field(..., description="摘要")
    keywords: List[str] = Field(..., description="关键词")
    sections: Dict[str, Dict[str, str]] = Field(..., description="章节内容")
    token_usage: int = Field(..., description="总Token使用量")

class SectionImprovementRequest(BaseModel):
    """章节改进请求"""
    topic: str = Field(..., description="论文主题")
    section_id: str = Field(..., description="章节ID")
    current_content: str = Field(..., description="当前内容")
    feedback: str = Field(..., description="用户反馈")
    literature: Optional[List[Dict[str, Any]]] = Field(None, description="相关文献")

class SectionImprovementResponse(BaseModel):
    """章节改进响应"""
    section_id: str = Field(..., description="章节ID")
    improved_content: str = Field(..., description="改进后的内容")
    token_usage: Dict[str, int] = Field(..., description="Token使用情况")
