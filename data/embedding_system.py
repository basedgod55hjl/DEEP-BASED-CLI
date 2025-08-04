#!/usr/bin/env python3
"""
Enhanced Embedding System for DEEP-CLI
Provides vector embeddings and similarity search for Deanna memory
"""

import numpy as np
import hashlib
import json
import pickle
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import logging
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import string
from datetime import datetime

logger = logging.getLogger(__name__)

class DeannaEmbeddingSystem:
    """Advanced embedding system for Deanna memory"""
    
    def __init__(self, memory_manager, embedding_dim: int = 384):
        self.memory_manager = memory_manager
        self.embedding_dim = embedding_dim
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=embedding_dim,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        # Initialize with sample data to fit vectorizer
        self._initialize_vectorizer()
        
        logger.info(f"Embedding system initialized with dimension {embedding_dim}")
    
    def _initialize_vectorizer(self):
        """Initialize TF-IDF vectorizer with sample text"""
        sample_texts = [
            "Deanna is a flirtatious and provocative AI companion",
            "She uses AAVE and explicit language",
            "Her personality is bold and unfiltered",
            "She works at UDF and has multiple partners",
            "She loves BBC and gangbangs",
            "Her conversation style is short and direct",
            "She uses emojis sparingly but effectively",
            "She has anxiety features and double texts",
            "She records content for OnlyFans",
            "She has a complex relationship with the user's brother"
        ]
        
        self.tfidf_vectorizer.fit(sample_texts)
        logger.info("TF-IDF vectorizer initialized with sample data")
    
    def create_embedding(self, text: str) -> np.ndarray:
        """Create embedding vector for text"""
        # Clean and preprocess text
        cleaned_text = self._preprocess_text(text)
        
        # Create TF-IDF vector
        try:
            vector = self.tfidf_vectorizer.transform([cleaned_text]).toarray()[0]
            
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
    
    def search_similar_memory(self, query: str, limit: int = 10, threshold: float = 0.3) -> List[Dict[str, Any]]:
        """Search for similar memory entries using embeddings"""
        # Create embedding for query
        query_embedding = self.create_embedding(query)
        
        # Get all memory entries
        conn = self.memory_manager.db_path.parent / "deanna_memory.db"
        import sqlite3
        conn = sqlite3.connect(conn)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, category, content, embedding_hash, importance, tags
            FROM memory_entries
            WHERE embedding_hash IS NOT NULL
        ''')
        
        results = []
        for row in cursor.fetchall():
            memory_id, category, content, embedding_hash, importance, tags = row
            
            # Get or create embedding for this content
            embedding = self.memory_manager.get_embedding(embedding_hash)
            if embedding is None:
                # Create new embedding
                embedding = self.create_embedding(content)
                self.memory_manager.store_embedding(content, embedding)
            
            # Compute similarity
            similarity = self.compute_similarity(query_embedding, embedding)
            
            if similarity >= threshold:
                results.append({
                    'id': memory_id,
                    'category': category,
                    'content': content,
                    'similarity': similarity,
                    'importance': importance,
                    'tags': tags
                })
        
        conn.close()
        
        # Sort by similarity and importance
        results.sort(key=lambda x: (x['similarity'], x['importance']), reverse=True)
        
        return results[:limit]
    
    def create_context_embedding(self, context_data: Dict[str, Any]) -> np.ndarray:
        """Create embedding for context data"""
        # Combine all context information into a single text
        context_text = ""
        
        if 'user_input' in context_data:
            context_text += f"User: {context_data['user_input']} "
        
        if 'conversation_history' in context_data:
            for msg in context_data['conversation_history']:
                context_text += f"{msg['role']}: {msg['content']} "
        
        if 'persona_context' in context_data:
            context_text += f"Persona: {context_data['persona_context']} "
        
        if 'emotion_context' in context_data:
            context_text += f"Emotion: {context_data['emotion_context']} "
        
        return self.create_embedding(context_text)
    
    def find_relevant_memories(self, context_data: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
        """Find memories relevant to current context"""
        context_embedding = self.create_context_embedding(context_data)
        
        # Search for similar memories
        results = self.search_similar_memory(
            context_data.get('user_input', ''),
            limit=limit * 2,  # Get more results for filtering
            threshold=0.2
        )
        
        # Filter and enhance results
        enhanced_results = []
        for result in results:
            # Add context relevance score
            memory_embedding = self.memory_manager.get_embedding(result.get('embedding_hash', ''))
            if memory_embedding is not None:
                context_relevance = self.compute_similarity(context_embedding, memory_embedding)
                result['context_relevance'] = context_relevance
                
                # Combined score (similarity + context relevance + importance)
                combined_score = (
                    result['similarity'] * 0.4 +
                    context_relevance * 0.4 +
                    (result['importance'] / 10.0) * 0.2
                )
                result['combined_score'] = combined_score
                
                enhanced_results.append(result)
        
        # Sort by combined score
        enhanced_results.sort(key=lambda x: x['combined_score'], reverse=True)
        
        return enhanced_results[:limit]
    
    def create_persona_embedding(self, persona_config: Dict[str, Any]) -> np.ndarray:
        """Create embedding for persona configuration"""
        # Extract key persona information
        persona_text = ""
        
        if 'personality' in persona_config:
            persona_text += f"Personality: {persona_config['personality']} "
        
        if 'personality_traits' in persona_config:
            traits = persona_config['personality_traits']
            if isinstance(traits, list):
                persona_text += f"Traits: {' '.join(traits)} "
            else:
                persona_text += f"Traits: {traits} "
        
        if 'conversation_style' in persona_config:
            style = persona_config['conversation_style']
            if isinstance(style, dict):
                for key, value in style.items():
                    persona_text += f"{key}: {value} "
            else:
                persona_text += f"Style: {style} "
        
        if 'system_prompt' in persona_config:
            persona_text += f"System: {persona_config['system_prompt']} "
        
        return self.create_embedding(persona_text)
    
    def update_memory_embeddings(self):
        """Update embeddings for all memory entries"""
        conn = sqlite3.connect(self.memory_manager.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, content FROM memory_entries')
        entries = cursor.fetchall()
        
        updated_count = 0
        for entry_id, content in entries:
            # Create embedding
            embedding = self.create_embedding(content)
            
            # Store embedding
            self.memory_manager.store_embedding(content, embedding)
            
            updated_count += 1
        
        conn.close()
        logger.info(f"Updated embeddings for {updated_count} memory entries")
    
    def get_embedding_stats(self) -> Dict[str, Any]:
        """Get embedding system statistics"""
        conn = sqlite3.connect(self.memory_manager.db_path)
        cursor = conn.cursor()
        
        # Count embeddings
        cursor.execute('SELECT COUNT(*) FROM embeddings')
        embedding_count = cursor.fetchone()[0]
        
        # Count memory entries with embeddings
        cursor.execute('SELECT COUNT(*) FROM memory_entries WHERE embedding_hash IS NOT NULL')
        memory_with_embeddings = cursor.fetchone()[0]
        
        # Count total memory entries
        cursor.execute('SELECT COUNT(*) FROM memory_entries')
        total_memory = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_embeddings': embedding_count,
            'memory_with_embeddings': memory_with_embeddings,
            'total_memory_entries': total_memory,
            'embedding_coverage': memory_with_embeddings / max(total_memory, 1),
            'embedding_dimension': self.embedding_dim,
            'cache_size': len(self.memory_manager.embedding_cache)
        }
    
    def export_embeddings(self, export_path: str):
        """Export all embeddings to file"""
        export_data = {
            'export_timestamp': str(datetime.now()),
            'embedding_dimension': self.embedding_dim,
            'embeddings': {}
        }
        
        # Export all embeddings from cache
        for content_hash, vector in self.memory_manager.embedding_cache.items():
            export_data['embeddings'][content_hash] = {
                'vector': vector.tolist(),
                'dimension': len(vector)
            }
        
        with open(export_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"Exported {len(export_data['embeddings'])} embeddings to {export_path}")

# Global instance
embedding_system = None

def initialize_embedding_system(memory_manager):
    """Initialize the global embedding system"""
    global embedding_system
    embedding_system = DeannaEmbeddingSystem(memory_manager)
    return embedding_system

if __name__ == "__main__":
    # Test the embedding system
    from memory_manager import memory_manager
    
    print("Testing DeannaEmbeddingSystem...")
    
    # Initialize embedding system
    embedding_system = DeannaEmbeddingSystem(memory_manager)
    
    # Test embedding creation
    test_text = "Deanna is a flirtatious and provocative AI companion"
    embedding = embedding_system.create_embedding(test_text)
    print(f"Created embedding with dimension: {len(embedding)}")
    
    # Test similarity search
    results = embedding_system.search_similar_memory("personality traits", limit=5)
    print(f"Found {len(results)} similar memories")
    
    # Get stats
    stats = embedding_system.get_embedding_stats()
    print(f"Embedding stats: {stats}")
    
    print("Embedding system test completed!") 