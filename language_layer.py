"""
Language Layer for Jumbo Chatbot
Provides language detection, translation, and cultural context for Telugu and Hindi
"""

import re
import logging
import pickle
import json
import os
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from googletrans import Translator
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

# Make language detection deterministic
DetectorFactory.seed = 0

logger = logging.getLogger(__name__)

class LanguageConfig:
    """Configuration for supported languages"""
    SUPPORTED_LANGUAGES = {
        'te': {
            'name': 'telugu',
            'native_name': 'తెలుగు',
            'voice_code': 'te-IN',
            'voice_name': 'te-IN-Wavenet-A'
        },
        'hi': {
            'name': 'hindi',
            'native_name': 'हिन्दी',
            'voice_code': 'hi-IN',
            'voice_name': 'hi-IN-Wavenet-A'
        },
        'en': {
            'name': 'english',
            'native_name': 'English',
            'voice_code': 'en-IN',
            'voice_name': 'en-IN-Wavenet-D'
        }
    }

    DEFAULT_LANGUAGE = 'te'  # Telugu as default
    TRANSLATION_CACHE_SIZE = 1000

# Telugu Cultural Context
TELUGU_CONTEXT = {
    "festivals": {
        "ugadi": "Telugu New Year",
        "ఉగాది": "Telugu New Year",
        "sankranti": "Harvest festival",
        "సంక్రాంతి": "Harvest festival",
        "bonalu": "Telangana festival",
        "బోనాలు": "Telangana festival",
        "bathukamma": "Flower festival",
        "బతుకమ్మ": "Flower festival",
        "dasara": "Dussehra festival",
        "దసరా": "Dussehra festival",
        "deepavali": "Festival of lights",
        "దీపావళి": "Festival of lights"
    },

    "family_terms": {
        "అమ్మ": "mother",
        "amma": "mother",
        "తల్లి": "mother",
        "నాన్న": "father",
        "nanna": "father",
        "తండ్రి": "father",
        "అన్న": "elder brother",
        "anna": "elder brother",
        "అక్క": "elder sister",
        "akka": "elder sister",
        "తమ్ముడు": "younger brother",
        "చెల్లి": "younger sister",
        "అత్త": "aunt/mother-in-law",
        "మామ": "uncle",
        "పిల్లలు": "children",
        "కుటుంబం": "family"
    },

    "respect_markers": {
        "గారు": "respectful suffix (like sir/madam)",
        "అవును": "yes (respectful)",
        "కాదు": "no",
        "లేదు": "no (informal)",
        "మీరు": "you (formal)",
        "నువ్వు": "you (informal)",
        "తను": "he/she (respectful)"
    },

    "emotions_telugu": {
        "సంతోషం": "happy",
        "santosham": "happy",
        "దుఃఖం": "sad",
        "dukhham": "sad",
        "కోపం": "anger",
        "kopam": "anger",
        "భయం": "fear",
        "bayam": "fear",
        "ఆందోళన": "anxiety",
        "andolana": "anxiety",
        "ఒత్తిడి": "stress",
        "ottidi": "stress",
        "అలసట": "tired",
        "ఆనందం": "joy",
        "ఏకాంతం": "loneliness"
    },

    "common_greetings": {
        "నమస్కారం": "hello/greetings",
        "namaskaram": "hello/greetings",
        "హలో": "hello",
        "ఎలా ఉన్నారు": "how are you (formal)",
        "ela unnaru": "how are you (formal)",
        "ఎలా ఉన్నావు": "how are you (informal)",
        "ela unnavu": "how are you (informal)",
        "మంచిగా ఉన్నాను": "I'm good",
        "manchiga unnanu": "I'm good",
        "బాగుండి": "good/fine",
        "bagundi": "good/fine"
    },

    "food_culture": {
        "biryani": "famous rice dish",
        "బిర్యానీ": "famous rice dish",
        "pulihora": "tamarind rice",
        "పులిహోర": "tamarind rice",
        "pesarattu": "green gram dosa",
        "పెసరట్టు": "green gram dosa",
        "gongura": "sorrel leaves curry",
        "గోంగూర": "sorrel leaves curry",
        "pootharekulu": "traditional sweet",
        "పూతరేకులు": "traditional sweet"
    },

    "places": {
        "hyderabad": "capital of Telangana",
        "హైదరాబాద్": "capital of Telangana",
        "charminar": "historic monument",
        "చార్మినార్": "historic monument",
        "golconda": "historic fort",
        "గోల్కొండ": "historic fort",
        "vijayawada": "city in Andhra Pradesh",
        "విజయవాడ": "city in Andhra Pradesh",
        "tirupati": "famous temple town",
        "తిరుపతి": "famous temple town"
    }
}

