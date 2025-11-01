"""
Efficient Memory and Preference Retrieval Service
Optimized for minimal database queries and fast response times
"""

import logging
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import re

logger = logging.getLogger(__name__)

@dataclass
class MemorySearchResult:
    """Result of memory search with relevance scoring"""
    memory: Dict[str, Any]
    relevance_score: float
    match_reasons: List[str] = field(default_factory=list)

@dataclass
class PreferenceProfile:
    """User preference profile"""
    user_id: str
    communication_style: str = 'empathetic'
    preferred_topics: List[str] = field(default_factory=list)
    avoided_topics: List[str] = field(default_factory=list)
    response_length: str = 'medium'  # short, medium, long
    personality_preference: str = 'gentle'
    language: str = 'en'
    mood_tracking_enabled: bool = True
    last_updated: datetime = field(default_factory=datetime.now)

class MemoryRetrievalService:
    """
    Efficient memory and preference retrieval with intelligent caching and search
    """
    
    def __init__(self, supabase_service=None):
        self.supabase_service = supabase_service
        
        # Memory caches
        self.memory_cache: Dict[str, List[Dict]] = {}  # user_id -> memories
        self.preference_cache: Dict[str, PreferenceProfile] = {}  # user_id -> preferences
        
        # Search optimization
        self.keyword_index: Dict[str, Set[str]] = {}  # keyword -> set of user_ids
        self.relationship_index: Dict[str, Dict[str, str]] = {}  # user_id -> {name: relationship}
        
        # Performance tracking
        self.query_stats = {
            'memory_queries': 0,
            'preference_queries': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        
        logger.info("MemoryRetrievalService initialized")
    
    def get_relevant_memories(self, user_id: str, search_terms: List[str] = None, 
                            limit: int = 10) -> List[MemorySearchResult]:
        """
        Get relevant memories with intelligent search and scoring
        """
        try:
            # Get user memories (cached or from database)
            memories = self._get_user_memories(user_id)
            
            if not memories:
                return []
            
            # If no search terms, return recent memories
            if not search_terms:
                recent_memories = sorted(
                    memories, 
                    key=lambda x: x.get('created_at', ''), 
                    reverse=True
                )[:limit]
                
                return [
                    MemorySearchResult(memory=mem, relevance_score=0.5, match_reasons=['recent'])
                    for mem in recent_memories
                ]
            
            # Search and score memories
            scored_memories = self._search_and_score_memories(memories, search_terms)
            
            # Return top results
            return scored_memories[:limit]
            
        except Exception as e:
            logger.error(f"Error retrieving memories for user {user_id}: {e}")
            return []
    
    def get_user_preferences(self, user_id: str) -> PreferenceProfile:
        """
        Get user preferences with caching
        """
        try:
            # Check cache first
            if user_id in self.preference_cache:
                cached_prefs = self.preference_cache[user_id]
                if self._is_preference_cache_valid(cached_prefs):
                    self.query_stats['cache_hits'] += 1
                    return cached_prefs
            
            # Cache miss - fetch from database
            self.query_stats['cache_misses'] += 1
            preferences = self._fetch_user_preferences(user_id)
            
            # Cache the preferences
            self.preference_cache[user_id] = preferences
            
            return preferences
            
        except Exception as e:
            logger.error(f"Error getting preferences for user {user_id}: {e}")
            return self._create_default_preferences(user_id)
    
    def search_memories_by_keyword(self, user_id: str, keywords: List[str], 
                                 limit: int = 5) -> List[Dict]:
        """
        Fast keyword-based memory search
        """
        try:
            memories = self._get_user_memories(user_id)
            if not memories:
                return []
            
            matching_memories = []
            keywords_lower = [kw.lower() for kw in keywords]
            
            for memory in memories:
                memory_text = memory.get('fact', '').lower()
                match_count = sum(1 for kw in keywords_lower if kw in memory_text)
                
                if match_count > 0:
                    memory['match_score'] = match_count / len(keywords_lower)
                    matching_memories.append(memory)
            
            # Sort by match score and recency
            matching_memories.sort(
                key=lambda x: (x.get('match_score', 0), x.get('created_at', '')), 
                reverse=True
            )
            
            return matching_memories[:limit]
            
        except Exception as e:
            logger.error(f"Error searching memories for user {user_id}: {e}")
            return []
    
    def get_relationship_context(self, user_id: str) -> Dict[str, str]:
        """
        Get user's relationship context efficiently
        """
        try:
            # Check relationship index first
            if user_id in self.relationship_index:
                return self.relationship_index[user_id].copy()
            
            # Build from memories
            memories = self._get_user_memories(user_id)
            relationships = {}
            
            for memory in memories:
                if memory.get('memory_type') == 'person':
                    name = memory.get('name', '')
                    relationship = memory.get('relationship', 'friend')
                    if name:
                        relationships[name] = relationship
            
            # Cache in index
            self.relationship_index[user_id] = relationships
            
            return relationships.copy()
            
        except Exception as e:
            logger.error(f"Error getting relationship context for user {user_id}: {e}")
            return {}
    
    def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """
        Update user preferences and invalidate cache
        """
        try:
            if not self.supabase_service:
                return False
            
            # Update in database
            success, message = self.supabase_service.update_user_profile(user_id, preferences)
            
            if success:
                # Invalidate cache
                if user_id in self.preference_cache:
                    del self.preference_cache[user_id]
                
                logger.info(f"Updated preferences for user {user_id}")
                return True
            else:
                logger.error(f"Failed to update preferences for user {user_id}: {message}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating preferences for user {user_id}: {e}")
            return False
    
    def _get_user_memories(self, user_id: str) -> List[Dict]:
        """Get user memories with caching"""
        # Check cache first
        if user_id in self.memory_cache:
            return self.memory_cache[user_id]
        
        # Fetch from database
        memories = self._fetch_user_memories(user_id)
        
        # Cache the memories
        self.memory_cache[user_id] = memories
        
        # Update keyword index
        self._update_keyword_index(user_id, memories)
        
        return memories
    
    def _fetch_user_memories(self, user_id: str) -> List[Dict]:
        """Fetch memories from database"""
        try:
            if not self.supabase_service:
                return []
            
            memories = self.supabase_service.get_user_memories(user_id, limit=50)
            self.query_stats['memory_queries'] += 1
            
            return memories or []
            
        except Exception as e:
            logger.error(f"Error fetching memories for user {user_id}: {e}")
            return []
    
    def _fetch_user_preferences(self, user_id: str) -> PreferenceProfile:
        """Fetch preferences from database"""
        try:
            if not self.supabase_service:
                return self._create_default_preferences(user_id)
            
            profile = self.supabase_service.get_user_profile(user_id)
            self.query_stats['preference_queries'] += 1
            
            if not profile:
                return self._create_default_preferences(user_id)
            
            # Extract preferences from profile
            preferences = PreferenceProfile(
                user_id=user_id,
                communication_style=profile.get('communication_style', 'empathetic'),
                preferred_topics=profile.get('preferred_topics', []),
                avoided_topics=profile.get('avoided_topics', []),
                response_length=profile.get('response_length', 'medium'),
                personality_preference=profile.get('personality_preference', 'gentle'),
                language=profile.get('language', 'en'),
                mood_tracking_enabled=profile.get('mood_tracking_enabled', True)
            )
            
            return preferences
            
        except Exception as e:
            logger.error(f"Error fetching preferences for user {user_id}: {e}")
            return self._create_default_preferences(user_id)
    
    def _search_and_score_memories(self, memories: List[Dict], 
                                 search_terms: List[str]) -> List[MemorySearchResult]:
        """Search and score memories by relevance"""
        scored_results = []
        search_terms_lower = [term.lower() for term in search_terms]
        
        for memory in memories:
            score, reasons = self._calculate_memory_relevance(memory, search_terms_lower)
            
            if score > 0:
                result = MemorySearchResult(
                    memory=memory,
                    relevance_score=score,
                    match_reasons=reasons
                )
                scored_results.append(result)
        
        # Sort by relevance score
        scored_results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return scored_results
    
    def _calculate_memory_relevance(self, memory: Dict, search_terms: List[str]) -> Tuple[float, List[str]]:
        """Calculate relevance score for a memory"""
        score = 0.0
        reasons = []
        
        memory_text = memory.get('fact', '').lower()
        memory_type = memory.get('memory_type', '')
        
        # Exact keyword matches
        exact_matches = sum(1 for term in search_terms if term in memory_text)
        if exact_matches > 0:
            score += exact_matches * 0.4
            reasons.append(f'{exact_matches} keyword matches')
        
        # Partial word matches
        partial_matches = 0
        for term in search_terms:
            if any(term in word for word in memory_text.split()):
                partial_matches += 1
        
        if partial_matches > 0:
            score += partial_matches * 0.2
            reasons.append(f'{partial_matches} partial matches')
        
        # Memory type bonuses
        if memory_type == 'person':
            score += 0.3
            reasons.append('relationship memory')
        elif memory_type == 'preference':
            score += 0.2
            reasons.append('preference memory')
        
        # Recency bonus
        try:
            created_at = datetime.fromisoformat(memory.get('created_at', ''))
            days_old = (datetime.now() - created_at).days
            
            if days_old < 7:
                score += 0.3
                reasons.append('recent memory')
            elif days_old < 30:
                score += 0.1
                reasons.append('fairly recent')
        except (ValueError, TypeError):
            pass
        
        # Importance score from memory
        importance = memory.get('importance_score', 0.5)
        score += importance * 0.2
        
        if importance > 0.8:
            reasons.append('high importance')
        
        return score, reasons
    
    def _update_keyword_index(self, user_id: str, memories: List[Dict]):
        """Update keyword index for fast searching"""
        try:
            # Extract keywords from memories
            keywords = set()
            
            for memory in memories:
                memory_text = memory.get('fact', '').lower()
                # Extract meaningful words (length > 3)
                words = re.findall(r'\b\w{4,}\b', memory_text)
                keywords.update(words)
            
            # Update index
            for keyword in keywords:
                if keyword not in self.keyword_index:
                    self.keyword_index[keyword] = set()
                self.keyword_index[keyword].add(user_id)
                
        except Exception as e:
            logger.error(f"Error updating keyword index for user {user_id}: {e}")
    
    def _create_default_preferences(self, user_id: str) -> PreferenceProfile:
        """Create default preferences for a user"""
        return PreferenceProfile(
            user_id=user_id,
            communication_style='empathetic',
            preferred_topics=[],
            avoided_topics=[],
            response_length='medium',
            personality_preference='gentle',
            language='en',
            mood_tracking_enabled=True
        )
    
    def _is_preference_cache_valid(self, preferences: PreferenceProfile) -> bool:
        """Check if cached preferences are still valid"""
        cache_age = datetime.now() - preferences.last_updated
        return cache_age.total_seconds() < (60 * 60)  # 1 hour cache
    
    def invalidate_user_cache(self, user_id: str):
        """Invalidate all cached data for a user"""
        if user_id in self.memory_cache:
            del self.memory_cache[user_id]
        
        if user_id in self.preference_cache:
            del self.preference_cache[user_id]
        
        if user_id in self.relationship_index:
            del self.relationship_index[user_id]
        
        # Remove from keyword index
        for keyword, user_set in self.keyword_index.items():
            user_set.discard(user_id)
        
        logger.debug(f"Cache invalidated for user {user_id}")
    
    def get_memory_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get memory statistics for a user"""
        try:
            memories = self._get_user_memories(user_id)
            
            if not memories:
                return {'total_memories': 0}
            
            # Count by type
            type_counts = {}
            for memory in memories:
                mem_type = memory.get('memory_type', 'unknown')
                type_counts[mem_type] = type_counts.get(mem_type, 0) + 1
            
            # Calculate recency
            recent_count = 0
            week_ago = datetime.now() - timedelta(days=7)
            
            for memory in memories:
                try:
                    created_at = datetime.fromisoformat(memory.get('created_at', ''))
                    if created_at > week_ago:
                        recent_count += 1
                except (ValueError, TypeError):
                    pass
            
            return {
                'total_memories': len(memories),
                'by_type': type_counts,
                'recent_memories': recent_count,
                'relationships_count': len(self.get_relationship_context(user_id))
            }
            
        except Exception as e:
            logger.error(f"Error getting memory statistics for user {user_id}: {e}")
            return {'total_memories': 0, 'error': str(e)}
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Get service performance statistics"""
        total_requests = self.query_stats['cache_hits'] + self.query_stats['cache_misses']
        hit_rate = (self.query_stats['cache_hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'cache_performance': {
                'hit_rate_percentage': round(hit_rate, 2),
                'total_requests': total_requests,
                'cache_hits': self.query_stats['cache_hits'],
                'cache_misses': self.query_stats['cache_misses']
            },
            'database_queries': {
                'memory_queries': self.query_stats['memory_queries'],
                'preference_queries': self.query_stats['preference_queries'],
                'total_queries': self.query_stats['memory_queries'] + self.query_stats['preference_queries']
            },
            'cache_sizes': {
                'memory_cache': len(self.memory_cache),
                'preference_cache': len(self.preference_cache),
                'relationship_index': len(self.relationship_index),
                'keyword_index': len(self.keyword_index)
            }
        }
    
    def clear_all_caches(self):
        """Clear all caches"""
        self.memory_cache.clear()
        self.preference_cache.clear()
        self.relationship_index.clear()
        self.keyword_index.clear()
        
        logger.info("All caches cleared")

# Global memory retrieval service instance
_memory_service = None

def get_memory_retrieval_service(supabase_service=None) -> MemoryRetrievalService:
    """Get global memory retrieval service instance"""
    global _memory_service
    if _memory_service is None:
        _memory_service = MemoryRetrievalService(supabase_service)
    elif supabase_service and not _memory_service.supabase_service:
        _memory_service.supabase_service = supabase_service
    return _memory_service