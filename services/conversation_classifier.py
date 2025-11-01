"""
Conversation Type and Intent Classification System
Classifies conversation types and user intents using pattern matching
"""

import re
import logging
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from enum import Enum

from services.template_models import ConversationType

logger = logging.getLogger(__name__)

class UserIntent(Enum):
    """User intent categories"""
    SEEKING_SUPPORT = "seeking_support"
    SHARING_NEWS = "sharing_news"
    ASKING_ADVICE = "asking_advice"
    CASUAL_CHAT = "casual_chat"
    VENTING = "venting"
    CELEBRATING = "celebrating"
    GREETING = "greeting"
    GOODBYE = "goodbye"
    MEMORY_RECALL = "memory_recall"
    INFORMATION_SEEKING = "information_seeking"
    EXPRESSING_GRATITUDE = "expressing_gratitude"
    MAKING_PLANS = "making_plans"

@dataclass
class ClassificationResult:
    """Result of conversation classification"""
    conversation_type: ConversationType
    user_intent: UserIntent
    confidence: float
    classification_reasons: List[str] = field(default_factory=list)
    detected_patterns: List[str] = field(default_factory=list)
    topic_indicators: List[str] = field(default_factory=list)

class ConversationClassifier:
    """
    Classifies conversation types and user intents using pattern matching
    """
    
    def __init__(self):
        self.conversation_patterns = self._load_conversation_patterns()
        self.intent_patterns = self._load_intent_patterns()
        self.topic_keywords = self._load_topic_keywords()
        self.transition_indicators = self._load_transition_indicators()
        
        # Classification statistics
        self.classification_stats = {
            'total_classifications': 0,
            'conversation_type_distribution': {},
            'intent_distribution': {},
            'high_confidence_classifications': 0
        }
        
        logger.info("ConversationClassifier initialized with pattern matching")
    
    def _load_conversation_patterns(self) -> Dict[ConversationType, List[Dict]]:
        """Load patterns for conversation type classification"""
        return {
            ConversationType.GREETING: [
                {
                    'patterns': ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening'],
                    'weight': 0.9,
                    'context': 'start_of_conversation'
                },
                {
                    'patterns': ['how are you', 'how\'s it going', 'what\'s up', 'how have you been'],
                    'weight': 0.8,
                    'context': 'greeting_inquiry'
                }
            ],
            
            ConversationType.GOODBYE: [
                {
                    'patterns': ['goodbye', 'bye', 'see you', 'talk later', 'take care', 'farewell'],
                    'weight': 0.9,
                    'context': 'end_of_conversation'
                },
                {
                    'patterns': ['gotta go', 'have to leave', 'need to run', 'catch you later'],
                    'weight': 0.8,
                    'context': 'departure_indication'
                }
            ],
            
            ConversationType.EMOTIONAL_SUPPORT: [
                {
                    'patterns': ['feeling sad', 'depressed', 'anxious', 'worried', 'stressed', 'overwhelmed'],
                    'weight': 0.9,
                    'context': 'emotional_distress'
                },
                {
                    'patterns': ['need help', 'don\'t know what to do', 'struggling', 'having a hard time'],
                    'weight': 0.8,
                    'context': 'support_seeking'
                },
                {
                    'patterns': ['feel like', 'i\'m so', 'can\'t handle', 'too much for me'],
                    'weight': 0.7,
                    'context': 'emotional_expression'
                }
            ],
            
            ConversationType.CELEBRATION: [
                {
                    'patterns': ['got promoted', 'new job', 'passed exam', 'graduated', 'engaged', 'married'],
                    'weight': 0.9,
                    'context': 'life_achievement'
                },
                {
                    'patterns': ['so excited', 'thrilled', 'amazing news', 'great news', 'wonderful'],
                    'weight': 0.8,
                    'context': 'positive_emotion'
                },
                {
                    'patterns': ['celebrate', 'party', 'success', 'accomplished', 'achieved'],
                    'weight': 0.7,
                    'context': 'celebration_indicators'
                }
            ],
            
            ConversationType.CASUAL_CHAT: [
                {
                    'patterns': ['what\'s new', 'how was your day', 'tell me about', 'what do you think'],
                    'weight': 0.7,
                    'context': 'casual_inquiry'
                },
                {
                    'patterns': ['by the way', 'speaking of', 'reminds me', 'random question'],
                    'weight': 0.6,
                    'context': 'casual_transition'
                }
            ],
            
            ConversationType.ADVICE_SEEKING: [
                {
                    'patterns': ['what should i', 'need advice', 'what would you do', 'help me decide'],
                    'weight': 0.9,
                    'context': 'direct_advice_request'
                },
                {
                    'patterns': ['not sure if', 'don\'t know whether', 'confused about', 'torn between'],
                    'weight': 0.8,
                    'context': 'decision_uncertainty'
                }
            ],
            
            ConversationType.MEMORY_RECALL: [
                {
                    'patterns': ['remember when', 'do you recall', 'we talked about', 'you mentioned'],
                    'weight': 0.9,
                    'context': 'explicit_memory_reference'
                },
                {
                    'patterns': ['last time', 'before', 'earlier', 'previously'],
                    'weight': 0.6,
                    'context': 'temporal_reference'
                }
            ]
        }
    
    def _load_intent_patterns(self) -> Dict[UserIntent, List[Dict]]:
        """Load patterns for user intent classification"""
        return {
            UserIntent.SEEKING_SUPPORT: [
                {
                    'patterns': ['need someone to talk to', 'feeling alone', 'need support', 'help me'],
                    'weight': 0.9
                },
                {
                    'patterns': ['going through', 'dealing with', 'struggling with', 'having trouble'],
                    'weight': 0.8
                }
            ],
            
            UserIntent.SHARING_NEWS: [
                {
                    'patterns': ['guess what', 'have news', 'something happened', 'want to tell you'],
                    'weight': 0.9
                },
                {
                    'patterns': ['just found out', 'heard that', 'discovered', 'learned'],
                    'weight': 0.7
                }
            ],
            
            UserIntent.ASKING_ADVICE: [
                {
                    'patterns': ['what do you think', 'should i', 'advice', 'recommend', 'suggest'],
                    'weight': 0.9
                },
                {
                    'patterns': ['opinion', 'thoughts on', 'perspective', 'input'],
                    'weight': 0.7
                }
            ],
            
            UserIntent.VENTING: [
                {
                    'patterns': ['so frustrated', 'can\'t believe', 'annoying', 'ridiculous', 'unfair'],
                    'weight': 0.8
                },
                {
                    'patterns': ['rant', 'complain', 'bothering me', 'driving me crazy'],
                    'weight': 0.9
                }
            ],
            
            UserIntent.CELEBRATING: [
                {
                    'patterns': ['so happy', 'excited to share', 'great news', 'celebration', 'achievement'],
                    'weight': 0.9
                },
                {
                    'patterns': ['proud of', 'accomplished', 'success', 'victory', 'win'],
                    'weight': 0.8
                }
            ],
            
            UserIntent.CASUAL_CHAT: [
                {
                    'patterns': ['just chatting', 'random thought', 'by the way', 'curious about'],
                    'weight': 0.7
                },
                {
                    'patterns': ['what\'s up', 'how\'s life', 'anything new', 'what\'s happening'],
                    'weight': 0.6
                }
            ],
            
            UserIntent.MEMORY_RECALL: [
                {
                    'patterns': ['remember', 'recall', 'mentioned', 'talked about', 'discussed'],
                    'weight': 0.8
                },
                {
                    'patterns': ['last time', 'before', 'previous', 'earlier conversation'],
                    'weight': 0.7
                }
            ],
            
            UserIntent.EXPRESSING_GRATITUDE: [
                {
                    'patterns': ['thank you', 'thanks', 'grateful', 'appreciate', 'helped me'],
                    'weight': 0.9
                },
                {
                    'patterns': ['means a lot', 'really helpful', 'made me feel better'],
                    'weight': 0.8
                }
            ],
            
            UserIntent.INFORMATION_SEEKING: [
                {
                    'patterns': ['tell me about', 'explain', 'what is', 'how does', 'information'],
                    'weight': 0.8
                },
                {
                    'patterns': ['curious', 'wondering', 'question', 'know more'],
                    'weight': 0.7
                }
            ]
        }
    
    def _load_topic_keywords(self) -> Dict[str, List[str]]:
        """Load topic-specific keywords"""
        return {
            'work': [
                'job', 'work', 'office', 'boss', 'colleague', 'meeting', 'project',
                'deadline', 'promotion', 'salary', 'career', 'interview', 'resume'
            ],
            'relationships': [
                'boyfriend', 'girlfriend', 'partner', 'spouse', 'husband', 'wife',
                'friend', 'family', 'parents', 'siblings', 'relationship', 'dating',
                'marriage', 'breakup', 'argument', 'fight'
            ],
            'health': [
                'doctor', 'hospital', 'medicine', 'sick', 'illness', 'pain',
                'therapy', 'mental health', 'anxiety', 'depression', 'stress'
            ],
            'education': [
                'school', 'college', 'university', 'student', 'teacher', 'exam',
                'grade', 'homework', 'study', 'class', 'degree', 'graduation'
            ],
            'family': [
                'mom', 'dad', 'mother', 'father', 'parents', 'children', 'kids',
                'brother', 'sister', 'grandparents', 'family', 'relatives'
            ],
            'hobbies': [
                'hobby', 'music', 'sports', 'reading', 'cooking', 'travel',
                'movies', 'games', 'art', 'photography', 'exercise', 'fitness'
            ]
        }
    
    def _load_transition_indicators(self) -> List[str]:
        """Load indicators of topic transitions"""
        return [
            'by the way', 'speaking of', 'that reminds me', 'on another note',
            'changing topics', 'different subject', 'also', 'additionally',
            'meanwhile', 'in other news', 'oh and', 'before i forget'
        ]
    
    def classify_conversation(self, message: str, conversation_history: List[Dict] = None) -> ClassificationResult:
        """
        Classify conversation type and user intent
        """
        try:
            self.classification_stats['total_classifications'] += 1
            
            # Preprocess message
            processed_message = self._preprocess_message(message)
            
            # Classify conversation type
            conv_type, conv_confidence, conv_reasons = self._classify_conversation_type(
                processed_message, conversation_history
            )
            
            # Classify user intent
            intent, intent_confidence, intent_reasons = self._classify_user_intent(
                processed_message, conv_type
            )
            
            # Combine confidences (weighted average)
            overall_confidence = (conv_confidence * 0.6) + (intent_confidence * 0.4)
            
            # Extract topic indicators
            topic_indicators = self._extract_topic_indicators(processed_message)
            
            # Detect patterns used
            detected_patterns = self._get_detected_patterns(processed_message)
            
            # Create result
            result = ClassificationResult(
                conversation_type=conv_type,
                user_intent=intent,
                confidence=overall_confidence,
                classification_reasons=conv_reasons + intent_reasons,
                detected_patterns=detected_patterns,
                topic_indicators=topic_indicators
            )
            
            # Update statistics
            self._update_statistics(result)
            
            logger.debug(f"Classified: {conv_type.value}/{intent.value} "
                        f"(confidence: {overall_confidence:.2f})")
            
            return result
            
        except Exception as e:
            logger.error(f"Error classifying conversation: {e}")
            return self._create_default_classification()
    
    def _preprocess_message(self, message: str) -> str:
        """Preprocess message for classification"""
        # Convert to lowercase
        processed = message.lower()
        
        # Remove extra whitespace
        processed = re.sub(r'\s+', ' ', processed).strip()
        
        # Handle contractions (same as emotion detector)
        contractions = {
            "i'm": "i am", "you're": "you are", "it's": "it is",
            "we're": "we are", "they're": "they are", "don't": "do not",
            "can't": "cannot", "won't": "will not", "isn't": "is not",
            "aren't": "are not", "wasn't": "was not", "weren't": "were not"
        }
        
        for contraction, expansion in contractions.items():
            processed = processed.replace(contraction, expansion)
        
        return processed
    
    def _classify_conversation_type(self, message: str, 
                                  conversation_history: List[Dict] = None) -> Tuple[ConversationType, float, List[str]]:
        """Classify conversation type"""
        type_scores = {}
        reasons = []
        
        # Check each conversation type
        for conv_type, pattern_groups in self.conversation_patterns.items():
            score = 0
            type_reasons = []
            
            for pattern_group in pattern_groups:
                patterns = pattern_group['patterns']
                weight = pattern_group['weight']
                context = pattern_group['context']
                
                # Check if any patterns match
                matches = sum(1 for pattern in patterns if pattern in message)
                if matches > 0:
                    pattern_score = (matches / len(patterns)) * weight
                    score = max(score, pattern_score)
                    type_reasons.append(f"{context}: {matches} pattern matches")
            
            if score > 0:
                type_scores[conv_type] = score
                reasons.extend(type_reasons)
        
        # Apply conversation history context
        if conversation_history:
            type_scores = self._apply_conversation_context(type_scores, conversation_history)
        
        # Determine best type
        if type_scores:
            best_type = max(type_scores, key=type_scores.get)
            confidence = type_scores[best_type]
        else:
            best_type = ConversationType.CASUAL_CHAT
            confidence = 0.3
            reasons.append("default: no strong patterns detected")
        
        return best_type, confidence, reasons
    
    def _classify_user_intent(self, message: str, conv_type: ConversationType) -> Tuple[UserIntent, float, List[str]]:
        """Classify user intent"""
        intent_scores = {}
        reasons = []
        
        # Check each intent
        for intent, pattern_groups in self.intent_patterns.items():
            score = 0
            intent_reasons = []
            
            for pattern_group in pattern_groups:
                patterns = pattern_group['patterns']
                weight = pattern_group['weight']
                
                # Check if any patterns match
                matches = sum(1 for pattern in patterns if pattern in message)
                if matches > 0:
                    pattern_score = (matches / len(patterns)) * weight
                    score = max(score, pattern_score)
                    intent_reasons.append(f"{intent.value}: {matches} pattern matches")
            
            if score > 0:
                intent_scores[intent] = score
                reasons.extend(intent_reasons)
        
        # Apply conversation type bias
        intent_scores = self._apply_conversation_type_bias(intent_scores, conv_type)
        
        # Determine best intent
        if intent_scores:
            best_intent = max(intent_scores, key=intent_scores.get)
            confidence = intent_scores[best_intent]
        else:
            best_intent = UserIntent.CASUAL_CHAT
            confidence = 0.3
            reasons.append("default: no strong intent patterns detected")
        
        return best_intent, confidence, reasons
    
    def _apply_conversation_context(self, type_scores: Dict[ConversationType, float], 
                                  conversation_history: List[Dict]) -> Dict[ConversationType, float]:
        """Apply conversation history context to type scores"""
        if not conversation_history:
            return type_scores
        
        # Boost greeting if this is start of conversation
        if len(conversation_history) == 0:
            if ConversationType.GREETING in type_scores:
                type_scores[ConversationType.GREETING] *= 1.3
        
        # Boost goodbye if conversation has been going on
        elif len(conversation_history) > 5:
            if ConversationType.GOODBYE in type_scores:
                type_scores[ConversationType.GOODBYE] *= 1.2
        
        # Check for topic continuity
        if len(conversation_history) > 0:
            last_message = conversation_history[-1].get('message', '').lower()
            
            # If previous message was emotional, boost emotional support
            emotional_words = ['sad', 'angry', 'worried', 'stressed', 'anxious']
            if any(word in last_message for word in emotional_words):
                if ConversationType.EMOTIONAL_SUPPORT in type_scores:
                    type_scores[ConversationType.EMOTIONAL_SUPPORT] *= 1.2
        
        return type_scores
    
    def _apply_conversation_type_bias(self, intent_scores: Dict[UserIntent, float], 
                                    conv_type: ConversationType) -> Dict[UserIntent, float]:
        """Apply conversation type bias to intent scores"""
        # Define intent-type relationships
        type_intent_boosts = {
            ConversationType.EMOTIONAL_SUPPORT: [UserIntent.SEEKING_SUPPORT, UserIntent.VENTING],
            ConversationType.CELEBRATION: [UserIntent.CELEBRATING, UserIntent.SHARING_NEWS],
            ConversationType.ADVICE_SEEKING: [UserIntent.ASKING_ADVICE],
            ConversationType.MEMORY_RECALL: [UserIntent.MEMORY_RECALL],
            ConversationType.GREETING: [UserIntent.CASUAL_CHAT],
            ConversationType.GOODBYE: [UserIntent.CASUAL_CHAT]
        }
        
        # Apply boosts
        if conv_type in type_intent_boosts:
            for intent in type_intent_boosts[conv_type]:
                if intent in intent_scores:
                    intent_scores[intent] *= 1.3
        
        return intent_scores
    
    def _extract_topic_indicators(self, message: str) -> List[str]:
        """Extract topic indicators from message"""
        indicators = []
        
        for topic, keywords in self.topic_keywords.items():
            matches = [keyword for keyword in keywords if keyword in message]
            if matches:
                indicators.append(f"{topic}: {', '.join(matches[:3])}")
        
        return indicators
    
    def _get_detected_patterns(self, message: str) -> List[str]:
        """Get list of patterns that were detected"""
        detected = []
        
        # Check conversation type patterns
        for conv_type, pattern_groups in self.conversation_patterns.items():
            for pattern_group in pattern_groups:
                for pattern in pattern_group['patterns']:
                    if pattern in message:
                        detected.append(f"{conv_type.value}: {pattern}")
        
        # Check intent patterns
        for intent, pattern_groups in self.intent_patterns.items():
            for pattern_group in pattern_groups:
                for pattern in pattern_group['patterns']:
                    if pattern in message:
                        detected.append(f"{intent.value}: {pattern}")
        
        return detected[:10]  # Limit to avoid clutter
    
    def _create_default_classification(self) -> ClassificationResult:
        """Create default classification when detection fails"""
        return ClassificationResult(
            conversation_type=ConversationType.CASUAL_CHAT,
            user_intent=UserIntent.CASUAL_CHAT,
            confidence=0.3,
            classification_reasons=["default: classification error"],
            detected_patterns=[],
            topic_indicators=[]
        )
    
    def _update_statistics(self, result: ClassificationResult):
        """Update classification statistics"""
        if result.confidence >= 0.7:
            self.classification_stats['high_confidence_classifications'] += 1
        
        # Update distributions
        conv_type = result.conversation_type.value
        intent = result.user_intent.value
        
        self.classification_stats['conversation_type_distribution'][conv_type] = \
            self.classification_stats['conversation_type_distribution'].get(conv_type, 0) + 1
        
        self.classification_stats['intent_distribution'][intent] = \
            self.classification_stats['intent_distribution'].get(intent, 0) + 1
    
    def detect_topic_transition(self, message: str) -> Tuple[bool, Optional[str]]:
        """Detect if message indicates a topic transition"""
        message_lower = message.lower()
        
        for indicator in self.transition_indicators:
            if indicator in message_lower:
                return True, indicator
        
        return False, None
    
    def get_supported_types_and_intents(self) -> Dict[str, List[str]]:
        """Get lists of supported conversation types and intents"""
        return {
            'conversation_types': [t.value for t in ConversationType],
            'user_intents': [i.value for i in UserIntent]
        }
    
    def get_classification_stats(self) -> Dict[str, any]:
        """Get classification statistics"""
        total = self.classification_stats['total_classifications']
        high_conf_rate = (
            self.classification_stats['high_confidence_classifications'] / total * 100
            if total > 0 else 0
        )
        
        return {
            'total_classifications': total,
            'high_confidence_rate': round(high_conf_rate, 2),
            'conversation_type_distribution': self.classification_stats['conversation_type_distribution'].copy(),
            'intent_distribution': self.classification_stats['intent_distribution'].copy(),
            'supported_types': len(ConversationType),
            'supported_intents': len(UserIntent)
        }
    
    def reset_stats(self):
        """Reset classification statistics"""
        self.classification_stats = {
            'total_classifications': 0,
            'conversation_type_distribution': {},
            'intent_distribution': {},
            'high_confidence_classifications': 0
        }

# Global conversation classifier instance
_conversation_classifier = None

def get_conversation_classifier() -> ConversationClassifier:
    """Get global conversation classifier instance"""
    global _conversation_classifier
    if _conversation_classifier is None:
        _conversation_classifier = ConversationClassifier()
    return _conversation_classifier