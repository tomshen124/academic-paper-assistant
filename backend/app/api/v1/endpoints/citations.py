from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any

from app.schemas.citation import (
    CitationFormatRequest,
    CitationFormatResponse,
    CitationExtractRequest,
    CitationExtractResponse,
    BibliographyRequest,
    BibliographyResponse,
    CitationStylesResponse
)
from app.services.citation_service import CitationService
from app.api.deps import get_citation_service

router = APIRouter()

@router.post("/format", response_model=CitationFormatResponse)
async def format_citations(
    request: CitationFormatRequest,
    citation_service: CitationService = Depends(get_citation_service)
):
    """格式化引用"""
    try:
        formatted = await citation_service.format_citations(
            content=request.content,
            literature=request.literature,
            style=request.style
        )
        return formatted
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"格式化引用失败: {str(e)}")

@router.post("/extract", response_model=CitationExtractResponse)
async def extract_citations(
    request: CitationExtractRequest,
    citation_service: CitationService = Depends(get_citation_service)
):
    """提取引用"""
    try:
        citations = await citation_service.extract_citations(
            content=request.content
        )
        return {"citations": citations, "total_count": len(citations)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"提取引用失败: {str(e)}")

@router.post("/bibliography", response_model=BibliographyResponse)
async def generate_bibliography(
    request: BibliographyRequest,
    citation_service: CitationService = Depends(get_citation_service)
):
    """生成参考文献列表"""
    try:
        bibliography = await citation_service.generate_bibliography(
            literature=request.literature,
            style=request.style
        )
        return {"bibliography": bibliography}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成参考文献列表失败: {str(e)}")

@router.get("/styles", response_model=CitationStylesResponse)
async def get_citation_styles(
    citation_service: CitationService = Depends(get_citation_service)
):
    """获取支持的引用样式"""
    try:
        styles = citation_service.get_citation_styles()
        return {"styles": styles}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取引用样式失败: {str(e)}")
