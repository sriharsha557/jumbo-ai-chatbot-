"""
Enhanced Emotion Detection System
Lightweight, keyword-based emotion analysis optimized for efficiency
"""

import re
import logging
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

class EmotionIntensity(Enum):
    """Emotion intensity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

@dataclass
class EmotionResult:
    """Result of emotion detection"""
    primary_emotion: str
    confidence: float
    intensity: EmotionIntensity
    detected_emotions: Dict[str, float] = field(default_factory=dict)
    emotional_indicators: List[str] = field(default_factory=list)
    context_clues: List[str] = field(default_factory=list)

class EnhancedEmotionDetector:
    """
    Lightweight emotion detection using keyword patterns and contextual analysis
    """
    
    def __init__(self):
        self.emotion_keywords = self._load_emotion_keywords()
        self.intensity_modifiers = self._load_intensity_modifiers()
        self.negation_words = self._load_negation_words()
        self.context_patterns = self._load_context_patterns()
        self.emoji_emotions = self._load_emoji_emotions()
        
        # Performance tracking
        self.detection_stats = {
            'total_detections': 0,
            'high_confidence_detections': 0,
            'emotion_distribution': {}
        }
        
        logger.info("EnhancedEmotionDetector initialized with keyword-based analysis")
    
    def _load_emotion_keywords(self) -> Dict[str, Dict[str, List[str]]]:
        """Load emotion keywords organized by category and intensity"""
        return {
            'happy': {
                'high': ['ecstatic', 'thrilled', 'overjoyed', 'elated', 'euphoric', 'blissful'],
                'medium': ['happy', 'joyful', 'cheerful', 'pleased', 'delighted', 'glad', 'excited'],
                'low': ['content', 'satisfied', 'okay', 'fine', 'good', 'alright', 'nice']
            },
            'sad': {
                'high': ['devastated', 'heartbroken', 'crushed', 'shattered', 'despairing', 'anguished'],
                'medium': ['sad', 'depressed', 'miserable', 'unhappy', 'sorrowful', 'melancholy'],
                'low': ['down', 'blue', 'low', 'disappointed', 'bummed', 'upset']
            },
            'angry': {
                'high': ['furious', 'enraged', 'livid', 'irate', 'seething', 'incensed'],
                'medium': ['angry', 'mad', 'pissed', 'irritated', 'annoyed', 'frustrated'],
                'low': ['bothered', 'irked', 'miffed', 'agitated', 'displeased', 'cross']
            },
            'anxious': {
                'high': ['panicked', 'terrified', 'petrified', 'horrified', 'paralyzed'],
                'medium': ['anxious', 'worried', 'nervous', 'stressed', 'tense', 'uneasy'],
                'low': ['concerned', 'apprehensive', 'uncertain', 'restless', 'edgy']
            },
            'confused': {
                'high': ['bewildered', 'perplexed', 'baffled', 'mystified', 'stumped'],
                'medium': ['confused', 'puzzled', 'uncertain', 'unclear', 'lost'],
                'low': ['unsure', 'questioning', 'wondering', 'doubtful', 'hesitant']
            },
            'frustrated': {
                'high': ['exasperated', 'infuriated', 'maddened', 'driven crazy'],
                'medium': ['frustrated', 'fed up', 'annoyed', 'irritated', 'aggravated'],
                'low': ['bothered', 'impatient', 'restless', 'dissatisfied']
            },
            'tired': {
                'high': ['exhausted', 'drained', 'depleted', 'wiped out', 'burnt out'],
                'medium': ['tired', 'weary', 'fatigued', 'worn out', 'sleepy'],
                'low': ['drowsy', 'sluggish', 'lethargic', 'low energy']
            },
            'excited': {
                'high': ['thrilled', 'ecstatic', 'pumped', 'stoked', 'hyped'],
                'medium': ['excited', 'enthusiastic', 'eager', 'animated', 'energetic'],
                'low': ['interested', 'curious', 'engaged', 'motivated']
            },
            'worried': {
                'high': ['terrified', 'panicked', 'alarmed', 'distressed'],
                'medium': ['worried', 'concerned', 'troubled', 'bothered', 'anxious'],
                'low': ['uneasy', 'apprehensive', 'cautious', 'wary']
            },
            'lonely': {
                'high': ['isolated', 'abandoned', 'forsaken', 'desolate'],
                'medium': ['lonely', 'alone', 'solitary', 'disconnected'],
                'low': ['by myself', 'on my own', 'single', 'independent']
            }
        }
    
    def _load_intensity_modifiers(self) -> Dict[str, float]:
        """Load words that modify emotion intensity"""
        return {
            # Amplifiers
            'extremely': 1.5, 'incredibly': 1.4, 'absolutely': 1.3, 'totally': 1.3,
            'completely': 1.3, 'utterly': 1.4, 'really': 1.2, 'very': 1.2,
            'quite': 1.1, 'pretty': 1.1, 'so': 1.2, 'super': 1.3,
            'deeply': 1.3, 'intensely': 1.4, 'severely': 1.4,
            
            # Diminishers
            'slightly': 0.7, 'somewhat': 0.8, 'a bit': 0.7, 'a little': 0.7,
            'kind of': 0.8, 'sort of': 0.8, 'rather': 0.9, 'fairly': 0.9,
            'mildly': 0.7, 'barely': 0.6, 'hardly': 0.6
        }
    
    def _load_negation_words(self) -> Set[str]:
        """Load negation words that flip emotion meaning"""
        return {
            'not', 'no', 'never', 'nothing', 'nobody', 'nowhere', 'neither',
            'nor', 'none', 'without', 'lack', 'lacking', 'absent', 'missing',
            'dont', "don't", 'wont', "won't", 'cant', "can't", 'isnt', "isn't",
            'arent', "aren't", 'wasnt', "wasn't", 'werent', "weren't"
        }
    
    def _load_context_patterns(self) -> Dict[str, List[str]]:
        """Load contextual patterns that indicate emotions"""
        return {
            'stress_indicators': [
                'too much', 'overwhelming', 'can\'t handle', 'breaking point',
                'under pressure', 'stressed out', 'burned out', 'at my limit'
            ],
            'support_seeking': [
                'need help', 'don\'t know what to do', 'lost', 'confused',
                'advice', 'what should i', 'help me', 'support'
            ],
            'positive_events': [
                'got promoted', 'new job', 'celebration', 'achievement',
                'success', 'won', 'accomplished', 'proud of'
            ],
            'negative_events': [
                'lost job', 'breakup', 'death', 'illness', 'accident',
                'failed', 'rejected', 'disappointed', 'let down'
            ],
            'relationship_issues': [
                'fight with', 'argument', 'broke up', 'relationship problems',
                'not talking', 'distant', 'conflict', 'disagreement'
            ],
            'work_stress': [
                'work stress', 'job pressure', 'deadline', 'boss',
                'overtime', 'workload', 'meeting', 'presentation'
            ]
        }
    
    def _load_emoji_emotions(self) -> Dict[str, Tuple[str, float]]:
        """Load emoji to emotion mappings"""
        return {
            # Happy emotions
            '😊': ('happy', 0.8), '😄': ('happy', 0.9), '😃': ('happy', 0.8),
            '😁': ('happy', 0.8), '🙂': ('happy', 0.6), '😌': ('content', 0.7),
            '😍': ('excited', 0.9), '🥰': ('happy', 0.9), '😘': ('happy', 0.8),
            
            # Sad emotions
            '😢': ('sad', 0.8), '😭': ('sad', 0.9), '😞': ('sad', 0.7),
            '😔': ('sad', 0.7), '☹️': ('sad', 0.6), '🙁': ('sad', 0.6),
            '💔': ('heartbroken', 0.9), '😿': ('sad', 0.8),
            
            # Angry emotions
            '😠': ('angry', 0.8), '😡': ('angry', 0.9), '🤬': ('furious', 0.9),
            '😤': ('frustrated', 0.7), '💢': ('angry', 0.8),
            
            # Anxious/worried emotions
            '😰': ('anxious', 0.8), '😨': ('worried', 0.8), '😱': ('panicked', 0.9),
            '😟': ('worried', 0.7), '😧': ('anxious', 0.7), '🤯': ('overwhelmed', 0.8),
            
            # Confused emotions
            '🤔': ('confused', 0.6), '😕': ('confused', 0.5), '🤷': ('confused', 0.7),
            
            # Tired emotions
            '😴': ('tired', 0.8), '🥱': ('tired', 0.7), '😪': ('tired', 0.8),
            
            # Excited emotions
            '🤩': ('excited', 0.9), '🎉': ('excited', 0.8), '🥳': ('excited', 0.9),
            '✨': ('excited', 0.6), '🔥': ('excited', 0.7)
        }
    
    def detect_emotion(self, text: str, context: Dict = None) -> EmotionResult:
        """
        Detect emotions in text with confidence scoring
        """
        try:
            self.detection_stats['total_detections'] += 1
            
            # Preprocess text
            processed_text = self._preprocess_text(text)
            
            # Extract emojis first
            emoji_emotions = self._detect_emoji_emotions(text)
            
            # Detect keyword-based emotions
            keyword_emotions = self._detect_keyword_emotions(processed_text)
            
            # Detect contextual emotions
            context_emotions = self._detect_contextual_emotions(processed_text)
            
            # Combine all emotion scores
            combined_emotions = self._combine_emotion_scores(
                emoji_emotions, keyword_emotions, context_emotions
            )
            
            # Apply intensity modifiers
            modified_emotions = self._apply_intensity_modifiers(
                combined_emotions, processed_text
            )
            
            # Handle negations
            final_emotions = self._handle_negations(modified_emotions, processed_text)
            
            # Determine primary emotion and confidence
            result = self._create_emotion_result(final_emotions, text)
            
            # Update statistics
            self._update_statistics(result)
            
            logger.debug(f"Detected emotion: {result.primary_emotion} "
                        f"(confidence: {result.confidence:.2f})")
            
            return result
            
        except Exception as e:
            logger.error(f"Error detecting emotion: {e}")
            return self._create_default_result()
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for emotion detection"""
        # Convert to lowercase
        processed = text.lower()
        
        # Remove extra whitespace
        processed = re.sub(r'\s+', ' ', processed).strip()
        
        # Handle contractions
        contractions = {
            "i'm": "i am", "you're": "you are", "it's": "it is",
            "we're": "we are", "they're": "they are", "i've": "i have",
            "you've": "you have", "we've": "we have", "they've": "they have",
            "i'll": "i will", "you'll": "you will", "it'll": "it will",
            "we'll": "we will", "they'll": "they will", "won't": "will not",
            "can't": "cannot", "don't": "do not", "doesn't": "does not",
            "didn't": "did not", "shouldn't": "should not", "wouldn't": "would not",
            "couldn't": "could not", "isn't": "is not", "aren't": "are not",
            "wasn't": "was not", "weren't": "were not", "haven't": "have not",
            "hasn't": "has not", "hadn't": "had not"
        }
        
        for contraction, expansion in contractions.items():
            processed = processed.replace(contraction, expansion)
        
        return processed
    
    def _detect_emoji_emotions(self, text: str) -> Dict[str, float]:
        """Detect emotions from emojis"""
        emotions = {}
        
        for emoji, (emotion, confidence) in self.emoji_emotions.items():
            if emoji in text:
                emotions[emotion] = emotions.get(emotion, 0) + confidence
        
        return emotions
    
    def _detect_keyword_emotions(self, text: str) -> Dict[str, float]:
        """Detect emotions from keywords"""
        emotions = {}
        words = text.split()
        
        for emotion, intensity_dict in self.emotion_keywords.items():
            emotion_score = 0
            
            for intensity, keywords in intensity_dict.items():
                for keyword in keywords:
                    if keyword in text:
                        # Score based on intensity
                        if intensity == 'high':
                            score = 0.9
                        elif intensity == 'medium':
                            score = 0.7
                        else:  # low
                            score = 0.5
                        
                        emotion_score = max(emotion_score, score)
            
            if emotion_score > 0:
                emotions[emotion] = emotion_score
        
        return emotions
    
    def _detect_contextual_emotions(self, text: str) -> Dict[str, float]:
        """Detect emotions from contextual patterns"""
        emotions = {}
        
        context_emotion_map = {
            'stress_indicators': ('anxious', 0.7),
            'support_seeking': ('confused', 0.6),
            'positive_events': ('happy', 0.8),
            'negative_events': ('sad', 0.8),
            'relationship_issues': ('sad', 0.7),
            'work_stress': ('frustrated', 0.7)
        }
        
        for pattern_type, patterns in self.context_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    emotion, confidence = context_emotion_map.get(pattern_type, ('neutral', 0.5))
                    emotions[emotion] = max(emotions.get(emotion, 0), confidence)
        
        return emotions
    
    def _combine_emotion_scores(self, *emotion_dicts) -> Dict[str, float]:
        """Combine multiple emotion score dictionaries"""
        combined = {}
        
        for emotion_dict in emotion_dicts:
            for emotion, score in emotion_dict.items():
                combined[emotion] = max(combined.get(emotion, 0), score)
        
        return combined
    
    def _apply_intensity_modifiers(self, emotions: Dict[str, float], text: str) -> Dict[str, float]:
        """Apply intensity modifiers to emotion scores"""
        modified = emotions.copy()
        
        # Find intensity modifiers in text
        words = text.split()
        for i, word in enumerate(words):
            if word in self.intensity_modifiers:
                modifier = self.intensity_modifiers[word]
                
                # Apply modifier to nearby emotion words (within 3 words)
                for j in range(max(0, i-3), min(len(words), i+4)):
                    if j != i:
                        nearby_word = words[j]
                        for emotion in emotions:
                            if self._word_in_emotion_keywords(nearby_word, emotion):
                                modified[emotion] = min(1.0, modified[emotion] * modifier)
        
        return modified
    
    def _handle_negations(self, emotions: Dict[str, float], text: str) -> Dict[str, float]:
        """Handle negations that flip emotion meaning"""
        words = text.split()
        negated_emotions = {}
        
        for i, word in enumerate(words):
            if word in self.negation_words:
                # Look for emotion words within 3 words after negation
                for j in range(i+1, min(len(words), i+4)):
                    negated_word = words[j]
                    for emotion in emotions:
                        if self._word_in_emotion_keywords(negated_word, emotion):
                            # Reduce confidence for negated emotions
                            negated_emotions[emotion] = emotions[emotion] * 0.3
        
        # Apply negations
        for emotion, reduced_score in negated_emotions.items():
            emotions[emotion] = reduced_score
        
        return emotions
    
    def _word_in_emotion_keywords(self, word: str, emotion: str) -> bool:
        """Check if word is in emotion keywords"""
        if emotion not in self.emotion_keywords:
            return False
        
        for intensity_dict in self.emotion_keywords[emotion].values():
            if word in intensity_dict:
                return True
        
        return False
    
    def _create_emotion_result(self, emotions: Dict[str, float], original_text: str) -> EmotionResult:
        """Create final emotion result"""
        if not emotions:
            return self._create_default_result()
        
        # Find primary emotion
        primary_emotion = max(emotions, key=emotions.get)
        confidence = emotions[primary_emotion]
        
        # Determine intensity
        intensity = self._determine_intensity(confidence, original_text)
        
        # Extract indicators
        indicators = self._extract_emotional_indicators(original_text, emotions)
        
        # Extract context clues
        context_clues = self._extract_context_clues(original_text)
        
        return EmotionResult(
            primary_emotion=primary_emotion,
            confidence=confidence,
            intensity=intensity,
            detected_emotions=emotions,
            emotional_indicators=indicators,
            context_clues=context_clues
        )
    
    def _determine_intensity(self, confidence: float, text: str) -> EmotionIntensity:
        """Determine emotion intensity based on confidence and text analysis"""
        # Base intensity on confidence
        if confidence >= 0.9:
            base_intensity = EmotionIntensity.VERY_HIGH
        elif confidence >= 0.7:
            base_intensity = EmotionIntensity.HIGH
        elif confidence >= 0.5:
            base_intensity = EmotionIntensity.MEDIUM
        else:
            base_intensity = EmotionIntensity.LOW
        
        # Adjust based on text features
        text_lower = text.lower()
        
        # Check for intensity indicators
        high_intensity_indicators = ['!!!', 'extremely', 'incredibly', 'absolutely']
        if any(indicator in text_lower for indicator in high_intensity_indicators):
            if base_intensity == EmotionIntensity.HIGH:
                return EmotionIntensity.VERY_HIGH
            elif base_intensity == EmotionIntensity.MEDIUM:
                return EmotionIntensity.HIGH
        
        # Check for caps (indicates strong emotion)
        caps_ratio = sum(1 for c in text if c.isupper()) / len(text) if text else 0
        if caps_ratio > 0.3:  # More than 30% caps
            if base_intensity == EmotionIntensity.MEDIUM:
                return EmotionIntensity.HIGH
            elif base_intensity == EmotionIntensity.LOW:
                return EmotionIntensity.MEDIUM
        
        return base_intensity
    
    def _extract_emotional_indicators(self, text: str, emotions: Dict[str, float]) -> List[str]:
        """Extract specific words/phrases that indicated emotions"""
        indicators = []
        text_lower = text.lower()
        
        # Find emotion keywords that were matched
        for emotion in emotions:
            if emotion in self.emotion_keywords:
                for intensity_dict in self.emotion_keywords[emotion].values():
                    for keyword in intensity_dict:
                        if keyword in text_lower:
                            indicators.append(keyword)
        
        # Find emojis
        for emoji in self.emoji_emotions:
            if emoji in text:
                indicators.append(emoji)
        
        return list(set(indicators))  # Remove duplicates
    
    def _extract_context_clues(self, text: str) -> List[str]:
        """Extract contextual clues that influenced emotion detection"""
        clues = []
        text_lower = text.lower()
        
        for pattern_type, patterns in self.context_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    clues.append(f"{pattern_type}: {pattern}")
        
        return clues
    
    def _create_default_result(self) -> EmotionResult:
        """Create default neutral emotion result"""
        return EmotionResult(
            primary_emotion='neutral',
            confidence=0.5,
            intensity=EmotionIntensity.LOW,
            detected_emotions={'neutral': 0.5},
            emotional_indicators=[],
            context_clues=[]
        )
    
    def _update_statistics(self, result: EmotionResult):
        """Update detection statistics"""
        if result.confidence >= 0.7:
            self.detection_stats['high_confidence_detections'] += 1
        
        emotion = result.primary_emotion
        self.detection_stats['emotion_distribution'][emotion] = \
            self.detection_stats['emotion_distribution'].get(emotion, 0) + 1
    
    def get_emotion_categories(self) -> List[str]:
        """Get list of supported emotion categories"""
        return list(self.emotion_keywords.keys()) + ['neutral']
    
    def get_detection_stats(self) -> Dict[str, any]:
        """Get emotion detection statistics"""
        total = self.detection_stats['total_detections']
        high_conf_rate = (
            self.detection_stats['high_confidence_detections'] / total * 100
            if total > 0 else 0
        )
        
        return {
            'total_detections': total,
            'high_confidence_rate': round(high_conf_rate, 2),
            'emotion_distribution': self.detection_stats['emotion_distribution'].copy(),
            'supported_emotions': self.get_emotion_categories()
        }
    
    def reset_stats(self):
        """Reset detection statistics"""
        self.detection_stats = {
            'total_detections': 0,
            'high_confidence_detections': 0,
            'emotion_distribution': {}
        }

# Global emotion detector instance
_emotion_detector = None

def get_emotion_detector() -> EnhancedEmotionDetector:
    """Get global emotion detector instance"""
    global _emotion_detector
    if _emotion_detector is None:
        _emotion_detector = EnhancedEmotionDetector()
    return _emotion_detector