"""
Conversational Summarizer for Jumbo Chatbot
Converts verbose responses to concise, natural conversation
"""

import logging
from typing import Dict, Tuple
from llm_service import LLMService

logger = logging.getLogger(__name__)

class ConversationalSummarizer:
    def __init__(self):
        self.llm_service = LLMService()
    
    def summarize_user_input(self, user_message: str, context: Dict = None) -> Dict:
        """
        Summarize user input to extract key emotional and contextual information
        Returns: {"mood": "tired but proud", "context": "work", "key_points": [...]}
        
        Example: "I've been tired lately because of long work hours, but I'm proud of what I've achieved."
        Returns: {"mood": "tired but proud", "context": "work", "key_points": ["long hours", "proud of achievements"]}
        """
        try:
            if not self.llm_service.is_enabled():
                return self._fallback_summarization(user_message)
            
            # Enhanced prompt based on your example
            summarization_prompt = f"""
            Analyze this user message and extract key emotional and contextual information.
            
            User message: "{user_message}"
            
            Extract the following in JSON format:
            1. Combined mood (e.g., "tired but proud", "happy", "anxious", "excited but nervous")
            2. Main context/topic (work, family, friends, health, relationship, school, etc.)
            3. Key points (max 2-3 most important facts or feelings)
            4. Emotional intensity (1-10, where 1=very mild, 10=very intense)
            5. Whether they need empathy/support
            6. Conversation direction (what they might want to talk about next)
            
            Examples:
            - "I've been tired lately because of long work hours, but I'm proud of what I've achieved."
              → {{"mood": "tired but proud", "context": "work", "key_points": ["long work hours", "feeling accomplished"], "emotional_intensity": 6, "needs_empathy": true, "conversation_direction": "work achievements"}}
            
            - "Just got accepted to my dream college!"
              → {{"mood": "excited", "context": "education", "key_points": ["college acceptance", "dream school"], "emotional_intensity": 9, "needs_empathy": false, "conversation_direction": "celebration"}}
            
            Respond ONLY with valid JSON:
            """
            
            response = self.llm_service.get_response(summarization_prompt)
            
            # Try to parse JSON response
            import json
            try:
                # Clean the response to extract just the JSON
                response = response.strip()
                if response.startswith('```json'):
                    response = response.replace('```json', '').replace('```', '').strip()
                elif response.startswith('```'):
                    response = response.replace('```', '').strip()
                
                # Find JSON object in response
                start_idx = response.find('{')
                end_idx = response.rfind('}') + 1
                if start_idx != -1 and end_idx > start_idx:
                    json_str = response[start_idx:end_idx]
                    summary = json.loads(json_str)
                    
                    # Validate required fields
                    required_fields = ['mood', 'context', 'key_points', 'emotional_intensity', 'needs_empathy']
                    if all(field in summary for field in required_fields):
                        return summary
                    else:
                        logger.warning("LLM response missing required fields, using fallback")
                        return self._fallback_summarization(user_message)
                else:
                    logger.warning("No valid JSON found in LLM response, using fallback")
                    return self._fallback_summarization(user_message)
                    
            except json.JSONDecodeError as e:
                logger.warning(f"JSON decode error: {e}, using fallback")
                return self._fallback_summarization(user_message)
                
        except Exception as e:
            logger.error(f"Summarization error: {e}")
            return self._fallback_summarization(user_message)
    
    def _fallback_summarization(self, user_message: str) -> Dict:
        """Enhanced rule-based summarization when LLM isn't available"""
        message_lower = user_message.lower()
        
        # Enhanced mood detection with combinations
        mood_keywords = {
            'happy': ['happy', 'joy', 'excited', 'great', 'awesome', 'wonderful', 'amazing', 'fantastic'],
            'sad': ['sad', 'down', 'depressed', 'upset', 'crying', 'heartbroken', 'disappointed'],
            'tired': ['tired', 'exhausted', 'drained', 'sleepy', 'worn out', 'burnt out'],
            'proud': ['proud', 'accomplished', 'achieved', 'success', 'victory', 'won', 'completed'],
            'anxious': ['anxious', 'worried', 'nervous', 'stress', 'overwhelmed', 'panic'],
            'angry': ['angry', 'mad', 'frustrated', 'annoyed', 'furious', 'irritated'],
            'confused': ['confused', 'lost', 'unsure', 'don\'t know', 'uncertain'],
            'grateful': ['grateful', 'thankful', 'blessed', 'appreciate'],
            'lonely': ['lonely', 'alone', 'isolated', 'miss', 'empty']
        }
        
        detected_moods = []
        for mood, keywords in mood_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                detected_moods.append(mood)
        
        # Create combined mood like "tired but proud"
        combined_mood = 'neutral'
        if len(detected_moods) >= 2:
            # Handle common combinations
            if 'tired' in detected_moods and 'proud' in detected_moods:
                combined_mood = 'tired but proud'
            elif 'happy' in detected_moods and 'anxious' in detected_moods:
                combined_mood = 'excited but nervous'
            elif 'sad' in detected_moods and 'grateful' in detected_moods:
                combined_mood = 'sad but grateful'
            else:
                combined_mood = f"{detected_moods[0]} but {detected_moods[1]}"
        elif len(detected_moods) == 1:
            combined_mood = detected_moods[0]
        
        # Enhanced context detection
        context_keywords = {
            'work': ['work', 'job', 'office', 'boss', 'colleague', 'project', 'meeting', 'deadline', 'career'],
            'family': ['family', 'mom', 'dad', 'parent', 'brother', 'sister', 'child', 'kids', 'home'],
            'friends': ['friend', 'buddy', 'pal', 'hang out', 'party', 'social'],
            'health': ['health', 'sick', 'doctor', 'medicine', 'hospital', 'pain', 'therapy'],
            'relationship': ['boyfriend', 'girlfriend', 'partner', 'dating', 'love', 'breakup', 'marriage'],
            'school': ['school', 'college', 'university', 'class', 'exam', 'study', 'homework', 'grade'],
            'money': ['money', 'financial', 'budget', 'expensive', 'cheap', 'salary', 'debt'],
            'personal': ['myself', 'personal', 'growth', 'change', 'future', 'goals', 'dreams']
        }
        
        detected_context = 'general'
        for context, keywords in context_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                detected_context = context
                break
        
        # Extract key points (simple version)
        key_points = []
        sentences = user_message.split('.')
        for sentence in sentences[:2]:  # Take first 2 sentences
            sentence = sentence.strip()
            if len(sentence) > 10:  # Only meaningful sentences
                key_points.append(sentence[:80])  # Truncate long sentences
        
        if not key_points:
            key_points = [user_message[:80]]
        
        # Determine conversation direction
        conversation_direction = 'general chat'
        if 'proud' in detected_moods or 'accomplished' in message_lower:
            conversation_direction = 'celebration'
        elif any(mood in ['sad', 'anxious', 'tired'] for mood in detected_moods):
            conversation_direction = 'support'
        elif 'excited' in detected_moods or 'happy' in detected_moods:
            conversation_direction = 'sharing joy'
        elif '?' in user_message:
            conversation_direction = 'seeking advice'
        
        return {
            'mood': combined_mood,
            'context': detected_context,
            'key_points': key_points,
            'emotional_intensity': min(len(detected_moods) * 2 + 4, 10),
            'needs_empathy': any(mood in ['sad', 'anxious', 'tired', 'lonely', 'confused'] for mood in detected_moods),
            'conversation_direction': conversation_direction
        }
    
    def generate_conversational_response(self, summary: Dict, user_name: str = "there", memory_context: Dict = None) -> str:
        """
        Generate a concise, conversational response based on the summary
        
        Example flow:
        User → "I've been tired lately because of long work hours, but I'm proud of what I've achieved."
        Summary → {"mood": "tired but proud", "context": "work"}
        Response → "That sounds exhausting but rewarding. What's been your biggest win this week?"
        """
        try:
            if not self.llm_service.is_enabled():
                return self._fallback_response(summary, user_name)
            
            # Build context from memory if available
            memory_info = ""
            if memory_context and memory_context.get('relevant_memories'):
                memories = memory_context['relevant_memories'][:2]  # Use top 2 memories
                memory_info = f"\nRelevant context: {', '.join([m.get('fact', '') for m in memories])}"
            
            conversation_prompt = f"""
            Generate a natural, concise response (1-2 sentences, max 40 words) based on this user analysis:
            
            User mood: {summary.get('mood', 'neutral')}
            Context: {summary.get('context', 'general')}
            Key points: {summary.get('key_points', [])}
            Needs empathy: {summary.get('needs_empathy', False)}
            Conversation direction: {summary.get('conversation_direction', 'general')}
            User name: {user_name}{memory_info}
            
            Guidelines:
            - Be conversational like a close friend
            - Match their emotional energy
            - Ask ONE engaging follow-up question
            - Use their name naturally (not every time)
            - Be concise but warm
            
            Examples:
            - Mood "tired but proud" + work context → "That sounds exhausting but rewarding. What's been your biggest win this week?"
            - Mood "excited" + school context → "I love your excitement! Tell me more about what happened."
            - Mood "anxious" + relationship context → "I can hear the worry in your message. Want to talk through what's on your mind?"
            
            Response (no quotes, just the message):
            """
            
            response = self.llm_service.get_response(conversation_prompt)
            
            # Clean up the response more thoroughly
            response = response.strip()
            
            # Remove common prefixes/suffixes
            prefixes_to_remove = ['Response:', 'Answer:', 'Reply:', '"', "'"]
            for prefix in prefixes_to_remove:
                if response.startswith(prefix):
                    response = response[len(prefix):].strip()
                if response.endswith(prefix):
                    response = response[:-len(prefix)].strip()
            
            # Remove quotes
            response = response.replace('"', '').replace("'", "")
            
            # Ensure it's not too long (fallback)
            if len(response.split()) > 45:
                sentences = response.split('.')
                if len(sentences) > 1:
                    response = sentences[0] + '.'
            
            return response
            
        except Exception as e:
            logger.error(f"Conversational response error: {e}")
            return self._fallback_response(summary, user_name)
    
    def _fallback_response(self, summary: Dict, user_name: str) -> str:
        """Generate a natural response when LLM isn't available"""
        mood = summary.get('mood', 'neutral')
        context = summary.get('context', 'general')
        needs_empathy = summary.get('needs_empathy', False)
        conversation_direction = summary.get('conversation_direction', 'general')
        
        # Natural responses based on mood combinations
        if 'tired but proud' in mood:
            return f"That sounds exhausting but rewarding. What's been your biggest win lately?"
        elif 'excited but nervous' in mood:
            return f"I can feel both your excitement and nerves! What's got you feeling this way?"
        elif 'sad but grateful' in mood:
            return f"It sounds like you're going through a lot. What are you most grateful for right now?"
        
        # Single mood responses
        if needs_empathy:
            responses = {
                'sad': f"I'm sorry you're going through this. Want to talk about what's happening?",
                'anxious': f"I can hear the worry in your message. What's weighing on your mind?",
                'tired': f"You sound really drained. What's been taking so much out of you?",
                'lonely': f"That sounds really tough. I'm here with you. What would help right now?",
                'confused': f"It's okay to feel uncertain. What's got you feeling lost?"
            }
            if mood in responses:
                return responses[mood]
        else:
            responses = {
                'happy': f"I love your positive energy! What's making you so happy?",
                'proud': f"You should absolutely be proud! Tell me more about what you accomplished.",
                'excited': f"Your excitement is contagious! What's got you so energized?",
                'grateful': f"It's beautiful to hear your gratitude. What's been on your heart?"
            }
            if mood in responses:
                return responses[mood]
        
        # Context-based responses
        context_responses = {
            'work': f"How are things going with work lately?",
            'family': f"Family can be complex. What's happening at home?",
            'friends': f"Tell me more about what's going on with your friends.",
            'relationship': f"Relationships can be intense. How are you feeling about things?",
            'school': f"How's school treating you these days?",
            'health': f"Taking care of yourself is so important. How are you feeling?"
        }
        
        if context in context_responses:
            return context_responses[context]
        
        # Default natural response
        return f"Thanks for sharing that with me. What's been on your mind lately?"
    
    def process_message(self, user_message: str, user_name: str = "there", memory_context: Dict = None) -> Tuple[str, Dict]:
        """
        Complete two-step process: Summarize → Generate Response
        
        Example flow:
        User → "I've been tired lately because of long work hours, but I'm proud of what I've achieved."
        ↓ Summarizer → {"mood": "tired but proud", "context": "work"}
        ↓ Chatbot → "That sounds exhausting but rewarding. What's been your biggest win this week?"
        
        Returns: (response_text, summary_metadata)
        """
        try:
            # Step 1: Summarize user input
            logger.info(f"Step 1: Summarizing user input: {user_message[:50]}...")
            summary = self.summarize_user_input(user_message)
            logger.info(f"Summary: {summary}")
            
            # Step 2: Generate conversational response
            logger.info(f"Step 2: Generating response for mood '{summary.get('mood')}' in context '{summary.get('context')}'")
            response = self.generate_conversational_response(summary, user_name, memory_context)
            logger.info(f"Generated response: {response}")
            
            # Return both response and metadata
            return response, {
                'mood': summary.get('mood', 'neutral'),
                'context': summary.get('context', 'general'),
                'emotional_intensity': summary.get('emotional_intensity', 5),
                'needs_empathy': summary.get('needs_empathy', False),
                'conversation_direction': summary.get('conversation_direction', 'general'),
                'key_points': summary.get('key_points', []),
                'used_summarizer': True,
                'response_type': 'conversational'
            }
            
        except Exception as e:
            logger.error(f"Message processing error: {e}")
            # Fallback to simple response
            return f"I hear you, {user_name}. Tell me more about what's on your mind.", {
                'mood': 'neutral',
                'context': 'general',
                'used_summarizer': False,
                'response_type': 'fallback'
            }