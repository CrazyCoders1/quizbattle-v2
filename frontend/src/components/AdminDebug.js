import React, { useState } from 'react';
import { apiService } from '../services/apiService';
import toast from 'react-hot-toast';

const AdminDebug = () => {
  const [debugInfo, setDebugInfo] = useState(null);
  const [loading, setLoading] = useState(false);

  const runDiagnostics = async () => {
    setLoading(true);
    const results = {};

    try {
      // Check token
      const token = localStorage.getItem('token');
      results.hasToken = !!token;
      results.tokenPrefix = token ? token.substring(0, 20) + '...' : 'No token';

      // Test profile endpoint
      try {
        const profileRes = await apiService.getProfile();
        results.profile = {
          success: true,
          data: profileRes.data
        };
      } catch (error) {
        results.profile = {
          success: false,
          error: error.response?.data || error.message
        };
      }

      // Test dashboard endpoint
      try {
        const dashboardRes = await apiService.getAdminDashboard();
        results.dashboard = {
          success: true,
          data: dashboardRes.data
        };
      } catch (error) {
        results.dashboard = {
          success: false,
          error: error.response?.data || error.message
        };
      }

      // Test users endpoint
      try {
        const usersRes = await apiService.getAdminUsers();
        results.users = {
          success: true,
          count: usersRes.data.users?.length || 0,
          data: usersRes.data
        };
      } catch (error) {
        results.users = {
          success: false,
          error: error.response?.data || error.message
        };
      }

      // Test questions endpoint
      try {
        const questionsRes = await apiService.getAdminQuestions();
        results.questions = {
          success: true,
          count: questionsRes.data.questions?.length || 0,
          data: questionsRes.data
        };
      } catch (error) {
        results.questions = {
          success: false,
          error: error.response?.data || error.message
        };
      }

      setDebugInfo(results);
      toast.success('Diagnostics completed');
    } catch (error) {
      toast.error('Diagnostics failed');
      console.error('Debug error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-gray-100 border border-gray-300 rounded-lg p-4 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">🔧 Admin Debug Panel</h3>
        <button
          onClick={runDiagnostics}
          disabled={loading}
          className="bg-yellow-500 hover:bg-yellow-600 text-white px-4 py-2 rounded font-medium disabled:opacity-50"
        >
          {loading ? '🔄 Running...' : '🔍 Run Diagnostics'}
        </button>
      </div>

      {debugInfo && (
        <div className="space-y-3 text-sm">
          <div className={`p-2 rounded ${debugInfo.hasToken ? 'bg-green-100' : 'bg-red-100'}`}>
            <strong>Token:</strong> {debugInfo.hasToken ? '✅ Present' : '❌ Missing'} ({debugInfo.tokenPrefix})
          </div>

          <div className={`p-2 rounded ${debugInfo.profile.success ? 'bg-green-100' : 'bg-red-100'}`}>
            <strong>Profile API:</strong> {debugInfo.profile.success ? '✅ Success' : '❌ Failed'}
            <pre className="mt-1 text-xs overflow-x-auto">
              {JSON.stringify(debugInfo.profile, null, 2)}
            </pre>
          </div>

          <div className={`p-2 rounded ${debugInfo.dashboard.success ? 'bg-green-100' : 'bg-red-100'}`}>
            <strong>Dashboard API:</strong> {debugInfo.dashboard.success ? '✅ Success' : '❌ Failed'}
            <pre className="mt-1 text-xs overflow-x-auto">
              {JSON.stringify(debugInfo.dashboard, null, 2)}
            </pre>
          </div>

          <div className={`p-2 rounded ${debugInfo.users.success ? 'bg-green-100' : 'bg-red-100'}`}>
            <strong>Users API:</strong> {debugInfo.users.success ? `✅ Success (${debugInfo.users.count} users)` : '❌ Failed'}
            <pre className="mt-1 text-xs overflow-x-auto">
              {JSON.stringify(debugInfo.users, null, 2)}
            </pre>
          </div>

          <div className={`p-2 rounded ${debugInfo.questions.success ? 'bg-green-100' : 'bg-red-100'}`}>
            <strong>Questions API:</strong> {debugInfo.questions.success ? `✅ Success (${debugInfo.questions.count} questions)` : '❌ Failed'}
            <pre className="mt-1 text-xs overflow-x-auto">
              {JSON.stringify(debugInfo.questions, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminDebug;