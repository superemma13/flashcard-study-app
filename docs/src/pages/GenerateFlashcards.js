import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import { useStore } from '../store';
import '../styles/GenerateFlashcards.css';

function GenerateFlashcards() {
  const [text, setText] = useState('');
  const [topic, setTopic] = useState('');
  const [numCards, setNumCards] = useState(5);
  const [difficulty, setDifficulty] = useState('medium');
  const [loading, setLoading] = useState(false);
  const [generatedCards, setGeneratedCards] = useState([]);
  const navigate = useNavigate();
  const isAuthenticated = useStore((state) => state.isAuthenticated);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
    }
  }, [isAuthenticated, navigate]);

  const handleGenerate = async (e) => {
    e.preventDefault();
    
    if (!text.trim() || !topic.trim()) {
      alert('Please enter text and topic');
      return;
    }

    setLoading(true);
    try {
      const response = await api.generateFlashcardsFromText(
        text,
        topic,
        numCards,
        difficulty
      );
      setGeneratedCards(response.cards || []);
    } catch (error) {
      alert('Failed to generate flashcards. Make sure Ollama is running.');
      console.error('Failed to generate:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="generate-container">
      <div className="generate-header">
        <a href="/dashboard">← Back</a>
        <h1>Generate Flashcards from Text</h1>
      </div>

      <form onSubmit={handleGenerate} className="generate-form">
        <div className="form-group">
          <label>Text to Generate From:</label>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste or type the text you want to convert to flashcards..."
            rows="8"
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Topic:</label>
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g., Biology, History"
            />
          </div>

          <div className="form-group">
            <label>Number of Cards:</label>
            <input
              type="number"
              value={numCards}
              onChange={(e) => setNumCards(parseInt(e.target.value))}
              min="1"
              max="20"
            />
          </div>

          <div className="form-group">
            <label>Difficulty:</label>
            <select
              value={difficulty}
              onChange={(e) => setDifficulty(e.target.value)}
            >
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>
          </div>
        </div>

        <button type="submit" disabled={loading} className="primary-btn">
          {loading ? 'Generating...' : 'Generate Flashcards'}
        </button>
      </form>

      {generatedCards.length > 0 && (
        <div className="generated-cards">
          <h2>Generated Flashcards ({generatedCards.length})</h2>
          <div className="cards-list">
            {generatedCards.map((card, index) => (
              <div key={index} className="generated-card">
                <div className="card-question">
                  <strong>Q:</strong> {card.question}
                </div>
                <div className="card-answer">
                  <strong>A:</strong> {card.answer}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default GenerateFlashcards;
