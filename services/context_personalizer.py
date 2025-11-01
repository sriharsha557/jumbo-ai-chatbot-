"""
Context Integration for Response Personalization
Integrates user context into template responses for personalized conversations
"""

import logging
import re
import random
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

from services.smart_context_extractor import UserContext
from services.memory_retrieval_service import MemorySearchResult, PreferenceProfile
from services.template_models import ConversationTemplate

logger = logging.getLogger(__name__)

@dataclass
class PersonalizationContext:
    """Context for personalizing responses"""
    user_context: UserContext
    template: ConversationTemplate
    current_message: str
    conversation_length: int = 0
    relevant_memories: List[MemorySearchResult] = None
    user_preferences: PreferenceProfile = None

class ContextPersonalizer:
    """
    Integrates user context into responses for personalized conversations
    """
    
    def __init__(self):
        self.personalization_patterns = self._load_personalization_patterns()
        self.memory_integration_templates = self._load_memory_templates()
        self.relationship_phrases = self._load_relationship_phrases()
        
        logger.info("ContextPersonalizer initialized")
    
    def _load_personalization_patterns(self) -> Dict[str, List[str]]:
        """Load patterns for personalizing responses"""
        return {
            'memory_connectors': [
                "I remember when you mentioned {memory}",
                "Speaking of what you told me about {memory}",
                "This reminds me of when you shared about {memory}",
                "I recall you saying something about {memory}",
                "Thinking back to our conversation about {memory}"
            ],
            'relationship_references': [
                "How is {friend_name} doing with this?",
                "Have you talked to {friend_name} about this?",
                "What would {friend_name} say about this?",
                "I remember you mentioning {friend_name}",
                "Does {friend_name} know about this?"
            ],
            'emotion_acknowledgments': [
                "I can sense you're feeling {emotion}",
                "It sounds like you're experiencing {emotion}",
                "I hear the {emotion} in your words",
                "Your {emotion} is completely understandable",
                "I recognize that {emotion} feeling"
            ],
            'preference_adaptations': {
                'short': ["Let me be brief:", "In short:", "Simply put:"],
                'medium': ["Here's what I'm thinking:", "Let me share:", "I want to say:"],
                'long': ["Let me take a moment to really think about this:", "I'd like to explore this with you:", "There's a lot to consider here:"]
            }
        }
    
    def _load_memory_templates(self) -> Dict[str, List[str]]:
        """Load templates for integrating memories"""
        return {
            'person_memory': [
                "I remember you telling me about {name}. {original_response}",
                "This makes me think of {name} that you mentioned. {original_response}",
                "Speaking of relationships, how is {name}? {original_response}"
            ],
            'preference_memory': [
                "I know you mentioned liking {preference}. {original_response}",
                "This relates to what you shared about {preference}. {original_response}",
                "Given what you told me about {preference}, {original_response}"
            ],
            'experience_memory': [
                "This reminds me of your experience with {experience}. {original_response}",
                "I recall you going through something similar with {experience}. {original_response}",
                "Like when you dealt with {experience}, {original_response}"
            ]
        }
    
    def _load_relationship_phrases(self) -> Dict[str, List[str]]:
        """Load phrases for different relationship types"""
        return {
            'friend': [
                "your friend {name}",
                "{name}, who you're close with",
                "your buddy {name}",
                "{name}, your friend"
            ],
            'family': [
                "your family member {name}",
                "{name} from your family",
                "your relative {name}",
                "{name}, who's family to you"
            ],
            'colleague': [
                "your colleague {name}",
                "{name} from work",
                "your coworker {name}",
                "{name}, who you work with"
            ],
            'partner': [
                "your partner {name}",
                "{name}, who's special to you",
                "your significant other {name}",
                "{name}, your partner"
            ]
        }
    
    def personalize_response(self, template_response: str, 
                           personalization_context: PersonalizationContext) -> str:
        """
        Personalize a template response with user context
        """
        try:
            # Start with the base response
            personalized = template_response
            
            # Apply basic context substitutions
            personalized = self._apply_basic_substitutions(personalized, personalization_context)
            
            # Integrate memories if relevant
            personalized = self._integrate_relevant_memories(personalized, personalization_context)
            
            # Add relationship context
            personalized = self._add_relationship_context(personalized, personalization_context)
            
            # Adapt to user preferences
            personalized = self._adapt_to_preferences(personalized, personalization_context)
            
            # Add emotional context
            personalized = self._add_emotional_context(personalized, personalization_context)
            
            # Final cleanup and validation
            personalized = self._cleanup_response(personalized)
            
            logger.debug(f"Personalized response: {personalized[:50]}...")
            return personalized
            
        except Exception as e:
            logger.error(f"Error personalizing response: {e}")
            # Fallback to basic substitution
            return self._apply_basic_substitutions(template_response, personalization_context)
    
    def _apply_basic_substitutions(self, response: str, context: PersonalizationContext) -> str:
        """Apply basic context substitutions"""
        substituted = response
        
        # User name substitution
        substituted = substituted.replace('{user_name}', context.user_context.preferred_name)
        
        # Remove any remaining unfilled placeholders
        substituted = re.sub(r'\{[^}]+\}', '', substituted)
        
        return substituted.strip()
    
    def _integrate_relevant_memories(self, response: str, context: PersonalizationContext) -> str:
        """Integrate relevant memories into the response"""
        if not context.relevant_memories or len(context.relevant_memories) == 0:
            return response
        
        # Don't add memories to very short responses
        if len(response) < 50:
            return response
        
        # Select most relevant memory
        best_memory = context.relevant_memories[0]
        
        # Only integrate if relevance is high enough
        if best_memory.relevance_score < 0.6:
            return response
        
        memory_data = best_memory.memory
        memory_type = memory_data.get('memory_type', 'fact')
        
        # Choose integration template based on memory type
        if memory_type == 'person' and memory_data.get('name'):
            return self._integrate_person_memory(response, memory_data, context)
        elif memory_type == 'preference':
            return self._integrate_preference_memory(response, memory_data, context)
        else:
            return self._integrate_general_memory(response, memory_data, context)
    
    def _integrate_person_memory(self, response: str, memory: Dict, context: PersonalizationContext) -> str:
        """Integrate person/relationship memory"""
        name = memory.get('name', '')
        if not name:
            return response
        
        # Choose a person memory template
        templates = self.memory_integration_templates['person_memory']
        template = random.choice(templates)
        
        # Apply template
        integrated = template.format(name=name, original_response=response)
        
        return integrated
    
    def _integrate_preference_memory(self, response: str, memory: Dict, context: PersonalizationContext) -> str:
        """Integrate preference memory"""
        fact = memory.get('fact', '')
        if not fact:
            return response
        
        # Extract preference from fact
        preference = self._extract_preference_from_fact(fact)
        if not preference:
            return response
        
        # Choose a preference memory template
        templates = self.memory_integration_templates['preference_memory']
        template = random.choice(templates)
        
        # Apply template
        integrated = template.format(preference=preference, original_response=response)
        
        return integrated
    
    def _integrate_general_memory(self, response: str, memory: Dict, context: PersonalizationContext) -> str:
        """Integrate general memory"""
        fact = memory.get('fact', '')
        if not fact or len(fact) > 100:  # Don't use very long facts
            return response
        
        # Add memory reference naturally
        memory_connectors = self.personalization_patterns['memory_connectors']
        connector = random.choice(memory_connectors)
        
        # Truncate fact if too long
        short_fact = fact[:50] + "..." if len(fact) > 50 else fact
        
        memory_reference = connector.format(memory=short_fact)
        
        # Integrate into response
        return f"{memory_reference}. {response}"
    
    def _add_relationship_context(self, response: str, context: PersonalizationContext) -> str:
        """Add relationship context to response"""
        relationships = context.user_context.key_relationships
        
        if not relationships or len(response) > 200:  # Don't add to long responses
            return response
        
        # Randomly decide whether to add relationship context (30% chance)
        if random.random() > 0.3:
            return response
        
        # Choose a relationship to reference
        name, relationship = random.choice(list(relationships.items()))
        
        # Get appropriate phrase for relationship type
        relationship_type = relationship.lower()
        if relationship_type not in self.relationship_phrases:
            relationship_type = 'friend'  # Default
        
        phrases = self.relationship_phrases[relationship_type]
        phrase = random.choice(phrases).format(name=name)
        
        # Add relationship reference
        relationship_refs = self.personalization_patterns['relationship_references']
        ref_template = random.choice(relationship_refs)
        relationship_question = ref_template.format(friend_name=name)
        
        return f"{response} {relationship_question}"
    
    def _adapt_to_preferences(self, response: str, context: PersonalizationContext) -> str:
        """Adapt response to user preferences"""
        if not context.user_preferences:
            return response
        
        prefs = context.user_preferences
        
        # Adapt response length
        if prefs.response_length == 'short' and len(response) > 100:
            # Shorten the response
            sentences = response.split('.')
            if len(sentences) > 1:
                response = sentences[0] + '.'
        elif prefs.response_length == 'long' and len(response) < 80:
            # Add elaboration
            elaborations = [
                "Let me elaborate on that.",
                "There's more to consider here.",
                "I'd like to explore this further with you.",
                "This is worth thinking about more deeply."
            ]
            elaboration = random.choice(elaborations)
            response = f"{response} {elaboration}"
        
        # Adapt communication style
        if prefs.communication_style == 'direct' and 'I think' in response:
            response = response.replace('I think', 'I believe')
        elif prefs.communication_style == 'gentle' and '!' in response:
            response = response.replace('!', '.')
        
        return response
    
    def _add_emotional_context(self, response: str, context: PersonalizationContext) -> str:
        """Add emotional context awareness"""
        recent_emotions = context.user_context.recent_emotions
        
        if not recent_emotions:
            return response
        
        # Get the most recent emotion
        current_emotion = recent_emotions[0]
        
        # Don't add emotional context to very short responses
        if len(response) < 60:
            return response
        
        # Randomly decide whether to add emotional acknowledgment (25% chance)
        if random.random() > 0.25:
            return response
        
        # Add emotional acknowledgment
        acknowledgments = self.personalization_patterns['emotion_acknowledgments']
        acknowledgment = random.choice(acknowledgments).format(emotion=current_emotion)
        
        return f"{acknowledgment}. {response}"
    
    def _extract_preference_from_fact(self, fact: str) -> Optional[str]:
        """Extract preference from memory fact"""
        # Simple extraction patterns
        patterns = [
            r'likes? (.+)',
            r'enjoys? (.+)',
            r'prefers? (.+)',
            r'loves? (.+)',
            r'interested in (.+)',
            r'favorite (.+)'
        ]
        
        fact_lower = fact.lower()
        
        for pattern in patterns:
            match = re.search(pattern, fact_lower)
            if match:
                preference = match.group(1).strip()
                # Clean up the preference
                preference = re.sub(r'[^\w\s]', '', preference)
                if len(preference) < 50:  # Reasonable length
                    return preference
        
        return None
    
    def _cleanup_response(self, response: str) -> str:
        """Clean up and validate the personalized response"""
        # Remove extra spaces
        cleaned = re.sub(r'\s+', ' ', response).strip()
        
        # Ensure proper sentence ending
        if cleaned and not cleaned.endswith(('.', '!', '?')):
            cleaned += '.'
        
        # Remove duplicate punctuation
        cleaned = re.sub(r'([.!?])\1+', r'\1', cleaned)
        
        # Ensure reasonable length (not too short or too long)
        if len(cleaned) < 10:
            cleaned += " I'm here to listen and support you."
        elif len(cleaned) > 500:
            # Truncate at sentence boundary
            sentences = cleaned.split('.')
            truncated = '.'.join(sentences[:3]) + '.'
            cleaned = truncated
        
        return cleaned
    
    def create_context_summary(self, context: PersonalizationContext) -> str:
        """Create a summary of available context for debugging"""
        summary_parts = []
        
        # User info
        summary_parts.append(f"User: {context.user_context.preferred_name}")
        
        # Relationships
        if context.user_context.key_relationships:
            rel_count = len(context.user_context.key_relationships)
            summary_parts.append(f"Relationships: {rel_count}")
        
        # Memories
        if context.relevant_memories:
            memory_count = len(context.relevant_memories)
            avg_relevance = sum(m.relevance_score for m in context.relevant_memories) / memory_count
            summary_parts.append(f"Memories: {memory_count} (avg relevance: {avg_relevance:.2f})")
        
        # Emotions
        if context.user_context.recent_emotions:
            emotions = ', '.join(context.user_context.recent_emotions[:2])
            summary_parts.append(f"Recent emotions: {emotions}")
        
        # Preferences
        if context.user_preferences:
            prefs = context.user_preferences
            summary_parts.append(f"Style: {prefs.communication_style}, Length: {prefs.response_length}")
        
        return " | ".join(summary_parts)
    
    def get_personalization_stats(self) -> Dict[str, Any]:
        """Get personalization statistics"""
        return {
            'available_patterns': {
                'memory_connectors': len(self.personalization_patterns['memory_connectors']),
                'relationship_references': len(self.personalization_patterns['relationship_references']),
                'emotion_acknowledgments': len(self.personalization_patterns['emotion_acknowledgments'])
            },
            'memory_templates': {
                'person_memory': len(self.memory_integration_templates['person_memory']),
                'preference_memory': len(self.memory_integration_templates['preference_memory']),
                'experience_memory': len(self.memory_integration_templates['experience_memory'])
            },
            'relationship_types': list(self.relationship_phrases.keys())
        }

# Global context personalizer instance
_context_personalizer = None

def get_context_personalizer() -> ContextPersonalizer:
    """Get global context personalizer instance"""
    global _context_personalizer
    if _context_personalizer is None:
        _context_personalizer = ContextPersonalizer()
    return _context_personalizer