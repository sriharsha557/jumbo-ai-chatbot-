"""
Advanced Language Layer Features
- Offline translation for common phrases
- Better code-switching detection
- Regional variations (Coastal Andhra vs Telangana)
- Voice integration hooks
"""

import json
import pickle
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Common phrases cache for offline operation
TELUGU_COMMON_PHRASES = {
    # Greetings
    "hello": "హలో",
    "good morning": "శుభోదయం",
    "good night": "శుభరాత్రి",
    "how are you": "ఎలా ఉన్నారు",
    "i am fine": "నేను బాగున్నాను",
    "thank you": "ధన్యవాదాలు",
    "welcome": "స్వాగతం",
    
    # Emotions
    "i am happy": "నేను సంతోషంగా ఉన్నాను",
    "i am sad": "నేను బాధగా ఉన్నాను",
    "i am angry": "నేను కోపంగా ఉన్నాను",
    "i am tired": "నేను అలసిపోయాను",
    "i am worried": "నేను ఆందోళన చెందుతున్నాను",
    "i am excited": "నేను ఉత్సాహంగా ఉన్నాను",
    "i feel stressed": "నాకు ఒత్తిడిగా ఉంది",
    "i feel lonely": "నాకు ఒంటరిగా అనిపిస్తోంది",
    
    # Common questions
    "what is your name": "మీ పేరు ఏమిటి",
    "where are you from": "మీరు ఎక్కడి వారు",
    "what are you doing": "మీరు ఏం చేస్తున్నారు",
    "can you help me": "మీరు నాకు సహాయం చేయగలరా",
    "i need help": "నాకు సహాయం కావాలి",
    
    # Family
    "my mother": "నా అమ్మ",
    "my father": "నా నాన్న",
    "my brother": "నా అన్న / నా తమ్ముడు",
    "my sister": "నా అక్క / నా చెల్లి",
    "my family": "నా కుటుంబం",
    
    # Common responses
    "yes": "అవును",
    "no": "కాదు / లేదు",
    "okay": "సరే",
    "maybe": "బహుశా",
    "i understand": "నాకు అర్థమైంది",
    "i don't understand": "నాకు అర్థం కాలేదు"
}

HINDI_COMMON_PHRASES = {
    # Greetings
    "hello": "नमस्ते",
    "good morning": "सुप्रभात",
    "good night": "शुभ रात्रि",
    "how are you": "आप कैसे हैं",
    "i am fine": "मैं ठीक हूं",
    "thank you": "धन्यवाद",
    "welcome": "स्वागत है",
    
    # Emotions
    "i am happy": "मैं खुश हूं",
    "i am sad": "मैं उदास हूं",
    "i am angry": "मैं गुस्से में हूं",
    "i am tired": "मैं थका हुआ हूं",
    "i am worried": "मैं चिंतित हूं",
    "i am excited": "मैं उत्साहित हूं",
    "i feel stressed": "मुझे तनाव है",
    "i feel lonely": "मुझे अकेलापन महसूस हो रहा है",
    
    # Common questions
    "what is your name": "आपका नाम क्या है",
    "where are you from": "आप कहां से हैं",
    "what are you doing": "आप क्या कर रहे हैं",
    "can you help me": "क्या आप मेरी मदद कर सकते हैं",
    "i need help": "मुझे मदद चाहिए",
    
    # Family
    "my mother": "मेरी माँ",
    "my father": "मेरे पिता / मेरे पापा",
    "my brother": "मेरा भाई",
    "my sister": "मेरी बहन",
    "my family": "मेरा परिवार",
    
    # Common responses
    "yes": "हां / जी",
    "no": "नहीं",
    "okay": "ठीक है",
    "maybe": "शायद",
    "i understand": "मुझे समझ आया",
    "i don't understand": "मुझे समझ नहीं आया"
}

# Regional Telugu variations
TELUGU_REGIONAL_VARIATIONS = {
    "coastal_andhra": {
        "how are you": "ఎలా ఉన్నావు రా",
        "what happened": "ఏమైంది రా",
        "come here": "ఇక్కడికి రా",
        "dialect_markers": ["రా", "మావ", "రే"]
    },
    "telangana": {
        "how are you": "ఎలా ఉన్నావ్ రా",
        "what happened": "ఏమైందీ",
        "come here": "ఇక్కడికొచ్చు",
        "dialect_markers": ["ఉన్నావ్", "చేస్తావ్", "ఏమైందీ"]
    },
    "rayalaseema": {
        "dialect_markers": ["అన్నయ్య", "మావయ్య", "చెప్పరా"]
    }
}

