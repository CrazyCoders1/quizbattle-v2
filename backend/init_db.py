#!/usr/bin/env python3
"""
Database initialization script for QuizBattle
"""
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Set environment variables
os.environ.setdefault('FLASK_APP', 'wsgi.py')

from app import create_app, db
from app.models import User, Admin, QuizQuestion, Challenge, QuizResult, Leaderboard
from werkzeug.security import generate_password_hash

def init_database():
    """Initialize database with tables and sample data"""
    app = create_app()
    
    with app.app_context():
        try:
            # Create all tables (this will use migration schema if migrations have run)
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Create admin user if it doesn't exist
            admin = Admin.query.filter_by(username='admin').first()
            if not admin:
                admin_password = os.environ.get('ADMIN_PASSWORD', 'admin987')
                admin = Admin(username='admin')
                
                # Try to create admin with standard method first
                try:
                    admin.set_password(admin_password)
                    db.session.add(admin)
                    db.session.commit()
                    print(f"✅ Admin user created: admin/{admin_password}")
                except Exception as password_error:
                    # If password hash is too long, use a shorter method
                    db.session.rollback()
                    print(f"⚠️ Standard password hash failed, trying shorter method: {password_error}")
                    
                    # Use PBKDF2 with SHA1 which produces shorter hashes
                    admin.password_hash = generate_password_hash(admin_password, method='pbkdf2:sha1')
                    db.session.add(admin)
                    db.session.commit()
                    print(f"✅ Admin user created with fallback method: admin/{admin_password}")
            else:
                print("✅ Admin user already exists")
            
            # Add sample questions if none exist
            if QuizQuestion.query.count() == 0:
                sample_questions = [
                    QuizQuestion(
                        text="What is the capital of India?",
                        options=["Mumbai", "Delhi", "Kolkata", "Chennai"],
                        answer=1,
                        difficulty="easy",
                        exam_type="General"
                    ),
                    QuizQuestion(
                        text="What is 2+2?",
                        options=["3", "4", "5", "6"],
                        answer=1,
                        difficulty="easy",
                        exam_type="Math"
                    ),
                    QuizQuestion(
                        text="Which planet is closest to the Sun?",
                        options=["Venus", "Earth", "Mercury", "Mars"],
                        answer=2,
                        difficulty="medium",
                        exam_type="Science"
                    )
                ]
                for q in sample_questions:
                    db.session.add(q)
                db.session.commit()
                print(f"✅ Added {len(sample_questions)} sample questions")
            else:
                print("✅ Sample questions already exist")
            
            print("🎉 Database initialization completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Database initialization failed: {str(e)}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)