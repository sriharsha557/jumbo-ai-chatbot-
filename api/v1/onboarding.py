"""
Onboarding API Endpoints
Handles the complete onboarding flow for new users
"""

from flask import Blueprint, request, jsonify
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

def create_onboarding_blueprint(supabase_service, auth_service):
    """Create onboarding blueprint with dependency injection"""
    
    onboarding_bp = Blueprint('onboarding', __name__)
    
    def get_authenticated_user():
        """Helper function to get authenticated user from request"""
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        access_token = auth_header.split(' ')[1]
        return auth_service.get_current_user(access_token)
    
    @onboarding_bp.route('/status', methods=['GET'])
    def get_onboarding_status():
        """Check if user has completed onboarding"""
        try:
            # Get current user
            user = get_authenticated_user()
            if not user:
                return jsonify({
                    'success': False,
                    'message': 'Authentication required'
                }), 401
            
            # Get user profile
            profile = supabase_service.get_user_profile(user['user_id'])
            if not profile:
                return jsonify({
                    'success': False,
                    'message': 'Profile not found'
                }), 404
            
            onboarding_completed = profile.get('onboarding_completed', False)
            onboarding_data = profile.get('onboarding_data', {})
            
            # Determine current step based on completed data
            current_step = 1
            if onboarding_data.get('welcome_seen'):
                current_step = 2
            if onboarding_data.get('personal_info'):
                current_step = 3
            if onboarding_data.get('emotional_baseline'):
                current_step = 4
            if onboarding_data.get('support_style'):
                current_step = 5
            if onboarding_data.get('focus_areas'):
                current_step = 6
            if onboarding_data.get('checkin_preferences'):
                current_step = 7
            if onboarding_completed:
                current_step = 8  # Completed
            
            return jsonify({
                'success': True,
                'completed': onboarding_completed,
                'current_step': current_step,
                'total_steps': 7,
                'onboarding_data': onboarding_data
            })
            
        except Exception as e:
            logger.error(f"Get onboarding status error: {e}")
            return jsonify({
                'success': False,
                'message': 'Failed to get onboarding status'
            }), 500
    
    @onboarding_bp.route('/step', methods=['POST'])
    def save_onboarding_step():
        """Save data from a specific onboarding step"""
        try:
            # Get current user
            user = get_authenticated_user()
            if not user:
                return jsonify({
                    'success': False,
                    'message': 'Authentication required'
                }), 401
            
            data = request.json
            step = data.get('step')
            step_data = data.get('data', {})
            
            if not step or not isinstance(step, int) or step < 1 or step > 7:
                return jsonify({
                    'success': False,
                    'message': 'Invalid step number'
                }), 400
            
            # Get current profile
            profile = supabase_service.get_user_profile(user['user_id'])
            if not profile:
                return jsonify({
                    'success': False,
                    'message': 'Profile not found'
                }), 404
            
            # Get existing onboarding data
            onboarding_data = profile.get('onboarding_data', {})
            
            # Update onboarding data based on step
            step_mapping = {
                1: 'welcome_seen',
                2: 'personal_info',
                3: 'emotional_baseline',
                4: 'support_style',
                5: 'focus_areas',
                6: 'checkin_preferences',
                7: 'privacy_acknowledged'
            }
            
            step_key = step_mapping.get(step)
            if step_key:
                onboarding_data[step_key] = step_data
                onboarding_data[f'{step_key}_timestamp'] = 'now()'
            
            # Update profile with new onboarding data
            update_data = {'onboarding_data': onboarding_data}
            
            # Also update specific profile fields based on step
            if step == 2 and 'personal_info' in onboarding_data:
                personal_info = onboarding_data['personal_info']
                if 'display_name' in personal_info:
                    update_data['display_name'] = personal_info['display_name']
                if 'pronouns' in personal_info:
                    update_data['pronouns'] = personal_info['pronouns']
                if 'preferred_language' in personal_info:
                    update_data['preferred_language'] = personal_info['preferred_language']
            
            elif step == 3 and 'emotional_baseline' in onboarding_data:
                emotional_baseline = onboarding_data['emotional_baseline']
                if 'current_mood' in emotional_baseline:
                    update_data['current_mood'] = emotional_baseline['current_mood']
                if 'emotion_comfort_level' in emotional_baseline:
                    update_data['emotion_comfort_level'] = emotional_baseline['emotion_comfort_level']
            
            elif step == 4 and 'support_style' in onboarding_data:
                support_style = onboarding_data['support_style']
                if 'support_style' in support_style:
                    update_data['support_style'] = support_style['support_style']
                if 'communication_tone' in support_style:
                    update_data['communication_tone'] = support_style['communication_tone']
            
            elif step == 5 and 'focus_areas' in onboarding_data:
                focus_areas = onboarding_data['focus_areas']
                if 'selected_areas' in focus_areas:
                    update_data['focus_areas'] = focus_areas['selected_areas']
            
            elif step == 6 and 'checkin_preferences' in onboarding_data:
                checkin_prefs = onboarding_data['checkin_preferences']
                if 'frequency' in checkin_prefs:
                    update_data['checkin_frequency'] = checkin_prefs['frequency']
                if 'time' in checkin_prefs:
                    update_data['checkin_time'] = checkin_prefs['time']
                if 'custom_time' in checkin_prefs:
                    update_data['custom_checkin_time'] = checkin_prefs['custom_time']
            
            # Save to database
            success, message = supabase_service.update_user_profile(user['user_id'], update_data)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': f'Step {step} saved successfully',
                    'next_step': step + 1 if step < 7 else None
                })
            else:
                return jsonify({
                    'success': False,
                    'message': f'Failed to save step {step}: {message}'
                }), 500
                
        except Exception as e:
            logger.error(f"Save onboarding step error: {e}")
            return jsonify({
                'success': False,
                'message': 'Failed to save onboarding step'
            }), 500
    
    @onboarding_bp.route('/complete', methods=['POST'])
    def complete_onboarding():
        """Mark onboarding as completed"""
        try:
            # Get current user
            user = get_authenticated_user()
            if not user:
                return jsonify({
                    'success': False,
                    'message': 'Authentication required'
                }), 401
            
            data = request.json
            final_onboarding_data = data.get('onboarding_data', {})
            
            # Mark onboarding as completed
            update_data = {
                'onboarding_completed': True,
                'onboarding_data': final_onboarding_data
            }
            
            # Save to database
            success, message = supabase_service.update_user_profile(user['user_id'], update_data)
            
            if success:
                logger.info(f"User {user['user_id']} completed onboarding")
                return jsonify({
                    'success': True,
                    'message': 'Onboarding completed successfully',
                    'redirect_to': '/chat'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': f'Failed to complete onboarding: {message}'
                }), 500
                
        except Exception as e:
            logger.error(f"Complete onboarding error: {e}")
            return jsonify({
                'success': False,
                'message': 'Failed to complete onboarding'
            }), 500
    
    @onboarding_bp.route('/preferences', methods=['GET'])
    def get_user_preferences():
        """Get user preferences for personalizing AI responses"""
        try:
            # Get current user
            user = get_authenticated_user()
            if not user:
                return jsonify({
                    'success': False,
                    'message': 'Authentication required'
                }), 401
            
            # Get user profile
            profile = supabase_service.get_user_profile(user['user_id'])
            if not profile:
                return jsonify({
                    'success': False,
                    'message': 'Profile not found'
                }), 404
            
            # Extract preferences for AI personalization
            preferences = {
                'display_name': profile.get('display_name'),
                'pronouns': profile.get('pronouns'),
                'preferred_language': profile.get('preferred_language', 'en'),
                'current_mood': profile.get('current_mood'),
                'emotion_comfort_level': profile.get('emotion_comfort_level'),
                'support_style': profile.get('support_style'),
                'communication_tone': profile.get('communication_tone'),
                'focus_areas': profile.get('focus_areas', []),
                'checkin_frequency': profile.get('checkin_frequency'),
                'checkin_time': profile.get('checkin_time'),
                'onboarding_completed': profile.get('onboarding_completed', False)
            }
            
            return jsonify({
                'success': True,
                'preferences': preferences
            })
            
        except Exception as e:
            logger.error(f"Get user preferences error: {e}")
            return jsonify({
                'success': False,
                'message': 'Failed to get user preferences'
            }), 500
    
    @onboarding_bp.route('/reset', methods=['POST'])
    def reset_onboarding():
        """Reset onboarding for testing purposes"""
        try:
            # Get current user
            user = get_authenticated_user()
            if not user:
                return jsonify({
                    'success': False,
                    'message': 'Authentication required'
                }), 401
            
            # Reset onboarding data
            update_data = {
                'onboarding_completed': False,
                'onboarding_data': {},
                'display_name': None,
                'pronouns': None,
                'current_mood': None,
                'emotion_comfort_level': None,
                'support_style': None,
                'communication_tone': None,
                'focus_areas': [],
                'checkin_frequency': None,
                'checkin_time': None,
                'custom_checkin_time': None
            }
            
            # Save to database
            success, message = supabase_service.update_user_profile(user['user_id'], update_data)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': 'Onboarding reset successfully'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': f'Failed to reset onboarding: {message}'
                }), 500
                
        except Exception as e:
            logger.error(f"Reset onboarding error: {e}")
            return jsonify({
                'success': False,
                'message': 'Failed to reset onboarding'
            }), 500
    
    return onboarding_bp