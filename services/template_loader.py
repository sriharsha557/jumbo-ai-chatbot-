"""
Template Loader for Enhanced Conversation System
Handles loading, validation, and management of conversation templates
"""

import json
import os
import logging
from typing import Dict, List, Optional
from pathlib import Path

from services.template_models import (
    ConversationTemplate, 
    create_template_from_dict, 
    validate_template,
    TemplateValidationError,
    ConversationType,
    EmotionCategory
)

logger = logging.getLogger(__name__)

class TemplateLoader:
    """
    Loads and manages conversation templates from JSON files
    """
    
    def __init__(self, template_file_path: str = "data/conversation_templates.json"):
        self.template_file_path = template_file_path
        self.templates: Dict[str, ConversationTemplate] = {}
        self.templates_by_emotion: Dict[str, List[ConversationTemplate]] = {}
        self.templates_by_type: Dict[ConversationType, List[ConversationTemplate]] = {}
        self._load_templates()
    
    def _load_templates(self):
        """Load templates from JSON file"""
        try:
            if not os.path.exists(self.template_file_path):
                logger.error(f"Template file not found: {self.template_file_path}")
                self._create_fallback_templates()
                return
            
            with open(self.template_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            templates_data = data.get('templates', [])
            loaded_count = 0
            
            for template_data in templates_data:
                try:
                    template = create_template_from_dict(template_data)
                    self.templates[template.id] = template
                    loaded_count += 1
                    
                    # Index by emotion
                    for emotion_tag in template.emotion_tags:
                        if emotion_tag not in self.templates_by_emotion:
                            self.templates_by_emotion[emotion_tag] = []
                        self.templates_by_emotion[emotion_tag].append(template)
                    
                    # Index by conversation type
                    if template.conversation_type not in self.templates_by_type:
                        self.templates_by_type[template.conversation_type] = []
                    self.templates_by_type[template.conversation_type].append(template)
                    
                except TemplateValidationError as e:
                    logger.error(f"Template validation error for {template_data.get('id', 'unknown')}: {e}")
                except Exception as e:
                    logger.error(f"Error loading template {template_data.get('id', 'unknown')}: {e}")
            
            logger.info(f"Successfully loaded {loaded_count} conversation templates")
            
            if loaded_count == 0:
                logger.warning("No templates loaded, creating fallback templates")
                self._create_fallback_templates()
                
        except Exception as e:
            logger.error(f"Error loading templates from {self.template_file_path}: {e}")
            self._create_fallback_templates()
    
    def _create_fallback_templates(self):
        """Create basic fallback templates if loading fails"""
        fallback_templates = [
            {
                "id": "fallback_empathetic",
                "category": "neutral",
                "emotion_tags": ["neutral", "sad", "anxious", "angry"],
                "conversation_type": "emotional_support",
                "base_template": "I hear you {user_name}. Thank you for sharing that with me.",
                "variations": [
                    "I'm here to listen {user_name}. Tell me more about how you're feeling.",
                    "That sounds important {user_name}. I want to understand better.",
                    "I can sense this matters to you {user_name}. Please continue."
                ],
                "follow_up_questions": [
                    "How are you feeling about this?",
                    "What would be most helpful right now?",
                    "Tell me more about what's on your mind."
                ],
                "context_requirements": ["user_name"],
                "personality_tone": "empathetic",
                "usage_weight": 1.0,
                "min_confidence": 0.0
            },
            {
                "id": "fallback_greeting",
                "category": "greeting",
                "emotion_tags": ["neutral", "happy"],
                "conversation_type": "greeting",
                "base_template": "Hello {user_name}! How are you today?",
                "variations": [
                    "Hi {user_name}! It's good to see you.",
                    "Welcome {user_name}! What's on your mind?",
                    "Hey there {user_name}! How can I help you today?"
                ],
                "follow_up_questions": [
                    "How has your day been?",
                    "What would you like to talk about?",
                    "How are you feeling today?"
                ],
                "context_requirements": ["user_name"],
                "personality_tone": "gentle",
                "usage_weight": 1.0,
                "min_confidence": 0.0
            }
        ]
        
        for template_data in fallback_templates:
            try:
                template = create_template_from_dict(template_data)
                self.templates[template.id] = template
                
                # Index fallback templates
                for emotion_tag in template.emotion_tags:
                    if emotion_tag not in self.templates_by_emotion:
                        self.templates_by_emotion[emotion_tag] = []
                    self.templates_by_emotion[emotion_tag].append(template)
                
                if template.conversation_type not in self.templates_by_type:
                    self.templates_by_type[template.conversation_type] = []
                self.templates_by_type[template.conversation_type].append(template)
                
            except Exception as e:
                logger.error(f"Error creating fallback template: {e}")
        
        logger.info(f"Created {len(fallback_templates)} fallback templates")
    
    def get_template_by_id(self, template_id: str) -> Optional[ConversationTemplate]:
        """Get template by ID"""
        return self.templates.get(template_id)
    
    def get_templates_by_emotion(self, emotion: str) -> List[ConversationTemplate]:
        """Get all templates matching an emotion"""
        return self.templates_by_emotion.get(emotion.lower(), [])
    
    def get_templates_by_type(self, conversation_type: ConversationType) -> List[ConversationTemplate]:
        """Get all templates matching a conversation type"""
        return self.templates_by_type.get(conversation_type, [])
    
    def get_templates_by_emotion_and_type(self, emotion: str, 
                                        conversation_type: ConversationType) -> List[ConversationTemplate]:
        """Get templates matching both emotion and conversation type"""
        emotion_templates = self.get_templates_by_emotion(emotion)
        return [t for t in emotion_templates if t.conversation_type == conversation_type]
    
    def get_all_templates(self) -> Dict[str, ConversationTemplate]:
        """Get all loaded templates"""
        return self.templates.copy()
    
    def get_template_stats(self) -> Dict[str, int]:
        """Get statistics about loaded templates"""
        stats = {
            'total_templates': len(self.templates),
            'emotions_covered': len(self.templates_by_emotion),
            'conversation_types_covered': len(self.templates_by_type)
        }
        
        # Count templates by emotion
        for emotion, templates in self.templates_by_emotion.items():
            stats[f'emotion_{emotion}'] = len(templates)
        
        # Count templates by conversation type
        for conv_type, templates in self.templates_by_type.items():
            stats[f'type_{conv_type.value}'] = len(templates)
        
        return stats
    
    def validate_all_templates(self) -> Dict[str, List[str]]:
        """Validate all loaded templates and return any issues"""
        validation_results = {
            'valid': [],
            'invalid': [],
            'warnings': []
        }
        
        for template_id, template in self.templates.items():
            try:
                # Check basic structure
                if not template.base_template:
                    validation_results['invalid'].append(f"{template_id}: Empty base template")
                    continue
                
                if not template.emotion_tags:
                    validation_results['warnings'].append(f"{template_id}: No emotion tags")
                
                if not template.variations:
                    validation_results['warnings'].append(f"{template_id}: No variations provided")
                
                # Check for placeholder consistency
                if '{user_name}' in template.base_template:
                    if 'user_name' not in template.context_requirements:
                        validation_results['warnings'].append(
                            f"{template_id}: Uses user_name but doesn't require it in context"
                        )
                
                validation_results['valid'].append(template_id)
                
            except Exception as e:
                validation_results['invalid'].append(f"{template_id}: {str(e)}")
        
        return validation_results
    
    def reload_templates(self):
        """Reload templates from file"""
        self.templates.clear()
        self.templates_by_emotion.clear()
        self.templates_by_type.clear()
        self._load_templates()
        logger.info("Templates reloaded successfully")

# Global template loader instance
_template_loader = None

def get_template_loader() -> TemplateLoader:
    """Get global template loader instance"""
    global _template_loader
    if _template_loader is None:
        _template_loader = TemplateLoader()
    return _template_loader

def reload_templates():
    """Reload templates globally"""
    global _template_loader
    if _template_loader is not None:
        _template_loader.reload_templates()
    else:
        _template_loader = TemplateLoader()