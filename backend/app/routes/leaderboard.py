from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Leaderboard, User, QuizResult, Challenge
from sqlalchemy import func, desc
from datetime import datetime
import logging

leaderboard_bp = Blueprint('leaderboard', __name__)

@leaderboard_bp.route('/', methods=['GET'])
@jwt_required()
def get_leaderboard():
    current_user_id = get_jwt_identity()
    leaderboard_type = request.args.get('type', 'global')
    challenge_id = request.args.get('challenge_id')
    
    current_app.logger.info(f"🏆 Leaderboard request: type={leaderboard_type}, challenge_id={challenge_id}, user={current_user_id}")
    
    # Validate challenge_id if provided
    if challenge_id:
        try:
            challenge_id = int(challenge_id)
        except (ValueError, TypeError):
            current_app.logger.error(f"❌ Invalid challenge_id: {challenge_id}")
            return jsonify({'error': 'Invalid challenge ID'}), 400
    
    try:
        if leaderboard_type == 'challenge' and challenge_id:
            # Challenge-specific leaderboard
            current_app.logger.info(f"🎯 Getting challenge leaderboard for challenge {challenge_id}")
            
            # First verify the challenge exists
            challenge = Challenge.query.get(challenge_id)
            if not challenge:
                current_app.logger.error(f"❌ Challenge {challenge_id} not found")
                return jsonify({'error': 'Challenge not found'}), 404
                
            current_app.logger.info(f"✅ Challenge found: {challenge.name}")
            
            # Get individual results for this specific challenge (not aggregated)
            results = db.session.query(
                QuizResult.user_id,
                User.username,
                QuizResult.score,
                QuizResult.correct_answers,
                QuizResult.wrong_answers,
                QuizResult.submitted_at
            ).join(User).filter(
                QuizResult.challenge_id == challenge_id
            ).order_by(
                desc(QuizResult.score),
                QuizResult.submitted_at.asc()  # Earlier submission wins ties
            ).all()
            
            current_app.logger.info(f"📊 Found {len(results)} results for challenge {challenge_id}")
            
            leaderboard = []
            for i, result in enumerate(results, 1):
                leaderboard.append({
                    'id': i,
                    'user_id': result.user_id,
                    'username': result.username,
                    'score': result.score,
                    'correct_answers': result.correct_answers,
                    'wrong_answers': result.wrong_answers,
                    'submitted_at': result.submitted_at.isoformat() if result.submitted_at else None
                })
        else:
            # Global leaderboard (monthly)
            current_month = datetime.now().month
            current_year = datetime.now().year
            
            current_app.logger.info(f"🌍 Getting global leaderboard for {current_month}/{current_year}")
            
            # Get or create leaderboard entries for current month
            try:
                leaderboard_entries = db.session.query(Leaderboard).filter(
                    Leaderboard.month == current_month,
                    Leaderboard.year == current_year
                ).all()
                
                current_app.logger.info(f"📈 Found {len(leaderboard_entries)} existing leaderboard entries")
            except Exception as query_error:
                current_app.logger.error(f"❌ Failed to query existing leaderboard entries: {query_error}")
                return jsonify({'leaderboard': [], 'error': 'Failed to fetch leaderboard data'}), 500
            
            if not leaderboard_entries:
                # Create leaderboard entries for current month
                current_app.logger.info(f"🛠️ Creating new leaderboard entries for current month")
                users = User.query.all()
                current_app.logger.info(f"👥 Found {len(users)} users to process")
                
                if not users:
                    # No users exist, return empty leaderboard
                    current_app.logger.warning(f"⚠️ No users found in database")
                    return jsonify({'leaderboard': []}), 200
                
                for user in users:
                    # Calculate total score and challenges completed for current month
                    monthly_results = QuizResult.query.filter(
                        QuizResult.user_id == user.id,
                        func.extract('month', QuizResult.submitted_at) == current_month,
                        func.extract('year', QuizResult.submitted_at) == current_year
                    ).all()
                    
                    total_score = sum(result.score for result in monthly_results)
                    challenges_completed = len(monthly_results)
                    
                    current_app.logger.debug(f"📄 User {user.username}: score={total_score}, completed={challenges_completed}")
                    
                    leaderboard_entry = Leaderboard(
                        user_id=user.id,
                        month=current_month,
                        year=current_year,
                        total_score=total_score,
                        challenges_completed=challenges_completed
                    )
                    db.session.add(leaderboard_entry)
                
                try:
                    db.session.commit()
                    current_app.logger.info(f"✅ Created leaderboard entries for {len(users)} users")
                except Exception as commit_error:
                    current_app.logger.error(f"❌ Failed to commit leaderboard entries: {commit_error}")
                    db.session.rollback()
                    # Fall back to empty leaderboard rather than crashing
                    return jsonify({'leaderboard': [], 'error': 'Failed to create leaderboard entries'}), 200
                
                leaderboard_entries = db.session.query(Leaderboard).filter(
                    Leaderboard.month == current_month,
                    Leaderboard.year == current_year
                ).all()
            
            # Join with users and sort by score
            try:
                results = db.session.query(
                    Leaderboard,
                    User.username
                ).join(User).filter(
                    Leaderboard.month == current_month,
                    Leaderboard.year == current_year
                ).order_by(desc(Leaderboard.total_score)).all()
                
                current_app.logger.info(f"📉 Retrieved {len(results)} leaderboard results")
                
            except Exception as query_error:
                current_app.logger.error(f"❌ Failed to query leaderboard results: {query_error}")
                return jsonify({'leaderboard': [], 'error': 'Failed to retrieve leaderboard data'}), 200
            
            leaderboard = []
            for i, (entry, username) in enumerate(results, 1):
                try:
                    leaderboard.append({
                        'id': entry.id,
                        'user_id': entry.user_id,
                        'username': username,
                        'total_score': entry.total_score,
                        'challenges_completed': entry.challenges_completed,
                        'last_updated': entry.last_updated.isoformat() if entry.last_updated else None,
                        'rank': i
                    })
                except Exception as format_error:
                    current_app.logger.error(f"❌ Error formatting leaderboard entry: {format_error}")
                    continue
        
        current_app.logger.info(f"✅ Leaderboard retrieved successfully: {len(leaderboard)} entries")
        return jsonify({'leaderboard': leaderboard}), 200
        
    except Exception as e:
        current_app.logger.error(f"❌ Leaderboard error: {str(e)}")
        return jsonify({'error': f'Failed to fetch leaderboard: {str(e)}'}), 500


