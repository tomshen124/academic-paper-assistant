from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api import deps
from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import User as UserSchema, UserCreate, UserUpdate
from app.core.logger import get_logger

logger = get_logger("users")
router = APIRouter()

@router.get("/", response_model=List[UserSchema])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    获取所有用户
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.post("/", response_model=UserSchema)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    创建新用户
    """
    # 检查邮箱是否已存在
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="该邮箱已被注册",
        )

    # 检查用户名是否已存在
    user = db.query(User).filter(User.username == user_in.username).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="该用户名已被使用",
        )

    # 创建新用户
    user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password),
        is_superuser=user_in.is_superuser,
        is_active=user_in.is_active,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info(f"创建新用户: {user.username}")
    return user

@router.post("/register", response_model=UserSchema)
def register_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
) -> Any:
    """
    公开注册新用户
    """
    # 检查邮箱是否已存在
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="该邮箱已被注册",
        )

    # 检查用户名是否已存在
    user = db.query(User).filter(User.username == user_in.username).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="该用户名已被使用",
        )

    # 创建新用户（禁止创建超级用户）
    user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password),
        is_superuser=False,  # 强制设置为非超级用户
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info(f"注册新用户: {user.username}")
    return user

@router.get("/me", response_model=UserSchema)
def read_user_me(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    获取当前用户
    """
    return current_user

@router.put("/me", response_model=UserSchema)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    更新当前用户
    """
    # 如果要更新邮箱，检查是否已存在
    if user_in.email and user_in.email != current_user.email:
        user = db.query(User).filter(User.email == user_in.email).first()
        if user:
            raise HTTPException(
                status_code=400,
                detail="该邮箱已被注册",
            )

    # 如果要更新用户名，检查是否已存在
    if user_in.username and user_in.username != current_user.username:
        user = db.query(User).filter(User.username == user_in.username).first()
        if user:
            raise HTTPException(
                status_code=400,
                detail="该用户名已被使用",
            )

    # 更新用户信息
    user_data = user_in.dict(exclude_unset=True)
    if user_in.password:
        user_data["hashed_password"] = get_password_hash(user_in.password)
        del user_data["password"]

    for key, value in user_data.items():
        setattr(current_user, key, value)

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    logger.info(f"更新用户信息: {current_user.username}")
    return current_user

@router.get("/{user_id}", response_model=UserSchema)
def read_user_by_id(
    user_id: int,
    current_user: User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    通过ID获取用户
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="用户不存在",
        )

    # 只有超级用户可以查看其他用户
    if user.id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=400,
            detail="权限不足",
        )

    return user

@router.put("/{user_id}", response_model=UserSchema)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    更新用户
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="用户不存在",
        )

    # 如果要更新邮箱，检查是否已存在
    if user_in.email and user_in.email != user.email:
        user_with_email = db.query(User).filter(User.email == user_in.email).first()
        if user_with_email:
            raise HTTPException(
                status_code=400,
                detail="该邮箱已被注册",
            )

    # 如果要更新用户名，检查是否已存在
    if user_in.username and user_in.username != user.username:
        user_with_username = db.query(User).filter(User.username == user_in.username).first()
        if user_with_username:
            raise HTTPException(
                status_code=400,
                detail="该用户名已被使用",
            )

    # 更新用户信息
    user_data = user_in.dict(exclude_unset=True)
    if user_in.password:
        user_data["hashed_password"] = get_password_hash(user_in.password)
        del user_data["password"]

    for key, value in user_data.items():
        setattr(user, key, value)

    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info(f"管理员更新用户信息: {user.username}")
    return user
