"""
llm_service.py - Groq LLM Service with Memory Context
"""

import logging
from typing import Optional, List, Dict
from config import Config

logger = logging.getLogger(__name__)

class LLMService:
    """Handle Groq LLM API calls with conversation context and memory"""
    
    def __init__(self):
        from config import config
        self.enabled = bool(config.llm.api_key)  # Enable if API key is present
        self.client = None
        
        if self.enabled:
            try:
                import os
                os.environ["GROQ_API_KEY"] = config.llm.api_key
                from groq import Groq
                # Simple initialization without extra parameters
                self.client = Groq(api_key=config.llm.api_key)
                logger.info("Groq LLM initialized successfully")
                print("✓ Groq LLM initialized successfully")
            except TypeError as e:
                # Handle version compatibility issues
                logger.warning(f"Groq init failed with TypeError: {e}, trying alternate method...")
                try:
                    from groq import Groq
                    self.client = Groq()
                    self.client.api_key = config.llm.api_key
                    logger.info("Groq LLM initialized with alternate method")
                    print("✓ Groq LLM initialized with alternate method")
                except Exception as e2:
                    logger.error(f"Failed to initialize Groq with alternate method: {e2}")
                    print(f"✗ Failed to initialize Groq: {e2}")
                    self.enabled = False
            except Exception as e:
                logger.error(f"Failed to initialize Groq: {e}")
                print(f"✗ Failed to initialize Groq: {e}")
                self.enabled = False
        else:
            logger.warning("LLM is disabled - no API key found")
            print("⚠ LLM is disabled - no API key found")
    
    def generate_response(self, user_message: str, language: str = "te", 
                         mood: str = "neutral", user_name: str = None,
                         memory_context: str = None,  # ADD THIS
                         conversation_history: List[Dict] = None) -> Optional[str]:
        """
        Generate response using Groq LLM with memory and conversation history
        
        Args:
            user_message: Current user message
            language: Language code (te, hi, en)
            mood: Detected mood
            user_name: User's name
            memory_context: Memory summary (friends, preferences, etc.)
            conversation_history: List of previous messages
        """
        
        if not self.enabled or not self.client:
            logger.error("LLM Service not available")
            return None
        
        try:
            logger.info(f"LLM Call - Message: {user_message[:50]}...")
            
            # Create system prompt WITH MEMORY
            system_prompt = self._get_system_prompt(
                language, user_name, mood, memory_context
            )
            
            # Build messages list
            messages = []
            
            # Add previous conversation for context (last 10 messages)
            if conversation_history:
                for msg in conversation_history[-10:]:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    
                    if role == "assistant":
                        messages.append({"role": "assistant", "content": content})
                    else:
                        messages.append({"role": "user", "content": content})
            
            # Add current message
            messages.append({"role": "user", "content": user_message})
            
            logger.info(f"Using {len(messages)} messages for context")

            # Call Groq API
            message = self.client.chat.completions.create(
                model=Config.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt}
                ] + messages,
                temperature=Config.LLM_TEMPERATURE,
                max_tokens=Config.LLM_MAX_TOKENS,
            )
            
            response = message.choices[0].message.content
            logger.info(f"LLM Response: {response[:50]}...")
            return response

        except Exception as e:
            logger.error(f"LLM error: {e}")
            return None
    
    def _get_system_prompt(self, language: str, user_name: str = None, 
                          mood: str = "neutral", memory_context: str = None) -> str:
        """Generate language-specific system prompt WITH MEMORY"""
        
        name_part = f" {user_name}" if user_name else ""
        
        # Add memory section if available
        memory_section = ""
        if memory_context:
            memory_section = f"\n\nUSER MEMORY:\n{memory_context}"
        
        if language == "te":
            return f"""నువ్వు జంబో, ఒక సంවేదనశీల AI సహచరి.

నీ లక్ష్యాలు:
1. తెలుగులో సపష్టంగా మాట్లాడు
2. వాడుకరి భావాలను అర్థం చేసుకో
3. వ్యక్తిగత మరియు సంఘీయ సలహా ఇవ్వు
4. గతీయ సంభాషణలను గుర్తుంచుకో
5. వాడుకరి పేరు సహజంగా ఉపయోగించు

సంపర్కం:
- సంక్షిప్తంగా, హృదయపూర్వకంగా మాట్లాడు (2-3 వాక్యాలు)
- వాడుకరి సంభావనను ప్రతిబింబించు
- చివరలో సంబంధిత ప్రశ్న అడుగు
- తెలుగు సంస్కృతిని గుర్తించు

మానస్సిక స్థితి: {mood}
{memory_section}

జంబో సమాధానం:"""

        elif language == "hi":
            return f"""आप जम्बो हो, एक सहानुभूतिपूर्ण एआई साथी।

आपके लक्ष्य:
1. हिंदी में स्पष्ट बात करो
2. उपयोगकर्ता की भावनाओं को समझो
3. व्यक्तिगत सलाह दो
4. पिछली बातचीत को याद रखो
5. उपयोगकर्ता का नाम स्वाभाविक रूप से उपयोग करो

संचार:
- संक्षिप्त, हृदयस्पर्शी प्रतिक्रिया (2-3 वाक्य)
- उपयोगकर्ता की भावना को प्रतिबिंबित करो
- अंत में संबंधित सवाल पूछो
- भारतीय संस्कृति को स्वीकार करो

मानसिक स्थिति: {mood}
{memory_section}

जम्बो का जवाब:"""

        else:  # English
            return f"""You are Jumbo, a caring elephant AI companion.

Your Goals:
1. Be empathetic and understanding
2. Provide supportive responses
3. Remember previous conversations
4. Use the user's name naturally
5. Offer practical advice

Communication Style:
- Keep responses brief and warm (2-3 sentences)
- Mirror the user's emotional tone
- End with a thoughtful question
- Reference past conversations when relevant

User: {name_part}
Emotional State: {mood}
{memory_section}

Your Response:"""
    
    def is_enabled(self) -> bool:
        """Check if LLM is enabled"""
        return self.enabled