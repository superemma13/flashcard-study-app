from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import enum
from app.config import settings

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class UserDB(Base):
    """User database model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    flashcards = relationship("FlashcardDB", back_populates="owner")
    study_sessions = relationship("StudySessionDB", back_populates="user")


class FlashcardDB(Base):
    """Flashcard database model"""
    __tablename__ = "flashcards"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    question = Column(String)
    answer = Column(String)
    topic = Column(String, index=True)
    difficulty = Column(String, default="medium")
    review_count = Column(Integer, default=0)
    difficulty_score = Column(Float, default=0.5)  # 0-1, higher = harder
    embedding = Column(String, nullable=True)  # JSON string of vector
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    last_reviewed = Column(DateTime, nullable=True, index=True)
    
    # Relationships
    owner = relationship("UserDB", back_populates="flashcards")
    quiz_attempts = relationship("QuizAttemptDB", back_populates="flashcard")


class StudySessionDB(Base):
    """Study session database model"""
    __tablename__ = "study_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    topic = Column(String, nullable=True)
    status = Column(String, default="active")  # active, completed, paused
    cards_studied = Column(Integer, default=0)
    cards_correct = Column(Integer, default=0)
    duration_minutes = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("UserDB", back_populates="study_sessions")
    quiz_attempts = relationship("QuizAttemptDB", back_populates="study_session")


class QuizAttemptDB(Base):
    """Quiz attempt database model"""
    __tablename__ = "quiz_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    study_session_id = Column(Integer, ForeignKey("study_sessions.id"))
    flashcard_id = Column(Integer, ForeignKey("flashcards.id"))
    is_correct = Column(Boolean)
    response_time_seconds = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    study_session = relationship("StudySessionDB", back_populates="quiz_attempts")
    flashcard = relationship("FlashcardDB", back_populates="quiz_attempts")


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database"""
    Base.metadata.create_all(bind=engine)
