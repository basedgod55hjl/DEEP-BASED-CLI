"""
DEEP-CLI Configuration
"""

import os
from typing import Dict, Any

# DeepSeek API Configuration
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-2942f8c8a2c6449db5a3858ff862b5de")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

# Configuration dictionary
CONFIG = {
    "llm": {
        "api_key": DEEPSEEK_API_KEY,
        "base_url": DEEPSEEK_BASE_URL,
        "default_model": "deepseek-chat",
        "max_tokens": 4000,
        "temperature": 0.7,
        "timeout_seconds": 60,
        "retry_attempts": 3,
        "retry_delay": 1.0,
        "enable_streaming": True,
        "enable_function_calling": True,
        "enable_fim_completion": True,
        "enable_prefix_completion": True
    },
    "database": {
        "sqlite_path": "data/deepcli_database.db",
        "vector_db_host": "localhost",
        "vector_db_port": 6333,
        "vector_db_api_key": None,
        "vector_collection_name": "deepcli_vectors",
        "max_connections": 10,
        "connection_timeout": 30,
        "enable_migrations": True,
        "backup_enabled": True,
        "backup_interval_hours": 24
    },
    "tools": {
        "enable_all": True,
        "timeout_seconds": 30,
        "max_concurrent": 5
    },
    "logging": {
        "log_level": "INFO",
        "log_file": "logs/enhanced_cli.log",
        "enable_console_logging": True,
        "enable_file_logging": True
    }
}

def get_config() -> Dict[str, Any]:
    """Get the configuration dictionary"""
    return CONFIG

def update_config(updates: Dict[str, Any]) -> None:
    """Update configuration values"""
    def deep_update(base: dict, update: dict):
        for key, value in update.items():
            if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                deep_update(base[key], value)
            else:
                base[key] = value
    
    deep_update(CONFIG, updates) 