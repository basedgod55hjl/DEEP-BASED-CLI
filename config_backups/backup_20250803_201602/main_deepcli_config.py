"""
Enhanced Configuration Management for DeepCLI
Advanced configuration system with dynamic settings and validation
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

# DeepSeek API Configuration
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-your-api-key")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")

# HuggingFace API Configuration
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "hf-your-api-token")

def update_api_keys(deepseek_key: str = None, huggingface_token: str = None):
    """Update API keys"""
    global DEEPSEEK_API_KEY, HUGGINGFACE_API_KEY
    
    if deepseek_key:
        DEEPSEEK_API_KEY = deepseek_key
        os.environ["DEEPSEEK_API_KEY"] = deepseek_key
        print(f"✅ DeepSeek API key updated")
    
    if huggingface_token:
        HUGGINGFACE_API_KEY = huggingface_token
        os.environ["HUGGINGFACE_API_KEY"] = huggingface_token
        print(f"✅ HuggingFace token updated")

def validate_deepseek_key(key: str = None) -> bool:
    """Check if DeepSeek API key is valid"""
    check_key = key or DEEPSEEK_API_KEY
    return check_key.startswith("sk-") and len(check_key) > 20

def validate_huggingface_token(token: str = None) -> bool:
    """Check if HuggingFace token is valid"""
    check_token = token or HUGGINGFACE_API_KEY
    return check_token.startswith("hf_") and len(check_token) > 20

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
    api_key: str = "sk-your-api-key"
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
    
    def __post_init__(self):
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
    
    # Metadata
    config_version: str = "2.0.0"
    created_at: datetime = None
    last_updated: datetime = None
    environment: str = "development"
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_updated is None:
            self.last_updated = datetime.now()

class ConfigManager:
    """Enhanced configuration manager with dynamic loading and validation"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration manager"""
        self.config_path = config_path or "config/enhanced_config.json"
        self.config: Optional[EnhancedConfig] = None
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file or create default"""
        try:
            if Path(self.config_path).exists():
                self.config = self._load_from_file()
            else:
                self.config = self._create_default_config()
                self._save_config()
                
        except Exception as e:
            logger.error(f"Failed to load configuration: {str(e)}")
            self.config = self._create_default_config()
    
    def _load_from_file(self) -> EnhancedConfig:
        """Load configuration from file"""
        try:
            with open(self.config_path, 'r') as f:
                config_data = json.load(f)
            
            # Convert nested dictionaries to dataclass instances
            return self._dict_to_config(config_data)
            
        except Exception as e:
            logger.error(f"Failed to load configuration from file: {str(e)}")
            return self._create_default_config()
    
    def _dict_to_config(self, config_data: Dict[str, Any]) -> EnhancedConfig:
        """Convert dictionary to EnhancedConfig instance"""
        try:
            # Create nested dataclass instances
            database = DatabaseConfig(**config_data.get("database", {}))
            llm = LLMConfig(**config_data.get("llm", {}))
            persona = PersonaConfig(**config_data.get("persona", {}))
            rag = RAGConfig(**config_data.get("rag", {}))
            memory = MemoryConfig(**config_data.get("memory", {}))
            tool = ToolConfig(**config_data.get("tool", {}))
            security = SecurityConfig(**config_data.get("security", {}))
            performance = PerformanceConfig(**config_data.get("performance", {}))
            logging_config = LoggingConfig(**config_data.get("logging", {}))
            session = SessionConfig(**config_data.get("session", {}))
            features = FeatureFlags(**config_data.get("features", {}))
            
            # Create main config
            config = EnhancedConfig(
                database=database,
                llm=llm,
                persona=persona,
                rag=rag,
                memory=memory,
                tool=tool,
                security=security,
                performance=performance,
                logging=logging_config,
                session=session,
                features=features
            )
            
            # Set metadata
            config.config_version = config_data.get("config_version", "2.0.0")
            config.environment = config_data.get("environment", "development")
            
            return config
            
        except Exception as e:
            logger.error(f"Failed to convert dictionary to config: {str(e)}")
            return self._create_default_config()
    
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
            features=FeatureFlags()
        )
    
    def _save_config(self):
        """Save configuration to file"""
        try:
            # Ensure directory exists
            Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Convert to dictionary
            config_dict = self._config_to_dict(self.config)
            
            # Save to file
            with open(self.config_path, 'w') as f:
                json.dump(config_dict, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Failed to save configuration: {str(e)}")
    
    def _config_to_dict(self, config: EnhancedConfig) -> Dict[str, Any]:
        """Convert EnhancedConfig to dictionary"""
        try:
            config_dict = asdict(config)
            
            # Handle datetime objects
            if config_dict.get("created_at"):
                config_dict["created_at"] = config.created_at.isoformat()
            if config_dict.get("last_updated"):
                config_dict["last_updated"] = config.last_updated.isoformat()
            
            return config_dict
            
        except Exception as e:
            logger.error(f"Failed to convert config to dictionary: {str(e)}")
            return {}
    
    def get_config(self) -> EnhancedConfig:
        """Get current configuration"""
        return self.config
    
    def update_config(self, updates: Dict[str, Any]):
        """Update configuration with new values"""
        try:
            # Update nested configurations
            for section, values in updates.items():
                if hasattr(self.config, section):
                    section_config = getattr(self.config, section)
                    for key, value in values.items():
                        if hasattr(section_config, key):
                            setattr(section_config, key, value)
            
            # Update metadata
            self.config.last_updated = datetime.now()
            
            # Save updated configuration
            self._save_config()
            
            logger.info("Configuration updated successfully")
            
        except Exception as e:
            logger.error(f"Failed to update configuration: {str(e)}")
    
    def validate_config(self) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []
        
        try:
            # Validate database configuration
            if not self.config.database.sqlite_path:
                issues.append("Database SQLite path is required")
            
            # Validate LLM configuration
            if not self.config.llm.api_key:
                issues.append("LLM API key is required")
            
            if self.config.llm.temperature < 0 or self.config.llm.temperature > 2:
                issues.append("LLM temperature must be between 0 and 2")
            
            # Validate RAG configuration
            if self.config.rag.similarity_threshold < 0 or self.config.rag.similarity_threshold > 1:
                issues.append("RAG similarity threshold must be between 0 and 1")
            
            # Validate memory configuration
            if self.config.memory.max_memory_entries <= 0:
                issues.append("Memory max entries must be positive")
            
            # Validate performance configuration
            if self.config.performance.cache_size_mb <= 0:
                issues.append("Cache size must be positive")
            
            # Validate security configuration
            if self.config.security.rate_limit_requests_per_minute <= 0:
                issues.append("Rate limit must be positive")
            
        except Exception as e:
            issues.append(f"Configuration validation error: {str(e)}")
        
        return issues
    
    def get_environment_config(self, environment: str) -> EnhancedConfig:
        """Get environment-specific configuration"""
        try:
            env_config_path = f"config/enhanced_config_{environment}.json"
            
            if Path(env_config_path).exists():
                # Load environment-specific config
                with open(env_config_path, 'r') as f:
                    env_config_data = json.load(f)
                
                # Merge with base config
                base_config_dict = self._config_to_dict(self.config)
                merged_config = self._deep_merge(base_config_dict, env_config_data)
                
                return self._dict_to_config(merged_config)
            else:
                # Return base config with environment flag
                self.config.environment = environment
                return self.config
                
        except Exception as e:
            logger.error(f"Failed to load environment config: {str(e)}")
            return self.config
    
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries"""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def export_config(self, format: str = "json") -> str:
        """Export configuration in specified format"""
        try:
            config_dict = self._config_to_dict(self.config)
            
            if format.lower() == "yaml":
                return yaml.dump(config_dict, default_flow_style=False, indent=2)
            elif format.lower() == "json":
                return json.dumps(config_dict, indent=2, default=str)
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            logger.error(f"Failed to export configuration: {str(e)}")
            return ""
    
    def import_config(self, config_data: str, format: str = "json"):
        """Import configuration from string"""
        try:
            if format.lower() == "yaml":
                config_dict = yaml.safe_load(config_data)
            elif format.lower() == "json":
                config_dict = json.loads(config_data)
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            # Validate imported config
            issues = self._validate_config_dict(config_dict)
            if issues:
                raise ValueError(f"Configuration validation failed: {', '.join(issues)}")
            
            # Update current config
            self.config = self._dict_to_config(config_dict)
            self._save_config()
            
            logger.info("Configuration imported successfully")
            
        except Exception as e:
            logger.error(f"Failed to import configuration: {str(e)}")
            raise
    
    def _validate_config_dict(self, config_dict: Dict[str, Any]) -> List[str]:
        """Validate configuration dictionary"""
        issues = []
        
        # Basic structure validation
        required_sections = ["database", "llm", "persona", "rag", "memory", "tool", 
                           "security", "performance", "logging", "session", "features"]
        
        for section in required_sections:
            if section not in config_dict:
                issues.append(f"Missing required section: {section}")
        
        return issues
    
    def create_backup(self) -> str:
        """Create configuration backup"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"config/backup/enhanced_config_backup_{timestamp}.json"
            
            # Ensure backup directory exists
            Path(backup_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Save backup
            config_dict = self._config_to_dict(self.config)
            with open(backup_path, 'w') as f:
                json.dump(config_dict, f, indent=2, default=str)
            
            logger.info(f"Configuration backup created: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Failed to create configuration backup: {str(e)}")
            return ""
    
    def restore_backup(self, backup_path: str):
        """Restore configuration from backup"""
        try:
            if not Path(backup_path).exists():
                raise FileNotFoundError(f"Backup file not found: {backup_path}")
            
            # Load backup
            with open(backup_path, 'r') as f:
                backup_data = json.load(f)
            
            # Validate and restore
            issues = self._validate_config_dict(backup_data)
            if issues:
                raise ValueError(f"Backup validation failed: {', '.join(issues)}")
            
            self.config = self._dict_to_config(backup_data)
            self._save_config()
            
            logger.info(f"Configuration restored from backup: {backup_path}")
            
        except Exception as e:
            logger.error(f"Failed to restore configuration: {str(e)}")
            raise

# Global configuration instance
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

def get_environment_config(environment: str) -> EnhancedConfig:
    """Get environment-specific configuration"""
    config_manager = get_config_manager()
    return config_manager.get_environment_config(environment)

# Environment-specific configuration helpers
def get_development_config() -> EnhancedConfig:
    """Get development environment configuration"""
    return get_environment_config("development")

def get_production_config() -> EnhancedConfig:
    """Get production environment configuration"""
    return get_environment_config("production")

def get_testing_config() -> EnhancedConfig:
    """Get testing environment configuration"""
    return get_environment_config("testing")

# Configuration validation helpers
def is_config_valid() -> bool:
    """Check if configuration is valid"""
    issues = validate_config()
    return len(issues) == 0

def get_config_issues() -> List[str]:
    """Get configuration validation issues"""
    return validate_config()

# Configuration export/import helpers
def export_config(format: str = "json") -> str:
    """Export configuration"""
    config_manager = get_config_manager()
    return config_manager.export_config(format)

def import_config(config_data: str, format: str = "json"):
    """Import configuration"""
    config_manager = get_config_manager()
    config_manager.import_config(config_data, format)

# Configuration backup helpers
def create_config_backup() -> str:
    """Create configuration backup"""
    config_manager = get_config_manager()
    return config_manager.create_backup()

def restore_config_backup(backup_path: str):
    """Restore configuration from backup"""
    config_manager = get_config_manager()
    config_manager.restore_backup(backup_path)
