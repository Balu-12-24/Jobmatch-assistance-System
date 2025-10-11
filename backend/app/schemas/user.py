from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    is_premium: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None


class UserProfileUpdate(BaseModel):
    location: Optional[str] = None
    preferences: Optional[dict] = None


class UserProfileResponse(BaseModel):
    id: int
    user_id: int
    skills: Optional[List[str]] = None
    experience_years: Optional[int] = None
    education_level: Optional[str] = None
    location: Optional[str] = None
    preferences: Optional[dict] = None
    updated_at: datetime
    
    class Config:
        from_attributes = True
