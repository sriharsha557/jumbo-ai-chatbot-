"""
Intelligent Template Selection Algorithm
Selects the best conversation template based on emotion, context, and anti-repetition logic
"""

import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import random

from services.template_models import (
    ConversationTemplate, 
    TemplateScore, 
    TemplateSelectionCriteria,
    TemplateUsageTracker,
    ConversationType,
    PersonalityTone
)
from services.template_loader import get_template_loader

logger = logging.getLogger(__name__)

@dataclass
class SelectionContext:
    """Context information for template selection"""
    user_id: str
    emotion: str
    emotion_confidence: float
    conversation_type: ConversationType
    available_context: List[str]
    recent_template_ids: List[str] = None  # Recently used templates to avoid
    personality_preference: Optional[PersonalityTone] = None
    conversation_length: int = 0  # Number of exchanges in current conversation
    time_of_day: Optional[str] = None  # morning, afternoon, evening, night

class IntelligentTemplateSelector:
    """
    Advanced template selection with emotion matching, context awareness, and anti-repetition
    """
    
    def __init__(self):
        self.template_loader = get_template_loader()
        self.usage_trackers: Dict[str, TemplateUsageTracker] = {}
        
        # Scoring weights for different factors
        self.weights = {
            'emotion_match': 0.35,
            'context_match': 0.25,
            'anti_repetition': 0.25,
            'personality_match': 0.10,
            'conversation_flow': 0.05
        }
    
    def select_best_template(self, selection_context: SelectionContext) -> Optional[ConversationTemplate]:
        """
        Select the best template based on comprehensive scoring
        """
        try:
            # Get candidate templates
            candidates = self._get_candidate_templates(selection_context)
            
            if not candidates:
                logger.warning(f"No candidate templates found for emotion: {selection_context.emotion}, "
                             f"type: {selection_context.conversation_type}")
                return self._get_fallback_template(selection_context)
            
            # Score all candidates
            scored_templates = self._score_templates(candidates, selection_context)
            
            if not scored_templates:
                logger.warning("No templates received scores")
                return self._get_fallback_template(selection_context)
            
            # Select best template with some randomization to avoid predictability
            selected_template = self._select_from_scored_templates(scored_templates, selection_context)
            
            # Record usage for anti-repetition
            if selected_template:
                self._record_template_usage(selection_context.user_id, selected_template.id)
                logger.info(f"Selected template: {selected_template.id} for user: {selection_context.user_id}")
            
            return selected_template
            
        except Exception as e:
            logger.error(f"Error in template selection: {e}")
            return self._get_fallback_template(selection_context)
    
    def _get_candidate_templates(self, context: SelectionContext) -> List[ConversationTemplate]:
        """Get candidate templates based on emotion and conversation type"""
        candidates = []
        
        # Primary: Get templates matching both emotion and conversation type
        emotion_type_matches = self.template_loader.get_templates_by_emotion_and_type(
            context.emotion, context.conversation_type
        )
        candidates.extend(emotion_type_matches)
        
        # Secondary: Get templates matching just emotion (if different conversation type)
        if len(candidates) < 3:  # Need more options
            emotion_matches = self.template_loader.get_templates_by_emotion(context.emotion)
            for template in emotion_matches:
                if template not in candidates:
                    candidates.append(template)
        
        # Tertiary: Get templates matching just conversation type (if different emotion)
        if len(candidates) < 2:  # Still need more options
            type_matches = self.template_loader.get_templates_by_type(context.conversation_type)
            for template in type_matches:
                if template not in candidates:
                    candidates.append(template)
        
        # Filter by minimum confidence
        candidates = [
            template for template in candidates 
            if context.emotion_confidence >= template.min_confidence
        ]
        
        logger.debug(f"Found {len(candidates)} candidate templates for {context.emotion}/{context.conversation_type}")
        return candidates
    
    def _score_templates(self, candidates: List[ConversationTemplate], 
                        context: SelectionContext) -> List[Tuple[ConversationTemplate, TemplateScore]]:
        """Score all candidate templates"""
        scored_templates = []
        
        for template in candidates:
            score = self._calculate_template_score(template, context)
            scored_templates.append((template, score))
        
        # Sort by total score (descending)
        scored_templates.sort(key=lambda x: x[1].total_score, reverse=True)
        
        return scored_templates
    
    def _calculate_template_score(self, template: ConversationTemplate, 
                                 context: SelectionContext) -> TemplateScore:
        """Calculate comprehensive score for a template"""
        score = TemplateScore(template_id=template.id)
        
        # 1. Emotion Match Score
        score.emotion_match_score = self._calculate_emotion_match_score(template, context)
        
        # 2. Context Match Score
        score.context_match_score = self._calculate_context_match_score(template, context)
        
        # 3. Anti-Repetition Score
        score.anti_repetition_score = self._calculate_anti_repetition_score(template, context)
        
        # 4. Personality Match Score
        score.personality_match_score = self._calculate_personality_match_score(template, context)
        
        # Calculate weighted total score
        score.total_score = (
            score.emotion_match_score * self.weights['emotion_match'] +
            score.context_match_score * self.weights['context_match'] +
            score.anti_repetition_score * self.weights['anti_repetition'] +
            score.personality_match_score * self.weights['personality_match']
        )
        
        # Add conversation flow bonus
        flow_bonus = self._calculate_conversation_flow_bonus(template, context)
        score.total_score += flow_bonus * self.weights['conversation_flow']
        
        return score
    
    def _calculate_emotion_match_score(self, template: ConversationTemplate, 
                                     context: SelectionContext) -> float:
        """Calculate how well template matches the detected emotion"""
        if context.emotion.lower() in [tag.lower() for tag in template.emotion_tags]:
            # Perfect match
            base_score = 1.0
        else:
            # Check for related emotions
            emotion_similarity = self._get_emotion_similarity(context.emotion, template.emotion_tags)
            base_score = emotion_similarity
        
        # Adjust by confidence
        confidence_factor = min(context.emotion_confidence, 1.0)
        
        # Boost score if conversation type also matches
        type_bonus = 0.2 if template.conversation_type == context.conversation_type else 0
        
        return min(base_score * confidence_factor + type_bonus, 1.0)
    
    def _calculate_context_match_score(self, template: ConversationTemplate, 
                                     context: SelectionContext) -> float:
        """Calculate how well available context matches template requirements"""
        if not template.context_requirements:
            return 1.0  # No requirements = perfect match
        
        available_context_set = set(context.available_context)
        required_context_set = set(template.context_requirements)
        
        if required_context_set.issubset(available_context_set):
            return 1.0  # All requirements met
        
        # Partial match scoring
        matched_requirements = len(required_context_set.intersection(available_context_set))
        total_requirements = len(required_context_set)
        
        return matched_requirements / total_requirements if total_requirements > 0 else 0.0
    
    def _calculate_anti_repetition_score(self, template: ConversationTemplate, 
                                       context: SelectionContext) -> float:
        """Calculate score to avoid repetitive template usage"""
        usage_tracker = self._get_usage_tracker(context.user_id)
        return usage_tracker.calculate_anti_repetition_score(template.id)
    
    def _calculate_personality_match_score(self, template: ConversationTemplate, 
                                         context: SelectionContext) -> float:
        """Calculate personality tone match score"""
        if not context.personality_preference:
            return 0.5  # Neutral score if no preference
        
        if template.personality_tone == context.personality_preference:
            return 1.0
        
        # Check for compatible personality tones
        compatibility_map = {
            PersonalityTone.EMPATHETIC: [PersonalityTone.SUPPORTIVE, PersonalityTone.VALIDATING],
            PersonalityTone.GENTLE: [PersonalityTone.CALMING, PersonalityTone.SUPPORTIVE],
            PersonalityTone.ENCOURAGING: [PersonalityTone.SUPPORTIVE, PersonalityTone.EMPATHETIC],
            PersonalityTone.CURIOUS: [PersonalityTone.GENTLE, PersonalityTone.EMPATHETIC]
        }
        
        compatible_tones = compatibility_map.get(context.personality_preference, [])
        if template.personality_tone in compatible_tones:
            return 0.7
        
        return 0.3  # Low but not zero for non-matching tones
    
    def _calculate_conversation_flow_bonus(self, template: ConversationTemplate, 
                                         context: SelectionContext) -> float:
        """Calculate bonus for conversation flow considerations"""
        bonus = 0.0
        
        # Bonus for templates with follow-up questions in longer conversations
        if context.conversation_length > 3 and template.follow_up_questions:
            bonus += 0.3
        
        # Bonus for greeting templates at conversation start
        if context.conversation_length == 0 and template.conversation_type == ConversationType.GREETING:
            bonus += 0.5
        
        # Time-of-day considerations (if available)
        if context.time_of_day:
            if context.time_of_day in ['evening', 'night'] and 'calm' in template.base_template.lower():
                bonus += 0.2
            elif context.time_of_day == 'morning' and any(word in template.base_template.lower() 
                                                        for word in ['energy', 'fresh', 'new']):
                bonus += 0.2
        
        return min(bonus, 1.0)
    
    def _select_from_scored_templates(self, scored_templates: List[Tuple[ConversationTemplate, TemplateScore]], 
                                    context: SelectionContext) -> Optional[ConversationTemplate]:
        """Select template from scored list with controlled randomization"""
        if not scored_templates:
            return None
        
        # Get top candidates (within 20% of best score)
        best_score = scored_templates[0][1].total_score
        threshold = best_score * 0.8
        
        top_candidates = [
            (template, score) for template, score in scored_templates 
            if score.total_score >= threshold
        ]
        
        # Weighted random selection from top candidates
        if len(top_candidates) == 1:
            return top_candidates[0][0]
        
        # Create weighted list (higher scores more likely to be selected)
        weighted_candidates = []
        for template, score in top_candidates:
            weight = int(score.total_score * 100)  # Convert to integer weight
            weighted_candidates.extend([template] * max(1, weight))
        
        return random.choice(weighted_candidates)
    
    def _get_emotion_similarity(self, target_emotion: str, template_emotions: List[str]) -> float:
        """Calculate similarity between target emotion and template emotions"""
        # Emotion similarity mapping
        emotion_groups = {
            'sad': ['depressed', 'down', 'upset', 'melancholy'],
            'happy': ['joyful', 'excited', 'cheerful', 'elated'],
            'angry': ['mad', 'furious', 'irritated', 'annoyed'],
            'anxious': ['worried', 'nervous', 'stressed', 'tense'],
            'confused': ['uncertain', 'lost', 'puzzled', 'unclear'],
            'tired': ['exhausted', 'drained', 'weary', 'fatigued']
        }
        
        target_lower = target_emotion.lower()
        template_emotions_lower = [emotion.lower() for emotion in template_emotions]
        
        # Check for direct similarity
        for emotion_group, similar_emotions in emotion_groups.items():
            if target_lower in similar_emotions or target_lower == emotion_group:
                for template_emotion in template_emotions_lower:
                    if template_emotion in similar_emotions or template_emotion == emotion_group:
                        return 0.8  # High similarity
        
        # Check for neutral compatibility
        if target_lower == 'neutral' or 'neutral' in template_emotions_lower:
            return 0.5
        
        return 0.2  # Low similarity
    
    def _get_usage_tracker(self, user_id: str) -> TemplateUsageTracker:
        """Get or create usage tracker for user"""
        if user_id not in self.usage_trackers:
            self.usage_trackers[user_id] = TemplateUsageTracker(user_id=user_id)
        return self.usage_trackers[user_id]
    
    def _record_template_usage(self, user_id: str, template_id: str):
        """Record template usage for anti-repetition tracking"""
        usage_tracker = self._get_usage_tracker(user_id)
        usage_tracker.record_usage(template_id)
    
    def _get_fallback_template(self, context: SelectionContext) -> Optional[ConversationTemplate]:
        """Get a fallback template when no good matches are found"""
        # Try to get any template matching the conversation type
        type_templates = self.template_loader.get_templates_by_type(context.conversation_type)
        if type_templates:
            return random.choice(type_templates)
        
        # Try to get any template matching the emotion
        emotion_templates = self.template_loader.get_templates_by_emotion(context.emotion)
        if emotion_templates:
            return random.choice(emotion_templates)
        
        # Last resort: get any template
        all_templates = self.template_loader.get_all_templates()
        if all_templates:
            return random.choice(list(all_templates.values()))
        
        logger.error("No fallback templates available")
        return None
    
    def get_selection_stats(self, user_id: str) -> Dict[str, any]:
        """Get template selection statistics for a user"""
        usage_tracker = self._get_usage_tracker(user_id)
        
        stats = {
            'total_selections': sum(len(usages) for usages in usage_tracker.template_usage.values()),
            'unique_templates_used': len(usage_tracker.template_usage),
            'most_used_templates': [],
            'recent_selections': []
        }
        
        # Calculate most used templates
        template_counts = {
            template_id: len(usages) 
            for template_id, usages in usage_tracker.template_usage.items()
        }
        
        sorted_templates = sorted(template_counts.items(), key=lambda x: x[1], reverse=True)
        stats['most_used_templates'] = sorted_templates[:5]
        
        # Get recent selections (last 24 hours)
        cutoff_time = datetime.now() - timedelta(hours=24)
        for template_id, usages in usage_tracker.template_usage.items():
            recent_usages = [usage for usage in usages if usage > cutoff_time]
            if recent_usages:
                stats['recent_selections'].append({
                    'template_id': template_id,
                    'count': len(recent_usages),
                    'last_used': max(recent_usages).isoformat()
                })
        
        return stats

# Global selector instance
_template_selector = None

def get_template_selector() -> IntelligentTemplateSelector:
    """Get global template selector instance"""
    global _template_selector
    if _template_selector is None:
        _template_selector = IntelligentTemplateSelector()
    return _template_selector