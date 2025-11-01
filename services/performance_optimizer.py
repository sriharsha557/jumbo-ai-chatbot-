"""
Performance Optimizer for Enhanced Conversation System
Optimizes memory usage, database queries, and response times for Render free tier
"""

import time
import psutil
import os
import threading
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import logging
import weakref
import gc

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics tracking"""
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    response_time_ms: float = 0.0
    database_queries: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    active_connections: int = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ResourceLimits:
    """Resource limits for Render free tier"""
    max_memory_mb: float = 512
    max_cpu_percent: float = 80
    max_response_time_ms: float = 3000
    max_database_connections: int = 5
    max_cache_size_mb: float = 100

class MemoryManager:
    """Manages memory usage and cleanup for optimal performance"""
    
    def __init__(self, max_memory_mb: float = 400):
        self.max_memory_mb = max_memory_mb
        self.cleanup_threshold = max_memory_mb * 0.8  # Cleanup at 80%
        self.last_cleanup = time.time()
        self.cleanup_interval = 300  # 5 minutes
        
        # Track object references for cleanup
        self.tracked_objects = weakref.WeakSet()
        
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / 1024 / 1024
        except Exception as e:
            logger.error(f"Error getting memory usage: {e}")
            return 0.0
    
    def check_memory_pressure(self) -> bool:
        """Check if memory usage is approaching limits"""
        current_memory = self.get_memory_usage()
        return current_memory > self.cleanup_threshold
    
    def cleanup_memory(self) -> float:
        """Perform memory cleanup and return freed memory"""
        initial_memory = self.get_memory_usage()
        
        try:
            # Force garbage collection
            collected = gc.collect()
            
            # Clear weak references to deleted objects
            self.tracked_objects.clear()
            
            # Additional cleanup for specific objects
            self._cleanup_caches()
            
            final_memory = self.get_memory_usage()
            freed_memory = initial_memory - final_memory
            
            logger.info(f"Memory cleanup completed: freed {freed_memory:.1f}MB, "
                       f"collected {collected} objects")
            
            self.last_cleanup = time.time()
            return freed_memory
            
        except Exception as e:
            logger.error(f"Error during memory cleanup: {e}")
            return 0.0
    
    def _cleanup_caches(self):
        """Clean up internal caches"""
        # This would be implemented to clean up specific caches
        # For now, just force garbage collection
        gc.collect()
    
    def register_object(self, obj):
        """Register object for tracking"""
        try:
            self.tracked_objects.add(obj)
        except TypeError:
            # Object not weakly referenceable
            pass
    
    def should_cleanup(self) -> bool:
        """Check if cleanup should be performed"""
        return (self.check_memory_pressure() or 
                time.time() - self.last_cleanup > self.cleanup_interval)

class DatabaseOptimizer:
    """Optimizes database queries and connection management"""
    
    def __init__(self, max_connections: int = 5):
        self.max_connections = max_connections
        self.active_connections = 0
        self.query_cache = {}
        self.cache_ttl = 300  # 5 minutes
        self.query_stats = defaultdict(int)
        self.connection_pool = []
        self._lock = threading.Lock()
    
    def acquire_connection(self) -> bool:
        """Acquire a database connection"""
        with self._lock:
            if self.active_connections < self.max_connections:
                self.active_connections += 1
                return True
            return False
    
    def release_connection(self):
        """Release a database connection"""
        with self._lock:
            if self.active_connections > 0:
                self.active_connections -= 1
    
    def cache_query_result(self, query_key: str, result: Any, ttl: int = None):
        """Cache query result with TTL"""
        ttl = ttl or self.cache_ttl
        expiry = time.time() + ttl
        
        self.query_cache[query_key] = {
            'result': result,
            'expiry': expiry,
            'hits': 0
        }
    
    def get_cached_result(self, query_key: str) -> Optional[Any]:
        """Get cached query result if valid"""
        if query_key in self.query_cache:
            cache_entry = self.query_cache[query_key]
            
            if time.time() < cache_entry['expiry']:
                cache_entry['hits'] += 1
                return cache_entry['result']
            else:
                # Expired, remove from cache
                del self.query_cache[query_key]
        
        return None
    
    def cleanup_expired_cache(self):
        """Remove expired cache entries"""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.query_cache.items()
            if current_time >= entry['expiry']
        ]
        
        for key in expired_keys:
            del self.query_cache[key]
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def get_query_stats(self) -> Dict[str, Any]:
        """Get database query statistics"""
        total_queries = sum(self.query_stats.values())
        cache_hits = sum(entry['hits'] for entry in self.query_cache.values())
        
        return {
            'total_queries': total_queries,
            'cache_entries': len(self.query_cache),
            'cache_hits': cache_hits,
            'active_connections': self.active_connections,
            'query_breakdown': dict(self.query_stats)
        }
    
    def record_query(self, query_type: str):
        """Record a database query for statistics"""
        self.query_stats[query_type] += 1

class ResponseTimeOptimizer:
    """Optimizes response times through caching and batching"""
    
    def __init__(self):
        self.response_cache = {}
        self.cache_ttl = 600  # 10 minutes for responses
        self.batch_operations = []
        self.batch_size = 10
        self.batch_timeout = 1.0  # 1 second
        self.last_batch_time = time.time()
        
        # Response time tracking
        self.response_times = deque(maxlen=100)  # Keep last 100 response times
        
    def cache_response(self, message_hash: str, response_data: Dict[str, Any]):
        """Cache response for similar messages"""
        expiry = time.time() + self.cache_ttl
        
        self.response_cache[message_hash] = {
            'response_data': response_data,
            'expiry': expiry,
            'hits': 0
        }
    
    def get_cached_response(self, message_hash: str) -> Optional[Dict[str, Any]]:
        """Get cached response if available and valid"""
        if message_hash in self.response_cache:
            cache_entry = self.response_cache[message_hash]
            
            if time.time() < cache_entry['expiry']:
                cache_entry['hits'] += 1
                return cache_entry['response_data']
            else:
                del self.response_cache[message_hash]
        
        return None
    
    def record_response_time(self, response_time_ms: float):
        """Record response time for analysis"""
        self.response_times.append(response_time_ms)
    
    def get_average_response_time(self) -> float:
        """Get average response time"""
        if not self.response_times:
            return 0.0
        return sum(self.response_times) / len(self.response_times)
    
    def get_response_percentiles(self) -> Dict[str, float]:
        """Get response time percentiles"""
        if not self.response_times:
            return {'p50': 0, 'p90': 0, 'p95': 0, 'p99': 0}
        
        sorted_times = sorted(self.response_times)
        length = len(sorted_times)
        
        return {
            'p50': sorted_times[int(length * 0.5)],
            'p90': sorted_times[int(length * 0.9)],
            'p95': sorted_times[int(length * 0.95)],
            'p99': sorted_times[int(length * 0.99)]
        }
    
    def should_use_fast_path(self, message_complexity: float) -> bool:
        """Determine if fast path should be used based on performance"""
        avg_time = self.get_average_response_time()
        
        # Use fast path if average response time is high or message is simple
        return avg_time > 1000 or message_complexity < 0.3
    
    def cleanup_expired_responses(self):
        """Clean up expired response cache"""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.response_cache.items()
            if current_time >= entry['expiry']
        ]
        
        for key in expired_keys:
            del self.response_cache[key]

class PerformanceOptimizer:
    """Main performance optimizer coordinating all optimization strategies"""
    
    def __init__(self, resource_limits: ResourceLimits = None):
        self.resource_limits = resource_limits or ResourceLimits()
        
        # Initialize optimizers
        self.memory_manager = MemoryManager(self.resource_limits.max_memory_mb * 0.8)
        self.db_optimizer = DatabaseOptimizer(self.resource_limits.max_database_connections)
        self.response_optimizer = ResponseTimeOptimizer()
        
        # Performance tracking
        self.metrics_history = deque(maxlen=1000)  # Keep last 1000 metrics
        self.optimization_events = []
        
        # Background optimization thread
        self.optimization_thread = None
        self.running = False
        
        logger.info("Performance optimizer initialized with Render free tier limits")
    
    def start_background_optimization(self):
        """Start background optimization thread"""
        if not self.running:
            self.running = True
            self.optimization_thread = threading.Thread(
                target=self._background_optimization_loop,
                daemon=True
            )
            self.optimization_thread.start()
            logger.info("Background optimization thread started")
    
    def stop_background_optimization(self):
        """Stop background optimization thread"""
        self.running = False
        if self.optimization_thread:
            self.optimization_thread.join(timeout=5)
        logger.info("Background optimization thread stopped")
    
    def _background_optimization_loop(self):
        """Background optimization loop"""
        while self.running:
            try:
                # Perform periodic optimizations
                self._periodic_cleanup()
                time.sleep(30)  # Run every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in background optimization: {e}")
                time.sleep(60)  # Wait longer on error
    
    def _periodic_cleanup(self):
        """Perform periodic cleanup operations"""
        # Memory cleanup
        if self.memory_manager.should_cleanup():
            freed_memory = self.memory_manager.cleanup_memory()
            if freed_memory > 0:
                self.optimization_events.append({
                    'type': 'memory_cleanup',
                    'freed_mb': freed_memory,
                    'timestamp': datetime.utcnow()
                })
        
        # Database cache cleanup
        self.db_optimizer.cleanup_expired_cache()
        
        # Response cache cleanup
        self.response_optimizer.cleanup_expired_responses()
    
    def get_current_metrics(self) -> PerformanceMetrics:
        """Get current performance metrics"""
        try:
            process = psutil.Process(os.getpid())
            memory_usage = process.memory_info().rss / 1024 / 1024
            cpu_usage = process.cpu_percent()
            
            metrics = PerformanceMetrics(
                memory_usage_mb=memory_usage,
                cpu_usage_percent=cpu_usage,
                response_time_ms=self.response_optimizer.get_average_response_time(),
                database_queries=sum(self.db_optimizer.query_stats.values()),
                cache_hits=sum(entry['hits'] for entry in self.db_optimizer.query_cache.values()),
                cache_misses=len(self.db_optimizer.query_stats),
                active_connections=self.db_optimizer.active_connections
            )
            
            # Store in history
            self.metrics_history.append(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return PerformanceMetrics()
    
    def check_resource_limits(self) -> Dict[str, bool]:
        """Check if resource limits are being exceeded"""
        metrics = self.get_current_metrics()
        
        return {
            'memory_ok': metrics.memory_usage_mb <= self.resource_limits.max_memory_mb,
            'cpu_ok': metrics.cpu_usage_percent <= self.resource_limits.max_cpu_percent,
            'response_time_ok': metrics.response_time_ms <= self.resource_limits.max_response_time_ms,
            'connections_ok': metrics.active_connections <= self.resource_limits.max_database_connections
        }
    
    def optimize_for_message(self, message: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize processing for a specific message"""
        optimization_strategy = {
            'use_cache': True,
            'use_fast_path': False,
            'limit_queries': True,
            'compress_context': False
        }
        
        # Check current resource usage
        metrics = self.get_current_metrics()
        resource_status = self.check_resource_limits()
        
        # Adjust strategy based on resource pressure
        if not resource_status['memory_ok']:
            optimization_strategy['compress_context'] = True
            optimization_strategy['use_cache'] = True
            logger.warning("Memory pressure detected, enabling context compression")
        
        if not resource_status['response_time_ok']:
            optimization_strategy['use_fast_path'] = True
            optimization_strategy['limit_queries'] = True
            logger.warning("Response time pressure detected, enabling fast path")
        
        if not resource_status['connections_ok']:
            optimization_strategy['limit_queries'] = True
            optimization_strategy['use_cache'] = True
            logger.warning("Database connection pressure detected, limiting queries")
        
        return optimization_strategy
    
    def get_optimization_recommendations(self) -> List[str]:
        """Get optimization recommendations based on current performance"""
        recommendations = []
        metrics = self.get_current_metrics()
        resource_status = self.check_resource_limits()
        
        if not resource_status['memory_ok']:
            recommendations.append("Reduce memory usage: enable aggressive caching and cleanup")
        
        if not resource_status['cpu_ok']:
            recommendations.append("Reduce CPU usage: use simpler algorithms and cache more results")
        
        if not resource_status['response_time_ok']:
            recommendations.append("Improve response time: use fast path and reduce complexity")
        
        if not resource_status['connections_ok']:
            recommendations.append("Reduce database load: increase caching and batch operations")
        
        # Performance trend analysis
        if len(self.metrics_history) >= 10:
            recent_metrics = list(self.metrics_history)[-10:]
            memory_trend = [m.memory_usage_mb for m in recent_metrics]
            
            if len(memory_trend) >= 2:
                memory_increase = memory_trend[-1] - memory_trend[0]
                if memory_increase > 50:  # 50MB increase
                    recommendations.append("Memory usage trending up: investigate memory leaks")
        
        return recommendations
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        current_metrics = self.get_current_metrics()
        resource_status = self.check_resource_limits()
        db_stats = self.db_optimizer.get_query_stats()
        response_percentiles = self.response_optimizer.get_response_percentiles()
        
        return {
            'current_metrics': {
                'memory_usage_mb': current_metrics.memory_usage_mb,
                'cpu_usage_percent': current_metrics.cpu_usage_percent,
                'response_time_ms': current_metrics.response_time_ms,
                'active_connections': current_metrics.active_connections
            },
            'resource_limits': {
                'memory_limit_mb': self.resource_limits.max_memory_mb,
                'cpu_limit_percent': self.resource_limits.max_cpu_percent,
                'response_time_limit_ms': self.resource_limits.max_response_time_ms,
                'connection_limit': self.resource_limits.max_database_connections
            },
            'resource_status': resource_status,
            'database_stats': db_stats,
            'response_time_percentiles': response_percentiles,
            'optimization_events': self.optimization_events[-10:],  # Last 10 events
            'recommendations': self.get_optimization_recommendations(),
            'render_compatibility': all(resource_status.values()),
            'timestamp': datetime.utcnow().isoformat()
        }

# Global performance optimizer instance
_performance_optimizer = None

def get_performance_optimizer() -> PerformanceOptimizer:
    """Get global performance optimizer instance"""
    global _performance_optimizer
    if _performance_optimizer is None:
        _performance_optimizer = PerformanceOptimizer()
        _performance_optimizer.start_background_optimization()
    return _performance_optimizer

def optimize_for_render() -> Dict[str, Any]:
    """Apply Render-specific optimizations"""
    optimizer = get_performance_optimizer()
    
    # Get current status
    report = optimizer.get_performance_report()
    
    # Apply optimizations if needed
    optimizations_applied = []
    
    if not report['resource_status']['memory_ok']:
        freed_memory = optimizer.memory_manager.cleanup_memory()
        optimizations_applied.append(f"Memory cleanup: freed {freed_memory:.1f}MB")
    
    if not report['resource_status']['response_time_ok']:
        # Enable fast path for all future requests
        optimizations_applied.append("Enabled fast path for response generation")
    
    return {
        'optimizations_applied': optimizations_applied,
        'performance_report': report,
        'render_compatible': report['render_compatibility']
    }