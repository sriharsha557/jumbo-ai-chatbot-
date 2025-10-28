"""
Jumbo Chatbot with Language Layer Integration - FIXED VERSION
"""

import re
import logging
import time
import random
import pickle
import os
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# LANGUAGE CONFIGURATION
# ============================================================================

class LanguageConfig:
    """Configuration for supported languages"""
    SUPPORTED_LANGUAGES = {
        'te': {
            'name': 'telugu',
            'native_name': 'తెలుగు',
            'voice_code': 'te-IN',
        },
        'hi': {
            'name': 'hindi',
            'native_name': 'हिंदी',
            'voice_code': 'hi-IN',
        },
        'en': {
            'name': 'english',
            'native_name': 'English',
            'voice_code': 'en-IN',
        }
    }
    DEFAULT_LANGUAGE = 'te'
    TRANSLATION_CACHE_SIZE = 1000

TELUGU_MOOD_KEYWORDS = {
    "happy": ["సంతోషం", "santosham", "ఆనందం", "anandam", "బాగు"],
    "sad": ["దుఃఖం", "dukhham", "బాధ", "badha"],
    "angry": ["కోపం", "kopam", "చిరాకు", "chiraku"],
    "anxious": ["ఆందోళన", "andolana", "భయం", "bayam"],
    "neutral": ["సరే", "సాధారణ"]
}

# ============================================================================
# LANGUAGE LAYER
# ============================================================================

class LanguageLayer:
    """Language detection and mood analysis"""

    def __init__(self):
        self.translation_cache = {}
        self.supported_languages = LanguageConfig.SUPPORTED_LANGUAGES

    def detect_language(self, text: str) -> str:
        """Detect language of input text"""
        try:
            text_clean = text.strip()
            if not text_clean:
                return LanguageConfig.DEFAULT_LANGUAGE

            if self._contains_telugu_script(text_clean):
                return 'te'
            if self._contains_devanagari_script(text_clean):
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
        """Check if text contains Hindi Unicode characters"""
        devanagari_pattern = re.compile(r'[\u0900-\u097F]')
        return bool(devanagari_pattern.search(text))

    def detect_mood_multilingual(self, text: str, language: str) -> Tuple[str, float]:
        """Detect mood from text"""
        try:
            text_lower = text.lower()
            mood_scores = {}

            for mood, keywords in TELUGU_MOOD_KEYWORDS.items():
                score = sum(1 for keyword in keywords if keyword.lower() in text_lower)
                if score > 0:
                    mood_scores[mood] = score / max(len(keywords), 1)

            if mood_scores:
                top_mood = max(mood_scores.items(), key=lambda x: x[1])
                return top_mood[0], min(top_mood[1] + 0.3, 1.0)

            return "neutral", 0.5

        except Exception as e:
            logger.error(f"Mood detection failed: {e}")
            return "neutral", 0.5

    def extract_name_multilingual(self, text: str, language: str) -> Optional[str]:
        """Extract name from text"""
        try:
            text_clean = text.lower().strip()
            patterns = []

            if language == 'te':
                patterns = [
                    (r"నా పేరు ([^\s\.]+)", 1),
                    (r"naa peru ([a-z]+)", 1),
                ]
            elif language == 'hi':
                patterns = [
                    (r"मेरा नाम ([^\s\.]+)", 1),
                    (r"mera naam ([a-z]+)", 1),
                ]
            else:
                patterns = [
                    (r"my name is ([a-z]+)", 1),
                    (r"i'm ([a-z]+)", 1),
                ]

            excluded = {'feeling', 'good', 'bad', 'fine', 'great'}

            for pattern, group in patterns:
                match = re.search(pattern, text_clean)
                if match:
                    name = match.group(group).strip()
                    if len(name) >= 2 and name.lower() not in excluded:
                        return name.title()

            return None
        except Exception as e:
            logger.error(f"Name extraction failed: {e}")
            return None

    def format_response_for_language(self, response: str, language: str) -> str:
        """Format response for target language"""
        return response


# ============================================================================
# TEXT EMBEDDING
# ============================================================================

