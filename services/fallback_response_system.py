"""
Robust Fallback Response System
Provides high-quality fallback responses when primary systems fail
"""

import logging
import random
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

from services.response_strategy_selector import ResponseStrategy
from services.enhanced_emotion_detector import EmotionResult
from services.conversation_classifier import ClassificationResult, UserIntent
from services.template_models import ConversationType

logger = logging.getLogger(__name__)

class FallbackLevel(Enum):
    """Levels of fallback responses"""
    BASIC_TEMPLATE = "basic_template"      # Simple templates with minimal context
    EMPATHY_FOCUSED = "empathy_focused"    # Empathetic responses for emotional situations
    EMERGENCY_SAFE = "emergency_safe"      # Ultra-safe responses for any situation
    CRISIS_SUPPORT = "crisis_support"      # Specialized responses for crisis situations

@dataclass
class FallbackContext:
    """Context for fallback response generation"""
    user_name: str = "friend"
    detected_emotion: str = "neutral"
    emotion_confidence: float = 0.5
    conversation_type: ConversationType = ConversationType.CASUAL_CHAT
    user_intent: UserIntent = UserIntent.CASUAL_CHAT
    is_crisis: bool = False
    conversation_length: int = 0
    available_context: List[str] = field(default_factory=list)

@dataclass
class FallbackResponse:
    """A fallback response with metadata"""
    text: str
    fallback_level: FallbackLevel
    confidence: float
    empathy_score: float
    safety_score: float
    personalization_level: float
    reasoning: List[str] = field(default_factory=list)

