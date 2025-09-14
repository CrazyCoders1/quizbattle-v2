from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db, limiter
from app.models import User, Admin

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Validate input
        username = data['username'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        
        if len(username) < 3:
            return jsonify({'error': 'Username must be at least 3 characters'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        user = User(
            username=username,
            email=email
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'message': 'User created successfully', 'user': user.to_dict()}), 201
    
    except Exception as e:
        db.session.rollback()
        print(f"Registration error: {str(e)}")  # Server-side logging
        return jsonify({
            'error': 'Registration failed', 
            'details': 'Please try again or contact support'
        }), 500

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Missing username or password'}), 400
        
        username = data['username'].strip()
        password = data['password']
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        access_token = create_access_token(identity=str(user.id))
        return jsonify({
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
    
    except Exception as e:
        print(f"Login error: {str(e)}")  # Server-side logging
        return jsonify({
            'error': 'Login failed',
            'details': 'Please try again or contact support'
        }), 500

@auth_bp.route('/admin/login', methods=['POST'])
@limiter.limit("3 per minute")
def admin_login():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Missing username or password'}), 400
    
    admin = Admin.query.filter_by(username=data['username']).first()
    
    if not admin or not admin.check_password(data['password']):
        return jsonify({'error': 'Invalid admin credentials'}), 401
    
    access_token = create_access_token(identity=f"admin_{admin.id}")
    return jsonify({
        'access_token': access_token,
        'admin': admin.to_dict()
    }), 200

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    current_user_id = get_jwt_identity()
    
    if isinstance(current_user_id, str) and current_user_id.startswith('admin_'):
        admin_id = int(current_user_id.split('_')[1])
        admin = Admin.query.get(admin_id)
        return jsonify({'admin': admin.to_dict()}), 200
    
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'user': user.to_dict()}), 200
