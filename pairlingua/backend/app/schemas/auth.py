from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, validator
import re


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    nickname: Optional[str] = None
    locale: str = "ru"
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter') 
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v
    
    @validator('nickname')
    def validate_nickname(cls, v):
        if v and len(v) < 3:
            raise ValueError('Nickname must be at least 3 characters long')
        if v and len(v) > 50:
            raise ValueError('Nickname must be less than 50 characters')
        if v and not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Nickname can only contain letters, numbers, underscore and dash')
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds until access token expires


class TokenRefresh(BaseModel):
    refresh_token: str


class TokenRefreshResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class PasswordReset(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str
    
    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v
