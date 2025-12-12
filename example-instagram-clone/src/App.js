import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Header from './components/Header';
import Feed from './components/Feed';
import Profile from './components/Profile';
import Login from './components/Login';
import Register from './components/Register';
import CreatePost from './components/CreatePost';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import './App.css';

function AppContent() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="loading">
        <div>Loading...</div>
      </div>
    );
  }

  return (
    <div className="App">
      <Router>
        {user && <Header />}
        <main className="main-content">
          <Routes>
            {user ? (
              <>
                <Route path="/" element={<Feed />} />
                <Route path="/profile/:username" element={<Profile />} />
                <Route path="/create" element={<CreatePost />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </>
            ) : (
              <>
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route path="*" element={<Navigate to="/login" replace />} />
              </>
            )}
          </Routes>
        </main>
      </Router>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
