"""
Entity Extraction for Personalization
Extracts names, topics, relationships, and emotional cues from user messages
"""

import re
import logging
from typing import Dict, List, Tuple, Optional, Set, Any
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

class EntityType(Enum):
    """Types of entities that can be extracted"""
    PERSON_NAME = "person_name"
    RELATIONSHIP = "relationship"
    EMOTION_CUE = "emotion_cue"
    TOPIC = "topic"
    LOCATION = "location"
    TIME_REFERENCE = "time_reference"
    ACTIVITY = "activity"
    PREFERENCE = "preference"
    GOAL = "goal"
    CONCERN = "concern"

@dataclass
class ExtractedEntity:
    """An extracted entity with metadata"""
    text: str
    entity_type: EntityType
    confidence: float
    context: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    start_position: int = -1
    end_position: int = -1

@dataclass
class EntityExtractionResult:
    """Result of entity extraction"""
    entities: List[ExtractedEntity] = field(default_factory=list)
    person_names: List[str] = field(default_factory=list)
    relationships: Dict[str, str] = field(default_factory=dict)  # name -> relationship
    topics: List[str] = field(default_factory=list)
    emotional_cues: List[str] = field(default_factory=list)
    preferences: List[str] = field(default_factory=list)
    activities: List[str] = field(default_factory=list)
    locations: List[str] = field(default_factory=list)
    time_references: List[str] = field(default_factory=list)

