"""
DEEP-CLI Configuration
Central configuration for all enhanced features
"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Database Configuration
DATABASE_CONFIG = {
    "sqlite": {
        "path": str(DATA_DIR / "deepcli_database.db"),
        "check_same_thread": False,
        "timeout": 30.0
    }
}

# Vector Database Configuration
VECTOR_DB_CONFIG = {
    "qdrant": {
        "host": os.getenv("QDRANT_HOST", "localhost"),
        "port": int(os.getenv("QDRANT_PORT", "6333")),
        "api_key": os.getenv("QDRANT_API_KEY", None),
        "collection_name": "deepcli_vectors",
        "embedding_model": "BAAI/bge-small-en-v1.5",
        "vector_size": 384,
        "distance": "Cosine"
    },
    "use_cloud": os.getenv("QDRANT_CLOUD", "false").lower() == "true"
}

# Persona Configuration
PERSONA_CONFIG = {
    "default": "Deanna",
    "personas": {
        "Deanna": {
            "description": "An advanced AI assistant with deep knowledge in technology, programming, and problem-solving",
            "traits": ["intelligent", "curious", "helpful", "patient", "creative", "analytical"],
            "communication_style": "professional yet friendly",
            "specialties": ["RAG systems", "vector databases", "LLM integration", "code generation"],
            "greeting": "Hello! I'm Deanna, your AI assistant. How can I help you today?",
            "thinking_style": "Let me analyze this step by step...",
            "completion_style": "I've completed the task. Is there anything else you'd like me to help with?"
        }
    }
}

# RAG Configuration
RAG_CONFIG = {
    "context_limit": 5,
    "max_tokens": 1500,
    "relevance_threshold": 0.5,
    "include_memory": True,
    "include_history": True,
    "memory_importance_threshold": 7,
    "history_limit": 3,
    "vector_search_limit": 10
}

# DeepSeek API Configuration
DEEPSEEK_CONFIG = {
    "api_key": os.getenv("DEEPSEEK_API_KEY", "sk-90e0dd863b8c4e0d879a02851a0ee194"),
    "api_endpoint": "https://api.deepseek.com/v1",
    "models": {
        "chat": "deepseek-chat",
        "reasoner": "deepseek-reasoner"
    },
    "default_model": "deepseek-chat",
    "temperature": {
        "creative": 1.5,
        "balanced": 0.7,
        "precise": 0.3
    },
    "max_tokens": 2000
}

# Memory Configuration
MEMORY_CONFIG = {
    "file_path": str(DATA_DIR / "based_god_memory.json"),
    "max_entries": 10000,
    "auto_cleanup": True,
    "cleanup_threshold": 8000,
    "importance_levels": {
        "low": 1,
        "medium": 5,
        "high": 8,
        "critical": 10
    }
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": str(LOGS_DIR / "deepcli.log"),
    "max_bytes": 10 * 1024 * 1024,  # 10MB
    "backup_count": 5
}

# Tool Configuration
TOOL_CONFIG = {
    "enabled_tools": [
        "web_scraper",
        "llm_query",
        "code_generator",
        "data_analyzer",
        "file_processor",
        "memory",
        "reasoning_engine",
        "vector_database",
        "sql_database",
        "rag_pipeline"
    ],
    "tool_timeout": 30.0,
    "max_retries": 3
}

# Session Configuration
SESSION_CONFIG = {
    "timeout": 3600,  # 1 hour
    "max_history": 100,
    "auto_save": True,
    "save_interval": 300  # 5 minutes
}

# Performance Configuration
PERFORMANCE_CONFIG = {
    "enable_caching": True,
    "cache_ttl": 3600,
    "max_concurrent_tools": 5,
    "enable_profiling": False
}

# Security Configuration
SECURITY_CONFIG = {
    "enable_sandboxing": True,
    "allowed_file_extensions": [".txt", ".py", ".js", ".json", ".csv", ".md", ".html", ".css"],
    "max_file_size": 10 * 1024 * 1024,  # 10MB
    "enable_api_key_encryption": False
}

# Feature Flags
FEATURE_FLAGS = {
    "enable_rag": True,
    "enable_vector_db": True,
    "enable_sql_db": True,
    "enable_personas": True,
    "enable_analytics": True,
    "enable_context_caching": True,
    "enable_streaming": True,
    "enable_function_calling": True
}

# Export configuration
CONFIG = {
    "database": DATABASE_CONFIG,
    "vector_db": VECTOR_DB_CONFIG,
    "personas": PERSONA_CONFIG,
    "rag": RAG_CONFIG,
    "deepseek": DEEPSEEK_CONFIG,
    "memory": MEMORY_CONFIG,
    "logging": LOGGING_CONFIG,
    "tools": TOOL_CONFIG,
    "session": SESSION_CONFIG,
    "performance": PERFORMANCE_CONFIG,
    "security": SECURITY_CONFIG,
    "features": FEATURE_FLAGS
}

def get_config(section: str = None):
    """Get configuration section or entire config"""
    if section:
        return CONFIG.get(section, {})
    return CONFIG

def update_config(section: str, updates: dict):
    """Update configuration section"""
    if section in CONFIG:
        CONFIG[section].update(updates)
    else:
        CONFIG[section] = updates