from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from app.api import deps
from app.core.security import create_access_token, verify_password, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
from app.models.user import User
from app.schemas.auth import Token, Login, RefreshToken
from app.core.logger import get_logger

logger = get_logger("auth")
router = APIRouter()

@router.post("/login", response_model=Token)
def login_access_token(
    db: Session = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    获取OAuth2兼容的令牌
    """
    # 验证用户
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.warning(f"登录失败: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 检查用户是否激活
    if not user.is_active:
        logger.warning(f"非活跃用户尝试登录: {form_data.username}")
        raise HTTPException(status_code=400, detail="用户未激活")

    # 创建访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    logger.info(f"用户登录成功: {user.username}")
    return {
        "access_token": create_access_token(
            user.username, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/login/json", response_model=Token)
def login_json(
    login: Login, db: Session = Depends(deps.get_db)
) -> Any:
    """
    使用JSON格式登录
    """
    # 验证用户
    user = db.query(User).filter(User.username == login.username).first()

    # 详细记录登录尝试
    if not user:
        logger.warning(f"JSON登录失败: 用户不存在 - {login.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    logger.info(f"尝试验证用户密码: {login.username}, 哈希密码长度: {len(user.hashed_password) if user.hashed_password else 0}")

    if not verify_password(login.password, user.hashed_password):
        logger.warning(f"JSON登录失败: 密码错误 - {login.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    # 检查用户是否激活
    if not user.is_active:
        logger.warning(f"非活跃用户尝试JSON登录: {login.username}")
        raise HTTPException(status_code=400, detail="用户未激活")

    # 创建访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    logger.info(f"用户JSON登录成功: {user.username}")
    return {
        "access_token": create_access_token(
            user.username, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/refresh", response_model=Token)
def refresh_token(
    refresh_token: RefreshToken, db: Session = Depends(deps.get_db)
) -> Any:
    """
    刷新访问令牌
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # 解析令牌
        payload = jwt.decode(refresh_token.token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            logger.warning("令牌中没有用户名")
            raise credentials_exception

        # 检查用户是否存在
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            logger.warning(f"刷新令牌失败: 用户不存在 {username}")
            raise credentials_exception

        # 检查用户是否激活
        if not user.is_active:
            logger.warning(f"非活跃用户尝试刷新令牌: {username}")
            raise HTTPException(status_code=400, detail="用户未激活")

        # 创建新令牌
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=user.username, expires_delta=access_token_expires
        )

        logger.info(f"令牌刷新成功: {username}")
        return {"access_token": access_token, "token_type": "bearer"}

    except JWTError as e:
        logger.error(f"刷新令牌失败: {str(e)}")
        raise credentials_exception
