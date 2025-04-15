from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any

from app.schemas.search import (
    SearchRequest,
    SearchResponse,
    PaperDetailRequest,
    PaperDetailResponse,
    TrendRequest,
    TrendResponse
)
from app.services.academic_search_service import AcademicSearchService
from app.api.deps import get_academic_search_service

router = APIRouter()

@router.post("/literature", response_model=SearchResponse)
async def search_literature(
    request: SearchRequest,
    search_service: AcademicSearchService = Depends(get_academic_search_service)
):
    """搜索学术文献"""
    try:
        search_result = await search_service.search_academic_papers(
            query=request.query,
            limit=request.limit,
            sources=request.sources,
            sort_by=request.sort_by,
            years=request.years,
            categories=request.categories,
            fields=request.fields
        )

        return {
            "results": search_result["results"],
            "total": search_result["total"],
            "query": request.query,
            "sources_stats": search_result["sources_stats"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索文献失败: {str(e)}")

@router.post("/paper", response_model=PaperDetailResponse)
async def get_paper_details(
    request: PaperDetailRequest,
    search_service: AcademicSearchService = Depends(get_academic_search_service)
):
    """获取论文详情"""
    try:
        paper = await search_service.get_paper_details(
            paper_id=request.paper_id,
            source=request.source
        )
        return paper
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取论文详情失败: {str(e)}")

@router.post("/trends", response_model=TrendResponse)
async def get_research_trends(
    request: TrendRequest,
    search_service: AcademicSearchService = Depends(get_academic_search_service)
):
    """获取研究趋势"""
    try:
        # 使用新的搜索方法获取研究趋势
        search_result = await search_service.search_academic_papers(
            query=f"survey {request.field} recent advances",
            limit=10,
            sort_by="date",
            years="last_5"
        )

        # 按引用次数排序
        papers = sorted(
            search_result["results"],
            key=lambda x: x.get("citations", 0),
            reverse=True
        )

        # 提取趋势信息
        trends = []
        for paper in papers[:10]:
            trend = {
                "title": paper.get("title", ""),
                "abstract": paper.get("abstract", ""),
                "year": paper.get("year", ""),
                "url": paper.get("url", ""),
                "citations": paper.get("citations", 0)
            }
            trends.append(trend)

        return {
            "trends": trends,
            "field": request.field
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取研究趋势失败: {str(e)}")
