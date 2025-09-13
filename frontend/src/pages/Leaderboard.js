import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { apiService } from '../services/apiService';
import toast from 'react-hot-toast';

const Leaderboard = () => {
  const { isAuthenticated } = useAuth();
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);
  const [viewType, setViewType] = useState('global'); // 'global' or 'challenge'
  const [challenges, setChallenges] = useState([]);
  const [selectedChallenge, setSelectedChallenge] = useState(null);

  useEffect(() => {
    if (isAuthenticated) {
      fetchLeaderboard();
      fetchChallenges();
    } else {
      setLoading(false);
    }
  }, [isAuthenticated]);

  useEffect(() => {
    if (isAuthenticated) {
      fetchLeaderboard();
    }
  }, [viewType, selectedChallenge]);

  const fetchLeaderboard = async () => {
    try {
      const challengeId = viewType === 'challenge' ? selectedChallenge : null;
      const response = await apiService.getLeaderboard(viewType, challengeId);
      setLeaderboard(response.data.leaderboard || []);
    } catch (error) {
      toast.error('Failed to fetch leaderboard');
    } finally {
      setLoading(false);
    }
  };

  const fetchChallenges = async () => {
    try {
      const response = await apiService.getChallenges();
      setChallenges(response.data.challenges || []);
    } catch (error) {
      console.error('Failed to fetch challenges:', error);
    }
  };

  const getRankIcon = (rank) => {
    if (rank === 1) return '🥇';
    if (rank === 2) return '🥈';
    if (rank === 3) return '🥉';
    return `#${rank}`;
  };

  const getRankColor = (rank) => {
    if (rank === 1) return 'bg-yellow-100 text-yellow-800';
    if (rank === 2) return 'bg-gray-100 text-gray-800';
    if (rank === 3) return 'bg-orange-100 text-orange-800';
    return 'bg-gray-50 text-gray-700';
  };

  if (!isAuthenticated) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Please Login to View Leaderboard</h2>
        <p className="text-gray-600 mb-6">You need to be logged in to view the leaderboard.</p>
        <a
          href="/login"
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
        >
          Login Now
        </a>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Leaderboard</h1>
        <p className="text-gray-600">See how you rank against other players</p>
      </div>

      {/* View Type Selector */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex justify-center space-x-4 mb-6">
          <button
            onClick={() => setViewType('global')}
            className={`px-6 py-3 rounded-lg font-medium transition-colors ${
              viewType === 'global'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Global Leaderboard
          </button>
          <button
            onClick={() => setViewType('challenge')}
            className={`px-6 py-3 rounded-lg font-medium transition-colors ${
              viewType === 'challenge'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Challenge Leaderboard
          </button>
        </div>

        {viewType === 'challenge' && (
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Challenge
            </label>
            <select
              value={selectedChallenge || ''}
              onChange={(e) => setSelectedChallenge(e.target.value || null)}
              className="w-full max-w-md mx-auto px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Select a challenge</option>
              {challenges.map((challenge) => (
                <option key={challenge.id} value={challenge.id}>
                  {challenge.name} ({challenge.code})
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* Leaderboard */}
      {leaderboard.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">📊</div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            {viewType === 'global' ? 'No Global Rankings Yet' : 'No Challenge Rankings Yet'}
          </h3>
          <p className="text-gray-600 mb-6">
            {viewType === 'global' 
              ? 'Complete some quizzes to appear on the global leaderboard!'
              : 'Select a challenge to view its leaderboard or complete challenges to see rankings.'
            }
          </p>
          <a
            href="/practice"
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
          >
            Start Practicing
          </a>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">
              {viewType === 'global' ? 'Global Rankings' : 'Challenge Rankings'}
            </h2>
          </div>
          
          <div className="divide-y divide-gray-200">
            {leaderboard.map((entry, index) => (
              <div key={entry.id || index} className="px-6 py-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg ${getRankColor(index + 1)}`}>
                      {getRankIcon(index + 1)}
                    </div>
                    
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">
                        {entry.username || entry.user?.username}
                      </h3>
                      <p className="text-sm text-gray-600">
                        {entry.challenges_completed || 0} challenges completed
                      </p>
                    </div>
                  </div>
                  
                  <div className="text-right">
                    <div className="text-2xl font-bold text-blue-600">
                      {entry.total_score || entry.score || 0}
                    </div>
                    <div className="text-sm text-gray-600">points</div>
                  </div>
                </div>
                
                {entry.last_updated && (
                  <div className="mt-2 text-xs text-gray-500">
                    Last updated: {new Date(entry.last_updated).toLocaleDateString()}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Stats Summary */}
      {leaderboard.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow-md p-6 text-center">
            <div className="text-3xl font-bold text-blue-600 mb-2">
              {leaderboard.length}
            </div>
            <div className="text-gray-600">Total Players</div>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-6 text-center">
            <div className="text-3xl font-bold text-green-500 mb-2">
              {leaderboard.length > 0 ? leaderboard[0].total_score || leaderboard[0].score || 0 : 0}
            </div>
            <div className="text-gray-600">Highest Score</div>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-6 text-center">
            <div className="text-3xl font-bold text-purple-500 mb-2">
              {leaderboard.length > 0 
                ? Math.round(leaderboard.reduce((sum, entry) => sum + (entry.total_score || entry.score || 0), 0) / leaderboard.length)
                : 0
              }
            </div>
            <div className="text-gray-600">Average Score</div>
          </div>
        </div>
      )}

      {/* How to Improve */}
      <div className="bg-blue-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-4">How to Improve Your Ranking</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="flex items-start space-x-3">
            <div className="bg-blue-100 rounded-full p-2">
              <span className="text-blue-600">📚</span>
            </div>
            <div>
              <h4 className="font-semibold text-blue-900">Practice Regularly</h4>
              <p className="text-sm text-blue-800">Take practice quizzes to improve your knowledge and speed.</p>
            </div>
          </div>
          
          <div className="flex items-start space-x-3">
            <div className="bg-blue-100 rounded-full p-2">
              <span className="text-blue-600">🏆</span>
            </div>
            <div>
              <h4 className="font-semibold text-blue-900">Join Challenges</h4>
              <p className="text-sm text-blue-800">Participate in competitive challenges to earn more points.</p>
            </div>
          </div>
          
          <div className="flex items-start space-x-3">
            <div className="bg-blue-100 rounded-full p-2">
              <span className="text-blue-600">⚡</span>
            </div>
            <div>
              <h4 className="font-semibold text-blue-900">Answer Quickly</h4>
              <p className="text-sm text-blue-800">Time management is key - don't spend too long on any question.</p>
            </div>
          </div>
          
          <div className="flex items-start space-x-3">
            <div className="bg-blue-100 rounded-full p-2">
              <span className="text-blue-600">🎯</span>
            </div>
            <div>
              <h4 className="font-semibold text-blue-900">Focus on Accuracy</h4>
              <p className="text-sm text-blue-800">Correct answers give +4 points, wrong answers give -1 point.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Leaderboard;
