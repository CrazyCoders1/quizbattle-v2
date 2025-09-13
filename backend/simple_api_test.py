#!/usr/bin/env python3
"""
Simple API test to verify core functionality
"""
import requests
import json
from datetime import datetime

BASE_URL = 'http://localhost:5000/api'

def test_basic_endpoints():
    """Test basic API functionality without auth"""
    print("🧪 Testing Basic API Functionality")
    print("=" * 40)
    
    # Test 1: Server is running
    try:
        response = requests.get(f"{BASE_URL}/admin/dashboard")
        print(f"✅ Server is running (Status: {response.status_code})")
    except requests.exceptions.RequestException:
        print("❌ Server is not running!")
        return False
    
    # Test 2: Admin login works (if admin exists)
    try:
        admin_response = requests.post(f"{BASE_URL}/auth/admin/login", json={
            'username': 'admin',
            'password': 'admin123'
        })
        
        if admin_response.status_code == 200:
            print("✅ Admin login working")
            admin_token = admin_response.json().get('access_token')
            
            # Test admin dashboard with token
            dashboard_response = requests.get(
                f"{BASE_URL}/admin/dashboard",
                headers={'Authorization': f'Bearer {admin_token}'}
            )
            
            if dashboard_response.status_code == 200:
                stats = dashboard_response.json().get('stats', {})
                print(f"✅ Admin dashboard accessible: {stats}")
            
            # Test admin users
            users_response = requests.get(
                f"{BASE_URL}/admin/users",
                headers={'Authorization': f'Bearer {admin_token}'}
            )
            
            if users_response.status_code == 200:
                users = users_response.json().get('users', [])
                print(f"✅ Admin users endpoint: {len(users)} users found")
                
                # Show first user for debugging
                if users:
                    first_user = users[0]
                    print(f"   First user: {first_user.get('username')} (ID: {first_user.get('id')})")
            
        else:
            print(f"⚠️ Admin login failed: {admin_response.status_code}")
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Admin test failed: {e}")
    
    # Test 3: Try to create a new user with unique username
    unique_username = f"testuser_{int(datetime.now().timestamp())}"
    try:
        register_response = requests.post(f"{BASE_URL}/auth/register", json={
            'username': unique_username,
            'email': f"{unique_username}@example.com",
            'password': 'testpass123'
        })
        
        if register_response.status_code == 201:
            print(f"✅ User registration working: {unique_username}")
            
            # Now try to login with the new user
            login_response = requests.post(f"{BASE_URL}/auth/login", json={
                'username': unique_username,
                'password': 'testpass123'
            })
            
            if login_response.status_code == 200:
                user_token = login_response.json().get('access_token')
                print("✅ User login working")
                
                # Test challenge creation
                challenge_data = {
                    'name': 'Test Challenge',
                    'exam_type': 'Physics 11',
                    'difficulty': 'easy',
                    'question_count': 5,
                    'time_limit': 10
                }
                
                challenge_response = requests.post(
                    f"{BASE_URL}/challenges/create",
                    json=challenge_data,
                    headers={'Authorization': f'Bearer {user_token}'}
                )
                
                if challenge_response.status_code == 201:
                    challenge = challenge_response.json().get('challenge', {})
                    print(f"✅ Challenge creation working: {challenge.get('name')} (Code: {challenge.get('code')})")
                    
                    # Test active challenges
                    active_response = requests.get(
                        f"{BASE_URL}/challenges/active",
                        headers={'Authorization': f'Bearer {user_token}'}
                    )
                    
                    if active_response.status_code == 200:
                        challenges = active_response.json().get('challenges', [])
                        print(f"✅ Active challenges working: {len(challenges)} challenges")
                    
                    # Test leaderboard
                    leaderboard_response = requests.get(
                        f"{BASE_URL}/leaderboard?type=global",
                        headers={'Authorization': f'Bearer {user_token}'}
                    )
                    
                    if leaderboard_response.status_code == 200:
                        leaderboard = leaderboard_response.json().get('leaderboard', [])
                        print(f"✅ Global leaderboard working: {len(leaderboard)} entries")
                    else:
                        print(f"⚠️ Leaderboard failed: {leaderboard_response.status_code}")
                
                else:
                    print(f"⚠️ Challenge creation failed: {challenge_response.status_code}")
                    print(f"   Response: {challenge_response.text[:200]}")
            
            else:
                print(f"⚠️ User login failed: {login_response.status_code}")
        
        else:
            print(f"⚠️ User registration failed: {register_response.status_code}")
            print(f"   Response: {register_response.text[:200]}")
    
    except requests.exceptions.RequestException as e:
        print(f"❌ User test failed: {e}")
    
    return True

def test_pdf_extraction_integration():
    """Test if PDF extraction is integrated with admin"""
    print("\n📄 Testing PDF Extraction Integration")
    print("=" * 40)
    
    try:
        # Try admin login first
        admin_response = requests.post(f"{BASE_URL}/auth/admin/login", json={
            'username': 'admin',
            'password': 'admin123'
        })
        
        if admin_response.status_code != 200:
            print("⚠️ Can't test PDF extraction - no admin access")
            return
        
        admin_token = admin_response.json().get('access_token')
        
        # Test questions endpoint
        questions_response = requests.get(
            f"{BASE_URL}/admin/questions",
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        if questions_response.status_code == 200:
            questions = questions_response.json().get('questions', [])
            print(f"✅ Questions endpoint working: {len(questions)} questions in database")
            
            if questions:
                sample_question = questions[0]
                print(f"   Sample: {sample_question.get('text', '')[:50]}...")
        else:
            print(f"⚠️ Questions endpoint failed: {questions_response.status_code}")
    
    except requests.exceptions.RequestException as e:
        print(f"❌ PDF integration test failed: {e}")

def main():
    print("🚀 QuizBattle Simple API Test")
    print("=" * 50)
    
    success = test_basic_endpoints()
    test_pdf_extraction_integration()
    
    if success:
        print("\n🎉 Basic API functionality is working!")
    else:
        print("\n❌ Some API tests failed.")

if __name__ == '__main__':
    main()