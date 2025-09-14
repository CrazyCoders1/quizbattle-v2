from flask import Blueprint, jsonify, request, render_template_string
from app import db
from app.models import User, QuizQuestion, Challenge, QuizResult, Leaderboard, Admin
import os

setup_bp = Blueprint('setup', __name__)

# Simple HTML template for manual database initialization
SETUP_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>QuizBattle Database Setup</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .success { color: green; font-weight: bold; }
        .error { color: red; font-weight: bold; }
        .warning { color: orange; font-weight: bold; }
        button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #0056b3; }
        .status { margin: 10px 0; padding: 10px; border-left: 4px solid #007bff; background: #f8f9fa; }
    </style>
</head>
<body>
    <h1>🚀 QuizBattle Database Setup</h1>
    <p>This page allows you to initialize the QuizBattle database manually.</p>
    
    {% if status %}
        <div class="status {{ status.type }}">
            <h3>{{ status.title }}</h3>
            <p>{{ status.message }}</p>
            {% if status.details %}
                <ul>
                {% for detail in status.details %}
                    <li>{{ detail }}</li>
                {% endfor %}
                </ul>
            {% endif %}
        </div>
    {% endif %}
    
    <form method="POST" action="/api/setup/init">
        <h2>Initialize Database</h2>
        <p>This will:</p>
        <ul>
            <li>Create all database tables</li>
            <li>Create admin user (admin/admin123)</li>
            <li>Add sample quiz questions</li>
        </ul>
        <button type="submit">Initialize Database</button>
    </form>
    
    <hr>
    
    <form method="GET" action="/api/setup/status">
        <h2>Check Database Status</h2>
        <p>Check if database is properly initialized.</p>
        <button type="submit">Check Status</button>
    </form>
    
    <hr>
    
    <h3>📋 Troubleshooting</h3>
    <p>If you encounter issues:</p>
    <ul>
        <li>Check that DATABASE_URL environment variable is set</li>
        <li>Ensure your Neon database is accessible</li>
        <li>Verify network connectivity to your database</li>
    </ul>
    
    <h3>🔐 Environment Status</h3>
    <ul>
        <li>DATABASE_URL: {{ 'Set' if db_url_set else 'NOT SET' }}</li>
        <li>JWT_SECRET: {{ 'Set' if jwt_secret_set else 'NOT SET' }}</li>
        <li>MONGO_URI: {{ 'Set' if mongo_uri_set else 'NOT SET' }}</li>
    </ul>
</body>
</html>
"""

@setup_bp.route('/', methods=['GET'])
def setup_page():
    """Show the database setup page"""
    return render_template_string(SETUP_TEMPLATE,
        status=request.args.get('status'),
        db_url_set=bool(os.environ.get('DATABASE_URL')),
        jwt_secret_set=bool(os.environ.get('JWT_SECRET')),
        mongo_uri_set=bool(os.environ.get('MONGO_URI'))
    )

@setup_bp.route('/init', methods=['POST'])
def initialize_database():
    """Initialize the database manually via web interface"""
    try:
        print("🗄️ Manual database initialization starting...")
        
        # Create all tables
        db.create_all()
        print("✅ Database tables created successfully")
        
        details = ["Database tables created"]
        
        # Create admin user
        admin = Admin.query.filter_by(username='admin').first()
        if not admin:
            admin = Admin(username='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin user created: admin/admin123")
            details.append("Admin user created (admin/admin123)")
        else:
            print("ℹ️ Admin already exists")
            details.append("Admin user already exists")
        
        # Add sample questions
        if QuizQuestion.query.count() == 0:
            sample_questions = [
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
            for q in sample_questions:
                db.session.add(q)
            db.session.commit()
            print(f"✅ Added {len(sample_questions)} sample questions")
            details.append(f"Added {len(sample_questions)} sample questions")
        else:
            details.append("Sample questions already exist")
        
        print("🎉 Database initialization completed successfully!")
        
        return render_template_string(SETUP_TEMPLATE,
            status={
                'type': 'success',
                'title': '✅ Database Initialization Successful!',
                'message': 'Your database has been initialized successfully.',
                'details': details
            },
            db_url_set=bool(os.environ.get('DATABASE_URL')),
            jwt_secret_set=bool(os.environ.get('JWT_SECRET')),
            mongo_uri_set=bool(os.environ.get('MONGO_URI'))
        )
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Database initialization failed: {error_msg}")
        
        return render_template_string(SETUP_TEMPLATE,
            status={
                'type': 'error',
                'title': '❌ Database Initialization Failed',
                'message': f'Error: {error_msg}',
                'details': [
                    'Check your DATABASE_URL environment variable',
                    'Ensure your Neon database is accessible',
                    'Check the application logs for more details'
                ]
            },
            db_url_set=bool(os.environ.get('DATABASE_URL')),
            jwt_secret_set=bool(os.environ.get('JWT_SECRET')),
            mongo_uri_set=bool(os.environ.get('MONGO_URI'))
        ), 500

@setup_bp.route('/status', methods=['GET'])
def check_status():
    """Check database status via web interface"""
    try:
        status_info = {
            'database_accessible': True,
            'tables': {},
            'counts': {}
        }
        
        # Test each model/table
        try:
            status_info['counts']['users'] = User.query.count()
            status_info['tables']['users'] = True
        except Exception:
            status_info['tables']['users'] = False
        
        try:
            status_info['counts']['admins'] = Admin.query.count()
            status_info['tables']['admins'] = True
        except Exception:
            status_info['tables']['admins'] = False
        
        try:
            status_info['counts']['questions'] = QuizQuestion.query.count()
            status_info['tables']['questions'] = True
        except Exception:
            status_info['tables']['questions'] = False
            
        try:
            status_info['counts']['challenges'] = Challenge.query.count()
            status_info['tables']['challenges'] = True
        except Exception:
            status_info['tables']['challenges'] = False
        
        # Determine status
        all_tables_exist = all(status_info['tables'].values())
        admin_exists = status_info['counts'].get('admins', 0) > 0
        questions_exist = status_info['counts'].get('questions', 0) > 0
        
        if all_tables_exist and admin_exists and questions_exist:
            status_type = 'success'
            status_title = '✅ Database is Ready!'
            status_message = 'All tables exist, admin user created, and sample questions loaded.'
        elif all_tables_exist and admin_exists:
            status_type = 'warning'
            status_title = '⚠️ Database Partially Ready'
            status_message = 'Tables and admin exist, but no sample questions found.'
        elif all_tables_exist:
            status_type = 'warning'
            status_title = '⚠️ Database Tables Exist'
            status_message = 'Tables exist but admin user and questions are missing.'
        else:
            status_type = 'error'
            status_title = '❌ Database Not Initialized'
            status_message = 'Database tables are missing or inaccessible.'
        
        details = [f"{k}: {v}" for k, v in status_info['counts'].items()]
        
        return render_template_string(SETUP_TEMPLATE,
            status={
                'type': status_type,
                'title': status_title,
                'message': status_message,
                'details': details
            },
            db_url_set=bool(os.environ.get('DATABASE_URL')),
            jwt_secret_set=bool(os.environ.get('JWT_SECRET')),
            mongo_uri_set=bool(os.environ.get('MONGO_URI'))
        )
        
    except Exception as e:
        return render_template_string(SETUP_TEMPLATE,
            status={
                'type': 'error',
                'title': '❌ Database Check Failed',
                'message': f'Error: {str(e)}',
                'details': ['Database may be inaccessible', 'Check your DATABASE_URL configuration']
            },
            db_url_set=bool(os.environ.get('DATABASE_URL')),
            jwt_secret_set=bool(os.environ.get('JWT_SECRET')),
            mongo_uri_set=bool(os.environ.get('MONGO_URI'))
        ), 500