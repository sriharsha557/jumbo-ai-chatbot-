"""
Template Variation and Rotation Engine
Generates dynamic variations and manages rotation to avoid monotonous responses
"""

import re
import random
import logging
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from services.template_models import ConversationTemplate, PersonalityTone

logger = logging.getLogger(__name__)

@dataclass
class VariationContext:
    """Context for generating template variations"""
    user_name: str
    emotion: str
    recent_memories: List[str] = field(default_factory=list)
    friend_names: List[str] = field(default_factory=list)
    conversation_length: int = 0
    time_of_day: Optional[str] = None
    user_preferences: Dict[str, any] = field(default_factory=dict)

@dataclass
class RotationState:
    """Tracks rotation state for template variations"""
    template_id: str
    used_variations: List[int] = field(default_factory=list)
    last_used_index: int = -1
    rotation_count: int = 0
    last_reset: datetime = field(default_factory=datetime.now)

class TemplateVariationEngine:
    """
    Generates dynamic variations and manages rotation to prevent repetitive responses
    """
    
    def __init__(self):
        self.rotation_states: Dict[str, Dict[str, RotationState]] = {}  # user_id -> template_id -> state
        self.variation_patterns = self._load_variation_patterns()
        self.personality_modifiers = self._load_personality_modifiers()
        self.contextual_enhancers = self._load_contextual_enhancers()
    
    def _load_variation_patterns(self) -> Dict[str, List[str]]:
        """Load patterns for generating variations"""
        return {
            'greeting_starters': [
                "Hello {user_name}!", "Hi there {user_name}!", "Hey {user_name}!",
                "Welcome back {user_name}!", "Good to see you {user_name}!",
                "Hi {user_name}, wonderful to connect again!"
            ],
            'empathy_expressions': [
                "I can sense", "I hear", "I understand", "I feel", "I recognize",
                "I can see", "I notice", "I'm aware", "I perceive"
            ],
            'support_phrases': [
                "I'm here with you", "You're not alone", "I'm here to listen",
                "I'm alongside you", "I'm present with you", "I'm here for you"
            ],
            'validation_phrases': [
                "That makes complete sense", "Your feelings are valid", 
                "That's completely understandable", "Anyone would feel that way",
                "Your reaction is natural", "That's a normal response"
            ],
            'curiosity_starters': [
                "I'm curious about", "I'd love to know more about", "Tell me about",
                "I'm interested in", "Help me understand", "Share with me about"
            ],
            'encouragement_phrases': [
                "You're doing great", "That's wonderful", "How amazing",
                "That's fantastic", "You should be proud", "That's incredible"
            ]
        }
    
    def _load_personality_modifiers(self) -> Dict[PersonalityTone, Dict[str, List[str]]]:
        """Load personality-specific modifiers"""
        return {
            PersonalityTone.EMPATHETIC: {
                'adjectives': ['gentle', 'understanding', 'compassionate', 'caring'],
                'adverbs': ['gently', 'softly', 'warmly', 'tenderly'],
                'phrases': ['with understanding', 'with compassion', 'with care']
            },
            PersonalityTone.ENCOURAGING: {
                'adjectives': ['inspiring', 'uplifting', 'motivating', 'positive'],
                'adverbs': ['encouragingly', 'positively', 'hopefully', 'optimistically'],
                'phrases': ['with enthusiasm', 'with hope', 'with confidence']
            },
            PersonalityTone.GENTLE: {
                'adjectives': ['soft', 'peaceful', 'calm', 'soothing'],
                'adverbs': ['gently', 'peacefully', 'calmly', 'softly'],
                'phrases': ['with gentleness', 'with peace', 'with calm']
            },
            PersonalityTone.SUPPORTIVE: {
                'adjectives': ['strong', 'reliable', 'steady', 'dependable'],
                'adverbs': ['supportively', 'steadily', 'reliably', 'consistently'],
                'phrases': ['with support', 'with strength', 'with reliability']
            },
            PersonalityTone.CURIOUS: {
                'adjectives': ['interested', 'engaged', 'attentive', 'fascinated'],
                'adverbs': ['curiously', 'attentively', 'interestedly', 'eagerly'],
                'phrases': ['with curiosity', 'with interest', 'with attention']
            },
            PersonalityTone.VALIDATING: {
                'adjectives': ['affirming', 'confirming', 'acknowledging', 'recognizing'],
                'adverbs': ['validatingly', 'affirmingly', 'acknowledgingly', 'recognizingly'],
                'phrases': ['with validation', 'with affirmation', 'with recognition']
            },
            PersonalityTone.CALMING: {
                'adjectives': ['peaceful', 'tranquil', 'serene', 'relaxing'],
                'adverbs': ['calmly', 'peacefully', 'serenely', 'tranquilly'],
                'phrases': ['with peace', 'with tranquility', 'with serenity']
            }
        }
    
    def _load_contextual_enhancers(self) -> Dict[str, List[str]]:
        """Load context-specific enhancers"""
        return {
            'memory_references': [
                "I remember when you mentioned {memory}",
                "Thinking back to what you shared about {memory}",
                "I recall you telling me about {memory}",
                "You mentioned {memory} before"
            ],
            'friend_references': [
                "How is {friend_name} doing?",
                "Have you talked to {friend_name} about this?",
                "What does {friend_name} think about this?",
                "I remember you mentioning {friend_name}"
            ],
            'time_contextual': {
                'morning': ['starting fresh', 'new beginning', 'morning energy', 'dawn of possibility'],
                'afternoon': ['midday reflection', 'afternoon thoughts', 'continuing journey'],
                'evening': ['evening contemplation', 'day reflection', 'peaceful evening'],
                'night': ['nighttime peace', 'quiet moments', 'restful thoughts']
            }
        }
    
    def generate_variation(self, template: ConversationTemplate, 
                          context: VariationContext) -> str:
        """
        Generate a contextual variation of the template
        """
        try:
            # Get the base variation using rotation
            base_variation = self._get_rotated_variation(template, context.user_name)
            
            # Apply contextual enhancements
            enhanced_variation = self._apply_contextual_enhancements(
                base_variation, template, context
            )
            
            # Apply personality modifications
            personality_enhanced = self._apply_personality_modifications(
                enhanced_variation, template.personality_tone, context
            )
            
            # Fill in placeholders
            final_variation = self._fill_placeholders(personality_enhanced, context)
            
            logger.debug(f"Generated variation for template {template.id}: {final_variation[:50]}...")
            return final_variation
            
        except Exception as e:
            logger.error(f"Error generating variation for template {template.id}: {e}")
            # Fallback to base template with basic placeholder filling
            return self._fill_placeholders(template.base_template, context)
    
    def _get_rotated_variation(self, template: ConversationTemplate, user_id: str) -> str:
        """Get next variation using rotation algorithm"""
        rotation_state = self._get_rotation_state(user_id, template.id)
        
        # Determine available variations
        available_variations = [template.base_template] + template.variations
        
        if len(available_variations) <= 1:
            return template.base_template
        
        # Check if we need to reset rotation (all variations used or time-based reset)
        if (len(rotation_state.used_variations) >= len(available_variations) or
            self._should_reset_rotation(rotation_state)):
            self._reset_rotation_state(rotation_state)
        
        # Find unused variations
        unused_indices = [
            i for i in range(len(available_variations))
            if i not in rotation_state.used_variations
        ]
        
        if not unused_indices:
            # Fallback: reset and use any variation
            self._reset_rotation_state(rotation_state)
            unused_indices = list(range(len(available_variations)))
        
        # Select variation (prefer unused, avoid recently used)
        selected_index = self._select_variation_index(unused_indices, rotation_state)
        
        # Update rotation state
        rotation_state.used_variations.append(selected_index)
        rotation_state.last_used_index = selected_index
        rotation_state.rotation_count += 1
        
        return available_variations[selected_index]
    
    def _apply_contextual_enhancements(self, variation: str, template: ConversationTemplate,
                                     context: VariationContext) -> str:
        """Apply context-specific enhancements to the variation"""
        enhanced = variation
        
        # Add memory references if appropriate
        if context.recent_memories and random.random() < 0.3:  # 30% chance
            memory_ref = random.choice(self.contextual_enhancers['memory_references'])
            memory = random.choice(context.recent_memories)
            memory_phrase = memory_ref.format(memory=memory)
            enhanced = f"{enhanced} {memory_phrase}."
        
        # Add friend references if appropriate
        if (context.friend_names and 
            template.conversation_type.value in ['casual_chat', 'memory_recall'] and
            random.random() < 0.25):  # 25% chance
            friend_ref = random.choice(self.contextual_enhancers['friend_references'])
            friend = random.choice(context.friend_names)
            friend_phrase = friend_ref.format(friend_name=friend)
            enhanced = f"{enhanced} {friend_phrase}"
        
        # Add time-contextual elements
        if context.time_of_day and context.time_of_day in self.contextual_enhancers['time_contextual']:
            time_elements = self.contextual_enhancers['time_contextual'][context.time_of_day]
            if random.random() < 0.2:  # 20% chance
                time_element = random.choice(time_elements)
                enhanced = enhanced.replace('today', f'this {context.time_of_day}')
        
        return enhanced
    
    def _apply_personality_modifications(self, variation: str, personality_tone: PersonalityTone,
                                       context: VariationContext) -> str:
        """Apply personality-specific modifications"""
        if personality_tone not in self.personality_modifiers:
            return variation
        
        modifiers = self.personality_modifiers[personality_tone]
        modified = variation
        
        # Occasionally add personality-specific phrases
        if random.random() < 0.3:  # 30% chance
            phrase = random.choice(modifiers['phrases'])
            # Insert phrase naturally
            if '.' in modified:
                parts = modified.split('.', 1)
                modified = f"{parts[0]} {phrase}.{parts[1] if len(parts) > 1 else ''}"
        
        # Replace generic words with personality-specific ones
        if random.random() < 0.4:  # 40% chance
            # Replace "good" with personality-specific adjectives
            if 'good' in modified.lower():
                replacement = random.choice(modifiers['adjectives'])
                modified = re.sub(r'\bgood\b', replacement, modified, flags=re.IGNORECASE)
        
        return modified
    
    def _fill_placeholders(self, variation: str, context: VariationContext) -> str:
        """Fill in placeholders with context information"""
        filled = variation
        
        # Basic placeholder filling
        filled = filled.replace('{user_name}', context.user_name)
        
        # Fill friend name if present
        if '{friend_name}' in filled and context.friend_names:
            friend_name = random.choice(context.friend_names)
            filled = filled.replace('{friend_name}', friend_name)
        
        # Fill memory if present
        if '{memory}' in filled and context.recent_memories:
            memory = random.choice(context.recent_memories)
            filled = filled.replace('{memory}', memory)
        
        # Remove any unfilled placeholders gracefully
        filled = re.sub(r'\{[^}]+\}', '', filled)
        
        # Clean up extra spaces
        filled = re.sub(r'\s+', ' ', filled).strip()
        
        return filled
    
    def _get_rotation_state(self, user_id: str, template_id: str) -> RotationState:
        """Get or create rotation state for user and template"""
        if user_id not in self.rotation_states:
            self.rotation_states[user_id] = {}
        
        if template_id not in self.rotation_states[user_id]:
            self.rotation_states[user_id][template_id] = RotationState(template_id=template_id)
        
        return self.rotation_states[user_id][template_id]
    
    def _should_reset_rotation(self, rotation_state: RotationState) -> bool:
        """Determine if rotation should be reset"""
        # Reset after 24 hours
        time_threshold = datetime.now() - timedelta(hours=24)
        if rotation_state.last_reset < time_threshold:
            return True
        
        # Reset after many rotations to prevent predictability
        if rotation_state.rotation_count > 20:
            return True
        
        return False
    
    def _reset_rotation_state(self, rotation_state: RotationState):
        """Reset rotation state"""
        rotation_state.used_variations.clear()
        rotation_state.last_used_index = -1
        rotation_state.rotation_count = 0
        rotation_state.last_reset = datetime.now()
    
    def _select_variation_index(self, unused_indices: List[int], 
                               rotation_state: RotationState) -> int:
        """Select variation index with anti-repetition logic"""
        if len(unused_indices) == 1:
            return unused_indices[0]
        
        # Avoid recently used variation if possible
        if rotation_state.last_used_index in unused_indices and len(unused_indices) > 1:
            available = [idx for idx in unused_indices if idx != rotation_state.last_used_index]
            if available:
                return random.choice(available)
        
        return random.choice(unused_indices)
    
    def generate_follow_up_question(self, template: ConversationTemplate,
                                   context: VariationContext) -> Optional[str]:
        """Generate a contextual follow-up question"""
        if not template.follow_up_questions:
            return None
        
        # Select follow-up question with some variation
        base_question = random.choice(template.follow_up_questions)
        
        # Apply contextual modifications
        enhanced_question = self._enhance_follow_up_question(base_question, context)
        
        return self._fill_placeholders(enhanced_question, context)
    
    def _enhance_follow_up_question(self, question: str, context: VariationContext) -> str:
        """Enhance follow-up question with context"""
        enhanced = question
        
        # Add conversation length awareness
        if context.conversation_length > 5:
            # Make questions more specific in longer conversations
            if 'how' in enhanced.lower() and random.random() < 0.3:
                enhanced = enhanced.replace('How', 'In what specific way')
        
        # Add time context
        if context.time_of_day == 'evening' and 'today' in enhanced:
            enhanced = enhanced.replace('today', 'this evening')
        elif context.time_of_day == 'morning' and 'today' in enhanced:
            enhanced = enhanced.replace('today', 'this morning')
        
        return enhanced
    
    def get_variation_stats(self, user_id: str) -> Dict[str, any]:
        """Get variation statistics for a user"""
        if user_id not in self.rotation_states:
            return {'total_templates': 0, 'rotation_states': {}}
        
        user_states = self.rotation_states[user_id]
        stats = {
            'total_templates': len(user_states),
            'rotation_states': {},
            'total_rotations': 0,
            'avg_variations_per_template': 0
        }
        
        total_rotations = 0
        total_variations = 0
        
        for template_id, state in user_states.items():
            stats['rotation_states'][template_id] = {
                'rotation_count': state.rotation_count,
                'used_variations': len(state.used_variations),
                'last_reset': state.last_reset.isoformat(),
                'last_used_index': state.last_used_index
            }
            total_rotations += state.rotation_count
            total_variations += len(state.used_variations)
        
        stats['total_rotations'] = total_rotations
        if len(user_states) > 0:
            stats['avg_variations_per_template'] = total_variations / len(user_states)
        
        return stats
    
    def reset_user_rotations(self, user_id: str):
        """Reset all rotation states for a user"""
        if user_id in self.rotation_states:
            for state in self.rotation_states[user_id].values():
                self._reset_rotation_state(state)
            logger.info(f"Reset rotation states for user: {user_id}")

# Global variation engine instance
_variation_engine = None

def get_variation_engine() -> TemplateVariationEngine:
    """Get global variation engine instance"""
    global _variation_engine
    if _variation_engine is None:
        _variation_engine = TemplateVariationEngine()
    return _variation_engine