from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any

from app.schemas.paper import (
    PaperSectionRequest,
    PaperSectionResponse,
    FullPaperRequest,
    FullPaperResponse,
    SectionImprovementRequest,
    SectionImprovementResponse
)
from app.services.paper_service import PaperService
from app.api.deps import get_paper_service

router = APIRouter()

@router.post("/sections", response_model=PaperSectionResponse)
async def generate_paper_section(
    request: PaperSectionRequest,
    paper_service: PaperService = Depends(get_paper_service)
):
    """生成论文章节"""
    try:
        section = await paper_service.generate_paper_section(
            topic=request.topic,
            outline=request.outline,
            section_id=request.section_id,
            literature=request.literature
        )
        return section
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成论文章节失败: {str(e)}")

@router.post("/generate", response_model=FullPaperResponse)
async def generate_full_paper(
    request: FullPaperRequest,
    paper_service: PaperService = Depends(get_paper_service)
):
    """生成完整论文"""
    try:
        paper = await paper_service.generate_full_paper(
            topic=request.topic,
            outline=request.outline,
            literature=request.literature
        )
        return paper
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成完整论文失败: {str(e)}")

@router.post("/improve", response_model=SectionImprovementResponse)
async def improve_section(
    request: SectionImprovementRequest,
    paper_service: PaperService = Depends(get_paper_service)
):
    """改进论文章节"""
    try:
        improved_section = await paper_service.improve_section(
            topic=request.topic,
            section_id=request.section_id,
            current_content=request.current_content,
            feedback=request.feedback,
            literature=request.literature
        )
        return improved_section
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"改进论文章节失败: {str(e)}")
