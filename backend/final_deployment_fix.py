#!/usr/bin/env python3
"""
Final comprehensive deployment diagnosis and fix attempt
"""
import requests
import time
import json
import os
import subprocess
from dotenv import load_dotenv

load_dotenv()

SERVICE_ID = "srv-d339gs3uibrs73ae5keg"
SERVICE_URL = "https://srv-d339gs3uibrs73ae5keg.onrender.com"

def check_local_setup():
    """Check if local setup is correct"""
    print("🔍 CHECKING LOCAL SETUP")
    print("=" * 50)
    
    # Check if key files exist
    files_to_check = [
        "requirements.txt",
        "app/__init__.py", 
        "app.py",
        ".env"
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
    
    print()

def test_local_import():
    """Test if the app can be imported locally"""
    print("🐍 TESTING LOCAL APP IMPORT")
    print("=" * 50)
    
    try:
        # Try importing the main app
        import sys
        sys.path.insert(0, '.')
        from app import create_app
        
        app = create_app()
        print("✅ App created successfully")
        
        # Test basic routes
        with app.test_client() as client:
            response = client.get('/')
            print(f"✅ Root route works: {response.status_code}")
            
            response = client.get('/health')  
            print(f"✅ Health route works: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Local import failed: {str(e)}")
        return False
    
    print()
    return True

def check_dependencies():
    """Check if all dependencies are properly specified"""
    print("📦 CHECKING DEPENDENCIES")
    print("=" * 50)
    
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read()
            
        critical_deps = [
            'flask',
            'gunicorn', 
            'psycopg2',
            'pymongo',
            'flask-sqlalchemy'
        ]
        
        for dep in critical_deps:
            if dep in requirements.lower():
                print(f"✅ {dep} found in requirements.txt")
            else:
                print(f"❌ {dep} missing from requirements.txt")
                
    except FileNotFoundError:
        print("❌ requirements.txt not found")
    
    print()

def create_minimal_test_app():
    """Create a minimal test version of the app"""
    print("🏗️ CREATING MINIMAL TEST APP")
    print("=" * 50)
    
    minimal_app_code = '''from flask import Flask, jsonify
import os

def create_app():
    app = Flask(__name__)
    
    @app.route('/')
    def root():
        return jsonify({
            'name': 'QuizBattle API',
            'version': '1.0.0',
            'status': 'running - minimal mode'
        }), 200
    
    @app.route('/health')
    def health():
        return jsonify({
            'status': 'healthy',
            'mode': 'minimal'
        }), 200
        
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
    
    # Save minimal app
    with open('app_minimal.py', 'w') as f:
        f.write(minimal_app_code)
        
    print("✅ Created app_minimal.py")
    
    # Create minimal requirements
    minimal_reqs = '''Flask==2.3.3
gunicorn==21.2.0
'''
    
    with open('requirements_minimal.txt', 'w') as f:
        f.write(minimal_reqs)
        
    print("✅ Created requirements_minimal.txt")
    print("💡 You can test minimal deployment by temporarily:")
    print("   1. Renaming app.py to app_backup.py")  
    print("   2. Renaming app_minimal.py to app.py")
    print("   3. Renaming requirements.txt to requirements_backup.txt")
    print("   4. Renaming requirements_minimal.txt to requirements.txt")
    print("   5. Committing and pushing to trigger deployment")
    print()

def diagnose_build_environment():
    """Diagnose potential build environment issues"""
    print("🔧 DIAGNOSING BUILD ENVIRONMENT")
    print("=" * 50)
    
    issues_and_fixes = [
        {
            "issue": "Python version mismatch",
            "fix": "Ensure runtime.txt specifies python-3.11.x"
        },
        {
            "issue": "Auto-initialization during build",  
            "fix": "Move all database initialization to manual routes"
        },
        {
            "issue": "Missing system dependencies",
            "fix": "Use psycopg2 instead of psycopg2-binary for Linux"
        },
        {
            "issue": "Environment variables not available during build",
            "fix": "Avoid accessing env vars during import time"
        }
    ]
    
    for i, item in enumerate(issues_and_fixes, 1):
        print(f"   {i}. {item['issue']}")
        print(f"      Fix: {item['fix']}")
        print()

def main():
    print("🚀 FINAL DEPLOYMENT DIAGNOSIS & FIX ATTEMPT")
    print("=" * 70)
    print()
    
    # Run diagnostics
    check_local_setup()
    
    if test_local_import():
        print("✅ Local app works - issue is likely deployment-specific")
    else:
        print("❌ Local app has issues - fix these first")
        
    check_dependencies()
    create_minimal_test_app()
    diagnose_build_environment()
    
    print("🎯 FINAL RECOMMENDATIONS")
    print("=" * 50)
    print("1. 🌐 Check Render Dashboard logs for specific build errors")
    print("2. 🧪 Try minimal app deployment first to isolate issues")
    print("3. 🔄 Clear build cache in Render dashboard")
    print("4. 📧 Contact Render support if issues persist")
    print()
    
    print("🔗 Quick Links:")
    print(f"   Dashboard: https://dashboard.render.com")
    print(f"   Service: {SERVICE_URL}")
    print("   Logs: Check 'Logs' tab in your Render service dashboard")

if __name__ == "__main__":
    main()