@leaderboard_bp.route('/<int:challenge_id>', methods=['GET'])
@jwt_required()
def get_challenge_leaderboard(challenge_id):
    """Get leaderboard for a specific challenge"""
    current_user_id = get_jwt_identity()
    
    current_app.logger.info(f"🎯 Specific challenge leaderboard request: challenge_id={challenge_id}, user={current_user_id}")
    
    try:
        # Get all results for this challenge
        results = db.session.query(
        QuizResult.user_id,
        User.username,
        QuizResult.score,
        QuizResult.correct_answers,
        QuizResult.wrong_answers,
        QuizResult.submitted_at
    ).join(User).filter(
        QuizResult.challenge_id == challenge_id
    ).order_by(
        desc(QuizResult.score),
        QuizResult.submitted_at.asc()  # Earlier submission wins in case of tie
        ).all()
        
        current_app.logger.info(f"📊 Found {len(results)} results for specific challenge {challenge_id}")
        
        leaderboard = []
        for i, result in enumerate(results, 1):
            leaderboard.append({
                'id': i,
                'user_id': result.user_id,
                'username': result.username,
                'score': result.score,
                'correct_answers': result.correct_answers,
                'wrong_answers': result.wrong_answers,
                'submitted_at': result.submitted_at.isoformat() if result.submitted_at else None
            })
        
        current_app.logger.info(f"✅ Challenge leaderboard retrieved: {len(leaderboard)} entries")
        return jsonify({'leaderboard': leaderboard}), 200
        
    except Exception as e:
        current_app.logger.error(f"❌ Challenge leaderboard error: {str(e)}")
        return jsonify({'error': f'Failed to fetch challenge leaderboard: {str(e)}'}), 500
