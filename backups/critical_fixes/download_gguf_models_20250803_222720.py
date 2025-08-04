#!/usr/bin/env python3
"""
Download GGUF models for DEEP-CLI
"""

import os
from typing import List, Dict, Any, Optional, Tuple

import sys
from pathlib import Path
from huggingface_hub import hf_hub_download
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_gguf_models() -> None:
    """Download GGUF models for the system"""
    
    # Create models directory
    models_dir = Path("data/models")
    models_dir.mkdir(parents=True, exist_ok=True)
    
    # Models to download
    models = [
        {
            "repo_id": "Qwen/Qwen3-Embedding-0.6B-GGUF",
            "filename": "qwen3-embedding-0.6b.gguf",
            "local_name": "qwen3-embedding-0.6b.gguf"
        },
        {
            "repo_id": "Qwen/Qwen3-Embedding-4B-GGUF", 
            "filename": "qwen3-embedding-4b.gguf",
            "local_name": "qwen3-embedding-4b.gguf"
        }
    ]
    
    # HuggingFace token (hardcoded as in the original system)
    token = "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"
    
    for model in models:
        try:
            logger.info(f"Downloading {model['repo_id']}...")
            
            # Check if model already exists
            local_path = models_dir / model["local_name"]
            if local_path.exists():
                logger.info(f"Model already exists: {local_path}")
                continue
            
            # Download the model
            model_path = hf_hub_download(
                repo_id=model["repo_id"],
                filename=model["filename"],
                token=token,
                local_dir=str(models_dir)
            )
            
            logger.info(f"Successfully downloaded: {model_path}")
            
        except Exception as e:
            logger.error(f"Failed to download {model['repo_id']}: {e}")
            continue
    
    # List downloaded models
    logger.info("Downloaded models:")
    for model_file in models_dir.glob("*.gguf"):
        size_mb = model_file.stat().st_size / (1024 * 1024)
        logger.info(f"  {model_file.name} ({size_mb:.1f} MB)")

if __name__ == "__main__":
    download_gguf_models() 