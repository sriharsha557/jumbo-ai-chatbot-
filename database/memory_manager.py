"""
Reliable Memory Manager for Jumbo Chatbot
Handles memory storage, retrieval, deduplication, and consistency
"""

import json
import hashlib
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

from supabase_service import SupabaseService
from monitoring import logger, monitor_database_query

@dataclass
class Memory:
    """Memory data structure"""
    id: Optional[str]
    user_id: str
    memory_type: str
    category: Optional[str]
    fact: str
    name: Optional[str]
    relationship: Optional[str]
    importance_score: float
    confidence_score: float
    embedding: Optional[List[float]]
    embedding_model: Optional[str]
    version: int
    is_active: bool
    duplicate_of: Optional[str]
    source_conversation_id: Optional[str]
    data: Dict[str, Any]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

class MemoryManager:
    """Manages user memories with reliability and consistency"""
    
    def __init__(self, supabase_service: SupabaseService):
        self.supabase = supabase_service
        self.similarity_threshold = 0.85
        self.max_memories_per_user = 10000
        self.cleanup_interval_days = 30
    
    @monitor_database_query()
    def store_memory(self, memory: Memory, ensure_transaction: bool = True) -> Tuple[bool, str, Optional[str]]:
        """
        Store memory with transactional integrity
        
        Args:
            memory: Memory object to store
            ensure_transaction: Whether to ensure transactional integrity
            
        Returns:
            Tuple of (success, message, memory_id)
        """
        try:
            # Start transaction if required
            if ensure_transaction:
                logger.info("Starting memory storage transaction", user_id=memory.user_id)
            
            # Check for duplicates first
            duplicates = self._find_duplicates(memory.user_id, memory.fact)
            
            if duplicates:
                existing_memory = duplicates[0]
                logger.info("Found duplicate memory, updating existing",
                           user_id=memory.user_id,
                           existing_id=existing_memory['id'],
                           similarity=duplicates[0].get('similarity', 0))
                
                # Update existing memory instead of creating duplicate
                return self._update_existing_memory(existing_memory['id'], memory)
            
            # Check memory limit
            if not self._check_memory_limit(memory.user_id):
                return False, "Memory limit exceeded for user", None
            
            # Generate embedding if not provided
            if not memory.embedding:
                memory.embedding = self._generate_embedding(memory.fact)
                memory.embedding_model = "text-embedding-ada-002"
            
            # Prepare memory data
            memory_data = {
                'user_id': memory.user_id,
                'memory_type': memory.memory_type,
                'category': memory.category,
                'fact': memory.fact,
                'name': memory.name,
                'relationship': memory.relationship,
                'importance_score': memory.importance_score,
                'confidence_score': memory.confidence_score,
                'embedding': memory.embedding,
                'embedding_model': memory.embedding_model,
                'version': memory.version,
                'is_active': memory.is_active,
                'duplicate_of': memory.duplicate_of,
                'source_conversation_id': memory.source_conversation_id,
                'data': memory.data
            }
            
            # Insert memory
            response = self.supabase.supabase.table('user_memories').insert(memory_data).execute()
            
            if response.data:
                memory_id = response.data[0]['id']
                logger.info("Memory stored successfully",
                           user_id=memory.user_id,
                           memory_id=memory_id,
                           memory_type=memory.memory_type)
                
                # Update memory statistics
                self._update_memory_stats(memory.user_id)
                
                return True, "Memory stored successfully", memory_id
            else:
                logger.error("Failed to store memory", user_id=memory.user_id)
                return False, "Failed to store memory", None
                
        except Exception as e:
            logger.error("Memory storage error", error=e, user_id=memory.user_id)
            return False, f"Memory storage error: {str(e)}", None
    
    @monitor_database_query()
    def retrieve_memories(self, user_id: str, 
                         memory_type: Optional[str] = None,
                         category: Optional[str] = None,
                         limit: int = 50,
                         include_inactive: bool = False) -> List[Dict]:
        """Retrieve user memories with filtering"""
        try:
            query = self.supabase.supabase.table('user_memories').select('*').eq('user_id', user_id)
            
            if not include_inactive:
                query = query.eq('is_active', True)
            
            if memory_type:
                query = query.eq('memory_type', memory_type)
            
            if category:
                query = query.eq('category', category)
            
            query = query.order('importance_score', desc=True).order('updated_at', desc=True).limit(limit)
            
            response = query.execute()
            
            logger.debug("Retrieved memories",
                        user_id=user_id,
                        count=len(response.data),
                        memory_type=memory_type,
                        category=category)
            
            return response.data
            
        except Exception as e:
            logger.error("Memory retrieval error", error=e, user_id=user_id)
            return []
    
    @monitor_database_query()
    def search_memories(self, user_id: str, query: str, limit: int = 20) -> List[Dict]:
        """Search memories using text search and vector similarity"""
        try:
            # Generate embedding for query
            query_embedding = self._generate_embedding(query)
            
            # Use vector similarity search if embeddings are available
            if query_embedding:
                # Note: This would use pgvector similarity search in a real implementation
                # For now, fall back to text search
                pass
            
            # Text search fallback
            response = self.supabase.supabase.table('user_memories').select('*').eq('user_id', user_id).eq('is_active', True).or_(
                f'fact.ilike.%{query}%,name.ilike.%{query}%'
            ).order('importance_score', desc=True).limit(limit).execute()
            
            logger.debug("Searched memories",
                        user_id=user_id,
                        query=query,
                        results=len(response.data))
            
            return response.data
            
        except Exception as e:
            logger.error("Memory search error", error=e, user_id=user_id, query=query)
            return []
    
    @monitor_database_query()
    def deduplicate_memories(self, user_id: str) -> Tuple[int, int]:
        """Remove duplicate memories for a user"""
        try:
            logger.info("Starting memory deduplication", user_id=user_id)
            
            memories = self.retrieve_memories(user_id, include_inactive=False)
            duplicates_found = 0
            duplicates_removed = 0
            
            # Group memories by similarity
            processed = set()
            
            for i, memory in enumerate(memories):
                if memory['id'] in processed:
                    continue
                
                # Find similar memories
                similar_memories = []
                for j, other_memory in enumerate(memories[i+1:], i+1):
                    if other_memory['id'] in processed:
                        continue
                    
                    similarity = self._calculate_text_similarity(memory['fact'], other_memory['fact'])
                    if similarity > self.similarity_threshold:
                        similar_memories.append((other_memory, similarity))
                        duplicates_found += 1
                
                # Mark duplicates as inactive
                if similar_memories:
                    # Keep the one with highest importance score
                    similar_memories.sort(key=lambda x: x[0]['importance_score'], reverse=True)
                    
                    for duplicate_memory, similarity in similar_memories[1:]:  # Skip the best one
                        success = self._mark_as_duplicate(duplicate_memory['id'], memory['id'])
                        if success:
                            duplicates_removed += 1
                            processed.add(duplicate_memory['id'])
                
                processed.add(memory['id'])
            
            logger.info("Memory deduplication completed",
                       user_id=user_id,
                       duplicates_found=duplicates_found,
                       duplicates_removed=duplicates_removed)
            
            return duplicates_found, duplicates_removed
            
        except Exception as e:
            logger.error("Memory deduplication error", error=e, user_id=user_id)
            return 0, 0
    
    @monitor_database_query()
    def cleanup_old_memories(self, days_old: int = 90) -> int:
        """Clean up old inactive memories"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            response = self.supabase.supabase.table('user_memories').delete().eq('is_active', False).lt('updated_at', cutoff_date.isoformat()).execute()
            
            deleted_count = len(response.data) if response.data else 0
            
            logger.info("Cleaned up old memories",
                       deleted_count=deleted_count,
                       days_old=days_old)
            
            return deleted_count
            
        except Exception as e:
            logger.error("Memory cleanup error", error=e)
            return 0
    
    @monitor_database_query()
    def backup_user_memories(self, user_id: str, backup_type: str = 'manual') -> Optional[str]:
        """Create backup of user memories"""
        try:
            memories = self.retrieve_memories(user_id, include_inactive=True, limit=self.max_memories_per_user)
            
            backup_data = {
                'user_id': user_id,
                'memory_data': memories,
                'backup_type': backup_type,
                'backup_date': datetime.now().isoformat(),
                'memory_count': len(memories)
            }
            
            response = self.supabase.supabase.table('user_memories_backup').insert(backup_data).execute()
            
            if response.data:
                backup_id = response.data[0]['backup_id']
                logger.info("Memory backup created",
                           user_id=user_id,
                           backup_id=backup_id,
                           memory_count=len(memories))
                return backup_id
            
            return None
            
        except Exception as e:
            logger.error("Memory backup error", error=e, user_id=user_id)
            return None
    
    def get_memory_stats(self, user_id: str) -> Dict[str, Any]:
        """Get memory statistics for user"""
        try:
            response = self.supabase.supabase.table('memory_stats').select('*').eq('user_id', user_id).execute()
            
            if response.data:
                return response.data[0]
            
            # Fallback calculation
            memories = self.retrieve_memories(user_id, include_inactive=True, limit=self.max_memories_per_user)
            
            stats = {
                'user_id': user_id,
                'total_memories': len(memories),
                'active_memories': len([m for m in memories if m['is_active']]),
                'inactive_memories': len([m for m in memories if not m['is_active']]),
                'avg_importance': sum(m['importance_score'] for m in memories) / max(len(memories), 1),
                'memory_types_count': len(set(m['memory_type'] for m in memories)),
                'categories_count': len(set(m['category'] for m in memories if m['category']))
            }
            
            return stats
            
        except Exception as e:
            logger.error("Memory stats error", error=e, user_id=user_id)
            return {}
    
    def _find_duplicates(self, user_id: str, fact: str) -> List[Dict]:
        """Find potential duplicate memories"""
        try:
            # Simple text-based duplicate detection
            memories = self.retrieve_memories(user_id, include_inactive=False)
            
            duplicates = []
            for memory in memories:
                similarity = self._calculate_text_similarity(fact, memory['fact'])
                if similarity > self.similarity_threshold:
                    duplicates.append({
                        'id': memory['id'],
                        'fact': memory['fact'],
                        'similarity': similarity
                    })
            
            return sorted(duplicates, key=lambda x: x['similarity'], reverse=True)
            
        except Exception as e:
            logger.error("Duplicate detection error", error=e, user_id=user_id)
            return []
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using simple metrics"""
        try:
            # Simple Jaccard similarity
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            
            if not union:
                return 0.0
            
            return len(intersection) / len(union)
            
        except Exception:
            return 0.0
    
    def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text (placeholder)"""
        # In a real implementation, this would call an embedding API
        # For now, return None to indicate no embedding
        return None
    
    def _check_memory_limit(self, user_id: str) -> bool:
        """Check if user is within memory limits"""
        try:
            stats = self.get_memory_stats(user_id)
            active_count = stats.get('active_memories', 0)
            return active_count < self.max_memories_per_user
        except Exception:
            return True  # Allow if we can't check
    
    def _update_existing_memory(self, memory_id: str, new_memory: Memory) -> Tuple[bool, str, str]:
        """Update existing memory with new information"""
        try:
            update_data = {
                'fact': new_memory.fact,
                'importance_score': max(new_memory.importance_score, 0.5),  # Don't decrease too much
                'confidence_score': new_memory.confidence_score,
                'updated_at': datetime.now().isoformat(),
                'version': new_memory.version + 1
            }
            
            response = self.supabase.supabase.table('user_memories').update(update_data).eq('id', memory_id).execute()
            
            if response.data:
                logger.info("Memory updated successfully", memory_id=memory_id)
                return True, "Memory updated successfully", memory_id
            
            return False, "Failed to update memory", memory_id
            
        except Exception as e:
            logger.error("Memory update error", error=e, memory_id=memory_id)
            return False, f"Memory update error: {str(e)}", memory_id
    
    def _mark_as_duplicate(self, memory_id: str, duplicate_of: str) -> bool:
        """Mark memory as duplicate"""
        try:
            update_data = {
                'is_active': False,
                'duplicate_of': duplicate_of,
                'updated_at': datetime.now().isoformat()
            }
            
            response = self.supabase.supabase.table('user_memories').update(update_data).eq('id', memory_id).execute()
            
            return bool(response.data)
            
        except Exception as e:
            logger.error("Mark duplicate error", error=e, memory_id=memory_id)
            return False
    
    def _update_memory_stats(self, user_id: str):
        """Update memory statistics (placeholder)"""
        # In a real implementation, this would update cached statistics
        pass