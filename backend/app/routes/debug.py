from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Challenge, QuizResult, User, Leaderboard, Admin, QuizQuestion
from sqlalchemy import func, desc
from datetime import datetime
import os

debug_bp = Blueprint('debug', __name__)

@debug_bp.route('/database/status', methods=['GET'])
def get_database_status():
    """Check database status and table existence (no auth required)"""
    try:
        current_app.logger.info("🔍 Checking database status")
        
        status = {
            'database_accessible': True,
            'tables': {},
            'counts': {},
            'initialization_status': 'unknown'
        }
        
        # Test each model/table
        try:
            status['counts']['users'] = User.query.count()
            status['tables']['users'] = True
        except Exception as e:
            status['tables']['users'] = False
            status['counts']['users'] = f"Error: {str(e)}"
        
        try:
            status['counts']['admins'] = Admin.query.count()
            status['tables']['admins'] = True
        except Exception as e:
            status['tables']['admins'] = False
            status['counts']['admins'] = f"Error: {str(e)}"
        
        try:
            status['counts']['questions'] = QuizQuestion.query.count()
            status['tables']['questions'] = True
        except Exception as e:
            status['tables']['questions'] = False
            status['counts']['questions'] = f"Error: {str(e)}"
            
        try:
            status['counts']['challenges'] = Challenge.query.count()
            status['tables']['challenges'] = True
        except Exception as e:
            status['tables']['challenges'] = False
            status['counts']['challenges'] = f"Error: {str(e)}"
        
        try:
            status['counts']['quiz_results'] = QuizResult.query.count()
            status['tables']['quiz_results'] = True
        except Exception as e:
            status['tables']['quiz_results'] = False
            status['counts']['quiz_results'] = f"Error: {str(e)}"
            
        try:
            status['counts']['leaderboard'] = Leaderboard.query.count()
            status['tables']['leaderboard'] = True
        except Exception as e:
            status['tables']['leaderboard'] = False
            status['counts']['leaderboard'] = f"Error: {str(e)}"
        
        # Check if all tables exist
        all_tables_exist = all(status['tables'].values())
        
        if all_tables_exist:
            admin_exists = status['counts'].get('admins', 0) > 0
            questions_exist = status['counts'].get('questions', 0) > 0
            
            if admin_exists and questions_exist:
                status['initialization_status'] = 'complete'
            elif admin_exists:
                status['initialization_status'] = 'partial (admin only)'
            else:
                status['initialization_status'] = 'tables exist but empty'
        else:
            status['initialization_status'] = 'tables missing'
        
        status['environment'] = {
            'database_url_set': bool(os.environ.get('DATABASE_URL')),
            'mongo_uri_set': bool(os.environ.get('MONGO_URI')),
            'jwt_secret_set': bool(os.environ.get('JWT_SECRET'))
        }
        
        current_app.logger.info(f"✅ Database status check completed: {status['initialization_status']}")
        return jsonify(status), 200
        
    except Exception as e:
        current_app.logger.error(f"❌ Database status check error: {str(e)}")
        return jsonify({
            'database_accessible': False,
            'error': str(e),
            'initialization_status': 'error'
        }), 500

