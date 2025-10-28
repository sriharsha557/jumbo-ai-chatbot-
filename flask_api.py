"""
Flask API Server for Jumbo Chatbot
Wraps the Python chatbot and exposes REST endpoints for the React UI
Run: python flask_api.py
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import sys
import os
import traceback

# Add your project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chatbot import JumboChatbot
from language_utils import Language

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Global chatbot instance
chatbot = None

def initialize_chatbot():
    """Initialize Jumbo chatbot"""
    global chatbot
    try:
        chatbot = JumboChatbot()
        logger.info("✓ Jumbo Chatbot initialized")
        return True
    except Exception as e:
        logger.error(f"✗ Failed to initialize chatbot: {e}")
        traceback.print_exc()
        chatbot = None
        return False

# ==================== HEALTH CHECK ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Check if API is running"""
    return jsonify({
        'status': 'ok',
        'message': 'Jumbo API is running',
        'chatbot_initialized': chatbot is not None
    })

# ==================== USER MANAGEMENT ====================

@app.route('/api/users/register', methods=['POST'])
def register_user():
    """Register a new user"""
    try:
        if chatbot is None:
            return jsonify({
                'success': False,
                'message': 'Chatbot not initialized'
            }), 500

        data = request.json
        if data is None:
            return jsonify({
                'success': False,
                'message': 'Invalid JSON data'
            }), 400

        name = data.get('name', '').strip()
        language = data.get('language', 'te')
        
        if not name or len(name) < 2:
            return jsonify({
                'success': False,
                'message': 'Name must be at least 2 characters long'
            }), 400
        
        success, message = chatbot.register_new_user(name, language)
        
        if success:
            user = chatbot.get_current_user()
            return jsonify({
                'success': True,
                'message': message,
                'user': {
                    'name': user.get('name'),
                    'language': user.get('language'),
                    'created_at': user.get('created_at')
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
    
    except Exception as e:
        logger.error(f"Registration error: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Registration error: {str(e)}'
        }), 500

@app.route('/api/users/login', methods=['POST'])
def login_user():
    """Login existing user"""
    try:
        data = request.json
        name = data.get('name', '').strip()
        
        if not name:
            return jsonify({
                'success': False,
                'message': 'Name is required'
            }), 400
        
        if not chatbot.user_exists(name):
            return jsonify({
                'success': False,
                'message': f'User "{name}" not found'
            }), 404
        
        chatbot.set_current_user(name)
        user = chatbot.get_current_user()
        
        return jsonify({
            'success': True,
            'message': f'Welcome back, {name}!',
            'user': {
                'name': user.get('name'),
                'language': user.get('language'),
                'created_at': user.get('created_at')
            }
        })
    
    except Exception as e:
        logger.error(f"Login error: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Login error: {str(e)}'
        }), 500

@app.route('/api/users/current', methods=['GET'])
def get_current_user():
    """Get current logged in user"""
    try:
        if not chatbot.is_user_logged_in():
            return jsonify({
                'success': False,
                'user': None,
                'message': 'No user logged in'
            }), 401
        
        user = chatbot.get_current_user()
        return jsonify({
            'success': True,
            'user': {
                'name': user.get('name'),
                'language': user.get('language'),
                'created_at': user.get('created_at')
            }
        })
    
    except Exception as e:
        logger.error(f"Error fetching user: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/users/list', methods=['GET'])
def list_users():
    """Get all registered users"""
    try:
        users = chatbot.get_all_users()
        return jsonify({
            'success': True,
            'users': users,
            'total': len(users)
        })
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/users/stats', methods=['GET'])
def get_user_stats():
    """Get current user statistics"""
    try:
        if not chatbot.is_user_logged_in():
            return jsonify({
                'success': False,
                'message': 'No user logged in'
            }), 401
        
        stats = chatbot.get_user_stats()
        return jsonify({
            'success': True,
            'stats': stats
        })
    
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# ==================== CHAT ====================

@app.route('/api/chat/message', methods=['POST'])
def send_message():
    """Send message with conversation context"""
    try:
        logger.info("=== Chat Message Request ===")
        
        if not chatbot.is_user_logged_in():
            logger.warning("No user logged in")
            return jsonify({
                'success': False,
                'message': 'Please login first'
            }), 401
        
        data = request.json
        logger.info(f"Request data: {data}")
        
        user_message = data.get('message', '').strip()
        conversation_history = data.get('conversation_context', [])
        
        logger.info(f"User message: {user_message}")
        logger.info(f"Conversation history length: {len(conversation_history)}")
        
        if not user_message:
            return jsonify({
                'success': False,
                'message': 'Message cannot be empty'
            }), 400
        
        # Get user info for memory context
        user = chatbot.get_current_user()
        memory_context = {
            'user_name': user.get('name'),
            'language': user.get('language'),
            'previous_conversations': conversation_history
        }
        
        logger.info(f"Processing message for user: {user.get('name')}")
        
        # Check if process_message accepts these parameters
        try:
            # Try with full parameters
            response, metadata = chatbot.process_message(
                user_message,
                conversation_history=conversation_history,
                memory_context=memory_context
            )
        except TypeError as te:
            # If that fails, try with just the message
            logger.warning(f"TypeError with full params: {te}, trying simple call")
            try:
                response, metadata = chatbot.process_message(user_message)
            except Exception as simple_err:
                logger.error(f"Simple call also failed: {simple_err}")
                traceback.print_exc()
                raise
        
        logger.info(f"Response generated successfully")
        
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
                'response_type': metadata.get('response_type', 'text')
            }
        })
    
    except Exception as e:
        logger.error(f"Chat error: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error processing message: {str(e)}',
            'error_type': type(e).__name__
        }), 500

