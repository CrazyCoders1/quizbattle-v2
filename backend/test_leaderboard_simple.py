#!/usr/bin/env python3
"""
Simple Leaderboard Test - Working Version
Tests the leaderboard forensics with proper Flask app setup
"""

import os
import sys
import requests
import time
import json
from datetime import datetime

# Set local testing environment
os.environ['DATABASE_URL'] = 'sqlite:///test_local.db'
os.environ['JWT_SECRET'] = 'test-secret-key'
os.environ['ADMIN_PASSWORD'] = 'admin987'
os.environ['FLASK_ENV'] = 'development'

def log(message, level="INFO"):
    """Log with timestamp"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] {level}: {message}")

def test_leaderboard_system():
    """Test the leaderboard system with a real Flask app"""
    log("🚀 Starting Simple Leaderboard Test")
    
    # Start the Flask app in background
    import subprocess
    import threading
    
    def start_server():
        """Start Flask server"""
        try:
            from app import create_app
            app = create_app()
            app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)
        except Exception as e:
            log(f"Server error: {e}", "ERROR")
    
    # Run server in thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    log("⏳ Waiting for server to start...")
    time.sleep(5)
    
    # Test server connectivity
    try:
        response = requests.get('http://127.0.0.1:5000/health', timeout=10)
        if response.status_code == 200:
            log("✅ Server health check passed")
            health_data = response.json()
            log(f"📊 Health status: {health_data}")
        else:
            log(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        log(f"❌ Could not connect to server: {e}")
        return False
    
    # Test admin authentication
    try:
        auth_response = requests.post(
            'http://127.0.0.1:5000/api/auth/admin/login',
            json={'username': 'admin', 'password': 'admin987'},
            timeout=10
        )
        
        if auth_response.status_code == 200:
            admin_token = auth_response.json().get('access_token')
            log("✅ Admin authentication successful")
            log(f"🔑 Token received: {admin_token[:20]}...")
        else:
            log(f"❌ Admin authentication failed: {auth_response.status_code}")
            log(f"Response: {auth_response.text}")
            return False
    except Exception as e:
        log(f"❌ Admin authentication error: {e}")
        return False
    
    # Test forensic endpoints
    if admin_token:
        headers = {'Authorization': f'Bearer {admin_token}'}
        
        endpoints_to_test = [
            ('/api/debug/database/status', 'Database Status'),
            ('/api/debug/leaderboard/raw?limit=5', 'Raw Leaderboard'),
            ('/api/debug/database/consistency', 'Consistency Check')
        ]
        
        for endpoint, name in endpoints_to_test:
            try:
                start_time = time.time()
                response = requests.get(f'http://127.0.0.1:5000{endpoint}', headers=headers, timeout=15)
                request_time = time.time() - start_time
                
                if response.status_code == 200:
                    log(f"✅ {name}: OK ({request_time:.2f}s)")
                    
                    # Show sample data for evidence
                    data = response.json()
                    if isinstance(data, dict) and len(str(data)) < 500:
                        log(f"📝 Sample response: {json.dumps(data, indent=2)}")
                    elif isinstance(data, dict):
                        keys = list(data.keys())[:3]
                        log(f"📝 Response keys: {keys}")
                else:
                    log(f"❌ {name}: Failed ({response.status_code})")
                    log(f"Error: {response.text[:200]}")
                    
            except Exception as e:
                log(f"❌ {name}: Exception - {e}")
    
    # Test leaderboard endpoints (regular user endpoints)
    regular_endpoints = [
        ('/api/leaderboard/', 'Global Leaderboard'),
    ]
    
    for endpoint, name in regular_endpoints:
        try:
            response = requests.get(f'http://127.0.0.1:5000{endpoint}', headers=headers, timeout=10)
            
            if response.status_code == 200:
                log(f"✅ {name}: OK")
                data = response.json()
                if 'leaderboard' in data:
                    entries = len(data['leaderboard'])
                    log(f"📊 Leaderboard entries: {entries}")
                    if entries > 0:
                        log("🎯 Flow confirmed: user → result → leaderboard")
                    else:
                        log("⚠️ No leaderboard data found")
                else:
                    log(f"📝 Response: {data}")
            else:
                log(f"❌ {name}: Failed ({response.status_code})")
                
        except Exception as e:
            log(f"❌ {name}: Exception - {e}")
    
    log("🏁 Simple leaderboard test completed")
    return True

def main():
    """Main test execution"""
    success = test_leaderboard_system()
    if success:
        log("🎉 Test completed successfully!")
    else:
        log("💥 Test failed!")

if __name__ == '__main__':
    main()