@debug_bp.route('/user/<int:user_id>/data', methods=['GET'])
@jwt_required()
def get_user_debug_data(user_id):
    """Debug endpoint to check user's challenges and submissions"""
    current_user_id = get_jwt_identity()
    
    # Allow admin or the user themselves to access debug data
    is_admin = isinstance(current_user_id, str) and current_user_id.startswith('admin_')
    is_self = str(current_user_id) == str(user_id)
    
    if not (is_admin or is_self):
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        user = User.query.get_or_404(user_id)
        current_app.logger.info(f"🔍 Debug data request for user {user_id} ({user.username})")
        
        # Get user's created challenges
        created_challenges = Challenge.query.filter_by(created_by=user_id).all()
        
        # Get user's quiz results
        quiz_results = QuizResult.query.filter_by(user_id=user_id).all()
        
        # Get user's leaderboard entries
        leaderboard_entries = Leaderboard.query.filter_by(user_id=user_id).all()
        
        # Calculate current month stats
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        monthly_results = QuizResult.query.filter(
            QuizResult.user_id == user_id,
            func.extract('month', QuizResult.submitted_at) == current_month,
            func.extract('year', QuizResult.submitted_at) == current_year
        ).all()
        
        calculated_monthly_score = sum(result.score for result in monthly_results)
        calculated_challenges_completed = len(monthly_results)
        
        # Get challenge details for each result
        challenge_details = []
        for result in quiz_results:
            challenge = Challenge.query.get(result.challenge_id)
            challenge_details.append({
                'result': result.to_dict(),
                'challenge': challenge.to_dict() if challenge else None
            })
        
        debug_data = {
            'user': user.to_dict(),
            'created_challenges': [c.to_dict() for c in created_challenges],
            'quiz_results': [r.to_dict() for r in quiz_results],
            'challenge_details': challenge_details,
            'leaderboard_entries': [l.to_dict() for l in leaderboard_entries],
            'calculated_stats': {
                'monthly_score': calculated_monthly_score,
                'challenges_completed': calculated_challenges_completed,
                'month': current_month,
                'year': current_year
            },
            'data_consistency': {
                'total_results_count': len(quiz_results),
                'monthly_results_count': len(monthly_results),
                'leaderboard_entries_count': len(leaderboard_entries),
                'created_challenges_count': len(created_challenges)
            }
        }
        
        current_app.logger.info(f"✅ Debug data compiled for user {user_id}")
        return jsonify(debug_data), 200
        
    except Exception as e:
        current_app.logger.error(f"❌ Debug data error: {str(e)}")
        return jsonify({'error': f'Failed to get debug data: {str(e)}'}), 500

@debug_bp.route('/challenge/<int:challenge_id>/data', methods=['GET'])
@jwt_required()
def get_challenge_debug_data(challenge_id):
    """Debug endpoint to check challenge data and submissions"""
    try:
        challenge = Challenge.query.get_or_404(challenge_id)
        current_app.logger.info(f"🔍 Debug data request for challenge {challenge_id} ({challenge.name})")
        
        # Get all results for this challenge
        results = QuizResult.query.filter_by(challenge_id=challenge_id).all()
        
        # Get challenge creator info
        creator = User.query.get(challenge.created_by)
        
        # Get detailed result info with user data
        detailed_results = []
        for result in results:
            user = User.query.get(result.user_id)
            detailed_results.append({
                'result': result.to_dict(),
                'user': user.to_dict() if user else None
            })
        
        debug_data = {
            'challenge': challenge.to_dict(),
            'creator': creator.to_dict() if creator else None,
            'results': [r.to_dict() for r in results],
            'detailed_results': detailed_results,
            'stats': {
                'total_submissions': len(results),
                'unique_users': len(set(r.user_id for r in results)),
                'avg_score': sum(r.score for r in results) / len(results) if results else 0,
                'max_score': max(r.score for r in results) if results else 0,
                'min_score': min(r.score for r in results) if results else 0
            }
        }
        
        current_app.logger.info(f"✅ Debug data compiled for challenge {challenge_id}")
        return jsonify(debug_data), 200
        
    except Exception as e:
        current_app.logger.error(f"❌ Challenge debug data error: {str(e)}")
        return jsonify({'error': f'Failed to get challenge debug data: {str(e)}'}), 500

