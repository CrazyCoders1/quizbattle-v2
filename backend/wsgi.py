#!/usr/bin/env python3
"""
WSGI entry point for QuizBattle Render deployment
"""
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Set environment variables for deployment
os.environ.setdefault('FLASK_APP', 'wsgi.py')

# Import and create the Flask app
from app import create_app

# Create the Flask app instance
app = create_app()

# Ensure database URL is compatible with psycopg3
with app.app_context():
    database_url = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if database_url.startswith('postgres://'):
        # Convert postgres:// to postgresql:// for psycopg3
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        print(f"✅ Updated database URL for psycopg3 compatibility")
    
    print(f"🗄️ Database URI configured: {database_url[:50]}...")
    print(f"🚀 WSGI application ready for deployment")

if __name__ == "__main__":
    # For local development only
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)