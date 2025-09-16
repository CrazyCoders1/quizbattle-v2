#!/usr/bin/env python3
"""
Production Database Seeding Script
Run this to populate the production database with sample data
"""
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Set environment variables
os.environ.setdefault('FLASK_APP', 'app.py')

from app import create_app, db
from app.models import User, Admin, QuizQuestion, Challenge, QuizResult, Leaderboard

def seed_database():
    """Seed production database with comprehensive data"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🌱 Starting production database seeding...")
            
            # Ensure all tables exist
            db.create_all()
            print("✅ Database tables verified")
            
            # Check current state
            questions_count = QuizQuestion.query.count()
            users_count = User.query.count()
            admin_count = Admin.query.count()
            
            print(f"📊 Current state: {questions_count} questions, {users_count} users, {admin_count} admins")
            
            # Seed sample users if none exist
            if users_count == 0:
                sample_users = [
                    {"username": "student1", "email": "student1@example.com", "password": "password123"},
                    {"username": "student2", "email": "student2@example.com", "password": "password123"},
                    {"username": "testuser", "email": "test@example.com", "password": "testpass"},
                    {"username": "demo", "email": "demo@example.com", "password": "demopass"}
                ]
                
                for user_data in sample_users:
                    user = User(username=user_data["username"], email=user_data["email"])
                    user.set_password(user_data["password"])
                    db.session.add(user)
                
                db.session.commit()
                print(f"✅ Created {len(sample_users)} sample users")
            
            # Create more comprehensive questions if needed
            if questions_count < 20:
                additional_questions = [
                    # Physics Questions
                    QuizQuestion(
                        text="Newton's first law of motion is also known as:",
                        options=["Law of inertia", "Law of acceleration", "Law of action-reaction", "Law of gravitation"],
                        answer=0,
                        difficulty="easy",
                        exam_type="CBSE 11"
                    ),
                    QuizQuestion(
                        text="The dimensional formula for force is:",
                        options=["[MLT⁻²]", "[MLT⁻¹]", "[ML²T⁻²]", "[MT⁻²]"],
                        answer=0,
                        difficulty="medium",
                        exam_type="CBSE 12"
                    ),
                    QuizQuestion(
                        text="In SHM, the acceleration is directly proportional to:",
                        options=["Velocity", "Displacement", "Time period", "Amplitude"],
                        answer=1,
                        difficulty="medium",
                        exam_type="JEE Main"
                    ),
                    
                    # Chemistry Questions
                    QuizQuestion(
                        text="The electronic configuration of Chlorine is:",
                        options=["2,8,7", "2,8,8", "2,8,6", "2,7,8"],
                        answer=0,
                        difficulty="easy",
                        exam_type="CBSE 11"
                    ),
                    QuizQuestion(
                        text="Which of the following is an aldehyde?",
                        options=["CH₃COOH", "CH₃CHO", "CH₃COCH₃", "C₂H₅OH"],
                        answer=1,
                        difficulty="medium",
                        exam_type="CBSE 12"
                    ),
                    
                    # Mathematics Questions
                    QuizQuestion(
                        text="The value of cos(90°) is:",
                        options=["0", "1", "-1", "√3/2"],
                        answer=0,
                        difficulty="easy",
                        exam_type="CBSE 11"
                    ),
                    QuizQuestion(
                        text="∫x dx equals:",
                        options=["x²/2 + C", "x² + C", "2x + C", "x/2 + C"],
                        answer=0,
                        difficulty="easy",
                        exam_type="CBSE 12"
                    ),
                    
                    # Biology Questions
                    QuizQuestion(
                        text="DNA replication occurs during which phase?",
                        options=["G1 phase", "S phase", "G2 phase", "M phase"],
                        answer=1,
                        difficulty="medium",
                        exam_type="CBSE 12"
                    ),
                    QuizQuestion(
                        text="The basic unit of life is:",
                        options=["Tissue", "Organ", "Cell", "Organism"],
                        answer=2,
                        difficulty="easy",
                        exam_type="CBSE 11"
                    ),
                    
                    # Advanced JEE Questions
                    QuizQuestion(
                        text="For a particle in SHM, if displacement is x = A sin(ωt), the velocity is:",
                        options=["Aω cos(ωt)", "-Aω cos(ωt)", "Aω sin(ωt)", "-Aω sin(ωt)"],
                        answer=0,
                        difficulty="tough",
                        exam_type="JEE Advanced",
                        hint="Differentiate displacement with respect to time"
                    ),
                    
                    # More Varied Questions
                    QuizQuestion(
                        text="Which programming language is known as the 'mother of all languages'?",
                        options=["Assembly", "C", "FORTRAN", "COBOL"],
                        answer=1,
                        difficulty="medium",
                        exam_type="General"
                    ),
                    QuizQuestion(
                        text="The square root of 144 is:",
                        options=["11", "12", "13", "14"],
                        answer=1,
                        difficulty="easy",
                        exam_type="Math"
                    ),
                    QuizQuestion(
                        text="Photosynthesis occurs in which part of the plant cell?",
                        options=["Mitochondria", "Nucleus", "Chloroplast", "Ribosome"],
                        answer=2,
                        difficulty="easy",
                        exam_type="Science"
                    )
                ]
                
                for question in additional_questions:
                    db.session.add(question)
                
                db.session.commit()
                final_questions = QuizQuestion.query.count()
                print(f"✅ Added {len(additional_questions)} additional questions. Total: {final_questions}")
            
            # Create sample challenges if users exist
            users = User.query.all()
            challenges_count = Challenge.query.count()
            
            if users and challenges_count == 0:
                sample_challenges = [
                    Challenge(
                        name="CBSE Class 11 Physics Challenge",
                        exam_type="CBSE 11",
                        difficulty="easy",
                        question_count=5,
                        time_limit=10,
                        created_by=users[0].id
                    ),
                    Challenge(
                        name="JEE Main Practice Test",
                        exam_type="JEE Main", 
                        difficulty="tough",
                        question_count=10,
                        time_limit=20,
                        created_by=users[0].id if len(users) > 0 else 1
                    ),
                    Challenge(
                        name="Quick General Knowledge",
                        exam_type="General",
                        difficulty="easy", 
                        question_count=8,
                        time_limit=8,
                        created_by=users[1].id if len(users) > 1 else 1
                    )
                ]
                
                for challenge in sample_challenges:
                    db.session.add(challenge)
                
                db.session.commit()
                print(f"✅ Created {len(sample_challenges)} sample challenges")
            
            # Final summary
            final_questions = QuizQuestion.query.count()
            final_users = User.query.count()
            final_challenges = Challenge.query.count()
            final_admins = Admin.query.count()
            
            print("\n🎉 Database seeding completed successfully!")
            print(f"📊 Final state:")
            print(f"   👥 Users: {final_users}")
            print(f"   🔑 Admins: {final_admins}")
            print(f"   ❓ Questions: {final_questions}")
            print(f"   🏆 Challenges: {final_challenges}")
            
            return True
            
        except Exception as e:
            print(f"❌ Database seeding failed: {str(e)}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = seed_database()
    sys.exit(0 if success else 1)