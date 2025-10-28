"""
llm_service.py - Groq LLM Service with Debug Logging
"""

import logging
from typing import Optional
from config import Config

logger = logging.getLogger(__name__)

class LLMService:
    """Handle Groq LLM API calls"""
    
    def __init__(self):
        self.enabled = Config.LLM_ENABLED
        self.client = None
        
        if self.enabled:
            try:
                from groq import Groq
                # Initialize without extra parameters
                self.client = Groq(api_key=Config.GROQ_API_KEY)
                logger.info("✓ Groq LLM initialized successfully")
                print("✓ Groq LLM initialized successfully")
            except TypeError as e:
                # If proxies error, try alternate initialization
                logger.warning(f"Initial Groq init failed: {e}, trying alternate method...")
                try:
                    from groq import Groq
                    self.client = Groq()
                    self.client.api_key = Config.GROQ_API_KEY
                    logger.info("✓ Groq LLM initialized with alternate method")
                    print("✓ Groq LLM initialized with alternate method")
                except Exception as e2:
                    logger.error(f"✗ Failed to initialize Groq: {e2}")
                    print(f"✗ Failed to initialize Groq: {e2}")
                    self.enabled = False
            except Exception as e:
                logger.error(f"✗ Failed to initialize Groq: {e}")
                print(f"✗ Failed to initialize Groq: {e}")
                self.enabled = False
        else:
            logger.warning("✗ LLM is disabled - no API key found")
            print("✗ LLM is disabled - no API key found")
    
    def generate_response(self, user_message: str, language: str = "te", 
                         mood: str = "neutral", user_name: str = None) -> Optional[str]:
        """
        Generate response using Groq LLM
        """
        
        if not self.enabled or not self.client:
            logger.error("✗ LLM Service not available")
            print("✗ LLM Service not available")
            return None
        
        try:
            logger.info(f"→ Calling LLM for: {user_message[:50]}...")
            print(f"→ Calling LLM for: {user_message[:50]}...")
            
            # Create language-specific system prompt
            system_prompt = self._get_system_prompt(language, user_name, mood)
            
            logger.info(f"→ System prompt language: {language}")
            print(f"→ System prompt language: {language}")
            
            # Call Groq API
            logger.info("→ Making API call to Groq...")
            print("→ Making API call to Groq...")
            
            message = self.client.chat.completions.create(
                model=Config.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=Config.LLM_TEMPERATURE,
                max_tokens=Config.LLM_MAX_TOKENS,
            )
            
            response = message.choices[0].message.content
            logger.info(f"✓ LLM generated response: {response[:50]}...")
            print(f"✓ LLM generated response: {response[:50]}...")
            return response
            
        except Exception as e:
            logger.error(f"✗ LLM error: {e}")
            print(f"✗ LLM error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _get_system_prompt(self, language: str, user_name: str = None, mood: str = "neutral") -> str:
        """Generate language-specific system prompt"""
        
        name_part = f" {user_name}" if user_name else ""
        
        if language == "te":
            return f"""మీరు జంబో, ఒక దయాకరమైన AI సహచారి. 
తెలుగులో సరిగా మరియు సహానుభూతిపూర్వకంగా సమాధానం ఇవ్వండి.

ముఖ్య చేతిపట్టికలు:
- సర్వదా తెలుగులో మాట్లాడండి
- చిన్న, సంభాషణ ప్రతిస్పందనలు (2-3 వాక్యాలు)
- వినయ మరియు సంతానం చూపించండి
- సమర్థవంతమైన సలహా ఇవ్వండి

వినియోగదారు: {name_part}
మానసిక స్థితి: {mood}"""
        
        elif language == "hi":
            return f"""आप जंबो हैं, एक दयालु AI साथी।
हिंदी में सही और सहानुभूतिपूर्वक उत्तर दें।

मुख्य दिशानिर्देश:
- हमेशा हिंदी में बोलें
- छोटे, बातचीत करने वाले जवाब (2-3 वाक्य)
- विनम्रता और सम्मान दिखाएं
- व्यावहारिक सलाह दें

उपयोगकर्ता: {name_part}
मानसिक स्थिति: {mood}"""
        
        else:  # English
            return f"""You are Jumbo, a caring AI companion.
Respond in English with empathy and understanding.

Key Guidelines:
- Keep responses concise (2-3 sentences)
- Be warm and supportive
- Give practical advice
- Be conversational and natural

User: {name_part}
Emotional state: {mood}"""
    
    def is_enabled(self) -> bool:
        """Check if LLM is enabled"""
        return self.enabled