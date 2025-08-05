import os
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class AppConfig:
    """Application configuration class"""
    
    def __init__(self):
        self.config_file = os.path.join(os.path.dirname(__file__), "config.json")
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            logger.info(f"Loaded configuration from {self.config_file}")
            return config
        except FileNotFoundError:
            logger.warning(f"Config file {self.config_file} not found, using defaults")
            return self._get_default_config()
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing config file: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "ollama": {
                "endpoint": "http://localhost:11434/api/generate",
                "model": "small-bank-chat"
            },
            "app": {
                "host": "0.0.0.0",
                "port": 5001,
                "debug": True,
                "secret_key": "dev-secret-key-12345"
            },
            "session": {
                "secure": False,
                "httponly": True,
                "samesite": "Lax",
                "lifetime_hours": 24
            },
            "cors": {
                "origins": [
                    "http://localhost:5000",
                    "http://127.0.0.1:5000", 
                    "http://localhost:5001",
                    "http://127.0.0.1:5001"
                ],
                "supports_credentials": True
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports dot notation)"""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_ollama_endpoint(self) -> str:
        """Get Ollama endpoint"""
        return self.get('ollama.endpoint', 'http://localhost:11434/api/generate')
    
    def get_ollama_model(self) -> str:
        """Get Ollama model name"""
        return self.get('ollama.model', 'small-bank-chat')
    
    def get_app_host(self) -> str:
        """Get app host"""
        return self.get('app.host', '0.0.0.0')
    
    def get_app_port(self) -> int:
        """Get app port"""
        return self.get('app.port', 5001)
    
    def get_app_debug(self) -> bool:
        """Get app debug mode"""
        return self.get('app.debug', True)
    
    def get_secret_key(self) -> str:
        """Get secret key"""
        return self.get('app.secret_key', 'dev-secret-key-12345')
    
    def get_session_config(self) -> Dict[str, Any]:
        """Get session configuration"""
        return {
            'SESSION_COOKIE_SECURE': self.get('session.secure', False),
            'SESSION_COOKIE_HTTPONLY': self.get('session.httponly', True),
            'SESSION_COOKIE_SAMESITE': self.get('session.samesite', 'Lax'),
            'PERMANENT_SESSION_LIFETIME': self.get('session.lifetime_hours', 24)
        }
    
    def get_cors_config(self) -> Dict[str, Any]:
        """Get CORS configuration"""
        return {
            'origins': self.get('cors.origins', []),
            'supports_credentials': self.get('cors.supports_credentials', True)
        } 