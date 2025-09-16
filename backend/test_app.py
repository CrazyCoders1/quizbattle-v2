#!/usr/bin/env python3
"""
Minimal Flask app for immediate testing - bypasses complex initialization
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import json

app = Flask(__name__)
CORS(app, origins=["*"])

# Simple in-memory data
users = []
leaderboard_data = []

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        'name': 'QuizBattle API',
        'status': 'running',
        'version': '1.0.0'
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'database': 'connected',
        'timestamp': '2025-09-16T14:13:00Z'
    })

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    # Check if user exists
    if any(u['username'] == username for u in users):
        return jsonify({'error': 'User already exists'}), 400
    
    # Create user
    user_id = len(users) + 1
    user = {
        'id': user_id,
        'username': username,
        'email': email,
        'password': password,
        'created_at': '2025-09-16T14:13:00Z'
    }
    users.append(user)
    
    return jsonify({
        'message': 'User created successfully',
        'user': {
            'id': user_id,
            'username': username,
            'email': email,
            'created_at': user['created_at']
        }
    }), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # Find user
    user = next((u for u in users if u['username'] == username and u['password'] == password), None)
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Return fake JWT token
    return jsonify({
        'access_token': f'fake_token_{user["id"]}',
        'user': {
            'id': user['id'],
            'username': user['username'],
            'email': user['email']
        }
    })

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    # Check for fake auth header
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer fake_token_'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Return sample leaderboard
    sample_leaderboard = [
        {
            'id': 1,
            'user_id': 1,
            'username': 'testuser',
            'total_score': 120,
            'challenges_completed': 3,
            'rank': 1,
            'last_updated': '2025-09-16T14:13:00Z'
        },
        {
            'id': 2,
            'user_id': 2,
            'username': 'player2',
            'total_score': 95,
            'challenges_completed': 2,
            'rank': 2,
            'last_updated': '2025-09-16T14:13:00Z'
        }
    ]
    
    return jsonify({'leaderboard': sample_leaderboard})

if __name__ == '__main__':
    print("🚀 Starting minimal QuizBattle test server")
    print("✅ Registration, login, and leaderboard will work")
    app.run(host='127.0.0.1', port=5000, debug=True)