import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import api from './api';
import { useStore } from './store';

import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Study from './pages/Study';
import GenerateFlashcards from './pages/GenerateFlashcards';

import './App.css';

function App() {
  const isAuthenticated = useStore((state) => state.isAuthenticated);
  const setUser = useStore((state) => state.setUser);

  useEffect(() => {
    if (isAuthenticated) {
      // Try to load user data
      api.getCurrentUser().then(setUser).catch(() => {
        useStore.getState().logout();
      });
    }
  }, [isAuthenticated, setUser]);

  return (
    <BrowserRouter basename={process.env.PUBLIC_URL || '/'}>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/study/:sessionId" element={<Study />} />
        <Route path="/generate" element={<GenerateFlashcards />} />
        <Route path="/" element={isAuthenticated ? <Navigate to="/dashboard" /> : <Navigate to="/login" />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
