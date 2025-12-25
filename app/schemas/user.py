from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from app.models.user import UserRole


class UserBase(BaseModel):
    username: str
    email: str  # Changed from EmailStr to str temporarily
    full_name: Optional[str] = None
    role: UserRole = UserRole.ORDER_MAINTAINER


class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v.encode('utf-8')) > 72:
            raise ValueError('Password is too long. Maximum 72 characters allowed.')
        if len(v) < 4:
            raise ValueError('Password must be at least 4 characters long.')
        return v


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None  # Changed from EmailStr to str temporarily
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[UserRole] = None


class RefreshToken(BaseModel):
    refresh_token: str