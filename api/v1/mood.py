"""
Mood Tracking API Endpoints
Handles mood entry storage, retrieval, and trend analysis
"""

from flask import Blueprint, request, jsonify
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

def create_mood_blueprint(supabase_service, auth_service):
    """Create mood blueprint with dependency injection"""
    
    mood_bp = Blueprint('mood', __name__)
    
    def get_authenticated_user():
        """Helper function to get authenticated user from request"""
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        access_token = auth_header.split(' ')[1]
        return auth_service.get_current_user(access_token)
    
    def validate_mood_type(mood_type: str) -> bool:
        """Validate mood type against allowed values"""
        allowed_moods = ['very_sad', 'sad', 'neutral', 'happy', 'very_happy']
        return mood_type in allowed_moods
    
    def mood_type_to_numeric(mood_type: str) -> int:
        """Convert mood type to numeric value for trend analysis"""
        mood_mapping = {
            'very_sad': 1,
            'sad': 2,
            'neutral': 3,
            'happy': 4,
            'very_happy': 5
        }
        return mood_mapping.get(mood_type, 3)
    
    @mood_bp.route('/entry', methods=['POST', 'OPTIONS'])
    def create_mood_entry():
        """Create a new mood entry"""
        # Handle CORS preflight request
        if request.method == 'OPTIONS':
            return '', 200
            
        try:
            # Get current user
            user = get_authenticated_user()
            if not user:
                return jsonify({
                    'success': False,
                    'message': 'Authentication required'
                }), 401
            
            data = request.json
            mood_type = data.get('mood_type')
            timestamp = data.get('timestamp')
            notes = data.get('notes', '')
            session_id = data.get('session_id')
            
            # Validate required fields
            if not mood_type:
                return jsonify({
                    'success': False,
                    'message': 'mood_type is required'
                }), 400
            
            if not validate_mood_type(mood_type):
                return jsonify({
                    'success': False,
                    'message': 'Invalid mood_type. Must be one of: very_sad, sad, neutral, happy, very_happy'
                }), 400
            
            # Parse timestamp or use current time
            if timestamp:
                try:
                    parsed_timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                except ValueError:
                    return jsonify({
                        'success': False,
                        'message': 'Invalid timestamp format. Use ISO format.'
                    }), 400
            else:
                parsed_timestamp = datetime.utcnow()
            
            # Create mood entry data
            mood_entry = {
                'user_id': user['user_id'],
                'mood_type': mood_type,
                'mood_numeric': mood_type_to_numeric(mood_type),
                'timestamp': parsed_timestamp.isoformat(),
                'notes': notes,
                'session_id': session_id,
                'created_at': datetime.utcnow().isoformat()
            }
            
            # Save to database
            try:
                # Insert into mood_entries table
                result = supabase_service.client.table('mood_entries').insert(mood_entry).execute()
                
                if result.data:
                    created_entry = result.data[0]
                    
                    # Update user profile with latest mood
                    profile_update = {
                        'last_mood_type': mood_type,
                        'last_mood_timestamp': parsed_timestamp.isoformat(),
                        'mood_tracking_enabled': True
                    }
                    
                    # Try to update profile, but don't fail if it doesn't exist
                    try:
                        supabase_service.update_user_profile(user['user_id'], profile_update)
                    except Exception as profile_error:
                        logger.warning(f"Failed to update profile with mood data: {profile_error}")
                    
                    logger.info(f"Mood entry created for user {user['user_id']}: {mood_type}")
                    
                    return jsonify({
                        'success': True,
                        'message': 'Mood entry created successfully',
                        'mood_entry': {
                            'id': created_entry['id'],
                            'mood_type': created_entry['mood_type'],
                            'timestamp': created_entry['timestamp'],
                            'notes': created_entry.get('notes', ''),
                            'session_id': created_entry.get('session_id')
                        }
                    })
                else:
                    return jsonify({
                        'success': False,
                        'message': 'Failed to create mood entry'
                    }), 500
                    
            except Exception as db_error:
                logger.error(f"Database error creating mood entry: {db_error}")
                return jsonify({
                    'success': False,
                    'message': 'Database error occurred'
                }), 500
                
        except Exception as e:
            logger.error(f"Create mood entry error: {e}")
            return jsonify({
                'success': False,
                'message': 'Failed to create mood entry'
            }), 500
    
    @mood_bp.route('/history', methods=['GET', 'OPTIONS'])
    def get_mood_history():
        """Get user's mood history with optional filtering"""
        # Handle CORS preflight request
        if request.method == 'OPTIONS':
            return '', 200
            
        try:
            # Get current user
            user = get_authenticated_user()
            if not user:
                return jsonify({
                    'success': False,
                    'message': 'Authentication required'
                }), 401
            
            # Get query parameters
            days = request.args.get('days', 7, type=int)
            limit = request.args.get('limit', 50, type=int)
            
            # Validate parameters
            if days < 1 or days > 365:
                days = 7
            if limit < 1 or limit > 100:
                limit = 50
            
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            try:
                # Query mood entries
                result = supabase_service.client.table('mood_entries')\
                    .select('*')\
                    .eq('user_id', user['user_id'])\
                    .gte('timestamp', start_date.isoformat())\
                    .lte('timestamp', end_date.isoformat())\
                    .order('timestamp', desc=True)\
                    .limit(limit)\
                    .execute()
                
                mood_entries = result.data or []
                
                # Calculate trend summary
                if mood_entries:
                    mood_values = [entry['mood_numeric'] for entry in mood_entries if entry.get('mood_numeric')]
                    average_mood = sum(mood_values) / len(mood_values) if mood_values else 3
                    
                    # Count mood distribution
                    mood_distribution = {}
                    for entry in mood_entries:
                        mood_type = entry['mood_type']
                        mood_distribution[mood_type] = mood_distribution.get(mood_type, 0) + 1
                    
                    trend_summary = {
                        'average_mood': round(average_mood, 2),
                        'mood_distribution': mood_distribution,
                        'total_entries': len(mood_entries),
                        'date_range': {
                            'start': start_date.isoformat(),
                            'end': end_date.isoformat(),
                            'days': days
                        }
                    }
                else:
                    trend_summary = {
                        'average_mood': 3.0,
                        'mood_distribution': {},
                        'total_entries': 0,
                        'date_range': {
                            'start': start_date.isoformat(),
                            'end': end_date.isoformat(),
                            'days': days
                        }
                    }
                
                # Format mood entries for response
                formatted_entries = []
                for entry in mood_entries:
                    formatted_entries.append({
                        'id': entry['id'],
                        'mood_type': entry['mood_type'],
                        'mood_numeric': entry.get('mood_numeric', mood_type_to_numeric(entry['mood_type'])),
                        'timestamp': entry['timestamp'],
                        'notes': entry.get('notes', ''),
                        'session_id': entry.get('session_id'),
                        'created_at': entry.get('created_at')
                    })
                
                return jsonify({
                    'success': True,
                    'mood_history': formatted_entries,
                    'trend_summary': trend_summary
                })
                
            except Exception as db_error:
                logger.error(f"Database error getting mood history: {db_error}")
                return jsonify({
                    'success': False,
                    'message': 'Database error occurred'
                }), 500
                
        except Exception as e:
            logger.error(f"Get mood history error: {e}")
            return jsonify({
                'success': False,
                'message': 'Failed to get mood history'
            }), 500
    
    @mood_bp.route('/latest', methods=['GET', 'OPTIONS'])
    def get_latest_mood():
        """Get user's most recent mood entry"""
        # Handle CORS preflight request
        if request.method == 'OPTIONS':
            return '', 200
            
        try:
            # Get current user
            user = get_authenticated_user()
            if not user:
                return jsonify({
                    'success': False,
                    'message': 'Authentication required'
                }), 401
            
            try:
                # Query latest mood entry
                result = supabase_service.client.table('mood_entries')\
                    .select('*')\
                    .eq('user_id', user['user_id'])\
                    .order('timestamp', desc=True)\
                    .limit(1)\
                    .execute()
                
                if result.data and len(result.data) > 0:
                    latest_entry = result.data[0]
                    
                    return jsonify({
                        'success': True,
                        'latest_mood': {
                            'id': latest_entry['id'],
                            'mood_type': latest_entry['mood_type'],
                            'mood_numeric': latest_entry.get('mood_numeric', mood_type_to_numeric(latest_entry['mood_type'])),
                            'timestamp': latest_entry['timestamp'],
                            'notes': latest_entry.get('notes', ''),
                            'session_id': latest_entry.get('session_id'),
                            'created_at': latest_entry.get('created_at')
                        }
                    })
                else:
                    return jsonify({
                        'success': True,
                        'latest_mood': None,
                        'message': 'No mood entries found'
                    })
                    
            except Exception as db_error:
                logger.error(f"Database error getting latest mood: {db_error}")
                return jsonify({
                    'success': False,
                    'message': 'Database error occurred'
                }), 500
                
        except Exception as e:
            logger.error(f"Get latest mood error: {e}")
            return jsonify({
                'success': False,
                'message': 'Failed to get latest mood'
            }), 500
    
    @mood_bp.route('/trends', methods=['GET', 'OPTIONS'])
    def get_mood_trends():
        """Get mood trends and analytics"""
        # Handle CORS preflight request
        if request.method == 'OPTIONS':
            return '', 200
            
        try:
            # Get current user
            user = get_authenticated_user()
            if not user:
                return jsonify({
                    'success': False,
                    'message': 'Authentication required'
                }), 401
            
            # Get query parameters
            days = request.args.get('days', 30, type=int)
            
            # Validate parameters
            if days < 1 or days > 365:
                days = 30
            
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            try:
                # Query mood entries for trend analysis
                result = supabase_service.client.table('mood_entries')\
                    .select('mood_type, mood_numeric, timestamp')\
                    .eq('user_id', user['user_id'])\
                    .gte('timestamp', start_date.isoformat())\
                    .lte('timestamp', end_date.isoformat())\
                    .order('timestamp', desc=False)\
                    .execute()
                
                mood_entries = result.data or []
                
                if not mood_entries:
                    return jsonify({
                        'success': True,
                        'trends': {
                            'daily_averages': [],
                            'weekly_summary': {},
                            'mood_patterns': {},
                            'insights': []
                        }
                    })
                
                # Group by day for daily averages
                daily_moods = {}
                for entry in mood_entries:
                    entry_date = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00')).date()
                    date_str = entry_date.isoformat()
                    
                    if date_str not in daily_moods:
                        daily_moods[date_str] = []
                    daily_moods[date_str].append(entry['mood_numeric'])
                
                # Calculate daily averages
                daily_averages = []
                for date_str, moods in daily_moods.items():
                    avg_mood = sum(moods) / len(moods)
                    daily_averages.append({
                        'date': date_str,
                        'average_mood': round(avg_mood, 2),
                        'entry_count': len(moods)
                    })
                
                # Sort by date
                daily_averages.sort(key=lambda x: x['date'])
                
                # Calculate weekly summary (last 7 days)
                recent_entries = [entry for entry in mood_entries 
                                if datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00')) >= (end_date - timedelta(days=7))]
                
                if recent_entries:
                    recent_moods = [entry['mood_numeric'] for entry in recent_entries]
                    weekly_avg = sum(recent_moods) / len(recent_moods)
                    
                    weekly_summary = {
                        'average_mood': round(weekly_avg, 2),
                        'total_entries': len(recent_entries),
                        'mood_range': {
                            'min': min(recent_moods),
                            'max': max(recent_moods)
                        }
                    }
                else:
                    weekly_summary = {
                        'average_mood': 3.0,
                        'total_entries': 0,
                        'mood_range': {'min': 3, 'max': 3}
                    }
                
                # Analyze mood patterns
                mood_counts = {}
                for entry in mood_entries:
                    mood_type = entry['mood_type']
                    mood_counts[mood_type] = mood_counts.get(mood_type, 0) + 1
                
                # Generate insights
                insights = []
                if len(mood_entries) >= 7:
                    all_moods = [entry['mood_numeric'] for entry in mood_entries]
                    avg_mood = sum(all_moods) / len(all_moods)
                    
                    if avg_mood >= 4:
                        insights.append("You've been feeling quite positive lately! 😊")
                    elif avg_mood <= 2:
                        insights.append("It looks like you've been having some tough days. Remember, it's okay to not be okay. 💛")
                    else:
                        insights.append("Your mood has been fairly balanced recently.")
                    
                    # Check for consistency
                    mood_variance = sum((mood - avg_mood) ** 2 for mood in all_moods) / len(all_moods)
                    if mood_variance < 0.5:
                        insights.append("Your mood has been quite consistent.")
                    elif mood_variance > 2:
                        insights.append("You've experienced a wide range of emotions recently.")
                
                return jsonify({
                    'success': True,
                    'trends': {
                        'daily_averages': daily_averages,
                        'weekly_summary': weekly_summary,
                        'mood_patterns': mood_counts,
                        'insights': insights,
                        'analysis_period': {
                            'start_date': start_date.isoformat(),
                            'end_date': end_date.isoformat(),
                            'days': days,
                            'total_entries': len(mood_entries)
                        }
                    }
                })
                
            except Exception as db_error:
                logger.error(f"Database error getting mood trends: {db_error}")
                return jsonify({
                    'success': False,
                    'message': 'Database error occurred'
                }), 500
                
        except Exception as e:
            logger.error(f"Get mood trends error: {e}")
            return jsonify({
                'success': False,
                'message': 'Failed to get mood trends'
            }), 500
    
    @mood_bp.route('/delete/<int:entry_id>', methods=['DELETE', 'OPTIONS'])
    def delete_mood_entry(entry_id):
        """Delete a specific mood entry"""
        # Handle CORS preflight request
        if request.method == 'OPTIONS':
            return '', 200
            
        try:
            # Get current user
            user = get_authenticated_user()
            if not user:
                return jsonify({
                    'success': False,
                    'message': 'Authentication required'
                }), 401
            
            try:
                # Delete mood entry (only if it belongs to the user)
                result = supabase_service.client.table('mood_entries')\
                    .delete()\
                    .eq('id', entry_id)\
                    .eq('user_id', user['user_id'])\
                    .execute()
                
                if result.data:
                    logger.info(f"Mood entry {entry_id} deleted by user {user['user_id']}")
                    return jsonify({
                        'success': True,
                        'message': 'Mood entry deleted successfully'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'message': 'Mood entry not found or access denied'
                    }), 404
                    
            except Exception as db_error:
                logger.error(f"Database error deleting mood entry: {db_error}")
                return jsonify({
                    'success': False,
                    'message': 'Database error occurred'
                }), 500
                
        except Exception as e:
            logger.error(f"Delete mood entry error: {e}")
            return jsonify({
                'success': False,
                'message': 'Failed to delete mood entry'
            }), 500
    
    return mood_bp