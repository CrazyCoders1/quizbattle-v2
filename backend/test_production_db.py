#!/usr/bin/env python3
"""
Test production database state directly to diagnose 500 errors
"""
import os
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
import traceback
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_production_database():
    """Test production database connection and data"""
    
    # Get production database URL
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ DATABASE_URL not found in environment")
        return False
    
    print("=" * 60)
    print("🔍 PRODUCTION DATABASE TEST")
    print("=" * 60)
    print(f"Database URL: {db_url[:50]}...")
    
    try:
        # Create engine and session
        engine = create_engine(db_url, echo=False)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        print("✅ Database connection successful")
        
        # Check if tables exist
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"📋 Tables found: {tables}")
        
        if not tables:
            print("❌ No tables found - database not initialized!")
            return False
        
        # Check users table
        if 'users' in tables:
            result = session.execute(text("SELECT COUNT(*) FROM users"))
            user_count = result.scalar()
            print(f"👥 Users table: {user_count} users")
            
            # Show sample users
            if user_count > 0:
                result = session.execute(text("SELECT id, username, email FROM users LIMIT 5"))
                users = result.fetchall()
                for user in users:
                    print(f"   - User {user[0]}: {user[1]} ({user[2]})")
        
        # Check admin_users table
        if 'admin_users' in tables:
            result = session.execute(text("SELECT COUNT(*) FROM admin_users"))
            admin_count = result.scalar()
            print(f"👑 Admin users table: {admin_count} admins")
            
            if admin_count > 0:
                result = session.execute(text("SELECT id, username FROM admin_users LIMIT 3"))
                admins = result.fetchall()
                for admin in admins:
                    print(f"   - Admin {admin[0]}: {admin[1]}")
        
        # Check quiz_questions table
        if 'quiz_questions' in tables:
            result = session.execute(text("SELECT COUNT(*) FROM quiz_questions"))
            question_count = result.scalar()
            print(f"❓ Quiz questions table: {question_count} questions")
        
        # Test a simple user query like registration would do
        print("\n🧪 Testing user insertion simulation...")
        try:
            # Try to execute what registration would do (without actually inserting)
            test_query = text("""
                SELECT 1 FROM users WHERE email = 'test@example.com' OR username = 'testuser'
            """)
            result = session.execute(test_query)
            print("✅ User query simulation successful")
            
        except Exception as e:
            print(f"❌ User query simulation failed: {str(e)}")
            print(traceback.format_exc())
        
        # Test admin authentication simulation
        print("\n🧪 Testing admin authentication simulation...")
        try:
            test_query = text("""
                SELECT id, username, password FROM admin_users WHERE username = 'admin'
            """)
            result = session.execute(test_query)
            admin_data = result.fetchone()
            if admin_data:
                print(f"✅ Admin user found: {admin_data[1]}")
            else:
                print("❌ No admin user found with username 'admin'")
                
        except Exception as e:
            print(f"❌ Admin query simulation failed: {str(e)}")
            print(traceback.format_exc())
        
        session.close()
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {str(e)}")
        print(traceback.format_exc())
        return False

def test_environment_variables():
    """Check if all required environment variables are set"""
    print("=" * 60)
    print("🔧 ENVIRONMENT VARIABLES CHECK")
    print("=" * 60)
    
    required_vars = [
        'DATABASE_URL',
        'MONGODB_URI', 
        'SECRET_KEY',
        'FLASK_ENV'
    ]
    
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Show partial value for security
            display_value = value[:20] + "..." if len(value) > 20 else value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: NOT SET")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {missing_vars}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 QuizBattle Production Database Test")
    
    # Test environment variables
    env_ok = test_environment_variables()
    print()
    
    # Test database
    db_ok = test_production_database()
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    if env_ok and db_ok:
        print("✅ All tests passed - database appears healthy")
        print("   The 500 errors might be due to application-level issues")
    else:
        print("❌ Tests failed - this explains the 500 errors")
        if not env_ok:
            print("   → Check environment variable configuration in Render")
        if not db_ok:
            print("   → Database needs to be re-initialized")