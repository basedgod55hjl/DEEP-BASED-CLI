"""
DeepCLI - A powerful AI-powered CLI for DeepSeek models
"""

__version__ = "2.0.0"
__author__ = "DEEP-CLI Team"

from .core.client import DeepSeekClient
from .core.models import DeepSeekModel, ResponseFormat
from .core.config import DeepCLIConfig

__all__ = [
    "DeepSeekClient",
    "DeepSeekModel", 
    "ResponseFormat",
    "DeepCLIConfig",
]