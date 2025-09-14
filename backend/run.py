import os
from dotenv import load_dotenv
from app import create_app, db
from app.models import User, QuizQuestion, Challenge, QuizResult, Leaderboard, Admin

# Load environment variables from .env file for local development
load_dotenv()

app = create_app()

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
    app.run(debug=True, host='0.0.0.0', port=5000)
