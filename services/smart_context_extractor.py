"""
Smart Context Extractor for Enhanced Conversation System
Efficiently extracts and caches user context with minimal database queries
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

@dataclass
class UserContext:
    """Comprehensive user context for personalized responses"""
    user_id: str
    preferred_name: str
    recent_emotions: List[str] = field(default_factory=list)
    key_relationships: Dict[str, str] = field(default_factory=dict)  # name -> relationship
    conversation_history: List[Dict] = field(default_factory=list)  # Limited to last 5
    preferences: Dict[str, Any] = field(default_factory=dict)
    recent_memories: List[Dict] = field(default_factory=list)
    mood_patterns: Dict[str, Any] = field(default_factory=dict)
    session_metadata: Dict[str, Any] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for caching"""
        return {
            'user_id': self.user_id,
            'preferred_name': self.preferred_name,
            'recent_emotions': self.recent_emotions,
            'key_relationships': self.key_relationships,
            'conversation_history': self.conversation_history,
            'preferences': self.preferences,
            'recent_memories': self.recent_memories,
            'mood_patterns': self.mood_patterns,
            'session_metadata': self.session_metadata,
            'last_updated': self.last_updated.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserContext':
        """Create from dictionary"""
        context = cls(
            user_id=data['user_id'],
            preferred_name=data['preferred_name'],
            recent_emotions=data.get('recent_emotions', []),
            key_relationships=data.get('key_relationships', {}),
            conversation_history=data.get('conversation_history', []),
            preferences=data.get('preferences', {}),
            recent_memories=data.get('recent_memories', []),
            mood_patterns=data.get('mood_patterns', {}),
            session_metadata=data.get('session_metadata', {})
        )
        
        # Parse last_updated
        if 'last_updated' in data:
            try:
                context.last_updated = datetime.fromisoformat(data['last_updated'])
            except (ValueError, TypeError):
                context.last_updated = datetime.now()
        
        return context

@dataclass
class ContextExtractionConfig:
    """Configuration for context extraction"""
    max_conversation_history: int = 5
    max_recent_memories: int = 10
    max_relationships: int = 20
    cache_ttl_minutes: int = 30
    max_database_queries: int = 3
    memory_relevance_threshold: float = 0.3

class SmartContextExtractor:
    """
    Lightweight context extraction with session-based caching
    Optimized for Render free tier constraints
    """
    
    def __init__(self, supabase_service=None, config: ContextExtractionConfig = None):
        self.supabase_service = supabase_service
        self.config = config or ContextExtractionConfig()
        
        # Session-based cache (in-memory)
        self.session_cache: Dict[str, UserContext] = {}
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'database_queries': 0,
            'cache_size': 0
        }
        
        # Query optimization
        self.query_count = 0
        self.max_queries_per_request = self.config.max_database_queries
        
        logger.info("SmartContextExtractor initialized with session caching")
    
    def get_user_context(self, user_id: str, message_content: str = None) -> UserContext:
        """
        Get comprehensive user context with intelligent caching
        """
        try:
            # Check cache first
            cached_context = self._get_cached_context(user_id)
            if cached_context and self._is_cache_valid(cached_context):
                self.cache_stats['hits'] += 1
                logger.debug(f"Cache hit for user {user_id}")
                return cached_context
            
            # Cache miss - extract fresh context
            self.cache_stats['misses'] += 1
            self.query_count = 0  # Reset query count for this request
            
            logger.debug(f"Cache miss for user {user_id}, extracting fresh context")
            
            # Build context with limited database queries
            context = self._extract_fresh_context(user_id, message_content)
            
            # Cache the context
            self._cache_context(context)
            
            logger.info(f"Context extracted for user {user_id} with {self.query_count} database queries")
            return context
            
        except Exception as e:
            logger.error(f"Error extracting context for user {user_id}: {e}")
            return self._create_minimal_context(user_id)
    
    def _extract_fresh_context(self, user_id: str, message_content: str = None) -> UserContext:
        """Extract fresh context from database with query limits"""
        
        # Initialize context with user profile (Query 1)
        context = self._get_base_user_context(user_id)
        
        if self.query_count >= self.max_queries_per_request:
            logger.warning(f"Query limit reached for user {user_id}")
            return context
        
        # Get recent memories and relationships (Query 2)
        self._enrich_with_memories_and_relationships(context, message_content)
        
        if self.query_count >= self.max_queries_per_request:
            return context
        
        # Get conversation history and mood patterns (Query 3)
        self._enrich_with_conversation_and_mood_data(context)
        
        return context
    
    def _get_base_user_context(self, user_id: str) -> UserContext:
        """Get basic user context from profile (Query 1)"""
        try:
            if not self.supabase_service:
                return self._create_minimal_context(user_id)
            
            # Get user profile
            profile = self.supabase_service.get_user_profile(user_id)
            self.query_count += 1
            self.cache_stats['database_queries'] += 1
            
            if not profile:
                logger.warning(f"No profile found for user {user_id}")
                return self._create_minimal_context(user_id)
            
            # Extract basic information
            preferred_name = (profile.get('preferred_name') or 
                            profile.get('display_name') or 
                            profile.get('name') or 
                            'friend')
            
            preferences = {
                'language': profile.get('language', 'en'),
                'mood_tracking_enabled': profile.get('mood_tracking_enabled', False),
                'onboarding_completed': profile.get('onboarding_completed', False)
            }
            
            context = UserContext(
                user_id=user_id,
                preferred_name=preferred_name,
                preferences=preferences
            )
            
            logger.debug(f"Base context created for user {user_id}: {preferred_name}")
            return context
            
        except Exception as e:
            logger.error(f"Error getting base context for user {user_id}: {e}")
            return self._create_minimal_context(user_id)
    
    def _enrich_with_memories_and_relationships(self, context: UserContext, message_content: str = None):
        """Enrich context with memories and relationships (Query 2)"""
        try:
            if not self.supabase_service or self.query_count >= self.max_queries_per_request:
                return
            
            # Get recent memories with relevance scoring
            memories = self.supabase_service.get_user_memories(
                context.user_id, 
                limit=self.config.max_recent_memories
            )
            self.query_count += 1
            self.cache_stats['database_queries'] += 1
            
            if memories:
                # Filter and score memories for relevance
                relevant_memories = self._filter_relevant_memories(memories, message_content)
                context.recent_memories = relevant_memories[:self.config.max_recent_memories]
                
                # Extract relationships from memories
                relationships = self._extract_relationships_from_memories(memories)
                context.key_relationships = relationships
                
                logger.debug(f"Added {len(context.recent_memories)} memories and "
                           f"{len(context.key_relationships)} relationships for user {context.user_id}")
            
        except Exception as e:
            logger.error(f"Error enriching with memories for user {context.user_id}: {e}")
    
    def _enrich_with_conversation_and_mood_data(self, context: UserContext):
        """Enrich context with conversation history and mood patterns (Query 3)"""
        try:
            if not self.supabase_service or self.query_count >= self.max_queries_per_request:
                return
            
            # Get recent conversation history
            conversations = self.supabase_service.get_user_conversations(
                context.user_id, 
                limit=self.config.max_conversation_history
            )
            self.query_count += 1
            self.cache_stats['database_queries'] += 1
            
            if conversations:
                # Process conversation history
                context.conversation_history = self._process_conversation_history(conversations)
                
                # Extract recent emotions from conversations
                context.recent_emotions = self._extract_recent_emotions(conversations)
                
                # Build mood patterns
                context.mood_patterns = self._build_mood_patterns(conversations)
                
                logger.debug(f"Added conversation history and mood data for user {context.user_id}")
            
        except Exception as e:
            logger.error(f"Error enriching with conversation data for user {context.user_id}: {e}")
    
    def _filter_relevant_memories(self, memories: List[Dict], message_content: str = None) -> List[Dict]:
        """Filter memories by relevance to current message"""
        if not message_content:
            return memories[:self.config.max_recent_memories]
        
        relevant_memories = []
        message_lower = message_content.lower()
        
        for memory in memories:
            relevance_score = 0.0
            memory_text = memory.get('fact', '').lower()
            
            # Simple keyword matching for relevance
            if any(word in memory_text for word in message_lower.split() if len(word) > 3):
                relevance_score += 0.5
            
            # Boost score for relationship memories
            if memory.get('memory_type') == 'person':
                relevance_score += 0.3
            
            # Boost score for recent memories
            try:
                created_at = datetime.fromisoformat(memory.get('created_at', ''))
                days_old = (datetime.now() - created_at).days
                if days_old < 7:
                    relevance_score += 0.2
            except (ValueError, TypeError):
                pass
            
            if relevance_score >= self.config.memory_relevance_threshold:
                memory['relevance_score'] = relevance_score
                relevant_memories.append(memory)
        
        # Sort by relevance score
        relevant_memories.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        return relevant_memories
    
    def _extract_relationships_from_memories(self, memories: List[Dict]) -> Dict[str, str]:
        """Extract key relationships from memories"""
        relationships = {}
        
        for memory in memories:
            if memory.get('memory_type') == 'person':
                name = memory.get('name', '')
                relationship = memory.get('relationship', 'friend')
                
                if name and len(relationships) < self.config.max_relationships:
                    relationships[name] = relationship
        
        return relationships
    
    def _process_conversation_history(self, conversations: List[Dict]) -> List[Dict]:
        """Process conversation history for context"""
        processed = []
        
        for conv in conversations[:self.config.max_conversation_history]:
            processed_conv = {
                'message': conv.get('message', '')[:200],  # Truncate long messages
                'response': conv.get('response', '')[:200],
                'timestamp': conv.get('created_at', ''),
                'metadata': conv.get('metadata', {})
            }
            processed.append(processed_conv)
        
        return processed
    
    def _extract_recent_emotions(self, conversations: List[Dict]) -> List[str]:
        """Extract recent emotions from conversation metadata"""
        emotions = []
        
        for conv in conversations[:5]:  # Last 5 conversations
            metadata = conv.get('metadata', {})
            emotion = metadata.get('mood') or metadata.get('emotion')
            
            if emotion and emotion not in emotions:
                emotions.append(emotion)
        
        return emotions[:5]  # Keep last 5 unique emotions
    
    def _build_mood_patterns(self, conversations: List[Dict]) -> Dict[str, Any]:
        """Build mood patterns from conversation history"""
        mood_counts = {}
        total_conversations = len(conversations)
        
        for conv in conversations:
            metadata = conv.get('metadata', {})
            mood = metadata.get('mood') or metadata.get('emotion', 'neutral')
            mood_counts[mood] = mood_counts.get(mood, 0) + 1
        
        # Calculate percentages
        mood_patterns = {}
        for mood, count in mood_counts.items():
            mood_patterns[mood] = {
                'count': count,
                'percentage': (count / total_conversations) * 100 if total_conversations > 0 else 0
            }
        
        # Add dominant mood
        if mood_counts:
            dominant_mood = max(mood_counts, key=mood_counts.get)
            mood_patterns['dominant_mood'] = dominant_mood
        
        return mood_patterns
    
    def _create_minimal_context(self, user_id: str) -> UserContext:
        """Create minimal context when database is unavailable"""
        return UserContext(
            user_id=user_id,
            preferred_name='friend',
            preferences={'language': 'en'},
            session_metadata={'fallback_context': True}
        )
    
    def _get_cached_context(self, user_id: str) -> Optional[UserContext]:
        """Get context from session cache"""
        return self.session_cache.get(user_id)
    
    def _is_cache_valid(self, context: UserContext) -> bool:
        """Check if cached context is still valid"""
        cache_age = datetime.now() - context.last_updated
        return cache_age.total_seconds() < (self.config.cache_ttl_minutes * 60)
    
    def _cache_context(self, context: UserContext):
        """Cache context in session memory"""
        context.last_updated = datetime.now()
        self.session_cache[context.user_id] = context
        self.cache_stats['cache_size'] = len(self.session_cache)
        
        # Prevent memory bloat - keep only recent contexts
        if len(self.session_cache) > 100:  # Max 100 cached contexts
            # Remove oldest contexts
            sorted_contexts = sorted(
                self.session_cache.items(),
                key=lambda x: x[1].last_updated
            )
            
            # Keep only the 80 most recent
            for user_id, _ in sorted_contexts[:-80]:
                del self.session_cache[user_id]
            
            self.cache_stats['cache_size'] = len(self.session_cache)
            logger.info("Cache cleanup performed - removed old contexts")
    
    def invalidate_cache(self, user_id: str):
        """Invalidate cached context for a user"""
        if user_id in self.session_cache:
            del self.session_cache[user_id]
            self.cache_stats['cache_size'] = len(self.session_cache)
            logger.debug(f"Cache invalidated for user {user_id}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = (self.cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'cache_hits': self.cache_stats['hits'],
            'cache_misses': self.cache_stats['misses'],
            'hit_rate_percentage': round(hit_rate, 2),
            'total_database_queries': self.cache_stats['database_queries'],
            'current_cache_size': self.cache_stats['cache_size'],
            'avg_queries_per_miss': (
                self.cache_stats['database_queries'] / self.cache_stats['misses']
                if self.cache_stats['misses'] > 0 else 0
            )
        }
    
    def clear_cache(self):
        """Clear all cached contexts"""
        self.session_cache.clear()
        self.cache_stats['cache_size'] = 0
        logger.info("All cached contexts cleared")
    
    def get_context_summary(self, user_id: str) -> str:
        """Get a text summary of user context for LLM"""
        context = self.get_user_context(user_id)
        
        summary_parts = []
        
        # Basic info
        summary_parts.append(f"User: {context.preferred_name}")
        
        # Relationships
        if context.key_relationships:
            friends = [name for name, rel in context.key_relationships.items() if rel == 'friend']
            if friends:
                summary_parts.append(f"Friends: {', '.join(friends[:3])}")
        
        # Recent emotions
        if context.recent_emotions:
            summary_parts.append(f"Recent emotions: {', '.join(context.recent_emotions[:3])}")
        
        # Dominant mood
        if context.mood_patterns.get('dominant_mood'):
            summary_parts.append(f"Typical mood: {context.mood_patterns['dominant_mood']}")
        
        # Recent memories
        if context.recent_memories:
            recent_facts = [mem.get('fact', '')[:50] for mem in context.recent_memories[:2]]
            if recent_facts:
                summary_parts.append(f"Recent topics: {'; '.join(recent_facts)}")
        
        return " | ".join(summary_parts) if summary_parts else f"User: {context.preferred_name}"

# Global context extractor instance
_context_extractor = None

def get_context_extractor(supabase_service=None) -> SmartContextExtractor:
    """Get global context extractor instance"""
    global _context_extractor
    if _context_extractor is None:
        _context_extractor = SmartContextExtractor(supabase_service)
    elif supabase_service and not _context_extractor.supabase_service:
        _context_extractor.supabase_service = supabase_service
    return _context_extractor