class FallbackResponseSystem:
    """
    Robust fallback system that provides quality responses when primary systems fail
    """
    
    def __init__(self):
        self.basic_templates = self._load_basic_templates()
        self.empathy_responses = self._load_empathy_responses()
        self.emergency_responses = self._load_emergency_responses()
        self.crisis_responses = self._load_crisis_responses()
        self.personalization_patterns = self._load_personalization_patterns()
        
        # Fallback usage statistics
        self.fallback_stats = {
            'total_fallbacks': 0,
            'fallback_level_usage': {},
            'emotion_fallback_distribution': {},
            'success_rates': {}
        }
        
        logger.info("FallbackResponseSystem initialized with multi-level responses")
    
    def _load_basic_templates(self) -> Dict[str, List[str]]:
        """Load basic template responses by category"""
        return {
            'greeting': [
                "Hello {user_name}! How are you today?",
                "Hi {user_name}! It's good to see you.",
                "Hey there {user_name}! What's on your mind?",
                "Welcome {user_name}! How can I help you today?",
                "Hi {user_name}! I'm here and ready to chat."
            ],
            'goodbye': [
                "Take care {user_name}! It was great talking with you.",
                "Goodbye {user_name}! Have a wonderful day.",
                "See you later {user_name}! Be well.",
                "Until next time {user_name}! Take good care of yourself.",
                "Farewell {user_name}! Wishing you all the best."
            ],
            'happy': [
                "That's wonderful {user_name}! I'm so happy for you.",
                "How exciting {user_name}! Your joy is contagious.",
                "That's fantastic news {user_name}! You deserve this happiness.",
                "I love hearing good news like this {user_name}!",
                "Your happiness makes me smile {user_name}!"
            ],
            'sad': [
                "I'm sorry you're going through this {user_name}. I'm here to listen.",
                "That sounds really difficult {user_name}. You're not alone.",
                "I hear the sadness in your words {user_name}. I'm here with you.",
                "Thank you for sharing this with me {user_name}. I care about you.",
                "I'm here to support you through this {user_name}."
            ],
            'angry': [
                "I can feel your frustration {user_name}. Your feelings are valid.",
                "That sounds incredibly frustrating {user_name}. I understand.",
                "Your anger makes sense {user_name}. Let's talk through this.",
                "I hear how upset you are {user_name}. I'm here to listen.",
                "It's okay to feel angry {user_name}. Tell me more about it."
            ],
            'anxious': [
                "I can sense your anxiety {user_name}. Let's take this step by step.",
                "Take a deep breath {user_name}. You're safe here with me.",
                "I understand you're feeling worried {user_name}. I'm here to help.",
                "Anxiety can be overwhelming {user_name}. You don't have to face it alone.",
                "Let's work through this together {user_name}. You're not alone."
            ],
            'neutral': [
                "I'm here to listen {user_name}. What would you like to talk about?",
                "Tell me more {user_name}. I'm interested in what you have to say.",
                "I'm with you {user_name}. Please continue.",
                "That's interesting {user_name}. Help me understand better.",
                "I'm here for you {user_name}. What's on your mind?"
            ],
            'advice_seeking': [
                "That's a thoughtful question {user_name}. Let me think about this with you.",
                "I can help you explore this {user_name}. What are your thoughts so far?",
                "That's something worth considering carefully {user_name}. What matters most to you?",
                "Let's work through this together {user_name}. What options are you considering?",
                "I'm here to help you think this through {user_name}."
            ],
            'celebration': [
                "Congratulations {user_name}! This is amazing news!",
                "How wonderful {user_name}! You should be so proud!",
                "That's incredible {user_name}! I'm celebrating with you!",
                "What fantastic news {user_name}! You deserve this success!",
                "I'm so excited for you {user_name}! This is wonderful!"
            ]
        }
    
    def _load_empathy_responses(self) -> Dict[str, List[str]]:
        """Load empathy-focused responses for emotional situations"""
        return {
            'validation': [
                "Your feelings are completely valid {user_name}.",
                "It makes perfect sense that you'd feel this way {user_name}.",
                "Anyone in your situation would feel the same {user_name}.",
                "Your reaction is completely natural {user_name}.",
                "You have every right to feel this way {user_name}."
            ],
            'support': [
                "I'm here with you {user_name}. You're not alone in this.",
                "You don't have to carry this by yourself {user_name}.",
                "I'm here to support you through this {user_name}.",
                "You have my full attention and support {user_name}.",
                "I'm standing with you {user_name}. We'll get through this together."
            ],
            'understanding': [
                "I can hear how much this means to you {user_name}.",
                "I can sense the depth of what you're feeling {user_name}.",
                "I understand this is really important to you {user_name}.",
                "I can feel the weight of what you're carrying {user_name}.",
                "I hear you {user_name}. This matters deeply to you."
            ],
            'encouragement': [
                "You're stronger than you know {user_name}.",
                "You've handled difficult things before {user_name}.",
                "I believe in your ability to get through this {user_name}.",
                "You have more resilience than you realize {user_name}.",
                "You're doing the best you can {user_name}, and that's enough."
            ]
        }
    
    def _load_emergency_responses(self) -> List[str]:
        """Load ultra-safe emergency responses"""
        return [
            "I'm here to listen and support you {user_name}.",
            "Thank you for sharing with me {user_name}. I care about you.",
            "I'm with you {user_name}. Please tell me more.",
            "Your feelings matter {user_name}. I'm here for you.",
            "I hear you {user_name}. You're important to me.",
            "I'm listening {user_name}. Please continue.",
            "You're not alone {user_name}. I'm here with you.",
            "I care about what you're going through {user_name}.",
            "Thank you for trusting me with this {user_name}.",
            "I'm here to support you {user_name}. Always."
        ]
    
    def _load_crisis_responses(self) -> Dict[str, List[str]]:
        """Load specialized responses for crisis situations"""
        return {
            'immediate_support': [
                "I'm really concerned about you {user_name}. You matter so much.",
                "I hear that you're in pain {user_name}. I'm here with you right now.",
                "Thank you for reaching out {user_name}. That takes courage.",
                "I'm glad you're talking to me {user_name}. You're not alone.",
                "Your life has value {user_name}. I'm here to listen."
            ],
            'gentle_guidance': [
                "Have you been able to talk to anyone else about this {user_name}?",
                "Is there someone you trust who could be with you right now {user_name}?",
                "Would it help to talk to a professional who specializes in this {user_name}?",
                "Are you somewhere safe right now {user_name}?",
                "What would help you feel a little safer right now {user_name}?"
            ],
            'resource_suggestion': [
                "There are people trained specifically to help with this {user_name}.",
                "You don't have to go through this alone {user_name}. Help is available.",
                "There are resources that can provide better support than I can {user_name}.",
                "Professional counselors are available 24/7 to help {user_name}.",
                "Crisis support is available anytime you need it {user_name}."
            ]
        }
    
    def _load_personalization_patterns(self) -> Dict[str, List[str]]:
        """Load patterns for adding personalization to responses"""
        return {
            'memory_references': [
                "I remember you mentioning this before {user_name}.",
                "This reminds me of what you shared earlier {user_name}.",
                "I recall you talking about something similar {user_name}.",
                "You've brought this up before {user_name}."
            ],
            'relationship_acknowledgments': [
                "I know your relationships are important to you {user_name}.",
                "You care deeply about the people in your life {user_name}.",
                "Your connections with others matter to you {user_name}.",
                "I can tell you value your relationships {user_name}."
            ],
            'emotional_continuity': [
                "I can see this is still on your mind {user_name}.",
                "These feelings seem to be staying with you {user_name}.",
                "This continues to be important to you {user_name}.",
                "I notice this keeps coming up for you {user_name}."
            ]
        }
    
    def generate_fallback_response(self, context: FallbackContext, 
                                 preferred_level: FallbackLevel = None) -> FallbackResponse:
        """
        Generate a fallback response based on context and preferred level
        """
        try:
            self.fallback_stats['total_fallbacks'] += 1
            
            # Determine appropriate fallback level
            if preferred_level:
                fallback_level = preferred_level
            else:
                fallback_level = self._determine_fallback_level(context)
            
            # Generate response based on level
            if fallback_level == FallbackLevel.CRISIS_SUPPORT:
                response = self._generate_crisis_response(context)
            elif fallback_level == FallbackLevel.EMPATHY_FOCUSED:
                response = self._generate_empathy_response(context)
            elif fallback_level == FallbackLevel.BASIC_TEMPLATE:
                response = self._generate_basic_template_response(context)
            else:  # EMERGENCY_SAFE
                response = self._generate_emergency_response(context)
            
            # Add personalization if possible
            response = self._add_personalization(response, context)
            
            # Create fallback response object
            fallback_response = FallbackResponse(
                text=response,
                fallback_level=fallback_level,
                confidence=self._calculate_confidence(fallback_level, context),
                empathy_score=self._calculate_empathy_score(response, context),
                safety_score=self._calculate_safety_score(fallback_level),
                personalization_level=self._calculate_personalization_level(response, context),
                reasoning=self._build_fallback_reasoning(fallback_level, context)
            )
            
            # Update statistics
            self._update_fallback_statistics(fallback_response, context)
            
            logger.debug(f"Generated {fallback_level.value} fallback response")
            return fallback_response
            
        except Exception as e:
            logger.error(f"Error generating fallback response: {e}")
            return self._generate_ultimate_fallback(context)
    
    def _determine_fallback_level(self, context: FallbackContext) -> FallbackLevel:
        """Determine appropriate fallback level based on context"""
        # Crisis situations get highest priority
        if context.is_crisis:
            return FallbackLevel.CRISIS_SUPPORT
        
        # High emotional intensity gets empathy focus
        if context.emotion_confidence > 0.7 and context.detected_emotion in ['sad', 'angry', 'anxious', 'worried']:
            return FallbackLevel.EMPATHY_FOCUSED
        
        # If we have some context, use basic templates
        if context.available_context or context.conversation_length > 0:
            return FallbackLevel.BASIC_TEMPLATE
        
        # Default to emergency safe
        return FallbackLevel.EMERGENCY_SAFE
    
    def _generate_crisis_response(self, context: FallbackContext) -> str:
        """Generate crisis support response"""
        # Start with immediate support
        support_responses = self.crisis_responses['immediate_support']
        response = random.choice(support_responses)
        
        # Add gentle guidance if appropriate
        if context.conversation_length > 1:
            guidance_responses = self.crisis_responses['gentle_guidance']
            guidance = random.choice(guidance_responses)
            response += f" {guidance}"
        
        return response.format(user_name=context.user_name)
    
    def _generate_empathy_response(self, context: FallbackContext) -> str:
        """Generate empathy-focused response"""
        # Choose empathy type based on emotion
        if context.detected_emotion in ['sad', 'disappointed', 'hurt']:
            empathy_type = 'support'
        elif context.detected_emotion in ['angry', 'frustrated', 'annoyed']:
            empathy_type = 'validation'
        elif context.detected_emotion in ['anxious', 'worried', 'stressed']:
            empathy_type = 'understanding'
        else:
            empathy_type = 'encouragement'
        
        # Get empathy response
        empathy_responses = self.empathy_responses[empathy_type]
        response = random.choice(empathy_responses)
        
        return response.format(user_name=context.user_name)
    
    def _generate_basic_template_response(self, context: FallbackContext) -> str:
        """Generate basic template response"""
        # Determine template category
        if context.conversation_type == ConversationType.GREETING:
            category = 'greeting'
        elif context.conversation_type == ConversationType.GOODBYE:
            category = 'goodbye'
        elif context.conversation_type == ConversationType.CELEBRATION:
            category = 'celebration'
        elif context.conversation_type == ConversationType.ADVICE_SEEKING:
            category = 'advice_seeking'
        elif context.detected_emotion in self.basic_templates:
            category = context.detected_emotion
        else:
            category = 'neutral'
        
        # Get template response
        templates = self.basic_templates.get(category, self.basic_templates['neutral'])
        response = random.choice(templates)
        
        return response.format(user_name=context.user_name)
    
    def _generate_emergency_response(self, context: FallbackContext) -> str:
        """Generate emergency safe response"""
        response = random.choice(self.emergency_responses)
        return response.format(user_name=context.user_name)
    
    def _add_personalization(self, response: str, context: FallbackContext) -> str:
        """Add personalization to response if context allows"""
        # Don't over-personalize crisis responses
        if context.is_crisis:
            return response
        
        # Add memory reference if conversation has history
        if context.conversation_length > 3 and random.random() < 0.3:
            memory_refs = self.personalization_patterns['memory_references']
            memory_ref = random.choice(memory_refs)
            response = f"{memory_ref.format(user_name=context.user_name)} {response}"
        
        # Add relationship acknowledgment for relationship topics
        elif 'relationship' in context.available_context and random.random() < 0.4:
            rel_acks = self.personalization_patterns['relationship_acknowledgments']
            rel_ack = random.choice(rel_acks)
            response += f" {rel_ack.format(user_name=context.user_name)}"
        
        return response
    
    def _calculate_confidence(self, level: FallbackLevel, context: FallbackContext) -> float:
        """Calculate confidence score for fallback response"""
        base_confidence = {
            FallbackLevel.CRISIS_SUPPORT: 0.9,
            FallbackLevel.EMPATHY_FOCUSED: 0.8,
            FallbackLevel.BASIC_TEMPLATE: 0.7,
            FallbackLevel.EMERGENCY_SAFE: 0.6
        }
        
        confidence = base_confidence[level]
        
        # Adjust based on context quality
        if context.emotion_confidence > 0.8:
            confidence += 0.1
        elif context.emotion_confidence < 0.3:
            confidence -= 0.1
        
        return min(1.0, max(0.0, confidence))
    
    def _calculate_empathy_score(self, response: str, context: FallbackContext) -> float:
        """Calculate empathy score for response"""
        empathy_indicators = [
            'understand', 'hear', 'feel', 'sense', 'with you', 'not alone',
            'here for you', 'support', 'care', 'listen', 'valid', 'makes sense'
        ]
        
        response_lower = response.lower()
        empathy_count = sum(1 for indicator in empathy_indicators if indicator in response_lower)
        
        # Base score on empathy indicators
        empathy_score = min(1.0, empathy_count * 0.2)
        
        # Boost for emotional contexts
        if context.detected_emotion in ['sad', 'angry', 'anxious', 'worried']:
            empathy_score += 0.2
        
        return min(1.0, empathy_score)
    
    def _calculate_safety_score(self, level: FallbackLevel) -> float:
        """Calculate safety score for fallback level"""
        safety_scores = {
            FallbackLevel.CRISIS_SUPPORT: 1.0,
            FallbackLevel.EMPATHY_FOCUSED: 0.9,
            FallbackLevel.BASIC_TEMPLATE: 0.8,
            FallbackLevel.EMERGENCY_SAFE: 1.0
        }
        return safety_scores[level]
    
    def _calculate_personalization_level(self, response: str, context: FallbackContext) -> float:
        """Calculate personalization level of response"""
        personalization_score = 0.0
        
        # Check for user name usage
        if context.user_name in response and context.user_name != "friend":
            personalization_score += 0.3
        
        # Check for context references
        if any(ctx in response.lower() for ctx in context.available_context):
            personalization_score += 0.4
        
        # Check for emotion acknowledgment
        if context.detected_emotion in response.lower():
            personalization_score += 0.3
        
        return min(1.0, personalization_score)
    
    def _build_fallback_reasoning(self, level: FallbackLevel, context: FallbackContext) -> List[str]:
        """Build reasoning for fallback selection"""
        reasoning = []
        
        if level == FallbackLevel.CRISIS_SUPPORT:
            reasoning.append("Crisis situation detected - prioritizing safety and support")
        elif level == FallbackLevel.EMPATHY_FOCUSED:
            reasoning.append(f"High emotional intensity ({context.detected_emotion}) - focusing on empathy")
        elif level == FallbackLevel.BASIC_TEMPLATE:
            reasoning.append("Sufficient context available for template-based response")
        else:
            reasoning.append("Using emergency safe response for maximum reliability")
        
        if context.conversation_length > 0:
            reasoning.append(f"Conversation history: {context.conversation_length} exchanges")
        
        if context.available_context:
            reasoning.append(f"Available context: {len(context.available_context)} elements")
        
        return reasoning
    
    def _generate_ultimate_fallback(self, context: FallbackContext) -> FallbackResponse:
        """Generate ultimate fallback when all else fails"""
        return FallbackResponse(
            text=f"I'm here to listen and support you {context.user_name}.",
            fallback_level=FallbackLevel.EMERGENCY_SAFE,
            confidence=0.5,
            empathy_score=0.8,
            safety_score=1.0,
            personalization_level=0.2,
            reasoning=["Ultimate fallback due to system error"]
        )
    
    def _update_fallback_statistics(self, response: FallbackResponse, context: FallbackContext):
        """Update fallback usage statistics"""
        level = response.fallback_level.value
        
        # Update level usage
        self.fallback_stats['fallback_level_usage'][level] = \
            self.fallback_stats['fallback_level_usage'].get(level, 0) + 1
        
        # Update emotion distribution
        emotion = context.detected_emotion
        self.fallback_stats['emotion_fallback_distribution'][emotion] = \
            self.fallback_stats['emotion_fallback_distribution'].get(emotion, 0) + 1
    
    def get_fallback_statistics(self) -> Dict[str, Any]:
        """Get fallback system statistics"""
        return {
            'total_fallbacks': self.fallback_stats['total_fallbacks'],
            'fallback_level_usage': self.fallback_stats['fallback_level_usage'].copy(),
            'emotion_fallback_distribution': self.fallback_stats['emotion_fallback_distribution'].copy(),
            'available_levels': [level.value for level in FallbackLevel],
            'template_categories': list(self.basic_templates.keys()),
            'empathy_types': list(self.empathy_responses.keys())
        }
    
    def test_fallback_coverage(self) -> Dict[str, Any]:
        """Test fallback system coverage for different scenarios"""
        test_scenarios = [
            FallbackContext(user_name="Alice", detected_emotion="sad", emotion_confidence=0.9),
            FallbackContext(user_name="Bob", detected_emotion="angry", emotion_confidence=0.8),
            FallbackContext(user_name="Carol", detected_emotion="anxious", emotion_confidence=0.7),
            FallbackContext(user_name="Dave", is_crisis=True),
            FallbackContext(user_name="Eve", conversation_type=ConversationType.GREETING),
            FallbackContext(user_name="Frank", conversation_type=ConversationType.CELEBRATION),
        ]
        
        coverage_results = {}
        
        for i, scenario in enumerate(test_scenarios):
            try:
                response = self.generate_fallback_response(scenario)
                coverage_results[f"scenario_{i+1}"] = {
                    'success': True,
                    'fallback_level': response.fallback_level.value,
                    'confidence': response.confidence,
                    'empathy_score': response.empathy_score,
                    'safety_score': response.safety_score
                }
            except Exception as e:
                coverage_results[f"scenario_{i+1}"] = {
                    'success': False,
                    'error': str(e)
                }
        
        return coverage_results

# Global fallback system instance
_fallback_system = None

def get_fallback_system() -> FallbackResponseSystem:
    """Get global fallback system instance"""
    global _fallback_system
    if _fallback_system is None:
        _fallback_system = FallbackResponseSystem()
    return _fallback_system