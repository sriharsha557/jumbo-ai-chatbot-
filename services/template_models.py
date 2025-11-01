"""
Template Models for Enhanced Conversation System
Defines data structures for conversation templates and related components
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import json
import random
from datetime import datetime

class EmotionCategory(Enum):
    """Emotion categories for template selection"""
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    ANXIOUS = "anxious"
    CONFUSED = "confused"
    FRUSTRATED = "frustrated"
    TIRED = "tired"
    NEUTRAL = "neutral"
    EXCITED = "excited"
    WORRIED = "worried"

class ConversationType(Enum):
    """Types of conversations for template selection"""
    GREETING = "greeting"
    GOODBYE = "goodbye"
    EMOTIONAL_SUPPORT = "emotional_support"
    CASUAL_CHAT = "casual_chat"
    MEMORY_RECALL = "memory_recall"
    ADVICE_SEEKING = "advice_seeking"
    CELEBRATION = "celebration"
    VENTING = "venting"

class PersonalityTone(Enum):
    """Personality tones for consistent voice"""
    EMPATHETIC = "empathetic"
    ENCOURAGING = "encouraging"
    GENTLE = "gentle"
    SUPPORTIVE = "supportive"
    CURIOUS = "curious"
    VALIDATING = "validating"
    CALMING = "calming"

@dataclass
class ConversationTemplate:
    """
    Enhanced conversation template with emotion-specific variations
    """
    id: str
    category: str  # emotion or conversation type
    emotion_tags: List[str]
    conversation_type: ConversationType
    base_template: str
    variations: List[str]
    follow_up_questions: List[str]
    context_requirements: List[str]  # Required context keys like 'user_name', 'recent_memory'
    personality_tone: PersonalityTone
    usage_weight: float = 1.0  # For rotation algorithm
    min_confidence: float = 0.5  # Minimum emotion confidence to use this template
    
    def __post_init__(self):
        """Validate template after initialization"""
        if not self.variations:
            self.variations = [self.base_template]
        
        if self.usage_weight <= 0:
            self.usage_weight = 1.0

    def get_random_variation(self) -> str:
        """Get a random variation of the template"""
        if self.variations:
            return random.choice(self.variations)
        return self.base_template
    
    def get_random_follow_up(self) -> Optional[str]:
        """Get a random follow-up question"""
        if self.follow_up_questions:
            return random.choice(self.follow_up_questions)
        return None
    
    def matches_emotion(self, emotion: str, confidence: float = 1.0) -> bool:
        """Check if template matches the given emotion"""
        return (emotion.lower() in [tag.lower() for tag in self.emotion_tags] and 
                confidence >= self.min_confidence)
    
    def matches_context(self, available_context: List[str]) -> bool:
        """Check if required context is available"""
        if not self.context_requirements:
            return True
        return all(req in available_context for req in self.context_requirements)

@dataclass
class TemplateUsageTracker:
    """
    Tracks template usage to prevent repetition
    """
    user_id: str
    template_usage: Dict[str, List[datetime]] = field(default_factory=dict)
    max_history: int = 10  # Keep last 10 usages per template
    
    def record_usage(self, template_id: str):
        """Record template usage"""
        if template_id not in self.template_usage:
            self.template_usage[template_id] = []
        
        self.template_usage[template_id].append(datetime.now())
        
        # Keep only recent usages
        if len(self.template_usage[template_id]) > self.max_history:
            self.template_usage[template_id] = self.template_usage[template_id][-self.max_history:]
    
    def get_usage_count(self, template_id: str, hours_back: int = 24) -> int:
        """Get usage count for template in last N hours"""
        if template_id not in self.template_usage:
            return 0
        
        cutoff_time = datetime.now().timestamp() - (hours_back * 3600)
        recent_usages = [
            usage for usage in self.template_usage[template_id]
            if usage.timestamp() > cutoff_time
        ]
        return len(recent_usages)
    
    def calculate_anti_repetition_score(self, template_id: str) -> float:
        """
        Calculate score to avoid repetition (higher = less recently used)
        """
        recent_usage_count = self.get_usage_count(template_id, hours_back=24)
        
        if recent_usage_count == 0:
            return 1.0
        elif recent_usage_count == 1:
            return 0.8
        elif recent_usage_count == 2:
            return 0.5
        else:
            return 0.2  # Heavily penalize overused templates

@dataclass
class TemplateSelectionCriteria:
    """
    Criteria for selecting the best template
    """
    emotion: str
    emotion_confidence: float
    conversation_type: ConversationType
    available_context: List[str]
    user_id: str
    personality_preference: Optional[PersonalityTone] = None
    
    def matches_template(self, template: ConversationTemplate) -> bool:
        """Check if template matches all criteria"""
        return (
            template.matches_emotion(self.emotion, self.emotion_confidence) and
            template.conversation_type == self.conversation_type and
            template.matches_context(self.available_context)
        )

@dataclass
class TemplateScore:
    """
    Scoring system for template selection
    """
    template_id: str
    emotion_match_score: float = 0.0
    context_match_score: float = 0.0
    anti_repetition_score: float = 0.0
    personality_match_score: float = 0.0
    total_score: float = 0.0
    
    def calculate_total_score(self):
        """Calculate weighted total score"""
        self.total_score = (
            self.emotion_match_score * 0.4 +
            self.context_match_score * 0.2 +
            self.anti_repetition_score * 0.3 +
            self.personality_match_score * 0.1
        )

class TemplateValidationError(Exception):
    """Exception raised for template validation errors"""
    pass

def validate_template(template_data: Dict[str, Any]) -> bool:
    """
    Validate template data structure
    """
    required_fields = ['id', 'category', 'emotion_tags', 'base_template', 'conversation_type']
    
    for field in required_fields:
        if field not in template_data:
            raise TemplateValidationError(f"Missing required field: {field}")
    
    # Validate emotion tags
    if not isinstance(template_data['emotion_tags'], list):
        raise TemplateValidationError("emotion_tags must be a list")
    
    # Validate conversation type
    try:
        ConversationType(template_data['conversation_type'])
    except ValueError:
        raise TemplateValidationError(f"Invalid conversation_type: {template_data['conversation_type']}")
    
    # Validate personality tone if provided
    if 'personality_tone' in template_data:
        try:
            PersonalityTone(template_data['personality_tone'])
        except ValueError:
            raise TemplateValidationError(f"Invalid personality_tone: {template_data['personality_tone']}")
    
    return True

def create_template_from_dict(template_data: Dict[str, Any]) -> ConversationTemplate:
    """
    Create ConversationTemplate from dictionary data
    """
    validate_template(template_data)
    
    return ConversationTemplate(
        id=template_data['id'],
        category=template_data['category'],
        emotion_tags=template_data['emotion_tags'],
        conversation_type=ConversationType(template_data['conversation_type']),
        base_template=template_data['base_template'],
        variations=template_data.get('variations', []),
        follow_up_questions=template_data.get('follow_up_questions', []),
        context_requirements=template_data.get('context_requirements', []),
        personality_tone=PersonalityTone(template_data.get('personality_tone', 'empathetic')),
        usage_weight=template_data.get('usage_weight', 1.0),
        min_confidence=template_data.get('min_confidence', 0.5)
    )