import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || (window.location.hostname === 'localhost' ? 'http://localhost:5000/api' : '/api');

class ApiService {
  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('token') || sessionStorage.getItem('token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
          console.log('🔑 JWT token attached to request:', config.url);
        } else {
          console.warn('⚠️ No JWT token found for request:', config.url);
        }
        return config;
      },
      (error) => {
        console.error('❌ Request interceptor error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor to handle errors
    this.api.interceptors.response.use(
      (response) => {
        console.log('✅ API Response:', response.config.url, response.status);
        return response;
      },
      (error) => {
        console.error('❌ API Error:', error.config?.url, error.response?.status);
        
        if (error.response?.status === 401) {
          console.warn('🚺 Unauthorized - clearing tokens and redirecting');
          localStorage.removeItem('token');
          sessionStorage.removeItem('token');
          window.location.href = '/login';
        } else if (error.response?.status === 403) {
          console.warn('🚫 Forbidden - insufficient permissions');
        }
        
        return Promise.reject(error);
      }
    );
  }

  setToken(token) {
    if (token) {
      this.api.defaults.headers.Authorization = `Bearer ${token}`;
    } else {
      delete this.api.defaults.headers.Authorization;
    }
  }

  // Generic HTTP methods
  async get(url, config = {}) {
    return this.api.get(url, config);
  }

  async post(url, data = {}, config = {}) {
    return this.api.post(url, data, config);
  }

  async put(url, data = {}, config = {}) {
    return this.api.put(url, data, config);
  }

  async delete(url, config = {}) {
    return this.api.delete(url, config);
  }

  // Auth endpoints
  async login(username, password) {
    return this.post('/auth/login', { username, password });
  }

  async adminLogin(username, password) {
    return this.post('/auth/admin/login', { username, password });
  }

  async register(username, email, password) {
    return this.post('/auth/register', { username, email, password });
  }

  async getProfile() {
    return this.get('/auth/profile');
  }

  // Challenge endpoints
  async getChallenges() {
    return this.get('/challenges/active');
  }

  async createChallenge(data) {
    return this.post('/challenges/create', data);
  }

  async joinChallenge(code) {
    return this.post(`/challenges/join/${code}`);
  }

  async getChallengeQuestions(challengeId) {
    return this.get(`/challenges/${challengeId}/play`);
  }

  async submitChallenge(challengeId, submissionData) {
    // submissionData should contain { answers, time_taken }
    return this.post(`/challenges/${challengeId}/submit`, submissionData);
  }

  async getChallengeResults(challengeId) {
    return this.get(`/challenges/${challengeId}/results`);
  }

  async getCompletedChallenges() {
    return this.get('/challenges/completed');
  }

  // Quiz endpoints
  async getQuestions(examType = null, difficulty = null) {
    const params = {};
    if (examType) params.exam_type = examType;
    if (difficulty) params.difficulty = difficulty;
    return this.get('/quizzes/questions', { params });
  }

  // Admin endpoints
  async getAdminDashboard() {
    return this.get('/admin/dashboard');
  }

  async getAdminUsers() {
    return this.get('/admin/users');
  }

  async getAdminQuestions() {
    return this.get('/admin/questions');
  }

  async createQuestion(data) {
    return this.post('/admin/questions', data);
  }

  async updateQuestion(id, data) {
    return this.put(`/admin/questions/${id}`, data);
  }

  async deleteQuestion(id) {
    return this.delete(`/admin/questions/${id}`);
  }

  async uploadPDF(file, examType = 'CBSE 11', difficulty = 'mixed') {
    console.log('📄 Uploading PDF:', file.name, 'Exam Type:', examType, 'Difficulty:', difficulty);
    const formData = new FormData();
    formData.append('pdf', file);
    formData.append('exam_type', examType);
    formData.append('difficulty', difficulty);
    
    return this.post('/admin/upload-pdf', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 120000, // 2 minute timeout for PDF processing
    });
  }

  // Leaderboard endpoints
  async getLeaderboard(type = 'global', challengeId = null) {
    console.log('🏆 Fetching leaderboard:', type, challengeId);
    
    if (type === 'challenge' && challengeId) {
      // Use specific challenge leaderboard endpoint
      return this.get(`/leaderboard/${challengeId}`);
    }
    
    // Global leaderboard - use query parameters
    const params = { type };
    if (challengeId) {
      params.challenge_id = challengeId;
    }
    
    return this.get('/leaderboard', { params });
  }
}

export const apiService = new ApiService();
