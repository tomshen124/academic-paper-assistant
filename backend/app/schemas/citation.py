from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class Citation(BaseModel):
    """引用"""
    id: str = Field(..., description="引用ID")
    formatted_citation: str = Field(..., description="格式化的引用文本")
    original_text: str = Field(..., description="原始引用文本")

class CitationFormatRequest(BaseModel):
    """引用格式化请求"""
    content: str = Field(..., description="内容")
    literature: List[Dict[str, Any]] = Field(..., description="文献列表")
    style: str = Field("apa", description="引用样式")

class CitationFormatResponse(BaseModel):
    """引用格式化响应"""
    formatted_content: str = Field(..., description="格式化后的内容")
    references: List[Citation] = Field(..., description="引用列表")
    bibliography: List[str] = Field(..., description="参考文献列表")

class CitationExtractRequest(BaseModel):
    """引用提取请求"""
    content: str = Field(..., description="内容")

class ExtractedCitation(BaseModel):
    """提取的引用"""
    text: str = Field(..., description="引用文本")
    position: str = Field(..., description="引用位置")
    author: Optional[str] = Field(None, description="可能的作者")
    year: Optional[str] = Field(None, description="可能的年份")

class CitationExtractResponse(BaseModel):
    """引用提取响应"""
    citations: List[ExtractedCitation] = Field(..., description="提取的引用")
    total_count: int = Field(..., description="引用总数")

class BibliographyRequest(BaseModel):
    """参考文献生成请求"""
    literature: List[Dict[str, Any]] = Field(..., description="文献列表")
    style: str = Field("apa", description="引用样式")

class BibliographyResponse(BaseModel):
    """参考文献生成响应"""
    bibliography: List[str] = Field(..., description="参考文献列表")

class CitationStylesResponse(BaseModel):
    """引用样式响应"""
    styles: Dict[str, str] = Field(..., description="支持的引用样式")
