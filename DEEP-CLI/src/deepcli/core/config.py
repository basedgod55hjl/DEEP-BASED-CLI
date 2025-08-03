"""
Configuration management for DeepCLI
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional
import toml
import yaml
from pydantic import BaseModel, Field, validator
from .models import DeepSeekModel


class DeepCLIConfig(BaseModel):
    """Main configuration for DeepCLI"""
    
    # API Configuration - Hardcoded default API key
    api_key: str = Field(default="sk-9af038dd3bdd46258c4a9d02850c9a6d", env="DEEPSEEK_API_KEY")
    base_url: str = Field(default="https://api.deepseek.com/v1", env="DEEPSEEK_API_ENDPOINT")
    beta_url: str = Field(default="https://api.deepseek.com/beta")
    
    # Model Configuration
    default_model: DeepSeekModel = Field(default=DeepSeekModel.CHAT)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4096, gt=0)
    
    # Request Configuration
    max_retries: int = Field(default=3, ge=0)
    retry_delay: float = Field(default=1.0, ge=0.0)
    timeout: float = Field(default=60.0, gt=0.0)
    
    # Memory Configuration
    memory_db_path: Path = Field(default=Path.home() / ".deepcli" / "memory.db")
    memory_enabled: bool = Field(default=True)
    
    # GitHub Configuration
    github_token: Optional[str] = Field(default=None, env="GITHUB_TOKEN")
    github_repo: Optional[str] = Field(default=None)
    
    # MCP Configuration
    mcp_servers_config: Path = Field(default=Path.home() / ".deepcli" / "mcp_servers.json")
    mcp_enabled: bool = Field(default=False)
    
    # UI Configuration
    use_rich: bool = Field(default=True)
    color_theme: str = Field(default="default")
    
    # Logging Configuration
    log_level: str = Field(default="INFO")
    log_file: Optional[Path] = Field(default=None)
    
    @validator("api_key")
    def validate_api_key(cls, v: str) -> str:
        """Validate API key is provided"""
        if not v:
            # Try to get from environment or use default
            v = os.getenv("DEEPSEEK_API_KEY", "sk-9af038dd3bdd46258c4a9d02850c9a6d")
        if not v:
            raise ValueError("DEEPSEEK_API_KEY is required")
        return v
    
    @validator("memory_db_path", "mcp_servers_config", "log_file", pre=True)
    def expand_paths(cls, v: Optional[Path]) -> Optional[Path]:
        """Expand user paths"""
        if v is None:
            return v
        if isinstance(v, str):
            v = Path(v)
        return v.expanduser().resolve()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


class ConfigManager:
    """Manage configuration loading and saving"""
    
    DEFAULT_CONFIG_PATH = Path.home() / ".deepcli" / "config.toml"
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self._config: Optional[DeepCLIConfig] = None
    
    def load(self) -> DeepCLIConfig:
        """Load configuration from file or create default"""
        if self._config is not None:
            return self._config
        
        if self.config_path.exists():
            try:
                with open(self.config_path, "r") as f:
                    data = toml.load(f)
                self._config = DeepCLIConfig(**data)
            except Exception as e:
                print(f"Warning: Failed to load config from {self.config_path}: {e}")
                self._config = DeepCLIConfig()
        else:
            # Create default config with hardcoded API key
            self._config = DeepCLIConfig()
            self.save()
        
        return self._config
    
    def save(self) -> None:
        """Save current configuration to file"""
        if self._config is None:
            return
        
        # Convert to dict and remove None values
        data = self._config.dict(exclude_none=True)
        
        # Convert Path objects to strings
        for key, value in data.items():
            if isinstance(value, Path):
                data[key] = str(value)
        
        # Save to file
        with open(self.config_path, "w") as f:
            toml.dump(data, f)
    
    def update(self, **kwargs: Any) -> None:
        """Update configuration values"""
        if self._config is None:
            self.load()
        
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
        
        self.save()
    
    def get_mcp_servers(self) -> Dict[str, Any]:
        """Load MCP server configurations"""
        if not self._config:
            self.load()
        
        if not self._config.mcp_servers_config.exists():
            return {}
        
        try:
            with open(self._config.mcp_servers_config, "r") as f:
                return yaml.safe_load(f) or {}
        except Exception:
            return {}
    
    def save_mcp_servers(self, servers: Dict[str, Any]) -> None:
        """Save MCP server configurations"""
        if not self._config:
            self.load()
        
        self._config.mcp_servers_config.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self._config.mcp_servers_config, "w") as f:
            yaml.dump(servers, f, default_flow_style=False)


# Global config manager instance
config_manager = ConfigManager()


def get_config() -> DeepCLIConfig:
    """Get the current configuration"""
    return config_manager.load()


def update_config(**kwargs: Any) -> None:
    """Update configuration values"""
    config_manager.update(**kwargs)