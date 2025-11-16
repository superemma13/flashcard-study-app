from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime


class UserAnalytics(BaseModel):
    """User analytics model"""
    user_id: int
    total_cards: int
    total_sessions: int
    total_study_minutes: float
    average_accuracy: float
    longest_streak: int
    current_streak: int
    cards_due_for_review: int
    topics: List[str]
    last_updated: datetime


class AnalyticsResponse(BaseModel):
    """Analytics response schema"""
    total_cards: int
    total_sessions: int
    total_study_minutes: float
    average_accuracy: float
    longest_streak: int
    current_streak: int
    cards_due_for_review: int
    topics: List[str]
    daily_study_minutes: Dict[str, float]  # Date -> minutes
    accuracy_by_topic: Dict[str, float]
    
    class Config:
        from_attributes = True
