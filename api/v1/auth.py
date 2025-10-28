"""
Authentication API v1 Endpoints
Handles user authentication with proper error handling and monitoring
"""

from flask import Blueprint, request, jsonify
from typing import Dict, Any

from services.auth_service import AuthService
from monitoring import monitor_endpoint, logger

def create_auth_blueprint(auth_service: AuthService) -> Blueprint:
    """Create authentication blueprint with service injection"""
    
    auth_bp = Blueprint('auth_v1', __name__)
    
    @auth_bp.route('/signup', methods=['POST'])
    @monitor_endpoint('auth_signup')
    def signup():
        """Sign up new user"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'message': 'Request body is required'
                }), 400
            
            email = data.get('email', '').strip()
            password = data.get('password', '')
            name = data.get('name', '').strip()
            
            success, message, user_data = auth_service.signup_user(email, password, name)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': message,
                    'user': user_data
                }), 201
            else:
                return jsonify({
                    'success': False,
                    'message': message
                }), 400
                
        except Exception as e:
            logger.error("Signup endpoint error", error=e)
            return jsonify({
                'success': False,
                'message': 'Internal server error'
            }), 500
    
    @auth_bp.route('/signin', methods=['POST'])
    @monitor_endpoint('auth_signin')
    def signin():
        """Sign in existing user"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'message': 'Request body is required'
                }), 400
            
            email = data.get('email', '').strip()
            password = data.get('password', '')
            
            success, message, user_data = auth_service.signin_user(email, password)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': message,
                    **user_data
                }), 200
            else:
                status_code = 401 if 'not confirmed' in message.lower() else 400
                return jsonify({
                    'success': False,
                    'message': message
                }), status_code
                
        except Exception as e:
            logger.error("Signin endpoint error", error=e)
            return jsonify({
                'success': False,
                'message': 'Internal server error'
            }), 500
    
    @auth_bp.route('/signout', methods=['POST'])
    @monitor_endpoint('auth_signout')
    def signout():
        """Sign out user"""
        try:
            # Get token from Authorization header
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({
                    'success': False,
                    'message': 'Authorization header required'
                }), 401
            
            access_token = auth_header.split(' ')[1]
            success, message = auth_service.signout_user(access_token)
            
            return jsonify({
                'success': success,
                'message': message
            }), 200 if success else 400
            
        except Exception as e:
            logger.error("Signout endpoint error", error=e)
            return jsonify({
                'success': False,
                'message': 'Internal server error'
            }), 500
    
    @auth_bp.route('/user', methods=['GET'])
    @monitor_endpoint('auth_get_user')
    def get_user():
        """Get current user"""
        try:
            is_authenticated, user_data, error_message = auth_service.require_auth(request)
            
            if not is_authenticated:
                return jsonify({
                    'success': False,
                    'message': error_message
                }), 401
            
            # Get fresh profile data
            profile = auth_service.refresh_user_profile(user_data['user_id'])
            
            return jsonify({
                'success': True,
                'user': user_data,
                'profile': profile
            }), 200
            
        except Exception as e:
            logger.error("Get user endpoint error", error=e)
            return jsonify({
                'success': False,
                'message': 'Internal server error'
            }), 500
    
    @auth_bp.route('/validate', methods=['POST'])
    @monitor_endpoint('auth_validate')
    def validate_token():
        """Validate access token"""
        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({
                    'success': False,
                    'message': 'Authorization header required',
                    'valid': False
                }), 401
            
            access_token = auth_header.split(' ')[1]
            is_valid, user_data = auth_service.validate_token(access_token)
            
            if is_valid:
                return jsonify({
                    'success': True,
                    'valid': True,
                    'user': user_data
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'valid': False,
                    'message': 'Invalid token'
                }), 401
                
        except Exception as e:
            logger.error("Validate token endpoint error", error=e)
            return jsonify({
                'success': False,
                'valid': False,
                'message': 'Internal server error'
            }), 500
    
    return auth_bp