#!/usr/bin/env python3
"""
Simple Download Script for Qwen3 Model
"""

import os
import sys
from pathlib import Path
import logging
from huggingface_hub import hf_hub_download, snapshot_download

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_qwen_model():
    """Download Qwen3 embedding model"""
    
    # HuggingFace token
    token = "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"
    
    # Model repository
    repo_id = "Qwen/Qwen3-Embedding-0.6B"
    
    # Create models directory
    models_dir = Path("data/models")
    models_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        logger.info(f"Downloading {repo_id}...")
        
        # Download the entire repository
        local_dir = models_dir / "qwen3_embedding"
        local_dir.mkdir(exist_ok=True)
        
        # Download all files from the repository
        snapshot_download(
            repo_id=repo_id,
            token=token,
            local_dir=str(local_dir),
            local_dir_use_symlinks=False
        )
        
        logger.info(f"✅ Model downloaded to: {local_dir}")
        
        # List downloaded files
        logger.info("Downloaded files:")
        for file_path in local_dir.rglob("*"):
            if file_path.is_file():
                size_mb = file_path.stat().st_size / (1024 * 1024)
                logger.info(f"  {file_path.name} ({size_mb:.1f} MB)")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to download model: {e}")
        return False

def list_available_files():
    """List available files in the repository"""
    try:
        from huggingface_hub import list_repo_files
        
        repo_id = "Qwen/Qwen3-Embedding-0.6B"
        token = "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"
        
        logger.info(f"Listing files in {repo_id}...")
        
        files = list_repo_files(repo_id, token=token)
        
        logger.info("Available files:")
        for file in files:
            logger.info(f"  {file}")
            
    except Exception as e:
        logger.error(f"Failed to list files: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "list":
        list_available_files()
    else:
        download_qwen_model() 