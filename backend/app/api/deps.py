from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.core.config import settings
from app.core.security import SECRET_KEY, ALGORITHM
from app.models.user import User

from app.services.llm_service import llm_service
from app.services.academic_search_service import academic_search_service
from app.services.topic_service import topic_service
from app.services.outline_service import outline_service
from app.services.paper_service import paper_service
from app.services.citation_service import citation_service
from app.services.agent_service import agent_coordinator
from app.services.token_service import token_service

# OAuth2 密码Bearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

# Token数据模型
class TokenData(BaseModel):
    username: Optional[str] = None

def get_db() -> Generator:
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="用户未激活")
    return current_user

def get_current_active_superuser(current_user: User = Depends(get_current_user)) -> User:
    """获取当前活跃超级用户"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="用户权限不足")
    return current_user

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