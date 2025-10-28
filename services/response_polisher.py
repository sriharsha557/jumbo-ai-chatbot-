"""
Response Polisher Service
Final quality assurance for all AI responses
Ensures emotional alignment, grammar, and empathetic communication
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
import random
from personality.jumbo_core import JumboPersonality

logger = logging.getLogger(__name__)

class ResponsePolisher:
    """
    Advanced response polishing system that ensures:
    - Emotional alignment with user's state
    - Empathetic language and tone
    - Natural, human-like communication
    - Grammar and readability optimization
    - Appropriate use of user's name
    """
    
    def __init__(self):
        self.personality = JumboPersonality()
        
        # Empathy enhancement patterns
        self.empathy_enhancers = {
            'sad': [
                "I can hear how difficult this is for you",
                "That sounds really hard",
                "I'm sorry you're going through this",
                "It makes sense that you'd feel this way",
                "I can feel the pain in your words"
            ],
            'angry': [
                "I can feel your frustration",
                "It sounds like this is really bothering you", 
                "Your anger is completely valid",
                "That would be frustrating for anyone",
                "I understand why you'd be upset about this"
            ],
            'anxious': [
                "I understand you're feeling worried",
                "It's completely natural to feel anxious about this",
                "I can sense your concern",
                "Anxiety about this makes total sense",
                "I hear the worry in your message"
            ],
            'fear': [
                "I can understand why that would be scary",
                "It's okay to feel afraid",
                "You're being so brave sharing this",
                "Fear about this is completely normal",
                "I can imagine how frightening that must be"
            ],
            'happy': [
                "I'm so glad to hear that!",
                "That sounds wonderful!",
                "I can feel your excitement!",
                "How amazing!",
                "I love hearing good news like this!"
            ],
            'surprise': [
                "Wow, that's unexpected!",
                "That must have been quite a surprise!",
                "I can imagine how that caught you off guard",
                "What a turn of events!",
                "That's certainly not what you were expecting!"
            ]
        }
        
        # Problematic phrases to avoid or replace
        self.problematic_phrases = {
            'sad': {
                'avoid': ['cheer up', 'look on the bright side', 'at least', 'everything happens for a reason', 'just be positive'],
                'replace_with': ['take your time with these feelings', 'it\'s okay to feel sad', 'your feelings are valid']
            },
            'angry': {
                'avoid': ['calm down', 'don\'t be angry', 'you shouldn\'t feel', 'just relax', 'it\'s not worth it'],
                'replace_with': ['I understand your frustration', 'your anger makes sense', 'it\'s natural to feel this way']
            },
            'anxious': {
                'avoid': ['don\'t worry', 'everything will be fine', 'just relax', 'stop overthinking', 'you\'re overreacting'],
                'replace_with': ['it\'s natural to feel concerned', 'your worries are understandable', 'anxiety is a normal response']
            },
            'fear': {
                'avoid': ['there\'s nothing to be afraid of', 'don\'t be scared', 'that\'s silly', 'you\'re being irrational'],
                'replace_with': ['your fear is understandable', 'it\'s okay to feel scared', 'fear is a natural response']
            }
        }
        
        # Grammar and readability improvements
        self.grammar_fixes = [
            (r'\s+', ' '),  # Multiple spaces to single space
            (r'\.{2,}', '.'),  # Multiple periods to single period
            (r'\?{2,}', '?'),  # Multiple question marks to single
            (r'!{2,}', '!'),  # Multiple exclamation marks to single
            (r'\s+([,.!?])', r'\1'),  # Remove space before punctuation
            (r'([,.!?])([a-zA-Z])', r'\1 \2'),  # Add space after punctuation
        ]
        
        # Conversation flow enhancers
        self.flow_enhancers = [
            'Tell me more about that',
            'How are you feeling about this?',
            'What would be most helpful right now?',
            'I\'m here to listen',
            'How has this been affecting you?',
            'What\'s been on your mind about this?'
        ]
        
        logger.info("Response polisher initialized")
    
    def polish_response(self, 
                       raw_response: str, 
                       user_emotion: str, 
                       user_name: str = None,
                       context: Dict = None) -> str:
        """
        Polish a raw response to ensure emotional alignment and quality
        
        Args:
            raw_response: The original response to polish
            user_emotion: Detected user emotion
            user_name: User's preferred name
            context: Additional context for polishing
            
        Returns:
            Polished, emotionally-aligned response
        """
        try:
            if not raw_response or not raw_response.strip():
                return self._generate_fallback_response(user_emotion, user_name)
            
            polished = raw_response.strip()
            
            # Apply polishing steps in order
            polished = self._fix_grammar_and_readability(polished)
            polished = self._ensure_emotional_alignment(polished, user_emotion)
            polished = self._add_empathy_if_missing(polished, user_emotion)
            polished = self._integrate_name_naturally(polished, user_name)
            polished = self._enhance_conversation_flow(polished, user_emotion, context)
            polished = self._final_quality_check(polished)
            
            logger.debug(f"Response polished: {len(raw_response)} → {len(polished)} chars")
            return polished
            
        except Exception as e:
            logger.error(f"Error polishing response: {e}")
            return raw_response  # Return original if polishing fails
    
    def _fix_grammar_and_readability(self, text: str) -> str:
        """Fix basic grammar and readability issues"""
        fixed = text
        
        # Apply grammar fixes
        for pattern, replacement in self.grammar_fixes:
            fixed = re.sub(pattern, replacement, fixed)
        
        # Capitalize first letter
        if fixed and fixed[0].islower():
            fixed = fixed[0].upper() + fixed[1:]
        
        # Ensure proper sentence ending
        if fixed and not fixed[-1] in '.!?':
            fixed += '.'
        
        return fixed.strip()
    
    def _ensure_emotional_alignment(self, text: str, emotion: str) -> str:
        """Ensure response tone aligns with user's emotion"""
        if emotion not in self.problematic_phrases:
            return text
        
        aligned = text
        avoid_phrases = self.problematic_phrases[emotion]['avoid']
        replacements = self.problematic_phrases[emotion]['replace_with']
        
        # Replace problematic phrases
        for avoid_phrase in avoid_phrases:
            if avoid_phrase.lower() in aligned.lower():
                replacement = random.choice(replacements)
                # Case-insensitive replacement
                pattern = re.compile(re.escape(avoid_phrase), re.IGNORECASE)
                aligned = pattern.sub(replacement, aligned, count=1)
                logger.debug(f"Replaced '{avoid_phrase}' with '{replacement}' for {emotion} emotion")
        
        return aligned
    
    def _add_empathy_if_missing(self, text: str, emotion: str) -> str:
        """Add empathy markers if the response lacks them"""
        if emotion == 'neutral' or emotion not in self.empathy_enhancers:
            return text
        
        # Check if response already has empathy markers
        empathy_indicators = [
            'i can', 'i understand', 'that sounds', 'i hear', 'i feel',
            'that must', 'it makes sense', 'i\'m sorry', 'i imagine',
            'i know', 'i see', 'i realize'
        ]
        
        text_lower = text.lower()
        has_empathy = any(indicator in text_lower for indicator in empathy_indicators)
        
        if not has_empathy:
            # Add appropriate empathy starter
            empathy_starter = random.choice(self.empathy_enhancers[emotion])
            return f"{empathy_starter}. {text}"
        
        return text
    
    def _integrate_name_naturally(self, text: str, user_name: str) -> str:
        """Integrate user's name naturally into the response"""
        if not user_name or user_name.lower() in ['user', 'friend', 'guest']:
            return text
        
        # Check if name is already present
        if user_name.lower() in text.lower():
            return text
        
        # 30% chance to add name for natural conversation
        if random.random() > 0.3:
            return text
        
        # Natural insertion patterns
        insertion_patterns = [
            (r'^(I can [^.]+)', rf'\1, {user_name}'),
            (r'^(That sounds [^.]+)', rf'\1, {user_name}'),
            (r'^(I understand [^.]+)', rf'\1, {user_name}'),
            (r'(\. )(I [^.]+)', rf'\1{user_name}, I\2'),
            (r'^(.*?)(\. )(.*?)$', rf'\1, {user_name}\2\3'),
        ]
        
        for pattern, replacement in insertion_patterns:
            if re.search(pattern, text):
                enhanced = re.sub(pattern, replacement, text, count=1)
                if enhanced != text:  # Only use if it actually changed
                    return enhanced
        
        # Fallback: add name at the beginning
        return f"I hear you, {user_name}. {text}"
    
    def _enhance_conversation_flow(self, text: str, emotion: str, context: Dict = None) -> str:
        """Enhance conversation flow with follow-up questions or supportive statements"""
        # Don't add flow enhancers to very short responses
        if len(text.split()) < 5:
            return text
        
        # Don't add if response already ends with a question
        if text.strip().endswith('?'):
            return text
        
        # 40% chance to add flow enhancer
        if random.random() > 0.4:
            return text
        
        # Choose appropriate flow enhancer based on emotion
        emotion_specific_enhancers = {
            'sad': [
                'How are you coping with this?',
                'What would feel most supportive right now?',
                'I\'m here to listen if you want to share more.'
            ],
            'anxious': [
                'What\'s been worrying you most about this?',
                'How can I best support you through this?',
                'Would it help to talk through your concerns?'
            ],
            'angry': [
                'What would help you feel better about this situation?',
                'How long has this been bothering you?',
                'What do you think would be a good next step?'
            ],
            'happy': [
                'I\'d love to hear more about what\'s making you so happy!',
                'What\'s been the best part of this experience?',
                'How are you planning to celebrate?'
            ]
        }
        
        enhancers = emotion_specific_enhancers.get(emotion, self.flow_enhancers)
        flow_enhancer = random.choice(enhancers)
        
        return f"{text} {flow_enhancer}"
    
    def _final_quality_check(self, text: str) -> str:
        """Final quality check and cleanup"""
        # Remove any double spaces that might have been introduced
        text = re.sub(r'\s+', ' ', text)
        
        # Ensure proper capitalization after periods
        text = re.sub(r'(\. )([a-z])', lambda m: m.group(1) + m.group(2).upper(), text)
        
        # Fix common grammar issues
        text = re.sub(r'\bi\b', 'I', text)  # Lowercase 'i' to 'I'
        text = re.sub(r"(\w)'(\w)", r"\1'\2", text)  # Fix apostrophes
        
        return text.strip()
    
    def _generate_fallback_response(self, emotion: str, user_name: str = None) -> str:
        """Generate a fallback response if original is empty or invalid"""
        fallback_responses = {
            'sad': "I can hear that you're going through a difficult time. I'm here to listen and support you.",
            'happy': "I can sense your positive energy! I'd love to hear more about what's making you feel so good.",
            'angry': "I can feel your frustration. It sounds like something is really bothering you.",
            'anxious': "I understand you're feeling worried. It's completely natural to have these concerns.",
            'fear': "I can sense your fear, and that's okay. You're safe here to share what's on your mind.",
            'surprise': "That sounds unexpected! I'd love to hear more about what happened.",
            'neutral': "I'm here and ready to listen. What's on your mind today?"
        }
        
        base_response = fallback_responses.get(emotion, fallback_responses['neutral'])
        
        if user_name and user_name.lower() not in ['user', 'friend', 'guest']:
            return f"I hear you, {user_name}. {base_response}"
        
        return base_response
    
    def analyze_response_quality(self, response: str, emotion: str) -> Dict[str, any]:
        """Analyze the quality of a response"""
        analysis = {
            'length': len(response),
            'word_count': len(response.split()),
            'has_empathy': False,
            'has_question': response.strip().endswith('?'),
            'emotional_alignment': 'unknown',
            'readability_score': 0,
            'suggestions': []
        }
        
        # Check for empathy markers
        empathy_indicators = ['i can', 'i understand', 'that sounds', 'i hear', 'i feel']
        analysis['has_empathy'] = any(indicator in response.lower() for indicator in empathy_indicators)
        
        # Check emotional alignment
        if emotion in self.problematic_phrases:
            avoid_phrases = self.problematic_phrases[emotion]['avoid']
            has_problematic = any(phrase in response.lower() for phrase in avoid_phrases)
            analysis['emotional_alignment'] = 'poor' if has_problematic else 'good'
        
        # Basic readability (simple metric)
        sentences = response.count('.') + response.count('!') + response.count('?')
        if sentences > 0:
            avg_words_per_sentence = analysis['word_count'] / sentences
            analysis['readability_score'] = max(0, min(100, 100 - (avg_words_per_sentence - 15) * 2))
        
        # Generate suggestions
        if not analysis['has_empathy'] and emotion != 'neutral':
            analysis['suggestions'].append('Add empathy markers')
        
        if analysis['emotional_alignment'] == 'poor':
            analysis['suggestions'].append('Improve emotional alignment')
        
        if analysis['word_count'] < 5:
            analysis['suggestions'].append('Expand response length')
        
        return analysis
    
    def batch_polish_responses(self, responses: List[Dict]) -> List[str]:
        """Polish multiple responses in batch"""
        polished_responses = []
        
        for response_data in responses:
            polished = self.polish_response(
                response_data.get('response', ''),
                response_data.get('emotion', 'neutral'),
                response_data.get('user_name'),
                response_data.get('context')
            )
            polished_responses.append(polished)
        
        return polished_responses

# Singleton instance for global use
_response_polisher = None

def get_response_polisher() -> ResponsePolisher:
    """Get the global response polisher instance"""
    global _response_polisher
    if _response_polisher is None:
        _response_polisher = ResponsePolisher()
    return _response_polisher

def polish_response_quick(response: str, emotion: str, user_name: str = None) -> str:
    """Quick response polishing function"""
    polisher = get_response_polisher()
    return polisher.polish_response(response, emotion, user_name)