"""
Chat API v1 Endpoints
Handles chat interactions with proper error handling and monitoring
"""

from flask import Blueprint, request, jsonify
from typing import Dict, Any

from services.chat_service import ChatService
from services.auth_service import AuthService
from monitoring import monitor_endpoint, logger

def create_chat_blueprint(chat_service: ChatService, auth_service: AuthService) -> Blueprint:
    """Create chat blueprint with service injection"""
    
    chat_bp = Blueprint('chat_v1', __name__)
    
    @chat_bp.route('/message', methods=['POST'])
    @monitor_endpoint('chat_message')
    def send_message():
        """Send chat message"""
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
            
            user_message = data.get('message', '').strip()
            if not user_message:
                return jsonify({
                    'success': False,
                    'message': 'Message cannot be empty'
                }), 400
            
            conversation_context = data.get('conversation_context', [])
            
            # Process message through chat service
            response, metadata = chat_service.process_message(
                user_data['user_id'],
                user_message,
                conversation_context
            )
            
            return jsonify({
                'success': True,
                'message': user_message,
                'response': response,
                'metadata': {
                    'mood': metadata.get('mood', 'neutral'),
                    'mood_confidence': metadata.get('mood_confidence', 0.0),
                    'language': metadata.get('language', 'en'),
                    'used_llm': metadata.get('used_llm', False),
                    'scenario': metadata.get('scenario', 'general'),
                    'response_type': metadata.get('response_type', 'text'),
                    'context': metadata.get('context'),
                    'emotional_intensity': metadata.get('emotional_intensity'),
                    'needs_empathy': metadata.get('needs_empathy'),
                    'conversation_direction': metadata.get('conversation_direction')
                }
            }), 200
            
        except ValueError as e:
            logger.warning("Chat message validation error", error=e)
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400
            
        except Exception as e:
            logger.error("Chat message endpoint error", error=e)
            return jsonify({
                'success': False,
                'message': 'Internal server error'
            }), 500
    
    @chat_bp.route('/history', methods=['GET'])
    @monitor_endpoint('chat_history')
    def get_conversation_history():
        """Get conversation history"""
        try:
            # Authenticate user
            is_authenticated, user_data, error_message = auth_service.require_auth(request)
            if not is_authenticated:
                return jsonify({
                    'success': False,
                    'message': error_message
                }), 401
            
            # Get query parameters
            limit = request.args.get('limit', 20, type=int)
            limit = min(max(limit, 1), 100)  # Clamp between 1 and 100
            
            # Get conversation history
            conversations = chat_service.get_conversation_history(user_data['user_id'], limit)
            
            return jsonify({
                'success': True,
                'conversations': conversations,
                'total': len(conversations)
            }), 200
            
        except Exception as e:
            logger.error("Get conversation history endpoint error", error=e)
            return jsonify({
                'success': False,
                'message': 'Internal server error'
            }), 500
    
    @chat_bp.route('/context', methods=['GET'])
    @monitor_endpoint('chat_context')
    def get_chat_context():
        """Get chat context for user (recent conversations, preferences, etc.)"""
        try:
            # Authenticate user
            is_authenticated, user_data, error_message = auth_service.require_auth(request)
            if not is_authenticated:
                return jsonify({
                    'success': False,
                    'message': error_message
                }), 401
            
            user_id = user_data['user_id']
            
            # Get recent conversations for context
            recent_conversations = chat_service.get_conversation_history(user_id, limit=5)
            
            # Get user profile
            profile = auth_service.refresh_user_profile(user_id)
            
            # Get recent memories
            memories = chat_service.get_user_memories(user_id, limit=10)
            
            return jsonify({
                'success': True,
                'context': {
                    'recent_conversations': recent_conversations,
                    'profile': profile,
                    'recent_memories': memories,
                    'user_id': user_id
                }
            }), 200
            
        except Exception as e:
            logger.error("Get chat context endpoint error", error=e)
            return jsonify({
                'success': False,
                'message': 'Internal server error'
            }), 500
    
    return chat_bp