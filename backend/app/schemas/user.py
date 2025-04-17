from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

# 用户基础模式
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False

# 创建用户时的请求模式
class UserCreate(UserBase):
    email: EmailStr
    username: str
    password: str

# 更新用户时的请求模式
class UserUpdate(UserBase):
    password: Optional[str] = None

# 数据库中的用户模式
class UserInDBBase(UserBase):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# API响应中的用户模式
class User(UserInDBBase):
    pass

# 数据库中包含密码的用户模式
class UserInDB(UserInDBBase):
    hashed_password: str
