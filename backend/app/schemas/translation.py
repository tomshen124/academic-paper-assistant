from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class TranslationRequest(BaseModel):
    """翻译请求"""
    content: str = Field(..., description="要翻译的内容")
    source_lang: str = Field("en", description="源语言代码")
    target_lang: str = Field("zh-CN", description="目标语言代码")
    is_academic: bool = Field(True, description="是否为学术内容")

class TranslationResponse(BaseModel):
    """翻译响应"""
    translated_content: str = Field(..., description="翻译后的内容")
    source_lang: str = Field(..., description="源语言代码")
    target_lang: str = Field(..., description="目标语言代码")

class BatchTranslationRequest(BaseModel):
    """批量翻译请求"""
    items: List[Dict[str, Any]] = Field(..., description="要翻译的项目列表")
    content_key: str = Field(..., description="内容字段的键名")
    source_lang: str = Field("en", description="源语言代码")
    target_lang: str = Field("zh-CN", description="目标语言代码")
    is_academic: bool = Field(True, description="是否为学术内容")

class BatchTranslationResponse(BaseModel):
    """批量翻译响应"""
    translated_items: List[Dict[str, Any]] = Field(..., description="翻译后的项目列表")
    source_lang: str = Field(..., description="源语言代码")
    target_lang: str = Field(..., description="目标语言代码")