def simple_text_embedding(text: str, embedding_dim: int = 384) -> np.ndarray:
    """Create simple text embedding"""
    import hashlib
    hash_obj = hashlib.md5(text.encode())
    hash_bytes = hash_obj.digest()

    embedding = np.zeros(embedding_dim)
    for i, byte_val in enumerate(hash_bytes):
        embedding[i % embedding_dim] += byte_val / 255.0

    return embedding


# ============================================================================
# ENHANCED JUMBO MEMORY
# ============================================================================

class EnhancedJumboMemory:
    """Memory system with language support"""

    def __init__(self, user_id: str = "default_user"):
        self.user_id = user_id
        self.embedding_dim = 384

        # Use /tmp for Render compatibility
        try:
            self.memory_dir = f"./user_memory_{user_id}"
            os.makedirs(self.memory_dir, exist_ok=True)
        except:
            self.memory_dir = f"/tmp/user_memory_{user_id}"
            os.makedirs(self.memory_dir, exist_ok=True)

        self.index = []
        self.metadata = []
        self.user_info = {}

        self._load_from_disk()

    def _load_from_disk(self):
        """Load memory from disk"""
        try:
            metadata_file = os.path.join(self.memory_dir, "metadata.pkl")
            if os.path.exists(metadata_file):
                with open(metadata_file, 'rb') as f:
                    self.metadata = pickle.load(f)

            user_info_file = os.path.join(self.memory_dir, "user_info.pkl")
            if os.path.exists(user_info_file):
                with open(user_info_file, 'rb') as f:
                    self.user_info = pickle.load(f)

            self.index = []
            for meta in self.metadata:
                text = f"User: {meta.get('user_message', '')}\nJumbo: {meta.get('jumbo_response', '')}"
                embedding = simple_text_embedding(text, self.embedding_dim)
                self.index.append(embedding)

        except Exception as e:
            logger.error(f"Failed to load memory: {e}")
            self.metadata = []
            self.user_info = {}

    def _save_to_disk(self):
        """Save memory to disk"""
        try:
            metadata_file = os.path.join(self.memory_dir, "metadata.pkl")
            with open(metadata_file, 'wb') as f:
                pickle.dump(self.metadata, f)

            user_info_file = os.path.join(self.memory_dir, "user_info.pkl")
            with open(user_info_file, 'wb') as f:
                pickle.dump(self.user_info, f)
        except Exception as e:
            logger.error(f"Failed to save memory: {e}")

    def _cleanup_old_memories(self, max_memories: int = 50):
        """Keep only recent memories"""
        if len(self.metadata) > max_memories:
            self.metadata.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            self.metadata = self.metadata[:max_memories]
            self.index = []
            for meta in self.metadata:
                text = f"User: {meta.get('user_message', '')}\nJumbo: {meta.get('jumbo_response', '')}"
                embedding = simple_text_embedding(text, self.embedding_dim)
                self.index.append(embedding)
            self._save_to_disk()

    def store_conversation(self, user_message: str, jumbo_response: str, mood: str,
                          confidence: float, user_name: str = None,
                          language: str = "te") -> bool:
        """Store conversation"""
        try:
            if not user_message or not jumbo_response:
                return False

            conversation_text = f"User: {user_message}\nJumbo: {jumbo_response}"
            embedding = simple_text_embedding(conversation_text, self.embedding_dim)

            metadata = {
                "timestamp": datetime.now().isoformat(),
                "mood": mood or "neutral",
                "confidence": max(0.0, min(1.0, confidence)),
                "user_message": user_message[:200],
                "jumbo_response": jumbo_response[:200],
                "language": language
            }
            if user_name:
                metadata["user_name"] = user_name[:50]

            self.index.append(embedding)
            self.metadata.append(metadata)
            self._save_to_disk()
            self._cleanup_old_memories()
            return True

        except Exception as e:
            logger.error(f"Failed to store conversation: {e}")
            return False

    def get_relevant_memories(self, query: str, limit: int = 3) -> List[Dict]:
        """Get relevant memories"""
        try:
            if not self.metadata:
                return []

            query_embedding = simple_text_embedding(query, self.embedding_dim)
            similarities = []

            for i, memory_embedding in enumerate(self.index):
                sim = cosine_similarity(
                    query_embedding.reshape(1, -1),
                    memory_embedding.reshape(1, -1)
                )[0][0]
                similarities.append((sim, i))

            similarities.sort(key=lambda x: x[0], reverse=True)
            relevant_indices = [idx for _, idx in similarities[:limit]]
            return [self.metadata[i] for i in relevant_indices]

        except Exception as e:
            logger.error(f"Failed to get memories: {e}")
            return []

    def store_user_info(self, key: str, value: str):
        """Store user info"""
        try:
            self.user_info[key] = {
                "value": value,
                "timestamp": datetime.now().isoformat()
            }
            self._save_to_disk()
        except Exception as e:
            logger.error(f"Failed to store user info: {e}")

    def get_user_name(self) -> Optional[str]:
        """Get user name"""
        try:
            name_info = self.user_info.get("name")
            if name_info and isinstance(name_info, dict):
                return name_info.get("value")
        except Exception as e:
            logger.error(f"Failed to get user name: {e}")
        return None

    def store_language_preference(self, language: str):
        """Store language preference"""
        try:
            if language in LanguageConfig.SUPPORTED_LANGUAGES:
                self.user_info["preferred_language"] = {
                    "value": language,
                    "timestamp": datetime.now().isoformat()
                }
                self._save_to_disk()
        except Exception as e:
            logger.error(f"Failed to store language preference: {e}")

    def get_language_preference(self) -> str:
        """Get language preference"""
        try:
            lang_info = self.user_info.get("preferred_language")
            if lang_info and isinstance(lang_info, dict):
                lang = lang_info.get("value")
                if lang in LanguageConfig.SUPPORTED_LANGUAGES:
                    return lang
        except Exception as e:
            logger.error(f"Failed to get language preference: {e}")
        return LanguageConfig.DEFAULT_LANGUAGE


