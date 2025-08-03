#!/usr/bin/env python3
"""
Simple Embedding System for DEEP-CLI
Uses TF-IDF and local processing for embeddings without external dependencies
"""

import numpy as np
import hashlib
import json
import pickle
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from datetime import datetime

logger = logging.getLogger(__name__)

class SimpleEmbeddingSystem:
    """Simple embedding system using TF-IDF"""
    
    def __init__(self, embedding_dim: int = 512):
        self.embedding_dim = embedding_dim
        self.vectorizer = TfidfVectorizer(
            max_features=embedding_dim,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95
        )
        
        # Initialize with sample Deanna-specific text
        self._initialize_vectorizer()
        
        logger.info(f"Simple embedding system initialized with dimension {embedding_dim}")
    
    def _initialize_vectorizer(self):
        """Initialize TF-IDF vectorizer with Deanna-specific sample text"""
        sample_texts = [
            "Deanna is a flirtatious and provocative AI companion from Cincinnati",
            "She uses AAVE and explicit language in her conversations",
            "Her personality is bold unfiltered and explicitly provocative",
            "She works at UDF and has multiple partners including the user's brother",
            "She loves BBC and gangbangs and records content for OnlyFans",
            "Her conversation style is short direct and filled with attitude",
            "She uses emojis sparingly but effectively in her messages",
            "She has anxiety features that cause double or triple texting",
            "She records every interaction especially dick sucking videos",
            "She has a complex relationship with the user's brother Derrick",
            "She loves to make the user feel like a cuckold",
            "She frequently mentions other men she's sleeping with",
            "She enjoys making the user watch or listen to sexual exploits",
            "She is known as the throat goat around the city",
            "She has a preference for BBC and larger men",
            "She works part-time at UDF but makes most money through sexual activities",
            "She drives a Tiffany blue BMW despite limited income",
            "She keeps her appearance well-maintained like a baddie",
            "She loves threesomes and gangbangs always looking for new experiences",
            "She has a traumatic childhood that led to hypersexuality"
        ]
        
        self.vectorizer.fit(sample_texts)
        logger.info("TF-IDF vectorizer initialized with Deanna-specific data")
    
    def create_embedding(self, text: str) -> np.ndarray:
        """Create embedding vector for text"""
        try:
            # Clean and preprocess text
            cleaned_text = self._preprocess_text(text)
            
            # Create TF-IDF vector
            vector = self.vectorizer.transform([cleaned_text]).toarray()[0]
            
            # Pad or truncate to target dimension
            if len(vector) < self.embedding_dim:
                vector = np.pad(vector, (0, self.embedding_dim - len(vector)))
            else:
                vector = vector[:self.embedding_dim]
            
            # Normalize vector
            norm = np.linalg.norm(vector)
            if norm > 0:
                vector = vector / norm
            
            return vector
            
        except Exception as e:
            logger.error(f"Error creating embedding: {e}")
            # Return zero vector as fallback
            return np.zeros(self.embedding_dim)
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for embedding"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation except for important characters
        text = re.sub(r'[^\w\s@#$%&*]', ' ', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Limit length
        if len(text) > 1000:
            text = text[:1000]
        
        return text
    
    def compute_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Compute cosine similarity between two vectors"""
        try:
            # Ensure vectors are 2D for sklearn
            vec1_2d = vec1.reshape(1, -1)
            vec2_2d = vec2.reshape(1, -1)
            
            similarity = cosine_similarity(vec1_2d, vec2_2d)[0][0]
            return float(similarity)
        except Exception as e:
            logger.error(f"Error computing similarity: {e}")
            return 0.0
    
    def search_similar_memory(self, query: str, memory_entries: List[Dict[str, Any]], 
                            limit: int = 10, threshold: float = 0.1) -> List[Dict[str, Any]]:
        """Search for similar memory entries using embeddings"""
        # Create embedding for query
        query_embedding = self.create_embedding(query)
        
        results = []
        for entry in memory_entries:
            # Create embedding for memory content
            content_embedding = self.create_embedding(entry.get('content', ''))
            
            # Compute similarity
            similarity = self.compute_similarity(query_embedding, content_embedding)
            
            if similarity >= threshold:
                result = entry.copy()
                result['similarity'] = similarity
                results.append(result)
        
        # Sort by similarity and importance
        results.sort(key=lambda x: (x.get('similarity', 0), x.get('importance', 0)), reverse=True)
        
        return results[:limit]
    
    def batch_create_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        """Create embeddings for multiple texts"""
        embeddings = []
        
        for text in texts:
            embedding = self.create_embedding(text)
            embeddings.append(embedding)
        
        return embeddings
    
    def test_embedding(self) -> bool:
        """Test if embedding system is working"""
        try:
            test_text = "Deanna is a flirtatious AI companion"
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
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get information about the embedding system"""
        return {
            'type': 'TF-IDF',
            'embedding_dimension': self.embedding_dim,
            'vectorizer_features': len(self.vectorizer.get_feature_names_out()),
            'model': 'Local TF-IDF',
            'cuda_enabled': False,
            'local': True
        }

# Global instance
simple_embedding_system = SimpleEmbeddingSystem()

if __name__ == "__main__":
    print("Testing Simple Embedding System...")
    
    # Test embedding
    if simple_embedding_system.test_embedding():
        print("✅ Simple embedding system is working!")
        
        # Test similarity
        text1 = "Deanna is a flirtatious AI companion"
        text2 = "She uses explicit language and AAVE"
        text3 = "Completely different topic about cooking"
        
        emb1 = simple_embedding_system.create_embedding(text1)
        emb2 = simple_embedding_system.create_embedding(text2)
        emb3 = simple_embedding_system.create_embedding(text3)
        
        sim12 = simple_embedding_system.compute_similarity(emb1, emb2)
        sim13 = simple_embedding_system.compute_similarity(emb1, emb3)
        
        print(f"Similarity between '{text1}' and '{text2}': {sim12:.4f}")
        print(f"Similarity between '{text1}' and '{text3}': {sim13:.4f}")
        
        # Get system info
        info = simple_embedding_system.get_system_info()
        print(f"System info: {info}")
        
    else:
        print("❌ Simple embedding system failed!") 