"""
scenario_engine.py - Define and manage response scenarios
Easy to extend with new scenarios without touching other code
"""

import re
import random
from typing import Dict, List, Optional, Tuple
from enum import Enum

class ScenarioType(Enum):
    DIRECT = "direct"              # Direct scenario match
    KEYWORD = "keyword"            # Match by keywords
    PATTERN = "pattern"            # Regex pattern match
    CONTEXT = "context"            # Based on conversation context

class ScenarioEngine:
    """Manage scenario-based responses"""
    
    def __init__(self):
        self.scenarios = self._load_scenarios()
    
    def _load_scenarios(self) -> Dict:
        """Load all scenarios - easy to extend"""
        return {
            "te": self._get_telugu_scenarios(),
            "hi": self._get_hindi_scenarios(),
            "en": self._get_english_scenarios(),
        }
    
    # ========================================================================
    # TELUGU SCENARIOS
    # ========================================================================
    
    def _get_telugu_scenarios(self) -> Dict:
        """Define all Telugu response scenarios"""
        return {
            # Greetings
            "greeting": {
                "type": ScenarioType.KEYWORD,
                "keywords": ["నమస్కారం", "హాయ్", "హలో", "సలాం", "మీరు"],
                "responses": [
                    "నమస్కారం! నేను జంబో. ఎలా ఉన్నారు?",
                    "హాయ్! నీకు సంతోషం నుండాలని కోరుకుంటున్నాను.",
                    "హలో! మీకు సహాయం చేయాలని నేను ఎంతో కోరుకుంటున్నాను.",
                ]
            },
            
            # Mood - Happy
            "mood_happy": {
                "type": ScenarioType.KEYWORD,
                "keywords": ["సంతోషం", "ఆనందం", "బాగు", "చక్కగా", "సూపర్"],
                "responses": [
                    "అద్భుతం! మీ సంతోషం నాకు ఆనందం ఇస్తుంది.",
                    "వాహ్! ఎంతో సంతోషం. ఈ సంతోషం ఎక్కడ నుండి వచ్చింది?",
                    "సూపర్! మీరు సంతోషంగా ఉన్నారన్నది నాకు ఖుషీ చేస్తుంది.",
                ]
            },
            
            # Mood - Sad
            "mood_sad": {
                "type": ScenarioType.KEYWORD,
                "keywords": ["దుఃఖం", "బాధ", "విచారం", "నిరాశ", "సరికాదు"],
                "responses": [
                    "నిన్ను చేరిపోయిన పరిస్థితి అర్థమైంది. నేను ఇక్కడ ఉన్నాను.",
                    "ఆ నొప్పి నాకు చూస్తున్నాను. చెప్పు, ఏమీ సహాయం చేయగలను?",
                    "బాధ చేసిన విషయానికి సంతాపం. కానీ గుర్తుంచుకో, ఇది కూడా జరుతుంది.",
                ]
            },
            
            # Health
            "health_concern": {
                "type": ScenarioType.KEYWORD,
                "keywords": ["జ్వరం", "సర్దీ", "చలి", "గాయం", "ఇబ్బంది", "ఆరోగ్యం"],
                "responses": [
                    "మీ ఆరోగ్యం ముఖ్యమైనది. బాగా విశ్రాంతి తీసుకోండి. సమస్య కొనసాగితే డాక్టరుని చూడండి.",
                    "స్వస్థతకు నా భక్తులు. బాగా జాగ్రత్త చేసుకోండి!",
                ]
            },
            
            # Help Request
            "help_request": {
                "type": ScenarioType.KEYWORD,
                "keywords": ["సహాయం", "చేయగలరా", "పరిష్కారం", "ఎలా", "సూచన"],
                "responses": [
                    "నిశ్చితంగా సహాయం చేస్తాను! ఏమీ చెప్పు.",
                    "నీకు ఏమీ సహాయం చేయాలనుకుంటే, నేను ఎదుట ఉన్నాను!",
                ]
            },
            
            # Goodbye
            "goodbye": {
                "type": ScenarioType.KEYWORD,
                "keywords": ["బై", "అలవిదా", "వీడిపెట్టు", "తర్వాత", "ఆపు"],
                "responses": [
                    "కలిసీ సుఖంగా ఉండండి! మరలా కలుసుకోదాం.",
                    "అలవిదా! ఆనందంగా ఉండండి.",
                    "మీకు విదానం. తర్వాత సంలాపించుకుందాం!",
                ]
            },
            
            # Thank you
            "gratitude": {
                "type": ScenarioType.KEYWORD,
                "keywords": ["ధన్యవాదాలు", "కృతజ్ఞ", "ఆభారి", "ధన్యవాదం"],
                "responses": [
                    "నీకు ఆభారి! నా సహాయం కొంచెం ఉపయోగపడిందేమో, చాలా ఆనందం.",
                    "సుందరమైన మాటలు! నేనూ నీకు సంతోషం కోరుకుంటున్నాను.",
                ]
            },
        }
    
    # ========================================================================
    # HINDI SCENARIOS
    # ========================================================================
    
    def _get_hindi_scenarios(self) -> Dict:
        """Define all Hindi response scenarios"""
        return {
            # Greetings
            "greeting": {
                "type": ScenarioType.KEYWORD,
                "keywords": ["नमस्ते", "हाय", "हेलो", "सलाम", "कैसे"],
                "responses": [
                    "नमस्ते! मैं जंबो हूँ। आप कैसे हैं?",
                    "हाय! मुझे खुशी है आपसे मिलकर।",
                    "नमस्ते! आपकी मदद करने के लिए मैं यहाँ हूँ।",
                ]
            },
            
            # Mood - Happy
            "mood_happy": {
                "type": ScenarioType.KEYWORD,
                "keywords": ["खुश", "अच्छा", "बढ़िया", "शानदार", "सुपर"],
                "responses": [
                    "वाह! आपकी खुशी मुझे भी खुश कर रही है।",
                    "शानदार! आप खुश हैं यह सुनकर दिल खुश हो गया।",
                    "बहुत अच्छा! क्या बताइए, ऐसा क्या हुआ?",
                ]
            },
            
            # Mood - Sad
            "mood_sad": {
                "type": ScenarioType.KEYWORD,
                "keywords": ["दुःख", "बुरा", "परेशान", "चिंता", "उदास"],
                "responses": [
                    "मुझे आपकी बात समझ आई। मैं यहाँ हूँ आपके साथ।",
                    "यह दर्द मेरे लिए समझ आता है। कृपया बताइए।",
                    "कठिन समय गुजर रहे हैं? मैं सुनने के लिए तैयार हूँ।",
                ]
            },
            
            # Health
            "health_concern": {
                "type": ScenarioType.KEYWORD,
                "keywords": ["बुखार", "सर्दी", "दर्द", "स्वास्थ्य", "बीमार"],
                "responses": [
                    "आपका स्वास्थ्य महत्वपूर्ण है। अच्छे से आराम लें। अगर समस्या रहे तो डॉक्टर को देखें।",
                    "जल्दी ठीक हो जाइए! अपना ध्यान रखें।",
                ]
            },
            
            # Help Request
            "help_request": {
                "type": ScenarioType.KEYWORD,
                "keywords": ["मदद", "कर सकते", "समाधान", "कैसे", "सलाह"],
                "responses": [
                    "हाँ, मैं आपकी मदद करूँगा! बताइए क्या चाहिए।",
                    "मुझे खुशी है कि आप पूछ रहे हैं। मैं यहाँ हूँ!",
                ]
            },
            
            # Goodbye
            "goodbye": {
                "type": ScenarioType.KEYWORD,
                "keywords": ["अलविदा", "विदा", "बाय", "फिर मिलेंगे", "रुकिए"],
                "responses": [
                    "अलविदा! खुश रहें। फिर मिलेंगे।",
                    "जल्दी मिलेंगे! आप खुश रहें।",
                ]
            },
            
            # Gratitude
            "gratitude": {
                "type": ScenarioType.KEYWORD,
                "keywords": ["धन्यवाद", "कृतज्ञ", "शुक्रिया", "आभारी"],
                "responses": [
                    "आपका स्वागत है! मुझे खुशी है कि मदद कर सकी।",
                    "धन्यवाद! आपकी खुशी मेरी खुशी है।",
                ]
            },
        }
    
    # ========================================================================
    # ENGLISH SCENARIOS
    # ========================================================================
    
    def _get_english_scenarios(self) -> Dict:
        """Define all English response scenarios"""
        return {
            "greeting": {
                "type": ScenarioType.KEYWORD,
                "keywords": ["hello", "hi", "hey", "greetings"],
                "responses": [
                    "Hello! I'm Jumbo. How are you doing?",
                    "Hi there! Great to meet you!",
                ]
            },
            "mood_happy": {
                "type": ScenarioType.KEYWORD,
                "keywords": ["happy", "great", "wonderful", "excellent", "awesome"],
                "responses": [
                    "That's wonderful! Your happiness makes me happy too!",
                    "Excellent! Tell me more about what's making you so happy.",
                ]
            },
            "mood_sad": {
                "type": ScenarioType.KEYWORD,
                "keywords": ["sad", "upset", "down", "unhappy", "terrible"],
                "responses": [
                    "I understand you're going through something. I'm here to listen.",
                    "That sounds tough. What's bothering you?",
                ]
            },
            "help_request": {
                "type": ScenarioType.KEYWORD,
                "keywords": ["help", "can you", "how to", "advice", "suggest"],
                "responses": [
                    "Of course! I'm here to help. What do you need?",
                    "I'd be happy to assist. Tell me more.",
                ]
            },
            "goodbye": {
                "type": ScenarioType.KEYWORD,
                "keywords": ["bye", "goodbye", "farewell", "see you", "later"],
                "responses": [
                    "Goodbye! Take care and stay happy!",
                    "See you soon! Have a great day!",
                ]
            },
        }
    
    # ========================================================================
    # MATCHING LOGIC
    # ========================================================================
    
    def find_scenario(self, text: str, language: str = "te") -> Optional[Tuple[str, str]]:
        """
        Find matching scenario for user input
        Returns: (scenario_name, response)
        """
        scenarios = self.scenarios.get(language, {})
        text_lower = text.lower()
        
        for scenario_name, scenario in scenarios.items():
            if scenario["type"] == ScenarioType.KEYWORD:
                # Check if any keyword matches
                keywords = scenario.get("keywords", [])
                for keyword in keywords:
                    if keyword.lower() in text_lower:
                        response = random.choice(scenario.get("responses", []))
                        return scenario_name, response
            
            elif scenario["type"] == ScenarioType.PATTERN:
                # Use regex pattern matching
                pattern = scenario.get("pattern", "")
                if re.search(pattern, text, re.IGNORECASE):
                    response = random.choice(scenario.get("responses", []))
                    return scenario_name, response
        
        return None, None
    
    def add_custom_scenario(self, language: str, name: str, scenario: Dict):
        """Add custom scenario at runtime"""
        if language not in self.scenarios:
            self.scenarios[language] = {}
        self.scenarios[language][name] = scenario
    
    def get_default_response(self, language: str = "te") -> str:
        """Get default response when no scenario matches"""
        defaults = {
            "te": "నా నుండి ఇంకా ఏమీ చెప్పండి. మీకు ఏమీ సహాయం చేయగలను?",
            "hi": "और भी बताइए। मैं आपकी मदद करने के लिए यहाँ हूँ।",
            "en": "Tell me more! I'm here to help.",
        }
        return defaults.get(language, defaults["en"])