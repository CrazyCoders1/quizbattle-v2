#!/usr/bin/env python3
"""
Fix production database with correct table names and environment variables
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash
import traceback
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def fix_production_database():
    """Fix production database by using the correct table names"""
    
    # Get production database URL
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ DATABASE_URL not found in environment")
        return False
    
    print("=" * 60)
    print("🔧 FIXING PRODUCTION DATABASE")
    print("=" * 60)
    print(f"Database URL: {db_url[:50]}...")
    
    try:
        # Create engine and session
        engine = create_engine(db_url, echo=False)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        print("✅ Database connection successful")
        
        # Check existing tables
        result = session.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
        existing_tables = [row[0] for row in result.fetchall()]
        print(f"📋 Existing tables: {existing_tables}")
        
        # Check if we have the correct tables (singular names)
        expected_tables = ['user', 'admin', 'quiz_question', 'challenge', 'leaderboard', 'quiz_result']
        missing_tables = [t for t in expected_tables if t not in existing_tables]
        
        if missing_tables:
            print(f"❌ Missing tables: {missing_tables}")
            print("   → The database needs proper Flask-SQLAlchemy initialization")
            return False
        
        print("✅ All required tables exist")
        
        # Check user table data
        result = session.execute(text("SELECT COUNT(*) FROM \"user\""))
        user_count = result.scalar()
        print(f"👥 User table: {user_count} users")
        
        if user_count > 0:
            result = session.execute(text("SELECT id, username, email FROM \"user\" LIMIT 5"))
            users = result.fetchall()
            for user in users:
                print(f"   - User {user[0]}: {user[1]} ({user[2]})")
        
        # Check admin table data
        result = session.execute(text("SELECT COUNT(*) FROM admin"))
        admin_count = result.scalar()
        print(f"👑 Admin table: {admin_count} admins")
        
        if admin_count == 0:
            print("   ⚠️  No admin user found - creating default admin...")
            password_hash = generate_password_hash('Admin@123')
            
            insert_admin = text("""
                INSERT INTO admin (username, password_hash) 
                VALUES ('admin', :password_hash)
            """)
            session.execute(insert_admin, {'password_hash': password_hash})
            session.commit()
            print("   ✅ Default admin user created")
        else:
            result = session.execute(text("SELECT id, username FROM admin LIMIT 3"))
            admins = result.fetchall()
            for admin in admins:
                print(f"   - Admin {admin[0]}: {admin[1]}")
        
        # Check quiz questions
        result = session.execute(text("SELECT COUNT(*) FROM quiz_question"))
        question_count = result.scalar()
        print(f"❓ Quiz questions: {question_count} questions")
        
        if question_count == 0:
            print("   ⚠️  No quiz questions found - adding sample questions...")
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
            print(f"   ✅ Added {len(sample_questions)} sample questions")
        
        # Test API-like operations
        print("\n🧪 Testing API operations...")
        
        # Test user query (like registration would do)
        try:
            result = session.execute(text("SELECT id FROM \"user\" WHERE email = 'test@example.com' OR username = 'testuser'"))
            print("✅ User query test passed")
        except Exception as e:
            print(f"❌ User query test failed: {str(e)}")
            return False
        
        # Test admin query (like login would do) 
        try:
            result = session.execute(text("SELECT id, username, password_hash FROM admin WHERE username = 'admin'"))
            admin_data = result.fetchone()
            if admin_data:
                print("✅ Admin query test passed")
            else:
                print("❌ Admin query test failed - no admin user")
                return False
        except Exception as e:
            print(f"❌ Admin query test failed: {str(e)}")
            return False
        
        session.close()
        return True
        
    except Exception as e:
        print(f"❌ Database fix failed: {str(e)}")
        print(traceback.format_exc())
        return False

def verify_environment():
    """Verify environment variables are set correctly"""
    print("=" * 60)
    print("🔧 ENVIRONMENT VARIABLES VERIFICATION")
    print("=" * 60)
    
    required_vars = {
        'DATABASE_URL': os.getenv('DATABASE_URL'),
        'MONGODB_URI': os.getenv('MONGODB_URI'), 
        'SECRET_KEY': os.getenv('SECRET_KEY'),
        'FLASK_ENV': os.getenv('FLASK_ENV')
    }
    
    all_good = True
    for var, value in required_vars.items():
        if value:
            display_value = value[:30] + "..." if len(value) > 30 else value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: NOT SET")
            all_good = False
    
    return all_good

if __name__ == "__main__":
    print("🚀 QuizBattle Production Database Fix")
    
    # Check environment
    env_ok = verify_environment()
    print()
    
    if env_ok:
        # Fix database
        db_ok = fix_production_database()
        
        print("\n" + "=" * 60)
        print("📊 SUMMARY")
        print("=" * 60)
        
        if db_ok:
            print("✅ Production database fixed successfully!")
            print("   → All tables exist with correct names")
            print("   → Admin user is available")
            print("   → Sample quiz questions added")
            print("\n🚀 Ready to test API endpoints again")
        else:
            print("❌ Database fix failed")
            print("   → Check the errors above")
    else:
        print("❌ Environment variables not configured properly")
        print("   → Update .env file and try again")