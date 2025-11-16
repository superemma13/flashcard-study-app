import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import { useStore } from '../store';
import '../styles/Dashboard.css';

function Dashboard() {
  const [analytics, setAnalytics] = useState(null);
  const [topics, setTopics] = useState([]);
  const [selectedTopic, setSelectedTopic] = useState('');
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const user = useStore((state) => state.user);
  const isAuthenticated = useStore((state) => state.isAuthenticated);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    
    loadAnalytics();
    loadTopics();
  }, [isAuthenticated, navigate]);

  const loadAnalytics = async () => {
    try {
      const data = await api.getAnalyticsDashboard();
      setAnalytics(data);
    } catch (error) {
      console.error('Failed to load analytics:', error);
    }
  };

  const loadTopics = async () => {
    try {
      const data = await api.getTopics();
      setTopics(data.topics || []);
    } catch (error) {
      console.error('Failed to load topics:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStartStudy = async () => {
    try {
      const session = await api.startStudySession(selectedTopic || null);
      navigate(`/study/${session.id}`, { state: { session } });
    } catch (error) {
      console.error('Failed to start study session:', error);
    }
  };

  if (loading) return <div className="loading">Loading...</div>;

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Welcome, {user?.username || 'Student'}!</h1>
        <button className="logout-btn" onClick={() => {
          useStore.getState().logout();
          navigate('/login');
        }}>
          Logout
        </button>
      </div>

      {analytics && (
        <div className="analytics-grid">
          <div className="stat-card">
            <h3>Total Cards</h3>
            <p className="stat-value">{analytics.total_cards}</p>
          </div>
          <div className="stat-card">
            <h3>Study Sessions</h3>
            <p className="stat-value">{analytics.total_sessions}</p>
          </div>
          <div className="stat-card">
            <h3>Average Accuracy</h3>
            <p className="stat-value">{(analytics.average_accuracy * 100).toFixed(1)}%</p>
          </div>
          <div className="stat-card">
            <h3>Study Time</h3>
            <p className="stat-value">{analytics.total_study_minutes.toFixed(1)}m</p>
          </div>
          <div className="stat-card">
            <h3>Current Streak</h3>
            <p className="stat-value">{analytics.current_streak}</p>
          </div>
          <div className="stat-card">
            <h3>Cards Due</h3>
            <p className="stat-value">{analytics.cards_due_for_review}</p>
          </div>
        </div>
      )}

      <div className="study-section">
        <h2>Start Study Session</h2>
        <div className="topic-selector">
          <label>Select Topic:</label>
          <select
            value={selectedTopic}
            onChange={(e) => setSelectedTopic(e.target.value)}
          >
            <option value="">All Topics</option>
            {topics.map((topic) => (
              <option key={topic} value={topic}>
                {topic}
              </option>
            ))}
          </select>
        </div>
        <button className="primary-btn" onClick={handleStartStudy}>
          Start Studying
        </button>
      </div>

      <div className="quick-links">
        <a href="/flashcards" className="link-btn">Manage Flashcards</a>
        <a href="/generate" className="link-btn">Generate from Text</a>
        <a href="/analytics" className="link-btn">View Analytics</a>
      </div>
    </div>
  );
}

export default Dashboard;
