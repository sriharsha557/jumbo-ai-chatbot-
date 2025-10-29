"""
Stateless Chat Service
Handles chat processing without maintaining state in memory
"""

from typing import Dict, List, Tuple, Optional, Any
import json
from datetime import datetime

from chatbot import JumboChatbot
from supabase_service import SupabaseService
from services.personality_service import PersonalityService
from services.emotion_service_factory import get_emotion_detector
from services.response_polisher import get_response_polisher
from monitoring import logger, monitor_llm_request, monitor_database_query, metrics

class ChatService:
    """Stateless chat service that processes messages without storing state"""
    
    def __init__(self, supabase_service: SupabaseService):
        self.supabase_service = supabase_service
        self.chatbot = JumboChatbot()
        self.personality_service = PersonalityService()
        self.emotion_detector = get_emotion_detector()
        self.response_polisher = get_response_polisher()
    
    @monitor_llm_request()
    def process_message(self, 
                       user_id: str, 
                       message: str, 
                       conversation_context: List[Dict] = None,
                       emotion: str = None) -> Tuple[str, Dict[str, Any]]:
        """
        Process a chat message in a stateless manner
        
        Args:
            user_id: User identifier
            message: User message
            conversation_context: Recent conversation history
            
        Returns:
            Tuple of (response, metadata)
        """
        try:
            # Get user profile from database, create if doesn't exist
            user_profile = self._get_user_profile(user_id)
            if not user_profile:
                logger.info(f"Creating profile for new user: {user_id}")
                # Create a basic profile for the user
                success, message = self.supabase_service.create_user_profile(user_id, {
                    'name': 'User',  # Required field
                    'display_name': 'User',
                    'preferred_name': 'friend',
                    'onboarding_completed': False
                })
                if success:
                    logger.info(f"Profile creation succeeded for user: {user_id}")
                    user_profile = self._get_user_profile(user_id)
                    if not user_profile:
                        logger.error(f"Profile was created but could not be retrieved for user: {user_id}")
                        # Try to continue with a minimal profile to avoid blocking chat
                        user_profile = {
                            'id': user_id,
                            'name': 'User',
                            'preferred_name': 'friend',
                            'onboarding_completed': False
                        }
                        logger.info(f"Using fallback profile for user: {user_id}")
                else:
                    logger.error(f"Failed to create user profile: {message}")
                    # Try to continue with a minimal profile to avoid blocking chat
                    user_profile = {
                        'id': user_id,
                        'name': 'User',
                        'preferred_name': 'friend',
                        'onboarding_completed': False
                    }
                    logger.info(f"Using fallback profile after creation failure for user: {user_id}")
            
            # Set up chatbot with user context (stateless)
            self._setup_chatbot_context(user_profile)
            
            # Add user to active users metrics
            metrics.add_active_user(user_id)
            
            # Get user's preferred name for personality system
            user_name = user_profile.get('preferred_name') or user_profile.get('name', 'friend')
            
            # Detect emotion if not provided
            if emotion is None:
                emotion_scores = self.emotion_detector.detect_emotion(message)
                if emotion_scores:
                    # Get the dominant emotion
                    emotion = max(emotion_scores.items(), key=lambda x: x[1])[0]
                    emotion_confidence = emotion_scores[emotion]
                    emotion_method = "keyword_detection"
                else:
                    emotion = "neutral"
                    emotion_confidence = 1.0
                    emotion_method = "default"
                logger.info(f"Detected emotion: {emotion} (confidence: {emotion_confidence:.2f}, method: {emotion_method})")
            else:
                emotion_confidence = 1.0
                emotion_method = "provided"
            
            # Check for first-time user flow
            if self._is_first_time_user(user_profile, conversation_context):
                response = self._handle_first_time_user_with_personality(user_profile, message, emotion)
                metadata = {
                    'response_type': 'name_request',
                    'mood': 'friendly',
                    'language': user_profile.get('language', 'en'),
                    'user_id': user_id,
                    'emotion': emotion,
                    'emotion_confidence': emotion_confidence,
                    'emotion_method': emotion_method,
                    'personality_enhanced': True
                }
                return response, metadata
            
            # Process message through chatbot with personality enhancement
            response, metadata = self._process_message_with_personality(
                message, 
                conversation_context or [], 
                emotion, 
                user_name,
                user_profile
            )
            
            # Add user context to metadata
            metadata.update({
                'user_id': user_id,
                'language': user_profile.get('language', 'en'),
                'preferred_name': user_profile.get('preferred_name'),
                'emotion': emotion,
                'emotion_confidence': emotion_confidence,
                'emotion_method': emotion_method,
                'personality_enhanced': True
            })
            
            # Save conversation to database
            self._save_conversation(user_id, message, response, metadata)
            
            # Increment conversation counter
            metrics.increment_conversations()
            
            logger.info("Message processed successfully",
                       user_id=user_id,
                       message_length=len(message),
                       response_type=metadata.get('response_type'),
                       scenario=metadata.get('scenario'))
            
            return response, metadata
            
        except Exception as e:
            logger.error("Failed to process message", 
                        error=e,
                        user_id=user_id,
                        message_length=len(message) if message else 0)
            raise
    
    @monitor_database_query()
    def _get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile from database"""
        return self.supabase_service.get_user_profile(user_id)
    
    def _setup_chatbot_context(self, user_profile: Dict):
        """Setup chatbot with user context (stateless)"""
        user_data = {
            'user_id': user_profile['id'],
            'email': user_profile.get('email'),
            'name': user_profile.get('name')
        }
        
        language = user_profile.get('language', 'en')
        preferred_name = user_profile.get('preferred_name')
        
        # Set user context in chatbot (this doesn't store state permanently)
        self.chatbot.set_supabase_user(user_data, language, preferred_name)
        
        # Set supabase service reference for database operations
        self.chatbot._supabase_service = self.supabase_service
    
    def _is_first_time_user(self, user_profile: Dict, conversation_context: List[Dict]) -> bool:
        """Check if this is a first-time user without preferred name"""
        has_preferred_name = user_profile.get('preferred_name') is not None
        has_conversation_history = conversation_context and len(conversation_context) > 0
        
        return not has_preferred_name and not has_conversation_history
    
    def _handle_first_time_user(self, user_profile: Dict, message: str) -> str:
        """Handle first-time user interaction"""
        # Skip name request for basic greetings
        if message.lower().strip() in ['hi', 'hello', 'hey']:
            return self.chatbot.get_personalized_greeting(is_first_time=True)
        
        # For other messages, still ask for name preference
        return self.chatbot.get_personalized_greeting(is_first_time=True)
    
    def _handle_first_time_user_with_personality(self, user_profile: Dict, message: str, emotion: str) -> str:
        """Handle first-time user interaction with personality system"""
        try:
            # Use personality service to create a warm, emotion-aware greeting
            greeting = self.personality_service.get_conversation_starter(emotion)
            
            # Add name request naturally
            name_request = "I'd love to know what you'd like me to call you - what name feels right?"
            
            return f"{greeting} {name_request}"
            
        except Exception as e:
            logger.error(f"Error in personality-enhanced first-time user handling: {e}")
            # Fallback to original method
            return self._handle_first_time_user(user_profile, message)
    
    def _process_message_with_personality(self, 
                                        message: str, 
                                        conversation_history: List[Dict], 
                                        emotion: str,
                                        user_name: str,
                                        user_profile: Dict) -> Tuple[str, Dict[str, any]]:
        """Process message with personality enhancement"""
        try:
            # Get relevant memories for context
            memories = self.get_user_memories(user_profile['id'], limit=5)
            
            # Build personality-enhanced system prompt
            system_prompt = self.personality_service.build_system_prompt(
                emotion=emotion,
                user_name=user_name,
                context=f"Recent conversation history: {len(conversation_history)} messages",
                memories=memories
            )
            
            # Process through chatbot with enhanced context
            if hasattr(self.chatbot, 'process_message_with_system_prompt'):
                response, metadata = self.chatbot.process_message_with_system_prompt(
                    message,
                    system_prompt,
                    conversation_history=conversation_history
                )
            else:
                # Fallback: use existing chatbot method and enhance response
                response, metadata = self.chatbot.process_message(
                    message,
                    conversation_history=conversation_history
                )
                
                # Enhance response with personality
                response = self.personality_service.enhance_response_with_personality(
                    response, emotion, user_name
                )
            
            # Final polish for quality assurance
            response = self.response_polisher.polish_response(
                response, emotion, user_name, context={'memories': memories}
            )
            
            # Add personality metadata
            personality_metadata = self.personality_service.get_emotion_metadata(emotion)
            metadata.update(personality_metadata)
            metadata.update({'response_polished': True})
            
            return response, metadata
            
        except Exception as e:
            logger.error(f"Error in personality-enhanced message processing: {e}")
            # Fallback to original chatbot processing
            return self.chatbot.process_message(message, conversation_history=conversation_history)
    
    @monitor_database_query()
    def _save_conversation(self, user_id: str, message: str, response: str, metadata: Dict):
        """Save conversation to database"""
        conversation_data = {
            'message': message,
            'response': response,
            'metadata': metadata
        }
        
        success, save_message, conversation_id = self.supabase_service.save_conversation(
            user_id, conversation_data
        )
        
        if not success:
            logger.warning("Failed to save conversation",
                          user_id=user_id,
                          error_message=save_message)
        
        return conversation_id if success else None
    
    @monitor_database_query()
    def get_conversation_history(self, user_id: str, limit: int = 20) -> List[Dict]:
        """Get conversation history for user"""
        try:
            conversations = self.supabase_service.get_user_conversations(user_id, limit)
            
            logger.debug("Retrieved conversation history",
                        user_id=user_id,
                        conversation_count=len(conversations))
            
            return conversations
            
        except Exception as e:
            logger.error("Failed to get conversation history",
                        error=e,
                        user_id=user_id)
            return []
    
    @monitor_database_query()
    def update_user_preference(self, user_id: str, preference_data: Dict) -> Tuple[bool, str]:
        """Update user preferences"""
        try:
            success, message = self.supabase_service.update_user_profile(user_id, preference_data)
            
            if success:
                logger.info("User preferences updated",
                           user_id=user_id,
                           updated_fields=list(preference_data.keys()))
            else:
                logger.warning("Failed to update user preferences",
                              user_id=user_id,
                              error_message=message)
            
            return success, message
            
        except Exception as e:
            logger.error("Error updating user preferences",
                        error=e,
                        user_id=user_id)
            return False, str(e)
    
    @monitor_database_query()
    def get_user_memories(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get user memories"""
        try:
            memories = self.supabase_service.get_user_memories(user_id, limit)
            
            logger.debug("Retrieved user memories",
                        user_id=user_id,
                        memory_count=len(memories))
            
            return memories
            
        except Exception as e:
            logger.error("Failed to get user memories",
                        error=e,
                        user_id=user_id)
            return []
    
    @monitor_database_query()
    def get_mood_history(self, user_id: str, days: int = 30) -> List[Dict]:
        """Get user mood history"""
        try:
            mood_history = self.supabase_service.get_user_mood_history(user_id, days)
            
            logger.debug("Retrieved mood history",
                        user_id=user_id,
                        mood_entries=len(mood_history))
            
            return mood_history
            
        except Exception as e:
            logger.error("Failed to get mood history",
                        error=e,
                        user_id=user_id)
            return []
    
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user statistics"""
        try:
            # Get various user data
            conversations = self.get_conversation_history(user_id, limit=1000)
            memories = self.get_user_memories(user_id)
            mood_history = self.get_mood_history(user_id)
            
            # Calculate statistics
            stats = {
                'total_conversations': len(conversations),
                'total_memories': len(memories),
                'mood_entries': len(mood_history),
                'days_active': len(set(conv.get('created_at', '')[:10] for conv in conversations)),
                'most_common_mood': self._get_most_common_mood(mood_history),
                'last_active': conversations[0].get('created_at') if conversations else None
            }
            
            logger.debug("Generated user statistics",
                        user_id=user_id,
                        stats=stats)
            
            return stats
            
        except Exception as e:
            logger.error("Failed to generate user statistics",
                        error=e,
                        user_id=user_id)
            return {}
    
    def _get_most_common_mood(self, mood_history: List[Dict]) -> Optional[str]:
        """Get the most common mood from mood history"""
        if not mood_history:
            return None
        
        mood_counts = {}
        for entry in mood_history:
            mood = entry.get('mood', 'neutral')
            mood_counts[mood] = mood_counts.get(mood, 0) + 1
        
        return max(mood_counts, key=mood_counts.get) if mood_counts else None