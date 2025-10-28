"""
Configuration Management for Jumbo Chatbot
Handles environment-specific settings and secrets
"""

import os
from typing import Dict, Any
from dataclasses import dataclass
from enum import Enum

class Environment(Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

@dataclass
class DatabaseConfig:
    """Database configuration"""
    url: str
    key: str
    jwt_secret: str
    service_role_key: str

@dataclass
class LLMConfig:
    """LLM service configuration"""
    provider: str
    api_key: str
    model: str
    max_tokens: int
    temperature: float

@dataclass
class RedisConfig:
    """Redis configuration for caching and sessions"""
    url: str
    password: str
    db: int

@dataclass
class MonitoringConfig:
    """Monitoring and logging configuration"""
    log_level: str
    sentry_dsn: str
    enable_metrics: bool
    metrics_port: int

class Config:
    """Main configuration class"""
    
    def __init__(self, env: str = None):
        self.environment = Environment(env or os.getenv('ENVIRONMENT', 'development'))
        self._load_config()
    
    def _load_config(self):
        """Load configuration based on environment"""
        
        # Base configuration
        self.debug = self.environment in [Environment.DEVELOPMENT, Environment.TESTING]
        self.testing = self.environment == Environment.TESTING
        
        # API Configuration
        self.api_version = "v1"
        self.api_prefix = f"/api/{self.api_version}"
        self.host = os.getenv('HOST', '0.0.0.0')
        self.port = int(os.getenv('PORT', 5000))
        
        # Security
        self.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
        self.cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
        
        # Database Configuration
        self.database = DatabaseConfig(
            url=os.getenv('SUPABASE_URL', ''),
            key=os.getenv('SUPABASE_ANON_KEY', ''),
            jwt_secret=os.getenv('SUPABASE_JWT_SECRET', ''),
            service_role_key=os.getenv('SUPABASE_SERVICE_ROLE_KEY', '')
        )
        
        # LLM Configuration
        self.llm = LLMConfig(
            provider=os.getenv('LLM_PROVIDER', 'groq'),
            api_key=os.getenv('GROQ_API_KEY', ''),
            model=os.getenv('LLM_MODEL', 'llama3-8b-8192'),
            max_tokens=int(os.getenv('LLM_MAX_TOKENS', 150)),
            temperature=float(os.getenv('LLM_TEMPERATURE', 0.7))
        )
        
        # Redis Configuration (for session management and caching)
        self.redis = RedisConfig(
            url=os.getenv('REDIS_URL', 'redis://localhost:6379'),
            password=os.getenv('REDIS_PASSWORD', ''),
            db=int(os.getenv('REDIS_DB', 0))
        )
        
        # Monitoring Configuration
        self.monitoring = MonitoringConfig(
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
            sentry_dsn=os.getenv('SENTRY_DSN', ''),
            enable_metrics=os.getenv('ENABLE_METRICS', 'false').lower() == 'true',
            metrics_port=int(os.getenv('METRICS_PORT', 9090))
        )
        
        # Environment-specific overrides
        self._apply_environment_overrides()
    
    def _apply_environment_overrides(self):
        """Apply environment-specific configuration overrides"""
        
        if self.environment == Environment.DEVELOPMENT:
            self.monitoring.log_level = 'DEBUG'
            
        elif self.environment == Environment.TESTING:
            self.database.url = os.getenv('TEST_SUPABASE_URL', self.database.url)
            self.database.key = os.getenv('TEST_SUPABASE_ANON_KEY', self.database.key)
            self.redis.db = 1  # Use different Redis DB for tests
            
        elif self.environment == Environment.STAGING:
            self.monitoring.enable_metrics = True
            
        elif self.environment == Environment.PRODUCTION:
            self.debug = False
            self.monitoring.enable_metrics = True
            # Ensure all required secrets are present
            self._validate_production_config()
    
    def _validate_production_config(self):
        """Validate that all required configuration is present for production"""
        required_vars = [
            ('SUPABASE_URL', self.database.url),
            ('SUPABASE_ANON_KEY', self.database.key),
            ('SECRET_KEY', self.secret_key),
        ]
        
        missing_vars = []
        for var_name, var_value in required_vars:
            if not var_value or var_value == 'dev-secret-key-change-in-production':
                missing_vars.append(var_name)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables for production: {', '.join(missing_vars)}")
    
    def get_database_url(self) -> str:
        """Get the appropriate database URL for the current environment"""
        return self.database.url
    
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.environment == Environment.DEVELOPMENT
    
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.environment == Environment.PRODUCTION
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary (excluding secrets)"""
        return {
            'environment': self.environment.value,
            'debug': self.debug,
            'api_version': self.api_version,
            'host': self.host,
            'port': self.port,
            'cors_origins': self.cors_origins,
            'llm_provider': self.llm.provider,
            'llm_model': self.llm.model,
            'monitoring_enabled': self.monitoring.enable_metrics,
            'log_level': self.monitoring.log_level
        }

# Global config instance
config = Config()

# Environment-specific configuration files
def load_env_file():
    """Load environment-specific .env file"""
    env_files = [
        f'.env.{config.environment.value}',
        '.env.local',
        '.env'
    ]
    
    for env_file in env_files:
        if os.path.exists(env_file):
            from dotenv import load_dotenv
            load_dotenv(env_file)
            break

# Load environment file on import
try:
    load_env_file()
except ImportError:
    # python-dotenv not installed, skip
    pass