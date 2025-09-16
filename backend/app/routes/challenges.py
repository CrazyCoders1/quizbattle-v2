from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Challenge, QuizQuestion, QuizResult, User
from datetime import datetime
import random
import logging

challenges_bp = Blueprint('challenges', __name__)

@challenges_bp.route('/create', methods=['POST'])
@jwt_required()
def create_challenge():
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    current_app.logger.info(f"🏆 Challenge creation attempt by user: {current_user_id}")
    current_app.logger.info(f"📝 Challenge data: {data}")
    
    if isinstance(current_user_id, str) and current_user_id.startswith('admin_'):
        current_app.logger.warning(f"❌ Admin {current_user_id} attempted to create challenge")
        return jsonify({'error': 'Admins cannot create challenges'}), 403
    
    try:
        # Check for duplicate challenge name by the same user
        challenge_name = data.get('name', '').strip()
        if not challenge_name:
            return jsonify({'error': 'Challenge name is required'}), 400
            
        existing_challenge = Challenge.query.filter_by(
            name=challenge_name,
            created_by=int(current_user_id),
            is_active=True
        ).first()
        
        if existing_challenge:
            current_app.logger.warning(f"🚫 Duplicate challenge name '{challenge_name}' by user {current_user_id}")
            return jsonify({
                'error': f'You already have an active challenge named "{challenge_name}". Please choose a different name.'
            }), 409
        
        challenge = Challenge(
            name=challenge_name,
            exam_type=data.get('exam_type'),
            difficulty=data.get('difficulty'),
            question_count=data.get('question_count', 10),
            time_limit=data.get('time_limit', 30),
            created_by=int(current_user_id)
        )
        
        db.session.add(challenge)
        db.session.commit()
        
        current_app.logger.info(f"✅ Challenge created successfully: ID={challenge.id}, Code={challenge.code}")
        return jsonify({'challenge': challenge.to_dict()}), 201
        
    except Exception as e:
        current_app.logger.error(f"❌ Challenge creation failed: {str(e)}")
        db.session.rollback()
        return jsonify({'error': f'Failed to create challenge: {str(e)}'}), 500

@challenges_bp.route('/active', methods=['GET'])
@jwt_required()
def get_active_challenges():
    current_user_id = get_jwt_identity()
    
    current_app.logger.info(f"📋 Active challenges request from user: {current_user_id}")
    
    # Skip admin users
    if isinstance(current_user_id, str) and current_user_id.startswith('admin_'):
        challenges = Challenge.query.filter_by(is_active=True).all()
        current_app.logger.info(f"👑 Admin user: returning {len(challenges)} active challenges")
        return jsonify({'challenges': [c.to_dict() for c in challenges]}), 200
    
    # Get all active challenges first
    all_active_challenges = Challenge.query.filter_by(is_active=True).all()
    current_app.logger.info(f"🏆 Found {len(all_active_challenges)} total active challenges")
    
    # Get challenges user hasn't completed
    completed_challenge_ids = db.session.query(QuizResult.challenge_id).filter_by(
        user_id=int(current_user_id)
    ).subquery()
    
    completed_ids = [row[0] for row in db.session.query(QuizResult.challenge_id).filter_by(
        user_id=int(current_user_id)
    ).all()]
    
    current_app.logger.info(f"✅ User {current_user_id} has completed challenges: {completed_ids}")
    
    active_challenges = Challenge.query.filter(
        Challenge.is_active == True,
        ~Challenge.id.in_(completed_challenge_ids)
    ).all()
    
    # Log details about filtered challenges
    user_created_challenges = [c for c in all_active_challenges if c.created_by == int(current_user_id)]
    current_app.logger.info(f"👤 User {current_user_id} has created {len(user_created_challenges)} challenges")
    
    for challenge in user_created_challenges:
        in_active_list = challenge in active_challenges
        current_app.logger.info(f"   Challenge '{challenge.name}' (ID={challenge.id}) - In active list: {in_active_list}")
    
    current_app.logger.info(f"📤 Returning {len(active_challenges)} active challenges to user {current_user_id}")
    return jsonify({'challenges': [c.to_dict() for c in active_challenges]}), 200

@challenges_bp.route('/join/<code>', methods=['POST'])
@jwt_required()
def join_challenge(code):
    challenge = Challenge.query.filter_by(code=code.upper(), is_active=True).first()
    if not challenge:
        return jsonify({'error': 'Challenge not found or inactive'}), 404
    
    return jsonify({'challenge': challenge.to_dict(), 'message': 'Successfully joined challenge'}), 200

