from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import QuizQuestion

quizzes_bp = Blueprint('quizzes', __name__)

@quizzes_bp.route('/questions', methods=['GET'])
@jwt_required()
def get_questions():
    exam_type = request.args.get('exam_type')
    difficulty = request.args.get('difficulty')
    
    query = QuizQuestion.query
    if exam_type:
        query = query.filter_by(exam_type=exam_type)
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    
    questions = query.all()
    return jsonify({'questions': [q.to_dict() for q in questions]}), 200

@quizzes_bp.route('/practice/submit', methods=['POST'])
@jwt_required()
def submit_practice():
    from app.models import QuizResult, Leaderboard
    from datetime import datetime
    import random
    
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    if isinstance(current_user_id, str) and current_user_id.startswith('admin_'):
        return jsonify({'error': 'Admins cannot submit practice results'}), 403
    
    # Create a practice result entry
    result = QuizResult(
        user_id=int(current_user_id),
        challenge_id=None,  # Practice mode, no specific challenge
        score=data.get('score', 0),
        total_questions=data.get('total', 0),
        correct_answers=data.get('correct_answers', 0),
        wrong_answers=data.get('wrong_answers', 0),
        time_taken=data.get('time_taken', 0)
    )
    
    db.session.add(result)
    
    # Update leaderboard for current month
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    leaderboard_entry = Leaderboard.query.filter_by(
        user_id=int(current_user_id),
        month=current_month,
        year=current_year
    ).first()
    
    if leaderboard_entry:
        leaderboard_entry.total_score += data.get('score', 0)
        leaderboard_entry.challenges_completed += 1
        leaderboard_entry.last_updated = datetime.utcnow()
    else:
        leaderboard_entry = Leaderboard(
            user_id=int(current_user_id),
            month=current_month,
            year=current_year,
            total_score=data.get('score', 0),
            challenges_completed=1
        )
        db.session.add(leaderboard_entry)
    
    db.session.commit()
    
    return jsonify({'message': 'Practice results submitted successfully'}), 200
