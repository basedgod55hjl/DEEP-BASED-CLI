#!/usr/bin/env python3
"""
Download Qwen3 Embedding Model
Uses the provided HuggingFace token to download the model
"""

import os
import sys
from pathlib import Path
import logging
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_qwen_model():
    """Download Qwen3 embedding model using the provided token"""
    
    # HuggingFace token
    token = "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"
    
    # Model name
    model_name = "Qwen/Qwen3-Embedding-0.6B"
    
    # Create models directory
    models_dir = Path("data/models")
    models_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        logger.info(f"Downloading {model_name}...")
        
        # Set the token for authentication
        os.environ["HF_TOKEN"] = token
        
        # Download tokenizer
        logger.info("Downloading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            token=token,
            cache_dir=str(models_dir)
        )
        
        # Download model
        logger.info("Downloading model...")
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            token=token,
            cache_dir=str(models_dir),
            torch_dtype=torch.float16,  # Use half precision to save memory
            device_map="auto"  # Automatically handle device placement
        )
        
        logger.info("✅ Model downloaded successfully!")
        
        # Save model info
        model_info = {
            "model_name": model_name,
            "tokenizer_path": str(models_dir / "tokenizer"),
            "model_path": str(models_dir / "model"),
            "status": "downloaded"
        }
        
        # Save tokenizer and model locally
        tokenizer_path = models_dir / "qwen3_embedding_tokenizer"
        model_path = models_dir / "qwen3_embedding_model"
        
        logger.info("Saving tokenizer locally...")
        tokenizer.save_pretrained(tokenizer_path)
        
        logger.info("Saving model locally...")
        model.save_pretrained(model_path)
        
        # Update model info
        model_info["local_tokenizer_path"] = str(tokenizer_path)
        model_info["local_model_path"] = str(model_path)
        
        # Save model info
        info_file = models_dir / "qwen3_model_info.json"
        import json
        with open(info_file, 'w') as f:
            json.dump(model_info, f, indent=2)
        
        logger.info(f"Model info saved to: {info_file}")
        
        # Test the model
        logger.info("Testing model...")
        test_text = "Hello world"
        inputs = tokenizer(test_text, return_tensors="pt")
        
        with torch.no_grad():
            outputs = model(**inputs)
        
        logger.info(f"✅ Model test passed! Input shape: {inputs['input_ids'].shape}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to download model: {e}")
        return False

def test_model_loading():
    """Test loading the downloaded model"""
    try:
        models_dir = Path("data/models")
        tokenizer_path = models_dir / "qwen3_embedding_tokenizer"
        model_path = models_dir / "qwen3_embedding_model"
        
        if not tokenizer_path.exists() or not model_path.exists():
            logger.error("Model files not found. Please download the model first.")
            return False
        
        logger.info("Loading downloaded model...")
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(str(tokenizer_path))
        
        # Load model
        model = AutoModelForCausalLM.from_pretrained(
            str(model_path),
            torch_dtype=torch.float16,
            device_map="auto"
        )
        
        # Test
        test_text = "This is a test"
        inputs = tokenizer(test_text, return_tensors="pt")
        
        with torch.no_grad():
            outputs = model(**inputs)
        
        logger.info("✅ Model loading test passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Model loading test failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_model_loading()
    else:
        download_qwen_model() 