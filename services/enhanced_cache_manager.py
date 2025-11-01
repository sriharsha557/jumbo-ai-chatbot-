"""
Enhanced Cache Manager for Conversation System
Provides intelligent caching for templates, contexts, and responses
"""

import time
import threading
import hashlib
import pickle
import json
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import OrderedDict, defaultdict
import logging
import weakref

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    value: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    ttl_seconds: Optional[int] = None
    size_bytes: int = 0
    tags: List[str] = field(default_factory=list)

class LRUCache:
    """LRU Cache with TTL and size limits"""
    
    def __init__(self, max_size: int = 1000, max_memory_mb: float = 50):
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        
        self.cache = OrderedDict()
        self.entries = {}  # key -> CacheEntry
        self.current_memory = 0
        self._lock = threading.RLock()
        
        # Statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'memory_evictions': 0,
            'ttl_evictions': 0,
            'total_size': 0
        }
    
    def _calculate_size(self, value: Any) -> int:
        """Calculate approximate size of value in bytes"""
        try:
            if isinstance(value, str):
                return len(value.encode('utf-8'))
            elif isinstance(value, (int, float)):
                return 8
            elif isinstance(value, (list, tuple)):
                return sum(self._calculate_size(item) for item in value)
            elif isinstance(value, dict):
                return sum(self._calculate_size(k) + self._calculate_size(v) 
                          for k, v in value.items())
            else:
                # Fallback to pickle size
                return len(pickle.dumps(value))
        except Exception:
            return 100  # Default size estimate
    
    def _evict_lru(self):
        """Evict least recently used item"""
        if self.cache:
            key = next(iter(self.cache))
            self._remove_entry(key)
            self.stats['evictions'] += 1
    
    def _evict_for_memory(self, required_bytes: int):
        """Evict items to free up memory"""
        while (self.current_memory + required_bytes > self.max_memory_bytes and 
               self.cache):
            key = next(iter(self.cache))
            self._remove_entry(key)
            self.stats['memory_evictions'] += 1
    
    def _remove_entry(self, key: str):
        """Remove entry from cache"""
        if key in self.cache:
            del self.cache[key]
        
        if key in self.entries:
            entry = self.entries[key]
            self.current_memory -= entry.size_bytes
            del self.entries[key]
    
    def _cleanup_expired(self):
        """Remove expired entries"""
        current_time = datetime.utcnow()
        expired_keys = []
        
        for key, entry in self.entries.items():
            if (entry.ttl_seconds and 
                current_time - entry.created_at > timedelta(seconds=entry.ttl_seconds)):\n                expired_keys.append(key)\n        \n        for key in expired_keys:\n            self._remove_entry(key)\n            self.stats['ttl_evictions'] += 1\n    \n    def get(self, key: str) -> Optional[Any]:\n        \"\"\"Get value from cache\"\"\"\n        with self._lock:\n            self._cleanup_expired()\n            \n            if key in self.cache:\n                # Move to end (most recently used)\n                value = self.cache[key]\n                del self.cache[key]\n                self.cache[key] = value\n                \n                # Update entry metadata\n                if key in self.entries:\n                    entry = self.entries[key]\n                    entry.last_accessed = datetime.utcnow()\n                    entry.access_count += 1\n                \n                self.stats['hits'] += 1\n                return value\n            else:\n                self.stats['misses'] += 1\n                return None\n    \n    def put(self, key: str, value: Any, ttl_seconds: Optional[int] = None, \n            tags: List[str] = None):\n        \"\"\"Put value in cache\"\"\"\n        with self._lock:\n            # Calculate size\n            size_bytes = self._calculate_size(value)\n            \n            # Check if we need to evict for memory\n            if size_bytes > self.max_memory_bytes:\n                logger.warning(f\"Value too large for cache: {size_bytes} bytes\")\n                return\n            \n            # Remove existing entry if present\n            if key in self.cache:\n                self._remove_entry(key)\n            \n            # Evict for memory if needed\n            self._evict_for_memory(size_bytes)\n            \n            # Evict for size if needed\n            while len(self.cache) >= self.max_size:\n                self._evict_lru()\n            \n            # Add new entry\n            self.cache[key] = value\n            self.entries[key] = CacheEntry(\n                key=key,\n                value=value,\n                created_at=datetime.utcnow(),\n                last_accessed=datetime.utcnow(),\n                ttl_seconds=ttl_seconds,\n                size_bytes=size_bytes,\n                tags=tags or []\n            )\n            \n            self.current_memory += size_bytes\n            self.stats['total_size'] = len(self.cache)\n    \n    def delete(self, key: str) -> bool:\n        \"\"\"Delete entry from cache\"\"\"\n        with self._lock:\n            if key in self.cache:\n                self._remove_entry(key)\n                return True\n            return False\n    \n    def clear_by_tags(self, tags: List[str]):\n        \"\"\"Clear entries with specific tags\"\"\"\n        with self._lock:\n            keys_to_remove = []\n            \n            for key, entry in self.entries.items():\n                if any(tag in entry.tags for tag in tags):\n                    keys_to_remove.append(key)\n            \n            for key in keys_to_remove:\n                self._remove_entry(key)\n    \n    def get_stats(self) -> Dict[str, Any]:\n        \"\"\"Get cache statistics\"\"\"\n        with self._lock:\n            total_requests = self.stats['hits'] + self.stats['misses']\n            hit_rate = self.stats['hits'] / total_requests if total_requests > 0 else 0\n            \n            return {\n                'size': len(self.cache),\n                'max_size': self.max_size,\n                'memory_usage_mb': self.current_memory / 1024 / 1024,\n                'max_memory_mb': self.max_memory_bytes / 1024 / 1024,\n                'hit_rate': hit_rate,\n                'hits': self.stats['hits'],\n                'misses': self.stats['misses'],\n                'evictions': self.stats['evictions'],\n                'memory_evictions': self.stats['memory_evictions'],\n                'ttl_evictions': self.stats['ttl_evictions']\n            }\n\nclass EnhancedCacheManager:\n    \"\"\"Enhanced cache manager with multiple cache layers\"\"\"\n    \n    def __init__(self):\n        # Different cache layers for different types of data\n        self.template_cache = LRUCache(max_size=500, max_memory_mb=20)  # Templates\n        self.context_cache = LRUCache(max_size=1000, max_memory_mb=30)  # User contexts\n        self.response_cache = LRUCache(max_size=2000, max_memory_mb=40) # Response cache\n        self.memory_cache = LRUCache(max_size=500, max_memory_mb=10)    # User memories\n        \n        # Cache warming and preloading\n        self.preload_functions = {}\n        self.warming_thread = None\n        self.warming_enabled = False\n        \n        # Cache invalidation tracking\n        self.invalidation_rules = defaultdict(list)\n        \n        logger.info(\"Enhanced cache manager initialized\")\n    \n    def _generate_cache_key(self, prefix: str, *args, **kwargs) -> str:\n        \"\"\"Generate consistent cache key\"\"\"\n        key_data = {\n            'args': args,\n            'kwargs': sorted(kwargs.items())\n        }\n        \n        key_string = json.dumps(key_data, sort_keys=True, default=str)\n        key_hash = hashlib.md5(key_string.encode()).hexdigest()[:16]\n        \n        return f\"{prefix}:{key_hash}\"\n    \n    # Template caching methods\n    def cache_template(self, template_id: str, template_data: Dict[str, Any], \n                      ttl_seconds: int = 3600):\n        \"\"\"Cache template data\"\"\"\n        key = f\"template:{template_id}\"\n        self.template_cache.put(key, template_data, ttl_seconds, tags=['template'])\n    \n    def get_cached_template(self, template_id: str) -> Optional[Dict[str, Any]]:\n        \"\"\"Get cached template data\"\"\"\n        key = f\"template:{template_id}\"\n        return self.template_cache.get(key)\n    \n    def invalidate_templates(self, template_ids: List[str] = None):\n        \"\"\"Invalidate template cache\"\"\"\n        if template_ids:\n            for template_id in template_ids:\n                key = f\"template:{template_id}\"\n                self.template_cache.delete(key)\n        else:\n            self.template_cache.clear_by_tags(['template'])\n    \n    # Context caching methods\n    def cache_user_context(self, user_id: str, context_data: Dict[str, Any], \n                          ttl_seconds: int = 1800):  # 30 minutes\n        \"\"\"Cache user context data\"\"\"\n        key = f\"context:{user_id}\"\n        self.context_cache.put(key, context_data, ttl_seconds, tags=['context', f'user:{user_id}'])\n    \n    def get_cached_user_context(self, user_id: str) -> Optional[Dict[str, Any]]:\n        \"\"\"Get cached user context\"\"\"\n        key = f\"context:{user_id}\"\n        return self.context_cache.get(key)\n    \n    def invalidate_user_context(self, user_id: str):\n        \"\"\"Invalidate user context cache\"\"\"\n        self.context_cache.clear_by_tags([f'user:{user_id}'])\n    \n    # Response caching methods\n    def cache_response(self, message_hash: str, response_data: Dict[str, Any], \n                      ttl_seconds: int = 600):  # 10 minutes\n        \"\"\"Cache response data\"\"\"\n        key = f\"response:{message_hash}\"\n        self.response_cache.put(key, response_data, ttl_seconds, tags=['response'])\n    \n    def get_cached_response(self, message_hash: str) -> Optional[Dict[str, Any]]:\n        \"\"\"Get cached response\"\"\"\n        key = f\"response:{message_hash}\"\n        return self.response_cache.get(key)\n    \n    def generate_message_hash(self, user_id: str, message: str, \n                            context_summary: str = \"\") -> str:\n        \"\"\"Generate hash for message caching\"\"\"\n        message_data = f\"{user_id}:{message}:{context_summary}\"\n        return hashlib.md5(message_data.encode()).hexdigest()\n    \n    # Memory caching methods\n    def cache_user_memories(self, user_id: str, memories: List[Dict[str, Any]], \n                           ttl_seconds: int = 3600):  # 1 hour\n        \"\"\"Cache user memories\"\"\"\n        key = f\"memories:{user_id}\"\n        self.memory_cache.put(key, memories, ttl_seconds, tags=['memories', f'user:{user_id}'])\n    \n    def get_cached_user_memories(self, user_id: str) -> Optional[List[Dict[str, Any]]]:\n        \"\"\"Get cached user memories\"\"\"\n        key = f\"memories:{user_id}\"\n        return self.memory_cache.get(key)\n    \n    def invalidate_user_memories(self, user_id: str):\n        \"\"\"Invalidate user memories cache\"\"\"\n        self.memory_cache.clear_by_tags([f'user:{user_id}'])\n    \n    # Advanced caching methods\n    def cache_with_dependencies(self, cache_type: str, key: str, value: Any, \n                               dependencies: List[str], ttl_seconds: int = 3600):\n        \"\"\"Cache value with dependency tracking\"\"\"\n        cache = self._get_cache_by_type(cache_type)\n        if cache:\n            tags = ['dependency'] + dependencies\n            cache.put(key, value, ttl_seconds, tags)\n            \n            # Register invalidation rules\n            for dep in dependencies:\n                self.invalidation_rules[dep].append((cache_type, key))\n    \n    def invalidate_by_dependency(self, dependency: str):\n        \"\"\"Invalidate all cache entries dependent on a key\"\"\"\n        if dependency in self.invalidation_rules:\n            for cache_type, key in self.invalidation_rules[dependency]:\n                cache = self._get_cache_by_type(cache_type)\n                if cache:\n                    cache.delete(key)\n            \n            del self.invalidation_rules[dependency]\n    \n    def _get_cache_by_type(self, cache_type: str) -> Optional[LRUCache]:\n        \"\"\"Get cache instance by type\"\"\"\n        cache_map = {\n            'template': self.template_cache,\n            'context': self.context_cache,\n            'response': self.response_cache,\n            'memory': self.memory_cache\n        }\n        return cache_map.get(cache_type)\n    \n    # Cache warming and preloading\n    def register_preload_function(self, cache_type: str, preload_func: Callable):\n        \"\"\"Register function for cache preloading\"\"\"\n        self.preload_functions[cache_type] = preload_func\n    \n    def start_cache_warming(self):\n        \"\"\"Start background cache warming\"\"\"\n        if not self.warming_enabled:\n            self.warming_enabled = True\n            self.warming_thread = threading.Thread(\n                target=self._cache_warming_loop,\n                daemon=True\n            )\n            self.warming_thread.start()\n            logger.info(\"Cache warming started\")\n    \n    def stop_cache_warming(self):\n        \"\"\"Stop background cache warming\"\"\"\n        self.warming_enabled = False\n        if self.warming_thread:\n            self.warming_thread.join(timeout=5)\n        logger.info(\"Cache warming stopped\")\n    \n    def _cache_warming_loop(self):\n        \"\"\"Background cache warming loop\"\"\"\n        while self.warming_enabled:\n            try:\n                for cache_type, preload_func in self.preload_functions.items():\n                    try:\n                        preload_func()\n                    except Exception as e:\n                        logger.error(f\"Error in cache preloading for {cache_type}: {e}\")\n                \n                time.sleep(300)  # Warm cache every 5 minutes\n                \n            except Exception as e:\n                logger.error(f\"Error in cache warming loop: {e}\")\n                time.sleep(600)  # Wait longer on error\n    \n    # Cache statistics and monitoring\n    def get_cache_stats(self) -> Dict[str, Any]:\n        \"\"\"Get comprehensive cache statistics\"\"\"\n        return {\n            'template_cache': self.template_cache.get_stats(),\n            'context_cache': self.context_cache.get_stats(),\n            'response_cache': self.response_cache.get_stats(),\n            'memory_cache': self.memory_cache.get_stats(),\n            'total_memory_mb': (\n                self.template_cache.current_memory +\n                self.context_cache.current_memory +\n                self.response_cache.current_memory +\n                self.memory_cache.current_memory\n            ) / 1024 / 1024,\n            'invalidation_rules': len(self.invalidation_rules),\n            'warming_enabled': self.warming_enabled\n        }\n    \n    def optimize_cache_sizes(self):\n        \"\"\"Optimize cache sizes based on usage patterns\"\"\"\n        stats = self.get_cache_stats()\n        \n        # Adjust cache sizes based on hit rates\n        for cache_name, cache_stats in stats.items():\n            if isinstance(cache_stats, dict) and 'hit_rate' in cache_stats:\n                hit_rate = cache_stats['hit_rate']\n                cache = self._get_cache_by_type(cache_name.replace('_cache', ''))\n                \n                if cache and hit_rate < 0.5:  # Low hit rate\n                    # Consider reducing cache size or TTL\n                    logger.info(f\"Low hit rate for {cache_name}: {hit_rate:.2f}\")\n                elif cache and hit_rate > 0.9:  # High hit rate\n                    # Consider increasing cache size\n                    logger.info(f\"High hit rate for {cache_name}: {hit_rate:.2f}\")\n    \n    def clear_all_caches(self):\n        \"\"\"Clear all caches\"\"\"\n        self.template_cache = LRUCache(max_size=500, max_memory_mb=20)\n        self.context_cache = LRUCache(max_size=1000, max_memory_mb=30)\n        self.response_cache = LRUCache(max_size=2000, max_memory_mb=40)\n        self.memory_cache = LRUCache(max_size=500, max_memory_mb=10)\n        self.invalidation_rules.clear()\n        logger.info(\"All caches cleared\")\n\n# Global cache manager instance\n_cache_manager = None\n\ndef get_cache_manager() -> EnhancedCacheManager:\n    \"\"\"Get global cache manager instance\"\"\"\n    global _cache_manager\n    if _cache_manager is None:\n        _cache_manager = EnhancedCacheManager()\n    return _cache_manager\n\ndef cache_decorator(cache_type: str, ttl_seconds: int = 3600, \n                   key_func: Callable = None):\n    \"\"\"Decorator for automatic caching\"\"\"\n    def decorator(func):\n        def wrapper(*args, **kwargs):\n            cache_manager = get_cache_manager()\n            \n            # Generate cache key\n            if key_func:\n                cache_key = key_func(*args, **kwargs)\n            else:\n                cache_key = cache_manager._generate_cache_key(\n                    f\"{func.__name__}\", *args, **kwargs\n                )\n            \n            # Try to get from cache\n            cache = cache_manager._get_cache_by_type(cache_type)\n            if cache:\n                cached_result = cache.get(cache_key)\n                if cached_result is not None:\n                    return cached_result\n            \n            # Execute function and cache result\n            result = func(*args, **kwargs)\n            \n            if cache:\n                cache.put(cache_key, result, ttl_seconds)\n            \n            return result\n        \n        return wrapper\n    return decorator\n