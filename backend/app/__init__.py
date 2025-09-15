from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from pymongo import MongoClient
import os
from datetime import timedelta, datetime

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address)
mongo_client = None

def create_app():
    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables
    
    app = Flask(__name__)
    
    # Configuration - use environment variables for production
    app.config['SECRET_KEY'] = os.environ.get('JWT_SECRET', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://quizbattle:password@localhost:5432/quizbattle')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET', 'jwt-secret-string')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    
    # MongoDB configuration
    mongodb_url = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
    mongodb_db = os.environ.get('MONGODB_DB', 'quizbattle_logs')
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    # Enable CORS for frontend - allow all origins for now, restrict in production
    CORS(app, origins=["*"], supports_credentials=True)
    limiter.init_app(app)
    
    # Initialize MongoDB
    global mongo_client
    mongo_client = MongoClient(mongodb_url)
    app.mongo_db = mongo_client[mongodb_db]
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.users import users_bp
    from app.routes.quizzes import quizzes_bp
    from app.routes.challenges import challenges_bp
    from app.routes.admin import admin_bp
    from app.routes.leaderboard import leaderboard_bp
    from app.routes.debug import debug_bp
    from app.routes.setup import setup_bp
    from app.routes.dbtest import dbtest_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(quizzes_bp, url_prefix='/api/quizzes')
    app.register_blueprint(challenges_bp, url_prefix='/api/challenges')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(leaderboard_bp, url_prefix='/api/leaderboard')
    app.register_blueprint(debug_bp, url_prefix='/api/debug')
    app.register_blueprint(setup_bp, url_prefix='/api/setup')
    app.register_blueprint(dbtest_bp, url_prefix='/api/dbtest')
    
    # Root endpoint
    @app.route('/', methods=['GET'])
    def root():
        return jsonify({
            'name': 'QuizBattle API',
            'version': '1.0.0',
            'status': 'running',
            'endpoints': {
                'health': '/health',
                'auth': '/api/auth',
                'admin': '/api/admin',
                'challenges': '/api/challenges'
            }
        }), 200
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0'
        }), 200
    
    # Auto-initialize database on first startup
    # with app.app_context():
    #     try:
    #         # Check if tables exist by trying to query Admin table
    #         from app.models import Admin, User, QuizQuestion, Challenge
    #         Admin.query.first()
    #         print("✅ Database tables already exist")
    #     except Exception as e:
    #         print("🗄️ Database tables not found, initializing...")
    #         try:
    #             # Create all tables
    #             db.create_all()
    #             print("✅ Database tables created successfully")
                
    #             # Create admin user if it doesn't exist
    #             admin = Admin.query.filter_by(username='admin').first()
    #             if not admin:
    #                 admin = Admin(username='admin')
    #                 admin.set_password('admin123')
    #                 db.session.add(admin)
    #                 db.session.commit()
    #                 print("✅ Admin user created: admin/admin123")
                
    #             # Add sample questions if none exist
    #             if QuizQuestion.query.count() == 0:
    #                 sample_questions = [
    #                     QuizQuestion(
    #                         text="What is the capital of India?",
    #                         options=["Mumbai", "Delhi", "Kolkata", "Chennai"],
    #                         answer=1,
    #                         difficulty="easy",
    #                         exam_type="General"
    #                     ),
    #                     QuizQuestion(
    #                         text="What is 2+2?",
    #                         options=["3", "4", "5", "6"],
    #                         answer=1,
    #                         difficulty="easy",
    #                         exam_type="Math"
    #                     )
    #                 ]
    #                 for q in sample_questions:
    #                     db.session.add(q)
    #                 db.session.commit()
    #                 print(f"✅ Added {len(sample_questions)} sample questions")
                
    #             print("🎉 Database initialization completed successfully!")
    #         except Exception as init_error:
    #             print(f"❌ Database initialization failed: {str(init_error)}")
    
    # Rate limit error handler
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({
            'error': 'Rate limit exceeded',
            'message': 'Too many requests. Please try again later.'
        }), 429
    
    return app
