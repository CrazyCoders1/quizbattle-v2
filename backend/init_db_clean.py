#!/usr/bin/env python3
"""
Clean database initialization script for QuizBattle
Creates tables and default admin user
"""
import os
import sys

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app import create_app, db
from app.models import Admin

def init_database():
    app = create_app()
    
    with app.app_context():
        print("=== QUIZBATTLE DATABASE INITIALIZATION ===")
        
        try:
            # Create all tables
            print("\n🔧 Creating database tables...")
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Check if admin already exists
            existing_admin = Admin.query.filter_by(username='admin').first()
            if existing_admin:
                print("✅ Admin user already exists")
            else:
                # Create default admin user
                print("\n👤 Creating default admin user...")
                admin = Admin(username='admin')
                admin.set_password('admin123')  # Default password
                db.session.add(admin)
                db.session.commit()
                print("✅ Default admin created (username: admin, password: admin123)")
            
            # Verify tables exist
            print("\n🔍 Verifying database structure...")
            tables = db.engine.table_names()
            expected_tables = ['user', 'admin', 'quiz_question', 'challenge', 'quiz_result']
            
            for table in expected_tables:
                if table in tables:
                    print(f"  ✅ Table '{table}' exists")
                else:
                    print(f"  ❌ Table '{table}' missing")
            
            print(f"\n📊 Database contains {len(tables)} tables total")
            print("🎉 Database initialization completed successfully!")
            
            return True
            
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    success = init_database()
    if success:
        print("\n✅ Ready for production!")
        print("🔗 You can now test user registration and login")
    else:
        print("\n❌ Fix the errors above and try again")
        sys.exit(1)