# Hindi Cultural Context
HINDI_CONTEXT = {
    "festivals": {
        "diwali": "Festival of lights",
        "दिवाली": "Festival of lights",
        "holi": "Festival of colors",
        "होली": "Festival of colors",
        "raksha bandhan": "Brother-sister festival",
        "रक्षा बंधन": "Brother-sister festival",
        "dussehra": "Victory of good over evil",
        "दशहरा": "Victory of good over evil",
        "eid": "Islamic festival",
        "ईद": "Islamic festival"
    },

    "family_terms": {
        "माँ": "mother",
        "maa": "mother",
        "पिता": "father",
        "पिताजी": "father (respectful)",
        "papa": "father",
        "भाई": "brother",
        "bhai": "brother",
        "बहन": "sister",
        "behen": "sister",
        "दादी": "grandmother",
        "nani": "maternal grandmother",
        "परिवार": "family",
        "parivar": "family"
    },

    "respect_markers": {
        "जी": "respectful suffix",
        "ji": "respectful suffix",
        "आप": "you (formal)",
        "aap": "you (formal)",
        "तुम": "you (informal)",
        "tum": "you (informal)"
    },

    "emotions_hindi": {
        "खुश": "happy",
        "khush": "happy",
        "दुखी": "sad",
        "dukhi": "sad",
        "गुस्सा": "anger",
        "gussa": "anger",
        "डर": "fear",
        "dar": "fear",
        "चिंता": "worry/anxiety",
        "chinta": "worry",
        "थका": "tired",
        "thaka": "tired"
    },

    "common_greetings": {
        "नमस्ते": "hello/greetings",
        "namaste": "hello/greetings",
        "कैसे हैं": "how are you (formal)",
        "kaise hain": "how are you (formal)",
        "कैसे हो": "how are you (informal)",
        "kaise ho": "how are you (informal)",
        "ठीक हूँ": "I'm fine",
        "theek hoon": "I'm fine"
    }
}

# Telugu Mood Keywords
TELUGU_MOOD_KEYWORDS = {
    "happy": ["సంతోషం", "santosham", "ఆనందం", "anandam", "మంచి", "manchi", "బాగుంది", "bagundi", "సంతోషంగా", "खुश", "khush"],
    "sad": ["దుఃఖం", "dukhham", "బాధ", "badha", "నిరాశ", "nirasha", "दुखी", "dukhi", "उदास", "udaas"],
    "angry": ["కోపం", "kopam", "చిరాకు", "chiraku", "गुस्सा", "gussa", "क्रोध", "krodh"],
    "anxious": ["ఆందోళన", "andolana", "భయం", "bayam", "చింత", "chinta", "चिंता", "chinta", "घबराहट", "ghabrahat"],
    "stressed": ["ఒత్తిడి", "ottidi", "టెన్షన్", "tension", "तनाव", "tanaav", "दबाव", "dabaav"],
    "tired": ["అలసట", "alasata", "అలసిపోయాను", "थका", "thaka", "थकान", "thakaan"],
    "lonely": ["ఏకాంతం", "ekantam", "ఒంటరి", "ontari", "अकेला", "akela", "अकेलापन", "akelapan"],
    "excited": ["ఉత్సాహం", "utsaham", "ఉత్తేజం", "uttejam", "उत्साह", "utsaah", "उत्सुक", "utsuk"]
}

