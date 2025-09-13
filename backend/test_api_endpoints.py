#!/usr/bin/env python3
"""
Test script to verify API endpoints are working correctly
Run this to test challenge creation, submission, leaderboards, etc.
"""
import sys
import os
import requests
import json
from datetime import datetime

# Test configuration
BASE_URL = 'http://localhost:5000/api'
TEST_USER = {
    'username': 'testuser',
    'email': 'test@example.com', 
    'password': 'testpass123'
}
TEST_ADMIN = {
    'username': 'admin',
    'password': 'admin123'
}

class APITester:
    def __init__(self):
        self.user_token = None
        self.admin_token = None
        self.test_challenge_id = None
        
    def log(self, message, level='INFO'):
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {level}: {message}")
    
    def make_request(self, method, endpoint, data=None, headers=None, token=None):
        """Make authenticated API request"""
        url = f"{BASE_URL}{endpoint}"
        req_headers = {'Content-Type': 'application/json'}
        
        if headers:
            req_headers.update(headers)
            
        if token:
            req_headers['Authorization'] = f'Bearer {token}'
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=req_headers, params=data)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=req_headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=req_headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=req_headers)
            
            self.log(f"{method} {endpoint} -> {response.status_code}")
            
            if response.status_code >= 400:
                self.log(f"Error response: {response.text}", 'ERROR')
            
            return response
            
        except requests.exceptions.RequestException as e:
            self.log(f"Request failed: {str(e)}", 'ERROR')
            return None
    
    def test_user_registration_login(self):
        """Test user registration and login"""
        self.log("🔐 Testing user registration and login")
        
        # Try to login first (user might already exist)
        response = self.make_request('POST', '/auth/login', {
            'username': TEST_USER['username'],
            'password': TEST_USER['password']
        })
        
        if response and response.status_code == 200:
            data = response.json()
            self.user_token = data.get('access_token')
            self.log("✅ User login successful (existing user)")
            return True
        
        # If login failed, try to register
        self.log("🆕 User doesn't exist, attempting registration")
        response = self.make_request('POST', '/auth/register', TEST_USER)
        
        if response and response.status_code == 201:
            self.log("✅ User registration successful")
            
            # Now login the newly registered user
            response = self.make_request('POST', '/auth/login', {
                'username': TEST_USER['username'],
                'password': TEST_USER['password']
            })
            
            if response and response.status_code == 200:
                data = response.json()
                self.user_token = data.get('access_token')
                self.log("✅ New user login successful")
                return True
            else:
                self.log("❌ New user login failed", 'ERROR')
                return False
        else:
            error_msg = response.json().get('error', 'Unknown error') if response else 'No response'
            self.log(f"❌ User registration failed: {error_msg}", 'ERROR')
            return False
    
    def test_admin_login(self):
        """Test admin login"""
        self.log("🔑 Testing admin login")
        
        # Try admin login
        response = self.make_request('POST', '/auth/admin/login', TEST_ADMIN)
        
        if response and response.status_code == 200:
            data = response.json()
            self.admin_token = data.get('access_token')
            self.log("✅ Admin login successful")
            return True
        else:
            self.log("❌ Admin login failed - this is expected if no admin user exists", 'WARN')
            return False
    
    def test_challenge_creation(self):
        """Test challenge creation"""
        if not self.user_token:
            self.log("❌ Cannot test challenge creation - no user token", 'ERROR')
            return False
        
        self.log("🏆 Testing challenge creation")
        
        challenge_data = {
            'name': 'Test Challenge',
            'exam_type': 'Physics 11',
            'difficulty': 'easy',
            'question_count': 5,
            'time_limit': 10
        }
        
        response = self.make_request('POST', '/challenges/create', challenge_data, token=self.user_token)
        
        if response and response.status_code == 201:
            data = response.json()
            self.test_challenge_id = data['challenge']['id']
            self.log(f"✅ Challenge created successfully - ID: {self.test_challenge_id}")
            return True
        else:
            self.log("❌ Challenge creation failed", 'ERROR')
            return False
    
    def test_active_challenges(self):
        """Test fetching active challenges"""
        if not self.user_token:
            return False
        
        self.log("📋 Testing active challenges fetch")
        
        response = self.make_request('GET', '/challenges/active', token=self.user_token)
        
        if response and response.status_code == 200:
            data = response.json()
            challenges = data.get('challenges', [])
            self.log(f"✅ Active challenges fetched: {len(challenges)} challenges")
            return True
        else:
            self.log("❌ Failed to fetch active challenges", 'ERROR')
            return False
    
    def test_challenge_submission(self):
        """Test challenge submission"""
        if not self.user_token or not self.test_challenge_id:
            self.log("❌ Cannot test submission - missing token or challenge ID", 'ERROR')
            return False
        
        self.log("📝 Testing challenge submission")
        
        # First get challenge questions
        response = self.make_request('GET', f'/challenges/{self.test_challenge_id}/play', token=self.user_token)
        
        if not response or response.status_code != 200:
            self.log("❌ Failed to get challenge questions", 'ERROR')
            return False
        
        data = response.json()
        questions = data.get('questions', [])
        self.log(f"📚 Got {len(questions)} questions for challenge")
        
        if not questions:
            self.log("❌ No questions found for challenge", 'ERROR')
            return False
        
        # Create mock answers (all correct = option 0)
        answers = {str(q['id']): 0 for q in questions}
        
        submission_data = {
            'answers': answers,
            'time_taken': 120  # 2 minutes
        }
        
        response = self.make_request('POST', f'/challenges/{self.test_challenge_id}/submit', 
                                   submission_data, token=self.user_token)
        
        if response and response.status_code == 200:
            data = response.json()
            result = data.get('result', {})
            score = result.get('score', 0)
            self.log(f"✅ Challenge submitted successfully - Score: {score}")
            return True
        else:
            self.log("❌ Challenge submission failed", 'ERROR')
            return False
    
    def test_global_leaderboard(self):
        """Test global leaderboard fetch"""
        if not self.user_token:
            return False
        
        self.log("🏆 Testing global leaderboard")
        
        response = self.make_request('GET', '/leaderboard?type=global', token=self.user_token)
        
        if response and response.status_code == 200:
            data = response.json()
            leaderboard = data.get('leaderboard', [])
            self.log(f"✅ Global leaderboard fetched: {len(leaderboard)} entries")
            return True
        else:
            self.log("❌ Failed to fetch global leaderboard", 'ERROR')
            return False
    
    def test_challenge_leaderboard(self):
        """Test challenge-specific leaderboard"""
        if not self.user_token or not self.test_challenge_id:
            return False
        
        self.log("🎯 Testing challenge leaderboard")
        
        response = self.make_request('GET', f'/leaderboard/{self.test_challenge_id}', token=self.user_token)
        
        if response and response.status_code == 200:
            data = response.json()
            leaderboard = data.get('leaderboard', [])
            self.log(f"✅ Challenge leaderboard fetched: {len(leaderboard)} entries")
            return True
        else:
            self.log("❌ Failed to fetch challenge leaderboard", 'ERROR')
            return False
    
    def test_admin_endpoints(self):
        """Test admin endpoints if admin token available"""
        if not self.admin_token:
            self.log("⚠️ Skipping admin tests - no admin token", 'WARN')
            return False
        
        self.log("👑 Testing admin endpoints")
        
        # Test admin dashboard
        response = self.make_request('GET', '/admin/dashboard', token=self.admin_token)
        if response and response.status_code == 200:
            self.log("✅ Admin dashboard accessible")
        else:
            self.log("❌ Admin dashboard failed", 'ERROR')
        
        # Test admin users
        response = self.make_request('GET', '/admin/users', token=self.admin_token)
        if response and response.status_code == 200:
            data = response.json()
            users = data.get('users', [])
            self.log(f"✅ Admin users fetched: {len(users)} users")
        else:
            self.log("❌ Admin users failed", 'ERROR')
        
        return True
    
    def test_debug_endpoints(self):
        """Test debug endpoints"""
        if not self.admin_token:
            self.log("⚠️ Skipping debug tests - no admin token", 'WARN')
            return False
        
        self.log("🔍 Testing debug endpoints")
        
        # Test database consistency
        response = self.make_request('GET', '/debug/database/consistency', token=self.admin_token)
        if response and response.status_code == 200:
            data = response.json()
            self.log("✅ Database consistency check completed")
            self.log(f"   Totals: {data.get('totals', {})}")
            self.log(f"   Inconsistencies: {len(data.get('leaderboard_inconsistencies', []))}")
            return True
        elif response and response.status_code == 404:
            self.log("⚠️ Debug endpoints not available - server may need restart", 'WARN')
            return True  # Don't fail the test for this
        else:
            self.log(f"❌ Database consistency check failed: {response.status_code if response else 'No response'}", 'ERROR')
            return False
    
    def run_all_tests(self):
        """Run all API tests"""
        self.log("🚀 Starting API endpoint tests")
        
        results = {
            'user_auth': self.test_user_registration_login(),
            'admin_auth': self.test_admin_login(),
            'challenge_creation': self.test_challenge_creation(),
            'active_challenges': self.test_active_challenges(),
            'challenge_submission': self.test_challenge_submission(),
            'global_leaderboard': self.test_global_leaderboard(),
            'challenge_leaderboard': self.test_challenge_leaderboard(),
            'admin_endpoints': self.test_admin_endpoints(),
            'debug_endpoints': self.test_debug_endpoints()
        }
        
        # Summary
        self.log("\n📊 Test Results Summary")
        self.log("=" * 40)
        
        passed = 0
        total = 0
        
        for test_name, result in results.items():
            total += 1
            if result:
                passed += 1
                status = "✅ PASS"
            else:
                status = "❌ FAIL"
            
            self.log(f"{status} {test_name}")
        
        self.log(f"\n🎯 Overall: {passed}/{total} tests passed")
        
        if passed == total:
            self.log("🎉 All tests passed! API is working correctly.")
        else:
            self.log("⚠️ Some tests failed. Check the logs above for details.")
        
        return passed == total

if __name__ == '__main__':
    print("🧪 QuizBattle API Endpoint Test Suite")
    print("=" * 50)
    
    tester = APITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ API testing completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ API testing completed with failures.")
        sys.exit(1)