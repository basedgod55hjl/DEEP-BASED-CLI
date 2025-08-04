#!/usr/bin/env python3
"""
API Keys Configuration
Centralized configuration for all API keys used in the Enhanced BASED GOD CLI
"""

import os
from typing import Optional

# DeepSeek API Configuration
# Get from environment variable or use default (needs to be updated)
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-90e0dd863b8c4e0d879a02851a0ee194")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/beta")

# HuggingFace API Configuration (for future use)
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "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")

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
    print(f"✅ DeepSeek API key updated")

def is_deepseek_key_valid() -> bool:
    """Check if DeepSeek API key is valid (basic validation)"""
    return DEEPSEEK_API_KEY.startswith("sk-") and len(DEEPSEEK_API_KEY) > 20

def print_api_status():
    """Print status of all API keys"""
    print("🔑 API Keys Status:")
    print(f"   DeepSeek: {'✅ Valid' if is_deepseek_key_valid() else '❌ Invalid/Expired'}")
    print(f"   HuggingFace: {'✅ Set' if HUGGINGFACE_API_KEY else '❌ Not set'}")
    print(f"   Qdrant: {'✅ Configured' if QDRANT_HOST else '❌ Not configured'}")

if __name__ == "__main__":
    print_api_status() 