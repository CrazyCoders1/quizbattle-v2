#!/usr/bin/env python3
"""
Production Database Initialization for Render
Fix the exact same database issues we had locally
"""
import os
import sys

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def init_production_database():
    try:
        print("🚀 Starting Render Database Initialization...")
        
        # Import after setting path
        from app import create_app, db
        from app.models import Admin
        
        app = create_app()
        
        with app.app_context():
            print("✅ App context created")
            
            # Create all database tables
            print("🔧 Creating database tables...")
            db.create_all()
            print("✅ All tables created successfully")
            
            # Check if admin exists
            existing_admin = Admin.query.filter_by(username='admin').first()
            if existing_admin:
                print("✅ Admin user already exists")
                return True
            
            # Create admin user
            print("👤 Creating default admin user...")
            admin = Admin(username='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin created: username=admin, password=admin123")
            
            # Verify admin was created
            verify_admin = Admin.query.filter_by(username='admin').first()
            if verify_admin:
                print("✅ Admin creation verified")
            else:
                print("❌ Admin verification failed")
                return False
                
            print("🎉 Production database initialization completed!")
            return True
            
    except Exception as e:
        print(f"❌ Production database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 50)
    print("RENDER PRODUCTION DATABASE INITIALIZATION")  
    print("=" * 50)
    
    success = init_production_database()
    
    if success:
        print("\n" + "=" * 50)
        print("✅ SUCCESS! Production database is ready")
        print("✅ You can now test user registration")
        print("✅ Admin panel is accessible")
        print("=" * 50)
        exit(0)
    else:
        print("\n" + "=" * 50)
        print("❌ FAILED! Check the errors above")
        print("=" * 50)
        exit(1)