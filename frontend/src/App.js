import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import MentorChat from './pages/MentorChat';
import ConceptBrowser from './pages/ConceptBrowser';
import LearningPath from './pages/LearningPath';
import Dashboard from './pages/Dashboard';
import './App.css';

const API = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const ApiContext = React.createContext(API);

function App() {
  return (
    <ApiContext.Provider value={API}>
      <BrowserRouter>
        <div className="app">
          <nav className="sidebar">
            <div className="logo">
              <span className="logo-icon">🧠</span>
              <span className="logo-text">NeuroForge</span>
            </div>
            <div className="nav-links">
              <NavLink to="/" end className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
                <span className="nav-icon">📊</span> Dashboard
              </NavLink>
              <NavLink to="/mentor" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
                <span className="nav-icon">🤖</span> AI Mentor
              </NavLink>
              <NavLink to="/concepts" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
                <span className="nav-icon">📚</span> Concepts
              </NavLink>
              <NavLink to="/paths" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
                <span className="nav-icon">🛤️</span> Learning Paths
              </NavLink>
            </div>
            <div className="user-info">
              <div className="user-avatar">DL</div>
              <div className="user-details">
                <div className="user-name">Demo Learner</div>
                <div className="user-role">Learner</div>
              </div>
            </div>
          </nav>
          <main className="main-content">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/mentor" element={<MentorChat />} />
              <Route path="/concepts" element={<ConceptBrowser />} />
              <Route path="/paths" element={<LearningPath />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </ApiContext.Provider>
  );
}

export default App;
