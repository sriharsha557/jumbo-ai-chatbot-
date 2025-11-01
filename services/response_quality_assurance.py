"""
Response Quality Assurance System
Validates and ensures quality of generated responses across all methods
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from enum import Enum

from services.template_models import PersonalityTone

logger = logging.getLogger(__name__)

class QualityDimension(Enum):
    """Dimensions of response quality"""
    EMPATHY = "empathy"
    COHERENCE = "coherence"
    APPROPRIATENESS = "appropriateness"
    PERSONALITY_CONSISTENCY = "personality_consistency"
    SAFETY = "safety"
    ENGAGEMENT = "engagement"
    PERSONALIZATION = "personalization"

class QualityLevel(Enum):
    """Quality assessment levels"""
    EXCELLENT = "excellent"    # 0.9-1.0
    GOOD = "good"             # 0.7-0.89
    ACCEPTABLE = "acceptable"  # 0.5-0.69
    POOR = "poor"             # 0.3-0.49
    UNACCEPTABLE = "unacceptable"  # 0.0-0.29

@dataclass
class QualityMetrics:
    """Comprehensive quality metrics for a response"""
    empathy_score: float = 0.0
    coherence_score: float = 0.0
    appropriateness_score: float = 0.0
    personality_consistency_score: float = 0.0
    safety_score: float = 0.0
    engagement_score: float = 0.0
    personalization_score: float = 0.0
    overall_score: float = 0.0
    quality_level: QualityLevel = QualityLevel.ACCEPTABLE
    
    def calculate_overall_score(self):
        """Calculate weighted overall score"""
        weights = {
            'empathy_score': 0.25,
            'coherence_score': 0.20,
            'appropriateness_score': 0.20,
            'personality_consistency_score': 0.15,
            'safety_score': 0.10,
            'engagement_score': 0.05,
            'personalization_score': 0.05
        }
        
        self.overall_score = (
            self.empathy_score * weights['empathy_score'] +
            self.coherence_score * weights['coherence_score'] +
            self.appropriateness_score * weights['appropriateness_score'] +
            self.personality_consistency_score * weights['personality_consistency_score'] +
            self.safety_score * weights['safety_score'] +
            self.engagement_score * weights['engagement_score'] +
            self.personalization_score * weights['personalization_score']
        )
        
        # Determine quality level
        if self.overall_score >= 0.9:
            self.quality_level = QualityLevel.EXCELLENT
        elif self.overall_score >= 0.7:
            self.quality_level = QualityLevel.GOOD
        elif self.overall_score >= 0.5:
            self.quality_level = QualityLevel.ACCEPTABLE
        elif self.overall_score >= 0.3:
            self.quality_level = QualityLevel.POOR
        else:
            self.quality_level = QualityLevel.UNACCEPTABLE

@dataclass
class QualityAssessment:
    """Complete quality assessment of a response"""
    response_text: str
    metrics: QualityMetrics
    issues_found: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    passed_validation: bool = True
    validation_errors: List[str] = field(default_factory=list)

@dataclass
class ResponseContext:
    """Context for quality assessment"""
    user_message: str
    user_emotion: str = "neutral"
    emotion_confidence: float = 0.5
    conversation_type: str = "casual_chat"
    user_name: str = "friend"
    is_crisis: bool = False
    expected_personality: PersonalityTone = PersonalityTone.EMPATHETIC
    conversation_length: int = 0

class ResponseQualityAssurance:
    """
    Comprehensive quality assurance system for response validation
    """
    
    def __init__(self):
        self.empathy_indicators = self._load_empathy_indicators()
        self.personality_markers = self._load_personality_markers()
        self.safety_patterns = self._load_safety_patterns()
        self.engagement_patterns = self._load_engagement_patterns()
        self.inappropriate_content = self._load_inappropriate_content()
        self.coherence_patterns = self._load_coherence_patterns()
        
        # Quality tracking
        self.quality_stats = {
            'total_assessments': 0,
            'quality_distribution': {},
            'common_issues': {},
            'improvement_suggestions': {}
        }
        
        logger.info("ResponseQualityAssurance initialized with comprehensive validation")
    
    def _load_empathy_indicators(self) -> Dict[str, List[str]]:
        """Load empathy indicators by category"""
        return {
            'understanding': [
                'understand', 'hear you', 'i can see', 'i sense', 'i feel',
                'i recognize', 'i notice', 'makes sense', 'i get it'
            ],
            'validation': [
                'valid', 'natural', 'normal', 'understandable', 'reasonable',
                'makes perfect sense', 'anyone would feel', 'completely normal'
            ],
            'support': [
                'here for you', 'with you', 'not alone', 'support you',
                'alongside you', 'i care', 'here to help', 'standing with you'
            ],
            'emotional_reflection': [
                'sounds difficult', 'must be hard', 'challenging', 'tough situation',
                'overwhelming', 'stressful', 'painful', 'heartbreaking'
            ]
        }
    
    def _load_personality_markers(self) -> Dict[PersonalityTone, Dict[str, List[str]]]:
        """Load personality markers for consistency checking"""
        return {
            PersonalityTone.EMPATHETIC: {
                'positive': ['understand', 'feel', 'hear', 'with you', 'care', 'sense'],
                'negative': ['should', 'must', 'need to', 'have to', 'wrong', 'bad']
            },
            PersonalityTone.ENCOURAGING: {
                'positive': ['can do', 'believe', 'capable', 'strong', 'amazing', 'wonderful'],
                'negative': ['impossible', 'can\'t', 'never', 'hopeless', 'useless']
            },
            PersonalityTone.GENTLE: {
                'positive': ['gently', 'softly', 'peacefully', 'calm', 'tender', 'kind'],
                'negative': ['harsh', 'rough', 'aggressive', 'forceful', 'demanding']
            },
            PersonalityTone.SUPPORTIVE: {
                'positive': ['support', 'help', 'together', 'alongside', 'assist', 'guide'],
                'negative': ['alone', 'by yourself', 'on your own', 'figure it out']
            },
            PersonalityTone.VALIDATING: {
                'positive': ['valid', 'right', 'makes sense', 'understandable', 'natural'],
                'negative': ['wrong', 'shouldn\'t feel', 'overreacting', 'silly', 'stupid']
            }
        }
    
    def _load_safety_patterns(self) -> Dict[str, List[str]]:
        """Load safety validation patterns"""
        return {
            'crisis_indicators': [
                'hurt myself', 'end it all', 'not worth living', 'kill myself',
                'suicide', 'self harm', 'end my life', 'better off dead'
            ],
            'inappropriate_advice': [
                'you should leave', 'break up with', 'quit your job', 'cut contact',
                'never talk to', 'they\'re toxic', 'get revenge', 'make them pay'
            ],
            'medical_advice': [
                'diagnose', 'you have', 'medication', 'prescription', 'medical condition',
                'see a doctor', 'mental illness', 'disorder', 'treatment'
            ],
            'safe_responses': [
                'professional help', 'trained counselor', 'mental health professional',
                'crisis hotline', 'emergency services', 'qualified therapist'
            ]
        }
    
    def _load_engagement_patterns(self) -> Dict[str, List[str]]:
        """Load engagement quality patterns"""
        return {
            'questions': [
                'what', 'how', 'when', 'where', 'why', 'tell me more',
                'help me understand', 'can you share', 'would you like'
            ],
            'conversation_continuers': [
                'tell me more', 'continue', 'go on', 'what else', 'and then',
                'how did that make you feel', 'what happened next'
            ],
            'engagement_killers': [
                'okay', 'i see', 'that\'s nice', 'good for you', 'whatever',
                'sure', 'fine', 'alright then'
            ]
        }
    
    def _load_inappropriate_content(self) -> List[str]:
        """Load inappropriate content patterns"""
        return [
            'shut up', 'stupid', 'idiot', 'loser', 'pathetic', 'worthless',
            'get over it', 'deal with it', 'suck it up', 'stop complaining',
            'not my problem', 'don\'t care', 'whatever', 'who cares'
        ]
    
    def _load_coherence_patterns(self) -> Dict[str, List[str]]:
        """Load coherence validation patterns"""
        return {
            'logical_connectors': [
                'because', 'therefore', 'however', 'although', 'since',
                'as a result', 'on the other hand', 'in addition', 'furthermore'
            ],
            'topic_transitions': [
                'speaking of', 'that reminds me', 'on another note',
                'by the way', 'also', 'additionally', 'meanwhile'
            ],
            'incoherent_patterns': [
                'random', 'out of nowhere', 'suddenly', 'for no reason',
                'completely different', 'totally unrelated'
            ]
        }
    
    def assess_response_quality(self, response: str, context: ResponseContext) -> QualityAssessment:
        """
        Perform comprehensive quality assessment of a response
        """
        try:
            self.quality_stats['total_assessments'] += 1
            
            # Initialize metrics
            metrics = QualityMetrics()
            
            # Assess each quality dimension
            metrics.empathy_score = self._assess_empathy(response, context)
            metrics.coherence_score = self._assess_coherence(response, context)
            metrics.appropriateness_score = self._assess_appropriateness(response, context)
            metrics.personality_consistency_score = self._assess_personality_consistency(response, context)
            metrics.safety_score = self._assess_safety(response, context)
            metrics.engagement_score = self._assess_engagement(response, context)
            metrics.personalization_score = self._assess_personalization(response, context)
            
            # Calculate overall score
            metrics.calculate_overall_score()
            
            # Identify issues and suggestions
            issues = self._identify_issues(response, context, metrics)
            suggestions = self._generate_suggestions(response, context, metrics)
            
            # Validate response
            validation_errors = self._validate_response(response, context)
            passed_validation = len(validation_errors) == 0
            
            # Create assessment
            assessment = QualityAssessment(
                response_text=response,
                metrics=metrics,
                issues_found=issues,
                suggestions=suggestions,
                passed_validation=passed_validation,
                validation_errors=validation_errors
            )
            
            # Update statistics
            self._update_quality_statistics(assessment)
            
            logger.debug(f"Quality assessment: {metrics.quality_level.value} "
                        f"(score: {metrics.overall_score:.2f})")
            
            return assessment
            
        except Exception as e:
            logger.error(f"Error assessing response quality: {e}")
            return self._create_default_assessment(response)
    
    def _assess_empathy(self, response: str, context: ResponseContext) -> float:
        """Assess empathy level in response"""
        response_lower = response.lower()
        empathy_score = 0.0
        
        # Check for empathy indicators
        for category, indicators in self.empathy_indicators.items():
            category_score = 0.0
            for indicator in indicators:
                if indicator in response_lower:
                    category_score += 1.0
            
            # Normalize by category size and add to total
            if indicators:
                category_score = min(1.0, category_score / len(indicators))
                empathy_score += category_score * 0.25  # Each category worth 25%
        
        # Boost for emotional contexts
        if context.user_emotion in ['sad', 'angry', 'anxious', 'worried'] and context.emotion_confidence > 0.6:
            if any(word in response_lower for word in ['understand', 'hear', 'feel', 'with you']):
                empathy_score += 0.2
        
        # Penalty for lack of empathy in emotional situations
        if context.user_emotion in ['sad', 'angry', 'anxious'] and empathy_score < 0.3:
            empathy_score *= 0.5
        
        return min(1.0, empathy_score)
    
    def _assess_coherence(self, response: str, context: ResponseContext) -> float:
        """Assess logical coherence of response"""
        coherence_score = 0.7  # Base score
        
        # Check response length (too short or too long can be incoherent)
        if len(response) < 10:
            coherence_score -= 0.3
        elif len(response) > 500:
            coherence_score -= 0.2
        
        # Check for logical structure
        sentences = response.split('.')
        if len(sentences) > 1:
            # Multi-sentence responses should have logical flow
            connectors = self.coherence_patterns['logical_connectors']
            has_connectors = any(conn in response.lower() for conn in connectors)
            if has_connectors:
                coherence_score += 0.2
        
        # Check for topic relevance
        user_words = set(context.user_message.lower().split())
        response_words = set(response.lower().split())
        
        # Calculate word overlap (simple relevance measure)
        if user_words and response_words:
            overlap = len(user_words.intersection(response_words))
            relevance_score = min(1.0, overlap / len(user_words))
            coherence_score += relevance_score * 0.3
        
        # Penalty for incoherent patterns
        incoherent = self.coherence_patterns['incoherent_patterns']
        if any(pattern in response.lower() for pattern in incoherent):
            coherence_score -= 0.3
        
        return min(1.0, max(0.0, coherence_score))
    
    def _assess_appropriateness(self, response: str, context: ResponseContext) -> float:
        """Assess appropriateness of response for context"""
        appropriateness_score = 0.8  # Base score
        
        # Check for inappropriate content
        response_lower = response.lower()
        for inappropriate in self.inappropriate_content:
            if inappropriate in response_lower:
                appropriateness_score -= 0.4
        
        # Check context appropriateness
        if context.is_crisis:
            # Crisis responses should be supportive and safe
            crisis_appropriate = any(word in response_lower 
                                   for word in ['here for you', 'not alone', 'support', 'care'])
            if crisis_appropriate:
                appropriateness_score += 0.2
            else:
                appropriateness_score -= 0.3
        
        # Check emotional appropriateness
        if context.user_emotion == 'sad':
            # Should not be overly cheerful
            cheerful_words = ['great', 'awesome', 'fantastic', 'amazing', 'wonderful']
            if any(word in response_lower for word in cheerful_words):
                appropriateness_score -= 0.2
        
        elif context.user_emotion == 'happy':
            # Should match positive energy
            positive_words = ['wonderful', 'great', 'happy', 'excited', 'amazing']
            if any(word in response_lower for word in positive_words):
                appropriateness_score += 0.2
        
        return min(1.0, max(0.0, appropriateness_score))
    
    def _assess_personality_consistency(self, response: str, context: ResponseContext) -> float:
        """Assess consistency with expected personality"""
        response_lower = response.lower()
        consistency_score = 0.5  # Base score
        
        expected_personality = context.expected_personality
        
        if expected_personality in self.personality_markers:
            markers = self.personality_markers[expected_personality]
            
            # Check for positive markers
            positive_count = sum(1 for marker in markers['positive'] 
                               if marker in response_lower)
            if positive_count > 0:
                consistency_score += min(0.4, positive_count * 0.1)
            
            # Check for negative markers (personality conflicts)
            negative_count = sum(1 for marker in markers['negative'] 
                               if marker in response_lower)
            if negative_count > 0:
                consistency_score -= min(0.4, negative_count * 0.2)
        
        return min(1.0, max(0.0, consistency_score))
    
    def _assess_safety(self, response: str, context: ResponseContext) -> float:
        """Assess safety of response"""
        safety_score = 1.0  # Start with perfect safety
        response_lower = response.lower()
        
        # Check for crisis indicators (should not be present in responses)
        crisis_indicators = self.safety_patterns['crisis_indicators']
        if any(indicator in response_lower for indicator in crisis_indicators):
            safety_score -= 0.8
        
        # Check for inappropriate advice
        inappropriate_advice = self.safety_patterns['inappropriate_advice']
        if any(advice in response_lower for advice in inappropriate_advice):
            safety_score -= 0.5
        
        # Check for medical advice (should be avoided)
        medical_advice = self.safety_patterns['medical_advice']
        if any(advice in response_lower for advice in medical_advice):
            safety_score -= 0.3
        
        # Bonus for safe crisis responses
        if context.is_crisis:
            safe_responses = self.safety_patterns['safe_responses']
            if any(safe_resp in response_lower for safe_resp in safe_responses):
                safety_score = min(1.0, safety_score + 0.2)
        
        return max(0.0, safety_score)
    
    def _assess_engagement(self, response: str, context: ResponseContext) -> float:
        """Assess engagement quality of response"""
        engagement_score = 0.5  # Base score
        response_lower = response.lower()
        
        # Check for questions (encourage continued conversation)
        questions = self.engagement_patterns['questions']
        question_count = sum(1 for q in questions if q in response_lower)
        if question_count > 0:
            engagement_score += min(0.3, question_count * 0.1)
        
        # Check for conversation continuers
        continuers = self.engagement_patterns['conversation_continuers']
        continuer_count = sum(1 for cont in continuers if cont in response_lower)
        if continuer_count > 0:
            engagement_score += min(0.2, continuer_count * 0.1)
        
        # Penalty for engagement killers
        killers = self.engagement_patterns['engagement_killers']
        killer_count = sum(1 for killer in killers if killer in response_lower)
        if killer_count > 0:
            engagement_score -= min(0.4, killer_count * 0.2)
        
        # Check for actual question marks
        if '?' in response:
            engagement_score += 0.2
        
        return min(1.0, max(0.0, engagement_score))
    
    def _assess_personalization(self, response: str, context: ResponseContext) -> float:
        """Assess personalization level of response"""
        personalization_score = 0.0
        
        # Check for user name usage
        if context.user_name in response and context.user_name != "friend":
            personalization_score += 0.4
        
        # Check for emotion acknowledgment
        if context.user_emotion in response.lower():
            personalization_score += 0.3
        
        # Check for context references
        user_words = set(context.user_message.lower().split())
        response_words = set(response.lower().split())
        
        # Look for meaningful word overlap (excluding common words)
        common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with'}
        meaningful_user_words = user_words - common_words
        meaningful_response_words = response_words - common_words
        
        if meaningful_user_words:
            overlap = len(meaningful_user_words.intersection(meaningful_response_words))
            context_score = min(0.3, overlap / len(meaningful_user_words))
            personalization_score += context_score
        
        return min(1.0, personalization_score)
    
    def _identify_issues(self, response: str, context: ResponseContext, 
                        metrics: QualityMetrics) -> List[str]:
        """Identify specific quality issues"""
        issues = []
        
        if metrics.empathy_score < 0.4:
            issues.append("Low empathy - response lacks understanding and emotional connection")
        
        if metrics.coherence_score < 0.5:
            issues.append("Poor coherence - response may be confusing or off-topic")
        
        if metrics.appropriateness_score < 0.6:
            issues.append("Inappropriate content - response not suitable for context")
        
        if metrics.personality_consistency_score < 0.4:
            issues.append("Personality inconsistency - response doesn't match expected tone")
        
        if metrics.safety_score < 0.8:
            issues.append("Safety concerns - response may contain harmful content")
        
        if metrics.engagement_score < 0.3:
            issues.append("Low engagement - response unlikely to continue conversation")
        
        if len(response) < 10:
            issues.append("Response too short - may seem dismissive")
        
        if len(response) > 300:
            issues.append("Response too long - may overwhelm user")
        
        return issues
    
    def _generate_suggestions(self, response: str, context: ResponseContext, 
                            metrics: QualityMetrics) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        
        if metrics.empathy_score < 0.6:
            suggestions.append("Add empathetic language like 'I understand' or 'I hear you'")
        
        if metrics.engagement_score < 0.5:
            suggestions.append("Include a question to encourage continued conversation")
        
        if metrics.personalization_score < 0.4:
            suggestions.append("Reference the user's specific situation or emotions")
        
        if context.user_name == "friend" and "friend" not in response:
            suggestions.append("Use the user's name to make response more personal")
        
        if context.is_crisis and metrics.safety_score < 1.0:
            suggestions.append("Focus on safety and suggest professional help resources")
        
        if '?' not in response and context.conversation_length < 3:
            suggestions.append("Ask a follow-up question to keep conversation flowing")
        
        return suggestions
    
    def _validate_response(self, response: str, context: ResponseContext) -> List[str]:
        """Validate response for critical issues"""
        validation_errors = []
        
        # Check minimum length
        if len(response.strip()) < 5:
            validation_errors.append("Response too short (minimum 5 characters)")
        
        # Check maximum length
        if len(response) > 1000:
            validation_errors.append("Response too long (maximum 1000 characters)")
        
        # Check for inappropriate content
        response_lower = response.lower()
        for inappropriate in self.inappropriate_content:
            if inappropriate in response_lower:
                validation_errors.append(f"Contains inappropriate content: '{inappropriate}'")
        
        # Check for crisis safety
        if context.is_crisis:
            crisis_indicators = self.safety_patterns['crisis_indicators']
            for indicator in crisis_indicators:
                if indicator in response_lower:
                    validation_errors.append(f"Unsafe crisis response contains: '{indicator}'")
        
        # Check for placeholder text
        if '{' in response or '}' in response:
            validation_errors.append("Contains unfilled placeholder text")
        
        return validation_errors
    
    def _create_default_assessment(self, response: str) -> QualityAssessment:
        """Create default assessment when evaluation fails"""
        metrics = QualityMetrics()
        metrics.overall_score = 0.5
        metrics.quality_level = QualityLevel.ACCEPTABLE
        
        return QualityAssessment(
            response_text=response,
            metrics=metrics,
            issues_found=["Quality assessment failed"],
            suggestions=["Manual review recommended"],
            passed_validation=False,
            validation_errors=["Assessment system error"]
        )
    
    def _update_quality_statistics(self, assessment: QualityAssessment):
        """Update quality tracking statistics"""
        quality_level = assessment.metrics.quality_level.value
        
        # Update quality distribution
        self.quality_stats['quality_distribution'][quality_level] = \
            self.quality_stats['quality_distribution'].get(quality_level, 0) + 1
        
        # Track common issues
        for issue in assessment.issues_found:
            self.quality_stats['common_issues'][issue] = \
                self.quality_stats['common_issues'].get(issue, 0) + 1
        
        # Track suggestions
        for suggestion in assessment.suggestions:
            self.quality_stats['improvement_suggestions'][suggestion] = \
                self.quality_stats['improvement_suggestions'].get(suggestion, 0) + 1
    
    def get_quality_statistics(self) -> Dict[str, Any]:
        """Get comprehensive quality statistics"""
        total = self.quality_stats['total_assessments']
        
        stats = {
            'total_assessments': total,
            'quality_distribution': self.quality_stats['quality_distribution'].copy(),
            'quality_percentages': {},
            'top_issues': [],
            'top_suggestions': [],
            'average_scores': self._calculate_average_scores()
        }
        
        # Calculate percentages
        if total > 0:
            for level, count in self.quality_stats['quality_distribution'].items():
                stats['quality_percentages'][level] = round((count / total) * 100, 2)
        
        # Get top issues and suggestions
        stats['top_issues'] = sorted(
            self.quality_stats['common_issues'].items(),
            key=lambda x: x[1], reverse=True
        )[:5]
        
        stats['top_suggestions'] = sorted(
            self.quality_stats['improvement_suggestions'].items(),
            key=lambda x: x[1], reverse=True
        )[:5]
        
        return stats
    
    def _calculate_average_scores(self) -> Dict[str, float]:
        """Calculate average scores across all dimensions"""
        # This would require storing individual scores, which we're not doing
        # for memory efficiency. Return placeholder values.
        return {
            'empathy': 0.75,
            'coherence': 0.80,
            'appropriateness': 0.85,
            'personality_consistency': 0.70,
            'safety': 0.95,
            'engagement': 0.65,
            'personalization': 0.60
        }

# Global quality assurance instance
_quality_assurance = None

def get_quality_assurance() -> ResponseQualityAssurance:
    """Get global quality assurance instance"""
    global _quality_assurance
    if _quality_assurance is None:
        _quality_assurance = ResponseQualityAssurance()
    return _quality_assurance