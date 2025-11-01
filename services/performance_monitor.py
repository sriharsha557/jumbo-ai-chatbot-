"""
Performance Monitor for Enhanced Conversation System
Monitors response quality, system performance, and user engagement
"""

import time
import threading
import json
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque, defaultdict
import logging
import statistics
from enum import Enum

logger = logging.getLogger(__name__)

class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class PerformanceAlert:
    """Performance alert"""
    level: AlertLevel
    message: str
    metric_name: str
    current_value: float
    threshold: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    resolved: bool = False

@dataclass
class ConversationMetrics:
    """Metrics for a single conversation"""
    user_id: str
    message_id: str
    timestamp: datetime
    
    # Response metrics
    response_time_ms: float
    strategy_used: str
    quality_score: float
    emotion_detected: str
    conversation_type: str
    
    # System metrics
    memory_usage_mb: float
    cpu_usage_percent: float
    database_queries: int
    cache_hits: int
    cache_misses: int
    
    # User engagement metrics
    message_length: int
    response_length: int
    personalization_applied: bool
    fallback_used: bool

@dataclass
class SystemHealthMetrics:
    """Overall system health metrics"""
    timestamp: datetime
    
    # Performance metrics
    avg_response_time_ms: float
    p95_response_time_ms: float
    avg_quality_score: float
    
    # Resource metrics
    memory_usage_mb: float
    cpu_usage_percent: float
    active_connections: int
    
    # Cache metrics
    cache_hit_rate: float
    cache_memory_mb: float
    
    # Error metrics
    error_rate: float
    fallback_rate: float
    
    # User engagement metrics
    active_users: int
    conversations_per_minute: float
    avg_user_satisfaction: float

