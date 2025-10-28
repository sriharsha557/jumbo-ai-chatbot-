"""
Memories API v1 Endpoints
Handles user memories and mood tracking
"""

from flask import Blueprint, request, jsonify
from typing import Dict, Any

from services.chat_service import ChatService
from services.auth_service import AuthService
from monitoring import monitor_endpoint, logger

def create_memories_blueprint(chat_service: ChatService, auth_service: AuthService) -> Blueprint:
    """Create memories blueprint with service injection"""
    
    memories_bp = Blueprint('memories_v1', __name__)
    
    @memories_bp.route('', methods=['GET'])
    @monitor_endpoint('memories_get')
    def get_memories():
        """Get user memories"""
        try:
            # Authenticate user
            is_authenticated, user_data, error_message = auth_service.require_auth(request)
            if not is_authenticated:
                return jsonify({
                    'success': False,
                    'message': error_message
                }), 401
            
            # Get query parameters
            limit = request.args.get('limit', 50, type=int)
            limit = min(max(limit, 1), 200)  # Clamp between 1 and 200
            
            memory_type = request.args.get('type')  # Optional filter by type
            
            # Get memories
            memories = chat_service.get_user_memories(user_data['user_id'], limit)
            
            # Filter by type if specified
            if memory_type:
                memories = [m for m in memories if m.get('memory_type') == memory_type]
            
            return jsonify({
                'success': True,
                'memories': memories,
                'total': len(memories)
            }), 200
            
        except Exception as e:
            logger.error("Get memories endpoint error", error=e)
            return jsonify({
                'success': False,
                'message': 'Internal server error'
            }), 500
    
    @memories_bp.route('/search', methods=['POST'])
    @monitor_endpoint('memories_search')
    def search_memories():
        """Search user memories"""
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
            
            search_terms = data.get('search_terms', [])
            if not search_terms:
                return jsonify({
                    'success': False,
                    'message': 'Search terms are required'
                }), 400
            
            limit = data.get('limit', 20)
            limit = min(max(limit, 1), 100)  # Clamp between 1 and 100
            
            # Search memories (this would need to be implemented in supabase_service)
            # For now, return empty results
            memories = []
            
            return jsonify({
                'success': True,
                'memories': memories,
                'search_terms': search_terms,
                'total': len(memories)
            }), 200
            
        except Exception as e:
            logger.error("Search memories endpoint error", error=e)
            return jsonify({
                'success': False,
                'message': 'Internal server error'
            }), 500
    
    @memories_bp.route('/mood/history', methods=['GET'])
    @monitor_endpoint('mood_history')
    def get_mood_history():
        """Get user mood history"""
        try:
            # Authenticate user
            is_authenticated, user_data, error_message = auth_service.require_auth(request)
            if not is_authenticated:
                return jsonify({
                    'success': False,
                    'message': error_message
                }), 401
            
            # Get query parameters
            days = request.args.get('days', 30, type=int)
            days = min(max(days, 1), 365)  # Clamp between 1 and 365 days
            
            # Get mood history
            mood_history = chat_service.get_mood_history(user_data['user_id'], days)
            
            return jsonify({
                'success': True,
                'mood_history': mood_history,
                'days': days,
                'total': len(mood_history)
            }), 200
            
        except Exception as e:
            logger.error("Get mood history endpoint error", error=e)
            return jsonify({
                'success': False,
                'message': 'Internal server error'
            }), 500
    
    @memories_bp.route('/mood/summary', methods=['GET'])
    @monitor_endpoint('mood_summary')
    def get_mood_summary():
        """Get mood summary and trends"""
        try:
            # Authenticate user
            is_authenticated, user_data, error_message = auth_service.require_auth(request)
            if not is_authenticated:
                return jsonify({
                    'success': False,
                    'message': error_message
                }), 401
            
            # Get mood history
            mood_history = chat_service.get_mood_history(user_data['user_id'], days=30)
            
            # Calculate mood summary
            mood_counts = {}
            total_entries = len(mood_history)
            
            for entry in mood_history:
                mood = entry.get('mood', 'neutral')
                mood_counts[mood] = mood_counts.get(mood, 0) + 1
            
            # Calculate percentages
            mood_percentages = {}
            for mood, count in mood_counts.items():
                mood_percentages[mood] = round((count / max(total_entries, 1)) * 100, 1)
            
            # Get most common mood
            most_common_mood = max(mood_counts, key=mood_counts.get) if mood_counts else 'neutral'
            
            return jsonify({
                'success': True,
                'summary': {
                    'total_entries': total_entries,
                    'most_common_mood': most_common_mood,
                    'mood_counts': mood_counts,
                    'mood_percentages': mood_percentages,
                    'period_days': 30
                }
            }), 200
            
        except Exception as e:
            logger.error("Get mood summary endpoint error", error=e)
            return jsonify({
                'success': False,
                'message': 'Internal server error'
            }), 500
    
    return memories_bp