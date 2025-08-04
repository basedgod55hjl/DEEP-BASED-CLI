#!/usr/bin/env python3
"""
🚀 BASED CODER CLI - Unified Configuration System
Made by @Lucariolucario55 on Telegram

Consolidated configuration management for the entire BASED CODER system
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime
import yaml
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION DATACLASSES
# ============================================================================

@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    sqlite_path: str = "data/deepcli_database.db"
    vector_db_host: str = "localhost"
    vector_db_port: int = 6333
    vector_db_api_key: Optional[str] = None
    vector_collection_name: str = "deepcli_vectors"
    max_connections: int = 10
    connection_timeout: int = 30
    enable_migrations: bool = True
    backup_enabled: bool = True
    backup_interval_hours: int = 24

@dataclass
class LLMConfig:
    """LLM configuration settings"""
    api_key: str = os.getenv("DEEPSEEK_API_KEY", "sk-9af038dd3bdd46258c4a9d02850c9a6d")
    base_url: str = "https://api.deepseek.com"
    default_model: str = "deepseek-chat"
    max_tokens: int = 4000
    temperature: float = 0.7
    timeout_seconds: int = 60
    retry_attempts: int = 3
    retry_delay: float = 1.0
    enable_streaming: bool = True
    enable_function_calling: bool = True
    enable_fim_completion: bool = True
    enable_prefix_completion: bool = True

@dataclass
class PersonaConfig:
    """Persona configuration settings"""
    default_persona: str = "enhanced_assistant"
    personas: Dict[str, Dict[str, Any]] = None
    enable_dynamic_adaptation: bool = True
    adaptation_threshold: float = 0.7
    max_persona_history: int = 50
    
    def __post_init__(self) -> Any:
        if self.personas is None:
            self.personas = {
                "enhanced_assistant": {
                    "name": "Enhanced AI Assistant",
                    "personality": "helpful, intelligent, and adaptive",
                    "expertise": ["general assistance", "problem solving", "learning"],
                    "communication_style": "clear, friendly, and professional",
                    "learning_preferences": "continuous improvement and adaptation",
                    "emotional_intelligence": "high",
                    "reasoning_capabilities": "advanced"
                },
                "deanna": {
                    "name": "Deanna",
                    "personality": "warm, empathetic, and insightful",
                    "expertise": ["conversation", "emotional support", "relationship building"],
                    "communication_style": "caring, understanding, and supportive",
                    "learning_preferences": "emotional intelligence and empathy",
                    "emotional_intelligence": "very high",
                    "reasoning_capabilities": "intuitive"
                },
                "expert_coder": {
                    "name": "Expert Coder",
                    "personality": "precise, analytical, and efficient",
                    "expertise": ["programming", "software architecture", "debugging"],
                    "communication_style": "technical, clear, and concise",
                    "learning_preferences": "best practices and optimization",
                    "emotional_intelligence": "moderate",
                    "reasoning_capabilities": "logical"
                },
                "creative_writer": {
                    "name": "Creative Writer",
                    "personality": "imaginative, expressive, and artistic",
                    "expertise": ["creative writing", "storytelling", "content creation"],
                    "communication_style": "engaging, vivid, and inspiring",
                    "learning_preferences": "creativity and expression",
                    "emotional_intelligence": "high",
                    "reasoning_capabilities": "creative"
                }
            }

@dataclass
class RAGConfig:
    """RAG configuration settings"""
    enable_rag: bool = True
    max_context_length: int = 2000
    similarity_threshold: float = 0.7
    max_retrieved_documents: int = 5
    enable_hybrid_search: bool = True
    enable_semantic_search: bool = True
    enable_keyword_search: bool = True
    reranking_enabled: bool = True
    context_window_size: int = 10
    enable_dynamic_context: bool = True

@dataclass
class MemoryConfig:
    """Memory configuration settings"""
    enable_memory: bool = True
    max_memory_entries: int = 10000
    memory_retention_days: int = 365
    enable_memory_compression: bool = True
    compression_threshold: float = 0.8
    enable_emotional_memory: bool = True
    enable_semantic_memory: bool = True
    enable_episodic_memory: bool = True
    memory_search_limit: int = 100
    enable_memory_consolidation: bool = True
    consolidation_interval_hours: int = 24

@dataclass
class ToolConfig:
    """Tool configuration settings"""
    enable_tool_management: bool = True
    max_concurrent_tools: int = 5
    tool_execution_timeout: int = 30
    enable_tool_caching: bool = True
    cache_ttl_seconds: int = 3600
    enable_tool_analytics: bool = True
    enable_tool_learning: bool = True
    tool_selection_strategy: str = "intelligent"
    enable_tool_orchestration: bool = True
    enable_tool_fallback: bool = True

@dataclass
class SecurityConfig:
    """Security configuration settings"""
    enable_encryption: bool = True
    encryption_algorithm: str = "AES-256"
    enable_api_key_rotation: bool = False
    key_rotation_interval_days: int = 90
    enable_rate_limiting: bool = True
    rate_limit_requests_per_minute: int = 60
    enable_input_validation: bool = True
    enable_output_sanitization: bool = True
    enable_audit_logging: bool = True
    audit_log_retention_days: int = 90

@dataclass
class PerformanceConfig:
    """Performance configuration settings"""
    enable_caching: bool = True
    cache_size_mb: int = 100
    enable_async_processing: bool = True
    max_async_tasks: int = 10
    enable_connection_pooling: bool = True
    pool_size: int = 5
    enable_compression: bool = True
    compression_level: int = 6
    enable_monitoring: bool = True
    monitoring_interval_seconds: int = 60
    enable_performance_metrics: bool = True

@dataclass
class LoggingConfig:
    """Logging configuration settings"""
    log_level: str = "INFO"
    log_file: str = "logs/enhanced_cli.log"
    enable_console_logging: bool = True
    enable_file_logging: bool = True
    enable_structured_logging: bool = True
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_rotation: bool = True
    max_log_size_mb: int = 10
    backup_count: int = 5
    enable_error_tracking: bool = True
    enable_performance_logging: bool = True

@dataclass
class SessionConfig:
    """Session configuration settings"""
    session_timeout_minutes: int = 60
    enable_session_persistence: bool = True
    session_file: str = "data/session_data.json"
    max_session_history: int = 100
    enable_session_analytics: bool = True
    enable_session_learning: bool = True
    session_encryption: bool = True
    enable_session_sharing: bool = False
    session_backup_enabled: bool = True
    session_backup_interval_minutes: int = 30

@dataclass
class FeatureFlags:
    """Feature flags for enabling/disabling features"""
    enable_fim_completion: bool = True
    enable_prefix_completion: bool = True
    enable_streaming: bool = True
    enable_unified_agent: bool = True
    enable_rag_pipeline: bool = True
    enable_vector_database: bool = True
    enable_sql_database: bool = True
    enable_advanced_reasoning: bool = True
    enable_emotional_intelligence: bool = True
    enable_predictive_analytics: bool = True
    enable_multi_modal_support: bool = True
    enable_real_time_learning: bool = True
    enable_autonomous_planning: bool = True
    enable_relationship_mapping: bool = True
    enable_context_awareness: bool = True

@dataclass
class ModelConfig:
    """Model configuration settings"""
    huggingface_token: str = os.getenv("HUGGINGFACE_API_KEY", "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")
    qwen_model_name: str = "Qwen/Qwen3-Embedding-0.6B"
    model_cache_dir: str = "data/models"
    enable_local_models: bool = True
    enable_cloud_models: bool = True
    model_download_timeout: int = 300
    enable_model_validation: bool = True

@dataclass
class EnhancedConfig:
    """Enhanced configuration container"""
    database: DatabaseConfig
    llm: LLMConfig
    persona: PersonaConfig
    rag: RAGConfig
    memory: MemoryConfig
    tool: ToolConfig
    security: SecurityConfig
    performance: PerformanceConfig
    logging: LoggingConfig
    session: SessionConfig
    features: FeatureFlags
    models: ModelConfig
    
    # Metadata
    config_version: str = "3.0.0"
    created_at: datetime = None
    last_updated: datetime = None
    environment: str = "development"
    
    def __post_init__(self) -> Any:
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_updated is None:
            self.last_updated = datetime.now()

# ============================================================================
# CONFIGURATION MANAGER
# ============================================================================

class ConfigManager:
    """Unified configuration manager"""
    
    def __init__(self, config_path: Optional[str] = None):
    
        self.config_path = config_path or "config/enhanced_config.json"
        self.config_dir = Path(self.config_path).parent
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self._config = None
        self._load_config()
    
    def _load_config(self) -> Any:
        """Load configuration from file or create default"""
        try:
            if Path(self.config_path).exists():
                self._config = self._load_from_file()
            else:
                self._config = self._create_default_config()
                self._save_config()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self._config = self._create_default_config()
    
    def _load_from_file(self) -> EnhancedConfig:
        """Load configuration from JSON file"""
        with open(self.config_path, 'r') as f:
            config_data = json.load(f)
        return self._dict_to_config(config_data)
    
    def _dict_to_config(self, config_data: Dict[str, Any]) -> EnhancedConfig:
        """Convert dictionary to EnhancedConfig"""
        # Create sub-configs
        database = DatabaseConfig(**config_data.get('database', {}))
        llm = LLMConfig(**config_data.get('llm', {}))
        persona = PersonaConfig(**config_data.get('persona', {}))
        rag = RAGConfig(**config_data.get('rag', {}))
        memory = MemoryConfig(**config_data.get('memory', {}))
        tool = ToolConfig(**config_data.get('tool', {}))
        security = SecurityConfig(**config_data.get('security', {}))
        performance = PerformanceConfig(**config_data.get('performance', {}))
        logging = LoggingConfig(**config_data.get('logging', {}))
        session = SessionConfig(**config_data.get('session', {}))
        features = FeatureFlags(**config_data.get('features', {}))
        models = ModelConfig(**config_data.get('models', {}))
        
        # Create main config
        return EnhancedConfig(
            database=database,
            llm=llm,
            persona=persona,
            rag=rag,
            memory=memory,
            tool=tool,
            security=security,
            performance=performance,
            logging=logging,
            session=session,
            features=features,
            models=models,
            config_version=config_data.get('config_version', '3.0.0'),
            environment=config_data.get('environment', 'development')
        )
    
    def _create_default_config(self) -> EnhancedConfig:
        """Create default configuration"""
        return EnhancedConfig(
            database=DatabaseConfig(),
            llm=LLMConfig(),
            persona=PersonaConfig(),
            rag=RAGConfig(),
            memory=MemoryConfig(),
            tool=ToolConfig(),
            security=SecurityConfig(),
            performance=PerformanceConfig(),
            logging=LoggingConfig(),
            session=SessionConfig(),
            features=FeatureFlags(),
            models=ModelConfig()
        )
    
    def _save_config(self) -> Any:
        """Save configuration to file"""
        config_dict = self._config_to_dict(self._config)
        with open(self.config_path, 'w') as f:
            json.dump(config_dict, f, indent=2, default=str)
    
    def _config_to_dict(self, config: EnhancedConfig) -> Dict[str, Any]:
        """Convert EnhancedConfig to dictionary"""
        config_dict = {}
        for field_name, field_value in config.__dict__.items():
            if hasattr(field_value, '__dict__'):
                config_dict[field_name] = field_value.__dict__
            else:
                config_dict[field_name] = field_value
        return config_dict
    
    def get_config(self) -> EnhancedConfig:
        """Get current configuration"""
        return self._config
    
    def update_config(self, updates: Dict[str, Any]):
    
        """Update configuration with new values"""
        for section, values in updates.items():
            if hasattr(self._config, section):
                section_config = getattr(self._config, section)
                for key, value in values.items():
                    if hasattr(section_config, key):
                        setattr(section_config, key, value)
        
        self._config.last_updated = datetime.now()
        self._save_config()
    
    def validate_config(self) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []
        
        # Validate API keys
        if not self._config.llm.api_key or not self._config.llm.api_key.startswith("sk-"):
            issues.append("Invalid DeepSeek API key")
        
        if not self._config.models.huggingface_token or not self._config.models.huggingface_token.startswith("hf_"):
            issues.append("Invalid HuggingFace token")
        
        # Validate paths
        if not Path(self._config.database.sqlite_path).parent.exists():
            issues.append("Database directory does not exist")
        
        if not Path(self._config.logging.log_file).parent.exists():
            issues.append("Log directory does not exist")
        
        return issues

# ============================================================================
# API KEYS MANAGEMENT
# ============================================================================

def validate_deepseek_key(api_key: str) -> bool:
    """Validate DeepSeek API key format"""
    if not api_key:
        return False
    if not api_key.startswith("sk-"):
        return False
    if len(api_key) < 20:
        return False
    return True

def validate_huggingface_token(token: str) -> bool:
    """Validate HuggingFace token format"""
    if not token:
        return False
    if not token.startswith("hf_"):
        return False
    if len(token) < 10:
        return False
    return True

def update_api_keys(deepseek_key: str = None, huggingface_token: str = None):
    
    """Update API keys in configuration and environment"""
    config = get_config()
    
    if deepseek_key and validate_deepseek_key(deepseek_key):
        config.llm.api_key = deepseek_key
        os.environ["DEEPSEEK_API_KEY"] = deepseek_key
    
    if huggingface_token and validate_huggingface_token(huggingface_token):
        config.models.huggingface_token = huggingface_token
        os.environ["HUGGINGFACE_API_KEY"] = huggingface_token
    
    # Save updated config
    config_manager = ConfigManager()
    config_manager.update_config({
        'llm': {'api_key': config.llm.api_key},
        'models': {'huggingface_token': config.models.huggingface_token}
    })

def print_api_status() -> None:
    """Print current API key status"""
    config = get_config()
    
    logging.info("🔑 API Keys Status:")
    logging.info(f"  DeepSeek: {'✅ Valid' if validate_deepseek_key(config.llm.api_key) else '❌ Invalid/Missing'}")
    logging.info(f"  HuggingFace: {'✅ Valid' if validate_huggingface_token(config.models.huggingface_token) else '❌ Invalid/Missing'}")

def is_deepseek_key_valid() -> bool:
    """Check if DeepSeek API key is valid"""
    config = get_config()
    return validate_deepseek_key(config.llm.api_key)

# ============================================================================
# GLOBAL CONFIGURATION INSTANCE
# ============================================================================

_config_manager = None

def get_config() -> EnhancedConfig:
    """Get global configuration instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager.get_config()

