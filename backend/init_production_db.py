#!/usr/bin/env python3
"""
Production Database Initialization Script for QuizBattle
Handles database creation, migrations, and seeding for Render deployment
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the app to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, QuizQuestion, Challenge, QuizResult, Leaderboard, Admin

def init_database():
    """Initialize database tables and create default admin user"""
    
    print("🗄️ Initializing QuizBattle Production Database...")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Test database connection
            print("📡 Testing database connection...")
            with db.engine.connect() as conn:
                conn.execute(db.text("SELECT 1"))
            print("✅ Database connection successful!")
            
            # Create all tables
            print("🔨 Creating database tables...")
            db.create_all()
            print("✅ All tables created successfully!")
            
            # Create default admin user
            print("👤 Creating default admin user...")
            admin = Admin.query.filter_by(username='admin').first()
            if not admin:
                admin = Admin(username='admin')
                admin.set_password('admin123')  # Change in production!
                db.session.add(admin)
                db.session.commit()
                print("✅ Default admin created: username=admin, password=admin123")
            else:
                print("ℹ️ Admin user already exists")
            
            # Create sample questions if none exist
            print("📚 Creating sample questions...")
            if QuizQuestion.query.count() == 0:
                sample_questions = [
                    QuizQuestion(
                        text="What is the capital of India?",
                        options=["Mumbai", "Delhi", "Kolkata", "Chennai"],
                        answer=1,
                        difficulty="easy",
                        exam_type="General Knowledge"
                    ),
                    QuizQuestion(
                        text="Which is the largest planet in our solar system?",
                        options=["Earth", "Jupiter", "Saturn", "Neptune"],
                        answer=1,
                        difficulty="easy",
                        exam_type="Science"
                    ),
                    QuizQuestion(
                        text="What is the derivative of x²?",
                        options=["x", "2x", "x²", "2x²"],
                        answer=1,
                        difficulty="tough",
                        exam_type="JEE Main"
                    ),
                    QuizQuestion(
                        text="Which element has the atomic number 1?",
                        options=["Helium", "Hydrogen", "Lithium", "Carbon"],
                        answer=1,
                        difficulty="easy",
                        exam_type="Chemistry"
                    ),
                    QuizQuestion(
                        text="What is the speed of light in vacuum?",
                        options=["3 × 10⁸ m/s", "3 × 10⁶ m/s", "3 × 10¹⁰ m/s", "3 × 10⁴ m/s"],
                        answer=0,
                        difficulty="tough",
                        exam_type="Physics"
                    )
                ]
                
                for question in sample_questions:
                    db.session.add(question)
                
                db.session.commit()
                print(f"✅ Created {len(sample_questions)} sample questions")
            else:
                print(f"ℹ️ Found {QuizQuestion.query.count()} existing questions")
            
            # Print database stats
            print("\n📊 Database Statistics:")
            print(f"   Users: {User.query.count()}")
            print(f"   Admins: {Admin.query.count()}")
            print(f"   Questions: {QuizQuestion.query.count()}")
            print(f"   Challenges: {Challenge.query.count()}")
            print(f"   Results: {QuizResult.query.count()}")
            
            print("\n🎉 Database initialization completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Database initialization failed: {str(e)}")
            print(f"   Error type: {type(e).__name__}")
            
            # Additional debugging info
            if "does not exist" in str(e):
                print("💡 This might be a table creation issue. Check database permissions.")
            elif "connection" in str(e).lower():
                print("💡 This appears to be a database connection issue.")
                print(f"   DATABASE_URL: {os.environ.get('DATABASE_URL', 'Not set')[:50]}...")
            
            return False

def check_environment():
    """Check if all required environment variables are set"""
    
    print("🔍 Checking environment configuration...")
    
    required_vars = [
        'DATABASE_URL',
        'JWT_SECRET',
        'MONGO_URI'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
        else:
            print(f"✅ {var}: Set")
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ All required environment variables are set!")
    return True

def main():
    """Main initialization function"""
    
    print("🚀 QuizBattle Production Database Setup")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        print("❌ Environment check failed. Please set all required variables.")
        sys.exit(1)
    
    # Initialize database
    if init_database():
        print("\n✅ Setup completed successfully!")
        print("\n📋 Next steps:")
        print("   1. Test user registration API")
        print("   2. Test admin login (admin/admin123)")
        print("   3. Verify all API endpoints")
        sys.exit(0)
    else:
        print("\n❌ Setup failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()