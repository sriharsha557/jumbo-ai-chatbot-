"""
Enhanced Chatbot with Integrated Conversation Enhancement System
Combines all enhanced systems for superior conversation quality
"""

import logging
import time
from typing import Tuple, Optional, Dict, List, Any
from datetime import datetime

# Enhanced system imports
from services.enhanced_emotion_detector import get_emotion_detector, EmotionResult
from services.conversation_classifier import get_conversation_classifier, ClassificationResult
from services.entity_extractor import get_entity_extractor, EntityExtractionResult
from services.smart_context_extractor import get_context_extractor, UserContext
from services.memory_retrieval_service import get_memory_retrieval_service
from services.template_selector import get_template_selector, SelectionContext
from services.template_variation_engine import get_variation_engine, VariationContext
from services.context_personalizer import get_context_personalizer, PersonalizationContext
from services.response_strategy_selector import (
    get_strategy_selector, 
    ResponseStrategy, 
    SystemMetrics, 
    SelectionCriteria
)
from services.fallback_response_system import get_fallback_system, FallbackContext
from services.response_quality_assurance import get_quality_assurance, ResponseContext

# Legacy imports for compatibility
from language_utils import LanguageUtils, Language, Mood
from llm_service import LLMService

logger = logging.getLogger(__name__)

