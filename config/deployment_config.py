"""
Deployment Configuration Manager
Handles different deployment tiers and ML capabilities
"""

import os
from enum import Enum
from typing import Dict, Any

class DeploymentTier(Enum):
    """Deployment tiers with different capabilities"""
    FREE = "free"           # Render free tier - minimal ML
    STARTER = "starter"     # Paid hosting - basic ML
    PROFESSIONAL = "pro"    # Full infrastructure - heavy ML
    ENTERPRISE = "enterprise" # Custom infrastructure - all features

class MLCapabilities:
    """ML capabilities based on deployment tier"""
    
    CAPABILITIES = {
        DeploymentTier.FREE: {
            "emotion_detection": "keyword",  # Keyword-based
            "memory_limit": "512MB",
            "ml_models": [],
            "requirements_file": "requirements.txt"
        },
        DeploymentTier.STARTER: {
            "emotion_detection": "lightweight",  # Small transformer
            "memory_limit": "2GB", 
            "ml_models": ["distilbert-base-uncased"],
            "requirements_file": "requirements-starter.txt"
        },
        DeploymentTier.PROFESSIONAL: {
            "emotion_detection": "advanced",  # Full transformer models
            "memory_limit": "8GB",
            "ml_models": ["j-hartmann/emotion-english-distilroberta-base"],
            "requirements_file": "requirements-full.txt"
        },
        DeploymentTier.ENTERPRISE: {
            "emotion_detection": "custom",  # Custom fine-tuned models
            "memory_limit": "unlimited",
            "ml_models": ["custom-emotion-model", "custom-personality-model"],
            "requirements_file": "requirements-enterprise.txt"
        }
    }
    
    @classmethod
    def get_tier(cls) -> DeploymentTier:
        """Detect current deployment tier from environment"""
        tier_env = os.getenv('DEPLOYMENT_TIER', 'free').lower()
        
        try:
            return DeploymentTier(tier_env)
        except ValueError:
            return DeploymentTier.FREE
    
    @classmethod
    def get_capabilities(cls) -> Dict[str, Any]:
        """Get capabilities for current deployment tier"""
        tier = cls.get_tier()
        return cls.CAPABILITIES[tier]
    
    @classmethod
    def supports_heavy_ml(cls) -> bool:
        """Check if current tier supports heavy ML models"""
        tier = cls.get_tier()
        return tier in [DeploymentTier.PROFESSIONAL, DeploymentTier.ENTERPRISE]
    
    @classmethod
    def get_emotion_service_type(cls) -> str:
        """Get the appropriate emotion service type"""
        capabilities = cls.get_capabilities()
        return capabilities["emotion_detection"]