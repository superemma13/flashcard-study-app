"""Analytics routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db import get_db, UserDB, FlashcardDB, StudySessionDB, QuizAttemptDB, decode_token
from app.models import AnalyticsResponse
from datetime import datetime, timedelta
from typing import Dict, List

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


def get_current_user(token: str, db: Session = Depends(get_db)) -> UserDB:
    """Get current user from token"""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No token provided"
        )
    
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user_id = int(payload.get("sub"))
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.get("/dashboard", response_model=AnalyticsResponse)
def get_analytics_dashboard(token: str, db: Session = Depends(get_db)):
    """Get user analytics for dashboard"""
    user = get_current_user(token, db)
    
    # Total cards
    total_cards = db.query(func.count(FlashcardDB.id)).filter(
        FlashcardDB.user_id == user.id
    ).scalar() or 0
    
    # Total sessions
    total_sessions = db.query(func.count(StudySessionDB.id)).filter(
        StudySessionDB.user_id == user.id,
        StudySessionDB.status == "completed"
    ).scalar() or 0
    
    # Total study time
    sessions = db.query(StudySessionDB).filter(
        StudySessionDB.user_id == user.id,
        StudySessionDB.status == "completed"
    ).all()
    
    total_study_minutes = sum(s.duration_minutes for s in sessions)
    
    # Average accuracy
    attempts = db.query(QuizAttemptDB).join(StudySessionDB).filter(
        StudySessionDB.user_id == user.id
    ).all()
    
    if attempts:
        average_accuracy = sum(1 for a in attempts if a.is_correct) / len(attempts)
    else:
        average_accuracy = 0.0
    
    # Streaks
    longest_streak = _calculate_longest_streak(user.id, db)
    current_streak = _calculate_current_streak(user.id, db)
    
    # Cards due for review
    now = datetime.utcnow()
    cards_due = db.query(func.count(FlashcardDB.id)).filter(
        FlashcardDB.user_id == user.id,
        (FlashcardDB.last_reviewed.is_(None) | (FlashcardDB.last_reviewed < now))
    ).scalar() or 0
    
    # Topics
    topics = db.query(FlashcardDB.topic).filter(
        FlashcardDB.user_id == user.id
    ).distinct().all()
    topic_list = [t[0] for t in topics if t[0]]
    
    # Daily study minutes (last 7 days)
    daily_study = _get_daily_study_minutes(user.id, db)
    
    # Accuracy by topic
    accuracy_by_topic = _get_accuracy_by_topic(user.id, db)
    
    return AnalyticsResponse(
        total_cards=total_cards,
        total_sessions=total_sessions,
        total_study_minutes=total_study_minutes,
        average_accuracy=average_accuracy,
        longest_streak=longest_streak,
        current_streak=current_streak,
        cards_due_for_review=cards_due,
        topics=topic_list,
        daily_study_minutes=daily_study,
        accuracy_by_topic=accuracy_by_topic
    )


def _calculate_longest_streak(user_id: int, db: Session) -> int:
    """Calculate longest study streak"""
    sessions = db.query(StudySessionDB).filter(
        StudySessionDB.user_id == user_id,
        StudySessionDB.status == "completed"
    ).order_by(StudySessionDB.completed_at).all()
    
    if not sessions:
        return 0
    
    longest = 0
    current = 0
    last_date = None
    
    for session in sessions:
        session_date = session.completed_at.date() if session.completed_at else None
        
        if last_date is None or session_date == last_date:
            current += 1
        elif (session_date - last_date).days == 1:
            current += 1
        else:
            longest = max(longest, current)
            current = 1
        
        last_date = session_date
    
    return max(longest, current)


def _calculate_current_streak(user_id: int, db: Session) -> int:
    """Calculate current study streak"""
    sessions = db.query(StudySessionDB).filter(
        StudySessionDB.user_id == user_id,
        StudySessionDB.status == "completed"
    ).order_by(StudySessionDB.completed_at.desc()).all()
    
    if not sessions:
        return 0
    
    today = datetime.utcnow().date()
    current = 0
    check_date = today
    
    for session in sessions:
        session_date = session.completed_at.date() if session.completed_at else None
        
        if session_date == check_date:
            current += 1
            check_date -= timedelta(days=1)
        elif session_date < check_date:
            break
    
    return current


def _get_daily_study_minutes(user_id: int, db: Session) -> Dict[str, float]:
    """Get daily study minutes for last 7 days"""
    daily = {}
    
    for i in range(7):
        date = (datetime.utcnow() - timedelta(days=i)).date()
        sessions = db.query(StudySessionDB).filter(
            StudySessionDB.user_id == user_id,
            func.date(StudySessionDB.created_at) == date
        ).all()
        
        total_minutes = sum(s.duration_minutes for s in sessions)
        daily[str(date)] = total_minutes
    
    return daily


def _get_accuracy_by_topic(user_id: int, db: Session) -> Dict[str, float]:
    """Get accuracy by topic"""
    accuracy = {}
    
    topics = db.query(FlashcardDB.topic).filter(
        FlashcardDB.user_id == user_id
    ).distinct().all()
    
    for topic_tuple in topics:
        topic = topic_tuple[0]
        if not topic:
            continue
        
        # Get attempts for cards in this topic
        attempts = db.query(QuizAttemptDB).join(
            FlashcardDB, QuizAttemptDB.flashcard_id == FlashcardDB.id
        ).filter(
            FlashcardDB.user_id == user_id,
            FlashcardDB.topic == topic
        ).all()
        
        if attempts:
            topic_accuracy = sum(1 for a in attempts if a.is_correct) / len(attempts)
            accuracy[topic] = topic_accuracy
    
    return accuracy


@router.get("/cards-by-difficulty")
def get_cards_by_difficulty(token: str, db: Session = Depends(get_db)):
    """Get card count by difficulty level"""
    user = get_current_user(token, db)
    
    difficulties = {}
    for difficulty in ["easy", "medium", "hard"]:
        count = db.query(func.count(FlashcardDB.id)).filter(
            FlashcardDB.user_id == user.id,
            FlashcardDB.difficulty == difficulty
        ).scalar() or 0
        difficulties[difficulty] = count
    
    return difficulties
