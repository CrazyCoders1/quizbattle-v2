import React, { useState } from 'react';
import { apiService } from '../services/apiService';

const Debug = () => {
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);

  const testAPI = async () => {
    setLoading(true);
    try {
      const response = await apiService.post('/auth/register', {
        username: 'debuguser',
        email: 'debug@example.com',
        password: 'debugpass123'
      });
      setResult(JSON.stringify(response.data, null, 2));
    } catch (error) {
      setResult(`Error: ${error.message}\n${JSON.stringify(error.response?.data, null, 2)}`);
    } finally {
      setLoading(false);
    }
  };

  const testLogin = async () => {
    setLoading(true);
    try {
      const response = await apiService.post('/auth/login', {
        username: 'debuguser',
        password: 'debugpass123'
      });
      setResult(JSON.stringify(response.data, null, 2));
    } catch (error) {
      setResult(`Error: ${error.message}\n${JSON.stringify(error.response?.data, null, 2)}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4">API Debug</h2>
      <div className="space-x-4 mb-4">
        <button
          onClick={testAPI}
          disabled={loading}
          className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50"
        >
          Test Register API
        </button>
        <button
          onClick={testLogin}
          disabled={loading}
          className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded disabled:opacity-50"
        >
          Test Login API
        </button>
      </div>
      {loading && <div>Loading...</div>}
      {result && (
        <pre className="bg-gray-100 p-4 rounded text-sm overflow-auto">
          {result}
        </pre>
      )}
    </div>
  );
};

export default Debug;