class CodeSwitchingDetector:
    """Detect and handle Telugu-English or Hindi-English code-switching"""
    
    def __init__(self):
        self.english_words = set([
            'office', 'work', 'boss', 'meeting', 'project', 'deadline',
            'home', 'house', 'car', 'bike', 'phone', 'computer',
            'food', 'restaurant', 'movie', 'cinema', 'party',
            'stress', 'tension', 'problem', 'issue', 'happy', 'sad',
            'okay', 'fine', 'good', 'bad', 'nice', 'sorry'
        ])
    
    def detect_code_switching(self, text: str, primary_language: str) -> Dict:
        """
        Detect code-switching patterns in text
        Returns dict with language breakdown and switching points
        """
        words = text.lower().split()
        english_word_count = sum(1 for word in words if word in self.english_words)
        
        # Check for script mixing
        has_telugu = bool(__import__('re').search(r'[\u0C00-\u0C7F]', text))
        has_devanagari = bool(__import__('re').search(r'[\u0900-\u097F]', text))
        has_english = bool(__import__('re').search(r'[a-zA-Z]', text))
        
        switching_detected = (
            (has_telugu and has_english) or 
            (has_devanagari and has_english) or
            english_word_count > 0
        )
        
        return {
            'code_switching_detected': switching_detected,
            'primary_language': primary_language,
            'has_telugu_script': has_telugu,
            'has_devanagari_script': has_devanagari,
            'has_english_script': has_english,
            'english_word_ratio': english_word_count / len(words) if words else 0,
            'mixed_ratio': english_word_count / len(words) if words else 0
        }
    
    def normalize_code_switched_text(self, text: str, target_language: str) -> str:
        """
        Normalize code-switched text for better processing
        Keeps English words but ensures consistent script
        """
        # This is a placeholder - actual implementation would be more sophisticated
        return text


