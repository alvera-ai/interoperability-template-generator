import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)

def load_env_file(filepath: str = '.env') -> dict:
    """Load environment variables from a file."""
    env_vars = {}
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
                        # Also set in os.environ for compatibility
                        os.environ[key.strip()] = value.strip()
        else:
            logger.warning(f"Environment file {filepath} not found")
    except Exception as e:
        logger.error(f"Error loading environment file: {e}")
    
    return env_vars

class Config:
    """Configuration management for the application."""
    
    def __init__(self):
        # Load environment variables from .env file (if exists)
        load_env_file()
        
        # Anthropic API configuration - HARDCODED (no environment variable reading)
        self.anthropic_api_key = "Fix this"
        
        # Database configuration (still use environment variables as fallback)
        self.postgres_host = self._get_env_var('POSTGRES_HOST', 'localhost')
        self.postgres_port = self._get_env_var('POSTGRES_PORT', '5432')
        self.postgres_db = self._get_env_var('POSTGRES_DB', 'api_interop')
        self.postgres_user = self._get_env_var('POSTGRES_USER', 'postgres')
        self.postgres_password = self._get_env_var('POSTGRES_PASSWORD', '')
        
        # Validate critical configuration
        if not self.anthropic_api_key:
            logger.warning("ANTHROPIC_API_KEY not found. Claude features will be disabled.")
        else:
            logger.info("Anthropic API key configured successfully (hardcoded)")
    
    def _get_env_var(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get environment variable with optional default."""
        return os.getenv(key, default)
    
    def get_postgres_config(self) -> dict:
        """Get PostgreSQL configuration as a dictionary."""
        return {
            'host': self.postgres_host,
            'port': self.postgres_port,
            'database': self.postgres_db,
            'username': self.postgres_user,
            'password': self.postgres_password
        }
    
    def has_anthropic_key(self) -> bool:
        """Check if Anthropic API key is available."""
        return bool(self.anthropic_api_key)

# Global configuration instance
config = Config() 