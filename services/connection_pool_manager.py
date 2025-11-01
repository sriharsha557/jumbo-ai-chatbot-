"""
Connection Pool Manager for Enhanced Conversation System
Manages database connections efficiently for Render free tier constraints
"""

import threading
import time
import queue
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

@dataclass
class ConnectionInfo:
    """Information about a database connection"""
    connection_id: str
    created_at: datetime
    last_used: datetime
    usage_count: int = 0
    is_active: bool = True

class ConnectionPool:
    """Database connection pool with automatic cleanup and monitoring"""
    
    def __init__(self, 
                 max_connections: int = 5,
                 connection_timeout: int = 300,  # 5 minutes
                 cleanup_interval: int = 60):    # 1 minute
        
        self.max_connections = max_connections
        self.connection_timeout = connection_timeout
        self.cleanup_interval = cleanup_interval
        
        # Connection management
        self.available_connections = queue.Queue(maxsize=max_connections)
        self.active_connections = {}
        self.connection_info = {}
        
        # Thread safety
        self._lock = threading.RLock()
        self._connection_counter = 0
        
        # Background cleanup
        self._cleanup_thread = None
        self._running = False
        
        # Statistics
        self.stats = {
            'total_created': 0,
            'total_destroyed': 0,
            'current_active': 0,
            'peak_usage': 0,
            'connection_requests': 0,
            'connection_waits': 0,
            'cleanup_runs': 0
        }
        
        logger.info(f"Connection pool initialized: max_connections={max_connections}")
    
    def start(self):
        """Start the connection pool and background cleanup"""
        with self._lock:
            if not self._running:
                self._running = True
                self._cleanup_thread = threading.Thread(
                    target=self._cleanup_loop,
                    daemon=True
                )
                self._cleanup_thread.start()
                logger.info("Connection pool started")
    
    def stop(self):
        """Stop the connection pool and cleanup all connections"""
        with self._lock:
            self._running = False
            
            if self._cleanup_thread:
                self._cleanup_thread.join(timeout=5)
            
            # Close all connections
            self._cleanup_all_connections()
            logger.info("Connection pool stopped")
    
    def _create_connection_id(self) -> str:
        """Generate unique connection ID"""
        with self._lock:
            self._connection_counter += 1
            return f"conn_{self._connection_counter}_{int(time.time())}"
    
    def _create_mock_connection(self, connection_id: str) -> Dict[str, Any]:
        """Create a mock database connection for testing"""
        return {
            'id': connection_id,
            'created_at': datetime.utcnow(),
            'status': 'active',
            'queries_executed': 0
        }
    
    @contextmanager
    def get_connection(self, timeout: float = 5.0):
        """Get a connection from the pool with automatic return"""
        connection = None
        connection_id = None
        
        try:
            connection, connection_id = self._acquire_connection(timeout)
            yield connection
            
        finally:\n            if connection and connection_id:\n                self._release_connection(connection_id)\n    \n    def _acquire_connection(self, timeout: float) -> tuple:\n        \"\"\"Acquire a connection from the pool\"\"\"\n        self.stats['connection_requests'] += 1\n        \n        start_time = time.time()\n        \n        try:\n            # Try to get an available connection\n            connection_id = self.available_connections.get(timeout=timeout)\n            \n        except queue.Empty:\n            # No available connections\n            with self._lock:\n                if len(self.active_connections) < self.max_connections:\n                    # Create new connection\n                    connection_id = self._create_new_connection()\n                else:\n                    # Pool is full, wait or fail\n                    self.stats['connection_waits'] += 1\n                    logger.warning(\"Connection pool exhausted, waiting for available connection\")\n                    raise Exception(\"Connection pool exhausted\")\n        \n        # Get the actual connection\n        with self._lock:\n            if connection_id in self.active_connections:\n                connection = self.active_connections[connection_id]\n                \n                # Update connection info\n                if connection_id in self.connection_info:\n                    info = self.connection_info[connection_id]\n                    info.last_used = datetime.utcnow()\n                    info.usage_count += 1\n                \n                wait_time = time.time() - start_time\n                if wait_time > 1.0:  # Log if wait time > 1 second\n                    logger.info(f\"Connection acquired after {wait_time:.2f}s wait\")\n                \n                return connection, connection_id\n            else:\n                raise Exception(f\"Connection {connection_id} not found in active pool\")\n    \n    def _create_new_connection(self) -> str:\n        \"\"\"Create a new database connection\"\"\"\n        connection_id = self._create_connection_id()\n        \n        # Create mock connection (in real implementation, this would create actual DB connection)\n        connection = self._create_mock_connection(connection_id)\n        \n        # Add to active connections\n        self.active_connections[connection_id] = connection\n        \n        # Track connection info\n        self.connection_info[connection_id] = ConnectionInfo(\n            connection_id=connection_id,\n            created_at=datetime.utcnow(),\n            last_used=datetime.utcnow()\n        )\n        \n        # Update statistics\n        self.stats['total_created'] += 1\n        self.stats['current_active'] = len(self.active_connections)\n        self.stats['peak_usage'] = max(self.stats['peak_usage'], self.stats['current_active'])\n        \n        logger.debug(f\"Created new connection: {connection_id}\")\n        return connection_id\n    \n    def _release_connection(self, connection_id: str):\n        \"\"\"Release a connection back to the pool\"\"\"\n        with self._lock:\n            if connection_id in self.active_connections:\n                # Check if connection is still valid\n                if self._is_connection_valid(connection_id):\n                    # Return to available pool\n                    try:\n                        self.available_connections.put_nowait(connection_id)\n                        logger.debug(f\"Connection {connection_id} returned to pool\")\n                    except queue.Full:\n                        # Pool is full, close this connection\n                        self._close_connection(connection_id)\n                else:\n                    # Connection is invalid, close it\n                    self._close_connection(connection_id)\n            else:\n                logger.warning(f\"Attempted to release unknown connection: {connection_id}\")\n    \n    def _is_connection_valid(self, connection_id: str) -> bool:\n        \"\"\"Check if a connection is still valid\"\"\"\n        if connection_id not in self.connection_info:\n            return False\n        \n        info = self.connection_info[connection_id]\n        \n        # Check if connection has timed out\n        if datetime.utcnow() - info.last_used > timedelta(seconds=self.connection_timeout):\n            return False\n        \n        # Check if connection is marked as active\n        if not info.is_active:\n            return False\n        \n        return True\n    \n    def _close_connection(self, connection_id: str):\n        \"\"\"Close and remove a connection\"\"\"\n        if connection_id in self.active_connections:\n            # In real implementation, would close actual DB connection\n            connection = self.active_connections[connection_id]\n            \n            # Remove from active connections\n            del self.active_connections[connection_id]\n            \n            # Remove connection info\n            if connection_id in self.connection_info:\n                del self.connection_info[connection_id]\n            \n            # Update statistics\n            self.stats['total_destroyed'] += 1\n            self.stats['current_active'] = len(self.active_connections)\n            \n            logger.debug(f\"Closed connection: {connection_id}\")\n    \n    def _cleanup_loop(self):\n        \"\"\"Background cleanup loop\"\"\"\n        while self._running:\n            try:\n                self._cleanup_expired_connections()\n                self.stats['cleanup_runs'] += 1\n                time.sleep(self.cleanup_interval)\n                \n            except Exception as e:\n                logger.error(f\"Error in connection cleanup: {e}\")\n                time.sleep(self.cleanup_interval * 2)  # Wait longer on error\n    \n    def _cleanup_expired_connections(self):\n        \"\"\"Clean up expired connections\"\"\"\n        expired_connections = []\n        \n        with self._lock:\n            current_time = datetime.utcnow()\n            \n            for connection_id, info in self.connection_info.items():\n                if current_time - info.last_used > timedelta(seconds=self.connection_timeout):\n                    expired_connections.append(connection_id)\n        \n        # Close expired connections\n        for connection_id in expired_connections:\n            self._close_connection(connection_id)\n            logger.info(f\"Cleaned up expired connection: {connection_id}\")\n        \n        if expired_connections:\n            logger.info(f\"Cleaned up {len(expired_connections)} expired connections\")\n    \n    def _cleanup_all_connections(self):\n        \"\"\"Close all connections\"\"\"\n        with self._lock:\n            connection_ids = list(self.active_connections.keys())\n            \n            for connection_id in connection_ids:\n                self._close_connection(connection_id)\n            \n            # Clear the available queue\n            while not self.available_connections.empty():\n                try:\n                    self.available_connections.get_nowait()\n                except queue.Empty:\n                    break\n    \n    def get_pool_stats(self) -> Dict[str, Any]:\n        \"\"\"Get connection pool statistics\"\"\"\n        with self._lock:\n            return {\n                'max_connections': self.max_connections,\n                'active_connections': len(self.active_connections),\n                'available_connections': self.available_connections.qsize(),\n                'total_created': self.stats['total_created'],\n                'total_destroyed': self.stats['total_destroyed'],\n                'peak_usage': self.stats['peak_usage'],\n                'connection_requests': self.stats['connection_requests'],\n                'connection_waits': self.stats['connection_waits'],\n                'cleanup_runs': self.stats['cleanup_runs'],\n                'connection_timeout': self.connection_timeout,\n                'pool_utilization': len(self.active_connections) / self.max_connections\n            }\n    \n    def get_connection_details(self) -> List[Dict[str, Any]]:\n        \"\"\"Get detailed information about all connections\"\"\"\n        with self._lock:\n            details = []\n            \n            for connection_id, info in self.connection_info.items():\n                details.append({\n                    'connection_id': connection_id,\n                    'created_at': info.created_at.isoformat(),\n                    'last_used': info.last_used.isoformat(),\n                    'usage_count': info.usage_count,\n                    'is_active': info.is_active,\n                    'age_seconds': (datetime.utcnow() - info.created_at).total_seconds(),\n                    'idle_seconds': (datetime.utcnow() - info.last_used).total_seconds()\n                })\n            \n            return details\n\nclass QueryBatcher:\n    \"\"\"Batches database queries for improved performance\"\"\"\n    \n    def __init__(self, batch_size: int = 10, batch_timeout: float = 1.0):\n        self.batch_size = batch_size\n        self.batch_timeout = batch_timeout\n        \n        self.pending_queries = []\n        self.batch_results = {}\n        self._lock = threading.Lock()\n        self._batch_thread = None\n        self._running = False\n        \n        # Statistics\n        self.stats = {\n            'queries_batched': 0,\n            'batches_executed': 0,\n            'average_batch_size': 0,\n            'total_time_saved_ms': 0\n        }\n    \n    def start(self):\n        \"\"\"Start the query batcher\"\"\"\n        with self._lock:\n            if not self._running:\n                self._running = True\n                self._batch_thread = threading.Thread(\n                    target=self._batch_processing_loop,\n                    daemon=True\n                )\n                self._batch_thread.start()\n                logger.info(\"Query batcher started\")\n    \n    def stop(self):\n        \"\"\"Stop the query batcher\"\"\"\n        with self._lock:\n            self._running = False\n            \n            if self._batch_thread:\n                self._batch_thread.join(timeout=5)\n            \n            logger.info(\"Query batcher stopped\")\n    \n    def add_query(self, query_id: str, query_func: Callable, *args, **kwargs) -> Any:\n        \"\"\"Add a query to the batch\"\"\"\n        with self._lock:\n            query_info = {\n                'id': query_id,\n                'func': query_func,\n                'args': args,\n                'kwargs': kwargs,\n                'timestamp': time.time(),\n                'result_event': threading.Event()\n            }\n            \n            self.pending_queries.append(query_info)\n            self.stats['queries_batched'] += 1\n            \n            # If batch is full, trigger immediate processing\n            if len(self.pending_queries) >= self.batch_size:\n                self._process_batch()\n        \n        # Wait for result\n        query_info['result_event'].wait(timeout=self.batch_timeout * 2)\n        \n        # Get result\n        if query_id in self.batch_results:\n            result = self.batch_results[query_id]\n            del self.batch_results[query_id]\n            return result\n        else:\n            # Timeout or error, execute query directly\n            logger.warning(f\"Query {query_id} not found in batch results, executing directly\")\n            return query_func(*args, **kwargs)\n    \n    def _batch_processing_loop(self):\n        \"\"\"Background batch processing loop\"\"\"\n        while self._running:\n            try:\n                time.sleep(self.batch_timeout)\n                \n                with self._lock:\n                    if self.pending_queries:\n                        self._process_batch()\n                        \n            except Exception as e:\n                logger.error(f\"Error in batch processing: {e}\")\n    \n    def _process_batch(self):\n        \"\"\"Process the current batch of queries\"\"\"\n        if not self.pending_queries:\n            return\n        \n        batch = self.pending_queries.copy()\n        self.pending_queries.clear()\n        \n        start_time = time.time()\n        \n        # Execute queries in batch\n        for query_info in batch:\n            try:\n                result = query_info['func'](*query_info['args'], **query_info['kwargs'])\n                self.batch_results[query_info['id']] = result\n                \n            except Exception as e:\n                logger.error(f\"Error executing batched query {query_info['id']}: {e}\")\n                self.batch_results[query_info['id']] = None\n            \n            finally:\n                query_info['result_event'].set()\n        \n        # Update statistics\n        batch_time = (time.time() - start_time) * 1000\n        self.stats['batches_executed'] += 1\n        \n        if self.stats['batches_executed'] > 0:\n            total_queries = self.stats['queries_batched']\n            self.stats['average_batch_size'] = total_queries / self.stats['batches_executed']\n        \n        logger.debug(f\"Processed batch of {len(batch)} queries in {batch_time:.1f}ms\")\n    \n    def get_batch_stats(self) -> Dict[str, Any]:\n        \"\"\"Get query batching statistics\"\"\"\n        return {\n            'batch_size': self.batch_size,\n            'batch_timeout': self.batch_timeout,\n            'queries_batched': self.stats['queries_batched'],\n            'batches_executed': self.stats['batches_executed'],\n            'average_batch_size': self.stats['average_batch_size'],\n            'pending_queries': len(self.pending_queries)\n        }\n\n# Global instances\n_connection_pool = None\n_query_batcher = None\n\ndef get_connection_pool() -> ConnectionPool:\n    \"\"\"Get global connection pool instance\"\"\"\n    global _connection_pool\n    if _connection_pool is None:\n        _connection_pool = ConnectionPool(max_connections=5)\n        _connection_pool.start()\n    return _connection_pool\n\ndef get_query_batcher() -> QueryBatcher:\n    \"\"\"Get global query batcher instance\"\"\"\n    global _query_batcher\n    if _query_batcher is None:\n        _query_batcher = QueryBatcher(batch_size=10, batch_timeout=1.0)\n        _query_batcher.start()\n    return _query_batcher\n\ndef cleanup_connection_resources():\n    \"\"\"Clean up connection pool and query batcher resources\"\"\"\n    global _connection_pool, _query_batcher\n    \n    if _connection_pool:\n        _connection_pool.stop()\n        _connection_pool = None\n    \n    if _query_batcher:\n        _query_batcher.stop()\n        _query_batcher = None\n    \n    logger.info(\"Connection resources cleaned up\")\n