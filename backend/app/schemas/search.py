from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class SearchRequest(BaseModel):
    """学术搜索请求"""
    query: str = Field(..., description="搜索查询")
    limit: int = Field(10, description="结果数量限制")
    sources: Optional[List[str]] = Field(None, description="搜索源列表，为空表示使用所有启用的源")
    sort_by: str = Field("relevance", description="排序方式：relevance, citations, date")
    years: str = Field("all", description="年份范围：all, last_1, last_5, last_10")
    categories: Optional[List[str]] = Field(None, description="arXiv类别列表")
    fields: Optional[List[str]] = Field(None, description="返回字段列表")

class Paper(BaseModel):
    """学术论文"""
    title: str = Field(..., description="标题")
    authors: List[str] = Field(..., description="作者")
    year: Optional[str] = Field(None, description="年份")
    abstract: Optional[str] = Field(None, description="摘要")
    url: Optional[str] = Field(None, description="URL")
    venue: Optional[str] = Field(None, description="发表期刊/会议")
    citations: Optional[int] = Field(None, description="引用次数")
    source: str = Field(..., description="来源")

class SearchResponse(BaseModel):
    """学术搜索响应"""
    results: List[Paper] = Field(..., description="搜索结果")
    total: int = Field(..., description="总结果数")
    query: str = Field(..., description="搜索查询")
    sources_stats: Dict[str, int] = Field({}, description="各搜索源的结果数量")

class PaperDetailRequest(BaseModel):
    """论文详情请求"""
    paper_id: str = Field(..., description="论文ID")
    source: str = Field(..., description="来源")

class PaperDetailResponse(BaseModel):
    """论文详情响应"""
    title: str = Field(..., description="标题")
    authors: List[str] = Field(..., description="作者")
    year: Optional[str] = Field(None, description="年份")
    abstract: str = Field(..., description="摘要")
    url: str = Field(..., description="URL")
    venue: Optional[str] = Field(None, description="发表期刊/会议")
    citations: Optional[int] = Field(None, description="引用次数")
    references: Optional[List[Dict[str, Any]]] = Field(None, description="参考文献")
    source: str = Field(..., description="来源")

class TrendRequest(BaseModel):
    """研究趋势请求"""
    field: str = Field(..., description="学术领域")

class Trend(BaseModel):
    """研究趋势"""
    title: str = Field(..., description="标题")
    abstract: str = Field(..., description="摘要")
    year: str = Field(..., description="年份")
    url: str = Field(..., description="URL")
    citations: int = Field(..., description="引用次数")

class TrendResponse(BaseModel):
    """研究趋势响应"""
    trends: List[Trend] = Field(..., description="研究趋势")
    field: str = Field(..., description="学术领域")
