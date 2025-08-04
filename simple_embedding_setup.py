#!/usr/bin/env python3
"""
Simple Embedding Setup for DEEP-CLI
Uses sentence-transformers for local embeddings
"""

import os
from typing import List, Dict, Any, Optional, Tuple

import sys
from pathlib import Path
import logging
import numpy as np
from sentence_transformers import SentenceTransformer
import hashlib
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleEmbeddingSystem:
    """Simple embedding system using sentence-transformers"""
    
    def __init__(self, model_name="all-MiniLM-L6-v2") -> Any:
        self.model_name = model_name
        self.model = None
        self.embedding_dim = 384  # Default for all-MiniLM-L6-v2
        
        # Create directories
        self.data_dir = Path("data")
        self.models_dir = self.data_dir / "models"
        self.embeddings_dir = self.data_dir / "embeddings"
        self.cache_dir = self.data_dir / "cache"
        
        for dir_path in [self.data_dir, self.models_dir, self.embeddings_dir, self.cache_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def initialize_model(self) -> Any:
        """Initialize the sentence transformer model"""
        try:
            logger.info(f"Loading model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("Model loaded successfully!")
            return True
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False
    
    def create_embedding(self, text: str) -> np.ndarray:
        """Create embedding for a text"""
        if self.model is None:
            if not self.initialize_model():
                # Fallback to simple hash-based embedding
                return self._create_hash_embedding(text)
        
        try:
            embedding = self.model.encode(text)
            return embedding
        except Exception as e:
            logger.error(f"Failed to create embedding: {e}")
            return self._create_hash_embedding(text)
    
    def _create_hash_embedding(self, text: str) -> np.ndarray:
        """Create a simple hash-based embedding as fallback"""
        # Create a simple hash-based embedding
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Convert to numpy array
        embedding = np.frombuffer(hash_bytes, dtype=np.float32)
        
        # Pad or truncate to embedding_dim
        if len(embedding) < self.embedding_dim:
            padding = np.zeros(self.embedding_dim - len(embedding), dtype=np.float32)
            embedding = np.concatenate([embedding, padding])
        else:
            embedding = embedding[:self.embedding_dim]
        
        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        return embedding
    
    def compute_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Compute cosine similarity between two vectors"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def batch_create_embeddings(self, texts: list, batch_size: int = 32) -> list:
        """Create embeddings for multiple texts"""
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = []
            
            for text in batch:
                embedding = self.create_embedding(text)
                batch_embeddings.append(embedding)
            
            embeddings.extend(batch_embeddings)
        
        return embeddings
    
    def test_embedding(self) -> bool:
        """Test the embedding system"""
        try:
            test_texts = [
                "Hello world",
                "This is a test",
                "Embedding system working"
            ]
            
            embeddings = self.batch_create_embeddings(test_texts)
            
            if len(embeddings) != len(test_texts):
                logger.error("Embedding count mismatch")
                return False
            
            # Test similarity
            sim = self.compute_similarity(embeddings[0], embeddings[1])
            logger.info(f"Similarity test: {sim:.4f}")
            
            logger.info("Embedding system test passed!")
            return True
            
        except Exception as e:
            logger.error(f"Embedding test failed: {e}")
            return False
    
    def save_embeddings(self, embeddings: list, filename: str):
    """save_embeddings function."""
        """Save embeddings to file"""
        filepath = self.embeddings_dir / filename
        np.save(filepath, np.array(embeddings))
        logger.info(f"Saved embeddings to: {filepath}")
    
    def load_embeddings(self, filename: str) -> np.ndarray:
        """Load embeddings from file"""
        filepath = self.embeddings_dir / filename
        if filepath.exists():
            embeddings = np.load(filepath)
            logger.info(f"Loaded embeddings from: {filepath}")
            return embeddings
        else:
            logger.error(f"Embeddings file not found: {filepath}")
            return np.array([])

def setup_embedding_system() -> None:
    """Set up the embedding system"""
    logger.info("Setting up embedding system...")
    
    # Initialize embedding system
    embedding_system = SimpleEmbeddingSystem()
    
    # Test the system
    if embedding_system.test_embedding():
        logger.info("✅ Embedding system setup successful!")
        
        # Save system info
        system_info = {
            "model_name": embedding_system.model_name,
            "embedding_dim": embedding_system.embedding_dim,
            "status": "working"
        }
        
        info_file = embedding_system.data_dir / "embedding_system_info.json"
        with open(info_file, 'w') as f:
            json.dump(system_info, f, indent=2)
        
        logger.info(f"System info saved to: {info_file}")
        return embedding_system
    else:
        logger.error("❌ Embedding system setup failed!")
        return None

if __name__ == "__main__":
    setup_embedding_system() 