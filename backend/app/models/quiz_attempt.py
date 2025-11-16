from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class QuizAttemptCreate(BaseModel):
    """Quiz attempt creation schema"""
    flashcard_id: int
    is_correct: bool
    response_time_seconds: int


class QuizAttemptResponse(BaseModel):
    """Quiz attempt response schema"""
    id: int
    flashcard_id: int
    is_correct: bool
    response_time_seconds: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class QuizAttempt(BaseModel):
    """Quiz attempt model for database"""
    id: Optional[int] = None
    study_session_id: int
    flashcard_id: int
    is_correct: bool
    response_time_seconds: int
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
