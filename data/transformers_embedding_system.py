#!/usr/bin/env python3
"""
Transformers Embedding System for DEEP-CLI
Uses Qwen/Qwen3-Embedding-0.6B model with transformers pipeline
"""

import numpy as np
import json
import hashlib
import pickle
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
import torch
from datetime import datetime
import time

logger = logging.getLogger(__name__)

class TransformersEmbeddingSystem:
    """Transformers-based embedding system using Qwen3-Embedding-0.6B"""
    
    def __init__(self, model_name: str = "Qwen/Qwen3-Embedding-0.6B", embedding_dim: int = 1024):
        self.model_name = model_name
        self.embedding_dim = embedding_dim
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # API Keys (hardcoded as requested)
        self.huggingface_token = "hf-your-api-token"
        self.deepseek_token = "sk-your-api-key"
        
        # Initialize pipeline and model
        self.pipeline = None
        self.tokenizer = None
        self.model = None
        
        logger.info(f"Transformers embedding system initialized for {model_name}")
        logger.info(f"Device: {self.device}")
        
        # Initialize the model
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the transformers model and pipeline"""
        try:
            logger.info("Loading Qwen3-Embedding-0.6B model...")
            
            # Method 1: Use pipeline for feature extraction
            try:
                from transformers import pipeline
                
                # Force float32 to avoid BFloat16 issues
                self.pipeline = pipeline(
                    "feature-extraction", 
                    model=self.model_name,
                    token=self.huggingface_token,
                    device=0 if self.device == "cuda" else -1,
                    torch_dtype=torch.float32  # Force float32
                )
                logger.info("Pipeline initialized successfully")
                
            except Exception as e:
                logger.warning(f"Pipeline initialization failed: {e}")
                self.pipeline = None
            
            # Method 2: Load model directly as fallback
            if not self.pipeline:
                try:
                    from transformers import AutoTokenizer, AutoModel
                    
                    self.tokenizer = AutoTokenizer.from_pretrained(
                        self.model_name,
                        token=self.huggingface_token,
                        trust_remote_code=True
                    )
                    
                    # Force float32 to avoid BFloat16 issues
                    self.model = AutoModel.from_pretrained(
                        self.model_name,
                        token=self.huggingface_token,
                        trust_remote_code=True,
                        torch_dtype=torch.float32  # Force float32 instead of auto
                    )
                    
                    if self.device == "cuda":
                        self.model = self.model.cuda()
                    
                    self.model.eval()
                    logger.info("Model loaded directly successfully")
                    
                except Exception as e:
                    logger.error(f"Direct model loading failed: {e}")
                    raise
            
        except Exception as e:
            logger.error(f"Model initialization failed: {e}")
            raise
    
    def create_embedding(self, text: str) -> np.ndarray:
        """Create embedding using transformers pipeline or direct model"""
        try:
            # Clean text
            cleaned_text = self._preprocess_text(text)
            
            if self.pipeline:
                # Use pipeline method
                embedding = self._create_embedding_pipeline(cleaned_text)
            elif self.model and self.tokenizer:
                # Use direct model method
                embedding = self._create_embedding_direct(cleaned_text)
            else:
                raise Exception("No model available for embedding")
            
            # Normalize embedding
            embedding = self._normalize_embedding(embedding)
            
            return embedding
            
        except Exception as e:
            logger.error(f"Error creating embedding: {e}")
            # Return zero vector as fallback
            return np.zeros(self.embedding_dim)
    
    def _create_embedding_pipeline(self, text: str) -> np.ndarray:
        """Create embedding using pipeline"""
        try:
            # Use pipeline for feature extraction
            features = self.pipeline(text, return_tensors="pt")
            
            # Extract the embedding (usually the last hidden state)
            if isinstance(features, dict):
                # Get the last hidden state
                embedding = features['last_hidden_state'].squeeze(0)
            else:
                # Features might be a tensor directly
                embedding = features.squeeze(0)
            
            # Take mean pooling over sequence length
            embedding = embedding.mean(dim=0)
            
            # Convert to numpy
            embedding = embedding.detach().cpu().numpy()
            
            return embedding
            
        except Exception as e:
            logger.error(f"Pipeline embedding failed: {e}")
            raise
    
    def _create_embedding_direct(self, text: str) -> np.ndarray:
        """Create embedding using direct model"""
        try:
            with torch.no_grad():
                # Tokenize input
                inputs = self.tokenizer(
                    text,
                    return_tensors="pt",
                    max_length=512,
                    truncation=True,
                    padding=True
                )
                
                # Move to device
                if self.device == "cuda":
                    inputs = {k: v.cuda() for k, v in inputs.items()}
                
                # Get model outputs
                outputs = self.model(**inputs)
                
                # Extract embeddings (last hidden state)
                embeddings = outputs.last_hidden_state
                
                # Mean pooling over sequence length
                embedding = embeddings.mean(dim=1).squeeze(0)
                
                # Convert to numpy
                embedding = embedding.cpu().numpy()
                
                return embedding
                
        except Exception as e:
            logger.error(f"Direct embedding failed: {e}")
            raise
    
    def _normalize_embedding(self, embedding: np.ndarray) -> np.ndarray:
        """Normalize embedding vector"""
        try:
            # Ensure it's a 1D array
            embedding = embedding.flatten()
            
            # Pad or truncate to target dimension
            if len(embedding) < self.embedding_dim:
                embedding = np.pad(embedding, (0, self.embedding_dim - len(embedding)))
            else:
                embedding = embedding[:self.embedding_dim]
            
            # Normalize to unit length
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
            
            return embedding.astype(np.float32)
            
        except Exception as e:
            logger.error(f"Normalization failed: {e}")
            return np.zeros(self.embedding_dim, dtype=np.float32)
    
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
            'model_name': self.model_name,
            'embedding_dimension': self.embedding_dim,
            'device': self.device,
            'pipeline_available': self.pipeline is not None,
            'direct_model_available': self.model is not None,
            'cuda_available': torch.cuda.is_available(),
            'model_type': 'Qwen3-Embedding-0.6B',
            'precision': 'float32'
        }
    
    def save_embeddings_cache(self, embeddings: Dict[str, np.ndarray], cache_file: str):
        """Save embeddings to cache file"""
        try:
            cache_path = Path("data/embeddings") / cache_file
            cache_path.parent.mkdir(exist_ok=True)
            
            # Convert numpy arrays to lists for JSON serialization
            cache_data = {k: v.tolist() for k, v in embeddings.items()}
            
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f)
            
            logger.info(f"Embeddings cache saved to {cache_path}")
            
        except Exception as e:
            logger.error(f"Failed to save embeddings cache: {e}")
    
    def load_embeddings_cache(self, cache_file: str) -> Dict[str, np.ndarray]:
        """Load embeddings from cache file"""
        try:
            cache_path = Path("data/embeddings") / cache_file
            
            if not cache_path.exists():
                logger.warning(f"Cache file not found: {cache_path}")
                return {}
            
            with open(cache_path, 'r') as f:
                cache_data = json.load(f)
            
            # Convert lists back to numpy arrays
            embeddings = {k: np.array(v, dtype=np.float32) for k, v in cache_data.items()}
            
            logger.info(f"Loaded {len(embeddings)} embeddings from cache")
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to load embeddings cache: {e}")
            return {}

# Global instance
transformers_embedding_system = None

def initialize_transformers_embedding_system():
    """Initialize the global transformers embedding system"""
    global transformers_embedding_system
    transformers_embedding_system = TransformersEmbeddingSystem()
    return transformers_embedding_system

if __name__ == "__main__":
    print("Testing Transformers Embedding System...")
    
    # Initialize system
    embedding_system = TransformersEmbeddingSystem()
    
    # Test embedding
    if embedding_system.test_embedding():
        print("Transformers embedding system is working!")
        
        # Test similarity
        text1 = "Hello world"
        text2 = "Hello there"
        text3 = "Completely different topic"
        
        emb1 = embedding_system.create_embedding(text1)
        emb2 = embedding_system.create_embedding(text2)
        emb3 = embedding_system.create_embedding(text3)
        
        sim12 = embedding_system.compute_similarity(emb1, emb2)
        sim13 = embedding_system.compute_similarity(emb1, emb3)
        
        print(f"Similarity between '{text1}' and '{text2}': {sim12:.4f}")
        print(f"Similarity between '{text1}' and '{text3}': {sim13:.4f}")
        
        # Get model info
        info = embedding_system.get_model_info()
        print(f"Model info: {info}")
        
    else:
        print("Transformers embedding system failed!") 