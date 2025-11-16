/**
 * API service for communicating with backend
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

class APIService {
  constructor() {
    this.token = localStorage.getItem('access_token');
  }

  setToken(token) {
    this.token = token;
    localStorage.setItem('access_token', token);
  }

  getAuthHeaders() {
    return {
      'Content-Type': 'application/json',
      ...(this.token && { 'Authorization': `Bearer ${this.token}` })
    };
  }

  async request(method, endpoint, data = null) {
    try {
      const config = {
        method,
        headers: this.getAuthHeaders(),
      };

      if (data) {
        config.body = JSON.stringify(data);
      }

      const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

      if (!response.ok) {
        if (response.status === 401) {
          localStorage.removeItem('access_token');
          window.location.href = '/login';
        }
        throw new Error(`API error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Auth endpoints
  async register(email, username, password) {
    return this.request('POST', '/auth/register', { email, username, password });
  }

  async login(email, password) {
    return this.request('POST', '/auth/login', { email, password });
  }

  async getCurrentUser() {
    return this.request('GET', `/auth/me?token=${this.token}`);
  }

  // Flashcard endpoints
  async getFlashcards(topic = null, difficulty = null) {
    let url = '/flashcards/?token=' + this.token;
    if (topic) url += `&topic=${topic}`;
    if (difficulty) url += `&difficulty=${difficulty}`;
    return this.request('GET', url);
  }

  async getFlashcard(id) {
    return this.request('GET', `/flashcards/${id}?token=${this.token}`);
  }

  async createFlashcard(question, answer, topic, difficulty = 'medium') {
    return this.request('POST', '/flashcards/?token=' + this.token, {
      question,
      answer,
      topic,
      difficulty
    });
  }

  async updateFlashcard(id, data) {
    return this.request('PUT', `/flashcards/${id}?token=${this.token}`, data);
  }

  async deleteFlashcard(id) {
    return this.request('DELETE', `/flashcards/${id}?token=${this.token}`);
  }

  async generateFlashcardsFromText(text, topic, num_cards = 5, difficulty = 'medium') {
    return this.request('POST', '/flashcards/generate-from-text?token=' + this.token, {
      text,
      topic,
      num_cards,
      difficulty
    });
  }

  async getTopics() {
    return this.request('GET', `/flashcards/topics/list?token=${this.token}`);
  }

  // Study endpoints
  async startStudySession(topic = null, target_count = 10) {
    return this.request('POST', `/study/session/start?token=${this.token}`, {
      topic,
      target_count
    });
  }

  async getStudySession(sessionId) {
    return this.request('GET', `/study/session/${sessionId}?token=${this.token}`);
  }

  async getCardsForSession(sessionId, difficulty = null, limit = 10) {
    let url = `/study/cards-for-session/${sessionId}?token=${this.token}&limit=${limit}`;
    if (difficulty) url += `&difficulty=${difficulty}`;
    return this.request('GET', url);
  }

  async submitQuizAnswer(sessionId, flashcardId, isCorrect, responseTime) {
    return this.request('POST', `/study/quiz/answer?session_id=${sessionId}&token=${this.token}`, {
      flashcard_id: flashcardId,
      is_correct: isCorrect,
      response_time_seconds: responseTime
    });
  }

  async getAdaptiveDifficulty(sessionId) {
    return this.request('GET', `/study/adaptive-difficulty/${sessionId}?token=${this.token}`);
  }

  async completeStudySession(sessionId) {
    return this.request('POST', `/study/session/${sessionId}/complete?token=${this.token}`);
  }

  // Analytics endpoints
  async getAnalyticsDashboard() {
    return this.request('GET', `/analytics/dashboard?token=${this.token}`);
  }

  async getCardsByDifficulty() {
    return this.request('GET', `/analytics/cards-by-difficulty?token=${this.token}`);
  }
}

export default new APIService();