class EntityExtractor:
    """
    Extracts entities from user messages for personalization
    """
    
    def __init__(self):
        self.name_patterns = self._load_name_patterns()
        self.relationship_patterns = self._load_relationship_patterns()
        self.emotion_cue_patterns = self._load_emotion_cue_patterns()
        self.topic_keywords = self._load_topic_keywords()
        self.preference_patterns = self._load_preference_patterns()
        self.activity_patterns = self._load_activity_patterns()
        self.location_patterns = self._load_location_patterns()
        self.time_patterns = self._load_time_patterns()
        
        # Common words to exclude from name extraction
        self.common_words = self._load_common_words()
        
        # Extraction statistics
        self.extraction_stats = {
            'total_extractions': 0,
            'entities_by_type': {},
            'high_confidence_extractions': 0
        }
        
        logger.info("EntityExtractor initialized with pattern-based extraction")
    
    def _load_name_patterns(self) -> List[Dict]:
        """Load patterns for extracting person names"""
        return [
            {
                'pattern': r'\b(?:my|our) (?:friend|buddy|pal) ([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
                'confidence': 0.9,
                'relationship': 'friend'
            },
            {
                'pattern': r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?) (?:is|was) (?:my|our)',
                'confidence': 0.8,
                'relationship': 'unknown'
            },
            {
                'pattern': r'\bwith ([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
                'confidence': 0.7,
                'relationship': 'unknown'
            },
            {
                'pattern': r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?) (?:said|told|asked|mentioned)',
                'confidence': 0.8,
                'relationship': 'unknown'
            },
            {
                'pattern': r'\btold ([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
                'confidence': 0.7,
                'relationship': 'unknown'
            },
            {
                'pattern': r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?) and (?:I|me)',
                'confidence': 0.8,
                'relationship': 'unknown'
            }
        ]
    
    def _load_relationship_patterns(self) -> Dict[str, List[str]]:
        """Load patterns for relationship extraction"""
        return {
            'family': [
                r'my (?:mom|mother|dad|father|parent)s? ([A-Z][a-z]+)',
                r'my (?:brother|sister|sibling) ([A-Z][a-z]+)',
                r'my (?:son|daughter|child) ([A-Z][a-z]+)',
                r'my (?:grandmother|grandfather|grandma|grandpa) ([A-Z][a-z]+)',
                r'my (?:aunt|uncle|cousin) ([A-Z][a-z]+)'
            ],
            'romantic': [
                r'my (?:boyfriend|girlfriend|partner|spouse|husband|wife) ([A-Z][a-z]+)',
                r'my (?:fiance|fiancee) ([A-Z][a-z]+)',
                r'(?:dating|seeing|with) ([A-Z][a-z]+)'
            ],
            'friend': [
                r'my (?:friend|buddy|pal|bestie|bff) ([A-Z][a-z]+)',
                r'my (?:best friend|close friend) ([A-Z][a-z]+)',
                r'friends with ([A-Z][a-z]+)'
            ],
            'professional': [
                r'my (?:boss|manager|supervisor) ([A-Z][a-z]+)',
                r'my (?:colleague|coworker|teammate) ([A-Z][a-z]+)',
                r'my (?:doctor|therapist|teacher|professor) ([A-Z][a-z]+)'
            ],
            'acquaintance': [
                r'(?:know|met) ([A-Z][a-z]+)',
                r'someone (?:named|called) ([A-Z][a-z]+)',
                r'this (?:person|guy|girl) ([A-Z][a-z]+)'
            ]
        }
    
    def _load_emotion_cue_patterns(self) -> List[Dict]:
        """Load patterns for emotional cue extraction"""
        return [
            {
                'pattern': r'feeling (\w+)',
                'confidence': 0.9,
                'context': 'direct_emotion'
            },
            {
                'pattern': r'(?:i am|i\'m) (?:so |really |very )?(\w+)',
                'confidence': 0.8,
                'context': 'state_description'
            },
            {
                'pattern': r'makes me (?:feel )?(\w+)',
                'confidence': 0.8,
                'context': 'causal_emotion'
            },
            {
                'pattern': r'(?:getting|becoming) (\w+)',
                'confidence': 0.7,
                'context': 'emotion_change'
            },
            {
                'pattern': r'(?:sound|seem|look) (\w+)',
                'confidence': 0.6,
                'context': 'perceived_emotion'
            }
        ]
    
    def _load_topic_keywords(self) -> Dict[str, List[str]]:
        """Load topic-specific keywords"""
        return {
            'work': [
                'job', 'work', 'office', 'career', 'employment', 'workplace',
                'boss', 'manager', 'colleague', 'coworker', 'meeting', 'project',
                'deadline', 'promotion', 'salary', 'interview', 'resume'
            ],
            'relationships': [
                'relationship', 'dating', 'marriage', 'friendship', 'family',
                'love', 'romance', 'breakup', 'argument', 'conflict', 'bond'
            ],
            'health': [
                'health', 'doctor', 'hospital', 'medicine', 'therapy', 'treatment',
                'illness', 'disease', 'pain', 'mental health', 'wellness'
            ],
            'education': [
                'school', 'college', 'university', 'education', 'learning',
                'student', 'teacher', 'class', 'exam', 'grade', 'homework'
            ],
            'hobbies': [
                'hobby', 'interest', 'passion', 'music', 'sports', 'reading',
                'cooking', 'travel', 'movies', 'games', 'art', 'exercise'
            ],
            'finance': [
                'money', 'budget', 'savings', 'debt', 'loan', 'investment',
                'bank', 'credit', 'financial', 'income', 'expense'
            ]
        }
    
    def _load_preference_patterns(self) -> List[Dict]:
        """Load patterns for preference extraction"""
        return [
            {
                'pattern': r'i (?:love|like|enjoy|prefer) ([^.!?]+)',
                'confidence': 0.9,
                'preference_type': 'positive'
            },
            {
                'pattern': r'my favorite ([^.!?]+) is ([^.!?]+)',
                'confidence': 0.9,
                'preference_type': 'favorite'
            },
            {
                'pattern': r'i (?:hate|dislike|don\'t like) ([^.!?]+)',
                'confidence': 0.8,
                'preference_type': 'negative'
            },
            {
                'pattern': r'(?:really into|passionate about|obsessed with) ([^.!?]+)',
                'confidence': 0.8,
                'preference_type': 'strong_positive'
            },
            {
                'pattern': r'(?:can\'t stand|avoid|stay away from) ([^.!?]+)',
                'confidence': 0.8,
                'preference_type': 'strong_negative'
            }
        ]
    
    def _load_activity_patterns(self) -> List[str]:
        """Load patterns for activity extraction"""
        return [
            r'(?:going to|planning to|want to|need to) ([^.!?]+)',
            r'(?:just|recently) (\w+ed) ([^.!?]+)',
            r'(?:will|gonna|going to) (\w+) ([^.!?]+)',
            r'(?:started|began|finished) (\w+ing) ([^.!?]+)',
            r'(?:love|enjoy|like) (\w+ing) ([^.!?]*)'
        ]
    
    def _load_location_patterns(self) -> List[str]:
        """Load patterns for location extraction"""
        return [
            r'(?:in|at|from|to) ([A-Z][a-z]+(?: [A-Z][a-z]+)*)',
            r'(?:live|work|study) in ([A-Z][a-z]+(?: [A-Z][a-z]+)*)',
            r'(?:going to|visiting|traveling to) ([A-Z][a-z]+(?: [A-Z][a-z]+)*)',
            r'(?:born|raised) in ([A-Z][a-z]+(?: [A-Z][a-z]+)*)'
        ]
    
    def _load_time_patterns(self) -> List[str]:
        """Load patterns for time reference extraction"""
        return [
            r'(?:yesterday|today|tomorrow)',
            r'(?:last|next) (?:week|month|year|weekend)',
            r'(?:this) (?:morning|afternoon|evening|week|month)',
            r'(?:in) (?:a few days|a week|a month)',
            r'(?:\d+) (?:days?|weeks?|months?|years?) (?:ago|from now)',
            r'(?:recently|lately|soon|eventually)'
        ]
    
    def _load_common_words(self) -> Set[str]:
        """Load common words to exclude from name extraction"""
        return {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before',
            'after', 'above', 'below', 'between', 'among', 'this', 'that', 'these',
            'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him',
            'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their',
            'myself', 'yourself', 'himself', 'herself', 'itself', 'ourselves',
            'yourselves', 'themselves', 'what', 'which', 'who', 'whom', 'whose',
            'where', 'when', 'why', 'how', 'all', 'any', 'both', 'each', 'few',
            'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only',
            'own', 'same', 'so', 'than', 'too', 'very', 'can', 'will', 'just',
            'should', 'now', 'good', 'bad', 'big', 'small', 'new', 'old', 'first',
            'last', 'long', 'great', 'little', 'right', 'wrong', 'high', 'low'
        }
    
    def extract_entities(self, text: str, context: Dict = None) -> EntityExtractionResult:
        """
        Extract all entities from text
        """
        try:
            self.extraction_stats['total_extractions'] += 1
            
            result = EntityExtractionResult()
            
            # Extract different types of entities
            person_entities = self._extract_person_names(text)
            relationship_entities = self._extract_relationships(text)
            emotion_entities = self._extract_emotion_cues(text)
            topic_entities = self._extract_topics(text)
            preference_entities = self._extract_preferences(text)
            activity_entities = self._extract_activities(text)
            location_entities = self._extract_locations(text)
            time_entities = self._extract_time_references(text)
            
            # Combine all entities
            all_entities = (person_entities + relationship_entities + emotion_entities +
                          topic_entities + preference_entities + activity_entities +
                          location_entities + time_entities)
            
            # Sort by confidence and remove duplicates
            all_entities = self._deduplicate_entities(all_entities)
            result.entities = sorted(all_entities, key=lambda x: x.confidence, reverse=True)
            
            # Populate specific lists
            result.person_names = [e.text for e in person_entities]
            result.relationships = self._build_relationship_dict(relationship_entities)
            result.topics = [e.text for e in topic_entities]
            result.emotional_cues = [e.text for e in emotion_entities]
            result.preferences = [e.text for e in preference_entities]
            result.activities = [e.text for e in activity_entities]
            result.locations = [e.text for e in location_entities]
            result.time_references = [e.text for e in time_entities]
            
            # Update statistics
            self._update_statistics(result)
            
            logger.debug(f"Extracted {len(result.entities)} entities from text")
            return result
            
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return EntityExtractionResult()
    
    def _extract_person_names(self, text: str) -> List[ExtractedEntity]:
        """Extract person names from text"""
        entities = []
        
        for pattern_info in self.name_patterns:
            pattern = pattern_info['pattern']
            confidence = pattern_info['confidence']
            relationship = pattern_info.get('relationship', 'unknown')
            
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                name = match.group(1).strip()
                
                # Validate name
                if self._is_valid_name(name):
                    entity = ExtractedEntity(
                        text=name,
                        entity_type=EntityType.PERSON_NAME,
                        confidence=confidence,
                        context=match.group(0),
                        metadata={'relationship': relationship},
                        start_position=match.start(1),
                        end_position=match.end(1)
                    )
                    entities.append(entity)
        
        return entities
    
    def _extract_relationships(self, text: str) -> List[ExtractedEntity]:
        """Extract relationship information from text"""
        entities = []
        
        for relationship_type, patterns in self.relationship_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    name = match.group(1).strip()
                    
                    if self._is_valid_name(name):
                        entity = ExtractedEntity(
                            text=name,
                            entity_type=EntityType.RELATIONSHIP,
                            confidence=0.9,
                            context=match.group(0),
                            metadata={'relationship_type': relationship_type},
                            start_position=match.start(1),
                            end_position=match.end(1)
                        )
                        entities.append(entity)
        
        return entities
    
    def _extract_emotion_cues(self, text: str) -> List[ExtractedEntity]:
        """Extract emotional cues from text"""
        entities = []
        
        for pattern_info in self.emotion_cue_patterns:
            pattern = pattern_info['pattern']
            confidence = pattern_info['confidence']
            context_type = pattern_info['context']
            
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                emotion_word = match.group(1).strip().lower()
                
                # Validate emotion word
                if self._is_valid_emotion_word(emotion_word):
                    entity = ExtractedEntity(
                        text=emotion_word,
                        entity_type=EntityType.EMOTION_CUE,
                        confidence=confidence,
                        context=match.group(0),
                        metadata={'context_type': context_type},
                        start_position=match.start(1),
                        end_position=match.end(1)
                    )
                    entities.append(entity)
        
        return entities
    
    def _extract_topics(self, text: str) -> List[ExtractedEntity]:
        """Extract topic keywords from text"""
        entities = []
        text_lower = text.lower()
        
        for topic, keywords in self.topic_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # Find position
                    start_pos = text_lower.find(keyword)
                    end_pos = start_pos + len(keyword)
                    
                    entity = ExtractedEntity(
                        text=keyword,
                        entity_type=EntityType.TOPIC,
                        confidence=0.7,
                        context=topic,
                        metadata={'topic_category': topic},
                        start_position=start_pos,
                        end_position=end_pos
                    )
                    entities.append(entity)
        
        return entities
    
    def _extract_preferences(self, text: str) -> List[ExtractedEntity]:
        """Extract user preferences from text"""
        entities = []
        
        for pattern_info in self.preference_patterns:
            pattern = pattern_info['pattern']
            confidence = pattern_info['confidence']
            pref_type = pattern_info['preference_type']
            
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                preference = match.group(1).strip()
                
                # Clean and validate preference
                preference = self._clean_preference_text(preference)
                if preference and len(preference) > 2:
                    entity = ExtractedEntity(
                        text=preference,
                        entity_type=EntityType.PREFERENCE,
                        confidence=confidence,
                        context=match.group(0),
                        metadata={'preference_type': pref_type},
                        start_position=match.start(1),
                        end_position=match.end(1)
                    )
                    entities.append(entity)
        
        return entities
    
    def _extract_activities(self, text: str) -> List[ExtractedEntity]:
        """Extract activities from text"""
        entities = []
        
        for pattern in self.activity_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                activity = match.group(0).strip()
                
                # Clean activity text
                activity = self._clean_activity_text(activity)
                if activity and len(activity) > 3:
                    entity = ExtractedEntity(
                        text=activity,
                        entity_type=EntityType.ACTIVITY,
                        confidence=0.6,
                        context=match.group(0),
                        start_position=match.start(),
                        end_position=match.end()
                    )
                    entities.append(entity)
        
        return entities
    
    def _extract_locations(self, text: str) -> List[ExtractedEntity]:
        """Extract location references from text"""
        entities = []
        
        for pattern in self.location_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                location = match.group(1).strip()
                
                # Validate location
                if self._is_valid_location(location):
                    entity = ExtractedEntity(
                        text=location,
                        entity_type=EntityType.LOCATION,
                        confidence=0.7,
                        context=match.group(0),
                        start_position=match.start(1),
                        end_position=match.end(1)
                    )
                    entities.append(entity)
        
        return entities
    
    def _extract_time_references(self, text: str) -> List[ExtractedEntity]:
        """Extract time references from text"""
        entities = []
        text_lower = text.lower()
        
        for pattern in self.time_patterns:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                time_ref = match.group(0).strip()
                
                entity = ExtractedEntity(
                    text=time_ref,
                    entity_type=EntityType.TIME_REFERENCE,
                    confidence=0.8,
                    context=match.group(0),
                    start_position=match.start(),
                    end_position=match.end()
                )
                entities.append(entity)
        
        return entities
    
    def _is_valid_name(self, name: str) -> bool:
        """Validate if extracted text is a valid name"""
        if not name or len(name) < 2:
            return False
        
        # Check if it's a common word
        if name.lower() in self.common_words:
            return False
        
        # Check if it contains only letters and spaces
        if not re.match(r'^[A-Za-z\s]+$', name):
            return False
        
        # Check if it starts with capital letter
        if not name[0].isupper():
            return False
        
        return True
    
    def _is_valid_emotion_word(self, word: str) -> bool:
        """Validate if word is a valid emotion"""
        # Basic validation - should be alphabetic and reasonable length
        return (word.isalpha() and 
                2 <= len(word) <= 20 and 
                word not in self.common_words)
    
    def _is_valid_location(self, location: str) -> bool:
        """Validate if text is a valid location"""
        if not location or len(location) < 2:
            return False
        
        # Should start with capital letter and contain only letters/spaces
        return (location[0].isupper() and 
                re.match(r'^[A-Za-z\s]+$', location) and
                location.lower() not in self.common_words)
    
    def _clean_preference_text(self, text: str) -> str:
        """Clean preference text"""
        # Remove common prefixes/suffixes
        text = re.sub(r'^(to|the|a|an)\s+', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s+(too|also|as well)$', '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def _clean_activity_text(self, text: str) -> str:
        """Clean activity text"""
        # Remove common prefixes
        text = re.sub(r'^(going to|planning to|want to|need to)\s+', '', text, flags=re.IGNORECASE)
        text = re.sub(r'^(will|gonna)\s+', '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def _deduplicate_entities(self, entities: List[ExtractedEntity]) -> List[ExtractedEntity]:
        """Remove duplicate entities"""
        seen = set()
        deduplicated = []
        
        for entity in entities:
            # Create a key based on text and type
            key = (entity.text.lower(), entity.entity_type)
            
            if key not in seen:
                seen.add(key)
                deduplicated.append(entity)
            else:
                # If duplicate, keep the one with higher confidence
                existing_idx = next(
                    i for i, e in enumerate(deduplicated) 
                    if (e.text.lower(), e.entity_type) == key
                )
                if entity.confidence > deduplicated[existing_idx].confidence:
                    deduplicated[existing_idx] = entity
        
        return deduplicated
    
    def _build_relationship_dict(self, relationship_entities: List[ExtractedEntity]) -> Dict[str, str]:
        """Build relationship dictionary from entities"""
        relationships = {}
        
        for entity in relationship_entities:
            name = entity.text
            rel_type = entity.metadata.get('relationship_type', 'unknown')
            relationships[name] = rel_type
        
        return relationships
    
    def _update_statistics(self, result: EntityExtractionResult):
        """Update extraction statistics"""
        total_entities = len(result.entities)
        high_confidence = sum(1 for e in result.entities if e.confidence >= 0.8)
        
        if high_confidence > 0:
            self.extraction_stats['high_confidence_extractions'] += 1
        
        # Update entity type distribution
        for entity in result.entities:
            entity_type = entity.entity_type.value
            self.extraction_stats['entities_by_type'][entity_type] = \
                self.extraction_stats['entities_by_type'].get(entity_type, 0) + 1
    
    def get_extraction_stats(self) -> Dict[str, Any]:
        """Get extraction statistics"""
        total = self.extraction_stats['total_extractions']
        high_conf_rate = (
            self.extraction_stats['high_confidence_extractions'] / total * 100
            if total > 0 else 0
        )
        
        return {
            'total_extractions': total,
            'high_confidence_rate': round(high_conf_rate, 2),
            'entities_by_type': self.extraction_stats['entities_by_type'].copy(),
            'supported_entity_types': [t.value for t in EntityType]
        }
    
    def reset_stats(self):
        """Reset extraction statistics"""
        self.extraction_stats = {
            'total_extractions': 0,
            'entities_by_type': {},
            'high_confidence_extractions': 0
        }

# Global entity extractor instance
_entity_extractor = None

def get_entity_extractor() -> EntityExtractor:
    """Get global entity extractor instance"""
    global _entity_extractor
    if _entity_extractor is None:
        _entity_extractor = EntityExtractor()
    return _entity_extractor