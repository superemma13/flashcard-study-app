"""Study session and quiz routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db import get_db, UserDB, FlashcardDB, StudySessionDB, QuizAttemptDB, decode_token
from app.models import StudySessionResponse, QuizAttemptCreate, QuizAttemptResponse
from app.services.spaced_repetition import SpacedRepetitionScheduler
from datetime import datetime, timedelta
import json

router = APIRouter(prefix="/api/study", tags=["study"])


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


@router.post("/session/start", response_model=StudySessionResponse)
def start_study_session(
    topic: Optional[str] = None,
    target_count: int = 10,
    token: str = None,
    db: Session = Depends(get_db)
):
    """Start a new study session"""
    user = get_current_user(token, db)
    
    session = StudySessionDB(
        user_id=user.id,
        topic=topic,
        status="active"
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return StudySessionResponse.from_orm(session)


@router.get("/session/{session_id}", response_model=StudySessionResponse)
def get_session(
    session_id: int,
    token: str,
    db: Session = Depends(get_db)
):
    """Get study session details"""
    user = get_current_user(token, db)
    
    session = db.query(StudySessionDB).filter(
        StudySessionDB.id == session_id,
        StudySessionDB.user_id == user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return StudySessionResponse.from_orm(session)


@router.post("/session/{session_id}/complete")
def complete_session(
    session_id: int,
    token: str,
    db: Session = Depends(get_db)
):
    """Complete a study session"""
    user = get_current_user(token, db)
    
    session = db.query(StudySessionDB).filter(
        StudySessionDB.id == session_id,
        StudySessionDB.user_id == user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    session.status = "completed"
    session.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(session)
    
    return StudySessionResponse.from_orm(session)


@router.get("/cards-for-session/{session_id}")
def get_cards_for_session(
    session_id: int,
    token: str,
    difficulty: Optional[str] = None,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get cards to study for current session using spaced repetition"""
    user = get_current_user(token, db)
    
    session = db.query(StudySessionDB).filter(
        StudySessionDB.id == session_id,
        StudySessionDB.user_id == user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Get user's flashcards
    query = db.query(FlashcardDB).filter(FlashcardDB.user_id == user.id)
    
    if session.topic:
        query = query.filter(FlashcardDB.topic == session.topic)
    
    cards = query.all()
    
    # Use spaced repetition algorithm to select cards
    selected_cards = SpacedRepetitionScheduler.select_next_cards(
        cards,
        limit=limit,
        preferred_difficulty=difficulty
    )
    
    return {
        "cards": [
            {
                "id": card.id,
                "question": card.question,
                "topic": card.topic,
                "difficulty": card.difficulty
            }
            for card in selected_cards
        ]
    }


@router.post("/quiz/answer", response_model=QuizAttemptResponse)
def submit_quiz_answer(
    attempt_data: QuizAttemptCreate,
    session_id: int,
    token: str,
    db: Session = Depends(get_db)
):
    """Submit quiz answer and update spaced repetition"""
    user = get_current_user(token, db)
    
    session = db.query(StudySessionDB).filter(
        StudySessionDB.id == session_id,
        StudySessionDB.user_id == user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    flashcard = db.query(FlashcardDB).filter(
        FlashcardDB.id == attempt_data.flashcard_id,
        FlashcardDB.user_id == user.id
    ).first()
    
    if not flashcard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flashcard not found"
        )
    
    # Record quiz attempt
    quiz_attempt = QuizAttemptDB(
        study_session_id=session_id,
        flashcard_id=attempt_data.flashcard_id,
        is_correct=attempt_data.is_correct,
        response_time_seconds=attempt_data.response_time_seconds
    )
    
    db.add(quiz_attempt)
    
    # Update flashcard based on answer quality
    quality = 5 if attempt_data.is_correct else 1  # 0-5 scale
    
    next_review, easiness, interval = SpacedRepetitionScheduler.calculate_next_review(
        quality=quality,
        review_count=flashcard.review_count,
        easiness_factor=max(1.3, min(2.5, flashcard.review_count + 1.3))
    )
    
    flashcard.last_reviewed = datetime.utcnow()
    flashcard.review_count += 1
    
    # Update difficulty score based on performance
    avg_response = attempt_data.response_time_seconds
    flashcard.difficulty_score = SpacedRepetitionScheduler.update_difficulty_score(
        flashcard.difficulty_score,
        attempt_data.is_correct,
        attempt_data.response_time_seconds,
        avg_response
    )
    
    # Update session stats
    session.cards_studied += 1
    if attempt_data.is_correct:
        session.cards_correct += 1
    
    db.commit()
    db.refresh(quiz_attempt)
    
    return QuizAttemptResponse.from_orm(quiz_attempt)


@router.get("/adaptive-difficulty/{session_id}")
def get_adaptive_difficulty(
    session_id: int,
    token: str,
    db: Session = Depends(get_db)
):
    """Get recommended difficulty for adaptive quiz"""
    user = get_current_user(token, db)
    
    session = db.query(StudySessionDB).filter(
        StudySessionDB.id == session_id,
        StudySessionDB.user_id == user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Calculate accuracy
    attempts = db.query(QuizAttemptDB).filter(
        QuizAttemptDB.study_session_id == session_id
    ).all()
    
    if not attempts:
        return {"recommended_difficulty": "medium"}
    
    accuracy = sum(1 for a in attempts if a.is_correct) / len(attempts)
    
    # Adjust difficulty based on accuracy
    if accuracy > 0.8:
        difficulty = "hard"
    elif accuracy > 0.6:
        difficulty = "medium"
    else:
        difficulty = "easy"
    
    return {
        "recommended_difficulty": difficulty,
        "accuracy": accuracy,
        "attempts": len(attempts)
    }
