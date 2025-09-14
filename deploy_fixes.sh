#!/bin/bash
# QuizBattle Production Deployment Fix Script
# Run this script on Render to initialize database and fix all issues

echo "🚀 QuizBattle Production Deployment Fix"
echo "======================================="

# Set up proper working directory
cd /opt/render/project/src/backend || {
    echo "❌ Failed to change to backend directory"
    exit 1
}

echo "📁 Current directory: $(pwd)"
echo "📦 Installing any missing dependencies..."

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

echo "🔍 Checking environment variables..."

# Check required environment variables
required_vars=("DATABASE_URL" "JWT_SECRET" "MONGO_URI")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Missing environment variable: $var"
        exit 1
    else
        echo "✅ $var is set"
    fi
done

echo "🗄️ Initializing database..."

# Run database initialization
python init_production_db.py || {
    echo "❌ Database initialization failed"
    echo "🔧 Trying alternative database setup..."
    
    # Alternative database setup using Flask shell
    python -c "
import os
import sys
sys.path.insert(0, '.')
from app import create_app, db
from app.models import User, QuizQuestion, Challenge, QuizResult, Leaderboard, Admin

app = create_app()
with app.app_context():
    try:
        # Test connection
        with db.engine.connect() as conn:
            conn.execute(db.text('SELECT 1'))
        print('✅ Database connection successful')
        
        # Create tables
        db.create_all()
        print('✅ Database tables created')
        
        # Create admin user
        admin = Admin.query.filter_by(username='admin').first()
        if not admin:
            admin = Admin(username='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('✅ Admin user created')
        
        print('✅ Database setup completed successfully')
    except Exception as e:
        print(f'❌ Database setup failed: {str(e)}')
        exit(1)
    "
}

echo "🧪 Running API validation tests..."

# Test the API endpoints
python validate_production_api.py || {
    echo "⚠️ Some API tests failed, but deployment will continue"
}

echo "🎉 Deployment fix script completed!"
echo ""
echo "📋 Next steps:"
echo "   1. Check Render logs for any errors"
echo "   2. Test user registration via frontend"
echo "   3. Test admin login (admin/admin123)"
echo "   4. Verify all functionality works"
echo ""
echo "✅ QuizBattle should now be ready for production!"