@debug_bp.route('/database/consistency', methods=['GET'])
@jwt_required()
def check_database_consistency():
    """Check overall database consistency"""
    current_user_id = get_jwt_identity()
    
    # Only allow admins
    if not (isinstance(current_user_id, str) and current_user_id.startswith('admin_')):
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        current_app.logger.info("🔍 Running database consistency check")
        
        # Count totals
        total_users = User.query.count()
        total_challenges = Challenge.query.count()
        total_results = QuizResult.query.count()
        total_leaderboard_entries = Leaderboard.query.count()
        
        # Check for orphaned records
        orphaned_results = db.session.query(QuizResult).outerjoin(
            Challenge, QuizResult.challenge_id == Challenge.id
        ).filter(Challenge.id.is_(None)).count()
        
        orphaned_leaderboard = db.session.query(Leaderboard).outerjoin(
            User, Leaderboard.user_id == User.id
        ).filter(User.id.is_(None)).count()
        
        # Check current month leaderboard accuracy
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        inconsistent_leaderboards = []
        leaderboard_entries = Leaderboard.query.filter_by(
            month=current_month, year=current_year
        ).all()
        
        for entry in leaderboard_entries:
            # Recalculate user's monthly stats
            monthly_results = QuizResult.query.filter(
                QuizResult.user_id == entry.user_id,
                func.extract('month', QuizResult.submitted_at) == current_month,
                func.extract('year', QuizResult.submitted_at) == current_year
            ).all()
            
            calculated_score = sum(r.score for r in monthly_results)
            calculated_completed = len(monthly_results)
            
            if (entry.total_score != calculated_score or 
                entry.challenges_completed != calculated_completed):
                inconsistent_leaderboards.append({
                    'user_id': entry.user_id,
                    'stored_score': entry.total_score,
                    'calculated_score': calculated_score,
                    'stored_completed': entry.challenges_completed,
                    'calculated_completed': calculated_completed
                })
        
        consistency_data = {
            'totals': {
                'users': total_users,
                'challenges': total_challenges,
                'quiz_results': total_results,
                'leaderboard_entries': total_leaderboard_entries
            },
            'orphaned_records': {
                'quiz_results_without_challenge': orphaned_results,
                'leaderboard_entries_without_user': orphaned_leaderboard
            },
            'leaderboard_inconsistencies': inconsistent_leaderboards,
            'current_period': {
                'month': current_month,
                'year': current_year
            },
            'recommendations': []
        }
        
        # Add recommendations
        if orphaned_results > 0:
            consistency_data['recommendations'].append(
                f"Clean up {orphaned_results} orphaned quiz results"
            )
        
        if orphaned_leaderboard > 0:
            consistency_data['recommendations'].append(
                f"Clean up {orphaned_leaderboard} orphaned leaderboard entries"
            )
        
        if inconsistent_leaderboards:
            consistency_data['recommendations'].append(
                f"Fix {len(inconsistent_leaderboards)} inconsistent leaderboard entries"
            )
        
        current_app.logger.info(f"✅ Consistency check completed")
        return jsonify(consistency_data), 200
        
    except Exception as e:
        current_app.logger.error(f"❌ Consistency check error: {str(e)}")
        return jsonify({'error': f'Failed to check consistency: {str(e)}'}), 500

