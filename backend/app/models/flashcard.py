from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class DifficultyLevel(str, Enum):
    """Difficulty levels for adaptive quiz"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class FlashcardCreate(BaseModel):
    """Flashcard creation schema"""
    question: str
    answer: str
    topic: str
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM


class FlashcardUpdate(BaseModel):
    """Flashcard update schema"""
    question: Optional[str] = None
    answer: Optional[str] = None
    topic: Optional[str] = None
    difficulty: Optional[DifficultyLevel] = None


class FlashcardResponse(BaseModel):
    """Flashcard response schema"""
    id: int
    question: str
    answer: str
    topic: str
    difficulty: DifficultyLevel
    created_at: datetime
    last_reviewed: Optional[datetime] = None
    review_count: int = 0
    difficulty_score: float = 0.5  # Between 0 and 1, where 1 is hardest
    
    class Config:
        from_attributes = True


class Flashcard(BaseModel):
    """Flashcard model for database"""
    id: Optional[int] = None
    user_id: int
    question: str
    answer: str
    topic: str
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    created_at: Optional[datetime] = None
    last_reviewed: Optional[datetime] = None
    review_count: int = 0
    difficulty_score: float = 0.5
    embedding: Optional[str] = None  # Vector embedding for semantic search
    
    class Config:
        from_attributes = True
