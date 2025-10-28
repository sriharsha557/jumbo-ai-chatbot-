"""
Flask API Server for Jumbo Chatbot with Supabase Integration
Handles authentication and data storage via Supabase
Run: python flask_api_supabase.py
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import sys
import os
import traceback
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add your project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from supabase_service import SupabaseService
from chatbot import JumboChatbot
from language_utils import Language

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=['http://localhost:3000'])  # Enable CORS with credentials

# Global instances
supabase_service = None
chatbot = None

def initialize_services():
    """Initialize Supabase and chatbot services"""
    global supabase_service, chatbot
    
    try:
        # Initialize Supabase
        supabase_service = SupabaseService()
        logger.info("✓ Supabase service initialized")
        
        # Initialize chatbot
        chatbot = JumboChatbot()
        logger.info("✓ Jumbo Chatbot initialized")
        
        return True
    except Exception as e:
        logger.error(f"✗ Failed to initialize services: {e}")
        traceback.print_exc()
        return False

# ==================== HEALTH CHECK ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Check if API is running"""
    return jsonify({
        'status': 'ok',
        'message': 'Jumbo API with Supabase is running',
        'supabase_initialized': supabase_service is not None,
        'chatbot_initialized': chatbot is not None
    })

# ==================== AUTHENTICATION ====================

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """Sign up new user with Supabase Auth"""
    try:
        data = request.json
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        name = data.get('name', '').strip()
        language = data.get('language', 'en')
        
        if not email or not password or not name:
            return jsonify({
                'success': False,
                'message': 'Email, password, and name are required'
            }), 400
        
        if len(password) < 6:
            return jsonify({
                'success': False,
                'message': 'Password must be at least 6 characters'
            }), 400
        
        # Sign up with Supabase
        success, message, user_data = supabase_service.sign_up(
            email, 
            password, 
            {'name': name, 'language': language}
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'user': user_data
            })
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
    
    except Exception as e:
        logger.error(f"Signup error: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Signup error: {str(e)}'
        }), 500

@app.route('/api/auth/signin', methods=['POST'])
def signin():
    """Sign in existing user"""
    try:
        data = request.json
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({
                'success': False,
                'message': 'Email and password are required'
            }), 400
        
        success, message, user_data = supabase_service.sign_in(email, password)
        
        if success:
            # Get user profile
            profile = supabase_service.get_user_profile(user_data['user_id'])
            
            return jsonify({
                'success': True,
                'message': message,
                'user': user_data,
                'profile': profile
            })
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 401
    
    except Exception as e:
        logger.error(f"Signin error: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Signin error: {str(e)}'
        }), 500

