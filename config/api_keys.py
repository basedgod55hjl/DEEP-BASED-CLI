#!/usr/bin/env python3
"""
API Keys Configuration
Centralized configuration for all API keys used in the Enhanced BASED GOD CLI
"""

import os
import logging

from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# DeepSeek API Configuration
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")

# HuggingFace API Configuration
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")

# Qdrant Configuration
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")

def get_deepseek_config() -> dict:
    """Get DeepSeek API configuration"""
    return {
        "api_key": DEEPSEEK_API_KEY,
        "base_url": DEEPSEEK_BASE_URL,
        "models": {
            "deepseek_chat": "deepseek-chat",
            "deepseek_coder": "deepseek-coder", 
            "deepseek_reasoner": "deepseek-reasoner"
        }
    }

def update_deepseek_api_key(new_key: str):
    
    """Update DeepSeek API key"""
    global DEEPSEEK_API_KEY
    DEEPSEEK_API_KEY = new_key
    os.environ["DEEPSEEK_API_KEY"] = new_key
    logging.info(f"✅ DeepSeek API key updated")

def is_deepseek_key_valid() -> bool:
    """Check if DeepSeek API key is valid (basic validation)"""
    return DEEPSEEK_API_KEY.startswith("sk-") and len(DEEPSEEK_API_KEY) > 20

def print_api_status() -> None:
    """Print status of all API keys"""
    logging.info("🔑 API Keys Status:")
    logging.info(f"   DeepSeek: {'✅ Valid' if is_deepseek_key_valid() else '❌ Invalid/Expired'}")
    logging.info(f"   HuggingFace: {'✅ Set' if HUGGINGFACE_API_KEY else '❌ Not set'}")
    logging.info(f"   Qdrant: {'✅ Configured' if QDRANT_HOST else '❌ Not configured'}")

if __name__ == "__main__":
    print_api_status() 