class EnhancedJumboChatbot:
    """
    Enhanced chatbot with integrated conversation enhancement systems
    """
    
    def __init__(self, supabase_service=None):
        # Initialize enhanced systems
        self.emotion_detector = get_emotion_detector()
        self.conversation_classifier = get_conversation_classifier()
        self.entity_extractor = get_entity_extractor()
        self.context_extractor = get_context_extractor(supabase_service)
        self.memory_service = get_memory_retrieval_service(supabase_service)
        self.template_selector = get_template_selector()
        self.variation_engine = get_variation_engine()
        self.context_personalizer = get_context_personalizer()
        self.strategy_selector = get_strategy_selector()
        self.fallback_system = get_fallback_system()
        self.quality_assurance = get_quality_assurance()
        
        # Legacy systems for compatibility
        self.llm_service = LLMService()
        
        # Current user context
        self.current_user = None
        self.language = Language.ENGLISH
        
        # Performance tracking
        self.performance_metrics = {
            'total_messages': 0,
            'average_response_time': 0.0,
            'strategy_usage': {},
            'quality_scores': []
        }
        
        logger.info("EnhancedJumboChatbot initialized with all enhancement systems")
    
    def set_supabase_user(self, user_data: dict, language: str = "en", preferred_name: str = None):
        """Set current user from Supabase data"""
        display_name = preferred_name or user_data.get('name', user_data.get('email', 'User'))
        
        self.current_user = {
            "name": display_name,
            "email": user_data.get('email'),
            "user_id": user_data.get('user_id'),
            "preferred_name": preferred_name,
            "language": language,
            "created_at": user_data.get('created_at', '2025-01-01')
        }
        self.language = Language(language)
        logger.info(f"Enhanced chatbot user set: {display_name}")
    
    def is_user_logged_in(self) -> bool:
        """Check if user is logged in"""
        return self.current_user is not None
    
    def process_message(self, user_message: str, 
                       conversation_history: List[Dict] = None,
                       system_metrics: SystemMetrics = None) -> Tuple[str, Dict]:
        """
        Enhanced message processing with full conversation enhancement pipeline
        """
        start_time = time.time()
        
        try:
            # Validate user login
            if not self.is_user_logged_in():
                return "Please log in to continue chatting.", {"error": "No user logged in"}
            
            # Clean input
            user_message = LanguageUtils.clean_text(user_message)
            user_id = self.current_user.get('user_id')
            
            logger.info(f"Processing message for user {user_id}: {user_message[:50]}...")
            
            # Step 1: Enhanced Message Analysis
            analysis_result = self._analyze_message(user_message, conversation_history)
            
            # Step 2: Extract User Context
            user_context = self._extract_user_context(user_id, user_message)
            
            # Step 3: Select Response Strategy
            strategy_decision = self._select_response_strategy(
                analysis_result, user_context, system_metrics
            )
            
            # Step 4: Generate Response
            response, response_metadata = self._generate_response(
                user_message, analysis_result, user_context, strategy_decision, conversation_history
            )
            
            # Step 5: Quality Assurance
            quality_assessment = self._assess_response_quality(
                response, user_message, analysis_result, user_context
            )
            
            # Step 6: Finalize Response
            final_response, final_metadata = self._finalize_response(
                response, analysis_result, user_context, strategy_decision, 
                quality_assessment, response_metadata
            )
            
            # Record performance metrics
            processing_time = (time.time() - start_time) * 1000  # Convert to ms
            self._record_performance_metrics(strategy_decision, quality_assessment, processing_time)
            
            logger.info(f"Message processed in {processing_time:.2f}ms using {strategy_decision.selected_strategy.value}")
            
            return final_response, final_metadata
            
        except Exception as e:
            logger.error(f"Error in enhanced message processing: {e}")
            return self._handle_processing_error(user_message, e)
    
    def _analyze_message(self, user_message: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Comprehensive message analysis using enhanced systems"""
        analysis_start = time.time()
        
        # Emotion detection
        emotion_result = self.emotion_detector.detect_emotion(user_message)
        
        # Conversation classification
        classification_result = self.conversation_classifier.classify_conversation(
            user_message, conversation_history
        )
        
        # Entity extraction
        entity_result = self.entity_extractor.extract_entities(user_message)
        
        analysis_time = (time.time() - analysis_start) * 1000
        
        return {
            'emotion': emotion_result,
            'classification': classification_result,
            'entities': entity_result,
            'analysis_time_ms': analysis_time,
            'is_crisis': self._detect_crisis_situation(emotion_result, entity_result, user_message)
        }
    
    def _extract_user_context(self, user_id: str, user_message: str) -> UserContext:
        """Extract comprehensive user context"""
        return self.context_extractor.get_user_context(user_id, user_message)
    
    def _select_response_strategy(self, analysis_result: Dict, user_context: UserContext, 
                                system_metrics: SystemMetrics = None) -> Any:
        """Select optimal response strategy"""
        if not system_metrics:
            system_metrics = self._get_current_system_metrics()
        
        # Build selection criteria
        criteria = SelectionCriteria(
            message_complexity=self._calculate_message_complexity(analysis_result),
            emotion_intensity=analysis_result['emotion'].confidence,
            context_availability=self._calculate_context_availability(user_context),
            user_engagement_level=0.7,  # Default engagement level
            conversation_length=len(user_context.conversation_history),
            requires_empathy=analysis_result['emotion'].primary_emotion in ['sad', 'angry', 'anxious', 'worried'],
            requires_memory=len(user_context.recent_memories) > 0,
            is_crisis_situation=analysis_result['is_crisis']
        )
        
        return self.strategy_selector.select_strategy(criteria, system_metrics)
    
    def _generate_response(self, user_message: str, analysis_result: Dict, 
                          user_context: UserContext, strategy_decision: Any,
                          conversation_history: List[Dict] = None) -> Tuple[str, Dict]:
        """Generate response using selected strategy"""
        strategy = strategy_decision.selected_strategy
        
        try:
            if strategy == ResponseStrategy.ENHANCED_TEMPLATE:
                return self._generate_enhanced_template_response(
                    user_message, analysis_result, user_context, conversation_history
                )
            elif strategy == ResponseStrategy.BASIC_TEMPLATE:
                return self._generate_basic_template_response(
                    user_message, analysis_result, user_context
                )
            elif strategy == ResponseStrategy.LLM_ASSISTED:
                return self._generate_llm_assisted_response(
                    user_message, analysis_result, user_context, conversation_history
                )
            else:  # EMERGENCY_FALLBACK
                return self._generate_emergency_fallback_response(
                    user_message, analysis_result, user_context
                )
                
        except Exception as e:
            logger.error(f"Error generating {strategy.value} response: {e}")
            # Fall back to emergency response
            return self._generate_emergency_fallback_response(
                user_message, analysis_result, user_context
            )
    
    def _generate_enhanced_template_response(self, user_message: str, analysis_result: Dict,
                                           user_context: UserContext, conversation_history: List[Dict] = None) -> Tuple[str, Dict]:
        """Generate enhanced template response with full personalization"""
        # Get relevant memories
        search_terms = [word for word in user_message.split() if len(word) > 3]
        relevant_memories = self.memory_service.get_relevant_memories(
            user_context.user_id, search_terms, limit=3
        )
        
        # Get user preferences
        user_preferences = self.memory_service.get_user_preferences(user_context.user_id)
        
        # Select appropriate template
        selection_context = SelectionContext(
            user_id=user_context.user_id,
            emotion=analysis_result['emotion'].primary_emotion,
            emotion_confidence=analysis_result['emotion'].confidence,
            conversation_type=analysis_result['classification'].conversation_type,
            available_context=[
                'user_name', 'recent_memories', 'relationships'
            ] if user_context.key_relationships else ['user_name']
        )
        
        template = self.template_selector.select_best_template(selection_context)
        
        if not template:
            # Fallback to basic template if no enhanced template available
            return self._generate_basic_template_response(user_message, analysis_result, user_context)
        
        # Generate variation
        variation_context = VariationContext(
            user_name=user_context.preferred_name,
            emotion=analysis_result['emotion'].primary_emotion,
            recent_memories=[mem.get('fact', '') for mem in user_context.recent_memories[:2]],
            friend_names=list(user_context.key_relationships.keys())[:3],
            conversation_length=len(user_context.conversation_history)
        )
        
        template_response = self.variation_engine.generate_variation(template, variation_context)
        
        # Personalize response
        personalization_context = PersonalizationContext(
            user_context=user_context,
            template=template,
            current_message=user_message,
            conversation_length=len(user_context.conversation_history),
            relevant_memories=relevant_memories,
            user_preferences=user_preferences
        )
        
        final_response = self.context_personalizer.personalize_response(
            template_response, personalization_context
        )
        
        # Generate follow-up question if appropriate
        follow_up = self.variation_engine.generate_follow_up_question(template, variation_context)
        if follow_up and len(final_response) < 150:  # Add follow-up to shorter responses
            final_response += f" {follow_up}"
        
        metadata = {
            'response_type': 'enhanced_template',
            'template_id': template.id,
            'personalization_level': 'high',
            'memories_used': len(relevant_memories),
            'relationships_referenced': len([name for name in user_context.key_relationships.keys() if name in final_response])
        }
        
        return final_response, metadata
    
    def _generate_basic_template_response(self, user_message: str, analysis_result: Dict,
                                        user_context: UserContext) -> Tuple[str, Dict]:
        """Generate basic template response with minimal personalization"""
        # Create fallback context
        fallback_context = FallbackContext(
            user_name=user_context.preferred_name,
            detected_emotion=analysis_result['emotion'].primary_emotion,
            emotion_confidence=analysis_result['emotion'].confidence,
            conversation_type=analysis_result['classification'].conversation_type,
            user_intent=analysis_result['classification'].user_intent,
            conversation_length=len(user_context.conversation_history)
        )
        
        # Generate fallback response
        fallback_response = self.fallback_system.generate_fallback_response(
            fallback_context, preferred_level=None
        )
        
        metadata = {
            'response_type': 'basic_template',
            'fallback_level': fallback_response.fallback_level.value,
            'personalization_level': 'basic',
            'confidence': fallback_response.confidence
        }
        
        return fallback_response.text, metadata
    
    def _generate_llm_assisted_response(self, user_message: str, analysis_result: Dict,
                                      user_context: UserContext, conversation_history: List[Dict] = None) -> Tuple[str, Dict]:
        """Generate LLM-assisted response for complex cases"""
        if not self.llm_service.is_enabled():
            # Fall back to enhanced template if LLM unavailable
            return self._generate_enhanced_template_response(
                user_message, analysis_result, user_context, conversation_history
            )
        
        # Create memory context for LLM
        memory_context = self.context_extractor.get_context_summary(user_context.user_id)
        
        # Generate LLM response
        llm_response = self.llm_service.generate_response(
            user_message,
            language=user_context.preferences.get('language', 'en'),
            mood=analysis_result['emotion'].primary_emotion,
            user_name=user_context.preferred_name,
            memory_context=memory_context,
            conversation_history=conversation_history
        )
        
        if llm_response:
            metadata = {
                'response_type': 'llm_assisted',
                'personalization_level': 'high',
                'memory_context_used': True
            }
            return llm_response, metadata
        else:
            # LLM failed, fall back to enhanced template
            return self._generate_enhanced_template_response(
                user_message, analysis_result, user_context, conversation_history
            )
    
    def _generate_emergency_fallback_response(self, user_message: str, analysis_result: Dict,
                                            user_context: UserContext) -> Tuple[str, Dict]:
        """Generate emergency fallback response"""
        fallback_context = FallbackContext(
            user_name=user_context.preferred_name,
            detected_emotion=analysis_result['emotion'].primary_emotion,
            is_crisis=analysis_result['is_crisis']
        )
        
        fallback_response = self.fallback_system.generate_fallback_response(
            fallback_context, preferred_level=None
        )
        
        metadata = {
            'response_type': 'emergency_fallback',
            'fallback_level': fallback_response.fallback_level.value,
            'safety_score': fallback_response.safety_score
        }
        
        return fallback_response.text, metadata
    
    def _assess_response_quality(self, response: str, user_message: str, 
                               analysis_result: Dict, user_context: UserContext) -> Any:
        """Assess response quality"""
        qa_context = ResponseContext(
            user_message=user_message,
            user_emotion=analysis_result['emotion'].primary_emotion,
            emotion_confidence=analysis_result['emotion'].confidence,
            conversation_type=analysis_result['classification'].conversation_type.value,
            user_name=user_context.preferred_name,
            is_crisis=analysis_result['is_crisis'],
            conversation_length=len(user_context.conversation_history)
        )
        
        return self.quality_assurance.assess_response_quality(response, qa_context)
    
    def _finalize_response(self, response: str, analysis_result: Dict, user_context: UserContext,
                          strategy_decision: Any, quality_assessment: Any, response_metadata: Dict) -> Tuple[str, Dict]:
        """Finalize response with metadata and quality checks"""
        
        # If quality is unacceptable, try fallback
        if not quality_assessment.passed_validation:
            logger.warning(f"Response failed quality validation: {quality_assessment.validation_errors}")
            
            # Generate emergency fallback
            fallback_context = FallbackContext(
                user_name=user_context.preferred_name,
                detected_emotion=analysis_result['emotion'].primary_emotion,
                is_crisis=analysis_result['is_crisis']
            )
            
            fallback_response = self.fallback_system.generate_fallback_response(fallback_context)
            response = fallback_response.text
            response_metadata['quality_fallback_used'] = True
        
        # Build comprehensive metadata
        final_metadata = {
            **response_metadata,
            'user_id': user_context.user_id,
            'user_name': user_context.preferred_name,
            'language': user_context.preferences.get('language', 'en'),
            'emotion_detected': analysis_result['emotion'].primary_emotion,
            'emotion_confidence': analysis_result['emotion'].confidence,
            'conversation_type': analysis_result['classification'].conversation_type.value,
            'user_intent': analysis_result['classification'].user_intent.value,
            'strategy_used': strategy_decision.selected_strategy.value,
            'strategy_confidence': strategy_decision.confidence,
            'quality_score': quality_assessment.metrics.overall_score,
            'quality_level': quality_assessment.metrics.quality_level.value,
            'empathy_score': quality_assessment.metrics.empathy_score,
            'safety_score': quality_assessment.metrics.safety_score,
            'entities_extracted': len(analysis_result['entities'].entities),
            'memories_available': len(user_context.recent_memories),
            'relationships_known': len(user_context.key_relationships),
            'is_crisis': analysis_result['is_crisis']
        }
        
        return response, final_metadata
    
    def _handle_processing_error(self, user_message: str, error: Exception) -> Tuple[str, Dict]:
        """Handle processing errors gracefully"""
        logger.error(f"Processing error: {error}")
        
        # Create minimal context for emergency response
        user_name = self.current_user.get('preferred_name', 'friend') if self.current_user else 'friend'
        
        fallback_context = FallbackContext(
            user_name=user_name,
            detected_emotion='neutral'
        )
        
        emergency_response = self.fallback_system.generate_fallback_response(fallback_context)
        
        metadata = {
            'response_type': 'error_fallback',
            'error': str(error),
            'safety_score': 1.0
        }
        
        return emergency_response.text, metadata
    
    def _detect_crisis_situation(self, emotion_result: EmotionResult, 
                                entity_result: EntityExtractionResult, user_message: str) -> bool:
        """Detect if this is a crisis situation requiring special handling"""
        crisis_keywords = [
            'suicide', 'kill myself', 'end my life', 'not worth living', 'hurt myself',
            'self harm', 'better off dead', 'want to die', 'end it all'
        ]
        
        message_lower = user_message.lower()
        
        # Check for explicit crisis keywords
        if any(keyword in message_lower for keyword in crisis_keywords):
            return True
        
        # Check for very high negative emotion intensity
        if (emotion_result.primary_emotion in ['sad', 'hopeless', 'desperate'] and 
            emotion_result.confidence > 0.8 and 
            emotion_result.intensity.value in ['high', 'very_high']):
            return True
        
        return False
    
    def _calculate_message_complexity(self, analysis_result: Dict) -> float:
        """Calculate message complexity score"""
        complexity = 0.0
        
        # Base complexity on number of entities
        entity_count = len(analysis_result['entities'].entities)
        complexity += min(0.4, entity_count * 0.1)
        
        # Add complexity for multiple emotions
        emotion_count = len(analysis_result['emotion'].detected_emotions)
        complexity += min(0.3, emotion_count * 0.1)
        
        # Add complexity for crisis situations
        if analysis_result['is_crisis']:
            complexity += 0.3
        
        return min(1.0, complexity)
    
    def _calculate_context_availability(self, user_context: UserContext) -> float:
        """Calculate context availability score"""
        availability = 0.0
        
        # User name availability
        if user_context.preferred_name != 'friend':
            availability += 0.2
        
        # Memory availability
        if user_context.recent_memories:
            availability += min(0.3, len(user_context.recent_memories) * 0.1)
        
        # Relationship availability
        if user_context.key_relationships:
            availability += min(0.3, len(user_context.key_relationships) * 0.1)
        
        # Conversation history availability
        if user_context.conversation_history:
            availability += min(0.2, len(user_context.conversation_history) * 0.05)
        
        return min(1.0, availability)
    
    def _get_current_system_metrics(self) -> SystemMetrics:
        """Get current system performance metrics"""
        # In a real implementation, this would gather actual system metrics
        # For now, return reasonable defaults
        return SystemMetrics(
            memory_usage_mb=200,
            cpu_usage_percent=30,
            response_time_ms=150,
            database_query_count=2,
            cache_hit_rate=0.8,
            active_users=1,
            error_rate=0.01
        )
    
    def _record_performance_metrics(self, strategy_decision: Any, quality_assessment: Any, processing_time: float):
        """Record performance metrics for monitoring"""
        self.performance_metrics['total_messages'] += 1
        
        # Update average response time
        total_messages = self.performance_metrics['total_messages']
        current_avg = self.performance_metrics['average_response_time']
        self.performance_metrics['average_response_time'] = (
            (current_avg * (total_messages - 1) + processing_time) / total_messages
        )
        
        # Track strategy usage
        strategy = strategy_decision.selected_strategy.value
        self.performance_metrics['strategy_usage'][strategy] = \
            self.performance_metrics['strategy_usage'].get(strategy, 0) + 1
        
        # Track quality scores
        self.performance_metrics['quality_scores'].append(quality_assessment.metrics.overall_score)
        
        # Keep only recent quality scores (last 100)
        if len(self.performance_metrics['quality_scores']) > 100:
            self.performance_metrics['quality_scores'] = \
                self.performance_metrics['quality_scores'][-100:]
    
    def get_performance_statistics(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        quality_scores = self.performance_metrics['quality_scores']
        
        return {
            'total_messages_processed': self.performance_metrics['total_messages'],
            'average_response_time_ms': round(self.performance_metrics['average_response_time'], 2),
            'strategy_usage_distribution': self.performance_metrics['strategy_usage'].copy(),
            'average_quality_score': round(sum(quality_scores) / len(quality_scores), 3) if quality_scores else 0.0,
            'quality_trend': quality_scores[-10:] if len(quality_scores) >= 10 else quality_scores,
            'system_health': {
                'emotion_detector': 'active',
                'conversation_classifier': 'active',
                'entity_extractor': 'active',
                'template_system': 'active',
                'fallback_system': 'active',
                'quality_assurance': 'active'
            }
        }

# Global enhanced chatbot instance
_enhanced_chatbot = None

def get_enhanced_chatbot(supabase_service=None) -> EnhancedJumboChatbot:
    """Get global enhanced chatbot instance"""
    global _enhanced_chatbot
    if _enhanced_chatbot is None:
        _enhanced_chatbot = EnhancedJumboChatbot(supabase_service)
    return _enhanced_chatbot        en
hanced from the existing system
        return SystemMetrics(
            memory_usage_mb=100,  # Placeholder - could be actual memory monitoring
            cpu_usage_percent=20,  # Placeholder
            response_time_avg_ms=self.conversation_stats.get('average_response_time', 200),
            llm_availability=self.llm_service.is_enabled() if self.llm_service else False,
            database_latency_ms=50  # Placeholder
        )
    
    def _build_available_context(self, analysis: ConversationAnalysis) -> Dict[str, Any]:
        """Build available context for template selection"""
        return {
            'user_name': analysis.user_context.preferred_name,
            'recent_memories': analysis.user_context.recent_memories[:3],
            'key_relationships': list(analysis.user_context.key_relationships.keys())[:3],
            'conversation_length': len(analysis.user_context.conversation_history),
            'recent_emotions': analysis.user_context.recent_emotions[:3]
        }
    
    def _build_llm_prompt(self, message: str, analysis: ConversationAnalysis, 
                         context_summary: str) -> str:
        """Build enhanced prompt for LLM"""
        user_name = analysis.user_context.preferred_name
        emotion = analysis.emotion_result.primary_emotion
        
        prompt = f"""You are Jumbo, a warm and empathetic AI companion. Respond to {user_name}'s message with care and understanding.

User's message: "{message}"
Detected emotion: {emotion} (confidence: {analysis.emotion_result.confidence:.2f})
Conversation type: {analysis.classification_result.conversation_type.value}

Context about {user_name}:
{context_summary}

Guidelines:
- Be warm, empathetic, and supportive
- Keep responses concise (1-2 sentences)
- Reference their name and context when appropriate
- Match their emotional tone
- Ask follow-up questions to show interest

Response:"""
        
        return prompt
    
    def _update_conversation_statistics(self, response_generation: ResponseGeneration, 
                                      total_time: float):
        """Update conversation statistics"""
        # Update strategy usage
        strategy = response_generation.strategy_used.value
        if strategy not in self.conversation_stats['strategy_usage']:
            self.conversation_stats['strategy_usage'][strategy] = 0
        self.conversation_stats['strategy_usage'][strategy] += 1
        
        # Update average response time
        current_avg = self.conversation_stats['average_response_time']
        total_convs = self.conversation_stats['total_conversations']
        new_avg = ((current_avg * (total_convs - 1)) + total_time) / total_convs
        self.conversation_stats['average_response_time'] = new_avg
        
        # Update quality scores
        if response_generation.quality_score > 0:
            self.conversation_stats['quality_scores'].append(response_generation.quality_score)
            # Keep only last 100 scores
            if len(self.conversation_stats['quality_scores']) > 100:
                self.conversation_stats['quality_scores'] = self.conversation_stats['quality_scores'][-100:]
        
        # Update fallback usage
        if response_generation.fallback_used:
            self.conversation_stats['fallback_usage'] += 1
    
    def _generate_emergency_response(self, user_id: str, message: str) -> Dict[str, Any]:
        """Generate emergency response when all systems fail"""
        user_name = self.current_user.get('preferred_name', 'there') if self.current_user else 'there'
        
        emergency_responses = [
            f"I'm here to listen and support you {user_name}.",
            f"I care about what you're going through {user_name}. Tell me more.",
            f"Thank you for sharing with me {user_name}. How are you feeling?",
            f"I'm glad you're talking to me {user_name}. What's on your mind?"
        ]
        
        import random
        response_text = random.choice(emergency_responses)
        
        return {
            'response': response_text,
            'strategy_used': 'emergency_fallback',
            'quality_score': 0.5,
            'processing_time_ms': 10,
            'emotion_detected': 'neutral',
            'conversation_type': 'general',
            'personalization_applied': False,
            'fallback_used': True,
            'reasoning': ['Emergency system failure - using hardcoded response']
        }
    
    def get_conversation_statistics(self) -> Dict[str, Any]:
        """Get current conversation statistics"""
        stats = self.conversation_stats.copy()
        
        # Calculate additional metrics
        if stats['quality_scores']:
            stats['average_quality_score'] = sum(stats['quality_scores']) / len(stats['quality_scores'])
        else:
            stats['average_quality_score'] = 0.0
        
        if stats['total_conversations'] > 0:
            stats['fallback_usage_percentage'] = (stats['fallback_usage'] / stats['total_conversations']) * 100
        else:
            stats['fallback_usage_percentage'] = 0.0
        
        return stats
    
    def reset_conversation_statistics(self):
        """Reset conversation statistics"""
        self.conversation_stats = {
            'total_conversations': 0,
            'strategy_usage': {},
            'average_response_time': 0.0,
            'quality_scores': [],
            'fallback_usage': 0
        }
        logger.info("Conversation statistics reset")

# Factory function for easy integration
def create_enhanced_chatbot(supabase_service=None, llm_service=None) -> EnhancedChatbot:
    """
    Factory function to create an enhanced chatbot instance
    """
    return EnhancedChatbot(supabase_service=supabase_service, llm_service=llm_service)

# Backward compatibility wrapper
class EnhancedChatbotWrapper:
    """
    Wrapper to maintain backward compatibility with existing chatbot interface
    """
    
    def __init__(self, supabase_service=None, llm_service=None):
        self.enhanced_chatbot = create_enhanced_chatbot(supabase_service, llm_service)
        self.supabase_service = supabase_service
        
    def process_message(self, user_id: str, message: str, 
                       conversation_history: List[Dict] = None) -> Tuple[str, Dict]:
        """
        Process message with enhanced system while maintaining original interface
        """
        try:
            # Set user context
            if self.supabase_service and user_id:
                user_data = self.supabase_service.get_user_profile(user_id)
                if user_data:
                    self.enhanced_chatbot.current_user = {
                        'user_id': user_id,
                        'name': user_data.get('name', 'User'),
                        'preferred_name': user_data.get('preferred_name'),
                        'email': user_data.get('email')
                    }
            
            # Process with enhanced system
            enhanced_response = self.enhanced_chatbot.process_message(
                user_id, message, conversation_history
            )
            
            # Convert to original format
            response_text = enhanced_response['response']
            metadata = {
                'strategy_used': enhanced_response['strategy_used'],
                'quality_score': enhanced_response['quality_score'],
                'processing_time_ms': enhanced_response['processing_time_ms'],
                'emotion_detected': enhanced_response['emotion_detected'],
                'conversation_type': enhanced_response['conversation_type'],
                'personalization_applied': enhanced_response['personalization_applied'],
                'fallback_used': enhanced_response['fallback_used'],
                'response_type': 'enhanced',
                'used_llm': enhanced_response['strategy_used'] == 'llm_assisted'
            }
            
            return response_text, metadata
            
        except Exception as e:
            logger.error(f"Enhanced chatbot wrapper error: {e}")
            # Fallback to simple response
            return f"I'm here to listen and support you. Tell me more about what's on your mind.", {
                'response_type': 'emergency_fallback',
                'error': str(e)
            }