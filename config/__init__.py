"""
Configuration package for Enhanced BASED GOD CLI
"""

from .deepcli_config import (
    get_config, 
    get_config_manager, 
    update_config, 
    validate_config,
    update_api_keys,
    validate_deepseek_key,
    validate_huggingface_token
)

__all__ = [
    "get_config",
    "get_config_manager",
    "update_config",
    "validate_config",
    "update_api_keys",
    "validate_deepseek_key",
    "validate_huggingface_token"
]
