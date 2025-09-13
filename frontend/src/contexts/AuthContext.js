import React, { createContext, useContext, useState, useEffect } from 'react';
import { apiService } from '../services/apiService';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [admin, setAdmin] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('token'));

  useEffect(() => {
    const savedToken = localStorage.getItem('token');
    if (savedToken && !token) {
      setToken(savedToken);
      apiService.setToken(savedToken);
      fetchProfile();
    } else if (token) {
      apiService.setToken(token);
      fetchProfile();
    } else {
      setLoading(false);
    }
  }, [token]);

  const fetchProfile = async () => {
    try {
      const response = await apiService.get('/auth/profile');
      if (response.data.admin) {
        setAdmin(response.data.admin);
        setUser(null);
      } else if (response.data.user) {
        setUser(response.data.user);
        setAdmin(null);
      }
    } catch (error) {
      console.error('Failed to fetch profile:', error);
      // Only logout if it's an authentication error, not a network error
      if (error.response?.status === 401) {
        logout();
      }
    } finally {
      setLoading(false);
    }
  };

  const login = async (username, password) => {
    try {
      const response = await apiService.post('/auth/login', { username, password });
      const { access_token, user: userData } = response.data;
      
      localStorage.setItem('token', access_token);
      setToken(access_token);
      apiService.setToken(access_token);
      setUser(userData);
      setAdmin(null);
      
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Login failed' 
      };
    }
  };

  const adminLogin = async (username, password) => {
    try {
      const response = await apiService.post('/auth/admin/login', { username, password });
      const { access_token, admin: adminData } = response.data;
      
      localStorage.setItem('token', access_token);
      setToken(access_token);
      apiService.setToken(access_token);
      setAdmin(adminData);
      setUser(null);
      
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Admin login failed' 
      };
    }
  };

  const register = async (username, email, password) => {
    try {
      const response = await apiService.post('/auth/register', { username, email, password });
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Registration failed' 
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    setAdmin(null);
    apiService.setToken(null);
  };

  const value = {
    user,
    admin,
    token,
    loading,
    login,
    adminLogin,
    register,
    logout,
    isAuthenticated: !!(user || admin),
    isAdmin: !!admin,
    isUser: !!user
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