class LanguageLayer:
    """Enhanced language detection and translation layer"""

    def __init__(self):
        self.translator = Translator()
        self.translation_cache = {}
        self.supported_languages = LanguageConfig.SUPPORTED_LANGUAGES

    def detect_language(self, text: str) -> str:
        """
        Detect the language of input text
        Returns: language code ('te', 'hi', 'en')
        """
        try:
            # Clean text
            text_clean = text.strip()

            if not text_clean:
                return LanguageConfig.DEFAULT_LANGUAGE

            # Check for Telugu script
            if self._contains_telugu_script(text_clean):
                return 'te'

            # Check for Devanagari script (Hindi)
            if self._contains_devanagari_script(text_clean):
                return 'hi'

            # Use langdetect for romanized text
            try:
                detected = detect(text_clean)
                if detected in self.supported_languages:
                    return detected
                # Map common variants
                if detected in ['ta', 'kn', 'ml']:  # Other South Indian languages
                    return 'te'  # Default to Telugu for now
                return 'en'  # Default to English
            except LangDetectException:
                # Check for romanized Telugu/Hindi keywords
                if self._contains_romanized_telugu(text_clean):
                    return 'te'
                if self._contains_romanized_hindi(text_clean):
                    return 'hi'
                return 'en'

        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return LanguageConfig.DEFAULT_LANGUAGE

    def _contains_telugu_script(self, text: str) -> bool:
        """Check if text contains Telugu Unicode characters"""
        telugu_pattern = re.compile(r'[\u0C00-\u0C7F]')
        return bool(telugu_pattern.search(text))

    def _contains_devanagari_script(self, text: str) -> bool:
        """Check if text contains Devanagari (Hindi) Unicode characters"""
        devanagari_pattern = re.compile(r'[\u0900-\u097F]')
        return bool(devanagari_pattern.search(text))

    def _contains_romanized_telugu(self, text: str) -> bool:
        """Check for common romanized Telugu words"""
        text_lower = text.lower()
        telugu_keywords = ['namaskaram', 'ela unnaru', 'bagundi', 'manchiga',
                          'santosham', 'dukhham', 'kopam', 'charminar', 'hyderabad']
        return any(keyword in text_lower for keyword in telugu_keywords)

    def _contains_romanized_hindi(self, text: str) -> bool:
        """Check for common romanized Hindi words"""
        text_lower = text.lower()
        hindi_keywords = ['namaste', 'kaise ho', 'theek hoon', 'aap',
                         'khush', 'dukhi', 'gussa', 'ji', 'maa', 'papa']
        return any(keyword in text_lower for keyword in hindi_keywords)

    def translate_text(self, text: str, target_lang: str = 'en',
                      source_lang: str = None) -> str:
        """
        Translate text to target language
        Uses caching to avoid repeated API calls
        """
        try:
            # Create cache key
            cache_key = f"{source_lang or 'auto'}_{target_lang}_{text[:50]}"

            # Check cache
            if cache_key in self.translation_cache:
                return self.translation_cache[cache_key]

            # Translate
            if source_lang:
                translation = self.translator.translate(
                    text, src=source_lang, dest=target_lang
                )
            else:
                translation = self.translator.translate(text, dest=target_lang)

            result = translation.text

            # Cache result (with size limit)
            if len(self.translation_cache) < LanguageConfig.TRANSLATION_CACHE_SIZE:
                self.translation_cache[cache_key] = result

            return result

        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return text  # Return original if translation fails

    def get_cultural_context(self, language: str) -> Dict:
        """Get cultural context for a language"""
        if language == 'te':
            return TELUGU_CONTEXT
        elif language == 'hi':
            return HINDI_CONTEXT
        return {}

    def extract_cultural_references(self, text: str, language: str) -> List[str]:
        """Extract cultural references from text"""
        references = []
        text_lower = text.lower()

        context = self.get_cultural_context(language)

        # Check all cultural categories
        for category, items in context.items():
            for key in items.keys():
                if key.lower() in text_lower:
                    references.append({
                        'term': key,
                        'category': category,
                        'meaning': items[key]
                    })

        return references

    def detect_mood_multilingual(self, text: str, language: str) -> Tuple[str, float]:
        """
        Enhanced mood detection supporting Telugu and Hindi
        Returns: (mood, confidence)
        """
        try:
            text_lower = text.lower()
            mood_scores = {}

            # Check language-specific mood keywords
            if language in ['te', 'hi']:
                for mood, keywords in TELUGU_MOOD_KEYWORDS.items():
                    score = sum(1 for keyword in keywords if keyword in text_lower)
                    if score > 0:
                        mood_scores[mood] = score / len(keywords)

            # If we found mood keywords, return the highest scoring mood
            if mood_scores:
                top_mood = max(mood_scores.items(), key=lambda x: x[1])
                return top_mood[0], min(top_mood[1] + 0.5, 1.0)

            # Fall back to English translation and detection
            if language != 'en':
                try:
                    english_text = self.translate_text(text, target_lang='en',
                                                      source_lang=language)
                    # Use original mood detection on translated text
                    # (You would call your existing enhanced_mood_detection here)
                    return "neutral", 0.5
                except:
                    pass

            return "neutral", 0.5

        except Exception as e:
            logger.error(f"Multilingual mood detection failed: {e}")
            return "neutral", 0.5

    def extract_name_multilingual(self, text: str, language: str) -> Optional[str]:
        """Extract name from Telugu/Hindi/English text"""
        text_clean = text.lower().strip()

        patterns = []

        if language == 'te':
            patterns = [
                (r"నా పేరు ([^\s]+)", 1),
                (r"naa peru ([a-zA-Z]{2,20})", 1),
                (r"నేను ([^\s]+)", 1),
                (r"nenu ([a-zA-Z]{2,20})", 1),
                (r"నన్ను ([^\s]+) అని పిలవండి", 1),
                (r"nannu ([a-zA-Z]{2,20}) ani pilavandi", 1)
            ]
        elif language == 'hi':
            patterns = [
                (r"मेरा नाम ([^\s]+)", 1),
                (r"mera naam ([a-zA-Z]{2,20})", 1),
                (r"मैं ([^\s]+)", 1),
                (r"main ([a-zA-Z]{2,20})", 1),
                (r"मुझे ([^\s]+) कहते हैं", 1),
                (r"mujhe ([a-zA-Z]{2,20}) kehte hain", 1)
            ]
        else:  # English
            patterns = [
                (r"my name is ([a-zA-Z]{2,20})", 1),
                (r"i'm ([a-zA-Z]{2,20})", 1),
                (r"i am ([a-zA-Z]{2,20})", 1),
                (r"call me ([a-zA-Z]{2,20})", 1),
                (r"name's ([a-zA-Z]{2,20})", 1)
            ]

        # Excluded words (not names)
        excluded = {'feeling', 'good', 'bad', 'okay', 'fine', 'great', 'happy',
                   'sad', 'angry', 'tired', 'బాగున్నాను', 'బాగా', 'ठीक', 'अच्छा'}

        for pattern, group in patterns:
            match = re.search(pattern, text_clean)
            if match:
                name = match.group(group).strip()
                if len(name) >= 2 and name.lower() not in excluded:
                    return name.title()

        return None

    def create_language_aware_prompt(self, base_prompt: str, language: str,
                                    cultural_context: Dict = None) -> str:
        """
        Create a language-aware prompt for the LLM
        Includes cultural context and language instructions
        """
        lang_info = self.supported_languages.get(language, self.supported_languages['en'])

        language_instruction = f"""
LANGUAGE CONTEXT:
- User is communicating in {lang_info['native_name']} ({lang_info['name']})
- Respond in the same language naturally
- Use appropriate cultural references and respect markers
- Understand code-switching (mixing with English) is common and natural
"""

        cultural_instruction = ""
        if cultural_context and language in ['te', 'hi']:
            cultural_instruction = f"""
CULTURAL AWARENESS:
- User may reference festivals, family terms, and local customs
- Use respectful language appropriately (గారు/जी when needed)
- Understand family dynamics common in {lang_info['name']} culture
- Be aware of regional food, places, and traditions
"""

        enhanced_prompt = f"{language_instruction}\n{cultural_instruction}\n{base_prompt}"

        return enhanced_prompt

    def format_response_for_language(self, response: str, language: str) -> str:
        """
        Format response appropriately for the target language
        Ensures natural language flow and cultural appropriateness
        """
        try:
            # If response needs translation
            if language != 'en':
                # Check if response is in English (needs translation)
                if not self._contains_script_for_language(response, language):
                    response = self.translate_text(response, target_lang=language,
                                                  source_lang='en')

            # Add cultural touches based on language
            if language == 'te' and response:
                # Ensure Telugu responses feel natural
                # (You can add more Telugu-specific formatting here)
                pass
            elif language == 'hi' and response:
                # Ensure Hindi responses feel natural
                pass

            return response

        except Exception as e:
            logger.error(f"Response formatting failed: {e}")
            return response

    def _contains_script_for_language(self, text: str, language: str) -> bool:
        """Check if text contains the script for the specified language"""
        if language == 'te':
            return self._contains_telugu_script(text)
        elif language == 'hi':
            return self._contains_devanagari_script(text)
        return True  # Assume English is present