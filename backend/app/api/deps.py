from typing import Generator
from app.services.llm_service import llm_service
from app.services.academic_search_service import academic_search_service
from app.services.topic_service import topic_service
from app.services.outline_service import outline_service
from app.services.paper_service import paper_service
from app.services.citation_service import citation_service
from app.services.agent_service import agent_coordinator
from app.services.token_service import token_service

# 保留数据库依赖的导入，以便将来集成
# from app.db.session import SessionLocal

# def get_db() -> Generator:
#     """
#     获取数据库会话依赖
#     """
#     try:
#         db = SessionLocal()
#         yield db
#     finally:
#         db.close()

def get_llm_service() -> Generator:
    """获取LLM服务"""
    yield llm_service

def get_academic_search_service() -> Generator:
    """获取学术搜索服务"""
    yield academic_search_service

def get_topic_service() -> Generator:
    """获取主题服务"""
    yield topic_service

def get_outline_service() -> Generator:
    """获取提纲服务"""
    yield outline_service

def get_paper_service() -> Generator:
    """获取论文服务"""
    yield paper_service

def get_citation_service() -> Generator:
    """获取引用服务"""
    yield citation_service

def get_agent_coordinator() -> Generator:
    """获取智能体协调器"""
    yield agent_coordinator

def get_token_service() -> Generator:
    """获取Token服务"""
    yield token_service