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
        # 添加日志记录
        import logging
        logger = logging.getLogger("app")
        logger.info(f"开始搜索学术文献: 查询={request.query}, 限制={request.limit}, 来源={request.sources}, 排序={request.sort_by}")

        # 参数验证
        if not request.query or not isinstance(request.query, str) or len(request.query.strip()) == 0:
            logger.warning("搜索查询为空")
            return {
                "results": [],
                "total": 0,
                "query": request.query,
                "sources_stats": {}
            }

        # 执行搜索
        search_result = await search_service.search_academic_papers(
            query=request.query,
            limit=request.limit,
            sources=request.sources,
            sort_by=request.sort_by,
            years=request.years,
            categories=request.categories,
            fields=request.fields
        )

        # 验证搜索结果
        if not isinstance(search_result, dict):
            logger.error(f"搜索结果不是字典类型: {type(search_result)}")
            return {
                "results": [],
                "total": 0,
                "query": request.query,
                "sources_stats": {}
            }

        # 确保所有必要的字段都存在
        results = search_result.get("results", [])
        total = search_result.get("total", 0)
        sources_stats = search_result.get("sources_stats", {})

        logger.info(f"搜索完成: 找到 {total} 条结果")

        return {
            "results": results,
            "total": total,
            "query": request.query,
            "sources_stats": sources_stats
        }
    except Exception as e:
        # 记录详细错误信息
        import traceback
        import logging
        logger = logging.getLogger("app")
        logger.error(f"搜索文献失败: {str(e)}")
        logger.error(traceback.format_exc())

        # 返回友好的错误信息
        raise HTTPException(status_code=500, detail=f"搜索文献失败: {str(e)}")

@router.post("/paper", response_model=PaperDetailResponse)
async def get_paper_details(
    request: PaperDetailRequest,
    search_service: AcademicSearchService = Depends(get_academic_search_service)
):
    """获取论文详情"""
    try:
        # 添加日志记录
        import logging
        logger = logging.getLogger("app")
        logger.info(f"开始获取论文详情: ID={request.paper_id}, 来源={request.source}")

        # 参数验证
        if not request.paper_id or not isinstance(request.paper_id, str) or len(request.paper_id.strip()) == 0:
            logger.warning("论文ID为空")
            raise HTTPException(status_code=400, detail="论文ID不能为空")

        # 执行查询
        paper = await search_service.get_paper_details(
            paper_id=request.paper_id,
            source=request.source
        )

        # 验证结果
        if not paper or not isinstance(paper, dict):
            logger.warning(f"未找到论文或结果格式无效: {request.paper_id}")
            raise HTTPException(status_code=404, detail=f"未找到论文: {request.paper_id}")

        logger.info(f"获取论文详情成功: {request.paper_id}")
        return paper
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        # 记录详细错误信息
        import traceback
        import logging
        logger = logging.getLogger("app")
        logger.error(f"获取论文详情失败: {str(e)}")
        logger.error(traceback.format_exc())

        # 返回友好的错误信息
        raise HTTPException(status_code=500, detail=f"获取论文详情失败: {str(e)}")

@router.post("/trends", response_model=TrendResponse)
async def get_research_trends(
    request: TrendRequest,
    search_service: AcademicSearchService = Depends(get_academic_search_service)
):
    """获取研究趋势"""
    try:
        # 添加日志记录
        import logging
        logger = logging.getLogger("app")
        logger.info(f"开始获取研究趋势: 领域={request.field}")

        # 参数验证
        if not request.field or not isinstance(request.field, str) or len(request.field.strip()) == 0:
            logger.warning("研究领域为空")
            return {
                "trends": [],
                "field": request.field
            }

        # 健壮性处理：确保field是有效字符串并转为英文查询
        field = request.field.strip()

        # 如果是中文字段，添加英文映射
        field_mapping = {
            "计算机科学": "computer science",
            "人工智能": "artificial intelligence",
            "机器学习": "machine learning",
            "深度学习": "deep learning",
            "自然语言处理": "natural language processing",
            "计算机视觉": "computer vision",
            "医学": "medicine",
            "生物学": "biology",
            "物理学": "physics",
            "化学": "chemistry",
            "数学": "mathematics",
            "经济学": "economics",
            "社会学": "sociology",
            "心理学": "psychology",
            "教育学": "education",
            "文学": "literature",
            "历史学": "history",
            "哲学": "philosophy",
            "法学": "law",
            "工程学": "engineering",
            "环境科学": "environmental science",
            "地理学": "geography",
            "农学": "agriculture",
            "管理学": "management"
        }

        search_field = field_mapping.get(field, field)
        logger.info(f"映射后的研究领域: {search_field}")

        # 直接使用服务中的方法获取研究趋势
        trends = await search_service.get_research_trends(search_field)

        # 验证结果
        if not isinstance(trends, list):
            logger.warning(f"研究趋势结果不是列表类型: {type(trends)}")
            trends = []

        logger.info(f"获取研究趋势成功: 找到 {len(trends)} 条趋势")

        return {
            "trends": trends,
            "field": request.field
        }
    except Exception as e:
        # 记录详细错误信息
        import traceback
        import logging
        logger = logging.getLogger("app")
        logger.error(f"获取研究趋势失败: {str(e)}")
        logger.error(traceback.format_exc())

        # 返回空结果而不是错误
        return {
            "trends": [],
            "field": request.field
        }