@app.route('/api/auth/signout', methods=['POST'])
def signout():
    """Sign out current user"""
    try:
        success, message = supabase_service.sign_out()
        
        return jsonify({
            'success': success,
            'message': message
        })
    
    except Exception as e:
        logger.error(f"Signout error: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/auth/user', methods=['GET'])
def get_current_user():
    """Get current authenticated user"""
    try:
        user = supabase_service.get_current_user()
        
        if user:
            profile = supabase_service.get_user_profile(user['user_id'])
            return jsonify({
                'success': True,
                'user': user,
                'profile': profile
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No user logged in'
            }), 401
    
    except Exception as e:
        logger.error(f"Get user error: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# ==================== USER PROFILE ====================

@app.route('/api/profile', methods=['GET'])
def get_profile():
    """Get user profile"""
    try:
        user = supabase_service.get_current_user()
        if not user:
            return jsonify({'success': False, 'message': 'Not authenticated'}), 401
        
        profile = supabase_service.get_user_profile(user['user_id'])
        
        return jsonify({
            'success': True,
            'profile': profile
        })
    
    except Exception as e:
        logger.error(f"Get profile error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/profile', methods=['PUT'])
def update_profile():
    """Update user profile"""
    try:
        user = supabase_service.get_current_user()
        if not user:
            return jsonify({'success': False, 'message': 'Not authenticated'}), 401
        
        data = request.json
        success, message = supabase_service.update_user_profile(user['user_id'], data)
        
        return jsonify({
            'success': success,
            'message': message
        })
    
    except Exception as e:
        logger.error(f"Update profile error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== CHAT ====================

@app.route('/api/chat/message', methods=['POST'])
def send_message():
    """Send message with Supabase storage"""
    try:
        # Get user from Supabase session or request
        data = request.json
        user = None
        
        # Try to get user from Authorization header (Supabase JWT)
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                # Verify Supabase JWT token
                user_data = supabase_service.supabase.auth.get_user(token)
                if user_data.user:
                    user = {
                        'user_id': user_data.user.id,
                        'email': user_data.user.email
                    }
            except Exception as e:
                logger.warning(f"JWT verification failed: {e}")
        
        # Fallback: get user from request data
        if not user:
            user_from_request = data.get('user')
            if user_from_request:
                user = {
                    'user_id': user_from_request.get('id'),
                    'email': user_from_request.get('email'),
                    'name': user_from_request.get('name')
                }
        
        if not user:
            return jsonify({'success': False, 'message': 'Authentication required'}), 401
        
        user_message = data.get('message', '').strip()
        conversation_history = data.get('conversation_context', [])
        provided_emotion = data.get('emotion')  # Optional emotion from frontend
        
        if not user_message:
            return jsonify({
                'success': False,
                'message': 'Message cannot be empty'
            }), 400
        
        # Get user profile for context
        profile = supabase_service.get_user_profile(user['user_id'])
        
        # Set the Supabase user in chatbot with preferred name
        user_language = profile.get('language', 'en') if profile else 'en'
        preferred_name = profile.get('preferred_name') if profile else None
        chatbot.set_supabase_user(user, user_language, preferred_name)
        
        # Store supabase service reference for name handling
        chatbot._supabase_service = supabase_service
        
        # Check if this is a first-time user without preferred name
        is_first_time = not preferred_name and len(conversation_history) == 0
        
        # If it's their first message and no preferred name, ask for it
        if is_first_time and user_message.lower().strip() not in ['hi', 'hello', 'hey']:
            # Use emotion detection for first-time users too
            from services.emotion_service import get_emotion_detector
            emotion_detector = get_emotion_detector()
            emotion_result = emotion_detector.detect_emotion(user_message)
            
            greeting = chatbot.get_personalized_greeting(is_first_time=True)
            return jsonify({
                'success': True,
                'message': user_message,
                'response': greeting,
                'metadata': {
                    'response_type': 'name_request',
                    'mood': 'friendly',
                    'language': user_language,
                    'emotion': emotion_result['emotion'],
                    'emotion_confidence': emotion_result['confidence'],
                    'emotion_method': emotion_result['method']
                }
            })
        
        # Process message with automatic emotion detection and personality enhancement
        try:
            # Import services
            from services.emotion_service import get_emotion_detector
            from services.personality_service import PersonalityService
            
            # Detect emotion automatically (unless provided by frontend)
            if provided_emotion:
                detected_emotion = provided_emotion
                emotion_confidence = 1.0
                emotion_method = "frontend_provided"
            else:
                emotion_detector = get_emotion_detector()
                emotion_result = emotion_detector.detect_emotion(user_message)
                detected_emotion = emotion_result['emotion']
                emotion_confidence = emotion_result['confidence']
                emotion_method = emotion_result['method']
            
            logger.info(f"Processing message with emotion: {detected_emotion} (confidence: {emotion_confidence:.2f})")
            
            # Process with chatbot
            response, metadata = chatbot.process_message(
                user_message,
                conversation_history=conversation_history,
                memory_context={
                    'user_name': user.get('name', user.get('email', 'User')),
                    'language': user_language,
                    'previous_conversations': conversation_history,
                    'user_email': user.get('email'),
                    'preferred_name': preferred_name
                }
            )
            
            # Enhance response with personality based on detected emotion
            personality_service = PersonalityService()
            user_display_name = preferred_name or user.get('name', 'friend')
            response = personality_service.enhance_response_with_personality(
                response, detected_emotion, user_display_name
            )
            
            # Final polish for quality assurance
            from services.response_polisher import get_response_polisher
            response_polisher = get_response_polisher()
            response = response_polisher.polish_response(
                response, detected_emotion, user_display_name
            )
            
            # Add emotion and personality metadata
            personality_metadata = personality_service.get_emotion_metadata(detected_emotion)
            metadata.update(personality_metadata)
            metadata.update({
                'emotion_confidence': emotion_confidence,
                'emotion_method': emotion_method,
                'auto_emotion_detection': True,
                'response_polished': True
            })
            
        except Exception as e:
            logger.warning(f"Enhanced processing failed, using fallback: {e}")
            # Fallback for simpler chatbot interface
            response, metadata = chatbot.process_message(user_message)
            detected_emotion = "neutral"
            emotion_confidence = 0.5
            emotion_method = "fallback"
        
        # Save conversation to Supabase
        conversation_data = {
            'message': user_message,
            'response': response,
            'metadata': metadata
        }
        
        success, save_message, conversation_id = supabase_service.save_conversation(
            user['user_id'], 
            conversation_data
        )
        
        if not success:
            logger.warning(f"Failed to save conversation: {save_message}")
        
        return jsonify({
            'success': True,
            'message': user_message,
            'response': response,
            'conversation_id': conversation_id if success else None,
            'metadata': {
                'mood': metadata.get('mood', 'neutral'),
                'mood_confidence': metadata.get('mood_confidence', 0.0),
                'language': metadata.get('language', 'en'),
                'used_llm': metadata.get('used_llm', False),
                'scenario': metadata.get('scenario', 'general'),
                'response_type': metadata.get('response_type', 'text'),
                'emotion': detected_emotion,
                'emotion_confidence': emotion_confidence,
                'emotion_method': emotion_method,
                'auto_emotion_detection': metadata.get('auto_emotion_detection', False),
                'personality_enhanced': metadata.get('personality_enhanced', True),
                'empathy_starter': metadata.get('empathy_starter', ''),
                'tone_markers': metadata.get('tone_markers', [])
            }
        })
    
    except Exception as e:
        logger.error(f"Chat error: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error processing message: {str(e)}'
        }), 500

@app.route('/api/chat/history', methods=['GET'])
def get_conversation_history():
    """Get conversation history from Supabase"""
    try:
        user = supabase_service.get_current_user()
        if not user:
            return jsonify({'success': False, 'message': 'Not authenticated'}), 401
        
        limit = request.args.get('limit', 20, type=int)
        conversations = supabase_service.get_user_conversations(user['user_id'], limit)
        
        return jsonify({
            'success': True,
            'conversations': conversations,
            'total': len(conversations)
        })
    
    except Exception as e:
        logger.error(f"History error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== MEMORIES ====================

@app.route('/api/memories', methods=['GET'])
def get_memories():
    """Get user memories"""
    try:
        user = supabase_service.get_current_user()
        if not user:
            return jsonify({'success': False, 'message': 'Not authenticated'}), 401
        
        memory_type = request.args.get('type')
        memories = supabase_service.get_user_memories(user['user_id'], memory_type)
        
        return jsonify({
            'success': True,
            'memories': memories
        })
    
    except Exception as e:
        logger.error(f"Get memories error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/memories', methods=['POST'])
def save_memory():
    """Save user memory"""
    try:
        user = supabase_service.get_current_user()
        if not user:
            return jsonify({'success': False, 'message': 'Not authenticated'}), 401
        
        data = request.json
        memory_type = data.get('memory_type', 'preference')
        memory_data = data.get('data', {})
        
        success, message = supabase_service.save_user_memory(
            user['user_id'], 
            memory_type, 
            memory_data
        )
        
        return jsonify({
            'success': success,
            'message': message
        })
    
    except Exception as e:
        logger.error(f"Save memory error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== MOOD TRACKING ====================

@app.route('/api/mood/history', methods=['GET'])
def get_mood_history():
    """Get user's mood history"""
    try:
        user = supabase_service.get_current_user()
        if not user:
            return jsonify({'success': False, 'message': 'Not authenticated'}), 401
        
        limit = request.args.get('limit', 30, type=int)
        mood_history = supabase_service.get_mood_history(user['user_id'], limit)
        
        return jsonify({
            'success': True,
            'mood_history': mood_history
        })
    
    except Exception as e:
        logger.error(f"Get mood history error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== STATISTICS ====================

@app.route('/api/stats', methods=['GET'])
def get_user_stats():
    """Get user statistics"""
    try:
        user = supabase_service.get_current_user()
        if not user:
            return jsonify({'success': False, 'message': 'Not authenticated'}), 401
        
        stats = supabase_service.get_user_stats(user['user_id'])
        
        return jsonify({
            'success': True,
            'stats': stats
        })
    
    except Exception as e:
        logger.error(f"Get stats error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== ONBOARDING ====================

@app.route('/api/onboarding/status', methods=['GET'])
def get_onboarding_status():
    """Check if user has completed onboarding"""
    try:
        user = supabase_service.get_current_user()
        if not user:
            return jsonify({'success': False, 'message': 'Not authenticated'}), 401
        
        profile = supabase_service.get_user_profile(user['user_id'])
        if not profile:
            return jsonify({'success': False, 'message': 'Profile not found'}), 404
        
        onboarding_completed = profile.get('onboarding_completed', False)
        onboarding_data = profile.get('onboarding_data', {})
        
        # Determine current step
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
            current_step = 8
        
        return jsonify({
            'success': True,
            'completed': onboarding_completed,
            'current_step': current_step,
            'total_steps': 7,
            'onboarding_data': onboarding_data
        })
    
    except Exception as e:
        logger.error(f"Get onboarding status error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/onboarding/step', methods=['POST'])
def save_onboarding_step():
    """Save data from a specific onboarding step"""
    try:
        user = supabase_service.get_current_user()
        if not user:
            return jsonify({'success': False, 'message': 'Not authenticated'}), 401
        
        data = request.json
        step = data.get('step')
        step_data = data.get('data', {})
        
        if not step or not isinstance(step, int) or step < 1 or step > 7:
            return jsonify({'success': False, 'message': 'Invalid step number'}), 400
        
        profile = supabase_service.get_user_profile(user['user_id'])
        if not profile:
            return jsonify({'success': False, 'message': 'Profile not found'}), 404
        
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
        
        update_data = {'onboarding_data': onboarding_data}
        
        # Update specific profile fields
        if step == 2:  # Personal Info
            if 'display_name' in step_data:
                update_data['display_name'] = step_data['display_name']
            if 'pronouns' in step_data:
                update_data['pronouns'] = step_data['pronouns']
            if 'preferred_language' in step_data:
                update_data['preferred_language'] = step_data['preferred_language']
        
        elif step == 3:  # Emotional Baseline
            if 'current_mood' in step_data:
                update_data['current_mood'] = step_data['current_mood']
            if 'emotion_comfort_level' in step_data:
                update_data['emotion_comfort_level'] = step_data['emotion_comfort_level']
        
        elif step == 4:  # Support Style
            if 'support_style' in step_data:
                update_data['support_style'] = step_data['support_style']
            if 'communication_tone' in step_data:
                update_data['communication_tone'] = step_data['communication_tone']
        
        elif step == 5:  # Focus Areas
            if 'selected_areas' in step_data:
                update_data['focus_areas'] = step_data['selected_areas']
        
        elif step == 6:  # Check-in Preferences
            if 'frequency' in step_data:
                update_data['checkin_frequency'] = step_data['frequency']
            if 'time' in step_data:
                update_data['checkin_time'] = step_data['time']
        
        success, message = supabase_service.update_user_profile(user['user_id'], update_data)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Step {step} saved successfully',
                'next_step': step + 1 if step < 7 else None
            })
        else:
            return jsonify({'success': False, 'message': message}), 500
    
    except Exception as e:
        logger.error(f"Save onboarding step error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/onboarding/complete', methods=['POST'])
def complete_onboarding():
    """Mark onboarding as completed"""
    try:
        user = supabase_service.get_current_user()
        if not user:
            return jsonify({'success': False, 'message': 'Not authenticated'}), 401
        
        update_data = {'onboarding_completed': True}
        success, message = supabase_service.update_user_profile(user['user_id'], update_data)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Onboarding completed successfully',
                'redirect_to': '/chat'
            })
        else:
            return jsonify({'success': False, 'message': message}), 500
    
    except Exception as e:
        logger.error(f"Complete onboarding error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/onboarding/preferences', methods=['GET'])
def get_user_preferences():
    """Get user preferences for AI personalization"""
    try:
        user = supabase_service.get_current_user()
        if not user:
            return jsonify({'success': False, 'message': 'Not authenticated'}), 401
        
        profile = supabase_service.get_user_profile(user['user_id'])
        if not profile:
            return jsonify({'success': False, 'message': 'Profile not found'}), 404
        
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
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== ERROR HANDLING ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'message': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def server_error(error):
    logger.error(f"Server error: {error}")
    traceback.print_exc()
    return jsonify({
        'success': False,
        'message': 'Internal server error'
    }), 500

# ==================== STARTUP ====================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("JUMBO CHATBOT API SERVER WITH SUPABASE")
    print("="*60)

    # Initialize services
    if not initialize_services():
        print("❌ Failed to initialize services")
        print("\nPlease check:")
        print("  1. Supabase environment variables are set")
        print("  2. chatbot.py exists and is importable")
        print("  3. All required dependencies are installed")
        sys.exit(1)

    print("\n✅ All services initialized successfully")
    print("🚀 Jumbo API with Supabase running on http://localhost:5000")
    print("🌐 CORS enabled for React frontend")
    print("\n📡 Available Endpoints:")
    print("  POST   /api/auth/signup           - Sign up new user")
    print("  POST   /api/auth/signin           - Sign in user")
    print("  POST   /api/auth/signout          - Sign out user")
    print("  GET    /api/auth/user             - Get current user")
    print("  GET    /api/profile               - Get user profile")
    print("  PUT    /api/profile               - Update user profile")
    print("  POST   /api/chat/message          - Send chat message")
    print("  GET    /api/chat/history          - Get conversation history")
    print("  GET    /api/memories              - Get user memories")
    print("  POST   /api/memories              - Save user memory")
    print("  GET    /api/mood/history          - Get mood history")
    print("  GET    /api/stats                 - Get user statistics")
    print("  GET    /api/onboarding/status     - Check onboarding status")
    print("  POST   /api/onboarding/step       - Save onboarding step")
    print("  POST   /api/onboarding/complete   - Complete onboarding")
    print("  GET    /api/onboarding/preferences - Get user preferences")
    print("  GET    /api/health                - Health check")
    print("\n" + "="*60 + "\n")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=False
    )