"""
Template Validator for Enhanced Conversation System
Provides comprehensive validation and categorization for conversation templates
"""

import re
import logging
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass

from services.template_models import (
    ConversationTemplate, 
    ConversationType, 
    PersonalityTone,
    EmotionCategory
)

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Result of template validation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]

class TemplateValidator:
    """
    Comprehensive validator for conversation templates
    """
    
    def __init__(self):
        self.placeholder_pattern = re.compile(r'\{([^}]+)\}')
        self.emotion_keywords = self._load_emotion_keywords()
        self.personality_indicators = self._load_personality_indicators()
    
    def _load_emotion_keywords(self) -> Dict[str, List[str]]:
        """Load emotion-specific keywords for validation"""
        return {
            'happy': ['wonderful', 'amazing', 'fantastic', 'great', 'excited', 'joy', 'celebrate'],
            'sad': ['sorry', 'difficult', 'tough', 'understand', 'here for you', 'listen'],
            'angry': ['frustrated', 'upset', 'valid', 'understand', 'feel', 'anger'],
            'anxious': ['calm', 'breathe', 'safe', 'together', 'step by step', 'okay'],
            'confused': ['clarify', 'understand', 'together', 'step by step', 'break down'],
            'tired': ['rest', 'tired', 'exhausted', 'care', 'recharge', 'energy'],
            'neutral': ['listen', 'understand', 'tell me', 'share', 'talk']
        }
    
    def _load_personality_indicators(self) -> Dict[PersonalityTone, List[str]]:
        """Load personality tone indicators"""
        return {
            PersonalityTone.EMPATHETIC: ['understand', 'feel', 'hear', 'sense', 'with you'],
            PersonalityTone.ENCOURAGING: ['wonderful', 'amazing', 'can do', 'believe', 'proud'],
            PersonalityTone.GENTLE: ['softly', 'gently', 'peacefully', 'calm', 'tender'],
            PersonalityTone.SUPPORTIVE: ['here for you', 'together', 'support', 'help', 'alongside'],
            PersonalityTone.CURIOUS: ['tell me', 'what', 'how', 'explore', 'discover'],
            PersonalityTone.VALIDATING: ['valid', 'makes sense', 'understand', 'right to feel'],
            PersonalityTone.CALMING: ['breathe', 'calm', 'peaceful', 'safe', 'relax']
        }
    
    def validate_template(self, template: ConversationTemplate) -> ValidationResult:
        """
        Comprehensive validation of a conversation template
        """
        errors = []
        warnings = []
        suggestions = []
        
        # Basic structure validation
        structure_result = self._validate_structure(template)
        errors.extend(structure_result.errors)
        warnings.extend(structure_result.warnings)
        suggestions.extend(structure_result.suggestions)
        
        # Content validation
        content_result = self._validate_content(template)
        errors.extend(content_result.errors)
        warnings.extend(content_result.warnings)
        suggestions.extend(content_result.suggestions)
        
        # Emotion alignment validation
        emotion_result = self._validate_emotion_alignment(template)
        warnings.extend(emotion_result.warnings)
        suggestions.extend(emotion_result.suggestions)
        
        # Personality consistency validation
        personality_result = self._validate_personality_consistency(template)
        warnings.extend(personality_result.warnings)
        suggestions.extend(personality_result.suggestions)
        
        # Context requirements validation
        context_result = self._validate_context_requirements(template)
        errors.extend(context_result.errors)
        warnings.extend(context_result.warnings)
        
        is_valid = len(errors) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions
        )
    
    def _validate_structure(self, template: ConversationTemplate) -> ValidationResult:
        """Validate basic template structure"""
        errors = []
        warnings = []
        suggestions = []
        
        # Required fields
        if not template.id:
            errors.append("Template ID is required")
        
        if not template.base_template:
            errors.append("Base template text is required")
        
        if not template.emotion_tags:
            warnings.append("No emotion tags specified")
        
        # Template length validation
        if len(template.base_template) > 500:
            warnings.append("Base template is very long (>500 chars), consider shortening")
        
        if len(template.base_template) < 10:
            warnings.append("Base template is very short (<10 chars), consider expanding")
        
        # Variations validation
        if not template.variations:
            suggestions.append("Consider adding variations to avoid repetitive responses")
        elif len(template.variations) < 3:
            suggestions.append("Consider adding more variations (recommended: 3-5)")
        
        # Follow-up questions validation
        if not template.follow_up_questions:
            suggestions.append("Consider adding follow-up questions to encourage conversation")
        
        return ValidationResult(True, errors, warnings, suggestions)
    
    def _validate_content(self, template: ConversationTemplate) -> ValidationResult:
        """Validate template content quality"""
        errors = []
        warnings = []
        suggestions = []
        
        # Check for placeholders
        placeholders = self._extract_placeholders(template.base_template)
        
        # Validate placeholder format
        for placeholder in placeholders:
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', placeholder):
                errors.append(f"Invalid placeholder format: {{{placeholder}}}")
        
        # Check for common placeholders
        if 'user_name' in template.base_template and 'user_name' not in placeholders:
            errors.append("Template references user_name but placeholder is malformed")
        
        # Content quality checks
        text_lower = template.base_template.lower()
        
        # Check for empathy indicators
        empathy_words = ['understand', 'hear', 'feel', 'sense', 'with you', 'listen']
        if not any(word in text_lower for word in empathy_words):
            suggestions.append("Consider adding empathetic language to show understanding")
        
        # Check for questions or engagement
        if '?' not in template.base_template and not template.follow_up_questions:
            suggestions.append("Consider adding questions to encourage user engagement")
        
        # Check for overly clinical language
        clinical_words = ['diagnose', 'treatment', 'therapy', 'disorder', 'condition']
        if any(word in text_lower for word in clinical_words):
            warnings.append("Avoid clinical language - focus on supportive conversation")
        
        return ValidationResult(True, errors, warnings, suggestions)
    
    def _validate_emotion_alignment(self, template: ConversationTemplate) -> ValidationResult:
        """Validate that template content aligns with emotion tags"""
        warnings = []
        suggestions = []
        
        text_lower = template.base_template.lower()
        
        for emotion_tag in template.emotion_tags:
            if emotion_tag in self.emotion_keywords:
                expected_keywords = self.emotion_keywords[emotion_tag]
                found_keywords = [kw for kw in expected_keywords if kw in text_lower]
                
                if not found_keywords:
                    suggestions.append(
                        f"Template tagged as '{emotion_tag}' but doesn't contain typical "
                        f"keywords. Consider adding: {', '.join(expected_keywords[:3])}"
                    )
        
        return ValidationResult(True, [], warnings, suggestions)
    
    def _validate_personality_consistency(self, template: ConversationTemplate) -> ValidationResult:
        """Validate personality tone consistency"""
        warnings = []
        suggestions = []
        
        text_lower = template.base_template.lower()
        personality_tone = template.personality_tone
        
        if personality_tone in self.personality_indicators:
            expected_indicators = self.personality_indicators[personality_tone]
            found_indicators = [ind for ind in expected_indicators if ind in text_lower]
            
            if not found_indicators:
                suggestions.append(
                    f"Template marked as '{personality_tone.value}' but doesn't reflect this tone. "
                    f"Consider adding phrases like: {', '.join(expected_indicators[:2])}"
                )
        
        return ValidationResult(True, [], warnings, suggestions)
    
    def _validate_context_requirements(self, template: ConversationTemplate) -> ValidationResult:
        """Validate context requirements match template content"""
        errors = []
        warnings = []
        
        placeholders = self._extract_placeholders(template.base_template)
        
        # Check if all placeholders are in context requirements
        for placeholder in placeholders:
            if placeholder not in template.context_requirements:
                errors.append(
                    f"Template uses placeholder '{{{placeholder}}}' but doesn't require it in context"
                )
        
        # Check if context requirements are actually used
        for requirement in template.context_requirements:
            if f'{{{requirement}}}' not in template.base_template:
                # Check variations too
                used_in_variations = any(
                    f'{{{requirement}}}' in variation 
                    for variation in template.variations
                )
                if not used_in_variations:
                    warnings.append(
                        f"Context requirement '{requirement}' is specified but not used in template"
                    )
        
        return ValidationResult(True, errors, warnings, [])
    
    def _extract_placeholders(self, text: str) -> List[str]:
        """Extract placeholder names from template text"""
        matches = self.placeholder_pattern.findall(text)
        return matches
    
    def categorize_template(self, template: ConversationTemplate) -> Dict[str, any]:
        """
        Automatically categorize template based on content analysis
        """
        text_lower = template.base_template.lower()
        
        # Analyze emotion indicators
        detected_emotions = []
        for emotion, keywords in self.emotion_keywords.items():
            keyword_count = sum(1 for kw in keywords if kw in text_lower)
            if keyword_count > 0:
                detected_emotions.append((emotion, keyword_count))
        
        # Sort by keyword count
        detected_emotions.sort(key=lambda x: x[1], reverse=True)
        
        # Analyze personality tone
        detected_tones = []
        for tone, indicators in self.personality_indicators.items():
            indicator_count = sum(1 for ind in indicators if ind in text_lower)
            if indicator_count > 0:
                detected_tones.append((tone, indicator_count))
        
        detected_tones.sort(key=lambda x: x[1], reverse=True)
        
        # Analyze conversation type
        conversation_type_indicators = {
            ConversationType.GREETING: ['hello', 'hi', 'welcome', 'good to see'],
            ConversationType.GOODBYE: ['goodbye', 'take care', 'until', 'farewell'],
            ConversationType.EMOTIONAL_SUPPORT: ['sorry', 'understand', 'here for you', 'listen'],
            ConversationType.CASUAL_CHAT: ['chat', 'talk', 'conversation', 'what\'s new'],
            ConversationType.MEMORY_RECALL: ['remember', 'recall', 'mentioned', 'told me'],
            ConversationType.ADVICE_SEEKING: ['help', 'advice', 'suggest', 'what should'],
            ConversationType.CELEBRATION: ['wonderful', 'amazing', 'congratulations', 'celebrate']
        }
        
        detected_types = []
        for conv_type, indicators in conversation_type_indicators.items():
            indicator_count = sum(1 for ind in indicators if ind in text_lower)
            if indicator_count > 0:
                detected_types.append((conv_type, indicator_count))
        
        detected_types.sort(key=lambda x: x[1], reverse=True)
        
        return {
            'suggested_emotions': [emotion for emotion, _ in detected_emotions[:3]],
            'suggested_personality_tone': detected_tones[0][0] if detected_tones else PersonalityTone.EMPATHETIC,
            'suggested_conversation_type': detected_types[0][0] if detected_types else ConversationType.CASUAL_CHAT,
            'confidence_scores': {
                'emotion_confidence': detected_emotions[0][1] / 5 if detected_emotions else 0,
                'tone_confidence': detected_tones[0][1] / 3 if detected_tones else 0,
                'type_confidence': detected_types[0][1] / 3 if detected_types else 0
            }
        }

def validate_template_batch(templates: List[ConversationTemplate]) -> Dict[str, ValidationResult]:
    """Validate multiple templates and return results"""
    validator = TemplateValidator()
    results = {}
    
    for template in templates:
        results[template.id] = validator.validate_template(template)
    
    return results

def get_validation_summary(results: Dict[str, ValidationResult]) -> Dict[str, any]:
    """Get summary statistics from validation results"""
    total_templates = len(results)
    valid_templates = sum(1 for result in results.values() if result.is_valid)
    total_errors = sum(len(result.errors) for result in results.values())
    total_warnings = sum(len(result.warnings) for result in results.values())
    
    return {
        'total_templates': total_templates,
        'valid_templates': valid_templates,
        'invalid_templates': total_templates - valid_templates,
        'total_errors': total_errors,
        'total_warnings': total_warnings,
        'validation_rate': valid_templates / total_templates if total_templates > 0 else 0
    }