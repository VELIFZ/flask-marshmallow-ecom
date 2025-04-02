from flask import request, jsonify, Blueprint, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from models import db
from models.user_model import User
from schemas.user_schema import user_schema
from marshmallow import ValidationError
from datetime import datetime, timedelta
import jwt
from functools import wraps
from utils.db_helpers import (
    get_table, row_to_dict, handle_error, execute_query
)
from sqlalchemy import select

auth_bp = Blueprint('auth', __name__)

# JWT token required decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check if token is in headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Token is missing or invalid'}), 401
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            # Decode the token
            data = jwt.decode(
                token, 
                current_app.config['SECRET_KEY'], 
                algorithms=["HS256"]
            )
            current_user = db.session.get(User, data['user_id'])
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except (jwt.InvalidTokenError, Exception) as e:
            return jsonify({'message': 'Token is invalid', 'error': str(e)}), 401
        
        # Pass the current user to the route
        return f(current_user, *args, **kwargs)
    
    return decorated

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        
        # Get users table
        users_table = get_table('users')
        
        # Check if email already exists
        existing_query = select(users_table).where(users_table.c.email == data['email'])
        existing_user = execute_query(existing_query, single_result=True)
        
        if existing_user:
            return jsonify({'message': 'Email already registered'}), 409
        
        # Create new user
        new_user = User(
            name=data['name'],
            last_name=data['last_name'],
            email=data['email'],
            password=generate_password_hash(data['password']) if 'password' in data else None,
            role=data.get('role', 'buyer')  # Default role is buyer
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user_schema.dump(new_user)
        }), 201
        
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        db.session.rollback()
        return handle_error(e, "registering user")

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        auth = request.json
        
        if not auth or not auth.get('email') or not auth.get('password'):
            return jsonify({'message': 'Missing email or password'}), 401
        
        # Get users table
        users_table = get_table('users')
        
        # Query user by email
        user_query = select(users_table).where(users_table.c.email == auth.get('email'))
        user_row = execute_query(user_query, single_result=True)
        
        if not user_row:
            return jsonify({'message': 'User not found'}), 404
        
        # Convert to User object for password verification
        user = db.session.get(User, user_row.id)
            
        if not user.password:  # Guest user without password
            return jsonify({'message': 'Account requires password setup'}), 403
            
        if not check_password_hash(user.password, auth.get('password')):
            return jsonify({'message': 'Incorrect password'}), 401
            
        # Generate JWT token
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, current_app.config['SECRET_KEY'], algorithm="HS256")
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': user_schema.dump(user)
        }), 200
        
    except Exception as e:
        return handle_error(e, "logging in")

@auth_bp.route('/refresh', methods=['POST'])
@token_required
def refresh_token(current_user):
    try:
        # Generate new JWT token
        token = jwt.encode({
            'user_id': current_user.id,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, current_app.config['SECRET_KEY'], algorithm="HS256")
        
        return jsonify({
            'message': 'Token refreshed',
            'token': token
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Token refresh failed', 'error': str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_me(current_user):
    try:
        return jsonify(user_schema.dump(current_user)), 200
    except Exception as e:
        return jsonify({'message': 'Failed to get user info', 'error': str(e)}), 500

@auth_bp.route('/reset-password', methods=['POST'])
def request_password_reset():
    try:
        data = request.json
        
        if not data or not data.get('email'):
            return jsonify({'message': 'Email is required'}), 400
            
        user = User.query.filter_by(email=data.get('email')).first()
        
        if not user:
            # For security reasons, don't reveal if user exists
            return jsonify({'message': 'If your email is registered, you will receive a reset link'}), 200
            
        # Generate reset token
        reset_token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(hours=1)
        }, current_app.config['SECRET_KEY'], algorithm="HS256")
        
        # In a real app, send email with reset link
        # For now, just return the token in response
        reset_link = f"/auth/reset-password/{reset_token}"
        
        return jsonify({
            'message': 'Password reset link generated',
            'reset_link': reset_link
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Password reset request failed', 'error': str(e)}), 500

@auth_bp.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    try:
        data = request.json
        
        if not data or not data.get('password'):
            return jsonify({'message': 'New password is required'}), 400
            
        try:
            # Decode the token
            payload = jwt.decode(
                token, 
                current_app.config['SECRET_KEY'], 
                algorithms=["HS256"]
            )
            user_id = payload['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Reset link has expired'}), 401
        except (jwt.InvalidTokenError, Exception):
            return jsonify({'message': 'Invalid reset link'}), 401
            
        user = db.session.get(User, user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
            
        # Update password
        user.password = generate_password_hash(data['password'])
        db.session.commit()
        
        return jsonify({'message': 'Password reset successful'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Password reset failed', 'error': str(e)}), 500 