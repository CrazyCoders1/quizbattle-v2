#!/usr/bin/env python3
"""
Production API Test for QuizBattle Hosting
Tests the live production API endpoints to verify deployment
"""
import requests
import json
from datetime import datetime

# Production API URL
PROD_API_URL = 'https://quizbattle-backend-7qzu.onrender.com'

def test_production_api():
    """Test production API endpoints"""
    print("🚀 Testing QuizBattle Production API")
    print(f"🔗 API URL: {PROD_API_URL}")
    print("=" * 60)
    
    # Test 1: Health check
    try:
        print("🏥 Testing health endpoint...")
        health_response = requests.get(f"{PROD_API_URL}/health", timeout=10)
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"✅ Health check passed: {health_data.get('status')}")
            print(f"   Database: {health_data.get('database')}")
            print(f"   Logging: {health_data.get('logging')}")
        else:
            print(f"❌ Health check failed: {health_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Root endpoint
    try:
        print("\n🏠 Testing root endpoint...")
        root_response = requests.get(f"{PROD_API_URL}/", timeout=10)
        if root_response.status_code == 200:
            root_data = root_response.json()
            print(f"✅ Root endpoint working: {root_data.get('name')} v{root_data.get('version')}")
        else:
            print(f"❌ Root endpoint failed: {root_response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
    
    # Test 3: User registration and authentication flow
    try:
        print("\n👤 Testing user authentication...")
        test_username = f"testuser_{int(datetime.now().timestamp())}"
        test_email = f"{test_username}@example.com"
        
        # Register user
        register_data = {
            'username': test_username,
            'email': test_email,
            'password': 'test123456'
        }
        
        register_response = requests.post(
            f"{PROD_API_URL}/api/auth/register",
            json=register_data,
            timeout=10
        )
        
        if register_response.status_code == 201:
            print(f"✅ User registration successful: {test_username}")
            
            # Login user
            login_response = requests.post(
                f"{PROD_API_URL}/api/auth/login",
                json={'username': test_username, 'password': 'test123456'},
                timeout=10
            )
            
            if login_response.status_code == 200:
                token = login_response.json().get('access_token')
                print("✅ User login successful")
                
                # Test authenticated endpoint - leaderboard
                headers = {'Authorization': f'Bearer {token}'}
                leaderboard_response = requests.get(
                    f"{PROD_API_URL}/api/leaderboard",
                    params={'type': 'global'},
                    headers=headers,
                    timeout=10
                )
                
                if leaderboard_response.status_code == 200:
                    leaderboard_data = leaderboard_response.json()
                    leaderboard_count = len(leaderboard_data.get('leaderboard', []))
                    print(f"✅ Leaderboard endpoint working: {leaderboard_count} entries")
                    print("🎯 LEADERBOARD IS WORKING IN PRODUCTION! 🎯")
                else:
                    print(f"❌ Leaderboard failed: {leaderboard_response.status_code}")
                    print(f"   Response: {leaderboard_response.text}")
            else:
                print(f"❌ User login failed: {login_response.status_code}")
        else:
            print(f"❌ User registration failed: {register_response.status_code}")
            print(f"   Response: {register_response.text}")
            
    except Exception as e:
        print(f"❌ Authentication test error: {e}")
    
    # Test 4: Admin endpoints (without authentication)
    try:
        print("\n🔧 Testing admin endpoints...")
        admin_dashboard_response = requests.get(f"{PROD_API_URL}/api/admin/dashboard", timeout=10)
        if admin_dashboard_response.status_code == 401:
            print("✅ Admin dashboard properly protected (401 Unauthorized)")
        else:
            print(f"⚠️ Unexpected admin dashboard response: {admin_dashboard_response.status_code}")
    except Exception as e:
        print(f"❌ Admin endpoint test error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Production API testing completed!")
    print(f"🌐 Frontend should work at: https://quizbattle-v2.netlify.app")
    print("📊 If all tests passed, the leaderboard should work in production!")
    
    return True

if __name__ == '__main__':
    test_production_api()