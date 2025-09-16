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
    
    # Handle DATABASE_URL for psycopg2 compatibility
    database_url = os.environ.get('DATABASE_URL', 'postgresql://quizbattle:password@localhost:5432/quizbattle')
    # Ensure postgres:// URLs are converted to postgresql:// for psycopg2
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # Optimize connection pool for production
    is_production = 'render.com' in os.environ.get('DATABASE_URL', '') or os.environ.get('FLASK_ENV') == 'production'
    
    # Configure engine options based on database type
    is_sqlite = database_url.startswith('sqlite://')
    
    engine_options = {
        'pool_pre_ping': True,  # Verify connections before use
        'pool_recycle': 300,    # Recycle connections every 5 minutes
        'pool_size': 10 if is_production else 5,  # Connection pool size
        'max_overflow': 20 if is_production else 10,  # Max overflow connections
        'pool_timeout': 30,     # Timeout when getting connection from pool
    }
    
    # Only add SSL for PostgreSQL, not SQLite
    if not is_sqlite and 'localhost' not in database_url:
        engine_options['connect_args'] = {"sslmode": "require"}
    
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = engine_options
    
    print(f"🔧 Database pool configured: size={engine_options['pool_size']}, overflow={engine_options['max_overflow']}")
    
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET', 'jwt-secret-string')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    
    # MongoDB/Redis configuration for logging
    mongodb_url = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
    redis_url = os.environ.get('REDIS_URL', None)
    mongodb_db = os.environ.get('MONGODB_DB', 'quizbattle_logs')
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    # Enable CORS for frontend - allow all origins for now, restrict in production
    CORS(app, origins=["*"], supports_credentials=True)
    limiter.init_app(app)
    
    # Initialize MongoDB or Redis for logging
    global mongo_client
    try:
        if redis_url and redis_url.startswith('redis://'):
            # Use Redis for logging instead of MongoDB on free tier
            import redis
            redis_client = redis.from_url(redis_url)
            app.mongo_db = redis_client  # Use Redis client as logging backend
            print("✅ Connected to Redis for logging")
        else:
            # Use MongoDB for logging
            mongo_client = MongoClient(mongodb_url)
            app.mongo_db = mongo_client[mongodb_db]
            print("✅ Connected to MongoDB for logging")
    except Exception as e:
        print(f"⚠️  Warning: Could not connect to logging backend: {str(e)}")
        app.mongo_db = None  # Graceful degradation
    
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
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'database': 'unknown',
            'logging': 'unknown'
        }
        
        # Check database connectivity
        try:
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
            health_status['database'] = 'connected'
        except Exception as e:
            health_status['database'] = f'error: {str(e)[:100]}'
            health_status['status'] = 'degraded'
        
        # Check logging backend
        try:
            if hasattr(app, 'mongo_db') and app.mongo_db:
                health_status['logging'] = 'connected'
            else:
                health_status['logging'] = 'disabled'
        except:
            health_status['logging'] = 'error'
            
        status_code = 200 if health_status['status'] == 'healthy' else 503
        return jsonify(health_status), status_code
    
    # Database monitoring endpoint for admins
    @app.route('/api/debug/db-status', methods=['GET'])
    def db_status():
        from app.utils.db_utils import get_db_stats, ensure_db_connection
        
        db_stats = {
            'connection_alive': ensure_db_connection(),
            'pool_stats': get_db_stats(),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        try:
            # Get table counts
            from app.models import User, Admin, QuizQuestion, Challenge, QuizResult, Leaderboard
            db_stats['table_counts'] = {
                'users': User.query.count(),
                'admins': Admin.query.count(),
                'questions': QuizQuestion.query.count(),
                'challenges': Challenge.query.count(),
                'quiz_results': QuizResult.query.count(),
                'leaderboard': Leaderboard.query.count()
            }
        except Exception as e:
            db_stats['table_counts'] = {'error': str(e)}
        
        return jsonify(db_stats), 200
    
    # Auto-initialize database with production-safe sample data
    with app.app_context():
        try:
            # Import models first
            from app.models import User, Admin, QuizQuestion, Challenge, QuizResult, Leaderboard
            
            # Always ensure tables exist
            db.create_all()
            print("✅ Database tables created/verified successfully")
            
            # Check if basic data exists
            questions_count = QuizQuestion.query.count()
            admin_count = Admin.query.count()
            
            print(f"📊 Current database state: {questions_count} questions, {admin_count} admins")
            
            # Create admin user if it doesn't exist
            admin = Admin.query.filter_by(username='admin').first()
            if not admin:
                admin_password = os.environ.get('ADMIN_PASSWORD', 'admin987')
                admin = Admin(username='admin')
                try:
                    admin.set_password(admin_password)
                    db.session.add(admin)
                    db.session.commit()
                    print(f"✅ Admin user created: admin/{admin_password}")
                except Exception as e:
                    db.session.rollback()
                    print(f"⚠️ Admin creation failed: {e}")
                    # Use fallback password hash method
                    from werkzeug.security import generate_password_hash
                    admin.password_hash = generate_password_hash(admin_password, method='pbkdf2:sha256')
                    db.session.add(admin)
                    db.session.commit()
                    print(f"✅ Admin user created with fallback method: admin/{admin_password}")
            else:
                print("✅ Admin user already exists")
            
            # Add comprehensive sample questions if database has fewer than 20 questions
            if questions_count < 20:
                print("🎯 Adding comprehensive sample questions for all exam types...")
                sample_questions = [
                    # CBSE 11 - Easy Questions
                    QuizQuestion(
                        text="What is the SI unit of electric current?",
                        options=["Volt", "Ampere", "Ohm", "Watt"],
                        answer=1,
                        difficulty="easy",
                        exam_type="CBSE 11"
                    ),
                    QuizQuestion(
                        text="Which gas is most abundant in Earth's atmosphere?",
                        options=["Oxygen", "Carbon dioxide", "Nitrogen", "Argon"],
                        answer=2,
                        difficulty="easy",
                        exam_type="CBSE 11"
                    ),
                    QuizQuestion(
                        text="What is the chemical formula of water?",
                        options=["H2O", "CO2", "NaCl", "C6H12O6"],
                        answer=0,
                        difficulty="easy",
                        exam_type="CBSE 11"
                    ),
                    QuizQuestion(
                        text="What is the speed of light in vacuum?",
                        options=["3 × 10^8 m/s", "3 × 10^6 m/s", "9 × 10^8 m/s", "1 × 10^8 m/s"],
                        answer=0,
                        difficulty="easy",
                        exam_type="CBSE 11"
                    ),
                    QuizQuestion(
                        text="Which planet is known as the Red Planet?",
                        options=["Venus", "Jupiter", "Mars", "Saturn"],
                        answer=2,
                        difficulty="easy",
                        exam_type="CBSE 11"
                    ),
                    
                    # CBSE 11 - Medium Questions
                    QuizQuestion(
                        text="A body is moving with uniform velocity. What is its acceleration?",
                        options=["Zero", "Constant", "Increasing", "Decreasing"],
                        answer=0,
                        difficulty="medium",
                        exam_type="CBSE 11"
                    ),
                    QuizQuestion(
                        text="What type of chemical bond is formed between sodium and chlorine in NaCl?",
                        options=["Covalent bond", "Metallic bond", "Ionic bond", "Hydrogen bond"],
                        answer=2,
                        difficulty="medium",
                        exam_type="CBSE 11"
                    ),
                    QuizQuestion(
                        text="If sin θ = 3/5, what is cos θ?",
                        options=["4/5", "3/4", "5/4", "5/3"],
                        answer=0,
                        difficulty="medium",
                        exam_type="CBSE 11"
                    ),
                    
                    # CBSE 12 - Easy Questions
                    QuizQuestion(
                        text="What is the derivative of x²?",
                        options=["x", "2x", "x²", "2x²"],
                        answer=1,
                        difficulty="easy",
                        exam_type="CBSE 12"
                    ),
                    QuizQuestion(
                        text="Which of the following is a greenhouse gas?",
                        options=["Nitrogen", "Oxygen", "Carbon dioxide", "Helium"],
                        answer=2,
                        difficulty="easy",
                        exam_type="CBSE 12"
                    ),
                    
                    # JEE Main - Tough Questions
                    QuizQuestion(
                        text="A particle moves along x-axis such that its position is given by x = 2t³ - 3t² + 1. The acceleration at t = 2s is:",
                        options=["18 m/s²", "12 m/s²", "6 m/s²", "24 m/s²"],
                        answer=0,
                        difficulty="tough",
                        exam_type="JEE Main",
                        hint="Use the second derivative of position to find acceleration"
                    ),
                    QuizQuestion(
                        text="The number of unpaired electrons in Mn²⁺ ion is:",
                        options=["3", "4", "5", "6"],
                        answer=2,
                        difficulty="tough",
                        exam_type="JEE Main",
                        hint="Consider the electronic configuration of Mn and the effect of losing 2 electrons"
                    ),
                    QuizQuestion(
                        text="If the roots of equation ax² + bx + c = 0 are α and β, then α + β equals:",
                        options=["-b/a", "b/a", "-c/a", "c/a"],
                        answer=0,
                        difficulty="tough",
                        exam_type="JEE Main",
                        hint="Use Vieta's formulas for quadratic equations"
                    ),
                    
                    # JEE Advanced - Very Tough Questions
                    QuizQuestion(
                        text="A uniform magnetic field B exists in a cylindrical region. An electron enters the field perpendicularly. The radius of its circular path is:",
                        options=["mv/eB", "eB/mv", "mvB/e", "e/mvB"],
                        answer=0,
                        difficulty="tough",
                        exam_type="JEE Advanced",
                        hint="Apply the Lorentz force formula and centripetal force condition"
                    ),
                    
                    # General Knowledge - Easy
                    QuizQuestion(
                        text="What is the capital of France?",
                        options=["London", "Berlin", "Paris", "Madrid"],
                        answer=2,
                        difficulty="easy",
                        exam_type="General"
                    ),
                    QuizQuestion(
                        text="Who wrote 'Romeo and Juliet'?",
                        options=["Charles Dickens", "William Shakespeare", "Mark Twain", "Jane Austen"],
                        answer=1,
                        difficulty="easy",
                        exam_type="General"
                    ),
                    
                    # Math - Various Difficulties
                    QuizQuestion(
                        text="What is 15% of 200?",
                        options=["25", "30", "35", "40"],
                        answer=1,
                        difficulty="easy",
                        exam_type="Math"
                    ),
                    QuizQuestion(
                        text="If log₂(x) = 3, then x equals:",
                        options=["6", "8", "9", "12"],
                        answer=1,
                        difficulty="medium",
                        exam_type="Math"
                    ),
                    
                    # Science - Various Topics
                    QuizQuestion(
                        text="What is the atomic number of Carbon?",
                        options=["4", "6", "8", "12"],
                        answer=1,
                        difficulty="easy",
                        exam_type="Science"
                    ),
                    QuizQuestion(
                        text="Which organelle is known as the powerhouse of the cell?",
                        options=["Nucleus", "Ribosome", "Mitochondria", "Chloroplast"],
                        answer=2,
                        difficulty="easy",
                        exam_type="Science"
                    )
                ]
                
                # Add questions in batches for better performance
                batch_size = 5
                for i in range(0, len(sample_questions), batch_size):
                    batch = sample_questions[i:i + batch_size]
                    for q in batch:
                        db.session.add(q)
                    try:
                        db.session.commit()
                        print(f"✅ Added questions batch {i//batch_size + 1}/{(len(sample_questions)-1)//batch_size + 1}")
                    except Exception as e:
                        db.session.rollback()
                        print(f"❌ Failed to add batch {i//batch_size + 1}: {e}")
                
                final_count = QuizQuestion.query.count()
                print(f"🎉 Database initialization completed! Total questions: {final_count}")
            else:
                print(f"✅ Database already contains {questions_count} questions")
                
        except Exception as init_error:
            print(f"❌ Database initialization failed: {str(init_error)}")
            import traceback
            traceback.print_exc()
    
    # Rate limit error handler
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({
            'error': 'Rate limit exceeded',
            'message': 'Too many requests. Please try again later.'
        }), 429
    
    return app
