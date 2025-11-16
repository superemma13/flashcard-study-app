"""Flashcard routes"""
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db import get_db, UserDB, FlashcardDB, decode_token
from app.models import FlashcardCreate, FlashcardUpdate, FlashcardResponse
from app.services.llm_service import OllamaService, VectorEmbeddingService
from datetime import datetime
import json

router = APIRouter(prefix="/api/flashcards", tags=["flashcards"])


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


@router.get("/", response_model=List[FlashcardResponse])
def get_flashcards(
    token: str,
    topic: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get user's flashcards with optional filtering"""
    user = get_current_user(token, db)
    
    query = db.query(FlashcardDB).filter(FlashcardDB.user_id == user.id)
    
    if topic:
        query = query.filter(FlashcardDB.topic == topic)
    
    if difficulty:
        query = query.filter(FlashcardDB.difficulty == difficulty)
    
    flashcards = query.all()
    return [FlashcardResponse.from_orm(card) for card in flashcards]


@router.get("/{flashcard_id}", response_model=FlashcardResponse)
def get_flashcard(
    flashcard_id: int,
    token: str,
    db: Session = Depends(get_db)
):
    """Get a specific flashcard"""
    user = get_current_user(token, db)
    flashcard = db.query(FlashcardDB).filter(
        FlashcardDB.id == flashcard_id,
        FlashcardDB.user_id == user.id
    ).first()
    
    if not flashcard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flashcard not found"
        )
    
    return FlashcardResponse.from_orm(flashcard)


@router.post("/", response_model=FlashcardResponse)
def create_flashcard(
    card_data: FlashcardCreate,
    token: str,
    db: Session = Depends(get_db)
):
    """Create a new flashcard"""
    user = get_current_user(token, db)
    
    # Generate embedding
    embedding_vector = VectorEmbeddingService.simple_embedding(
        card_data.question + " " + card_data.answer
    )
    
    new_card = FlashcardDB(
        user_id=user.id,
        question=card_data.question,
        answer=card_data.answer,
        topic=card_data.topic,
        difficulty=card_data.difficulty,
        embedding=json.dumps(embedding_vector)
    )
    
    db.add(new_card)
    db.commit()
    db.refresh(new_card)
    
    return FlashcardResponse.from_orm(new_card)


@router.put("/{flashcard_id}", response_model=FlashcardResponse)
def update_flashcard(
    flashcard_id: int,
    update_data: FlashcardUpdate,
    token: str,
    db: Session = Depends(get_db)
):
    """Update a flashcard"""
    user = get_current_user(token, db)
    flashcard = db.query(FlashcardDB).filter(
        FlashcardDB.id == flashcard_id,
        FlashcardDB.user_id == user.id
    ).first()
    
    if not flashcard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flashcard not found"
        )
    
    # Update fields
    if update_data.question:
        flashcard.question = update_data.question
    if update_data.answer:
        flashcard.answer = update_data.answer
    if update_data.topic:
        flashcard.topic = update_data.topic
    if update_data.difficulty:
        flashcard.difficulty = update_data.difficulty
    
    # Regenerate embedding if question or answer changed
    if update_data.question or update_data.answer:
        embedding_vector = VectorEmbeddingService.simple_embedding(
            flashcard.question + " " + flashcard.answer
        )
        flashcard.embedding = json.dumps(embedding_vector)
    
    db.commit()
    db.refresh(flashcard)
    
    return FlashcardResponse.from_orm(flashcard)


@router.delete("/{flashcard_id}")
def delete_flashcard(
    flashcard_id: int,
    token: str,
    db: Session = Depends(get_db)
):
    """Delete a flashcard"""
    user = get_current_user(token, db)
    flashcard = db.query(FlashcardDB).filter(
        FlashcardDB.id == flashcard_id,
        FlashcardDB.user_id == user.id
    ).first()
    
    if not flashcard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flashcard not found"
        )
    
    db.delete(flashcard)
    db.commit()
    
    return {"message": "Flashcard deleted successfully"}


@router.post("/generate-from-text")
async def generate_flashcards_from_text(
    text: str,
    token: str,
    topic: str = "General",
    num_cards: int = 5,
    difficulty: str = "medium",
    db: Session = Depends(get_db)
):
    """Generate flashcards from text using Ollama"""
    user = get_current_user(token, db)
    
    # Generate flashcards using LLM
    ollama_service = OllamaService()
    generated_cards = await ollama_service.generate_flashcards(
        text=text,
        num_cards=num_cards,
        difficulty=difficulty
    )
    
    if not generated_cards:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate flashcards. Is Ollama running?"
        )
    
    # Save to database
    created_cards = []
    for card_data in generated_cards:
        embedding_vector = VectorEmbeddingService.simple_embedding(
            card_data["question"] + " " + card_data["answer"]
        )
        
        new_card = FlashcardDB(
            user_id=user.id,
            question=card_data["question"],
            answer=card_data["answer"],
            topic=topic,
            difficulty=difficulty,
            embedding=json.dumps(embedding_vector)
        )
        
        db.add(new_card)
        created_cards.append(new_card)
    
    db.commit()
    
    return {
        "created": len(created_cards),
        "cards": [FlashcardResponse.from_orm(card) for card in created_cards]
    }


@router.get("/topics/list")
def get_topics(token: str, db: Session = Depends(get_db)):
    """Get all topics for current user"""
    user = get_current_user(token, db)
    
    topics = db.query(FlashcardDB.topic).filter(
        FlashcardDB.user_id == user.id
    ).distinct().all()
    
    return {"topics": [t[0] for t in topics if t[0]]}
