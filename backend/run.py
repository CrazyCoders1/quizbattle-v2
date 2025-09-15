import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from app import create_app, db

# Load environment variables from .env file for local development
# In production, Render will provide these via environment
if os.path.exists('.env'):
    load_dotenv()

# Create the Flask app instance
app = create_app()

# Import models after app creation to avoid circular imports
try:
    from app.models import User, QuizQuestion, Challenge, QuizResult, Leaderboard, Admin
except ImportError as e:
    print(f"⚠️  Warning: Could not import models: {e}")
    User = QuizQuestion = Challenge = QuizResult = Leaderboard = Admin = None

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'QuizQuestion': QuizQuestion,
        'Challenge': Challenge,
        'QuizResult': QuizResult,
        'Leaderboard': Leaderboard,
        'Admin': Admin
    }

@app.cli.command()
def init_db():
    """Initialize the database with sample data"""
    db.create_all()
    
    # Create default admin user
    admin = Admin.query.filter_by(username='admin').first()
    if not admin:
        admin = Admin(username='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Default admin created: username=admin, password=admin123")
    
    # Create sample questions
    if QuizQuestion.query.count() == 0:
        sample_questions = [
            QuizQuestion(
                text="What is the capital of India?",
                options=["Mumbai", "Delhi", "Kolkata", "Chennai"],
                answer=1,
                difficulty="easy",
                exam_type="CBSE 11"
            ),
            QuizQuestion(
                text="Which is the largest planet in our solar system?",
                options=["Earth", "Jupiter", "Saturn", "Neptune"],
                answer=1,
                difficulty="easy",
                exam_type="CBSE 11"
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
                exam_type="CBSE 12"
            ),
            QuizQuestion(
                text="What is the speed of light in vacuum?",
                options=["3 × 10⁸ m/s", "3 × 10⁶ m/s", "3 × 10¹⁰ m/s", "3 × 10⁴ m/s"],
                answer=0,
                difficulty="tough",
                exam_type="JEE Advanced"
            )
        ]
        
        for question in sample_questions:
            db.session.add(question)
        
        db.session.commit()
        print("Sample questions created")

if __name__ == '__main__':
    # Get port from environment (Render provides PORT variable)
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'production') != 'production'
    
    print(f"🚀 Starting QuizBattle server on port {port}")
    print(f"🔧 Debug mode: {debug}")
    
    app.run(debug=debug, host='0.0.0.0', port=port)
