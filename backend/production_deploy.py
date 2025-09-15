#!/usr/bin/env python3
"""
QuizBattle Production Deployment Script - Sequential Execution
Using real credentials for Render, Neon Postgres, and MongoDB Atlas
"""
import requests
import json
import os
import time
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash
import pymongo
from datetime import datetime
import traceback

# Real Production Credentials
RENDER_SERVICE_ID = "srv-d339gs3uibrs73ae5keg"
RENDER_API_KEY = "rnd_iJR8ksNjoCQbyE2HFele7Mn0Utyi"
DATABASE_URL = "postgresql://neondb_owner:npg_NY1EtTX5cqZH@ep-dawn-star-a1lemfrx-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
MONGODB_URI = "mongodb+srv://quizbattle-db:4XPuEpIO2UUMemYR@cluster0.mongodb.net/quizbattle?retryWrites=true&w=majority"
GITHUB_REPO = "https://github.com/CrazyCoders1/quizbattle"

# Deployment Log
deployment_log = []

def log_step(step_name, status, details="", error=None):
    """Log deployment step with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {
        "timestamp": timestamp,
        "step": step_name,
        "status": status,
        "details": details,
        "error": str(error) if error else None
    }
    deployment_log.append(log_entry)
    
    # Print to console
    status_icon = "✅" if status == "SUCCESS" else "❌" if status == "ERROR" else "⏳"
    print(f"{status_icon} [{timestamp}] {step_name}")
    if details:
        print(f"   {details}")
    if error:
        print(f"   ERROR: {error}")
    print()

def step1_fix_python_runtime():
    """Step 1: Fix Python Runtime on Render"""
    log_step("1️⃣ FIXING PYTHON RUNTIME", "IN_PROGRESS", "Updating to Python 3.11...")
    
    try:
        url = f"https://api.render.com/v1/services/{RENDER_SERVICE_ID}"
        headers = {
            'Authorization': f'Bearer {RENDER_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        # Get current service config
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code != 200:
            raise Exception(f"Failed to get service info: {response.status_code} - {response.text}")
        
        service_data = response.json()
        current_runtime = service_data.get('runtime', 'unknown')
        log_step("Current Runtime Check", "INFO", f"Current runtime: {current_runtime}")
        
        # Update to Python 3.11
        update_payload = {
            "runtime": "python3.11"
        }
        
        response = requests.patch(url, headers=headers, json=update_payload, timeout=30)
        if response.status_code == 200:
            updated_service = response.json()
            new_runtime = updated_service.get('runtime', 'unknown')
            log_step("1️⃣ FIXING PYTHON RUNTIME", "SUCCESS", f"Runtime updated to {new_runtime}")
            return True
        else:
            raise Exception(f"Update failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        log_step("1️⃣ FIXING PYTHON RUNTIME", "ERROR", error=e)
        return False

def step2_update_environment_variables():
    """Step 2: Update Render Environment Variables"""
    log_step("2️⃣ UPDATING ENVIRONMENT VARIABLES", "IN_PROGRESS", "Setting all required variables...")
    
    try:
        # Environment variables for production
        env_vars = [
            {"key": "DATABASE_URL", "value": DATABASE_URL},
            {"key": "MONGODB_URI", "value": MONGODB_URI},
            {"key": "SECRET_KEY", "value": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0"},
            {"key": "JWT_SECRET", "value": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0"},
            {"key": "FLASK_ENV", "value": "production"},
            {"key": "PORT", "value": "5000"},
            {"key": "PYTHONPATH", "value": "/opt/render/project/src"}
        ]
        
        url = f"https://api.render.com/v1/services/{RENDER_SERVICE_ID}/env-vars"
        headers = {
            'Authorization': f'Bearer {RENDER_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        response = requests.put(url, headers=headers, json=env_vars, timeout=60)
        if response.status_code == 200:
            result = response.json()
            log_step("2️⃣ UPDATING ENVIRONMENT VARIABLES", "SUCCESS", f"Set {len(env_vars)} environment variables")
            return True
        else:
            raise Exception(f"Failed to update env vars: {response.status_code} - {response.text}")
            
    except Exception as e:
        log_step("2️⃣ UPDATING ENVIRONMENT VARIABLES", "ERROR", error=e)
        return False

def step3_update_build_configuration():
    """Step 3: Update Render Build Configuration for Linux"""
    log_step("3️⃣ UPDATING BUILD CONFIGURATION", "IN_PROGRESS", "Setting Linux-compatible build...")
    
    try:
        url = f"https://api.render.com/v1/services/{RENDER_SERVICE_ID}"
        headers = {
            'Authorization': f'Bearer {RENDER_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        # Update service configuration for Linux build
        update_payload = {
            "repo": GITHUB_REPO,
            "rootDir": "backend",
            "buildCommand": "pip install --no-cache-dir -r requirements.txt",
            "startCommand": "python production_startup.py",
            "runtime": "python3.11"
        }
        
        response = requests.patch(url, headers=headers, json=update_payload, timeout=30)
        if response.status_code == 200:
            log_step("3️⃣ UPDATING BUILD CONFIGURATION", "SUCCESS", "Linux-compatible build configured")
            return True
        else:
            raise Exception(f"Build config update failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        log_step("3️⃣ UPDATING BUILD CONFIGURATION", "ERROR", error=e)
        return False

def step4_trigger_deployment():
    """Step 4: Trigger Render Deployment with Cache Clear"""
    log_step("4️⃣ TRIGGERING DEPLOYMENT", "IN_PROGRESS", "Deploying with cache clear...")
    
    try:
        url = f"https://api.render.com/v1/services/{RENDER_SERVICE_ID}/deploys"
        headers = {
            'Authorization': f'Bearer {RENDER_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        payload = {"clearCache": "clear"}
        
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        if response.status_code == 201:
            deploy_info = response.json()
            deploy_id = deploy_info.get('id', 'unknown')
            log_step("4️⃣ TRIGGERING DEPLOYMENT", "SUCCESS", f"Deploy triggered: {deploy_id}")
            
            # Wait for deployment to complete
            log_step("Waiting for Deployment", "IN_PROGRESS", "Monitoring deployment status...")
            
            for attempt in range(20):  # Wait up to 10 minutes
                time.sleep(30)
                
                # Check deployment status
                status_url = f"https://api.render.com/v1/services/{RENDER_SERVICE_ID}/deploys/{deploy_id}"
                status_response = requests.get(status_url, headers=headers, timeout=30)
                
                if status_response.status_code == 200:
                    deploy_status = status_response.json()
                    status = deploy_status.get('status', 'unknown')
                    
                    log_step("Deployment Status", "INFO", f"Status: {status} (attempt {attempt + 1}/20)")
                    
                    if status == 'live':
                        log_step("Deployment Complete", "SUCCESS", "Service is now live")
                        return True
                    elif status == 'build_failed' or status == 'failed':
                        raise Exception(f"Deployment failed with status: {status}")
                        
            raise Exception("Deployment timeout - took longer than 10 minutes")
            
        else:
            raise Exception(f"Deploy trigger failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        log_step("4️⃣ TRIGGERING DEPLOYMENT", "ERROR", error=e)
        return False

def step5_initialize_postgres():
    """Step 5: Initialize Neon Postgres Database"""
    log_step("5️⃣ INITIALIZING NEON POSTGRES", "IN_PROGRESS", "Creating tables and seeding data...")
    
    try:
        # Connect to database
        engine = create_engine(DATABASE_URL, echo=False)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        log_step("Database Connection", "SUCCESS", "Connected to Neon Postgres")
        
        # Check existing tables
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        log_step("Table Check", "INFO", f"Existing tables: {existing_tables}")
        
        # Create tables if they don't exist (using Flask-SQLAlchemy would be better, but direct SQL for now)
        if 'user' not in existing_tables:
            create_user_table = text("""
                CREATE TABLE IF NOT EXISTS "user" (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(80) UNIQUE NOT NULL,
                    email VARCHAR(120) UNIQUE NOT NULL,
                    password_hash VARCHAR(128),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            session.execute(create_user_table)
            log_step("User Table", "SUCCESS", "Created user table")
        
        if 'admin' not in existing_tables:
            create_admin_table = text("""
                CREATE TABLE IF NOT EXISTS admin (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(80) UNIQUE NOT NULL,
                    email VARCHAR(120) UNIQUE,
                    password_hash VARCHAR(128)
                )
            """)
            session.execute(create_admin_table)
            log_step("Admin Table", "SUCCESS", "Created admin table")
        
        if 'quiz_question' not in existing_tables:
            create_quiz_table = text("""
                CREATE TABLE IF NOT EXISTS quiz_question (
                    id SERIAL PRIMARY KEY,
                    question TEXT NOT NULL,
                    option_a VARCHAR(255),
                    option_b VARCHAR(255),
                    option_c VARCHAR(255),
                    option_d VARCHAR(255),
                    correct_answer VARCHAR(1),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            session.execute(create_quiz_table)
            log_step("Quiz Questions Table", "SUCCESS", "Created quiz_question table")
        
        session.commit()
        
        # Seed admin user
        admin_check = session.execute(text("SELECT COUNT(*) FROM admin WHERE username = 'admin'"))
        if admin_check.scalar() == 0:
            admin_password = generate_password_hash('Admin@123')
            insert_admin = text("""
                INSERT INTO admin (username, email, password_hash)
                VALUES ('admin', 'admin@example.com', :password_hash)
            """)
            session.execute(insert_admin, {'password_hash': admin_password})
            session.commit()
            log_step("Admin Seeding", "SUCCESS", "Admin user created (admin/Admin@123)")
        else:
            log_step("Admin Seeding", "INFO", "Admin user already exists")
        
        # Add sample quiz questions
        question_check = session.execute(text("SELECT COUNT(*) FROM quiz_question"))
        if question_check.scalar() == 0:
            sample_questions = [
                {
                    'question': 'What is the capital of France?',
                    'option_a': 'London',
                    'option_b': 'Berlin',
                    'option_c': 'Paris',
                    'option_d': 'Madrid',
                    'correct_answer': 'c'
                },
                {
                    'question': 'What is 2 + 2?',
                    'option_a': '3',
                    'option_b': '4',
                    'option_c': '5',
                    'option_d': '6',
                    'correct_answer': 'b'
                },
                {
                    'question': 'Who wrote "Romeo and Juliet"?',
                    'option_a': 'Charles Dickens',
                    'option_b': 'William Shakespeare',
                    'option_c': 'Mark Twain',
                    'option_d': 'Jane Austen',
                    'correct_answer': 'b'
                }
            ]
            
            for q in sample_questions:
                insert_question = text("""
                    INSERT INTO quiz_question (question, option_a, option_b, option_c, option_d, correct_answer)
                    VALUES (:question, :option_a, :option_b, :option_c, :option_d, :correct_answer)
                """)
                session.execute(insert_question, q)
            
            session.commit()
            log_step("Quiz Seeding", "SUCCESS", f"Added {len(sample_questions)} sample questions")
        else:
            log_step("Quiz Seeding", "INFO", "Quiz questions already exist")
        
        session.close()
        log_step("5️⃣ INITIALIZING NEON POSTGRES", "SUCCESS", "Database initialization complete")
        return True
        
    except Exception as e:
        log_step("5️⃣ INITIALIZING NEON POSTGRES", "ERROR", error=e)
        return False

def step6_initialize_mongodb():
    """Step 6: Initialize MongoDB Atlas"""
    log_step("6️⃣ INITIALIZING MONGODB ATLAS", "IN_PROGRESS", "Connecting and creating collections...")
    
    try:
        # Connect to MongoDB
        client = pymongo.MongoClient(MONGODB_URI)
        db = client.quizbattle
        
        # Test connection
        db.admin.command('ping')
        log_step("MongoDB Connection", "SUCCESS", "Connected to MongoDB Atlas")
        
        # Create collections
        required_collections = ['logs', 'admin_actions', 'pdf_uploads', 'system_events']
        existing_collections = db.list_collection_names()
        
        for collection_name in required_collections:
            if collection_name not in existing_collections:
                db.create_collection(collection_name)
                log_step(f"Collection: {collection_name}", "SUCCESS", "Created")
            else:
                log_step(f"Collection: {collection_name}", "INFO", "Already exists")
        
        # Add a test document to verify write access
        test_doc = {
            "type": "deployment_test",
            "timestamp": datetime.utcnow(),
            "message": "QuizBattle deployment successful"
        }
        db.system_events.insert_one(test_doc)
        log_step("Write Test", "SUCCESS", "MongoDB write access confirmed")
        
        client.close()
        log_step("6️⃣ INITIALIZING MONGODB ATLAS", "SUCCESS", "MongoDB initialization complete")
        return True
        
    except Exception as e:
        log_step("6️⃣ INITIALIZING MONGODB ATLAS", "ERROR", error=e)
        return False

def step7_verify_api_endpoints():
    """Step 7: Verify API Endpoints"""
    log_step("7️⃣ VERIFYING API ENDPOINTS", "IN_PROGRESS", "Testing all endpoints...")
    
    try:
        base_url = f"https://{RENDER_SERVICE_ID}.onrender.com"
        
        # Test health endpoint
        try:
            health_response = requests.get(f"{base_url}/health", timeout=30)
            if health_response.status_code == 200:
                log_step("Health Check", "SUCCESS", f"Status: {health_response.status_code}")
            else:
                log_step("Health Check", "ERROR", f"Status: {health_response.status_code}")
                return False
        except Exception as e:
            log_step("Health Check", "ERROR", error=e)
            return False
        
        # Test user registration
        try:
            registration_data = {
                "username": "testuser_deploy",
                "email": "testuser_deploy@example.com",
                "password": "testpass123"
            }
            reg_response = requests.post(f"{base_url}/api/auth/register", 
                                       json=registration_data, timeout=30)
            if reg_response.status_code == 201:
                log_step("User Registration", "SUCCESS", f"Status: {reg_response.status_code}")
            else:
                log_step("User Registration", "WARNING", f"Status: {reg_response.status_code} - {reg_response.text}")
        except Exception as e:
            log_step("User Registration", "ERROR", error=e)
        
        # Test admin login
        try:
            admin_login_data = {
                "username": "admin",
                "password": "Admin@123"
            }
            admin_response = requests.post(f"{base_url}/api/auth/admin/login",
                                         json=admin_login_data, timeout=30)
            if admin_response.status_code == 200:
                log_step("Admin Login", "SUCCESS", f"Status: {admin_response.status_code}")
            else:
                log_step("Admin Login", "WARNING", f"Status: {admin_response.status_code} - {admin_response.text}")
        except Exception as e:
            log_step("Admin Login", "ERROR", error=e)
        
        log_step("7️⃣ VERIFYING API ENDPOINTS", "SUCCESS", "Endpoint verification complete")
        return True
        
    except Exception as e:
        log_step("7️⃣ VERIFYING API ENDPOINTS", "ERROR", error=e)
        return False

def generate_final_report():
    """Generate detailed deployment report"""
    log_step("8️⃣ GENERATING FINAL REPORT", "IN_PROGRESS", "Creating deployment summary...")
    
    print("\n" + "="*80)
    print("🚀 QUIZBATTLE PRODUCTION DEPLOYMENT REPORT")
    print("="*80)
    
    success_count = sum(1 for log in deployment_log if log['status'] == 'SUCCESS')
    error_count = sum(1 for log in deployment_log if log['status'] == 'ERROR')
    
    print(f"📊 SUMMARY: {success_count} Success, {error_count} Errors")
    print(f"🕒 Total Steps: {len([log for log in deployment_log if log['step'].startswith(('1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣'))])}")
    
    print("\n📋 DETAILED LOG:")
    for log_entry in deployment_log:
        status_icon = "✅" if log_entry['status'] == 'SUCCESS' else "❌" if log_entry['status'] == 'ERROR' else "ℹ️"
        print(f"{status_icon} [{log_entry['timestamp']}] {log_entry['step']}")
        if log_entry['details']:
            print(f"   {log_entry['details']}")
        if log_entry['error']:
            print(f"   ERROR: {log_entry['error']}")
    
    print("\n🎯 FINAL STATUS:")
    if error_count == 0:
        print("✅ DEPLOYMENT SUCCESSFUL - All systems operational")
        print(f"🌐 Frontend: https://quizbattle-frontend.netlify.app")
        print(f"🔧 Backend: https://{RENDER_SERVICE_ID}.onrender.com")
    else:
        print("⚠️ DEPLOYMENT COMPLETED WITH ISSUES - Check errors above")
    
    print("="*80)
    
    log_step("8️⃣ GENERATING FINAL REPORT", "SUCCESS", "Deployment report generated")

if __name__ == "__main__":
    print("🚀 Starting QuizBattle Production Deployment")
    print("=" * 50)
    
    # Execute all steps sequentially
    steps = [
        step1_fix_python_runtime,
        step2_update_environment_variables,
        step3_update_build_configuration,
        step4_trigger_deployment,
        step5_initialize_postgres,
        step6_initialize_mongodb,
        step7_verify_api_endpoints
    ]
    
    for step_func in steps:
        success = step_func()
        if not success:
            print(f"❌ Step failed: {step_func.__name__}")
            print("Continuing with remaining steps...")
    
    # Generate final report
    generate_final_report()