from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """User creation schema"""
    email: EmailStr
    username: str
    password: str


class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User response schema"""
    id: int
    email: str
    username: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class User(BaseModel):
    """User model for database"""
    id: Optional[int] = None
    email: str
    username: str
    hashed_password: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
