/**
 * Zustand store for application state
 */

import create from 'zustand';

export const useStore = create((set) => ({
  // Auth state
  user: null,
  isAuthenticated: !!localStorage.getItem('access_token'),
  
  setUser: (user) => set({ user, isAuthenticated: !!user }),
  logout: () => {
    localStorage.removeItem('access_token');
    set({ user: null, isAuthenticated: false });
  },
  
  // Study session state
  currentSession: null,
  currentCards: [],
  currentCardIndex: 0,
  sessionStats: {
    correct: 0,
    total: 0,
    accuracy: 0
  },
  
  setCurrentSession: (session) => set({ currentSession: session }),
  setCurrentCards: (cards) => set({ currentCards: cards, currentCardIndex: 0 }),
  
  updateSessionStats: (correct, total) => set({
    sessionStats: {
      correct,
      total,
      accuracy: total > 0 ? (correct / total * 100).toFixed(1) : 0
    }
  }),
  
  nextCard: () => set((state) => ({
    currentCardIndex: Math.min(state.currentCardIndex + 1, state.currentCards.length - 1)
  })),
  
  // Analytics state
  analytics: null,
  setAnalytics: (analytics) => set({ analytics }),
}));
