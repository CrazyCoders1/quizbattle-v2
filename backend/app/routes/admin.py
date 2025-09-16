from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db, limiter
from app.models import User, QuizQuestion, Challenge, QuizResult
from datetime import datetime
import re
import os
from app.services.pdf_extractor import get_extractor

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    current_user_id = get_jwt_identity()
    
    if not isinstance(current_user_id, str) or not current_user_id.startswith('admin_'):
        return jsonify({'error': 'Admin access required'}), 403
    
    stats = {
        'total_users': User.query.count(),
        'total_questions': QuizQuestion.query.count(),
        'total_challenges': Challenge.query.count(),
        'total_results': QuizResult.query.count()
    }
    
    return jsonify({'stats': stats}), 200

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    current_user_id = get_jwt_identity()
    
    if not isinstance(current_user_id, str) or not current_user_id.startswith('admin_'):
        return jsonify({'error': 'Admin access required'}), 403
    
    users = User.query.all()
    return jsonify({'users': [user.to_dict() for user in users]}), 200

@admin_bp.route('/questions', methods=['GET'])
@jwt_required()
def get_questions():
    current_user_id = get_jwt_identity()
    
    if not isinstance(current_user_id, str) or not current_user_id.startswith('admin_'):
        return jsonify({'error': 'Admin access required'}), 403
    
    # Only return active questions by default
    include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
    
    if include_inactive:
        questions = QuizQuestion.query.all()
    else:
        questions = QuizQuestion.query.filter_by(is_active=True).all()
    
    return jsonify({'questions': [q.to_dict() for q in questions]}), 200

@admin_bp.route('/questions', methods=['POST'])
@jwt_required()
def create_question():
    current_user_id = get_jwt_identity()
    
    if not isinstance(current_user_id, str) or not current_user_id.startswith('admin_'):
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    
    question = QuizQuestion(
        text=data.get('text'),
        options=data.get('options'),
        answer=data.get('answer'),
        difficulty=data.get('difficulty'),
        exam_type=data.get('exam_type')
    )
    
    db.session.add(question)
    db.session.commit()
    
    return jsonify({'question': question.to_dict()}), 201

@admin_bp.route('/questions/<int:question_id>', methods=['PUT'])
@jwt_required()
def update_question(question_id):
    current_user_id = get_jwt_identity()
    
    if not isinstance(current_user_id, str) or not current_user_id.startswith('admin_'):
        return jsonify({'error': 'Admin access required'}), 403
    
    question = QuizQuestion.query.get_or_404(question_id)
    data = request.get_json()
    
    question.text = data.get('text', question.text)
    question.options = data.get('options', question.options)
    question.answer = data.get('answer', question.answer)
    question.difficulty = data.get('difficulty', question.difficulty)
    question.exam_type = data.get('exam_type', question.exam_type)
    
    db.session.commit()
    
    return jsonify({'question': question.to_dict()}), 200

@admin_bp.route('/questions/<int:question_id>', methods=['DELETE'])
@jwt_required()
def delete_question(question_id):
    current_user_id = get_jwt_identity()
    
    if not isinstance(current_user_id, str) or not current_user_id.startswith('admin_'):
        return jsonify({'error': 'Admin access required'}), 403
    
    question = QuizQuestion.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    
    return jsonify({'message': 'Question deleted successfully'}), 200

