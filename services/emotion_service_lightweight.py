"""
Lightweight Emotion Service
Uses smaller, more efficient models for starter tier deployments
"""

import logging
from typing import Dict, Optional
import os

logger = logging.getLogger(__name__)

class LightweightEmotionDetector:
    """Lightweight emotion detection using smaller models"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize lightweight emotion model"""
        try:
            # Use a smaller, more efficient model
            from transformers import pipeline
            
            # Use a lightweight model that's faster and uses less memory
            model_name = "cardiffnlp/twitter-roberta-base-emotion"
            
            self.emotion_pipeline = pipeline(
                "text-classification",
                model=model_name,
                device=-1,  # Force CPU usage
                framework="pt"
            )
            
            logger.info(f"✅ Lightweight emotion model loaded: {model_name}")
            
        except Exception as e:
            logger.error(f"Failed to load lightweight emotion model: {e}")
            raise
    
    def detect_emotion(self, text: str) -> Dict[str, float]:
        """Detect emotions using lightweight model"""
        if not text or not self.emotion_pipeline:
            return {'neutral': 1.0}
        
        try:
            # Get predictions
            results = self.emotion_pipeline(text)
            
            # Convert to our emotion format
            emotion_scores = {}
            for result in results:
                label = result['label'].lower()
                score = result['score']
                
                # Map model labels to our emotion categories
                emotion_map = {
                    'joy': 'joy',
                    'sadness': 'sadness', 
                    'anger': 'anger',
                    'fear': 'fear',
                    'surprise': 'surprise',
                    'optimism': 'joy',
                    'pessimism': 'sadness'
                }
                
                emotion = emotion_map.get(label, 'neutral')
                emotion_scores[emotion] = score
            
            return emotion_scores if emotion_scores else {'neutral': 1.0}
            
        except Exception as e:
            logger.error(f"Error in lightweight emotion detection: {e}")
            return {'neutral': 1.0}
    
    def get_dominant_emotion(self, text: str) -> str:
        """Get the dominant emotion from text"""
        emotions = self.detect_emotion(text)
        if not emotions:
            return 'neutral'
        
        return max(emotions.items(), key=lambda x: x[1])[0]

# Global instance
_emotion_detector = None

def get_emotion_detector():
    """Get the global lightweight emotion detector instance"""
    global _emotion_detector
    if _emotion_detector is None:
        _emotion_detector = LightweightEmotionDetector()
    return _emotion_detector