# ============================================================================
# ENHANCED JUMBO CREW
# ============================================================================

class EnhancedJumboCrew:
    """Main chatbot class"""

    def __init__(self, user_id: str = "default_user"):
        self.user_id = user_id
        try:
            self.memory = EnhancedJumboMemory(user_id)
            self.language_layer = LanguageLayer()
            logger.info("Jumbo initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize: {e}")
            raise

    def respond(self, user_message: str) -> Tuple[str, Dict]:
        """Generate response"""
        response_metadata = {
            "timestamp": datetime.now().isoformat(),
            "processing_time": 0,
            "mood_detected": "neutral",
            "confidence": 0.5,
            "memories_used": 0,
            "success": False,
            "language_detected": "te"
        }
        start_time = time.time()

        try:
            # Detect language
            detected_language = self.language_layer.detect_language(user_message)
            response_metadata["language_detected"] = detected_language

            # Store language preference
            stored_lang = self.memory.get_language_preference()
            if stored_lang != detected_language:
                self.memory.store_language_preference(detected_language)

            # Extract name
            extracted_name = self.language_layer.extract_name_multilingual(
                user_message, detected_language
            )

            if extracted_name:
                current_name = self.memory.get_user_name()
                if not current_name or current_name != extracted_name:
                    self.memory.store_user_info("name", extracted_name)

            user_name = self.memory.get_user_name()

            # Detect mood
            detected_mood, confidence = self.language_layer.detect_mood_multilingual(
                user_message, detected_language
            )
            response_metadata.update({
                "mood_detected": detected_mood,
                "confidence": confidence
            })

            # Get memories
            relevant_memories = self.memory.get_relevant_memories(user_message, limit=2)
            response_metadata["memories_used"] = len(relevant_memories)

            # Generate response
            response = self._get_fallback_response(
                detected_mood, user_name, detected_language
            )

            # Store conversation
            self.memory.store_conversation(
                user_message, response, detected_mood, confidence,
                user_name, detected_language
            )

            response_metadata.update({
                "processing_time": time.time() - start_time,
                "success": True
            })
            return response, response_metadata

        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            response_metadata["error"] = str(e)
            response_metadata["processing_time"] = time.time() - start_time
            return self._get_fallback_response("neutral", None, "en"), response_metadata

    def _get_fallback_response(self, mood: str, user_name: Optional[str],
                              language: str = "te") -> str:
        """Generate response based on mood"""
        name_part = f", {user_name}" if user_name else ""

        telugu_responses = {
            "happy": [
                f"ఆ విషయం చాలా బాగుంది{name_part}! మీరు సంతోషంగా ఉన్నారు. ఇది మీకు ఎంత సంతోషం ఇస్తుంది?",
                f"నిజంగా! మీ సంతోషం నాకు చాలా ఆనందం ఇస్తుంది.",
            ],
            "sad": [
                f"మీరు కష్టపడుతున్నారని అర్థమైంది{name_part}. మీ మనస్సులో ఏమి ఉంది?",
                f"ఆ విషయం చాలా బాధకరం. నేను ఇక్కడ ఉన్నాను.",
            ],
            "angry": [
                f"నీ కోపం నాకు అర్థమైంది{name_part}. ఏమైంది?",
                f"నిరాశ ఎవరికీ ఇష్టం లేదు. ఈ రోషం ఎక్కడ నుండి వచ్చింది?",
            ],
            "anxious": [
                f"ఆందోళన చేయవద్దు{name_part}. నేను ఇక్కడ ఉన్నాను.",
                f"భయపడకండి. ఏమీ చెప్పండి.",
            ],
            "neutral": [
                f"నేను నీ మాటలను విన్నాను{name_part}. ఇంకా చెప్పండి.",
                f"సరే, నీకు ఏమీ చెప్పాలనుకుంటే చెప్పు.",
            ]
        }

        hindi_responses = {
            "happy": [
                f"वह बहुत अच्छा है{name_part}! आप खुश हैं। क्या बताइए?",
                f"आपकी खुशी मुझे भी खुश कर रही है।",
            ],
            "sad": [
                f"आपकी बातों को मैं समझता हूँ{name_part}। क्या हुआ?",
                f"यह बहुत दुःख की बात है। मैं यहाँ हूँ।",
            ],
            "angry": [
                f"तुम्हारा गुस्सा मुझे समझ आता है{name_part}। क्या हुआ?",
                f"गुस्सा किसी को पसंद नहीं है। बताइए क्या हुआ।",
            ],
            "anxious": [
                f"चिंता मत करो{name_part}। मैं यहाँ हूँ।",
                f"डरो मत। कुछ कहो।",
            ],
            "neutral": [
                f"मैं सुन रहा हूँ{name_part}। क्या कहना चाहते हो?",
                f"ठीक है। कुछ कहो।",
            ]
        }

        english_responses = {
            "happy": [f"That's wonderful{name_part}! You sound really happy. What's making you so joyful?"],
            "sad": [f"I understand you're going through something{name_part}. What's on your mind?"],
            "angry": [f"I sense some frustration{name_part}. What happened?"],
            "anxious": [f"Take a breath{name_part}. I'm here to listen. What's worrying you?"],
            "neutral": [f"I'm listening{name_part}. What would you like to talk about?"]
        }

        if language == 'te':
            responses = telugu_responses.get(mood, telugu_responses['neutral'])
        elif language == 'hi':
            responses = hindi_responses.get(mood, hindi_responses['neutral'])
        else:
            responses = english_responses.get(mood, english_responses['neutral'])

        return random.choice(responses) if responses else f"Hello{name_part}!"


# ============================================================================
# TESTING
# ============================================================================

def test_chatbot():
    """Test the chatbot"""
    print("\nTesting Jumbo Chatbot...\n")
    
    try:
        crew = EnhancedJumboCrew("test_user")
        
        test_messages = [
            "నా పేరు రాజు. నేను చాలా సంతోషంగా ఉన్నాను",
            "मैं बहुत खुश हूँ",
            "I'm feeling a bit sad today",
        ]
        
        for msg in test_messages:
            print(f"You: {msg}")
            response, metadata = crew.respond(msg)
            print(f"Jumbo: {response}")
            print(f"Mood: {metadata['mood_detected']}, Language: {metadata['language_detected']}\n")
        
        print("Test completed successfully!")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_chatbot()