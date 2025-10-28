"""
Emotion Detection Service
Real-time emotion analysis using Transformers
"""

import logging
from typing import Dict, Optional, List, Tuple
import re
import time
from transformers import pipeline
import torch

logger = logging.getLogger(__name__)

class EmotionDetector:
    """
    Advanced emotion detection using pre-trained transformer models
    Supports multiple emotions with confidence scores
    """
    
    def __init__(self, model_name: str = "j-hartmann/emotion-english-distilroberta-base"):
        """
        Initialize emotion detector with specified model
        
        Args:
            model_name: HuggingFace model for emotion classification
        """
        self.model_name = model_name
        self.classifier = None
        self.is_initialized = False
        self.initialization_error = None
        
        # Emotion mapping for consistency
        self.emotion_mapping = {
            'joy': 'happy',
            'happiness': 'happy',
            'sadness': 'sad',
            'fear': 'fear',
            'anger': 'angry',
            'surprise': 'surprise',
            'disgust': 'angry',  # Map disgust to angry for simplicity
            'neutral': 'neutral'
        }
        
        # Initialize the model
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the emotion classification model"""
        try:
            logger.info(f"Initializing emotion detector with model: {self.model_name}")
            
            # Use CPU for better compatibility
            device = -1  # CPU
            if torch.cuda.is_available():
                device = 0  # GPU if available
                logger.info("CUDA available, using GPU for emotion detection")
            else:
                logger.info("Using CPU for emotion detection")
            
            # Initialize the pipeline
            self.classifier = pipeline(
                "text-classification",
                model=self.model_name,
                device=device,
                return_all_scores=True  # Get all emotion scores
            )
            
            self.is_initialized = True
            logger.info("✅ Emotion detector initialized successfully")
            
            # Test the model with a simple phrase
            test_result = self._detect_emotion_raw("I am happy")
            logger.info(f"✅ Model test successful: {test_result}")
            
        except Exception as e:
            self.initialization_error = str(e)
            logger.error(f"❌ Failed to initialize emotion detector: {e}")
            logger.warning("Emotion detection will fall back to rule-based detection")
    
    def detect_emotion(self, text: str) -> Dict[str, any]:
        """
        Detect emotion from text with confidence score
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dict with emotion, confidence, and metadata
        """
        if not text or not text.strip():
            return {
                "emotion": "neutral",
                "confidence": 0.5,
                "method": "empty_input",
                "raw_scores": {},
                "processing_time": 0.0
            }
        
        start_time = time.time()
        
        try:
            # Clean the text
            cleaned_text = self._clean_text(text)
            
            # Try ML-based detection first
            if self.is_initialized and self.classifier:
                result = self._detect_emotion_ml(cleaned_text)
                result["processing_time"] = time.time() - start_time
                return result
            
            # Fallback to rule-based detection
            result = self._detect_emotion_rule_based(cleaned_text)
            result["processing_time"] = time.time() - start_time
            return result
            
        except Exception as e:
            logger.error(f"Error in emotion detection: {e}")
            return {
                "emotion": "neutral",
                "confidence": 0.5,
                "method": "error_fallback",
                "error": str(e),
                "raw_scores": {},
                "processing_time": time.time() - start_time
            }
    
    def _detect_emotion_ml(self, text: str) -> Dict[str, any]:
        """ML-based emotion detection using transformers"""
        try:
            # Get predictions from the model
            predictions = self.classifier(text)
            
            # Process results
            if predictions and len(predictions) > 0:
                # Get the top prediction
                top_prediction = max(predictions[0], key=lambda x: x['score'])
                
                # Map emotion to our standard set
                raw_emotion = top_prediction['label'].lower()
                mapped_emotion = self.emotion_mapping.get(raw_emotion, raw_emotion)
                
                # Create raw scores dict
                raw_scores = {pred['label'].lower(): pred['score'] for pred in predictions[0]}
                
                return {
                    "emotion": mapped_emotion,
                    "confidence": top_prediction['score'],
                    "method": "ml_transformer",
                    "raw_emotion": raw_emotion,
                    "raw_scores": raw_scores,
                    "model": self.model_name
                }
            
            # Fallback if no predictions
            return self._detect_emotion_rule_based(text)
            
        except Exception as e:
            logger.error(f"ML emotion detection failed: {e}")
            return self._detect_emotion_rule_based(text)
    
    def _detect_emotion_rule_based(self, text: str) -> Dict[str, any]:
        """Rule-based emotion detection as fallback"""
        text_lower = text.lower()
        
        # Emotion keywords with weights
        emotion_patterns = {
            'happy': {
                'keywords': ['happy', 'joy', 'excited', 'great', 'awesome', 'wonderful', 'amazing', 'fantastic', 'love', 'perfect', 'excellent', 'brilliant', 'thrilled', 'delighted', 'cheerful', 'glad', 'pleased'],
                'weight': 1.0
            },
            'sad': {
                'keywords': ['sad', 'depressed', 'down', 'upset', 'hurt', 'crying', 'tears', 'miserable', 'heartbroken', 'devastated', 'disappointed', 'gloomy', 'melancholy', 'sorrowful', 'grief'],
                'weight': 1.0
            },
            'angry': {
                'keywords': ['angry', 'mad', 'furious', 'rage', 'hate', 'annoyed', 'irritated', 'frustrated', 'pissed', 'outraged', 'livid', 'enraged', 'infuriated', 'aggravated'],
                'weight': 1.0
            },
            'anxious': {
                'keywords': ['anxious', 'worried', 'nervous', 'scared', 'afraid', 'panic', 'stress', 'overwhelmed', 'concerned', 'uneasy', 'tense', 'apprehensive', 'fearful'],
                'weight': 1.0
            },
            'fear': {
                'keywords': ['terrified', 'frightened', 'horror', 'dread', 'phobia', 'petrified', 'alarmed', 'startled'],
                'weight': 1.0
            },
            'surprise': {
                'keywords': ['surprised', 'shocked', 'amazed', 'astonished', 'stunned', 'bewildered', 'unexpected', 'wow'],
                'weight': 1.0
            }
        }
        
        # Calculate scores for each emotion
        emotion_scores = {}
        for emotion, data in emotion_patterns.items():
            score = 0
            for keyword in data['keywords']:
                if keyword in text_lower:
                    score += data['weight']
            
            # Normalize by text length
            if len(text_lower.split()) > 0:
                emotion_scores[emotion] = score / len(text_lower.split())
            else:
                emotion_scores[emotion] = 0
        
        # Find the highest scoring emotion
        if emotion_scores and max(emotion_scores.values()) > 0:
            top_emotion = max(emotion_scores, key=emotion_scores.get)
            confidence = min(emotion_scores[top_emotion] * 2, 1.0)  # Scale confidence
            
            return {
                "emotion": top_emotion,
                "confidence": confidence,
                "method": "rule_based",
                "raw_scores": emotion_scores
            }
        
        # Default to neutral
        return {
            "emotion": "neutral",
            "confidence": 0.7,
            "method": "rule_based_default",
            "raw_scores": emotion_scores
        }
    
    def _detect_emotion_raw(self, text: str) -> List[Dict]:
        """Raw emotion detection for testing"""
        if self.classifier:
            return self.classifier(text)
        return []
    
    def _clean_text(self, text: str) -> str:
        """Clean and preprocess text for emotion detection"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Keep only letters, numbers, spaces, and basic punctuation
        text = re.sub(r'[^a-zA-Z0-9\s.,!?\'"-]', '', text)
        
        return text.strip()
    
    def get_emotion_intensity(self, text: str) -> Dict[str, float]:
        """
        Get intensity scores for all emotions
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dict mapping emotions to intensity scores
        """
        result = self.detect_emotion(text)
        
        if "raw_scores" in result and result["raw_scores"]:
            return result["raw_scores"]
        
        # Fallback: return single emotion with confidence
        return {result["emotion"]: result["confidence"]}
    
    def batch_detect_emotions(self, texts: List[str]) -> List[Dict[str, any]]:
        """
        Detect emotions for multiple texts
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            List of emotion detection results
        """
        results = []
        for text in texts:
            results.append(self.detect_emotion(text))
        return results
    
    def is_available(self) -> bool:
        """Check if emotion detection is available"""
        return self.is_initialized and self.classifier is not None
    
    def get_status(self) -> Dict[str, any]:
        """Get status information about the emotion detector"""
        return {
            "initialized": self.is_initialized,
            "model": self.model_name,
            "method": "ml_transformer" if self.is_initialized else "rule_based",
            "error": self.initialization_error,
            "cuda_available": torch.cuda.is_available()
        }

# Singleton instance for global use
_emotion_detector = None

def get_emotion_detector() -> EmotionDetector:
    """Get the global emotion detector instance"""
    global _emotion_detector
    if _emotion_detector is None:
        _emotion_detector = EmotionDetector()
    return _emotion_detector

def detect_emotion_quick(text: str) -> str:
    """Quick emotion detection returning just the emotion name"""
    detector = get_emotion_detector()
    result = detector.detect_emotion(text)
    return result["emotion"]

def detect_emotion_with_confidence(text: str) -> Tuple[str, float]:
    """Emotion detection returning emotion and confidence"""
    detector = get_emotion_detector()
    result = detector.detect_emotion(text)
    return result["emotion"], result["confidence"]