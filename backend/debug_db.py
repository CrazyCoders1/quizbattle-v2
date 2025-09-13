#!/usr/bin/env python3
"""
Debug script to check database contents and admin API issues
"""
import os
import sys

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app import create_app, db
from app.models import User, QuizQuestion, Challenge, QuizResult, Admin

def debug_database():
    app = create_app()
    
    with app.app_context():
        print("=== DATABASE DEBUG INFO ===")
        
        # Check Users
        users = User.query.all()
        print(f"\n🔍 USERS TABLE ({len(users)} records):")
        for user in users[:5]:  # Show first 5
            print(f"  ID: {user.id}, Username: {user.username}, Email: {user.email}")
        
        # Check Admins
        admins = Admin.query.all()
        print(f"\n🔍 ADMINS TABLE ({len(admins)} records):")
        for admin in admins[:5]:
            print(f"  ID: {admin.id}, Username: {admin.username}")
        
        # Check Questions
        questions = QuizQuestion.query.all()
        print(f"\n🔍 QUIZ_QUESTIONS TABLE ({len(questions)} records):")
        for question in questions[:3]:  # Show first 3
            print(f"  ID: {question.id}, Text: {question.text[:50]}..., Difficulty: {question.difficulty}")
        
        # Check Challenges
        challenges = Challenge.query.all()
        print(f"\n🔍 CHALLENGES TABLE ({len(challenges)} records):")
        for challenge in challenges[:3]:
            print(f"  ID: {challenge.id}, Name: {challenge.name}, Code: {challenge.code}")
        
        # Check Quiz Results
        results = QuizResult.query.all()
        print(f"\n🔍 QUIZ_RESULTS TABLE ({len(results)} records):")
        for result in results[:3]:
            print(f"  ID: {result.id}, User: {result.user_id}, Challenge: {result.challenge_id}, Score: {result.score}")
        
        # Check for duplicates in quiz_result
        duplicate_check = db.session.execute("""
            SELECT user_id, challenge_id, COUNT(*) as count 
            FROM quiz_result 
            GROUP BY user_id, challenge_id 
            HAVING COUNT(*) > 1
        """).fetchall()
        
        print(f"\n🔍 DUPLICATE CHECK:")
        if duplicate_check:
            print("  ❌ Found duplicates:")
            for dup in duplicate_check:
                print(f"    User {dup[0]}, Challenge {dup[1]}: {dup[2]} records")
        else:
            print("  ✅ No duplicates found")
        
        # Test admin endpoints logic
        print(f"\n🔍 ADMIN API SIMULATION:")
        print(f"  get_users() would return: {len(users)} users")
        print(f"  get_questions() would return: {len(questions)} questions")
        
        return {
            'users_count': len(users),
            'admins_count': len(admins), 
            'questions_count': len(questions),
            'challenges_count': len(challenges),
            'results_count': len(results)
        }

if __name__ == '__main__':
    try:
        stats = debug_database()
        print(f"\n✅ Database connection successful!")
        print(f"📊 Summary: {stats}")
    except Exception as e:
        print(f"❌ Database error: {e}")
        import traceback
        traceback.print_exc()