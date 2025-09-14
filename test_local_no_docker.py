#!/usr/bin/env python3
"""
Test script to verify QuizBattle works locally without Docker
"""

import os
import sys
import time
import requests
import subprocess
import threading
from pathlib import Path

def test_local_setup():
    """Test that QuizBattle can run locally without Docker"""
    
    print("🧪 Testing QuizBattle Local Setup (No Docker)")
    print("=" * 60)
    
    # Test 1: Backend dependencies
    print("\n📦 Testing backend dependencies...")
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    # Check if we can import Flask app
    sys.path.insert(0, str(backend_dir))
    try:
        from run import app
        print("✅ Backend Flask app imports successfully")
        
        # Test health endpoint
        with app.test_client() as client:
            response = client.get('/health')
            if response.status_code == 200:
                print("✅ Health endpoint working")
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
                
    except ImportError as e:
        print(f"❌ Backend import failed: {e}")
        print("💡 Run: pip install -r requirements.txt")
        return False
    
    # Test 2: Environment variables
    print("\n🌍 Testing environment variables...")
    env_vars = ['JWT_SECRET', 'DATABASE_URL', 'MONGO_URI']
    
    # Load from .env file
    from dotenv import load_dotenv
    load_dotenv()
    
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            print(f"✅ {var}: {'*' * min(len(value), 20)}")
        else:
            print(f"⚠️ {var}: Not set")
    
    # Test 3: Frontend setup
    print("\n⚛️ Testing frontend setup...")
    frontend_dir = Path(__file__).parent / "frontend"
    
    # Check package.json
    package_json = frontend_dir / "package.json"
    if package_json.exists():
        print("✅ Frontend package.json exists")
        
        # Check if proxy is removed
        with open(package_json) as f:
            content = f.read()
            if '"proxy"' not in content:
                print("✅ Proxy removed from package.json")
            else:
                print("⚠️ Proxy still in package.json")
    else:
        print("❌ Frontend package.json not found")
    
    # Check .env file
    frontend_env = frontend_dir / ".env"
    if frontend_env.exists():
        print("✅ Frontend .env file exists")
        with open(frontend_env) as f:
            content = f.read()
            if "REACT_APP_API_URL" in content:
                print("✅ REACT_APP_API_URL configured")
            else:
                print("❌ REACT_APP_API_URL not found")
    
    # Test 4: Deployment files
    print("\n🚀 Testing deployment configuration...")
    
    project_root = Path(__file__).parent
    deployment_files = {
        "Procfile": "Render deployment",
        "netlify.toml": "Netlify deployment", 
        "render.yaml": "Render Blueprint",
        "RENDER_NETLIFY_DEPLOYMENT.md": "Deployment guide"
    }
    
    for file_name, description in deployment_files.items():
        file_path = project_root / file_name
        if file_path.exists():
            print(f"✅ {file_name}: {description}")
        else:
            print(f"❌ {file_name}: Missing")
    
    print(f"\n🎯 Local Development Commands:")
    print(f"Backend:  cd backend && pip install -r requirements.txt && flask run")
    print(f"Frontend: cd frontend && npm install && npm start")
    
    print(f"\n🌐 Production Deployment:")
    print(f"1. Push to GitHub: https://github.com/CrazyCoders1/quizbattle")
    print(f"2. Deploy backend to Render")
    print(f"3. Deploy frontend to Netlify")
    print(f"4. Set environment variables")
    
    print(f"\n✅ Setup Test Complete!")
    print(f"📖 See RENDER_NETLIFY_DEPLOYMENT.md for deployment instructions")
    
    return True

if __name__ == '__main__':
    test_local_setup()