@debug_bp.route('/fix/leaderboard', methods=['POST'])
@jwt_required()
def fix_leaderboard_inconsistencies():
    """Fix leaderboard inconsistencies"""
    current_user_id = get_jwt_identity()
    
    # Only allow admins
    if not (isinstance(current_user_id, str) and current_user_id.startswith('admin_')):
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        current_app.logger.info("🔧 Starting leaderboard fix")
        
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        # Get all users with quiz results this month
        users_with_results = db.session.query(QuizResult.user_id).filter(
            func.extract('month', QuizResult.submitted_at) == current_month,
            func.extract('year', QuizResult.submitted_at) == current_year
        ).distinct().all()
        
        fixed_count = 0
        created_count = 0
        
        for (user_id,) in users_with_results:
            # Recalculate user's monthly stats
            monthly_results = QuizResult.query.filter(
                QuizResult.user_id == user_id,
                func.extract('month', QuizResult.submitted_at) == current_month,
                func.extract('year', QuizResult.submitted_at) == current_year
            ).all()
            
            calculated_score = sum(r.score for r in monthly_results)
            calculated_completed = len(monthly_results)
            
            # Find or create leaderboard entry
            entry = Leaderboard.query.filter_by(
                user_id=user_id,
                month=current_month,
                year=current_year
            ).first()
            
            if entry:
                if (entry.total_score != calculated_score or 
                    entry.challenges_completed != calculated_completed):
                    entry.total_score = calculated_score
                    entry.challenges_completed = calculated_completed
                    entry.last_updated = datetime.utcnow()
                    fixed_count += 1
            else:
                entry = Leaderboard(
                    user_id=user_id,
                    month=current_month,
                    year=current_year,
                    total_score=calculated_score,
                    challenges_completed=calculated_completed
                )
                db.session.add(entry)
                created_count += 1
        
        db.session.commit()
        
        current_app.logger.info(f"✅ Leaderboard fix completed: {fixed_count} fixed, {created_count} created")
        return jsonify({
            'message': 'Leaderboard inconsistencies fixed',
            'fixed_entries': fixed_count,
            'created_entries': created_count
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"❌ Leaderboard fix error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': f'Failed to fix leaderboard: {str(e)}'}), 500

@debug_bp.route('/extraction/logs', methods=['GET'])
@jwt_required()
def get_extraction_logs():
    """Get PDF extraction logs including OpenRouter model usage"""
    current_user_id = get_jwt_identity()
    
    # Only allow admins
    if not (isinstance(current_user_id, str) and current_user_id.startswith('admin_')):
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        current_app.logger.info("🔍 Fetching extraction logs")
        
        # Get query parameters
        limit = request.args.get('limit', 50, type=int)
        service = request.args.get('service', None)  # openrouter, pdf_extractor, regex
        success_only = request.args.get('success_only', 'false').lower() == 'true'
        
        # Build MongoDB query
        query = {}
        if service:
            query['service'] = service
        if success_only:
            query['success'] = True
        
        # Fetch logs from MongoDB
        logs = list(current_app.mongo_db.extraction_logs.find(
            query
        ).sort('timestamp', -1).limit(limit))
        
        # Convert ObjectId to string for JSON serialization
        for log in logs:
            log['_id'] = str(log['_id'])
            if 'timestamp' in log:
                log['timestamp'] = log['timestamp'].isoformat()
        
        # Calculate statistics
        total_logs = len(logs)
        successful_extractions = sum(1 for log in logs if log.get('success', False))
        failed_extractions = total_logs - successful_extractions
        
        # Provider statistics
        provider_stats = {}
        service_stats = {}
        total_questions_extracted = 0
        
        for log in logs:
            provider = log.get('provider', 'unknown')
            service_name = log.get('service', 'unknown')
            questions = log.get('questions_extracted', 0)
            
            if provider not in provider_stats:
                provider_stats[provider] = {'attempts': 0, 'successes': 0, 'questions': 0}
            if service_name not in service_stats:
                service_stats[service_name] = {'attempts': 0, 'successes': 0, 'questions': 0}
            
            provider_stats[provider]['attempts'] += 1
            service_stats[service_name]['attempts'] += 1
            
            if log.get('success', False):
                provider_stats[provider]['successes'] += 1
                provider_stats[provider]['questions'] += questions
                service_stats[service_name]['successes'] += 1
                service_stats[service_name]['questions'] += questions
                total_questions_extracted += questions
        
        # Recent session activity
        session_stats = {}
        for log in logs:
            session_id = log.get('session_id', 'unknown')
            if session_id not in session_stats:
                session_stats[session_id] = {'attempts': 0, 'questions': 0}
            session_stats[session_id]['attempts'] += 1
            if log.get('success', False):
                session_stats[session_id]['questions'] += log.get('questions_extracted', 0)
        
        extraction_data = {
            'logs': logs,
            'query_params': {
                'limit': limit,
                'service': service,
                'success_only': success_only
            },
            'statistics': {
                'total_logs': total_logs,
                'successful_extractions': successful_extractions,
                'failed_extractions': failed_extractions,
                'success_rate': (successful_extractions / total_logs * 100) if total_logs > 0 else 0,
                'total_questions_extracted': total_questions_extracted
            },
            'provider_stats': provider_stats,
            'service_stats': service_stats,
            'session_stats': dict(list(session_stats.items())[:10])  # Top 10 sessions
        }
        
        current_app.logger.info(f"✅ Fetched {total_logs} extraction logs")
        return jsonify(extraction_data), 200
        
    except Exception as e:
        current_app.logger.error(f"❌ Extraction logs error: {str(e)}")
        return jsonify({'error': f'Failed to get extraction logs: {str(e)}'}), 500

@debug_bp.route('/leaderboard/raw', methods=['GET'])
@jwt_required()
def get_raw_leaderboard_data():
    """Forensic endpoint: Get raw quiz_result data for leaderboard analysis"""
    current_user_id = get_jwt_identity()
    
    # Only allow admins
    if not (isinstance(current_user_id, str) and current_user_id.startswith('admin_')):
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        current_app.logger.info("🔍 Raw leaderboard forensic query requested")
        
        # Get query parameters
        limit = request.args.get('limit', 50, type=int)
        challenge_id = request.args.get('challenge_id', type=int)
        user_id = request.args.get('user_id', type=int)
        
        # Build base query for top scoring quiz results
        query = QuizResult.query
        
        # Apply filters if provided
        if challenge_id:
            query = query.filter(QuizResult.challenge_id == challenge_id)
            current_app.logger.info(f"🎯 Filtering by challenge_id: {challenge_id}")
        
        if user_id:
            query = query.filter(QuizResult.user_id == user_id)
            current_app.logger.info(f"👤 Filtering by user_id: {user_id}")
        
        # Get results ordered by score (top performers first)
        results = query.order_by(desc(QuizResult.score), desc(QuizResult.submitted_at)).limit(limit).all()
        
        # Get user and challenge info for each result
        forensic_data = []
        for result in results:
            user = User.query.get(result.user_id)
            challenge = Challenge.query.get(result.challenge_id)
            
            forensic_data.append({
                'quiz_result': result.to_dict(),
                'user_info': {
                    'id': user.id if user else None,
                    'username': user.username if user else 'DELETED_USER'
                },
                'challenge_info': {
                    'id': challenge.id if challenge else None,
                    'name': challenge.name if challenge else 'DELETED_CHALLENGE'
                }
            })
        
        response_data = {
            'total_results': len(forensic_data),
            'query_params': {
                'limit': limit,
                'challenge_id': challenge_id,
                'user_id': user_id
            },
            'raw_leaderboard_data': forensic_data
        }
        
        current_app.logger.info(f"✅ Raw leaderboard data compiled: {len(forensic_data)} results")
        return jsonify(response_data), 200
        
    except Exception as e:
        current_app.logger.error(f"❌ Raw leaderboard forensic error: {str(e)}")
        return jsonify({'error': f'Failed to get raw leaderboard data: {str(e)}'}), 500

@debug_bp.route('/challenge/<int:challenge_id>/results', methods=['GET'])
@jwt_required()
def get_challenge_results_forensic(challenge_id):
    """Forensic endpoint: Get all quiz results for a specific challenge"""
    current_user_id = get_jwt_identity()
    
    # Only allow admins
    if not (isinstance(current_user_id, str) and current_user_id.startswith('admin_')):
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        current_app.logger.info(f"🔍 Challenge forensic query requested for challenge_id: {challenge_id}")
        
        # Verify challenge exists
        challenge = Challenge.query.get(challenge_id)
        if not challenge:
            return jsonify({'error': f'Challenge {challenge_id} not found'}), 404
        
        # Get all results for this challenge
        results = QuizResult.query.filter_by(challenge_id=challenge_id).order_by(
            desc(QuizResult.score), 
            QuizResult.submitted_at.asc()
        ).all()
        
        # Get detailed forensic data
        forensic_results = []
        user_participation = {}
        
        for result in results:
            user = User.query.get(result.user_id)
            
            # Track user participation patterns
            if result.user_id not in user_participation:
                user_participation[result.user_id] = {
                    'username': user.username if user else 'DELETED_USER',
                    'submission_count': 0,
                    'best_score': 0,
                    'avg_score': 0,
                    'scores': []
                }
            
            user_participation[result.user_id]['submission_count'] += 1
            user_participation[result.user_id]['scores'].append(result.score)
            
            forensic_results.append({
                'quiz_result': result.to_dict(),
                'user_info': {
                    'id': user.id if user else None,
                    'username': user.username if user else 'DELETED_USER'
                }
            })
        
        # Calculate user participation stats
        for user_id, stats in user_participation.items():
            stats['best_score'] = max(stats['scores'])
            stats['avg_score'] = sum(stats['scores']) / len(stats['scores'])
            del stats['scores']  # Remove raw scores for cleaner output
        
        response_data = {
            'challenge_info': challenge.to_dict(),
            'total_results': len(forensic_results),
            'unique_participants': len(user_participation),
            'results': forensic_results,
            'user_participation_analysis': user_participation,
            'statistics': {
                'avg_score': sum(r.score for r in results) / len(results) if results else 0,
                'max_score': max(r.score for r in results) if results else 0,
                'min_score': min(r.score for r in results) if results else 0,
                'score_distribution': {
                    'perfect_scores': len([r for r in results if r.score == r.total_questions]),
                    'above_80pct': len([r for r in results if r.score >= (r.total_questions * 0.8)]),
                    'above_60pct': len([r for r in results if r.score >= (r.total_questions * 0.6)]),
                    'below_60pct': len([r for r in results if r.score < (r.total_questions * 0.6)])
                }
            }
        }
        
        current_app.logger.info(f"✅ Challenge forensic data compiled: {len(forensic_results)} results, {len(user_participation)} users")
        return jsonify(response_data), 200
        
    except Exception as e:
        current_app.logger.error(f"❌ Challenge forensic error: {str(e)}")
        return jsonify({'error': f'Failed to get challenge forensic data: {str(e)}'}), 500

@debug_bp.route('/user/<int:user_id>/results', methods=['GET'])
@jwt_required()
def get_user_results_forensic(user_id):
    """Forensic endpoint: Get all quiz results for a specific user"""
    current_user_id = get_jwt_identity()
    
    # Only allow admins
    if not (isinstance(current_user_id, str) and current_user_id.startswith('admin_')):
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        current_app.logger.info(f"🔍 User forensic query requested for user_id: {user_id}")
        
        # Verify user exists
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': f'User {user_id} not found'}), 404
        
        # Get all results for this user
        results = QuizResult.query.filter_by(user_id=user_id).order_by(
            desc(QuizResult.submitted_at)
        ).all()
        
        # Get detailed forensic data
        forensic_results = []
        challenge_participation = {}
        monthly_stats = {}
        
        for result in results:
            challenge = Challenge.query.get(result.challenge_id)
            submission_month = result.submitted_at.strftime('%Y-%m') if result.submitted_at else 'unknown'
            
            # Track challenge participation
            if result.challenge_id not in challenge_participation:
                challenge_participation[result.challenge_id] = {
                    'challenge_name': challenge.name if challenge else 'DELETED_CHALLENGE',
                    'submissions': 0,
                    'best_score': 0,
                    'latest_submission': None
                }
            
            challenge_participation[result.challenge_id]['submissions'] += 1
            challenge_participation[result.challenge_id]['best_score'] = max(
                challenge_participation[result.challenge_id]['best_score'], 
                result.score
            )
            challenge_participation[result.challenge_id]['latest_submission'] = result.submitted_at.isoformat() if result.submitted_at else None
            
            # Track monthly stats
            if submission_month not in monthly_stats:
                monthly_stats[submission_month] = {
                    'total_score': 0,
                    'challenges_completed': 0,
                    'avg_score': 0
                }
            
            monthly_stats[submission_month]['total_score'] += result.score
            monthly_stats[submission_month]['challenges_completed'] += 1
            
            forensic_results.append({
                'quiz_result': result.to_dict(),
                'challenge_info': {
                    'id': challenge.id if challenge else None,
                    'name': challenge.name if challenge else 'DELETED_CHALLENGE'
                }
            })
        
        # Calculate monthly averages
        for month, stats in monthly_stats.items():
            stats['avg_score'] = stats['total_score'] / stats['challenges_completed'] if stats['challenges_completed'] > 0 else 0
        
        # Get current leaderboard entry
        current_month = datetime.now().month
        current_year = datetime.now().year
        current_leaderboard = Leaderboard.query.filter_by(
            user_id=user_id,
            month=current_month,
            year=current_year
        ).first()
        
        response_data = {
            'user_info': user.to_dict(),
            'total_results': len(forensic_results),
            'unique_challenges': len(challenge_participation),
            'results': forensic_results,
            'challenge_participation_analysis': challenge_participation,
            'monthly_performance': monthly_stats,
            'current_leaderboard_entry': current_leaderboard.to_dict() if current_leaderboard else None,
            'statistics': {
                'total_score_all_time': sum(r.score for r in results),
                'avg_score_all_time': sum(r.score for r in results) / len(results) if results else 0,
                'best_score': max(r.score for r in results) if results else 0,
                'perfect_scores': len([r for r in results if r.score == r.total_questions]),
                'participation_streak': len(set(r.submitted_at.strftime('%Y-%m') for r in results if r.submitted_at))
            }
        }
        
        current_app.logger.info(f"✅ User forensic data compiled: {len(forensic_results)} results, {len(challenge_participation)} challenges")
        return jsonify(response_data), 200
        
    except Exception as e:
        current_app.logger.error(f"❌ User forensic error: {str(e)}")
        return jsonify({'error': f'Failed to get user forensic data: {str(e)}'}), 500

@debug_bp.route('/extraction/models', methods=['GET'])
@jwt_required()
def get_openrouter_model_stats():
    """Get OpenRouter model usage statistics"""
    current_user_id = get_jwt_identity()
    
    # Only allow admins
    if not (isinstance(current_user_id, str) and current_user_id.startswith('admin_')):
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        current_app.logger.info("🔍 Fetching OpenRouter model statistics")
        
        # Get OpenRouter-specific logs
        openrouter_logs = list(current_app.mongo_db.extraction_logs.find({
            'service': 'openrouter'
        }).sort('timestamp', -1))
        
        # Analyze model performance
        model_stats = {}
        recent_24h_count = 0
        recent_24h_threshold = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        for log in openrouter_logs:
            provider = log.get('provider', 'unknown')
            success = log.get('success', False)
            questions = log.get('questions_extracted', 0)
            timestamp = log.get('timestamp')
            
            if timestamp and timestamp >= recent_24h_threshold:
                recent_24h_count += 1
            
            if provider not in model_stats:
                model_stats[provider] = {
                    'total_attempts': 0,
                    'successful_attempts': 0,
                    'failed_attempts': 0,
                    'total_questions': 0,
                    'success_rate': 0,
                    'avg_questions_per_success': 0,
                    'last_used': None,
                    'errors': []
                }
            
            stats = model_stats[provider]
            stats['total_attempts'] += 1
            
            if success:
                stats['successful_attempts'] += 1
                stats['total_questions'] += questions
            else:
                stats['failed_attempts'] += 1
                error = log.get('error')
                if error and len(stats['errors']) < 5:  # Keep last 5 errors
                    stats['errors'].append(error)
            
            # Update last used timestamp
            if timestamp and (not stats['last_used'] or timestamp > stats['last_used']):
                stats['last_used'] = timestamp
        
        # Calculate derived statistics
        for provider, stats in model_stats.items():
            if stats['total_attempts'] > 0:
                stats['success_rate'] = (stats['successful_attempts'] / stats['total_attempts']) * 100
            if stats['successful_attempts'] > 0:
                stats['avg_questions_per_success'] = stats['total_questions'] / stats['successful_attempts']
            if stats['last_used']:
                stats['last_used'] = stats['last_used'].isoformat()
        
        # Sort models by success rate and recent usage
        sorted_models = sorted(
            model_stats.items(), 
            key=lambda x: (x[1]['success_rate'], x[1]['successful_attempts']), 
            reverse=True
        )
        
        # Get available models list from OpenRouter service
        try:
            from app.services.openrouter_pdf_extractor import get_openrouter_extractor
            extractor = get_openrouter_extractor()
            available_models = extractor.openrouter.MODELS if extractor.openrouter else []
        except:
            available_models = []
        
        model_data = {
            'total_openrouter_logs': len(openrouter_logs),
            'recent_24h_attempts': recent_24h_count,
            'available_models': available_models,
            'available_models_count': len(available_models),
            'tested_models_count': len(model_stats),
            'model_statistics': dict(sorted_models),
            'top_performing_models': [
                {'model': model, 'stats': stats} 
                for model, stats in sorted_models[:10]
            ],
            'summary': {
                'total_questions_from_openrouter': sum(
                    stats['total_questions'] for stats in model_stats.values()
                ),
                'most_reliable_model': sorted_models[0][0] if sorted_models else None,
                'least_reliable_model': sorted_models[-1][0] if sorted_models else None
            }
        }
        
        current_app.logger.info(f"✅ Compiled OpenRouter model statistics: {len(model_stats)} models analyzed")
        return jsonify(model_data), 200
        
    except Exception as e:
        current_app.logger.error(f"❌ OpenRouter model stats error: {str(e)}")
        return jsonify({'error': f'Failed to get OpenRouter model stats: {str(e)}'}), 500