@challenges_bp.route('/<int:challenge_id>/play', methods=['GET'])
@jwt_required()
def get_challenge_questions(challenge_id):
    current_user_id = get_jwt_identity()
    current_app.logger.info(f"🎮 Challenge play request: Challenge={challenge_id}, User={current_user_id}")
    
    challenge = Challenge.query.get_or_404(challenge_id)
    current_app.logger.info(f"✅ Challenge found: {challenge.name} (exam_type={challenge.exam_type}, difficulty={challenge.difficulty}, question_count={challenge.question_count})")
    
    # Get questions based on challenge criteria
    questions = QuizQuestion.query.filter_by(
        exam_type=challenge.exam_type,
        difficulty=challenge.difficulty
    ).all()
    
    current_app.logger.info(f"📊 Found {len(questions)} questions for exam_type={challenge.exam_type}, difficulty={challenge.difficulty}")
    
    if not questions:
        current_app.logger.warning(f"❌ No questions found for challenge criteria!")
        # Try to find any questions with this exam_type
        fallback_questions = QuizQuestion.query.filter_by(exam_type=challenge.exam_type).all()
        current_app.logger.info(f"🔄 Fallback: Found {len(fallback_questions)} questions for exam_type={challenge.exam_type} (any difficulty)")
        
        if fallback_questions:
            questions = fallback_questions
            current_app.logger.info(f"✅ Using fallback questions")
        else:
            # Last resort: get any questions
            any_questions = QuizQuestion.query.limit(10).all()
            current_app.logger.info(f"🆘 Last resort: Using {len(any_questions)} random questions")
            questions = any_questions
    
    # Shuffle and take required number
    import random
    random.shuffle(questions)
    selected_questions = questions[:challenge.question_count]
    
    current_app.logger.info(f"🎯 Returning {len(selected_questions)} questions for challenge play")
    
    return jsonify({
        'questions': [q.to_dict() for q in selected_questions], 
        'challenge': challenge.to_dict()
    }), 200

