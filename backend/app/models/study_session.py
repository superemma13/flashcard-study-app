from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class SessionStatus(str, Enum):
    """Study session statuses"""
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"


class StudySessionCreate(BaseModel):
    """Study session creation schema"""
    topic: Optional[str] = None
    target_count: int = 10


class StudySessionResponse(BaseModel):
    """Study session response schema"""
    id: int
    user_id: int
    topic: Optional[str] = None
    status: SessionStatus
    cards_studied: int
    cards_correct: int
    accuracy: float = 0.0
    duration_minutes: float
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class StudySession(BaseModel):
    """Study session model for database"""
    id: Optional[int] = None
    user_id: int
    topic: Optional[str] = None
    status: SessionStatus = SessionStatus.ACTIVE
    cards_studied: int = 0
    cards_correct: int = 0
    duration_minutes: float = 0.0
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
