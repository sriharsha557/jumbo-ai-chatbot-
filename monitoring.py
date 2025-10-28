"""
Monitoring and Logging System for Jumbo Chatbot
Handles structured logging, error tracking, and metrics
"""

import logging
import sys
import time
import json
from typing import Dict, Any, Optional
from functools import wraps
from datetime import datetime
import traceback

class StructuredLogger:
    """Structured JSON logger for better log analysis"""
    
    def __init__(self, name: str, level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # Create structured formatter
        formatter = StructuredFormatter()
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler for production
        try:
            from config import config
            if config.is_production():
                file_handler = logging.FileHandler('logs/app.log')
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
        except ImportError:
            pass
    
    def info(self, message: str, **kwargs):
        """Log info message with structured data"""
        self._log(logging.INFO, message, **kwargs)
    
    def error(self, message: str, error: Exception = None, **kwargs):
        """Log error message with structured data"""
        if error:
            kwargs['error_type'] = type(error).__name__
            kwargs['error_message'] = str(error)
            kwargs['traceback'] = traceback.format_exc()
        self._log(logging.ERROR, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with structured data"""
        self._log(logging.WARNING, message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with structured data"""
        self._log(logging.DEBUG, message, **kwargs)
    
    def _log(self, level: int, message: str, **kwargs):
        """Internal logging method"""
        extra = {
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'jumbo-chatbot',
            **kwargs
        }
        self.logger.log(level, message, extra=extra)

class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logs"""
    
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add extra fields
        if hasattr(record, 'timestamp'):
            log_data.update({k: v for k, v in record.__dict__.items() 
                           if k not in ['name', 'msg', 'args', 'levelname', 'levelno', 
                                      'pathname', 'filename', 'module', 'lineno', 
                                      'funcName', 'created', 'msecs', 'relativeCreated', 
                                      'thread', 'threadName', 'processName', 'process',
                                      'getMessage', 'exc_info', 'exc_text', 'stack_info']})
        
        return json.dumps(log_data, default=str)

class MetricsCollector:
    """Simple metrics collector for monitoring"""
    
    def __init__(self):
        self.metrics = {
            'requests_total': 0,
            'requests_by_endpoint': {},
            'response_times': [],
            'errors_total': 0,
            'active_users': set(),
            'conversations_total': 0,
            'llm_requests': 0,
            'database_queries': 0
        }
        self.start_time = time.time()
    
    def increment_requests(self, endpoint: str):
        """Increment request counter"""
        self.metrics['requests_total'] += 1
        self.metrics['requests_by_endpoint'][endpoint] = \
            self.metrics['requests_by_endpoint'].get(endpoint, 0) + 1
    
    def record_response_time(self, duration: float):
        """Record response time"""
        self.metrics['response_times'].append(duration)
        # Keep only last 1000 response times
        if len(self.metrics['response_times']) > 1000:
            self.metrics['response_times'] = self.metrics['response_times'][-1000:]
    
    def increment_errors(self):
        """Increment error counter"""
        self.metrics['errors_total'] += 1
    
    def add_active_user(self, user_id: str):
        """Add active user"""
        self.metrics['active_users'].add(user_id)
    
    def increment_conversations(self):
        """Increment conversation counter"""
        self.metrics['conversations_total'] += 1
    
    def increment_llm_requests(self):
        """Increment LLM request counter"""
        self.metrics['llm_requests'] += 1
    
    def increment_database_queries(self):
        """Increment database query counter"""
        self.metrics['database_queries'] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        uptime = time.time() - self.start_time
        avg_response_time = (sum(self.metrics['response_times']) / 
                           len(self.metrics['response_times'])) if self.metrics['response_times'] else 0
        
        return {
            'uptime_seconds': uptime,
            'requests_total': self.metrics['requests_total'],
            'requests_by_endpoint': self.metrics['requests_by_endpoint'],
            'average_response_time_ms': avg_response_time * 1000,
            'errors_total': self.metrics['errors_total'],
            'active_users_count': len(self.metrics['active_users']),
            'conversations_total': self.metrics['conversations_total'],
            'llm_requests': self.metrics['llm_requests'],
            'database_queries': self.metrics['database_queries'],
            'error_rate': (self.metrics['errors_total'] / max(self.metrics['requests_total'], 1)) * 100
        }

# Global instances
logger = StructuredLogger('jumbo-chatbot')
metrics = MetricsCollector()

def monitor_endpoint(endpoint_name: str = None):
    """Decorator to monitor API endpoints"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            endpoint = endpoint_name or func.__name__
            
            try:
                # Increment request counter
                metrics.increment_requests(endpoint)
                
                # Execute function
                result = func(*args, **kwargs)
                
                # Record response time
                duration = time.time() - start_time
                metrics.record_response_time(duration)
                
                # Log successful request
                logger.info(f"API request completed", 
                          endpoint=endpoint, 
                          duration_ms=duration * 1000,
                          status="success")
                
                return result
                
            except Exception as e:
                # Record error
                metrics.increment_errors()
                duration = time.time() - start_time
                
                # Log error
                logger.error(f"API request failed", 
                           error=e,
                           endpoint=endpoint,
                           duration_ms=duration * 1000,
                           status="error")
                
                raise
        
        return wrapper
    return decorator

def monitor_llm_request():
    """Decorator to monitor LLM requests"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                metrics.increment_llm_requests()
                result = func(*args, **kwargs)
                
                duration = time.time() - start_time
                logger.info("LLM request completed",
                          duration_ms=duration * 1000,
                          status="success")
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                logger.error("LLM request failed",
                           error=e,
                           duration_ms=duration * 1000,
                           status="error")
                raise
        
        return wrapper
    return decorator

def monitor_database_query():
    """Decorator to monitor database queries"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                metrics.increment_database_queries()
                result = func(*args, **kwargs)
                
                duration = time.time() - start_time
                logger.debug("Database query completed",
                           duration_ms=duration * 1000,
                           status="success")
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                logger.error("Database query failed",
                           error=e,
                           duration_ms=duration * 1000,
                           status="error")
                raise
        
        return wrapper
    return decorator

class HealthChecker:
    """Health check system for monitoring service status"""
    
    def __init__(self):
        self.checks = {}
    
    def register_check(self, name: str, check_func):
        """Register a health check"""
        self.checks[name] = check_func
    
    def run_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        results = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'checks': {}
        }
        
        overall_healthy = True
        
        for name, check_func in self.checks.items():
            try:
                check_result = check_func()
                results['checks'][name] = {
                    'status': 'healthy' if check_result else 'unhealthy',
                    'details': check_result if isinstance(check_result, dict) else {}
                }
                if not check_result:
                    overall_healthy = False
            except Exception as e:
                results['checks'][name] = {
                    'status': 'error',
                    'error': str(e)
                }
                overall_healthy = False
        
        results['status'] = 'healthy' if overall_healthy else 'unhealthy'
        return results

# Global health checker
health_checker = HealthChecker()

def setup_sentry():
    """Setup Sentry error tracking if configured"""
    try:
        from config import config
        if config.monitoring.sentry_dsn:
            import sentry_sdk
            from sentry_sdk.integrations.flask import FlaskIntegration
            
            sentry_sdk.init(
                dsn=config.monitoring.sentry_dsn,
                integrations=[FlaskIntegration()],
                environment=config.environment.value,
                traces_sample_rate=0.1 if config.is_production() else 1.0
            )
            logger.info("Sentry error tracking initialized")
    except ImportError:
        logger.warning("Sentry SDK not installed, skipping error tracking setup")
    except Exception as e:
        logger.error("Failed to setup Sentry", error=e)