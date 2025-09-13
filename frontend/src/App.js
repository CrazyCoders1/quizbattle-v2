import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './contexts/AuthContext';
import Layout from './components/Layout/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Challenges from './pages/Challenges';
import Practice from './pages/Practice';
import Leaderboard from './pages/Leaderboard';
import Admin from './pages/Admin';
import PlayChallenge from './pages/PlayChallenge';
import './index.css';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/" element={<Layout><Home /></Layout>} />
            <Route path="/challenges" element={<Layout><ProtectedRoute><Challenges /></ProtectedRoute></Layout>} />
            <Route path="/challenges/:challengeId/play" element={<ProtectedRoute><PlayChallenge /></ProtectedRoute>} />
            <Route path="/practice" element={<Layout><ProtectedRoute><Practice /></ProtectedRoute></Layout>} />
            <Route path="/leaderboard" element={<Layout><ProtectedRoute><Leaderboard /></ProtectedRoute></Layout>} />
            <Route path="/admin" element={<Layout><ProtectedRoute requireAdmin><Admin /></ProtectedRoute></Layout>} />
          </Routes>
          <Toaster position="top-right" />
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
