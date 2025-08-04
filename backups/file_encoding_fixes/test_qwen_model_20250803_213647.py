#!/usr/bin/env python3
"""
Test Qwen3 Embedding Model
Tests the downloaded model for embedding generation
"""

import os
import sys
from pathlib import Path
import logging
import torch
from sentence_transformers import SentenceTransformer
import numpy as np

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_qwen_embedding():
    """Test the downloaded Qwen3 embedding model"""
    
    try:
        models_dir = Path("data/models")
        model_path = models_dir / "qwen3_embedding"
        
        if not model_path.exists():
            logger.error("Model not found. Please download the model first.")
            return False
        
        logger.info("Loading Qwen3 embedding model...")
        
        # Load the model using sentence-transformers
        model = SentenceTransformer(str(model_path))
        
        logger.info("✅ Model loaded successfully!")
        
        # Test embeddings
        test_texts = [
            "Hello world",
            "This is a test sentence",
            "The quick brown fox jumps over the lazy dog",
            "Machine learning is fascinating"
        ]
        
        logger.info("Generating embeddings...")
        embeddings = model.encode(test_texts)
        
        logger.info(f"✅ Generated {len(embeddings)} embeddings")
        logger.info(f"Embedding shape: {embeddings.shape}")
        logger.info(f"Embedding dimension: {embeddings.shape[1]}")
        
        # Test similarity
        from sklearn.metrics.pairwise import cosine_similarity
        
        # Calculate similarities
        similarities = cosine_similarity(embeddings)
        
        logger.info("Similarity matrix:")
        for i, text1 in enumerate(test_texts):
            for j, text2 in enumerate(test_texts):
                if i <= j:  # Only show upper triangle
                    sim = similarities[i][j]
                    logger.info(f"  '{text1[:20]}...' vs '{text2[:20]}...': {sim:.4f}")
        
        # Test with similar sentences
        similar_texts = [
            "I love machine learning",
            "I enjoy machine learning",
            "Machine learning is great"
        ]
        
        logger.info("\nTesting with similar sentences...")
        similar_embeddings = model.encode(similar_texts)
        similar_similarities = cosine_similarity(similar_embeddings)
        
        for i, text1 in enumerate(similar_texts):
            for j, text2 in enumerate(similar_texts):
                if i < j:  # Only show different pairs
                    sim = similar_similarities[i][j]
                    logger.info(f"  '{text1}' vs '{text2}': {sim:.4f}")
        
        logger.info("✅ Qwen3 embedding model test passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Qwen3 embedding test failed: {e}")
        return False

def create_embedding_system():
    """Create an embedding system using the downloaded model"""
    
    try:
        models_dir = Path("data/models")
        model_path = models_dir / "qwen3_embedding"
        
        if not model_path.exists():
            logger.error("Model not found. Please download the model first.")
            return None
        
        logger.info("Creating embedding system...")
        
        # Load the model
        model = SentenceTransformer(str(model_path))
        
        # Create a simple embedding class
        class QwenEmbeddingSystem:
            def __init__(self, model):
                self.model = model
                self.embedding_dim = model.get_sentence_embedding_dimension()
            
            def create_embedding(self, text: str) -> np.ndarray:
                """Create embedding for a text"""
                return self.model.encode(text)
            
            def create_embeddings(self, texts: list) -> np.ndarray:
                """Create embeddings for multiple texts"""
                return self.model.encode(texts)
            
            def compute_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
                """Compute cosine similarity between two vectors"""
                from sklearn.metrics.pairwise import cosine_similarity
                return cosine_similarity([vec1], [vec2])[0][0]
        
        embedding_system = QwenEmbeddingSystem(model)
        
        logger.info(f"✅ Embedding system created with dimension: {embedding_system.embedding_dim}")
        
        # Save system info
        system_info = {
            "model_path": str(model_path),
            "embedding_dim": embedding_system.embedding_dim,
            "model_type": "Qwen3-Embedding-0.6B",
            "status": "working"
        }
        
        info_file = models_dir / "qwen_embedding_system_info.json"
        import json
        with open(info_file, 'w') as f:
            json.dump(system_info, f, indent=2)
        
        logger.info(f"System info saved to: {info_file}")
        
        return embedding_system
        
    except Exception as e:
        logger.error(f"❌ Failed to create embedding system: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "create":
        create_embedding_system()
    else:
        test_qwen_embedding() 