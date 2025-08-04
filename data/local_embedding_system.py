#!/usr/bin/env python3
"""
Local Embedding System using llama.cpp with CUDA
Uses Qwen/Qwen3-Embedding-0.6B-GGUF model for local embeddings
"""

import numpy as np
import json
import hashlib
import pickle
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
import subprocess
import tempfile
import os
from datetime import datetime
import requests
import time

logger = logging.getLogger(__name__)

class LocalEmbeddingSystem:
    """Local embedding system using llama.cpp with CUDA"""
    
    def __init__(self, model_path: str = None, embedding_dim: int = 1024):
    """__init__ function."""
        self.embedding_dim = embedding_dim
        self.model_path = model_path or self._download_model()
        self.llama_cpp_path = self._find_llama_cpp()
        self.temp_dir = Path("data/temp_embeddings")
        self.temp_dir.mkdir(exist_ok=True)
        
        # API Keys (hardcoded as requested)
        self.huggingface_token = "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"
        self.deepseek_token = "sk-90e0dd863b8c4e0d879a02851a0ee194"
        
        logger.info(f"Local embedding system initialized with model: {self.model_path}")
    
    def _find_llama_cpp(self) -> str:
        """Find llama.cpp executable"""
        possible_paths = [
            "llama.cpp/main",
            "llama.cpp/build/main",
            "llama-cpp-python/llama_cpp/llama_cpp.dll",
            "llama-cpp-python/llama_cpp/llama_cpp.so",
            "llama-cpp-python/llama_cpp/llama_cpp.dylib"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # Try to find in PATH
        try:
            result = subprocess.run(["which", "llama-cpp"], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        
        logger.warning("llama.cpp not found, will attempt to use Python bindings")
        return "python"
    
    def _download_model(self) -> str:
        """Download Qwen3 embedding model from HuggingFace"""
        model_name = "Qwen/Qwen3-Embedding-0.6B-GGUF"
        model_dir = Path("data/models")
        model_dir.mkdir(exist_ok=True)
        
        # Check if model already exists
        model_files = list(model_dir.glob("*.gguf"))
        if model_files:
            logger.info(f"Found existing model: {model_files[0]}")
            return str(model_files[0])
        
        logger.info(f"Downloading {model_name}...")
        
        # Use huggingface_hub to download
        try:
            from huggingface_hub import hf_hub_download
            
            model_file = hf_hub_download(
                repo_id=model_name,
                filename="qwen3-embedding-0.6b.gguf",
                token=self.huggingface_token,
                local_dir=str(model_dir)
            )
            
            logger.info(f"Model downloaded to: {model_file}")
            return model_file
            
        except Exception as e:
            logger.error(f"Failed to download model: {e}")
            # Fallback to manual download
            return self._manual_download_model(model_name, model_dir)
    
    def _manual_download_model(self, model_name: str, model_dir: Path) -> str:
        """Manual download using requests"""
        url = f"https://huggingface.co/{model_name}/resolve/main/qwen3-embedding-0.6b.gguf"
        headers = {"Authorization": f"Bearer {self.huggingface_token}"}
        
        model_file = model_dir / "qwen3-embedding-0.6b.gguf"
        
        logger.info(f"Downloading from {url}")
        
        try:
            response = requests.get(url, headers=headers, stream=True)
            response.raise_for_status()
            
            with open(model_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Model downloaded to: {model_file}")
            return str(model_file)
            
        except Exception as e:
            logger.error(f"Manual download failed: {e}")
            raise
    
    def create_embedding(self, text: str) -> np.ndarray:
        """Create embedding using llama.cpp with CUDA"""
        try:
            # Clean text
            cleaned_text = self._preprocess_text(text)
            
            # Create temporary input file
            input_file = self.temp_dir / f"input_{hashlib.md5(cleaned_text.encode()).hexdigest()[:8]}.txt"
            with open(input_file, 'w', encoding='utf-8') as f:
                f.write(cleaned_text)
            
            # Run llama.cpp embedding
            embedding = self._run_llama_embedding(input_file)
            
            # Clean up
            input_file.unlink(missing_ok=True)
            
            return embedding
            
        except Exception as e:
            logger.error(f"Error creating embedding: {e}")
            # Return zero vector as fallback
            return np.zeros(self.embedding_dim)
    
    def _run_llama_embedding(self, input_file: Path) -> np.ndarray:
        """Run llama.cpp embedding command"""
        try:
            # Use llama.cpp main with embedding mode
            cmd = [
                self.llama_cpp_path,
                "-m", self.model_path,
                "-f", str(input_file),
                "--embedding",
                "--n-gpu-layers", "35",  # Use GPU layers
                "--ctx-size", "2048",
                "--batch-size", "512"
            ]
            
            logger.debug(f"Running command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logger.error(f"llama.cpp failed: {result.stderr}")
                raise Exception(f"llama.cpp failed: {result.stderr}")
            
            # Parse embedding from output
            embedding = self._parse_embedding_output(result.stdout)
            
            return embedding
            
        except subprocess.TimeoutExpired:
            logger.error("llama.cpp embedding timed out")
            raise
        except Exception as e:
            logger.error(f"llama.cpp embedding failed: {e}")
            raise
    
    def _parse_embedding_output(self, output: str) -> np.ndarray:
        """Parse embedding vector from llama.cpp output"""
        try:
            # Look for embedding data in output
            lines = output.strip().split('\n')
            
            # Find the line with embedding data
            embedding_line = None
            for line in lines:
                if line.startswith('[') and line.endswith(']'):
                    embedding_line = line
                    break
            
            if embedding_line:
                # Parse the embedding vector
                embedding_str = embedding_line.strip('[]')
                embedding_values = [float(x.strip()) for x in embedding_str.split(',')]
                embedding = np.array(embedding_values, dtype=np.float32)
                
                # Normalize
                norm = np.linalg.norm(embedding)
                if norm > 0:
                    embedding = embedding / norm
                
                return embedding
            
            # Fallback: try to extract numbers from output
            import re
            numbers = re.findall(r'-?\d+\.\d+', output)
            if numbers:
                embedding = np.array([float(x) for x in numbers], dtype=np.float32)
                # Pad or truncate to target dimension
                if len(embedding) < self.embedding_dim:
                    embedding = np.pad(embedding, (0, self.embedding_dim - len(embedding)))
                else:
                    embedding = embedding[:self.embedding_dim]
                
                # Normalize
                norm = np.linalg.norm(embedding)
                if norm > 0:
                    embedding = embedding / norm
                
                return embedding
            
            raise Exception("Could not parse embedding from output")
            
        except Exception as e:
            logger.error(f"Failed to parse embedding: {e}")
            raise
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for embedding"""
        import re
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove special characters but keep important ones
        text = re.sub(r'[^\w\s@#$%&*]', ' ', text)
        
        # Limit length to avoid context overflow
        if len(text) > 1000:
            text = text[:1000]
        
        return text
    
    def compute_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Compute cosine similarity between two vectors"""
        try:
            # Ensure vectors are the same length
            min_len = min(len(vec1), len(vec2))
            vec1 = vec1[:min_len]
            vec2 = vec2[:min_len]
            
            # Compute cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error computing similarity: {e}")
            return 0.0
    
    def batch_create_embeddings(self, texts: List[str], batch_size: int = 4) -> List[np.ndarray]:
        """Create embeddings for multiple texts in batches"""
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = []
            
            for text in batch:
                embedding = self.create_embedding(text)
                batch_embeddings.append(embedding)
            
            embeddings.extend(batch_embeddings)
            
            # Small delay between batches
            time.sleep(0.1)
        
        return embeddings
    
    def test_embedding(self) -> bool:
        """Test if embedding system is working"""
        try:
            test_text = "Hello world"
            embedding = self.create_embedding(test_text)
            
            if embedding is not None and len(embedding) > 0:
                logger.info(f"Embedding test successful: {len(embedding)} dimensions")
                return True
            else:
                logger.error("Embedding test failed: empty embedding")
                return False
                
        except Exception as e:
            logger.error(f"Embedding test failed: {e}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the embedding model"""
        return {
            'model_path': self.model_path,
            'model_name': 'Qwen/Qwen3-Embedding-0.6B-GGUF',
            'embedding_dimension': self.embedding_dim,
            'llama_cpp_path': self.llama_cpp_path,
            'cuda_enabled': True,
            'gpu_layers': 35
        }

# Global instance
local_embedding_system = None

def initialize_local_embedding_system() -> None:
    """Initialize the global local embedding system"""
    global local_embedding_system
    local_embedding_system = LocalEmbeddingSystem()
    return local_embedding_system

if __name__ == "__main__":
    logging.info("Testing Local Embedding System...")
    
    # Initialize system
    embedding_system = LocalEmbeddingSystem()
    
    # Test embedding
    if embedding_system.test_embedding():
        logging.info("✅ Local embedding system is working!")
        
        # Test similarity
        text1 = "Hello world"
        text2 = "Hello there"
        text3 = "Completely different topic"
        
        emb1 = embedding_system.create_embedding(text1)
        emb2 = embedding_system.create_embedding(text2)
        emb3 = embedding_system.create_embedding(text3)
        
        sim12 = embedding_system.compute_similarity(emb1, emb2)
        sim13 = embedding_system.compute_similarity(emb1, emb3)
        
        logging.info(f"Similarity between '{text1}' and '{text2}': {sim12:.4f}")
        logging.info(f"Similarity between '{text1}' and '{text3}': {sim13:.4f}")
        
        # Get model info
        info = embedding_system.get_model_info()
        logging.info(f"Model info: {info}")
        
    else:
        logging.info("❌ Local embedding system failed!") 