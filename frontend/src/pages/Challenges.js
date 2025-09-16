import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { apiService } from '../services/apiService';
import toast from 'react-hot-toast';

const Challenges = () => {
  const { isAuthenticated, isUser } = useAuth();
  const [challenges, setChallenges] = useState([]);
  const [completedChallenges, setCompletedChallenges] = useState([]);
  const [activeTab, setActiveTab] = useState('active');
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showJoinForm, setShowJoinForm] = useState(false);
  const [joinCode, setJoinCode] = useState('');
  const [isCreating, setIsCreating] = useState(false);
  const [isJoining, setIsJoining] = useState(false);
  const [createForm, setCreateForm] = useState({
    name: '',
    exam_type: 'CBSE 11',
    difficulty: 'easy',
    question_count: 10,
    time_limit: 30
  });

  useEffect(() => {
    if (isAuthenticated) {
      fetchChallenges();
    } else {
      setLoading(false);
    }
  }, [isAuthenticated]);

  const fetchChallenges = async () => {
    try {
      const [activeChallengesRes, completedChallengesRes] = await Promise.all([
        apiService.getChallenges(),
        apiService.getCompletedChallenges().catch(() => ({ data: { challenges: [] } }))
      ]);
      
      setChallenges(activeChallengesRes.data.challenges);
      setCompletedChallenges(completedChallengesRes.data.challenges);
    } catch (error) {
      toast.error('Failed to fetch challenges');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateChallenge = async (e) => {
    e.preventDefault();
    if (isCreating) return; // Prevent duplicate requests
    
    setIsCreating(true);
    try {
      const response = await apiService.createChallenge(createForm);
      toast.success('Challenge created successfully!');
      setShowCreateForm(false);
      setCreateForm({
        name: '',
        exam_type: 'CBSE 11',
        difficulty: 'easy',
        question_count: 10,
        time_limit: 30
      });
      await fetchChallenges();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to create challenge');
    } finally {
      setIsCreating(false);
    }
  };

  const handleJoinChallenge = async (e) => {
    e.preventDefault();
    if (isJoining) return; // Prevent duplicate requests
    
    setIsJoining(true);
    try {
      const response = await apiService.joinChallenge(joinCode);
      const challenge = response.data.challenge;
      toast.success(`Successfully joined "${challenge.name}"! Starting challenge...`);
      setShowJoinForm(false);
      setJoinCode('');
      
      // Small delay to let user see the success message, then redirect
      setTimeout(() => {
        window.location.href = `/challenges/${challenge.id}/play`;
      }, 1000);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to join challenge');
    } finally {
      setIsJoining(false);
    }
  };
  
  const handleJoinNowClick = async (challenge) => {
    try {
      // Join the challenge by code first
      const response = await apiService.joinChallenge(challenge.code);
      toast.success(`Joined "${challenge.name}"! Starting challenge...`);
      
      // Small delay, then redirect to play
      setTimeout(() => {
        window.location.href = `/challenges/${challenge.id}/play`;
      }, 500);
    } catch (error) {
      // If already joined, just go to play
      if (error.response?.status === 409) {
        toast.info('Already joined this challenge. Starting...');
        setTimeout(() => {
          window.location.href = `/challenges/${challenge.id}/play`;
        }, 500);
      } else {
        toast.error(error.response?.data?.error || 'Failed to join challenge');
      }
    }
  };

  const copyChallengeCode = (code) => {
    navigator.clipboard.writeText(code);
    toast.success('Challenge code copied to clipboard!');
  };

  if (!isAuthenticated) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Please Login to Access Challenges</h2>
        <p className="text-gray-600 mb-6">You need to be logged in to view and participate in challenges.</p>
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
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">🏆 Challenges</h1>
        <p className="text-gray-600 mb-6">Create competitive challenges or join existing ones to test your knowledge!</p>
        
        {/* Action Buttons - Prominent Display */}
        <div className="bg-gradient-to-r from-blue-50 to-green-50 rounded-xl p-6 mb-6">
          <div className="flex flex-col sm:flex-row justify-center gap-4">
            {isUser && (
              <button
                onClick={() => setShowCreateForm(true)}
                className="bg-green-600 hover:bg-green-700 text-white px-8 py-4 rounded-lg font-semibold text-lg transition-all transform hover:scale-105 flex items-center justify-center gap-2 shadow-lg"
              >
                <span className="text-xl">+</span>
                Create Challenge
              </button>
            )}
            <button
              onClick={() => setShowJoinForm(true)}
              className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-lg font-semibold text-lg transition-all transform hover:scale-105 flex items-center justify-center gap-2 shadow-lg"
            >
              <span className="text-xl">🔑</span>
              Join with Code
            </button>
          </div>
        </div>
      </div>
      
      {/* Tab Navigation */}
      <div className="bg-white rounded-lg shadow-md">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            <button
              onClick={() => setActiveTab('active')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'active'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <span className="mr-2">🎯</span>
              Active Challenges ({challenges.length})
            </button>
            <button
              onClick={() => setActiveTab('completed')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'completed'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <span className="mr-2">✅</span>
              Completed ({completedChallenges.length})
            </button>
          </nav>
        </div>
        
        <div className="p-6">
          {activeTab === 'active' && (
            <div>
              <h2 className="text-xl font-bold text-gray-900 mb-4">Active Challenges</h2>

      {/* Create Challenge Modal */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">Create New Challenge</h3>
            <form onSubmit={handleCreateChallenge}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Challenge Name
                  </label>
                  <input
                    type="text"
                    required
                    value={createForm.name}
                    onChange={(e) => setCreateForm({...createForm, name: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Enter challenge name"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Exam Type
                  </label>
                  <select
                    value={createForm.exam_type}
                    onChange={(e) => setCreateForm({...createForm, exam_type: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="CBSE 11">CBSE 11</option>
                    <option value="CBSE 12">CBSE 12</option>
                    <option value="JEE Main">JEE Main</option>
                    <option value="JEE Advanced">JEE Advanced</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Difficulty
                  </label>
                  <select
                    value={createForm.difficulty}
                    onChange={(e) => setCreateForm({...createForm, difficulty: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="easy">Easy</option>
                    <option value="medium">Medium</option>
                    <option value="tough">Tough</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Question Count
                  </label>
                  <input
                    type="number"
                    min="5"
                    max="50"
                    value={createForm.question_count}
                    onChange={(e) => setCreateForm({...createForm, question_count: parseInt(e.target.value)})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Time Limit (minutes)
                  </label>
                  <input
                    type="number"
                    min="5"
                    max="120"
                    value={createForm.time_limit}
                    onChange={(e) => setCreateForm({...createForm, time_limit: parseInt(e.target.value)})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>
              
              <div className="flex justify-end space-x-3 mt-6">
                <button
                  type="button"
                  onClick={() => setShowCreateForm(false)}
                  className="px-4 py-2 text-gray-700 bg-gray-200 hover:bg-gray-300 rounded-md transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isCreating}
                  className={`px-4 py-2 text-white rounded-md transition-colors ${
                    isCreating 
                      ? 'bg-gray-400 cursor-not-allowed' 
                      : 'bg-green-500 hover:bg-green-600'
                  }`}
                >
                  {isCreating ? (
                    <div className="flex items-center">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Creating...
                    </div>
                  ) : (
                    'Create'
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Join Challenge Modal */}
      {showJoinForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">Join Challenge</h3>
            <form onSubmit={handleJoinChallenge}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Challenge Code
                </label>
                <input
                  type="text"
                  required
                  value={joinCode}
                  onChange={(e) => setJoinCode(e.target.value.toUpperCase())}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Enter 6-character code"
                  maxLength="6"
                />
              </div>
              
              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setShowJoinForm(false)}
                  className="px-4 py-2 text-gray-700 bg-gray-200 hover:bg-gray-300 rounded-md transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isJoining}
                  className={`px-4 py-2 text-white rounded-md transition-colors ${
                    isJoining 
                      ? 'bg-gray-400 cursor-not-allowed' 
                      : 'bg-blue-600 hover:bg-blue-700'
                  }`}
                >
                  {isJoining ? (
                    <div className="flex items-center">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Joining...
                    </div>
                  ) : (
                    'Join'
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

        {/* Challenges List */}
        {challenges.length === 0 ? (
          <div className="text-center py-12">
          <div className="text-6xl mb-4">🏆</div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">No Active Challenges</h3>
          <p className="text-gray-600 mb-6">Be the first to create a challenge or join one!</p>
          {isUser && (
            <button
              onClick={() => setShowCreateForm(true)}
              className="bg-green-500 hover:bg-green-600 text-white px-6 py-3 rounded-lg font-medium transition-colors"
            >
              Create First Challenge
            </button>
          )}
        </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {challenges.map((challenge) => (
            <div key={challenge.id} className="bg-white rounded-lg shadow-md p-6">
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-lg font-semibold text-gray-900">{challenge.name}</h3>
                <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded">
                  {challenge.code}
                </span>
              </div>
              
              <div className="space-y-2 mb-4">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Exam Type:</span>
                  <span className="text-sm font-medium">{challenge.exam_type}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Difficulty:</span>
                  <span className={`text-sm font-medium px-2 py-1 rounded ${
                    challenge.difficulty === 'easy' ? 'bg-green-100 text-green-800' :
                    challenge.difficulty === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {challenge.difficulty}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Questions:</span>
                  <span className="text-sm font-medium">{challenge.question_count}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Time Limit:</span>
                  <span className="text-sm font-medium">{challenge.time_limit} min</span>
                </div>
              </div>
              
              <div className="flex space-x-2">
                <button
                  onClick={() => copyChallengeCode(challenge.code)}
                  className="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                >
                  Copy Code
                </button>
                <button
                  onClick={() => handleJoinNowClick(challenge)}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-md text-sm font-medium transition-colors"
                >
                  Join & Play
                </button>
              </div>
            </div>
          ))}
              </div>
            )}
          </div>
        )}
        
        {activeTab === 'completed' && (
          <div>
            <h2 className="text-xl font-bold text-gray-900 mb-4">Completed Challenges</h2>
            
            {completedChallenges.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">✅</div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">No Completed Challenges</h3>
                <p className="text-gray-600 mb-6">Complete some challenges to see your history here!</p>
                <button
                  onClick={() => setActiveTab('active')}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
                >
                  View Active Challenges
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {completedChallenges.map((challenge) => (
                  <div key={challenge.id} className="bg-gray-50 rounded-lg shadow-md p-6 border-l-4 border-green-500">
                    <div className="flex justify-between items-start mb-4">
                      <h3 className="text-lg font-semibold text-gray-900">{challenge.name}</h3>
                      <span className="bg-green-100 text-green-800 text-xs font-medium px-2.5 py-0.5 rounded">
                        Completed
                      </span>
                    </div>
                    
                    <div className="space-y-2 mb-4">
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Score:</span>
                        <span className="text-sm font-bold text-green-600">{challenge.result.score} pts</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Accuracy:</span>
                        <span className="text-sm font-medium">
                          {Math.round((challenge.result.correct_answers / challenge.result.total_questions) * 100)}%
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Completed:</span>
                        <span className="text-sm text-gray-500">
                          {new Date(challenge.result.submitted_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                    
                    <div className="bg-white p-3 rounded border">
                      <div className="grid grid-cols-3 gap-2 text-center text-sm">
                        <div>
                          <div className="text-green-600 font-semibold">{challenge.result.correct_answers}</div>
                          <div className="text-gray-500">Correct</div>
                        </div>
                        <div>
                          <div className="text-red-600 font-semibold">{challenge.result.wrong_answers}</div>
                          <div className="text-gray-500">Wrong</div>
                        </div>
                        <div>
                          <div className="text-gray-600 font-semibold">
                            {challenge.result.total_questions - challenge.result.correct_answers - challenge.result.wrong_answers}
                          </div>
                          <div className="text-gray-500">Skipped</div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
        </div>
      </div>
    </div>
  );
};

export default Challenges;
