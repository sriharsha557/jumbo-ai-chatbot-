"""
chatbot.py - FIXED Priority: LLM First for unique questions, scenarios for emotions
NOW WITH MEMORY LAYER
"""

from typing import Tuple, Optional, Dict, List
from database import Database
from scenario_engine import ScenarioEngine
from language_utils import LanguageUtils, Language, Mood
from llm_service import LLMService
from config import Config
from memory_service import MemoryService  # ADD THIS IMPORT
from conversational_summarizer import ConversationalSummarizer  # ADD THIS IMPORT
import logging
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JumboChatbot:
    """Main chatbot class - LLM as primary, scenarios for emotions, NOW WITH MEMORY"""
    
    def __init__(self, data_dir: str = "./jumbo_data"):
        self.db = Database(data_dir)
        self.scenario_engine = ScenarioEngine()
        self.llm_service = LLMService()
        self.memory_service = MemoryService()  # ADD THIS LINE
        self.conversational_summarizer = ConversationalSummarizer()  # ADD THIS LINE
        self.current_user = None
        self.language = Language.ENGLISH
        logger.info("Jumbo Chatbot initialized")
        logger.info(f"LLM Service: {'ENABLED' if self.llm_service.is_enabled() else 'DISABLED'}")
        logger.info("Memory Service: ENABLED")  # ADD THIS LINE
    
    # ========================================================================
    # USER MANAGEMENT (KEEP AS IS)
    # ========================================================================
    
    def register_new_user(self, name: str, language: str = "te") -> Tuple[bool, str]:
        """Register a new user with unique name"""
        name = LanguageUtils.clean_text(name)
        
        if not name or len(name) < 2:
            return False, "Name must be at least 2 characters long."
        
        success, message = self.db.register_user(name, language)
        
        if success:
            self.set_current_user(name, language)
        
        return success, message
    
    def set_current_user(self, name: str, language: str = "te"):
        """Set current user for conversation"""
        user = self.db.get_user(name)
        if user:
            self.current_user = user
            self.language = Language(language)
            self.db.update_user_activity(name)
            logger.info(f"User switched to: {name}")
        else:
            logger.warning(f"User not found: {name}")
    
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
        logger.info(f"Supabase user set: {display_name}")

    def check_for_name_preference(self, user_message: str, supabase_service) -> Tuple[bool, str]:
        """Check if user is providing their preferred name"""
        # Enhanced patterns to detect name responses
        name_patterns = [
            "call me", "i'm", "my name is", "name's", "i am",
            "just", "please call", "you can call", "i prefer", "i go by",
            "my friends call me", "everyone calls me", "people call me"
        ]
        
        # Check if this looks like a name response
        message_lower = user_message.lower().strip()
        
        # If it's a short response (likely a name) or contains name patterns
        if (len(user_message.split()) <= 4 and len(user_message) > 1) or \
           any(pattern in message_lower for pattern in name_patterns):
            
            # Extract the name using improved logic
            potential_name = self._extract_name_from_message(user_message, message_lower, name_patterns)
            
            if potential_name and len(potential_name.split()) <= 2:  # Max 2 words for name
                # Capitalize properly
                potential_name = ' '.join(word.capitalize() for word in potential_name.split())
                
                # Save to Supabase
                user_id = self.current_user.get('user_id')
                if user_id:
                    success, message = supabase_service.set_preferred_name(user_id, potential_name)
                    if success:
                        # Update current user
                        self.current_user['preferred_name'] = potential_name
                        self.current_user['name'] = potential_name
                        return True, message
                
        return False, ""
    
    def check_for_memory_recall(self, user_message: str, supabase_service) -> Optional[str]:
        """Check if user is asking about past conversations or memories"""
        message_lower = user_message.lower().strip()
        
        # Memory recall patterns
        memory_patterns = [
            'what did we talk about',
            'do you remember',
            'what did i tell you',
            'what did i say',
            'our previous conversation',
            'last time we talked',
            'earlier we discussed',
            'you mentioned',
            'i told you about',
            'we were talking about',
            'from our last chat',
            'what was i saying',
            'continue our conversation',
            'where were we',
            'what did we discuss'
        ]
        
        # Check if user is asking for memory recall
        is_memory_request = any(pattern in message_lower for pattern in memory_patterns)
        
        if is_memory_request and hasattr(self, '_supabase_service'):
            try:
                # Get recent conversations from Supabase
                user_id = self.current_user.get('user_id')
                if user_id:
                    conversations = supabase_service.get_user_conversations(user_id, limit=5)
                    
                    if conversations:
                        # Format recent conversations for response
                        memory_summary = "Here's what we've talked about recently:\n\n"
                        for i, conv in enumerate(conversations[-3:], 1):  # Last 3 conversations
                            user_msg = conv.get('message', '')[:100]  # Truncate long messages
                            bot_response = conv.get('response', '')[:100]
                            
                            memory_summary += f"{i}. You said: \"{user_msg}{'...' if len(conv.get('message', '')) > 100 else ''}\"\n"
                            memory_summary += f"   I responded about: {bot_response}{'...' if len(conv.get('response', '')) > 100 else ''}\n\n"
                        
                        memory_summary += "Is there something specific you'd like to continue discussing?"
                        return memory_summary
                    else:
                        return "This seems to be our first conversation! I don't have any previous memories to recall. What would you like to talk about?"
            except Exception as e:
                logger.error(f"Memory recall error: {e}")
                return "I'm having trouble accessing our conversation history right now, but I'm here to chat with you!"
        
        return None
    
    def _extract_name_from_message(self, original_message: str, message_lower: str, name_patterns: list) -> str:
        """Extract name from user message using various patterns"""
        import re
        
        # Start with the original message
        potential_name = original_message.strip()
        
        # Pattern-based extraction with regex
        extraction_patterns = [
            (r"call me (\w+(?:\s+\w+)?)", 1),
            (r"you can call me (\w+(?:\s+\w+)?)", 1),
            (r"i'm (\w+(?:\s+\w+)?)", 1),
            (r"my name is (\w+(?:\s+\w+)?)", 1),
            (r"i am (\w+(?:\s+\w+)?)", 1),
            (r"i prefer (?:to be called )?(\w+(?:\s+\w+)?)", 1),
            (r"i go by (\w+(?:\s+\w+)?)", 1),
            (r"(?:my friends?|everyone|people) calls? me (\w+(?:\s+\w+)?)", 1),
            (r"just (?:call me )?(\w+(?:\s+\w+)?)", 1)
        ]
        
        # Try pattern matching first
        for pattern, group in extraction_patterns:
            match = re.search(pattern, message_lower)
            if match:
                potential_name = match.group(group).strip()
                break
        else:
            # If no pattern matches, try simple prefix removal
            prefixes_to_remove = [
                "call me ", "you can call me ", "i'm ", "my name is ", 
                "i am ", "just ", "i prefer ", "i go by ",
                "my friends call me ", "everyone calls me ", "people call me ",
                "just call me "
            ]
            
            for prefix in prefixes_to_remove:
                if message_lower.startswith(prefix):
                    potential_name = original_message[len(prefix):].strip()
                    break
        
        # Clean up the extracted name
        potential_name = re.sub(r'[^\w\s]', '', potential_name).strip()
        
        # Validate the name (should be 1-2 words, alphabetic)
        words = potential_name.split()
        if len(words) <= 2 and all(word.isalpha() for word in words):
            return potential_name
        
        return ""

    def get_personalized_greeting(self, is_first_time: bool = False) -> str:
        """Get a personalized greeting based on user's preferred name"""
        user_name = self.current_user.get('preferred_name') or self.current_user.get('name', 'there')
        
        if is_first_time and not self.current_user.get('preferred_name'):
            # First time user without preferred name
            account_name = self.current_user.get('name', 'there')
            return f"Hey {account_name}! I noticed your name from your account, but I'd love to know—what should I call you? 😊"
        elif self.current_user.get('preferred_name'):
            # User has a preferred name
            return f"Hey {user_name}, welcome back! How can I help you today? 😊"
        else:
            # Regular greeting
            return f"Hello {user_name}! How are you feeling today? 😊"

    def extract_memories_from_message(self, user_message: str, supabase_service) -> List[Dict]:
        """Extract important facts/memories from user message"""
        memories_to_save = []
        message_lower = user_message.lower()
        
        # Pattern matching for different types of memories
        memory_patterns = {
            'personal_relationship': [
                r'my (?:best )?friend(?:s)? (?:is|are) ([^.!?]+)',
                r'(?:i have a|my) (?:friend|buddy|pal) (?:named|called) ([^.!?]+)',
                r'(?:i\'m friends with|i know) ([^.!?]+)',
                r'friends (?:are|include) ([^.!?]+)',
                r'(?:^|\s)([A-Z][a-z]+(?:\s+and\s+[A-Z][a-z]+)*)\s+(?:is|are)\s+my\s+friend',
                r'(?:^|\s)([A-Z][a-z]+(?:\s+and\s+[A-Z][a-z]+)*)\s+(?:and\s+)?(?:are\s+)?my\s+(?:best\s+)?friends?',
            ],
            'family': [
                r'my (?:mom|mother|dad|father|brother|sister|parent) (?:is|are) ([^.!?]+)',
                r'(?:i have a|my) (?:brother|sister) (?:named|called) ([^.!?]+)',
            ],
            'preference': [
                r'i (?:love|like|enjoy|prefer) ([^.!?]+)',
                r'my favorite ([^.!?]+) is ([^.!?]+)',
                r'i (?:hate|dislike|don\'t like) ([^.!?]+)',
            ],
            'work': [
                r'i work (?:at|for) ([^.!?]+)',
                r'my job is ([^.!?]+)',
                r'i\'m a ([^.!?]+)',
            ],
            'personal_info': [
                r'i (?:live|stay) in ([^.!?]+)',
                r'i\'m from ([^.!?]+)',
                r'i study (?:at|in) ([^.!?]+)',
            ]
        }
        
        import re
        
        # Simple direct extraction for common phrases
        if 'friend' in message_lower:
            # Look for names (capitalized words)
            words = user_message.split()
            names = [word.strip('.,!?') for word in words if word[0].isupper() and len(word) > 2]
            
            if names:
                friends_list = ', '.join(names)
                memory = {
                    'fact': f"Friends: {friends_list}",
                    'category': 'personal_relationship',
                    'memory_type': 'person',
                    'name': friends_list,
                    'relationship': 'friend',
                    'importance_score': 0.9,
                    'data': {
                        'original_message': user_message,
                        'extracted_names': names
                    }
                }
                memories_to_save.append(memory)
                logger.info(f"Extracted friends: {friends_list}")
        
        # Pattern-based extraction
        for category, patterns in memory_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, user_message, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        fact = ' '.join(match).strip()
                    else:
                        fact = match.strip()
                    
                    if len(fact) > 2:  # Valid fact
                        memory = {
                            'fact': f"User mentioned: {fact}",
                            'category': category,
                            'memory_type': 'fact',
                            'importance_score': 0.8,
                            'data': {
                                'original_message': user_message,
                                'extracted_fact': fact
                            }
                        }
                        
                        # Special handling for relationships
                        if category == 'personal_relationship':
                            memory['memory_type'] = 'person'
                            memory['name'] = fact
                            memory['relationship'] = 'friend'
                            memory['fact'] = f"Friends: {fact}"
                        
                        memories_to_save.append(memory)
        
        # Save memories to database
        user_id = self.current_user.get('user_id')
        if user_id and memories_to_save:
            logger.info(f"Saving {len(memories_to_save)} memories for user {user_id}")
            for memory in memories_to_save:
                success, message = supabase_service.save_user_memory(user_id, memory['memory_type'], memory)
                logger.info(f"Memory save result: {success}, {message}")
        else:
            logger.info(f"No memories to save. User ID: {user_id}, Memories: {len(memories_to_save)}")
        
        return memories_to_save

    def check_for_memory_recall(self, user_message: str, supabase_service) -> str:
        """Check if user is asking to recall a memory"""
        message_lower = user_message.lower()
        
        # Patterns that indicate memory recall requests
        recall_patterns = [
            'do you remember', 'do you know', 'what do you know about',
            'tell me about', 'who are my', 'what are my', 'remind me',
            'what did i tell you', 'what do i like', 'who is my',
            'my friends', 'about my friends', 'friends names'
        ]
        
        if any(pattern in message_lower for pattern in recall_patterns):
            # Extract search terms
            search_terms = []
            
            # Common recall queries
            if 'friend' in message_lower:
                search_terms.extend(['friend', 'best friend'])
            if 'family' in message_lower:
                search_terms.extend(['mom', 'dad', 'mother', 'father', 'brother', 'sister'])
            if 'like' in message_lower or 'favorite' in message_lower:
                search_terms.extend(['love', 'like', 'favorite', 'prefer'])
            if 'work' in message_lower or 'job' in message_lower:
                search_terms.extend(['work', 'job'])
            
            # If no specific terms, use words from the message
            if not search_terms:
                words = user_message.lower().split()
                search_terms = [word for word in words if len(word) > 3]
            
            # Search memories
            user_id = self.current_user.get('user_id')
            if user_id and search_terms:
                memories = supabase_service.search_user_memories(user_id, search_terms)
                
                if memories:
                    # Format response based on found memories
                    user_name = self.current_user.get('preferred_name') or self.current_user.get('name', 'you')
                    
                    if len(memories) == 1:
                        memory = memories[0]
                        return f"Of course! You told me {memory['fact']}. 😊"
                    else:
                        facts = [memory['fact'] for memory in memories[:3]]
                        return f"Yes {user_name}! I remember several things: {', '.join(facts)}. 😊"
                else:
                    return f"Hmm, I don't think you've told me about that yet. Would you like to share? 😊"
        
        return None
    
    def get_current_user(self) -> Optional[Dict]:
        """Get current user info"""
        return self.current_user
    
    def is_user_logged_in(self) -> bool:
        """Check if user is logged in"""
        return self.current_user is not None
    
    def get_relevant_memories(self, user_message: str, supabase_service, limit: int = 3) -> List[Dict]:
        """Get relevant memories for conversational context"""
        try:
            user_id = self.current_user.get('user_id')
            if not user_id:
                return []
            
            # Extract key terms from the message for memory search
            search_terms = []
            words = user_message.lower().split()
            
            # Look for important nouns and names
            important_words = [word for word in words if len(word) > 3 and word.isalpha()]
            search_terms.extend(important_words[:5])  # Take first 5 important words
            
            if search_terms:
                memories = supabase_service.search_user_memories(user_id, search_terms, limit)
                return memories if memories else []
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting relevant memories: {e}")
            return []
    
    # ========================================================================
    # CONVERSATION PROCESSING - WITH MEMORY
    # ========================================================================
    
    def process_message(self, user_message: str, 
                       conversation_history: list = None,
                       memory_context: Dict = None) -> Tuple[str, Dict]:
        """
        Process user message with memory layer and context
        
        Args:
            user_message: The user's input message
            conversation_history: Recent conversation history
            memory_context: Additional context including user info and memories
            
        Returns: (response, metadata)
        """
        # Handle Supabase users properly
        if not self.is_user_logged_in():
            return "Please log in to continue chatting.", {"error": "No user logged in"}
        
        # Clean input
        user_message = LanguageUtils.clean_text(user_message)
        
        # Process memory context if provided
        user_name = self.current_user.get("name", "User")
        user_language = self.language.value
        
        if memory_context:
            # Extract user information from memory context
            if 'user_name' in memory_context:
                user_name = memory_context['user_name']
            if 'language' in memory_context:
                user_language = memory_context['language']
            
            # Store memory context for use in response generation
            self._current_memory_context = memory_context
        else:
            self._current_memory_context = {}
        
        # Check if this is a name preference response (needs supabase_service)
        if hasattr(self, '_supabase_service'):
            is_name_response, name_message = self.check_for_name_preference(user_message, self._supabase_service)
            if is_name_response:
                return name_message, {
                    "user": self.current_user.get("name"),
                    "language": self.language.value,
                    "response_type": "name_confirmation",
                    "mood": "happy"
                }
            
            # Check for memory recall requests
            recall_response = self.check_for_memory_recall(user_message, self._supabase_service)
            if recall_response:
                return recall_response, {
                    "user": self.current_user.get("name"),
                    "language": self.language.value,
                    "response_type": "memory_recall",
                    "mood": "helpful"
                }
        
        user_name = self.current_user.get("name")
        
        metadata = {
            "user": user_name,
            "language": self.language.value,
            "input_length": len(user_message),
            "used_llm": False,
            "memory_extracted": False,
        }
        
        # Detect language from input
        detected_language = LanguageUtils.detect_language(user_message)
        metadata["detected_language"] = detected_language.value
        
        # Update language if different
        if detected_language != self.language:
            self.language = detected_language
        
        # Detect mood
        mood, confidence = LanguageUtils.detect_mood(user_message, detected_language)
        metadata["mood"] = mood.value
        metadata["mood_confidence"] = confidence
        
        # ====================================================================
        # MEMORY: Extract relationships from message (Legacy system)
        # ====================================================================
        relationships = self.memory_service.extract_relationships(user_name, user_message)
        if relationships:
            metadata["memory_extracted"] = True
            metadata["relationships_found"] = [r["name"] for r in relationships]
            logger.info(f"Extracted relationships: {relationships}")
        
        # ====================================================================
        # MEMORY: Extract memories using Supabase (New system)
        # ====================================================================
        if hasattr(self, '_supabase_service'):
            extracted_memories = self.extract_memories_from_message(user_message, self._supabase_service)
            if extracted_memories:
                metadata["supabase_memory_extracted"] = True
                metadata["supabase_memories_count"] = len(extracted_memories)
                logger.info(f"Extracted Supabase memories: {len(extracted_memories)}")
        
        # ====================================================================
        # MEMORY: Record mood for trends
        # ====================================================================
        self.memory_service.record_mood(user_name, mood.value, confidence)
        
        # ====================================================================
        # PRIORITY 1: SPECIAL PATTERNS (Greetings, Goodbyes)
        # ====================================================================
        
        print(f"[DEBUG] Processing: {user_message}")
        print(f"[DEBUG] Language: {detected_language.value}, Mood: {mood.value}")
        
        if LanguageUtils.is_goodbye(user_message, detected_language):
            print("[DEBUG] Matched: Goodbye")
            response = self._handle_goodbye()
            metadata["scenario"] = "goodbye"
            metadata["response_type"] = "special"
            logger.info("Matched: Goodbye")
        
        elif LanguageUtils.is_greeting(user_message, detected_language):
            print("[DEBUG] Matched: Greeting")
            response = self._handle_greeting()
            metadata["scenario"] = "greeting"
            metadata["response_type"] = "special"
            logger.info("Matched: Greeting")
        
        # ====================================================================
        # PRIORITY 2: STRONG EMOTIONS - Use specific emotion responses
        # ====================================================================
        
        elif mood != Mood.NEUTRAL and confidence > 0.6:
            response = self._generate_emotion_response(user_message, detected_language, mood)
            metadata["scenario"] = f"emotion_{mood.value}"
            metadata["response_type"] = "emotion"
            logger.info(f"Matched: Strong emotion - {mood.value}")
        
        # ====================================================================
        # PRIORITY 3: TRY SCENARIO ENGINE (predefined responses)
        # ====================================================================
        
        else:
            scenario_name, scenario_response = self.scenario_engine.find_scenario(
                user_message, 
                detected_language.value
            )
            
            if scenario_response:
                response = scenario_response
                metadata["scenario"] = scenario_name
                metadata["response_type"] = "scenario"
                logger.info(f"Matched scenario: {scenario_name}")
            
            # ====================================================================
            # PRIORITY 4: CONVERSATIONAL SUMMARIZER (Natural, concise responses)
            # ====================================================================
            
            else:
                # Try conversational summarizer for natural responses
                try:
                    # Get memory context for the summarizer
                    memory_context = None
                    if hasattr(self, '_supabase_service'):
                        # Get relevant memories from Supabase
                        relevant_memories = self.get_relevant_memories(user_message, self._supabase_service)
                        if relevant_memories:
                            memory_context = {'relevant_memories': relevant_memories}
                    
                    # Use conversational summarizer
                    response, summarizer_metadata = self.conversational_summarizer.process_message(
                        user_message, 
                        user_name, 
                        memory_context
                    )
                    
                    # Merge metadata
                    metadata.update(summarizer_metadata)
                    metadata["scenario"] = "conversational_summarizer"
                    logger.info(f"Used conversational summarizer: mood={summarizer_metadata.get('mood')}, context={summarizer_metadata.get('context')}")
                    
                except Exception as e:
                    logger.error(f"Conversational summarizer error: {e}")
                    # Fallback to original LLM approach
                    if self.llm_service.is_enabled():
                        # GET MEMORY CONTEXT - Enhanced with passed context
                        memory_summary = self.memory_service.create_memory_summary(user_name)
                        
                        # Combine memory service context with passed memory context
                        combined_memory_context = memory_summary
                        if hasattr(self, '_current_memory_context') and self._current_memory_context:
                            combined_memory_context += f"\n\nAdditional Context: {self._current_memory_context}"
                        
                        metadata["memory_context"] = combined_memory_context
                        
                        llm_response = self.llm_service.generate_response(
                            user_message,
                            language=detected_language.value,
                            mood=mood.value,
                            user_name=user_name,
                            memory_context=combined_memory_context,  # Use combined context
                            conversation_history=conversation_history
                        )
                        
                        if llm_response:
                            response = llm_response
                            metadata["response_type"] = "llm"
                            metadata["used_llm"] = True
                            metadata["scenario"] = "llm_generated"
                            logger.info("Used LLM for response")
                        else:
                            response = self._response_neutral(detected_language, user_name)
                            metadata["response_type"] = "default"
                    else:
                        response = self._response_neutral(detected_language, user_name)
                        metadata["response_type"] = "default"
                        logger.info("LLM disabled, using default response")
        
        # Save conversation
        self.db.save_conversation(
            user_name,
            user_message,
            response,
            mood.value,
            metadata
        )
        
        return response, metadata
    
    # ========================================================================
    # EMOTION RESPONSE HANDLER (KEEP ALL EXISTING CODE BELOW)
    # ========================================================================
    
    def _generate_emotion_response(self, user_message: str, language: Language, mood: Mood) -> str:
        """Generate response based on strong emotion detected"""
        user_name = self.current_user.get("name")
        
        if mood == Mood.HAPPY:
            return self._response_happy(language, user_name)
        elif mood == Mood.SAD:
            return self._response_sad(language, user_name)
        elif mood == Mood.ANGRY:
            return self._response_angry(language, user_name)
        elif mood == Mood.ANXIOUS:
            return self._response_anxious(language, user_name)
        elif mood == Mood.CONFUSED:
            return self._response_confused(language, user_name)
        elif mood == Mood.FRUSTRATED:
            return self._response_frustrated(language, user_name)
        elif mood == Mood.TIRED:
            return self._response_tired(language, user_name)
        else:
            return self._response_neutral(language, user_name)
    
    # ========================================================================
    # KEEP ALL YOUR EXISTING RESPONSE METHODS UNCHANGED
    # ========================================================================
    
    def _handle_greeting(self) -> str:
        """Handle greeting with user memory"""
        user_name = self.current_user.get("name")
        
        greetings = {
            Language.TELUGU: [
                f"నమస్కారం {user_name}! ఎలా ఉన్నారు?",
                f"హాయ్ {user_name}! నీకు సంతోషం ఎక్కడ నుండి వచ్చిన్ది?",
            ],
            Language.HINDI: [
                f"नमस्ते {user_name}! आप कैसे हैं?",
                f"हाय {user_name}! आपसे मिलकर खुशी हुई।",
            ],
            Language.ENGLISH: [
                f"Hello {user_name}! How are you?",
                f"Hi {user_name}! Great to see you!",
            ],
        }
        
        return random.choice(greetings.get(self.language, greetings[Language.ENGLISH]))
    
    def _handle_goodbye(self) -> str:
        """Handle goodbye"""
        goodbyes = {
            Language.TELUGU: [
                "కలిసీ సుఖంగా ఉండం! తర్వాత కలుస్కోదాం.",
                "అలవిదా! ఆనందంగా ఉండం.",
            ],
            Language.HINDI: [
                "अलविदा! खुश रहें। फिर मिलेंगे।",
                "जल्दी मिलेंगे! आप खुश रहें।",
            ],
            Language.ENGLISH: [
                "Goodbye! Take care!",
                "See you soon! Have a great day!",
            ],
        }
        
        return random.choice(goodbyes.get(self.language, goodbyes[Language.ENGLISH]))
    
    # KEEP ALL YOUR EXISTING _response_* METHODS UNCHANGED
    def _response_happy(self, language: Language, user_name: str) -> str:
        responses = {
            Language.TELUGU: [
                f"అద్భుతం {user_name}! మీ సంతోషం నాకు ఆనందం ఇస్తుంది.",
                f"సూపర్! {user_name}, ఈ సంతోషం ఎక్కడ నుండి వచ్చిన్ది?",
            ],
            Language.HINDI: [
                f"शानदार {user_name}! आपकी खुशी मेरी खुशी है।",
                f"वाह {user_name}! क्या हुआ?",
            ],
            Language.ENGLISH: [
                f"That's wonderful {user_name}! I'm happy for you.",
                f"{user_name}, tell me more about this joy!",
            ],
        }
        return random.choice(responses.get(language, responses[Language.ENGLISH]))
    
    def _response_sad(self, language: Language, user_name: str) -> str:
        responses = {
            Language.TELUGU: [
                f"నిన్ను చేరిపోయిన పరిస్థితి నాకు అర్థమైంది {user_name}. నేను ఇక్కడ ఉన్నాను.",
                f"{user_name}, ఈ నొప్పి నాకు చూస్తుందాను. చెప్పు.",
            ],
            Language.HINDI: [
                f"मुझे आपकी बात समझ आई {user_name}। मैं यहां हूं।",
                f"{user_name}, दर्द समझता हूं। बताइए क्या हुआ।",
            ],
            Language.ENGLISH: [
                f"I'm sorry you're going through this {user_name}. I'm here to listen.",
                f"{user_name}, talk to me. What's wrong?",
            ],
        }
        return random.choice(responses.get(language, responses[Language.ENGLISH]))
    
    def _response_angry(self, language: Language, user_name: str) -> str:
        responses = {
            Language.TELUGU: [
                f"నీ కోపం నాకు అర్థమైంది {user_name}. చెప్పు.",
                f"నిరాశ ఎవరికి ఇష్టం? నేను ఇక్కడ ఉన్నాను.",
            ],
            Language.HINDI: [
                f"तुम्हारा गुस्सा मेरे लिए समझ आता है {user_name}। बताइए क्या हुआ।",
                f"मैं सुन रहा हूं। बोलो।",
            ],
            Language.ENGLISH: [
                f"I can feel your anger {user_name}. Tell me what happened.",
                f"I'm here to listen. What's bothering you?",
            ],
        }
        return random.choice(responses.get(language, responses[Language.ENGLISH]))
    
    def _response_anxious(self, language: Language, user_name: str) -> str:
        responses = {
            Language.TELUGU: [
                f"आंदोलन చేయవద్దు {user_name}. నేను ఇక్కడ ఉన్నాను.",
                f"భయపడకు. నీ వెంట నేను ఉన్నాను.",
            ],
            Language.HINDI: [
                f"चिंता मत करो {user_name}। मैं यहां हूं।",
                f"डरो मत। तुम सुरक्षित हो।",
            ],
            Language.ENGLISH: [
                f"Don't worry {user_name}. I'm here.",
                f"Take a breath. You're safe with me.",
            ],
        }
        return random.choice(responses.get(language, responses[Language.ENGLISH]))
    
    def _response_confused(self, language: Language, user_name: str) -> str:
        responses = {
            Language.TELUGU: [
                f"గందరగోళం నాకు అర్థమైంది {user_name}. విషయం చెప్పు.",
                f"చిలికిపోయా? విషయాలు సపష్టం చెయ్యదాన్ని నేను ఇక్కడ ఉన్నాను.",
            ],
            Language.HINDI: [
                f"भ्रमित होना सामान्य है {user_name}। बताइए।",
                f"आइए, एक-एक करके समझते हैं।",
            ],
            Language.ENGLISH: [
                f"Confusion is normal {user_name}. Tell me what's unclear.",
                f"Let's work through this together.",
            ],
        }
        return random.choice(responses.get(language, responses[Language.ENGLISH]))
    
    def _response_frustrated(self, language: Language, user_name: str) -> str:
        responses = {
            Language.TELUGU: [
                f"విసుగు నాకు అర్థమైంది {user_name}. చెప్పు.",
                f"కుచేష్టితం చాలా నిర్ధారణ. నేను ఇక్కడ ఉన్నాను.",
            ],
            Language.HINDI: [
                f"निराशा मैं समझता हूं {user_name}। क्या हुआ?",
                f"खीज की भावना आम है। बताइए।",
            ],
            Language.ENGLISH: [
                f"I feel your frustration {user_name}. What's the issue?",
                f"Frustration is valid. Tell me what's wrong.",
            ],
        }
        return random.choice(responses.get(language, responses[Language.ENGLISH]))
    
    def _response_tired(self, language: Language, user_name: str) -> str:
        responses = {
            Language.TELUGU: [
                f"అలసిపోయా {user_name}? విశ్రాంతి తీసుకో.",
                f"శక్తిలేనిది సాధారణ. కొంచెం విశ్రాంతి తీసుకో.",
            ],
            Language.HINDI: [
                f"थक गए हो {user_name}? आराम करो।",
                f"थकान सामान्य है। विश्राम लो।",
            ],
            Language.ENGLISH: [
                f"You sound tired {user_name}. Take some rest.",
                f"It's okay to be tired. You deserve a break.",
            ],
        }
        return random.choice(responses.get(language, responses[Language.ENGLISH]))
    
    def _response_neutral(self, language: Language, user_name: str) -> str:
        """Default neutral response"""
        responses = {
            Language.TELUGU: [
                f"నీ గురించి మరింత చెప్పు {user_name}. నేను వింటున్నాను.",
            ],
            Language.HINDI: [
                f"अधिक बताइए {user_name}। मैं सुन रहा हूं।",
            ],
            Language.ENGLISH: [
                f"Tell me more {user_name}. I'm listening.",
            ],
        }
        return random.choice(responses.get(language, responses[Language.ENGLISH]))
    
    # ========================================================================
    # CONTEXT AND MEMORY
    # ========================================================================
    
    def get_conversation_summary(self) -> str:
        """Get summary of recent conversations"""
        if not self.is_user_logged_in():
            return ""
        
        return self.db.get_conversation_summary(self.current_user.get("name"))
    
    def get_user_stats(self) -> Dict:
        """Get user statistics"""
        if not self.is_user_logged_in():
            return {}
        
        user_name = self.current_user.get("name")
        conversations = self.db.load_conversations(user_name)
        
        # ADD MEMORY INFO
        memories = self.memory_service.get_all_people(user_name)
        preferences = self.memory_service.get_preferences(user_name)
        
        return {
            "user_name": user_name,
            "total_conversations": len(conversations),
            "language": self.language.value,
            "created_at": self.current_user.get("created_at"),
            "last_active": self.current_user.get("last_active"),
            "known_people": len(memories),  # ADD THIS
            "preferences": len(preferences),  # ADD THIS
        }
    
    # ========================================================================
    # ADMIN FUNCTIONS (KEEP AS IS)
    # ========================================================================
    
    def get_all_users(self) -> list:
        """Get all registered users"""
        return self.db.get_all_users()
    
    def user_exists(self, name: str) -> bool:
        """Check if user exists"""
        return self.db.name_exists(name)
    
    def get_total_users(self) -> int:
        """Get total number of users"""
        return self.db.user_count()