@admin_bp.route('/upload-pdf', methods=['POST'])
@jwt_required()
@limiter.limit("2 per minute")
def upload_pdf():
    current_user_id = get_jwt_identity()
    
    if not isinstance(current_user_id, str) or not current_user_id.startswith('admin_'):
        return jsonify({'error': 'Admin access required'}), 403
    
    if 'pdf' not in request.files:
        return jsonify({'error': 'No PDF file provided'}), 400
    
    file = request.files['pdf']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
        
    exam_type = request.form.get('exam_type', 'CBSE 11')
    difficulty_mode = request.form.get('difficulty', 'mixed')  # easy, tough, mixed
    
    if file and file.filename.lower().endswith('.pdf'):
        try:
            # Import required modules
            from PyPDF2 import PdfReader
            import tempfile
            from flask import current_app
            
            current_app.logger.info(f"📁 Starting PDF processing: {file.filename}")
            
            # Use temp directory which is writable on Render
            upload_folder = None
            for tmp_path in ['/tmp', tempfile.gettempdir(), './tmp']:
                if os.path.exists(tmp_path) or tmp_path == tempfile.gettempdir():
                    upload_folder = tmp_path
                    break
                    
            if not upload_folder:
                current_app.logger.error("❌ No writable temp directory found")
                return jsonify({'error': 'Server configuration error: no writable directory'}), 500
            
            current_app.logger.info(f"📂 Using upload folder: {upload_folder}")
            
            # Ensure directory exists and is writable
            try:
                os.makedirs(upload_folder, exist_ok=True)
                # Test write access
                test_file = os.path.join(upload_folder, '.write_test')
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                current_app.logger.info("✅ Directory write test successful")
            except Exception as e:
                current_app.logger.error(f"❌ Directory not writable: {str(e)}")
                return jsonify({'error': f'Cannot write to temp directory: {str(e)}'}), 500
            
            # Generate safe filename
            safe_filename = re.sub(r'[^\w\s-]', '', file.filename.replace(' ', '_'))
            filename = f"pdf_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{safe_filename}"
            filepath = os.path.join(upload_folder, filename)
            
            current_app.logger.info(f"💾 Saving file to: {filepath}")
            file.save(filepath)
            
            # Verify file was saved
            if not os.path.exists(filepath):
                current_app.logger.error(f"❌ File not found after save: {filepath}")
                return jsonify({'error': 'Failed to save uploaded file'}), 500
                
            file_size = os.path.getsize(filepath)
            current_app.logger.info(f"✅ File saved successfully: {file_size} bytes")
            
            # Process PDF and extract questions
            reader = PdfReader(filepath)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            
            # Extract questions using new AI + regex service with difficulty mode
            extractor = get_extractor()
            questions_extracted = extractor.extract_questions_from_text(text, exam_type, difficulty_mode)
            
            # Save extracted questions to database
            saved_questions = []
            for q_data in questions_extracted:
                question = QuizQuestion(
                    text=q_data['question'],
                    options=q_data['options'],
                    answer=q_data['correct_answer'],
                    difficulty=q_data['difficulty'],
                    exam_type=q_data['exam_type'],
                    hint=q_data.get('hint')
                )
                db.session.add(question)
                saved_questions.append(q_data)
            
            db.session.commit()
            
            # Log the upload in MongoDB
            from app import mongo_client
            upload_log = {
                'filename': filename,
                'original_filename': file.filename,
                'uploaded_by': current_user_id,
                'uploaded_at': datetime.utcnow(),
                'file_size': os.path.getsize(filepath),
                'status': 'processed',
                'questions_extracted': len(saved_questions),
                'exam_type': exam_type
            }
            
            # Insert into MongoDB (note: fixed the mongo access)
            try:
                current_app.mongo_db.pdf_uploads.insert_one(upload_log)
                current_app.logger.info("✅ Upload logged to MongoDB")
            except Exception as mongo_error:
                current_app.logger.warning(f"⚠️ MongoDB logging failed: {str(mongo_error)}")
            
            # Clean up temp file
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
                    current_app.logger.info(f"🗑️ Cleaned up temp file: {filename}")
            except Exception as cleanup_error:
                current_app.logger.warning(f"⚠️ Failed to cleanup temp file: {str(cleanup_error)}")
            
            current_app.logger.info(f"✅ PDF processing completed successfully: {len(saved_questions)} questions added")
            
            return jsonify({
                'message': 'PDF processed successfully!',
                'filename': filename,
                'questions_added': len(saved_questions),
                'breakdown': {
                    'easy': sum(1 for q in saved_questions if q['difficulty'] == 'easy'),
                    'tough': sum(1 for q in saved_questions if q['difficulty'] == 'tough')
                },
                'extraction_details': {
                    'total_extracted': len(questions_extracted),
                    'total_saved': len(saved_questions),
                    'exam_type': exam_type,
                    'difficulty_mode': difficulty_mode
                }
            }), 200
            
        except Exception as e:
            current_app.logger.error(f"❌ PDF processing failed: {str(e)}")
            
            # Clean up temp file on error
            try:
                if 'filepath' in locals() and os.path.exists(filepath):
                    os.remove(filepath)
                    current_app.logger.info(f"🗑️ Cleaned up temp file after error: {filename}")
            except Exception as cleanup_error:
                current_app.logger.warning(f"⚠️ Failed to cleanup temp file after error: {str(cleanup_error)}")
            
            db.session.rollback()
            return jsonify({'error': f'Failed to process PDF: {str(e)}'}), 500
    else:
        return jsonify({'error': 'Only PDF files are allowed'}), 400

@admin_bp.route('/questions/delete-bulk', methods=['POST'])
@jwt_required()
def delete_bulk_questions():
    current_user_id = get_jwt_identity()
    
    if not isinstance(current_user_id, str) or not current_user_id.startswith('admin_'):
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    question_ids = data.get('question_ids', [])
    
    if not question_ids or not isinstance(question_ids, list):
        return jsonify({'error': 'Invalid question_ids provided'}), 400
    
    try:
        # Track results
        success_count = 0
        failed_ids = []
        
        for question_id in question_ids:
            try:
                # Soft delete: mark as inactive instead of hard delete
                question = QuizQuestion.query.get(question_id)
                if question:
                    question.is_active = False
                    success_count += 1
                else:
                    failed_ids.append(question_id)
                    
            except Exception as e:
                failed_ids.append(question_id)
                current_app.logger.error(f"Failed to delete question {question_id}: {str(e)}")
        
        # Also mark questions as inactive in any challenges they belong to
        # Note: You may need to create a challenge_questions table with is_active field
        # For now, we'll just handle the questions table
        
        db.session.commit()
        
        return jsonify({
            'message': f'Successfully deleted {success_count} questions',
            'success_count': success_count,
            'failed_count': len(failed_ids),
            'failed_ids': failed_ids,
            'total_requested': len(question_ids)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete questions: {str(e)}'}), 500

