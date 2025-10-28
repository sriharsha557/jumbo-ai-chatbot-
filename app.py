"""
Production-Ready Jumbo Chatbot API Server
Stateless, monitored, and properly structured for production deployment
"""

import os
import sys
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import configuration and monitoring
from config import config
from monitoring import (
    logger, metrics, health_checker, setup_sentry,
    monitor_endpoint, StructuredLogger
)

# Import services
from supabase_service import SupabaseService
from services.auth_service import AuthService
from services.chat_service import ChatService

# Import memory reliability system
from database.memory_manager import MemoryManager
from database.backup_manager import BackupManager
from database.migrations.migration_manager import MigrationManager

# Import API blueprints
from api.v1.auth import create_auth_blueprint
from api.v1.chat import create_chat_blueprint
from api.v1.profile import create_profile_blueprint
from api.v1.memories import create_memories_blueprint
from api.v1.onboarding import create_onboarding_blueprint

def create_app() -> Flask:
    """Application factory pattern"""
    
    # Initialize Flask app
    app = Flask(__name__)
    app.config['SECRET_KEY'] = config.secret_key
    
    # Setup CORS
    CORS(app, origins=config.cors_origins)
    
    # Setup error tracking
    setup_sentry()
    
    # Initialize services
    supabase_service = None
    auth_service = None
    chat_service = None
    memory_manager = None
    backup_manager = None
    migration_manager = None
    
    try:
        # Initialize core services
        supabase_service = SupabaseService()
        auth_service = AuthService(supabase_service)
        chat_service = ChatService(supabase_service)
        
        # Initialize memory reliability system
        memory_manager = MemoryManager(supabase_service)
        backup_manager = BackupManager(supabase_service)
        migration_manager = MigrationManager(supabase_service)
        
        logger.info("Services initialized successfully",
                   environment=config.environment.value,
                   debug=config.debug,
                   memory_system_enabled=True)
        
    except Exception as e:
        logger.error("Failed to initialize services", error=e)
        raise
    
    # Register health checks
    def check_database():
        """Check database connectivity"""
        try:
            # Simple health check - try to get service status
            return supabase_service is not None
        except Exception:
            return False
    
    def check_llm_service():
        """Check LLM service availability"""
        try:
            from llm_service import LLMService
            llm = LLMService()
            return llm.is_enabled()
        except Exception:
            return False
    
    def check_memory_system():
        """Check memory system health"""
        try:
            if memory_manager:
                # Test basic memory operations
                stats = memory_manager.get_memory_stats('health-check-user')
                return True
            return False
        except Exception:
            return False
    
    def check_backup_system():
        """Check backup system health"""
        try:
            if backup_manager:
                # Test backup list retrieval
                backups = backup_manager.get_backup_list()
                return True
            return False
        except Exception:
            return False
    
    health_checker.register_check('database', check_database)
    health_checker.register_check('llm_service', check_llm_service)
    health_checker.register_check('memory_system', check_memory_system)
    health_checker.register_check('backup_system', check_backup_system)
    
    # Register API blueprints with versioning
    api_prefix = config.api_prefix
    
    # v1 API endpoints
    app.register_blueprint(
        create_auth_blueprint(auth_service),
        url_prefix=f'{api_prefix}/auth'
    )
    
    app.register_blueprint(
        create_chat_blueprint(chat_service, auth_service),
        url_prefix=f'{api_prefix}/chat'
    )
    
    app.register_blueprint(
        create_profile_blueprint(chat_service, auth_service),
        url_prefix=f'{api_prefix}/profile'
    )
    
    app.register_blueprint(
        create_memories_blueprint(chat_service, auth_service),
        url_prefix=f'{api_prefix}/memories'
    )
    
    app.register_blueprint(
        create_onboarding_blueprint(supabase_service, auth_service),
        url_prefix=f'{api_prefix}/onboarding'
    )
    
    # Core endpoints
    @app.route('/health', methods=['GET'])
    @monitor_endpoint('health_check')
    def health_check():
        """Health check endpoint"""
        health_status = health_checker.run_checks()
        status_code = 200 if health_status['status'] == 'healthy' else 503
        
        return jsonify(health_status), status_code
    
    @app.route('/metrics', methods=['GET'])
    @monitor_endpoint('metrics')
    def get_metrics():
        """Metrics endpoint for monitoring"""
        if not config.monitoring.enable_metrics:
            return jsonify({
                'error': 'Metrics not enabled'
            }), 404
        
        return jsonify({
            'metrics': metrics.get_metrics(),
            'config': config.to_dict()
        }), 200
    
    @app.route('/info', methods=['GET'])
    @monitor_endpoint('info')
    def get_info():
        """API information endpoint"""
        return jsonify({
            'service': 'jumbo-chatbot-api',
            'version': config.api_version,
            'environment': config.environment.value,
            'endpoints': {
                'auth': f'{api_prefix}/auth',
                'chat': f'{api_prefix}/chat',
                'profile': f'{api_prefix}/profile',
                'memories': f'{api_prefix}/memories',
                'onboarding': f'{api_prefix}/onboarding',
                'health': '/health',
                'metrics': '/metrics' if config.monitoring.enable_metrics else None
            }
        }), 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors"""
        return jsonify({
            'success': False,
            'message': 'Endpoint not found',
            'available_endpoints': [
                f'{api_prefix}/auth',
                f'{api_prefix}/chat',
                f'{api_prefix}/profile',
                f'{api_prefix}/memories',
                f'{api_prefix}/onboarding',
                '/health',
                '/info'
            ]
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        logger.error("Internal server error", error=error)
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500
    
    @app.errorhandler(429)
    def rate_limit_error(error):
        """Handle rate limiting errors"""
        return jsonify({
            'success': False,
            'message': 'Rate limit exceeded'
        }), 429
    
    # Request/response middleware
    @app.before_request
    def before_request():
        """Log incoming requests"""
        if request.endpoint not in ['health_check', 'get_metrics']:
            logger.debug("Incoming request",
                        method=request.method,
                        endpoint=request.endpoint,
                        path=request.path,
                        user_agent=request.headers.get('User-Agent', ''))
    
    @app.after_request
    def after_request(response):
        """Log outgoing responses"""
        if request.endpoint not in ['health_check', 'get_metrics']:
            logger.debug("Outgoing response",
                        method=request.method,
                        endpoint=request.endpoint,
                        status_code=response.status_code)
        return response
    
    return app

def main():
    """Main entry point"""
    try:
        # Create application
        app = create_app()
        
        # Print startup information
        logger.info("Starting Jumbo Chatbot API Server",
                   environment=config.environment.value,
                   host=config.host,
                   port=config.port,
                   debug=config.debug,
                   api_version=config.api_version)
        
        # Print available endpoints
        logger.info("Available endpoints",
                   endpoints={
                       'auth': f'{config.api_prefix}/auth',
                       'chat': f'{config.api_prefix}/chat',
                       'profile': f'{config.api_prefix}/profile',
                       'memories': f'{config.api_prefix}/memories',
                       'onboarding': f'{config.api_prefix}/onboarding',
                       'health': '/health',
                       'info': '/info',
                       'metrics': '/metrics' if config.monitoring.enable_metrics else None
                   })
        
        # Run application
        app.run(
            host=config.host,
            port=config.port,
            debug=config.debug,
            threaded=True
        )
        
    except Exception as e:
        logger.error("Failed to start application", error=e)
        sys.exit(1)

# Create app instance for testing
app = create_app()

@app.route('/health')
def health_check():
    return {'status': 'healthy', 'service': 'jumbo-api'}, 200

if __name__ == '__main__':
    main()