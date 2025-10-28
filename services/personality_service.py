"""
Personality Service
Integrates Jumbo's personality system with the chat service
"""

from typing import Dict, Optional, Tuple
import logging
from personality.jumbo_core import JumboPersonality, get_personality_prompt, get_empathy_response, should_use_name

logger = logging.getLogger(__name__)

class PersonalityService:
    """Service for managing Jumbo's personality and emotional responses"""
    
    def __init__(self):
        self.personality = JumboPersonality()
        logger.info("Personality service initialized")
    
    def build_system_prompt(self, 
                           emotion: str = "neutral", 
                           user_name: str = None, 
                           context: str = None,
                           memories: list = None) -> str:
        """
        Build a complete system prompt with personality and emotional context
        
        Args:
            emotion: Detected user emotion
            user_name: User's preferred name
            context: Additional conversation context
            memories: Relevant user memories
            
        Returns:
            Complete system prompt for LLM
        """
        try:
            # Build base personality prompt
            base_prompt = get_personality_prompt(emotion, user_name, context)
            
            # Add memory context if available
            if memories:
                memory_context = self._format_memory_context(memories)
                base_prompt += f"\n\nRelevant memories about the user:\n{memory_context}"
            
            # Add final instructions
            base_prompt += f"""

IMPORTANT RESPONSE GUIDELINES:
1. Always respond as Jumbo - warm, empathetic, and caring
2. Current user emotion is: {emotion}
3. Adapt your tone and language to match their emotional needs
4. Use their name ({user_name or 'friend'}) naturally if appropriate
5. Validate their emotions before offering advice or solutions
6. Ask thoughtful follow-up questions to show genuine interest
7. Keep responses conversational and human-like, never clinical

Remember: You're not just answering questions - you're being a caring companion who genuinely cares about this person's wellbeing."""

            return base_prompt
            
        except Exception as e:
            logger.error(f"Error building system prompt: {e}")
            # Fallback to basic personality prompt
            return JumboPersonality.get_base_prompt()
    
    def enhance_response_with_personality(self, 
                                        raw_response: str, 
                                        emotion: str, 
                                        user_name: str = None) -> str:
        """
        Enhance a raw LLM response with personality markers
        
        Args:
            raw_response: Raw response from LLM
            emotion: User's detected emotion
            user_name: User's preferred name
            
        Returns:
            Enhanced response with personality markers
        """
        try:
            enhanced_response = raw_response
            
            # Add empathy starter if missing
            if not self._has_empathy_marker(raw_response, emotion):
                empathy_starter = get_empathy_response(emotion)
                enhanced_response = f"{empathy_starter}. {enhanced_response}"
            
            # Add user name naturally if appropriate
            if user_name and should_use_name(user_name):
                enhanced_response = self._add_name_naturally(enhanced_response, user_name)
            
            # Ensure emotional alignment
            enhanced_response = self._ensure_emotional_alignment(enhanced_response, emotion)
            
            return enhanced_response
            
        except Exception as e:
            logger.error(f"Error enhancing response: {e}")
            return raw_response
    
    def get_emotion_metadata(self, emotion: str) -> Dict:
        """Get metadata about how to handle a specific emotion"""
        emotion_data = JumboPersonality.get_emotion_guidance(emotion)
        
        return {
            "emotion": emotion,
            "tone_markers": emotion_data.get("tone_markers", []),
            "empathy_starter": get_empathy_response(emotion),
            "guidance": emotion_data.get("guidance", ""),
            "avoid_phrases": emotion_data.get("avoid", [])
        }
    
    def _format_memory_context(self, memories: list) -> str:
        """Format memories for inclusion in system prompt"""
        if not memories:
            return "No previous memories available."
        
        formatted_memories = []
        for memory in memories[:5]:  # Limit to 5 most relevant memories
            if isinstance(memory, dict):
                content = memory.get('content', str(memory))
                memory_type = memory.get('type', 'general')
                formatted_memories.append(f"- {memory_type}: {content}")
            else:
                formatted_memories.append(f"- {str(memory)}")
        
        return "\n".join(formatted_memories)
    
    def _has_empathy_marker(self, response: str, emotion: str) -> bool:
        """Check if response already has empathy markers"""
        empathy_indicators = [
            "i can", "i understand", "that sounds", "i hear", "i feel",
            "that must", "it makes sense", "i'm sorry", "i imagine"
        ]
        
        response_lower = response.lower()
        return any(indicator in response_lower for indicator in empathy_indicators)
    
    def _add_name_naturally(self, response: str, user_name: str) -> str:
        """Add user name naturally to the response"""
        if user_name.lower() in response.lower():
            return response  # Name already present
        
        # Find natural insertion points
        insertion_points = [
            (", and ", f", {user_name}, and "),
            ("You know", f"You know, {user_name}"),
            ("I think", f"I think, {user_name}"),
            ("That's", f"That's really something, {user_name}"),
        ]
        
        for original, replacement in insertion_points:
            if original in response:
                return response.replace(original, replacement, 1)
        
        # If no natural insertion point, add at the beginning
        return f"I hear you, {user_name}. {response}"
    
    def _ensure_emotional_alignment(self, response: str, emotion: str) -> str:
        """Ensure response tone aligns with user emotion"""
        emotion_data = JumboPersonality.get_emotion_guidance(emotion)
        avoid_phrases = emotion_data.get("avoid", [])
        
        # Remove or replace phrases that don't align with the emotion
        aligned_response = response
        
        for avoid_phrase in avoid_phrases:
            if avoid_phrase.lower() in aligned_response.lower():
                # Replace with more appropriate language
                if emotion == "sad" and "cheer up" in avoid_phrase.lower():
                    aligned_response = aligned_response.replace(avoid_phrase, "take your time with these feelings")
                elif emotion == "angry" and "calm down" in avoid_phrase.lower():
                    aligned_response = aligned_response.replace(avoid_phrase, "I understand your frustration")
                elif emotion == "anxious" and "don't worry" in avoid_phrase.lower():
                    aligned_response = aligned_response.replace(avoid_phrase, "it's natural to feel concerned")
        
        return aligned_response
    
    def get_conversation_starter(self, emotion: str = "neutral", user_name: str = None) -> str:
        """Get a conversation starter based on emotion and context"""
        starters = {
            "sad": [
                "I'm here to listen if you'd like to share what's on your mind.",
                "How are you feeling right now?",
                "I can sense something might be weighing on you. Want to talk about it?"
            ],
            "happy": [
                "You seem like you're in a good mood! What's been going well?",
                "I'd love to hear what's making you happy today!",
                "Something good happened, didn't it? Tell me about it!"
            ],
            "anxious": [
                "I'm here with you. What's been on your mind lately?",
                "How can I support you right now?",
                "Take your time - I'm here to listen."
            ],
            "neutral": [
                "How has your day been treating you?",
                "What's been on your mind lately?",
                "I'm here and ready to listen. How are you doing?"
            ]
        }
        
        import random
        emotion_starters = starters.get(emotion, starters["neutral"])
        starter = random.choice(emotion_starters)
        
        if user_name and should_use_name(user_name):
            starter = f"Hi {user_name}! {starter}"
        
        return starter