def get_config_manager() -> ConfigManager:
    """Get global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager

def update_config(updates: Dict[str, Any]):
    
    """Update global configuration"""
    config_manager = get_config_manager()
    config_manager.update_config(updates)

def validate_config() -> List[str]:
    """Validate global configuration"""
    config_manager = get_config_manager()
    return config_manager.validate_config()

def is_config_valid() -> bool:
    """Check if configuration is valid"""
    return len(validate_config()) == 0

def get_config_issues() -> List[str]:
    """Get list of configuration issues"""
    return validate_config()

def export_config(format: str = "json") -> str:
    """Export configuration to string"""
    config = get_config()
    config_dict = asdict(config)
    
    if format.lower() == "json":
        return json.dumps(config_dict, indent=2, default=str)
    elif format.lower() == "yaml":
        return yaml.dump(config_dict, default_flow_style=False)
    else:
        raise ValueError(f"Unsupported format: {format}")

def import_config(config_data: str, format: str = "json"):
    
    """Import configuration from string"""
    if format.lower() == "json":
        config_dict = json.loads(config_data)
    elif format.lower() == "yaml":
        config_dict = yaml.safe_load(config_data)
    else:
        raise ValueError(f"Unsupported format: {format}")
    
    config_manager = get_config_manager()
    config_manager._config = config_manager._dict_to_config(config_dict)
    config_manager._save_config()

# ============================================================================
# ENVIRONMENT-SPECIFIC CONFIGS
# ============================================================================

def get_development_config() -> EnhancedConfig:
    """Get development configuration"""
    config = get_config()
    config.environment = "development"
    config.logging.log_level = "DEBUG"
    config.performance.enable_monitoring = True
    return config

def get_production_config() -> EnhancedConfig:
    """Get production configuration"""
    config = get_config()
    config.environment = "production"
    config.logging.log_level = "WARNING"
    config.security.enable_encryption = True
    config.performance.enable_monitoring = True
    return config

def get_testing_config() -> EnhancedConfig:
    """Get testing configuration"""
    config = get_config()
    config.environment = "testing"
    config.logging.log_level = "DEBUG"
    config.database.sqlite_path = "data/test_database.db"
    config.logging.log_file = "logs/test.log"
    return config

# ============================================================================
# CONFIGURATION UTILITIES
# ============================================================================

def create_config_backup() -> str:
    """Create configuration backup"""
    config_manager = get_config_manager()
    backup_path = f"{config_manager.config_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    with open(config_manager.config_path, 'r') as src, open(backup_path, 'w') as dst:
        dst.write(src.read())
    
    return backup_path

def restore_config_backup(backup_path: str):
    
    """Restore configuration from backup"""
    config_manager = get_config_manager()
    
    if not Path(backup_path).exists():
        raise FileNotFoundError(f"Backup file not found: {backup_path}")
    
    with open(backup_path, 'r') as src, open(config_manager.config_path, 'w') as dst:
        dst.write(src.read())
    
    # Reload configuration
    config_manager._load_config()

# ============================================================================
# INITIALIZATION
# ============================================================================

def initialize_config() -> None:
    """Initialize configuration system"""
    try:
        config = get_config()
        logger.info(f"Configuration loaded: {config.config_version}")
        
        # Validate configuration
        issues = validate_config()
        if issues:
            logger.warning(f"Configuration issues found: {issues}")
        
        return True
    except Exception as e:
        logger.error(f"Failed to initialize configuration: {e}")
        return False

# Initialize configuration on import
initialize_config() 