"""
Minimal emotion service for production deployment
Uses simple keyword-based emotion detection instead of heavy ML models
"""

import re
from typing import Dict, Optional

class MinimalEmotionDetector:
    """Lightweight emotion detection using keyword matching"""
    
    def __init__(self):
        self.emotion_keywords = {
            'joy': ['happy', 'excited', 'great', 'awesome', 'wonderful', 'amazing', 'love', 'fantastic'],
            'sadness': ['sad', 'depressed', 'down', 'upset', 'disappointed', 'hurt', 'cry'],
            'anger': ['angry', 'mad', 'furious', 'annoyed', 'frustrated', 'hate', 'irritated'],
            'fear': ['scared', 'afraid', 'worried', 'anxious', 'nervous', 'terrified', 'panic'],
            'surprise': ['surprised', 'shocked', 'amazed', 'wow', 'unexpected', 'sudden'],
            'disgust': ['disgusted', 'gross', 'yuck', 'awful', 'terrible', 'horrible']
        }
    
    def detect_emotion(self, text: str) -> Dict[str, float]:
        """
        Detect emotions using keyword matching
        Returns emotion scores between 0 and 1
        """
        if not text:
            return {'neutral': 1.0}
        
        text_lower = text.lower()
        emotion_scores = {}
        
        for emotion, keywords in self.emotion_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    score += 1
            
            if score > 0:
                # Normalize score (simple approach)
                emotion_scores[emotion] = min(score / len(keywords), 1.0)
        
        # If no emotions detected, return neutral
        if not emotion_scores:
            emotion_scores['neutral'] = 1.0
        
        return emotion_scores
    
    def get_dominant_emotion(self, text: str) -> str:
        """Get the dominant emotion from text"""
        emotions = self.detect_emotion(text)
        if not emotions:
            return 'neutral'
        
        return max(emotions.items(), key=lambda x: x[1])[0]

# Global instance
_emotion_detector = None

def get_emotion_detector():
    """Get the global emotion detector instance"""
    global _emotion_detector
    if _emotion_detector is None:
        _emotion_detector = MinimalEmotionDetector()
    return _emotion_detector