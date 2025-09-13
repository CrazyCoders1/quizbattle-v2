import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Home = () => {
  const { isAuthenticated, isAdmin } = useAuth();

  const features = [
    {
      title: 'Challenges',
      description: 'Join competitive quiz challenges and compete with others',
      icon: '🏆',
      link: '/challenges',
      color: 'bg-blue-500 hover:bg-blue-600'
    },
    {
      title: 'Practice',
      description: 'Practice with quizzes by exam type and difficulty',
      icon: '📚',
      link: '/practice',
      color: 'bg-green-500 hover:bg-green-600'
    },
    {
      title: 'Leaderboard',
      description: 'Check your ranking and see top performers',
      icon: '📊',
      link: '/leaderboard',
      color: 'bg-purple-500 hover:bg-purple-600'
    },
    {
      title: 'Admin Panel',
      description: 'Manage quizzes, users, and system settings',
      icon: '⚙️',
      link: '/admin',
      color: 'bg-gray-500 hover:bg-gray-600',
      adminOnly: true
    }
  ];

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Welcome to QuizBattle 🎯
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          Test your knowledge, compete with others, and climb the leaderboard!
        </p>
        
        {!isAuthenticated && (
          <div className="flex justify-center space-x-4">
            <Link
              to="/register"
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
            >
              Get Started
            </Link>
            <Link
              to="/login"
              className="bg-white hover:bg-gray-50 text-blue-600 border border-blue-600 px-6 py-3 rounded-lg font-medium transition-colors"
            >
              Login
            </Link>
          </div>
        )}
      </div>

      {/* Features Section - Admin tab always visible */}
      <div className="flex flex-wrap justify-center gap-6">
        {features.map((feature, index) => {
          const isDisabled = feature.adminOnly && !isAdmin; // Only disables click & styling

          return (
            <div
              key={index}
              className={`rounded-lg shadow-md transition-shadow p-6 h-full w-64 text-center
                ${isDisabled ? 'bg-gray-200 cursor-not-allowed' : 'bg-white hover:shadow-lg'}
              `}
            >
              <div className="text-4xl mb-4">{feature.icon}</div>
              <h3 className={`text-xl font-semibold mb-2 ${isDisabled ? 'text-gray-600' : 'text-gray-900'}`}>
                {feature.title}
              </h3>
              <p className={`mb-4 ${isDisabled ? 'text-gray-500' : 'text-gray-600'}`}>{feature.description}</p>

              {isDisabled ? (
                <div className="inline-block px-4 py-2 rounded-lg bg-gray-400 text-gray-700 font-medium cursor-not-allowed">
                  Admin Only
                </div>
              ) : (
                <Link
                  to={feature.link}
                  className={`inline-block px-4 py-2 rounded-lg text-white font-medium transition-colors ${feature.color}`}
                >
                  Go to {feature.title}
                </Link>
              )}
            </div>
          );
        })}
      </div>

      {/* Stats Section */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
          Platform Statistics
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600 mb-2">500+</div>
            <div className="text-gray-600">Questions Available</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-green-500 mb-2">1000+</div>
            <div className="text-gray-600">Active Users</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-purple-500 mb-2">50+</div>
            <div className="text-gray-600">Challenges Completed</div>
          </div>
        </div>
      </div>

      {/* How it Works */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
          How QuizBattle Works
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">📝</span>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">1. Choose Your Challenge</h3>
            <p className="text-gray-600">Select from available challenges or create your own</p>
          </div>
          <div className="text-center">
            <div className="bg-green-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">⚡</span>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">2. Answer Questions</h3>
            <p className="text-gray-600">Test your knowledge with timed multiple-choice questions</p>
          </div>
          <div className="text-center">
            <div className="bg-purple-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">🏆</span>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">3. Climb Leaderboard</h3>
            <p className="text-gray-600">See your score and compete with others globally</p>
          </div>
        </div>
      </div>

    </div>
  );
};

export default Home;