@challenges_bp.route('/<int:challenge_id>/submit', methods=['POST'])
@jwt_required()
def submit_challenge(challenge_id):
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    current_app.logger.info(f"📝 Challenge submission attempt: User={current_user_id}, Challenge={challenge_id}")
    current_app.logger.info(f"📊 Submission data: {len(data.get('answers', {}))} answers, time_taken={data.get('time_taken', 0)}")
    
    if isinstance(current_user_id, str) and current_user_id.startswith('admin_'):
        current_app.logger.warning(f"❌ Admin {current_user_id} attempted to submit challenge")
        return jsonify({'error': 'Admins cannot submit challenges'}), 403
    
    try:
        challenge = Challenge.query.get_or_404(challenge_id)
        current_app.logger.info(f"✅ Challenge found: {challenge.name} (ID={challenge_id})")
        
        answers = data.get('answers', {})
    
        # Calculate score
        questions = QuizQuestion.query.filter_by(
            exam_type=challenge.exam_type,
            difficulty=challenge.difficulty
        ).limit(challenge.question_count).all()
        
        current_app.logger.info(f"🧮 Found {len(questions)} questions for exam_type={challenge.exam_type}, difficulty={challenge.difficulty}")
        
        correct_answers = 0
        wrong_answers = 0
        unanswered = 0
        
        for question in questions:
            user_answer = answers.get(str(question.id))
            if user_answer is not None:
                if user_answer == question.answer:
                    correct_answers += 1
                    current_app.logger.debug(f"✅ Q{question.id}: Correct (user={user_answer}, correct={question.answer})")
                else:
                    wrong_answers += 1
                    current_app.logger.debug(f"❌ Q{question.id}: Wrong (user={user_answer}, correct={question.answer})")
            else:
                unanswered += 1
                current_app.logger.debug(f"⚪ Q{question.id}: Unanswered")
        
        score = max(0, (correct_answers * 4) - (wrong_answers * 1))
        time_taken = data.get('time_taken', 0)
        
        current_app.logger.info(f"📊 Score calculation: Correct={correct_answers}, Wrong={wrong_answers}, Unanswered={unanswered}, Score={score}")
    
        # Check for existing result
        existing_result = QuizResult.query.filter_by(
            user_id=int(current_user_id),
            challenge_id=challenge_id
        ).first()
        
        if existing_result:
            current_app.logger.info(f"🔄 Updating existing result: Old score={existing_result.score}, New score={score}")
            # Update existing result
            existing_result.score = score
            existing_result.total_questions = len(questions)
            existing_result.correct_answers = correct_answers
            existing_result.wrong_answers = wrong_answers
            existing_result.time_taken = time_taken
            existing_result.submitted_at = datetime.utcnow()
            result = existing_result
            message = 'Challenge updated successfully - your latest attempt has been recorded'
        else:
            current_app.logger.info(f"✨ Creating new quiz result for user {current_user_id}")
            # Create new result
            result = QuizResult(
                user_id=int(current_user_id),
                challenge_id=challenge_id,
                score=score,
                total_questions=len(questions),
                correct_answers=correct_answers,
                wrong_answers=wrong_answers,
                time_taken=time_taken
            )
            db.session.add(result)
            message = 'Challenge submitted successfully'
        
        # Commit the result first
        db.session.commit()
        current_app.logger.info(f"💾 Quiz result saved to database: Result ID={result.id}")
        
        # Update leaderboard data (force refresh for this user)
        try:
            update_user_leaderboard_stats(int(current_user_id))
            current_app.logger.info(f"🏆 Leaderboard stats updated for user {current_user_id}")
        except Exception as e:
            current_app.logger.error(f"⚠️ Failed to update leaderboard: {str(e)}")
        
        return jsonify({
            'result': result.to_dict(),
            'message': message
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"❌ Challenge submission failed: {str(e)}")
        db.session.rollback()
        return jsonify({'error': f'Failed to submit challenge: {str(e)}'}), 500

@challenges_bp.route('/<int:challenge_id>/results', methods=['GET'])
@jwt_required()
def get_challenge_results(challenge_id):
    results = QuizResult.query.filter_by(challenge_id=challenge_id).order_by(QuizResult.score.desc()).all()
    return jsonify({'results': [r.to_dict() for r in results]}), 200

@challenges_bp.route('/completed', methods=['GET'])
@jwt_required()
def get_completed_challenges():
    current_user_id = get_jwt_identity()
    
    if isinstance(current_user_id, str) and current_user_id.startswith('admin_'):
        return jsonify({'error': 'Admins cannot view completed challenges'}), 403
    
    # Get challenges user has completed with their results
    completed = db.session.query(
        Challenge,
        QuizResult
    ).join(QuizResult).filter(
        QuizResult.user_id == int(current_user_id)
    ).order_by(QuizResult.submitted_at.desc()).all()
    
    completed_challenges = []
    for challenge, result in completed:
        challenge_dict = challenge.to_dict()
        challenge_dict['result'] = result.to_dict()
        completed_challenges.append(challenge_dict)
    
    return jsonify({'challenges': completed_challenges}), 200


def update_user_leaderboard_stats(user_id):
    """Update leaderboard stats for a specific user after challenge completion"""
    from app.models import Leaderboard
    from sqlalchemy import func
    
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    # Calculate user's monthly stats
    monthly_results = QuizResult.query.filter(
        QuizResult.user_id == user_id,
        func.extract('month', QuizResult.submitted_at) == current_month,
        func.extract('year', QuizResult.submitted_at) == current_year
    ).all()
    
    total_score = sum(result.score for result in monthly_results)
    challenges_completed = len(monthly_results)
    
    current_app.logger.info(f"📊 User {user_id} monthly stats: Score={total_score}, Completed={challenges_completed}")
    
    # Update or create leaderboard entry
    leaderboard_entry = Leaderboard.query.filter_by(
        user_id=user_id,
        month=current_month,
        year=current_year
    ).first()
    
    if leaderboard_entry:
        leaderboard_entry.total_score = total_score
        leaderboard_entry.challenges_completed = challenges_completed
        leaderboard_entry.last_updated = datetime.utcnow()
        current_app.logger.info(f"🔄 Updated leaderboard entry for user {user_id}")
    else:
        leaderboard_entry = Leaderboard(
            user_id=user_id,
            month=current_month,
            year=current_year,
            total_score=total_score,
            challenges_completed=challenges_completed
        )
        db.session.add(leaderboard_entry)
        current_app.logger.info(f"✨ Created new leaderboard entry for user {user_id}")
    
    db.session.commit()