class MetricsCollector:
    """Collects and aggregates performance metrics"""
    
    def __init__(self, max_history: int = 10000):
        self.max_history = max_history
        
        # Conversation metrics storage
        self.conversation_metrics = deque(maxlen=max_history)
        self.system_health_history = deque(maxlen=1000)  # Keep 1000 health snapshots
        
        # Real-time aggregations
        self.response_times = deque(maxlen=1000)
        self.quality_scores = deque(maxlen=1000)
        self.error_counts = defaultdict(int)
        self.user_activity = defaultdict(list)
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Statistics cache
        self._stats_cache = {}
        self._cache_expiry = 0
        self._cache_ttl = 30  # 30 seconds
        
        logger.info("Metrics collector initialized")
    
    def record_conversation(self, metrics: ConversationMetrics):
        """Record conversation metrics"""
        with self._lock:
            self.conversation_metrics.append(metrics)
            
            # Update real-time aggregations
            self.response_times.append(metrics.response_time_ms)
            self.quality_scores.append(metrics.quality_score)
            
            # Track user activity
            self.user_activity[metrics.user_id].append(metrics.timestamp)
            
            # Clean old user activity (keep last 24 hours)
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            self.user_activity[metrics.user_id] = [\n                ts for ts in self.user_activity[metrics.user_id] \n                if ts > cutoff_time\n            ]\n            \n            # Clear stats cache\n            self._stats_cache.clear()\n    \n    def record_error(self, error_type: str, error_message: str = \"\"):\n        \"\"\"Record system error\"\"\"\n        with self._lock:\n            self.error_counts[error_type] += 1\n            \n            # Log error for debugging\n            logger.warning(f\"System error recorded: {error_type} - {error_message}\")\n    \n    def get_real_time_stats(self) -> Dict[str, Any]:\n        \"\"\"Get real-time performance statistics\"\"\"\n        current_time = time.time()\n        \n        # Check cache\n        if current_time < self._cache_expiry and self._stats_cache:\n            return self._stats_cache\n        \n        with self._lock:\n            stats = self._calculate_stats()\n            \n            # Update cache\n            self._stats_cache = stats\n            self._cache_expiry = current_time + self._cache_ttl\n            \n            return stats\n    \n    def _calculate_stats(self) -> Dict[str, Any]:\n        \"\"\"Calculate current statistics\"\"\"\n        now = datetime.utcnow()\n        \n        # Response time statistics\n        response_time_stats = {}\n        if self.response_times:\n            response_time_stats = {\n                'avg': statistics.mean(self.response_times),\n                'median': statistics.median(self.response_times),\n                'p95': self._percentile(list(self.response_times), 95),\n                'p99': self._percentile(list(self.response_times), 99),\n                'min': min(self.response_times),\n                'max': max(self.response_times)\n            }\n        \n        # Quality score statistics\n        quality_stats = {}\n        if self.quality_scores:\n            quality_stats = {\n                'avg': statistics.mean(self.quality_scores),\n                'median': statistics.median(self.quality_scores),\n                'min': min(self.quality_scores),\n                'max': max(self.quality_scores)\n            }\n        \n        # Recent activity (last hour)\n        hour_ago = now - timedelta(hours=1)\n        recent_conversations = [\n            m for m in self.conversation_metrics \n            if m.timestamp > hour_ago\n        ]\n        \n        # Strategy usage\n        strategy_usage = defaultdict(int)\n        fallback_count = 0\n        \n        for conv in recent_conversations:\n            strategy_usage[conv.strategy_used] += 1\n            if conv.fallback_used:\n                fallback_count += 1\n        \n        # Active users (last hour)\n        active_users = set()\n        for user_id, timestamps in self.user_activity.items():\n            if any(ts > hour_ago for ts in timestamps):\n                active_users.add(user_id)\n        \n        # Error rate\n        total_errors = sum(self.error_counts.values())\n        total_conversations = len(recent_conversations)\n        error_rate = total_errors / max(total_conversations, 1)\n        \n        # Fallback rate\n        fallback_rate = fallback_count / max(total_conversations, 1)\n        \n        return {\n            'timestamp': now.isoformat(),\n            'response_time': response_time_stats,\n            'quality': quality_stats,\n            'activity': {\n                'conversations_last_hour': len(recent_conversations),\n                'conversations_per_minute': len(recent_conversations) / 60,\n                'active_users': len(active_users),\n                'unique_users_24h': len(self.user_activity)\n            },\n            'strategy_usage': dict(strategy_usage),\n            'error_rate': error_rate,\n            'fallback_rate': fallback_rate,\n            'total_conversations': len(self.conversation_metrics),\n            'total_errors': total_errors\n        }\n    \n    def _percentile(self, data: List[float], percentile: int) -> float:\n        \"\"\"Calculate percentile of data\"\"\"\n        if not data:\n            return 0.0\n        \n        sorted_data = sorted(data)\n        index = (percentile / 100) * (len(sorted_data) - 1)\n        \n        if index.is_integer():\n            return sorted_data[int(index)]\n        else:\n            lower = sorted_data[int(index)]\n            upper = sorted_data[int(index) + 1]\n            return lower + (upper - lower) * (index - int(index))\n    \n    def get_user_engagement_metrics(self, user_id: str = None) -> Dict[str, Any]:\n        \"\"\"Get user engagement metrics\"\"\"\n        with self._lock:\n            if user_id:\n                # Metrics for specific user\n                user_conversations = [\n                    m for m in self.conversation_metrics \n                    if m.user_id == user_id\n                ]\n                \n                if not user_conversations:\n                    return {'user_id': user_id, 'conversations': 0}\n                \n                return {\n                    'user_id': user_id,\n                    'conversations': len(user_conversations),\n                    'avg_quality_score': statistics.mean([c.quality_score for c in user_conversations]),\n                    'avg_response_time': statistics.mean([c.response_time_ms for c in user_conversations]),\n                    'personalization_rate': sum(1 for c in user_conversations if c.personalization_applied) / len(user_conversations),\n                    'fallback_rate': sum(1 for c in user_conversations if c.fallback_used) / len(user_conversations),\n                    'first_conversation': min(c.timestamp for c in user_conversations).isoformat(),\n                    'last_conversation': max(c.timestamp for c in user_conversations).isoformat()\n                }\n            else:\n                # Overall engagement metrics\n                total_users = len(self.user_activity)\n                if total_users == 0:\n                    return {'total_users': 0}\n                \n                # Calculate engagement statistics\n                conversations_per_user = [len(convs) for convs in self.user_activity.values()]\n                \n                return {\n                    'total_users': total_users,\n                    'avg_conversations_per_user': statistics.mean(conversations_per_user),\n                    'median_conversations_per_user': statistics.median(conversations_per_user),\n                    'most_active_user_conversations': max(conversations_per_user) if conversations_per_user else 0,\n                    'users_with_multiple_conversations': sum(1 for count in conversations_per_user if count > 1)\n                }\n\nclass AlertManager:\n    \"\"\"Manages performance alerts and notifications\"\"\"\n    \n    def __init__(self):\n        self.alerts = deque(maxlen=1000)  # Keep last 1000 alerts\n        self.alert_rules = {}\n        self.notification_callbacks = []\n        self._lock = threading.Lock()\n        \n        # Default alert rules\n        self._setup_default_rules()\n        \n        logger.info(\"Alert manager initialized\")\n    \n    def _setup_default_rules(self):\n        \"\"\"Setup default alert rules\"\"\"\n        self.alert_rules = {\n            'response_time_high': {\n                'metric': 'avg_response_time_ms',\n                'threshold': 2000,  # 2 seconds\n                'level': AlertLevel.WARNING,\n                'message': 'Average response time is high: {value:.1f}ms (threshold: {threshold}ms)'\n            },\n            'response_time_critical': {\n                'metric': 'p95_response_time_ms',\n                'threshold': 5000,  # 5 seconds\n                'level': AlertLevel.CRITICAL,\n                'message': '95th percentile response time is critical: {value:.1f}ms (threshold: {threshold}ms)'\n            },\n            'quality_score_low': {\n                'metric': 'avg_quality_score',\n                'threshold': 0.4,\n                'level': AlertLevel.WARNING,\n                'message': 'Average quality score is low: {value:.2f} (threshold: {threshold})'\n            },\n            'error_rate_high': {\n                'metric': 'error_rate',\n                'threshold': 0.1,  # 10%\n                'level': AlertLevel.ERROR,\n                'message': 'Error rate is high: {value:.1%} (threshold: {threshold:.1%})'\n            },\n            'fallback_rate_high': {\n                'metric': 'fallback_rate',\n                'threshold': 0.3,  # 30%\n                'level': AlertLevel.WARNING,\n                'message': 'Fallback rate is high: {value:.1%} (threshold: {threshold:.1%})'\n            },\n            'memory_usage_high': {\n                'metric': 'memory_usage_mb',\n                'threshold': 400,  # 400MB (80% of 512MB limit)\n                'level': AlertLevel.WARNING,\n                'message': 'Memory usage is high: {value:.1f}MB (threshold: {threshold}MB)'\n            }\n        }\n    \n    def add_alert_rule(self, rule_name: str, metric: str, threshold: float, \n                      level: AlertLevel, message: str):\n        \"\"\"Add custom alert rule\"\"\"\n        self.alert_rules[rule_name] = {\n            'metric': metric,\n            'threshold': threshold,\n            'level': level,\n            'message': message\n        }\n    \n    def check_alerts(self, metrics: Dict[str, Any]):\n        \"\"\"Check metrics against alert rules\"\"\"\n        with self._lock:\n            for rule_name, rule in self.alert_rules.items():\n                metric_value = self._get_nested_metric(metrics, rule['metric'])\n                \n                if metric_value is not None:\n                    threshold = rule['threshold']\n                    \n                    # Check if alert should be triggered\n                    should_alert = False\n                    if rule['level'] in [AlertLevel.WARNING, AlertLevel.ERROR, AlertLevel.CRITICAL]:\n                        should_alert = metric_value > threshold\n                    \n                    if should_alert:\n                        alert = PerformanceAlert(\n                            level=rule['level'],\n                            message=rule['message'].format(\n                                value=metric_value,\n                                threshold=threshold\n                            ),\n                            metric_name=rule['metric'],\n                            current_value=metric_value,\n                            threshold=threshold\n                        )\n                        \n                        self._trigger_alert(alert)\n    \n    def _get_nested_metric(self, metrics: Dict[str, Any], metric_path: str) -> Optional[float]:\n        \"\"\"Get nested metric value from metrics dict\"\"\"\n        try:\n            # Handle nested paths like 'response_time.avg'\n            if '.' in metric_path:\n                parts = metric_path.split('.')\n                value = metrics\n                for part in parts:\n                    value = value[part]\n                return float(value)\n            else:\n                return float(metrics.get(metric_path, 0))\n        except (KeyError, TypeError, ValueError):\n            return None\n    \n    def _trigger_alert(self, alert: PerformanceAlert):\n        \"\"\"Trigger an alert\"\"\"\n        # Check if similar alert was recently triggered (avoid spam)\n        recent_alerts = [\n            a for a in self.alerts \n            if (a.metric_name == alert.metric_name and \n                datetime.utcnow() - a.timestamp < timedelta(minutes=5))\n        ]\n        \n        if not recent_alerts:\n            self.alerts.append(alert)\n            \n            # Log alert\n            logger.log(\n                logging.WARNING if alert.level == AlertLevel.WARNING else logging.ERROR,\n                f\"Performance Alert [{alert.level.value.upper()}]: {alert.message}\"\n            )\n            \n            # Notify callbacks\n            for callback in self.notification_callbacks:\n                try:\n                    callback(alert)\n                except Exception as e:\n                    logger.error(f\"Error in alert notification callback: {e}\")\n    \n    def add_notification_callback(self, callback: Callable[[PerformanceAlert], None]):\n        \"\"\"Add notification callback for alerts\"\"\"\n        self.notification_callbacks.append(callback)\n    \n    def get_recent_alerts(self, hours: int = 24) -> List[PerformanceAlert]:\n        \"\"\"Get recent alerts\"\"\"\n        cutoff_time = datetime.utcnow() - timedelta(hours=hours)\n        return [alert for alert in self.alerts if alert.timestamp > cutoff_time]\n    \n    def get_alert_summary(self) -> Dict[str, Any]:\n        \"\"\"Get alert summary\"\"\"\n        recent_alerts = self.get_recent_alerts()\n        \n        alert_counts = defaultdict(int)\n        for alert in recent_alerts:\n            alert_counts[alert.level.value] += 1\n        \n        return {\n            'total_alerts_24h': len(recent_alerts),\n            'alert_counts': dict(alert_counts),\n            'most_recent_alert': recent_alerts[-1].message if recent_alerts else None,\n            'active_rules': len(self.alert_rules)\n        }\n\nclass PerformanceMonitor:\n    \"\"\"Main performance monitoring system\"\"\"\n    \n    def __init__(self):\n        self.metrics_collector = MetricsCollector()\n        self.alert_manager = AlertManager()\n        \n        # Background monitoring\n        self.monitoring_thread = None\n        self.monitoring_enabled = False\n        self.monitoring_interval = 60  # 1 minute\n        \n        # Performance baselines\n        self.baselines = {\n            'response_time_ms': 500,\n            'quality_score': 0.7,\n            'error_rate': 0.05,\n            'fallback_rate': 0.2\n        }\n        \n        logger.info(\"Performance monitor initialized\")\n    \n    def start_monitoring(self):\n        \"\"\"Start background performance monitoring\"\"\"\n        if not self.monitoring_enabled:\n            self.monitoring_enabled = True\n            self.monitoring_thread = threading.Thread(\n                target=self._monitoring_loop,\n                daemon=True\n            )\n            self.monitoring_thread.start()\n            logger.info(\"Performance monitoring started\")\n    \n    def stop_monitoring(self):\n        \"\"\"Stop background performance monitoring\"\"\"\n        self.monitoring_enabled = False\n        if self.monitoring_thread:\n            self.monitoring_thread.join(timeout=5)\n        logger.info(\"Performance monitoring stopped\")\n    \n    def _monitoring_loop(self):\n        \"\"\"Background monitoring loop\"\"\"\n        while self.monitoring_enabled:\n            try:\n                # Get current metrics\n                metrics = self.metrics_collector.get_real_time_stats()\n                \n                # Check for alerts\n                self.alert_manager.check_alerts(metrics)\n                \n                # Log performance summary\n                self._log_performance_summary(metrics)\n                \n                time.sleep(self.monitoring_interval)\n                \n            except Exception as e:\n                logger.error(f\"Error in monitoring loop: {e}\")\n                time.sleep(self.monitoring_interval * 2)\n    \n    def _log_performance_summary(self, metrics: Dict[str, Any]):\n        \"\"\"Log periodic performance summary\"\"\"\n        response_time = metrics.get('response_time', {})\n        quality = metrics.get('quality', {})\n        activity = metrics.get('activity', {})\n        \n        logger.info(\n            f\"Performance Summary: \"\n            f\"Avg Response: {response_time.get('avg', 0):.1f}ms, \"\n            f\"Quality: {quality.get('avg', 0):.2f}, \"\n            f\"Active Users: {activity.get('active_users', 0)}, \"\n            f\"Conversations/min: {activity.get('conversations_per_minute', 0):.1f}\"\n        )\n    \n    def record_conversation_metrics(self, **kwargs):\n        \"\"\"Record conversation metrics\"\"\"\n        metrics = ConversationMetrics(**kwargs)\n        self.metrics_collector.record_conversation(metrics)\n    \n    def record_system_error(self, error_type: str, error_message: str = \"\"):\n        \"\"\"Record system error\"\"\"\n        self.metrics_collector.record_error(error_type, error_message)\n    \n    def get_performance_dashboard(self) -> Dict[str, Any]:\n        \"\"\"Get comprehensive performance dashboard data\"\"\"\n        real_time_stats = self.metrics_collector.get_real_time_stats()\n        engagement_metrics = self.metrics_collector.get_user_engagement_metrics()\n        alert_summary = self.alert_manager.get_alert_summary()\n        recent_alerts = self.alert_manager.get_recent_alerts(hours=1)\n        \n        return {\n            'real_time_stats': real_time_stats,\n            'engagement_metrics': engagement_metrics,\n            'alert_summary': alert_summary,\n            'recent_alerts': [\n                {\n                    'level': alert.level.value,\n                    'message': alert.message,\n                    'timestamp': alert.timestamp.isoformat()\n                }\n                for alert in recent_alerts\n            ],\n            'baselines': self.baselines,\n            'monitoring_enabled': self.monitoring_enabled,\n            'dashboard_generated_at': datetime.utcnow().isoformat()\n        }\n    \n    def get_health_check(self) -> Dict[str, Any]:\n        \"\"\"Get system health check\"\"\"\n        stats = self.metrics_collector.get_real_time_stats()\n        \n        # Determine health status\n        health_status = \"healthy\"\n        issues = []\n        \n        # Check response time\n        avg_response_time = stats.get('response_time', {}).get('avg', 0)\n        if avg_response_time > self.baselines['response_time_ms'] * 2:\n            health_status = \"degraded\"\n            issues.append(f\"High response time: {avg_response_time:.1f}ms\")\n        \n        # Check quality score\n        avg_quality = stats.get('quality', {}).get('avg', 1.0)\n        if avg_quality < self.baselines['quality_score']:\n            health_status = \"degraded\"\n            issues.append(f\"Low quality score: {avg_quality:.2f}\")\n        \n        # Check error rate\n        error_rate = stats.get('error_rate', 0)\n        if error_rate > self.baselines['error_rate']:\n            health_status = \"unhealthy\" if error_rate > 0.2 else \"degraded\"\n            issues.append(f\"High error rate: {error_rate:.1%}\")\n        \n        return {\n            'status': health_status,\n            'issues': issues,\n            'metrics_summary': {\n                'avg_response_time_ms': avg_response_time,\n                'avg_quality_score': avg_quality,\n                'error_rate': error_rate,\n                'active_users': stats.get('activity', {}).get('active_users', 0)\n            },\n            'timestamp': datetime.utcnow().isoformat()\n        }\n\n# Global performance monitor instance\n_performance_monitor = None\n\ndef get_performance_monitor() -> PerformanceMonitor:\n    \"\"\"Get global performance monitor instance\"\"\"\n    global _performance_monitor\n    if _performance_monitor is None:\n        _performance_monitor = PerformanceMonitor()\n        _performance_monitor.start_monitoring()\n    return _performance_monitor\n\ndef monitor_conversation(func):\n    \"\"\"Decorator to automatically monitor conversation metrics\"\"\"\n    def wrapper(*args, **kwargs):\n        start_time = time.time()\n        \n        try:\n            result = func(*args, **kwargs)\n            \n            # Extract metrics from result if it's a tuple\n            if isinstance(result, tuple) and len(result) == 2:\n                response, metadata = result\n                \n                # Record metrics\n                monitor = get_performance_monitor()\n                \n                processing_time = (time.time() - start_time) * 1000\n                \n                monitor.record_conversation_metrics(\n                    user_id=kwargs.get('user_id', 'unknown'),\n                    message_id=f\"msg_{int(time.time())}\",\n                    timestamp=datetime.utcnow(),\n                    response_time_ms=processing_time,\n                    strategy_used=metadata.get('strategy_used', 'unknown'),\n                    quality_score=metadata.get('quality_score', 0.5),\n                    emotion_detected=metadata.get('emotion_detected', 'neutral'),\n                    conversation_type=metadata.get('conversation_type', 'general'),\n                    memory_usage_mb=0,  # Would be filled by actual monitoring\n                    cpu_usage_percent=0,  # Would be filled by actual monitoring\n                    database_queries=metadata.get('database_queries', 0),\n                    cache_hits=metadata.get('cache_hits', 0),\n                    cache_misses=metadata.get('cache_misses', 0),\n                    message_length=len(kwargs.get('message', '')),\n                    response_length=len(response),\n                    personalization_applied=metadata.get('personalization_applied', False),\n                    fallback_used=metadata.get('fallback_used', False)\n                )\n            \n            return result\n            \n        except Exception as e:\n            # Record error\n            monitor = get_performance_monitor()\n            monitor.record_system_error('conversation_error', str(e))\n            raise\n    \n    return wrapper\n