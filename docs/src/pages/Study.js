import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api';
import { useStore } from '../store';
import '../styles/Study.css';

function Study() {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const isAuthenticated = useStore((state) => state.isAuthenticated);

  const [cards, setCards] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  const [loading, setLoading] = useState(true);
  const [sessionStats, setSessionStats] = useState({ correct: 0, total: 0 });
  const [adaptiveDifficulty, setAdaptiveDifficulty] = useState('medium');
  const [startTime, setStartTime] = useState(Date.now());

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    
    loadCards();
  }, [isAuthenticated, navigate, sessionId]);

  const loadCards = async () => {
    try {
      const data = await api.getCardsForSession(sessionId, adaptiveDifficulty);
      setCards(data.cards || []);
      setLoading(false);
    } catch (error) {
      console.error('Failed to load cards:', error);
      setLoading(false);
    }
  };

  const handleAnswer = async (isCorrect) => {
    const responseTime = Math.round((Date.now() - startTime) / 1000);
    
    try {
      await api.submitQuizAnswer(
        sessionId,
        cards[currentIndex].id,
        isCorrect,
        responseTime
      );
      
      const newStats = {
        correct: sessionStats.correct + (isCorrect ? 1 : 0),
        total: sessionStats.total + 1
      };
      setSessionStats(newStats);
      
      // Update adaptive difficulty
      const adaptive = await api.getAdaptiveDifficulty(sessionId);
      setAdaptiveDifficulty(adaptive.recommended_difficulty);
      
      // Move to next card or finish
      if (currentIndex < cards.length - 1) {
        setCurrentIndex(currentIndex + 1);
        setShowAnswer(false);
        setStartTime(Date.now());
      } else {
        completeSession();
      }
    } catch (error) {
      console.error('Failed to submit answer:', error);
    }
  };

  const completeSession = async () => {
    try {
      await api.completeStudySession(sessionId);
      navigate('/dashboard');
    } catch (error) {
      console.error('Failed to complete session:', error);
    }
  };

  if (loading) return <div className="loading">Loading cards...</div>;
  if (cards.length === 0) return <div className="loading">No cards available</div>;

  const currentCard = cards[currentIndex];
  const progress = ((currentIndex + 1) / cards.length) * 100;

  return (
    <div className="study-container">
      <div className="study-header">
        <h1>Quiz Mode</h1>
        <div className="study-stats">
          <span>Correct: {sessionStats.correct}/{sessionStats.total}</span>
          <span>Difficulty: {adaptiveDifficulty}</span>
        </div>
      </div>

      <div className="progress-bar">
        <div className="progress" style={{ width: `${progress}%` }}></div>
      </div>

      <div className="flashcard">
        <div className="card-counter">
          Card {currentIndex + 1} of {cards.length}
        </div>
        
        <div className="card-content">
          <h2>Question:</h2>
          <p className="question">{currentCard.question}</p>
          
          {showAnswer && (
            <>
              <h2>Answer:</h2>
              <p className="answer">{currentCard.answer}</p>
            </>
          )}
        </div>

        {!showAnswer ? (
          <button className="primary-btn" onClick={() => setShowAnswer(true)}>
            Reveal Answer
          </button>
        ) : (
          <div className="answer-buttons">
            <button className="btn-incorrect" onClick={() => handleAnswer(false)}>
              ✗ Incorrect
            </button>
            <button className="btn-correct" onClick={() => handleAnswer(true)}>
              ✓ Correct
            </button>
          </div>
        )}
      </div>

      <button className="end-btn" onClick={completeSession}>
        End Session
      </button>
    </div>
  );
}

export default Study;
