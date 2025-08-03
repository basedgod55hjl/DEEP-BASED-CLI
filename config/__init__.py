"""
Configuration package for Enhanced BASED GOD CLI
"""

from .deepcli_config import get_config, get_config_manager, update_config, validate_config

__all__ = [
    "get_config",
    "get_config_manager",
    "update_config",
    "validate_config",
]