class OfflineTranslator:
    """Handle common phrase translations without API calls"""
    
    def __init__(self, cache_dir: str = "./translation_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        self.telugu_phrases = TELUGU_COMMON_PHRASES
        self.hindi_phrases = HINDI_COMMON_PHRASES
        
        # Load custom cache if exists
        self.custom_cache = self._load_custom_cache()
    
    def _load_custom_cache(self) -> Dict:
        """Load user-specific translation cache"""
        cache_file = self.cache_dir / "custom_translations.pkl"
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                logger.warning(f"Could not load custom cache: {e}")
        return {}
    
    def _save_custom_cache(self):
        """Save custom translations for offline use"""
        cache_file = self.cache_dir / "custom_translations.pkl"
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(self.custom_cache, f)
        except Exception as e:
            logger.error(f"Could not save custom cache: {e}")
    
    def translate_offline(self, text: str, target_lang: str) -> Optional[str]:
        """
        Try to translate using cached phrases
        Returns None if not in cache
        """
        text_lower = text.lower().strip()
        
        # Check common phrases
        if target_lang == 'te' and text_lower in self.telugu_phrases:
            return self.telugu_phrases[text_lower]
        elif target_lang == 'hi' and text_lower in self.hindi_phrases:
            return self.hindi_phrases[text_lower]
        
        # Check custom cache
        cache_key = f"{text_lower}_{target_lang}"
        if cache_key in self.custom_cache:
            return self.custom_cache[cache_key]
        
        return None
    
    def add_to_cache(self, source: str, target: str, target_lang: str):
        """Add a translation to custom cache"""
        cache_key = f"{source.lower().strip()}_{target_lang}"
        self.custom_cache[cache_key] = target
        self._save_custom_cache()


class RegionalDialectHandler:
    """Handle Telugu regional variations"""
    
    def __init__(self):
        self.variations = TELUGU_REGIONAL_VARIATIONS
    
    def detect_region(self, text: str) -> Optional[str]:
        """
        Detect which Telugu region the text is from
        Returns: 'coastal_andhra', 'telangana', 'rayalaseema', or None
        """
        text_lower = text.lower()
        
        region_scores = {}
        for region, data in self.variations.items():
            markers = data.get('dialect_markers', [])
            score = sum(1 for marker in markers if marker in text_lower)
            if score > 0:
                region_scores[region] = score
        
        if region_scores:
            return max(region_scores.items(), key=lambda x: x[1])[0]
        return None
    
    def adapt_response_to_region(self, response: str, region: Optional[str]) -> str:
        """
        Adapt response to match regional dialect
        This is a placeholder - would need more sophisticated implementation
        """
        if not region:
            return response
        
        # You could add region-specific vocabulary substitutions here
        return response


class VoiceIntegrationHelper:
    """Helper class for voice integration with regional languages"""
    
    VOICE_CONFIGS = {
        'te': {
            'standard': 'te-IN-Wavenet-A',
            'female': 'te-IN-Wavenet-B',
            'male': 'te-IN-Standard-A'
        },
        'hi': {
            'standard': 'hi-IN-Wavenet-A',
            'female': 'hi-IN-Wavenet-B',
            'male': 'hi-IN-Wavenet-C',
            'enhanced': 'hi-IN-Neural2-A'
        },
        'en': {
            'indian_female': 'en-IN-Wavenet-A',
            'indian_male': 'en-IN-Wavenet-B',
            'indian_enhanced': 'en-IN-Neural2-A'
        }
    }
    
    @staticmethod
    def get_voice_config(language: str, gender: str = 'standard') -> str:
        """Get Google Cloud TTS voice configuration"""
        return VoiceIntegrationHelper.VOICE_CONFIGS.get(language, {}).get(gender)
    
    @staticmethod
    def prepare_text_for_speech(text: str, language: str) -> str:
        """
        Prepare text for better speech synthesis
        - Add pauses
        - Handle abbreviations
        - Fix pronunciation hints
        """
        # Add SSML breaks for natural speech
        import re
        
        # Add pause after sentences
        text = re.sub(r'([.!?])\s+', r'\1<break time="500ms"/> ', text)
        
        # Add pause after commas
        text = re.sub(r',\s+', r',<break time="300ms"/> ', text)
        
        return text


class EnhancedLanguageLayer:
    """
    Enhanced language layer with offline capability and advanced features
    """
    
    def __init__(self, cache_dir: str = "./translation_cache"):
        # Import the original LanguageLayer
        from language_layer import LanguageLayer
        
        self.base_layer = LanguageLayer()
        self.offline_translator = OfflineTranslator(cache_dir)
        self.code_switch_detector = CodeSwitchingDetector()
        self.dialect_handler = RegionalDialectHandler()
        self.voice_helper = VoiceIntegrationHelper()
    
    def translate_with_fallback(self, text: str, target_lang: str, 
                               source_lang: str = None) -> str:
        """
        Translate with offline fallback
        Tries: 1) Offline cache -> 2) Online API -> 3) Returns original
        """
        # Try offline first
        offline_result = self.offline_translator.translate_offline(text, target_lang)
        if offline_result:
            logger.info("Using offline translation")
            return offline_result
        
        # Try online API
        try:
            online_result = self.base_layer.translate_text(text, target_lang, source_lang)
            # Cache the result for future offline use
            self.offline_translator.add_to_cache(text, online_result, target_lang)
            return online_result
        except Exception as e:
            logger.error(f"Online translation failed: {e}")
            return text  # Return original if all fails
    
    def process_user_input(self, text: str) -> Dict:
        """
        Comprehensive processing of user input
        Returns detailed analysis including language, mood, code-switching, etc.
        """
        # Detect primary language
        detected_lang = self.base_layer.detect_language(text)
        
        # Check for code-switching
        code_switch_info = self.code_switch_detector.detect_code_switching(
            text, detected_lang
        )
        
        # Detect regional dialect (for Telugu)
        region = None
        if detected_lang == 'te':
            region = self.dialect_handler.detect_region(text)
        
        # Extract cultural references
        cultural_refs = self.base_layer.extract_cultural_references(text, detected_lang)
        
        # Detect mood
        mood, confidence = self.base_layer.detect_mood_multilingual(text, detected_lang)
        
        # Extract name
        name = self.base_layer.extract_name_multilingual(text, detected_lang)
        
        return {
            'language': detected_lang,
            'region': region,
            'code_switching': code_switch_info,
            'cultural_references': cultural_refs,
            'mood': mood,
            'mood_confidence': confidence,
            'name_detected': name,
            'text_length': len(text),
            'word_count': len(text.split())
        }
    
    def generate_response_prompt(self, user_input: str, analysis: Dict, 
                                user_name: Optional[str], 
                                memory_context: str) -> str:
        """
        Generate enhanced prompt for LLM with all contextual information
        """
        lang = analysis['language']
        lang_name = self.base_layer.supported_languages[lang]['native_name']
        
        # Build code-switching instruction
        code_switch_note = ""
        if analysis['code_switching']['code_switching_detected']:
            code_switch_note = f"""
NOTE: User is code-switching between {lang_name} and English (mixed: {analysis['code_switching']['english_word_ratio']:.0%}).
This is natural - you should also code-switch in your response when appropriate.
"""
        
        # Build regional dialect note
        dialect_note = ""
        if analysis.get('region'):
            dialect_note = f"""
REGIONAL DIALECT: User is from {analysis['region']} region.
Be aware of regional expressions and vocabulary preferences.
"""
        
        # Build cultural context
        cultural_note = ""
        if analysis.get('cultural_references'):
            refs = ", ".join([r['term'] for r in analysis['cultural_references'][:3]])
            cultural_note = f"""
CULTURAL CONTEXT: User mentioned: {refs}
Show awareness of these cultural elements in your response.
"""
        
        prompt = f"""You are Jumbo, a caring elephant companion speaking in {lang_name}.

USER INPUT ANALYSIS:
- Language: {lang_name} ({lang})
- Mood: {analysis['mood']} (confidence: {analysis['mood_confidence']:.2f})
- User name: {user_name or 'Unknown'}
{code_switch_note}{dialect_note}{cultural_note}

CONVERSATION HISTORY:
{memory_context}

USER MESSAGE: "{user_input}"

YOUR RESPONSE MUST:
1. Be entirely in {lang_name} (code-switching with English is okay if user does it)
2. Use "you" language to reflect user's feelings
3. Address specific content they shared
4. Show cultural awareness
5. Match their emotional tone
6. Be warm and conversational (2-3 sentences)
7. End with a caring question
8. Use their name ({user_name}) naturally if known

Respond as Jumbo:"""
        
        return prompt
    
    def prepare_for_voice_output(self, text: str, language: str) -> Dict:
        """
        Prepare response for voice synthesis
        Returns SSML-enhanced text and voice configuration
        """
        # Prepare text with pauses
        enhanced_text = self.voice_helper.prepare_text_for_speech(text, language)
        
        # Get voice configuration
        voice_config = self.voice_helper.get_voice_config(language)
        
        return {
            'text': text,
            'ssml_text': enhanced_text,
            'voice_name': voice_config,
            'language_code': language
        }


# Utility functions for easy integration

def quick_translate(text: str, to_language: str) -> str:
    """Quick translation function"""
    layer = EnhancedLanguageLayer()
    return layer.translate_with_fallback(text, to_language)


def analyze_message(text: str) -> Dict:
    """Quickly analyze a message"""
    layer = EnhancedLanguageLayer()
    return layer.process_user_input(text)


def test_enhanced_features():
    """Test enhanced language layer features"""
    layer = EnhancedLanguageLayer()
    
    print("🧪 Testing Enhanced Language Layer\n")
    
    # Test 1: Code-switching detection
    print("1️⃣ Code-switching Detection:")
    mixed_text = "నేను office నుండి home వచ్చాను. చాలా tired గా ఉంది"
    analysis = layer.process_user_input(mixed_text)
    print(f"   Input: {mixed_text}")
    print(f"   Language: {analysis['language']}")
    print(f"   Code-switching: {analysis['code_switching']['code_switching_detected']}")
    print(f"   English ratio: {analysis['code_switching']['english_word_ratio']:.0%}\n")
    
    # Test 2: Regional dialect detection
    print("2️⃣ Regional Dialect Detection:")
    telangana_text = "ఎలా ఉన్నావ్ రా"
    analysis = layer.process_user_input(telangana_text)
    print(f"   Input: {telangana_text}")
    print(f"   Region: {analysis.get('region', 'Not detected')}\n")
    
    # Test 3: Offline translation
    print("3️⃣ Offline Translation:")
    result = layer.translate_with_fallback("hello", "te")
    print(f"   'hello' -> Telugu: {result}")
    result = layer.translate_with_fallback("thank you", "hi")
    print(f"   'thank you' -> Hindi: {result}\n")
    
    # Test 4: Comprehensive analysis
    print("4️⃣ Comprehensive Analysis:")
    complex_text = "నా పేరు రాజు. నేను చాలా stressed గా ఉన్నాను office work తో. Tomorrow ఉగాది festival ఉంది కానీ enjoy చేయలేను"
    analysis = layer.process_user_input(complex_text)
    print(f"   Input: {complex_text}")
    print(f"   Language: {analysis['language']}")
    print(f"   Name detected: {analysis['name_detected']}")
    print(f"   Mood: {analysis['mood']} ({analysis['mood_confidence']:.2f})")
    print(f"   Code-switching: {analysis['code_switching']['code_switching_detected']}")
    print(f"   Cultural refs: {[r['term'] for r in analysis['cultural_references']]}\n")
    
    # Test 5: Voice preparation
    print("5️⃣ Voice Output Preparation:")
    response_text = "మీరు చాలా stressed గా ఉన్నట్లు అనిపిస్తోంది. ఉగాది సందర్భంగా కొంచెం విశ్రాంతి తీసుకోండి. ఏం చేస్తే మీకు మంచి అనిపిస్తుంది?"
    voice_ready = layer.prepare_for_voice_output(response_text, 'te')
    print(f"   Original: {voice_ready['text'][:50]}...")
    print(f"   Voice: {voice_ready['voice_name']}")
    print(f"   SSML enhanced: {len(voice_ready['ssml_text']) > len(voice_ready['text'])}")
    
    print("\n✅ All enhanced features tested!")


if __name__ == "__main__":
    test_enhanced_features()