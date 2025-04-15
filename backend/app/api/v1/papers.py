from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.paper.extractor import paper_extractor
from app.services.ai.agent import paper_agent
from app.schemas.paper import PaperAnalysisResponse

router = APIRouter(prefix="/papers")

@router.post("/analyze", response_model=PaperAnalysisResponse)
async def analyze_paper(
    file: UploadFile = File(...)
):
    """分析上传的论文"""
    try:
        # 1. 提取论文内容
        content = await paper_extractor.extract(file)
        
        # 2. 使用Agent分析论文
        analysis_result = await paper_agent.analyze_paper(content)
        
        if not analysis_result['success']:
            raise HTTPException(
                status_code=500,
                detail=analysis_result['error']
            )
            
        # 3. 查找相似论文
        similar_papers = await paper_agent.get_similar_papers(content)
        
        return {
            'analysis': analysis_result['data'],
            'similar_papers': similar_papers
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Paper analysis failed: {str(e)}"
        )

@router.get("/similar/{paper_id}")
async def get_similar_papers(
    paper_id: str,
    limit: int = 5
):
    """获取相似论文"""
    try:
        # 获取论文内容
        content = await paper_extractor.get_paper_content(paper_id)
        
        # 查找相似论文
        similar_papers = await paper_agent.get_similar_papers(
            content,
            limit=limit
        )
        
        return similar_papers
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to find similar papers: {str(e)}"
        )