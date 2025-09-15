#!/usr/bin/env python3
"""
Test production database connectivity and basic operations
"""
import os
import sys

# Set production environment variables
os.environ['DATABASE_URL'] = 'postgresql://neondb_owner:npg_NY1EtTX5cqZH@ep-dawn-star-a1lemfrx-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
os.environ['MONGO_URI'] = 'mongodb+srv://quizbattle-db:4XPuEpIO2UUMemYR@cluster0.pzs2nrd.mongodb.net/quizbattle?retryWrites=true&w=majority&appName=Cluster0'
os.environ['FLASK_ENV'] = 'production'

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def test_production_database():
    try:
        print("Testing Production Database Connection...")
        
        from app import create_app, db
        from app.models import Admin, User, QuizQuestion
        
        app = create_app()
        
        with app.app_context():
            # Test connection and create tables
            print("Creating tables...")
            db.create_all()
            
            # Test admin creation
            admin = Admin.query.filter_by(username='admin').first()
            if not admin:
                admin = Admin(username='admin')
                admin.set_password('Admin@123')
                db.session.add(admin)
                db.session.commit()
                print("Admin user created")
            else:
                print("Admin user already exists")
            
            # Count records
            admin_count = Admin.query.count()
            user_count = User.query.count()
            question_count = QuizQuestion.query.count()
            
            print(f"Database Summary:")
            print(f"- Admins: {admin_count}")
            print(f"- Users: {user_count}")
            print(f"- Questions: {question_count}")
            
            return True
            
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == '__main__':
    success = test_production_database()
    if success:
        print("Production database test PASSED!")
    else:
        print("Production database test FAILED!")
    exit(0 if success else 1)