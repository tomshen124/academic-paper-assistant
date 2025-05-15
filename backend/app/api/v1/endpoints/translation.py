from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List

from app.schemas.translation import (
    TranslationRequest, 
    TranslationResponse,
    BatchTranslationRequest,
    BatchTranslationResponse
)
from app.services.translation_service import TranslationService
from app.api.deps import get_translation_service, get_current_active_user
from app.models.user import User
from app.core.logger import get_logger

logger = get_logger("translation_api")
router = APIRouter()

@router.post("", response_model=TranslationResponse)
async def translate_content(
    request: TranslationRequest,
    translation_service: TranslationService = Depends(get_translation_service),
    current_user: User = Depends(get_current_active_user)
):
    """翻译内容"""
    try:
        logger.info(f"用户 {current_user.username} 请求翻译内容: {request.source_lang} -> {request.target_lang}")
        
        translated_content = await translation_service.translate(
            content=request.content,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
            is_academic=request.is_academic
        )
        
        return {
            "translated_content": translated_content,
            "source_lang": request.source_lang,
            "target_lang": request.target_lang
        }
    except Exception as e:
        logger.error(f"翻译失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"翻译失败: {str(e)}")

@router.post("/batch", response_model=BatchTranslationResponse)
async def batch_translate_content(
    request: BatchTranslationRequest,
    translation_service: TranslationService = Depends(get_translation_service),
    current_user: User = Depends(get_current_active_user)
):
    """批量翻译内容"""
    try:
        logger.info(f"用户 {current_user.username} 请求批量翻译 {len(request.items)} 个项目: {request.source_lang} -> {request.target_lang}")
        
        translated_items = await translation_service.batch_translate(
            items=request.items,
            content_key=request.content_key,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
            is_academic=request.is_academic
        )
        
        return {
            "translated_items": translated_items,
            "source_lang": request.source_lang,
            "target_lang": request.target_lang
        }
    except Exception as e:
        logger.error(f"批量翻译失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"批量翻译失败: {str(e)}")
