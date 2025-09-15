#!/usr/bin/env python3
"""
Production startup script for Render deployment
Ensures database is initialized before starting the app
"""
import os
import sys
import subprocess
import time

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            if result.stdout:
                print(f"   Output: {result.stdout[:200]}...")
            return True
        else:
            print(f"❌ {description} failed with return code {result.returncode}")
            if result.stderr:
                print(f"   Error: {result.stderr[:200]}...")
            if result.stdout:
                print(f"   Output: {result.stdout[:200]}...")
            return False
    except subprocess.TimeoutExpired:
        print(f"❌ {description} timed out after 60 seconds")
        return False
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return False

def main():
    print("=" * 60)
    print("🚀 QUIZBATTLE PRODUCTION STARTUP")
    print("=" * 60)
    
    # Step 1: Initialize database with comprehensive seeding
    if not run_command("python production_db_seed.py", "Database initialization & seeding"):
        print("❌ Database initialization failed, but attempting to continue...")
    
    # Wait a moment for database to be ready
    print("⏳ Waiting 5 seconds for database to be ready...")
    time.sleep(5)
    
    # Step 2: Start the application
    print("🚀 Starting Gunicorn application server...")
    
    # Use exec to replace the process (important for Render)
    os.execv('/opt/render/project/src/.venv/bin/gunicorn', [
        'gunicorn',
        '-b', '0.0.0.0:10000',
        '-w', '4',  # 4 workers for better performance
        '--timeout', '120',  # 2 minute timeout
        '--max-requests', '1000',  # Restart workers after 1000 requests
        '--preload',  # Preload the app for better memory usage
        'wsgi:app'
    ])

if __name__ == '__main__':
    main()