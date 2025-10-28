"""
language_utils.py - Language detection, mood analysis, and text processing
"""

import re
from typing import Tuple, Optional
from enum import Enum

class Language(Enum):
    TELUGU = "te"
    HINDI = "hi"
    ENGLISH = "en"

class Mood(Enum):
    HAPPY = "happy"
    SAD = "sad"
    ANXIOUS = "anxious"
    NEUTRAL = "neutral"
    ANGRY = "angry"

class LanguageUtils:
    """Handle language detection and processing"""
    
    # Telugu mood keywords
    TELUGU_MOOD_KEYWORDS = {
        Mood.HAPPY: ["సంతోషం", "ఆనందం", "బాగు", "చక్కగా", "సూపర్", "అద్భుతం"],
        Mood.SAD: ["దుఃఖం", "బాధ", "విచారం", "నిరాశ", "సరికాదు", "కోలిపోయిన"],
        Mood.ANGRY: ["కోపం", "చిరాకు", "చిరాక", "రోషం", "ఆగ్రహం"],
        Mood.ANXIOUS: ["భయం", "ఆందోళన", "చింత", "ఇబ్బంది", "సమస్య"],
    }
    
    # Hindi mood keywords
    HINDI_MOOD_KEYWORDS = {
        Mood.HAPPY: ["खुश", "अच्छा", "बढ़िया", "शानदार", "सुपर", "वाह"],
        Mood.SAD: ["दुःख", "बुरा", "परेशान", "चिंता", "उदास"],
        Mood.ANGRY: ["गुस्सा", "नाराज", "क्रोध", "चिड़चिड़ा"],
        Mood.ANXIOUS: ["डर", "घबराहट", "तनाव", "परेशानी"],
    }
    
    # English mood keywords
    ENGLISH_MOOD_KEYWORDS = {
        Mood.HAPPY: ["happy", "great", "wonderful", "excellent", "awesome", "amazing"],
        Mood.SAD: ["sad", "upset", "down", "unhappy", "terrible", "awful"],
        Mood.ANGRY: ["angry", "furious", "mad", "irritated", "frustrated"],
        Mood.ANXIOUS: ["anxious", "worried", "nervous", "scared", "afraid"],
    }
    
    @staticmethod
    def detect_language(text: str) -> Language:
        """Detect which language the text is in"""
        if not text:
            return Language.ENGLISH
        
        # Check Telugu script
        if re.search(r'[\u0C00-\u0C7F]', text):
            return Language.TELUGU
        
        # Check Devanagari script (Hindi)
        if re.search(r'[\u0900-\u097F]', text):
            return Language.HINDI
        
        return Language.ENGLISH
    
    @staticmethod
    def detect_mood(text: str, language: Language = None) -> Tuple[Mood, float]:
        """
        Detect mood from text
        Returns: (mood, confidence_score)
        """
        if not language:
            language = LanguageUtils.detect_language(text)
        
        text_lower = text.lower()
        
        # Select keyword set based on language
        if language == Language.TELUGU:
            mood_keywords = LanguageUtils.TELUGU_MOOD_KEYWORDS
        elif language == Language.HINDI:
            mood_keywords = LanguageUtils.HINDI_MOOD_KEYWORDS
        else:
            mood_keywords = LanguageUtils.ENGLISH_MOOD_KEYWORDS
        
        mood_scores = {}
        
        # Check each mood
        for mood, keywords in mood_keywords.items():
            matches = sum(1 for keyword in keywords if keyword.lower() in text_lower)
            if matches > 0:
                confidence = min(matches / len(keywords), 1.0)
                mood_scores[mood] = confidence
        
        # Return highest scoring mood or neutral
        if mood_scores:
            best_mood = max(mood_scores.items(), key=lambda x: x[1])
            return best_mood[0], best_mood[1]
        
        return Mood.NEUTRAL, 0.5
    
    @staticmethod
    def extract_name(text: str, language: Language = None) -> Optional[str]:
        """Extract name from introduction text"""
        if not language:
            language = LanguageUtils.detect_language(text)
        
        patterns = {}
        
        if language == Language.TELUGU:
            patterns = [
                r"నా పేరు\s+([^\s\.।।]+)",
                r"నేను\s+([^\s]+)\s+(?:అని|అన్నారు)",
                r"([^\s]+)\s+అని\s+పిలుస్తారు",
            ]
        elif language == Language.HINDI:
            patterns = [
                r"मेरा नाम\s+([^\s\.।।]+)",
                r"मैं\s+([^\s]+)\s+(?:हूँ|हूं)",
                r"([^\s]+)\s+कहते?\s+हैं",
            ]
        else:
            patterns = [
                r"my name is\s+([a-z]+)",
                r"i'm\s+([a-z]+)",
                r"i am\s+([a-z]+)",
                r"call me\s+([a-z]+)",
            ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                if len(name) >= 2 and not name.isdigit():
                    return name.title()
        
        return None
    
    @staticmethod
    def get_language_name(language: Language) -> str:
        """Get display name for language"""
        names = {
            Language.TELUGU: "తెలుగు",
            Language.HINDI: "हिंदी",
            Language.ENGLISH: "English",
        }
        return names.get(language, "Unknown")
    
    @staticmethod
    def get_language_code(language: Language) -> str:
        """Get language code"""
        return language.value
    
    @staticmethod
    def is_greeting(text: str, language: Language = None) -> bool:
        """Check if text is a greeting - must be at start or standalone"""
        if not language:
            language = LanguageUtils.detect_language(text)
        
        greetings = {
            Language.TELUGU: ["నమస్కారం", "హాయ్", "హలో", "సలాం"],
            Language.HINDI: ["नमस्ते", "हाय", "हेलो", "सलाम"],
            Language.ENGLISH: ["hello", "hi", "hey", "greetings", "good morning", "good afternoon", "good evening"],
        }
        
        text_lower = text.lower().strip()
        words = text_lower.split()
        
        # Check if it's a short message (likely a greeting)
        if len(words) <= 3:
            return any(g.lower() in text_lower for g in greetings.get(language, []))
        
        # For longer messages, only match if greeting is at the start
        for greeting in greetings.get(language, []):
            if text_lower.startswith(greeting.lower()):
                return True
        
        return False
    
    @staticmethod
    def is_goodbye(text: str, language: Language = None) -> bool:
        """Check if text is a goodbye - must be at start or standalone"""
        if not language:
            language = LanguageUtils.detect_language(text)
        
        goodbyes = {
            Language.TELUGU: ["బై", "అలవిదా", "వీడిపెట్టు", "తర్వాత"],
            Language.HINDI: ["अलविदा", "विदा", "बाय", "फिर मिलेंगे"],
            Language.ENGLISH: ["bye", "goodbye", "farewell", "see you", "good night", "take care"],
        }
        
        text_lower = text.lower().strip()
        words = text_lower.split()
        
        # Check if it's a short message (likely a goodbye)
        if len(words) <= 4:
            return any(g.lower() in text_lower for g in goodbyes.get(language, []))
        
        # For longer messages, only match if goodbye is at the start or end
        for goodbye in goodbyes.get(language, []):
            if text_lower.startswith(goodbye.lower()) or text_lower.endswith(goodbye.lower()):
                return True
        
        return False
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean user input text"""
        if not text:
            return ""
        # Remove extra spaces
        text = " ".join(text.split())
        return text.strip()
    
    @staticmethod
    def format_response(text: str, language: Language) -> str:
        """Format response for better readability in target language"""
        return text