@app.route('/api/chat/history', methods=['GET'])
def get_conversation_history():
    """Get conversation history for current user"""
    try:
        if not chatbot.is_user_logged_in():
            return jsonify({
                'success': False,
                'message': 'Please login first'
            }), 401
        
        limit = request.args.get('limit', 10, type=int)
        user_name = chatbot.get_current_user().get('name')
        
        # Get recent conversations
        conversations = chatbot.db.get_recent_conversations(user_name, limit)
        
        return jsonify({
            'success': True,
            'conversations': conversations,
            'total': len(conversations)
        })
    
    except Exception as e:
        logger.error(f"History error: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# ==================== LANGUAGE ====================

@app.route('/api/language/supported', methods=['GET'])
def get_supported_languages():
    """Get list of supported languages"""
    return jsonify({
        'success': True,
        'languages': [
            {'code': 'te', 'name': 'Telugu', 'native': 'తెలుగు'},
            {'code': 'hi', 'name': 'Hindi', 'native': 'हिंदी'},
            {'code': 'en', 'name': 'English', 'native': 'English'}
        ]
    })

@app.route('/api/language/set', methods=['POST'])
def set_language():
    """Set language for current user"""
    try:
        if not chatbot.is_user_logged_in():
            return jsonify({
                'success': False,
                'message': 'Please login first'
            }), 401
        
        data = request.json
        language = data.get('language', 'en')
        
        valid_languages = ['te', 'hi', 'en']
        if language not in valid_languages:
            return jsonify({
                'success': False,
                'message': f'Invalid language. Supported: {", ".join(valid_languages)}'
            }), 400
        
        chatbot.language = Language(language)
        
        return jsonify({
            'success': True,
            'message': f'Language set to {language}',
            'language': language
        })
    
    except Exception as e:
        logger.error(f"Language error: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

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
    print("JUMBO CHATBOT API SERVER")
    print("="*60)

    # Initialize chatbot
    if not initialize_chatbot():
        print("❌ Failed to initialize chatbot")
        print("\nPlease check:")
        print("  1. chatbot.py exists and is importable")
        print("  2. All required dependencies are installed")
        print("  3. Database is accessible")
        sys.exit(1)

    print("\n✅ Chatbot initialized successfully")
    print("\nInitializing Flask server...")
    print("🚀 Jumbo API running on http://localhost:5000")
    print("🌐 CORS enabled for React frontend")
    print("\n📡 Available Endpoints:")
    print("  POST   /api/users/register       - Register new user")
    print("  POST   /api/users/login          - Login existing user")
    print("  GET    /api/users/current        - Get current user")
    print("  GET    /api/users/list           - List all users")
    print("  GET    /api/users/stats          - Get user statistics")
    print("  POST   /api/chat/message         - Send chat message")
    print("  GET    /api/chat/history         - Get conversation history")
    print("  GET    /api/language/supported   - Get supported languages")
    print("  POST   /api/language/set         - Set user language")
    print("  GET    /api/health               - Health check")
    print("\n" + "="*60 + "\n")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,  # Changed to True for better error messages
        use_reloader=False
    )