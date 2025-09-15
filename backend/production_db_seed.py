#!/usr/bin/env python3
"""
Production Database Initialization and Seeding Script
Creates tables and seeds admin user + transfers local users to production
"""
import os
import sys
from datetime import datetime

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def init_production_database():
    """Initialize production database with all tables and seed data"""
    try:
        print("🚀 Starting Production Database Initialization...")
        
        # Import after setting path
        from app import create_app, db
        from app.models import Admin, User, QuizQuestion, Challenge, QuizResult
        from werkzeug.security import generate_password_hash
        
        app = create_app()
        
        with app.app_context():
            print("✅ App context created")
            
            # Create all database tables
            print("🔧 Creating database tables...")
            db.create_all()
            print("✅ All tables created successfully")
            
            # Check and create admin user
            print("👤 Setting up admin user...")
            existing_admin = Admin.query.filter_by(username='admin').first()
            if existing_admin:
                print("ℹ️ Admin user already exists, updating password...")
                existing_admin.password_hash = generate_password_hash('Admin@123')
                db.session.commit()
            else:
                admin = Admin(username='admin')
                admin.set_password('Admin@123')
                db.session.add(admin)
                db.session.commit()
                print("✅ Admin created: username=admin, password=Admin@123")
            
            # Seed some sample users for testing
            print("👥 Creating sample users...")
            sample_users = [
                {'username': 'student1', 'email': 'student1@example.com', 'password': 'Student@123'},
                {'username': 'student2', 'email': 'student2@example.com', 'password': 'Student@123'},
                {'username': 'teacher1', 'email': 'teacher1@example.com', 'password': 'Teacher@123'},
            ]
            
            for user_data in sample_users:
                existing_user = User.query.filter_by(username=user_data['username']).first()
                if not existing_user:
                    user = User(
                        username=user_data['username'],
                        email=user_data['email'],
                        password_hash=generate_password_hash(user_data['password'])
                    )
                    db.session.add(user)
                    print(f"  ✅ Created user: {user_data['username']}")
                else:
                    print(f"  ℹ️ User {user_data['username']} already exists")
            
            db.session.commit()
            
            # Create some sample quiz questions
            print("📝 Creating sample quiz questions...")
            sample_questions = [
                {
                    'text': 'What is the capital of France?',
                    'options': ['London', 'Berlin', 'Paris', 'Madrid'],
                    'answer': 2,  # Paris is at index 2
                    'difficulty': 'easy',
                    'exam_type': 'General Knowledge'
                },
                {
                    'text': 'What is 2 + 2?',
                    'options': ['3', '4', '5', '6'],
                    'answer': 1,  # 4 is at index 1
                    'difficulty': 'easy',
                    'exam_type': 'Mathematics'
                },
                {
                    'text': 'Which planet is known as the Red Planet?',
                    'options': ['Venus', 'Mars', 'Jupiter', 'Saturn'],
                    'answer': 1,  # Mars is at index 1
                    'difficulty': 'easy',
                    'exam_type': 'Science'
                }
            ]
            
            for q_data in sample_questions:
                existing_q = QuizQuestion.query.filter_by(text=q_data['text']).first()
                if not existing_q:
                    question = QuizQuestion(**q_data)
                    db.session.add(question)
                    print(f"  ✅ Created question: {q_data['text'][:50]}...")
            
            db.session.commit()
            
            # Verify everything was created
            print("\n📊 Database Summary:")
            print(f"  - Admins: {Admin.query.count()}")
            print(f"  - Users: {User.query.count()}")  
            print(f"  - Questions: {QuizQuestion.query.count()}")
            print(f"  - Challenges: {Challenge.query.count()}")
            print(f"  - Results: {QuizResult.query.count()}")
            
            print("🎉 Production database initialization completed successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Production database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("PRODUCTION DATABASE INITIALIZATION & SEEDING")  
    print("=" * 60)
    
    success = init_production_database()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ SUCCESS! Production database is fully initialized")
        print("✅ Admin user created/updated")
        print("✅ Sample users and questions added")
        print("✅ Ready for testing!")
        print("=" * 60)
        exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ FAILED! Check the errors above")
        print("=" * 60)
        exit(1)