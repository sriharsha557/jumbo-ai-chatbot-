"""
Emotion Service Factory
Dynamically loads appropriate emotion service based on deployment tier
"""

import os
import logging
from typing import Any

logger = logging.getLogger(__name__)

def get_emotion_detector():
    """
    Factory function to get appropriate emotion detector
    based on deployment tier and available resources
    """
    
    # Check deployment tier
    deployment_tier = os.getenv('DEPLOYMENT_TIER', 'free').lower()
    
    try:
        if deployment_tier in ['professional', 'enterprise']:
            # Try to load heavy ML emotion service
            try:
                from services.emotion_service import get_emotion_detector as get_heavy_detector
                detector = get_heavy_detector()
                logger.info("✅ Loaded heavy ML emotion detector")
                return detector
            except (ImportError, RuntimeError, MemoryError) as e:
                logger.warning(f"Heavy ML emotion detector failed: {e}, falling back to lightweight")
        
        elif deployment_tier == 'starter':
            # Try lightweight transformer model
            try:
                from services.emotion_service_lightweight import get_emotion_detector as get_light_detector
                detector = get_light_detector()
                logger.info("✅ Loaded lightweight emotion detector")
                return detector
            except (ImportError, RuntimeError, MemoryError) as e:
                logger.warning(f"Lightweight emotion detector failed: {e}, falling back to minimal")
        
        # Default: Use minimal keyword-based emotion detection
        from services.emotion_service_minimal import get_emotion_detector as get_minimal_detector
        detector = get_minimal_detector()
        logger.info("✅ Loaded minimal keyword-based emotion detector")
        return detector
        
    except Exception as e:
        logger.error(f"Failed to load any emotion detector: {e}")
        # Return a dummy detector that always returns neutral
        return DummyEmotionDetector()

class DummyEmotionDetector:
    """Fallback emotion detector that always returns neutral"""
    
    def detect_emotion(self, text: str):
        return {'neutral': 1.0}
    
    def get_dominant_emotion(self, text: str):
        return 'neutral'