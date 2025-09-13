import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { apiService } from '../services/apiService';
import AdminDebug from '../components/AdminDebug';
import toast from 'react-hot-toast';

const Admin = () => {
  const { admin, isAdmin, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('dashboard');
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showCreateQuestion, setShowCreateQuestion] = useState(false);
  const [selectedQuestions, setSelectedQuestions] = useState([]);
  const [bulkDeleteLoading, setBulkDeleteLoading] = useState(false);
  const [questionFilters, setQuestionFilters] = useState({
    difficulty: 'all',
    exam_type: 'all',
    search: ''
  });
  const [newQuestion, setNewQuestion] = useState({
    text: '',
    options: ['', '', '', ''],
    answer: 0,
    difficulty: 'easy',
    exam_type: 'CBSE 11'
  });
  const [pdfUploadSettings, setPdfUploadSettings] = useState({
    exam_type: 'CBSE 11',
    difficulty: 'mixed' // Easy, Tough, or Mixed by default
  });

  useEffect(() => {
    if (isAdmin) {
      fetchDashboardData();
    }
  }, [isAdmin]);

  const fetchUsers = async () => {
    try {
      console.log('👥 Fetching users data...');
      const response = await apiService.getAdminUsers();
      console.log('👥 Users response:', response.data);
      setUsers(response.data.users || []);
      return response.data.users || [];
    } catch (error) {
      console.error('❌ Failed to fetch users:', error);
      toast.error('Failed to fetch users data');
      return [];
    }
  };

  const fetchQuestions = async () => {
    try {
      console.log('❓ Fetching questions data...');
      const response = await apiService.getAdminQuestions();
      console.log('❓ Questions response:', response.data);
      setQuestions(response.data.questions || []);
      return response.data.questions || [];
    } catch (error) {
      console.error('❌ Failed to fetch questions:', error);
      toast.error('Failed to fetch questions data');
      return [];
    }
  };

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      console.log('🔍 Admin: Fetching dashboard data...');
      console.log('🔑 Admin token:', localStorage.getItem('token'));
      
      const [dashboardRes, usersRes, questionsRes] = await Promise.all([
        apiService.getAdminDashboard(),
        apiService.getAdminUsers(),
        apiService.getAdminQuestions()
      ]);
      
      console.log('📊 Dashboard response:', dashboardRes.data);
      console.log('👥 Users response:', usersRes.data);
      console.log('❓ Questions response:', questionsRes.data);
      
      setStats(dashboardRes.data.stats || {});
      setUsers(usersRes.data.users || []);
      setQuestions(questionsRes.data.questions || []);
      
      console.log('✅ Admin data fetched successfully');
    } catch (error) {
      console.error('❌ Admin data fetch error:', error);
      console.error('Error response:', error.response?.data);
      console.error('Error status:', error.response?.status);
      
      // More specific error handling
      if (error.response?.status === 403) {
        toast.error('Access denied - Admin privileges required');
      } else if (error.response?.status === 401) {
        toast.error('Authentication failed - Please login again');
        logout();
      } else {
        toast.error(`Failed to fetch admin data: ${error.response?.data?.error || error.message}`);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCreateQuestion = async (e) => {
    e.preventDefault();
    
    if (newQuestion.options.some(opt => !opt.trim())) {
      toast.error('All options must be filled');
      return;
    }

    try {
      await apiService.createQuestion(newQuestion);
      toast.success('Question created successfully!');
      setShowCreateQuestion(false);
      setNewQuestion({
        text: '',
        options: ['', '', '', ''],
        answer: 0,
        difficulty: 'easy',
        exam_type: 'CBSE 11'
      });
      await fetchQuestions(); // Just refresh questions, not all data
      fetchDashboardData(); // Also refresh dashboard stats
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to create question');
    }
  };

  const handleDeleteQuestion = async (questionId) => {
    if (window.confirm('Are you sure you want to delete this question?')) {
      try {
        await apiService.deleteQuestion(questionId);
        toast.success('Question deleted successfully!');
        await fetchQuestions(); // Just refresh questions
        fetchDashboardData(); // Also refresh dashboard stats
      } catch (error) {
        toast.error('Failed to delete question');
      }
    }
  };

  const handleSelectQuestion = (questionId) => {
    setSelectedQuestions(prev => 
      prev.includes(questionId) 
        ? prev.filter(id => id !== questionId)
        : [...prev, questionId]
    );
  };

  const handleSelectAllQuestions = () => {
    const visibleQuestionIds = filteredQuestions.map(q => q.id);
    if (selectedQuestions.length === visibleQuestionIds.length && visibleQuestionIds.every(id => selectedQuestions.includes(id))) {
      setSelectedQuestions([]);
    } else {
      setSelectedQuestions(visibleQuestionIds);
    }
  };

  // Filter questions based on current filters
  const filteredQuestions = questions.filter(question => {
    const matchesDifficulty = questionFilters.difficulty === 'all' || question.difficulty === questionFilters.difficulty;
    const matchesExamType = questionFilters.exam_type === 'all' || question.exam_type === questionFilters.exam_type;
    const matchesSearch = questionFilters.search === '' || 
      question.text.toLowerCase().includes(questionFilters.search.toLowerCase()) ||
      question.options.some(option => option.toLowerCase().includes(questionFilters.search.toLowerCase()));
    
    return matchesDifficulty && matchesExamType && matchesSearch;
  });

  const handleBulkDelete = async () => {
    if (selectedQuestions.length === 0) {
      toast.error('Please select questions to delete');
      return;
    }

    const confirmMessage = `Are you sure you want to delete ${selectedQuestions.length} selected questions? This action cannot be undone.`;
    if (!window.confirm(confirmMessage)) {
      return;
    }

    try {
      setBulkDeleteLoading(true);
      const response = await apiService.post('/admin/questions/delete-bulk', {
        question_ids: selectedQuestions
      });
      
      const { success_count, failed_count } = response.data;
      
      if (success_count > 0) {
        toast.success(`Successfully deleted ${success_count} questions`);
      }
      if (failed_count > 0) {
        toast.error(`Failed to delete ${failed_count} questions`);
      }
      
      setSelectedQuestions([]);
      await fetchQuestions();
      fetchDashboardData();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to delete questions');
    } finally {
      setBulkDeleteLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (file.type !== 'application/pdf') {
      toast.error('Please select a PDF file');
      return;
    }

    try {
      setLoading(true);
      const formData = new FormData();
      formData.append('pdf', file);
      formData.append('exam_type', pdfUploadSettings.exam_type);
      formData.append('difficulty', pdfUploadSettings.difficulty);
      
      const response = await apiService.post('/admin/upload-pdf', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      const { questions_added, breakdown } = response.data;
      toast.success(`✅ PDF processed! ${questions_added} questions added: ${breakdown.easy} Easy, ${breakdown.tough} Tough`);
      await fetchQuestions(); // Refresh questions to show newly uploaded ones
      fetchDashboardData(); // Also refresh dashboard stats
      
      // Reset file input
      e.target.value = '';
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to upload PDF');
    } finally {
      setLoading(false);
    }
  };

  if (!isAdmin) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Access Denied</h2>
        <p className="text-gray-600 mb-6">You need admin privileges to access this page.</p>
        <button
          onClick={logout}
          className="bg-primary-500 hover:bg-primary-600 text-white px-6 py-3 rounded-lg font-medium transition-colors"
        >
          Login as Admin
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Admin Panel</h1>
          <p className="text-gray-600">Welcome back, {admin?.username}</p>
        </div>
        <button
          onClick={logout}
          className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg font-medium transition-colors"
        >
          Logout
        </button>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white rounded-lg shadow-md">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {[
              { id: 'dashboard', label: 'Dashboard', icon: '📊' },
              { id: 'users', label: 'Users', icon: '👥' },
              { id: 'questions', label: 'Questions', icon: '❓' },
              { id: 'upload', label: 'Upload PDF', icon: '📄' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => {
                  setActiveTab(tab.id);
                  // Fetch data when switching to specific tabs
                  if (tab.id === 'users' && users.length === 0) {
                    fetchUsers();
                  } else if (tab.id === 'questions' && questions.length === 0) {
                    fetchQuestions();
                  }
                }}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {/* Dashboard Tab */}
          {activeTab === 'dashboard' && (
            <div>
              {loading ? (
                <div className="flex justify-center items-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
                </div>
              ) : (
                <div className="space-y-6">
                  <h2 className="text-2xl font-bold text-gray-900">System Overview</h2>
                  
                  {/* Debug Panel */}
                  <AdminDebug />
                  
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <div className="bg-blue-50 p-6 rounded-lg">
                      <div className="flex items-center">
                        <div className="text-3xl mr-4">👥</div>
                        <div>
                          <div className="text-2xl font-bold text-blue-600">{stats?.total_users || 0}</div>
                          <div className="text-blue-800">Total Users</div>
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-green-50 p-6 rounded-lg">
                      <div className="flex items-center">
                        <div className="text-3xl mr-4">❓</div>
                        <div>
                          <div className="text-2xl font-bold text-green-600">{stats?.total_questions || 0}</div>
                          <div className="text-green-800">Total Questions</div>
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-purple-50 p-6 rounded-lg">
                      <div className="flex items-center">
                        <div className="text-3xl mr-4">🏆</div>
                        <div>
                          <div className="text-2xl font-bold text-purple-600">{stats?.total_challenges || 0}</div>
                          <div className="text-purple-800">Total Challenges</div>
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-orange-50 p-6 rounded-lg">
                      <div className="flex items-center">
                        <div className="text-3xl mr-4">📊</div>
                        <div>
                          <div className="text-2xl font-bold text-orange-600">{stats?.total_results || 0}</div>
                          <div className="text-orange-800">Quiz Results</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Users Tab */}
          {activeTab === 'users' && (
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">User Management</h2>
              
              {loading ? (
                <div className="flex justify-center items-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
                  <span className="ml-3 text-gray-600">Loading users...</span>
                </div>
              ) : users.length === 0 ? (
                <div className="text-center py-12">
                  <div className="text-6xl mb-4">👥</div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">No Users Found</h3>
                  <p className="text-gray-600 mb-4">No users have registered yet, or there was an error loading users.</p>
                  <button
                    onClick={fetchUsers}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
                  >
                    🔄 Retry Loading Users
                  </button>
                </div>
              ) : (
                <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          User
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Email
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Joined
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {users.map((user) => (
                        <tr key={user.id}>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm font-medium text-gray-900">{user.username}</div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm text-gray-900">{user.email}</div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm text-gray-900">
                              {new Date(user.created_at).toLocaleDateString()}
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {/* Questions Tab */}
          {activeTab === 'questions' && (
            <div>
              <div className="space-y-6">
                <div className="flex justify-between items-center">
                  <h2 className="text-2xl font-bold text-gray-900">Question Management</h2>
                  <div className="flex gap-3">
                    {selectedQuestions.length > 0 && (
                      <button
                        onClick={handleBulkDelete}
                        disabled={bulkDeleteLoading}
                        className="bg-red-500 hover:bg-red-600 disabled:opacity-50 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2"
                      >
                        {bulkDeleteLoading ? (
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        ) : (
                          '🗑️'
                        )}
                        Delete Selected ({selectedQuestions.length})
                      </button>
                    )}
                    <button
                      onClick={() => setShowCreateQuestion(true)}
                      className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg font-medium transition-colors"
                    >
                      Add Question
                    </button>
                  </div>
                </div>

                {/* Filters */}
                <div className="bg-white border border-gray-200 rounded-lg p-4">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Filter Questions</h3>
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Search</label>
                      <input
                        type="text"
                        placeholder="Search in questions or options..."
                        value={questionFilters.search}
                        onChange={(e) => setQuestionFilters({...questionFilters, search: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Difficulty</label>
                      <select
                        value={questionFilters.difficulty}
                        onChange={(e) => setQuestionFilters({...questionFilters, difficulty: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      >
                        <option value="all">All Difficulties</option>
                        <option value="easy">Easy</option>
                        <option value="medium">Medium</option>
                        <option value="tough">Tough</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Exam Type</label>
                      <select
                        value={questionFilters.exam_type}
                        onChange={(e) => setQuestionFilters({...questionFilters, exam_type: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      >
                        <option value="all">All Exam Types</option>
                        <option value="CBSE 11">CBSE 11</option>
                        <option value="CBSE 12">CBSE 12</option>
                        <option value="JEE Main">JEE Main</option>
                        <option value="JEE Advanced">JEE Advanced</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Results</label>
                      <div className="text-sm text-gray-600 pt-2">
                        <p>Showing: <span className="font-semibold text-blue-600">{filteredQuestions.length}</span></p>
                        <p>Total: <span className="font-semibold">{questions.length}</span></p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {loading ? (
                <div className="flex justify-center items-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500"></div>
                  <span className="ml-3 text-gray-600">Loading questions...</span>
                </div>
              ) : filteredQuestions.length === 0 && questions.length === 0 ? (
                <div className="text-center py-12">
                  <div className="text-6xl mb-4">❓</div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">No Questions Found</h3>
                  <p className="text-gray-600 mb-6">Create your first question or try reloading.</p>
                  <div className="space-x-4">
                    <button
                      onClick={fetchQuestions}
                      className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
                    >
                      🔄 Retry Loading Questions
                    </button>
                    <button
                      onClick={() => setShowCreateQuestion(true)}
                      className="bg-green-500 hover:bg-green-600 text-white px-6 py-3 rounded-lg font-medium transition-colors"
                    >
                      Add First Question
                    </button>
                  </div>
                </div>
              ) : filteredQuestions.length === 0 ? (
                <div className="text-center py-12">
                  <div className="text-6xl mb-4">🔍</div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">No Questions Match Your Filters</h3>
                  <p className="text-gray-600 mb-6">Try adjusting your search criteria or clear filters to see all questions.</p>
                  <button
                    onClick={() => setQuestionFilters({ difficulty: 'all', exam_type: 'all', search: '' })}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
                  >
                    Clear All Filters
                  </button>
                </div>
              ) : (
                <div className="space-y-4">
                  {/* Select All Header */}
                  <div className="bg-white border border-gray-200 p-4 rounded-lg">
                    <div className="flex items-center gap-3">
                      <input
                        type="checkbox"
                        checked={filteredQuestions.length > 0 && filteredQuestions.every(q => selectedQuestions.includes(q.id))}
                        onChange={handleSelectAllQuestions}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      <label className="text-sm font-medium text-gray-700">
                        Select All Visible ({filteredQuestions.length} shown)
                      </label>
                      {selectedQuestions.length > 0 && (
                        <span className="text-sm text-blue-600 font-medium">
                          {selectedQuestions.length} selected
                        </span>
                      )}
                    </div>
                  </div>
                  
                  {filteredQuestions.map((question) => (
                    <div key={question.id} className="bg-gray-50 p-4 rounded-lg">
                      <div className="flex items-start gap-3">
                        <input
                          type="checkbox"
                          checked={selectedQuestions.includes(question.id)}
                          onChange={() => handleSelectQuestion(question.id)}
                          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded mt-1 flex-shrink-0"
                        />
                        <div className="flex-1">
                          <div className="flex justify-between items-start mb-2">
                            <h3 className="text-lg font-semibold text-gray-900">{question.text}</h3>
                            <div className="flex space-x-2">
                              <span className={`px-2 py-1 text-xs rounded ${
                                question.difficulty === 'easy' ? 'bg-green-100 text-green-800' :
                                question.difficulty === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                                'bg-red-100 text-red-800'
                              }`}>
                                {question.difficulty}
                              </span>
                              <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">
                                {question.exam_type}
                              </span>
                            </div>
                          </div>
                          
                          <div className="grid grid-cols-2 gap-2 mb-3">
                            {question.options.map((option, index) => (
                              <div
                                key={index}
                                className={`p-2 rounded text-sm ${
                                  index === question.answer
                                    ? 'bg-green-100 text-green-800 font-semibold'
                                    : 'bg-white text-gray-700'
                                }`}
                              >
                                {String.fromCharCode(65 + index)}. {option}
                              </div>
                            ))}
                          </div>
                          
                          <div className="flex justify-end">
                            <button
                              onClick={() => handleDeleteQuestion(question.id)}
                              className="bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded text-sm transition-colors"
                            >
                              Delete
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Upload PDF Tab */}
          {activeTab === 'upload' && (
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Upload PDF Questions</h2>
              
              {/* PDF Settings */}
              <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">PDF Processing Settings</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Exam Type
                    </label>
                    <select
                      value={pdfUploadSettings.exam_type}
                      onChange={(e) => setPdfUploadSettings({...pdfUploadSettings, exam_type: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="CBSE 11">CBSE 11</option>
                      <option value="CBSE 12">CBSE 12</option>
                      <option value="JEE Main">JEE Main</option>
                      <option value="JEE Advanced">JEE Advanced</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Difficulty Mode
                    </label>
                    <select
                      value={pdfUploadSettings.difficulty}
                      onChange={(e) => setPdfUploadSettings({...pdfUploadSettings, difficulty: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="easy">Easy Only</option>
                      <option value="tough">Tough Only</option>
                      <option value="mixed">Mixed (60% Easy, 40% Tough)</option>
                    </select>
                  </div>
                </div>
              </div>
              
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                <div className="text-center">
                  <div className="text-4xl mb-4">📄</div>
                  <h3 className="text-lg font-semibold text-blue-900 mb-2">Upload PDF File</h3>
                  <p className="text-blue-800 mb-4">
                    Upload a PDF file containing quiz questions. The system will automatically extract and categorize them.
                  </p>
                  
                  <div className="mt-6">
                    <input
                      type="file"
                      accept=".pdf"
                      onChange={handleFileUpload}
                      disabled={loading}
                      className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 disabled:opacity-50"
                    />
                  </div>
                  
                  <div className="mt-4 text-sm text-blue-700 space-y-1">
                    <p><strong>Processing Rules:</strong></p>
                    <p>✅ <strong>Easy Mode:</strong> Text-only questions, no complex images</p>
                    <p>✅ <strong>Tough Mode:</strong> All questions + explainable images + AI hints</p>
                    <p>✅ <strong>Mixed Mode:</strong> 60% Easy + 40% Tough questions</p>
                    <p>❌ Complex/unexplainable images always skipped</p>
                    <p className="mt-2 font-semibold">AI Services: DeepSeek → Gemini → Regex Fallback</p>
                    <p className="font-semibold">Supported: PDF only, Max: 10MB</p>
                  </div>
                  
                  {loading && (
                    <div className="mt-4">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                      <p className="text-sm text-blue-700 mt-2">Processing PDF...</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Create Question Modal */}
      {showCreateQuestion && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <h3 className="text-lg font-semibold mb-4">Create New Question</h3>
            <form onSubmit={handleCreateQuestion}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Question Text
                  </label>
                  <textarea
                    required
                    value={newQuestion.text}
                    onChange={(e) => setNewQuestion({...newQuestion, text: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                    rows="3"
                    placeholder="Enter the question text"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Options
                  </label>
                  {newQuestion.options.map((option, index) => (
                    <div key={index} className="flex items-center mb-2">
                      <input
                        type="radio"
                        name="correctAnswer"
                        checked={newQuestion.answer === index}
                        onChange={() => setNewQuestion({...newQuestion, answer: index})}
                        className="mr-2"
                      />
                      <input
                        type="text"
                        value={option}
                        onChange={(e) => {
                          const newOptions = [...newQuestion.options];
                          newOptions[index] = e.target.value;
                          setNewQuestion({...newQuestion, options: newOptions});
                        }}
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                        placeholder={`Option ${String.fromCharCode(65 + index)}`}
                      />
                    </div>
                  ))}
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Difficulty
                    </label>
                    <select
                      value={newQuestion.difficulty}
                      onChange={(e) => setNewQuestion({...newQuestion, difficulty: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                    >
                      <option value="easy">Easy</option>
                      <option value="medium">Medium</option>
                      <option value="tough">Tough</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Exam Type
                    </label>
                    <select
                      value={newQuestion.exam_type}
                      onChange={(e) => setNewQuestion({...newQuestion, exam_type: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                    >
                      <option value="CBSE 11">CBSE 11</option>
                      <option value="CBSE 12">CBSE 12</option>
                      <option value="JEE Main">JEE Main</option>
                      <option value="JEE Advanced">JEE Advanced</option>
                    </select>
                  </div>
                </div>
              </div>
              
              <div className="flex justify-end space-x-3 mt-6">
                <button
                  type="button"
                  onClick={() => setShowCreateQuestion(false)}
                  className="px-4 py-2 text-gray-700 bg-gray-200 hover:bg-gray-300 rounded-md transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-md transition-colors"
                >
                  Create Question
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Admin;
