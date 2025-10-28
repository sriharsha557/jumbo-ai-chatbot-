"""
Profile API v1 Endpoints
Handles user profile management
"""

from flask import Blueprint, request, jsonify
from typing import Dict, Any

from services.chat_service import ChatService
from services.auth_service import AuthService
from monitoring import monitor_endpoint, logger

def create_profile_blueprint(chat_service: ChatService, auth_service: AuthService) -> Blueprint:
    """Create profile blueprint with service injection"""
    
    profile_bp = Blueprint('profile_v1', __name__)
    
    @profile_bp.route('', methods=['GET'])
    @monitor_endpoint('profile_get')
    def get_profile():
        """Get user profile"""
        try:
            # Authenticate user
            is_authenticated, user_data, error_message = auth_service.require_auth(request)
            if not is_authenticated:
                return jsonify({
                    'success': False,
                    'message': error_message
                }), 401
            
            # Get fresh profile data
            profile = auth_service.refresh_user_profile(user_data['user_id'])
            
            if not profile:
                return jsonify({
                    'success': False,
                    'message': 'Profile not found'
                }), 404
            
            return jsonify({
                'success': True,
                'profile': profile
            }), 200
            
        except Exception as e:
            logger.error("Get profile endpoint error", error=e)
            return jsonify({
                'success': False,
                'message': 'Internal server error'
            }), 500
    
    @profile_bp.route('', methods=['PUT'])
    @monitor_endpoint('profile_update')
    def update_profile():
        """Update user profile"""
        try:
            # Authenticate user
            is_authenticated, user_data, error_message = auth_service.require_auth(request)
            if not is_authenticated:
                return jsonify({
                    'success': False,
                    'message': error_message
                }), 401
            
            # Get request data
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'message': 'Request body is required'
                }), 400
            
            # Validate allowed fields
            allowed_fields = ['preferred_name', 'language', 'avatar_url', 'metadata']
            update_data = {k: v for k, v in data.items() if k in allowed_fields}
            
            if not update_data:
                return jsonify({
                    'success': False,
                    'message': 'No valid fields to update'
                }), 400
            
            # Update profile
            success, message = chat_service.update_user_preference(user_data['user_id'], update_data)
            
            if success:
                # Get updated profile
                updated_profile = auth_service.refresh_user_profile(user_data['user_id'])
                
                return jsonify({
                    'success': True,
                    'message': message,
                    'profile': updated_profile
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': message
                }), 400
                
        except Exception as e:
            logger.error("Update profile endpoint error", error=e)
            return jsonify({
                'success': False,
                'message': 'Internal server error'
            }), 500
    
    @profile_bp.route('/stats', methods=['GET'])
    @monitor_endpoint('profile_stats')
    def get_user_stats():
        """Get user statistics"""
        try:
            # Authenticate user
            is_authenticated, user_data, error_message = auth_service.require_auth(request)
            if not is_authenticated:
                return jsonify({
                    'success': False,
                    'message': error_message
                }), 401
            
            # Get user statistics
            stats = chat_service.get_user_stats(user_data['user_id'])
            
            return jsonify({
                'success': True,
                'stats': stats
            }), 200
            
        except Exception as e:
            logger.error("Get user stats endpoint error", error=e)
            return jsonify({
                'success': False,
                'message': 'Internal server error'
            }), 500
    
    return profile_bp