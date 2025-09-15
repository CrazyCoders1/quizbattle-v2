#!/usr/bin/env python3
"""
Production startup script for Render deployment - Linux compatible
Ensures database is initialized before starting the app
"""
import os
import sys
import subprocess
import time
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash
import pymongo
from datetime import datetime

def initialize_postgres():
    """Initialize Postgres database"""
    print("🔧 Initializing Neon Postgres database...")
    
    try:
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            print("❌ DATABASE_URL not found")
            return False
        
        engine = create_engine(db_url, echo=False)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        print("✅ Connected to Neon Postgres")
        
        # Check existing tables
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        # Create tables if needed
        if 'user' not in existing_tables:
            session.execute(text("""
                CREATE TABLE IF NOT EXISTS "user" (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(80) UNIQUE NOT NULL,
                    email VARCHAR(120) UNIQUE NOT NULL,
                    password_hash VARCHAR(128),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            print("✅ Created user table")
        
        if 'admin' not in existing_tables:
            session.execute(text("""
                CREATE TABLE IF NOT EXISTS admin (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(80) UNIQUE NOT NULL,
                    email VARCHAR(120) UNIQUE,
                    password_hash VARCHAR(128)
                )
            """))
            print("✅ Created admin table")
        
        if 'quiz_question' not in existing_tables:
            session.execute(text("""
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
            """))
            print("✅ Created quiz_question table")
        
        session.commit()
        
        # Seed admin if not exists
        admin_check = session.execute(text("SELECT COUNT(*) FROM admin WHERE username = 'admin'"))
        if admin_check.scalar() == 0:
            admin_password = generate_password_hash('Admin@123')
            session.execute(text("""
                INSERT INTO admin (username, email, password_hash)
                VALUES ('admin', 'admin@example.com', :password_hash)
            """), {'password_hash': admin_password})
            session.commit()
            print("✅ Admin user created")
        
        session.close()
        return True
        
    except Exception as e:
        print(f"❌ Postgres initialization failed: {e}")
        return False

def initialize_mongodb():
    """Initialize MongoDB Atlas"""
    print("🔧 Initializing MongoDB Atlas...")
    
    try:
        mongodb_uri = os.getenv('MONGODB_URI')
        if not mongodb_uri:
            print("❌ MONGODB_URI not found")
            return False
        
        client = pymongo.MongoClient(mongodb_uri)
        db = client.quizbattle
        db.admin.command('ping')
        print("✅ Connected to MongoDB Atlas")
        
        # Create required collections
        collections = ['logs', 'admin_actions', 'pdf_uploads', 'system_events']
        existing_collections = db.list_collection_names()
        
        for collection_name in collections:
            if collection_name not in existing_collections:
                db.create_collection(collection_name)
                print(f"✅ Created collection: {collection_name}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ MongoDB initialization failed: {e}")
        return False

def main():
    print("=" * 60)
    print("🚀 QUIZBATTLE PRODUCTION STARTUP")
    print("=" * 60)
    
    # Initialize databases
    postgres_ok = initialize_postgres()
    mongodb_ok = initialize_mongodb()
    
    if postgres_ok:
        print("✅ Postgres ready")
    if mongodb_ok:
        print("✅ MongoDB ready")
    
    # Start the application using gunicorn directly
    print("🚀 Starting Gunicorn server...")
    
    # Get port from environment (Render sets PORT)
    port = os.getenv('PORT', '10000')
    
    # Start gunicorn with proper configuration for Render
    cmd = [
        'gunicorn',
        '--bind', f'0.0.0.0:{port}',
        '--workers', '4',
        '--timeout', '120',
        '--max-requests', '1000',
        '--preload',
        'run:app'
    ]
    
    print(f"✅ Starting server on port {port}")
    os.execvp('gunicorn', cmd)

if __name__ == '__main__':
    main()
