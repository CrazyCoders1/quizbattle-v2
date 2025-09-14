#!/usr/bin/env python3
"""
Simple one-liner database initialization for Render console
Run: python render_db_init.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set required environment variables if not set
os.environ.setdefault('FLASK_APP', 'run.py')

try:
    from app import create_app, db
    from app.models import User, QuizQuestion, Challenge, QuizResult, Leaderboard, Admin
    
    print("🗄️ Initializing QuizBattle Database...")
    
    app = create_app()
    with app.app_context():
        # Test connection
        print("📡 Testing database connection...")
        with db.engine.connect() as conn:
            result = conn.execute(db.text("SELECT 1"))
            print("✅ Database connection successful!")
        
        # Create all tables
        print("🔨 Creating database tables...")
        db.create_all()
        print("✅ All tables created!")
        
        # Create admin user
        print("👤 Creating admin user...")
        admin = Admin.query.filter_by(username='admin').first()
        if not admin:
            admin = Admin(username='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin created: admin/admin123")
        else:
            print("ℹ️ Admin already exists")
        
        # Add sample questions
        print("📚 Adding sample questions...")
        if QuizQuestion.query.count() == 0:
            questions = [
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
                )
            ]
            for q in questions:
                db.session.add(q)
            db.session.commit()
            print(f"✅ Added {len(questions)} sample questions")
        
        # Print stats
        print(f"\n📊 Database Status:")
        print(f"   👥 Users: {User.query.count()}")
        print(f"   👨‍💼 Admins: {Admin.query.count()}")
        print(f"   📝 Questions: {QuizQuestion.query.count()}")
        print(f"   🎯 Challenges: {Challenge.query.count()}")
        
        print(f"\n🎉 Database initialization completed!")
        print(f"🔑 Admin credentials: admin / admin123")
        print(f"✅ API should now work correctly!")

except Exception as e:
    print(f"❌ Database initialization failed!")
    print(f"Error: {str(e)}")
    print(f"Type: {type(e).__name__}")
    
    # Print additional debugging info
    if "does not exist" in str(e).lower():
        print("💡 Database or tables may not exist")
    elif "connection" in str(e).lower():
        print("💡 Database connection issue")
        print(f"DATABASE_URL present: {'Yes' if os.environ.get('DATABASE_URL') else 'No'}")
    elif "permission" in str(e).lower():
        print("💡 Database permission issue")
    
    sys.exit(1)