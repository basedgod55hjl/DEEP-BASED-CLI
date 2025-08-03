#!/usr/bin/env python3
"""
Simple Embedding Tool
Lightweight embedding generation using basic NLP techniques
"""

import asyncio
import json
import logging
import hashlib
import numpy as np
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from datetime import datetime
import re

from .base_tool import BaseTool, ToolResponse

@dataclass
class SimpleEmbeddingResult:
    """Result of simple embedding generation"""
    text: str
    embedding: List[float]
    metadata: Dict[str, Any]
    timestamp: datetime

class SimpleEmbeddingTool(BaseTool):
    """
    Simple Embedding Tool using basic NLP techniques
    Provides lightweight embedding generation without external dependencies
    """
    
    def __init__(self, 
                 embedding_dimension: int = 384,
                 use_tfidf: bool = True,
                 use_hash_features: bool = True):
        """Initialize Simple Embedding Tool"""
        super().__init__(
            name="Simple Embedding",
            description="Generate embeddings using basic NLP techniques",
            capabilities=[
                "simple_embedding_generation",
                "batch_embedding",
                "similarity_computation",
                "text_analysis"
            ]
        )
        
        self.embedding_dimension = embedding_dimension
        self.use_tfidf = use_tfidf
        self.use_hash_features = use_hash_features
        self.logger = logging.getLogger(__name__)
        
        # Simple vocabulary for basic embeddings
        self.common_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can',
            'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
            'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their'
        }
        
        self.logger.info(f"Simple embedding tool initialized with dimension {embedding_dimension}")
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for embedding generation"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _extract_features(self, text: str) -> Dict[str, float]:
        """Extract basic features from text"""
        features = {}
        
        # Word count
        words = text.split()
        features['word_count'] = len(words)
        
        # Character count
        features['char_count'] = len(text)
        
        # Average word length
        if words:
            features['avg_word_length'] = sum(len(word) for word in words) / len(words)
        else:
            features['avg_word_length'] = 0
        
        # Unique word ratio
        if words:
            features['unique_word_ratio'] = len(set(words)) / len(words)
        else:
            features['unique_word_ratio'] = 0
        
        # Common word ratio
        if words:
            common_count = sum(1 for word in words if word in self.common_words)
            features['common_word_ratio'] = common_count / len(words)
        else:
            features['common_word_ratio'] = 0
        
        # Sentence count (rough estimate)
        sentences = re.split(r'[.!?]+', text)
        features['sentence_count'] = len([s for s in sentences if s.strip()])
        
        return features
    
    def _generate_hash_features(self, text: str) -> List[float]:
        """Generate hash-based features"""
        features = []
        
        # Use different hash functions to generate features
        hash_functions = [
            hashlib.md5,
            hashlib.sha1,
            hashlib.sha256
        ]
        
        for hash_func in hash_functions:
            # Hash the text
            hash_obj = hash_func(text.encode('utf-8'))
            hash_hex = hash_obj.hexdigest()
            
            # Convert hex to numbers
            for i in range(0, min(len(hash_hex), 32), 2):
                if i + 1 < len(hash_hex):
                    hex_pair = hash_hex[i:i+2]
                    try:
                        num = int(hex_pair, 16) / 255.0  # Normalize to 0-1
                        features.append(num)
                    except ValueError:
                        features.append(0.0)
        
        return features
    
    def _generate_tfidf_features(self, text: str, corpus: List[str] = None) -> List[float]:
        """Generate simple TF-IDF features"""
        if not corpus:
            corpus = [text]  # Use the text itself as corpus
        
        words = text.split()
        if not words:
            return [0.0] * 50  # Return zeros if no words
        
        # Simple TF calculation
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Simple IDF calculation
        word_doc_freq = {}
        for doc in corpus:
            doc_words = set(doc.split())
            for word in doc_words:
                word_doc_freq[word] = word_doc_freq.get(word, 0) + 1
        
        # Generate TF-IDF features
        features = []
        for word in words:
            tf = word_freq[word] / len(words)
            idf = np.log(len(corpus) / (word_doc_freq.get(word, 1) + 1))
            tfidf = tf * idf
            features.append(tfidf)
        
        # Pad or truncate to fixed size
        target_size = 50
        if len(features) < target_size:
            features.extend([0.0] * (target_size - len(features)))
        else:
            features = features[:target_size]
        
        return features
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        # Preprocess text
        processed_text = self._preprocess_text(text)
        
        # Extract basic features
        basic_features = self._extract_features(processed_text)
        
        # Convert basic features to list
        feature_list = [
            basic_features['word_count'] / 100.0,  # Normalize
            basic_features['char_count'] / 1000.0,  # Normalize
            basic_features['avg_word_length'] / 10.0,  # Normalize
            basic_features['unique_word_ratio'],
            basic_features['common_word_ratio'],
            basic_features['sentence_count'] / 10.0  # Normalize
        ]
        
        # Add hash features if enabled
        if self.use_hash_features:
            hash_features = self._generate_hash_features(processed_text)
            feature_list.extend(hash_features)
        
        # Add TF-IDF features if enabled
        if self.use_tfidf:
            tfidf_features = self._generate_tfidf_features(processed_text)
            feature_list.extend(tfidf_features)
        
        # Pad or truncate to target dimension
        if len(feature_list) < self.embedding_dimension:
            # Pad with zeros
            feature_list.extend([0.0] * (self.embedding_dimension - len(feature_list)))
        else:
            # Truncate
            feature_list = feature_list[:self.embedding_dimension]
        
        # Normalize the embedding
        embedding_array = np.array(feature_list)
        norm = np.linalg.norm(embedding_array)
        if norm > 0:
            embedding_array = embedding_array / norm
        
        return embedding_array.tolist()
    
    async def execute(self, **kwargs) -> ToolResponse:
        """Execute simple embedding operation"""
        operation = kwargs.get("operation", "embed")
        
        try:
            if operation == "embed":
                return await self._generate_embeddings(**kwargs)
            elif operation == "batch_embed":
                return await self._batch_generate_embeddings(**kwargs)
            elif operation == "similarity":
                return await self._compute_similarity(**kwargs)
            elif operation == "info":
                return await self._get_tool_info(**kwargs)
            else:
                return ToolResponse(
                    success=False,
                    data={"error": f"Unknown operation: {operation}"},
                    message=f"Unknown simple embedding operation: {operation}"
                )
                
        except Exception as e:
            self.logger.error(f"Simple embedding operation failed: {str(e)}")
            return ToolResponse(
                success=False,
                data={"error": str(e)},
                message=f"Simple embedding operation failed: {str(e)}"
            )
    
    async def _generate_embeddings(self, **kwargs) -> ToolResponse:
        """Generate embeddings for text"""
        try:
            texts = kwargs.get("texts", [])
            if isinstance(texts, str):
                texts = [texts]
            
            if not texts:
                return ToolResponse(
                    success=False,
                    data={"error": "No texts provided"},
                    message="No texts provided for embedding generation"
                )
            
            # Generate embeddings
            embeddings = []
            for text in texts:
                embedding = self._generate_embedding(text)
                embeddings.append(embedding)
            
            # Prepare results
            results = []
            for i, (text, embedding) in enumerate(zip(texts, embeddings)):
                results.append({
                    "id": i,
                    "text": text,
                    "embedding": embedding,
                    "dimension": len(embedding),
                    "timestamp": datetime.now().isoformat()
                })
            
            return ToolResponse(
                success=True,
                data={
                    "embeddings": results,
                    "model": "simple_embedding",
                    "total_generated": len(texts),
                    "embedding_dimension": len(embeddings[0]) if embeddings else 0
                },
                message=f"Successfully generated {len(texts)} embeddings"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to generate embeddings: {str(e)}")
            return ToolResponse(
                success=False,
                data={"error": str(e)},
                message=f"Failed to generate embeddings: {str(e)}"
            )
    
    async def _batch_generate_embeddings(self, **kwargs) -> ToolResponse:
        """Generate embeddings in batches"""
        try:
            texts = kwargs.get("texts", [])
            batch_size = kwargs.get("batch_size", 32)
            
            if not texts:
                return ToolResponse(
                    success=False,
                    data={"error": "No texts provided"},
                    message="No texts provided for batch embedding generation"
                )
            
            # Process in batches
            all_embeddings = []
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                batch_embeddings = []
                for text in batch_texts:
                    embedding = self._generate_embedding(text)
                    batch_embeddings.append(embedding)
                all_embeddings.extend(batch_embeddings)
            
            # Prepare results
            results = []
            for i, (text, embedding) in enumerate(zip(texts, all_embeddings)):
                results.append({
                    "id": i,
                    "text": text,
                    "embedding": embedding,
                    "dimension": len(embedding),
                    "timestamp": datetime.now().isoformat()
                })
            
            return ToolResponse(
                success=True,
                data={
                    "embeddings": results,
                    "model": "simple_embedding",
                    "total_generated": len(texts),
                    "batch_size": batch_size,
                    "embedding_dimension": len(all_embeddings[0]) if all_embeddings else 0
                },
                message=f"Successfully generated {len(texts)} embeddings in batches"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to generate batch embeddings: {str(e)}")
            return ToolResponse(
                success=False,
                data={"error": str(e)},
                message=f"Failed to generate batch embeddings: {str(e)}"
            )
    
    async def _compute_similarity(self, **kwargs) -> ToolResponse:
        """Compute similarity between embeddings"""
        try:
            embedding1 = kwargs.get("embedding1", [])
            embedding2 = kwargs.get("embedding2", [])
            
            if not embedding1 or not embedding2:
                return ToolResponse(
                    success=False,
                    data={"error": "Both embeddings required"},
                    message="Both embeddings required for similarity computation"
                )
            
            # Convert to numpy arrays
            emb1 = np.array(embedding1)
            emb2 = np.array(embedding2)
            
            # Compute cosine similarity
            similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
            
            return ToolResponse(
                success=True,
                data={
                    "similarity": float(similarity),
                    "embedding1_dimension": len(embedding1),
                    "embedding2_dimension": len(embedding2),
                    "timestamp": datetime.now().isoformat()
                },
                message=f"Similarity computed: {similarity:.4f}"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to compute similarity: {str(e)}")
            return ToolResponse(
                success=False,
                data={"error": str(e)},
                message=f"Failed to compute similarity: {str(e)}"
            )
    
    async def _get_tool_info(self, **kwargs) -> ToolResponse:
        """Get tool information"""
        try:
            info = {
                "model_name": "simple_embedding",
                "embedding_dimension": self.embedding_dimension,
                "use_tfidf": self.use_tfidf,
                "use_hash_features": self.use_hash_features,
                "capabilities": self.capabilities
            }
            
            return ToolResponse(
                success=True,
                data=info,
                message=f"Tool info retrieved for simple embedding"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get tool info: {str(e)}")
            return ToolResponse(
                success=False,
                data={"error": str(e)},
                message=f"Failed to get tool info: {str(e)}"
            )
    
    def get_schema(self) -> Dict[str, Any]:
        """Get parameter schema for simple embedding operations"""
        return {
            "name": "Simple Embedding",
            "description": "Simple embedding generation using basic NLP techniques",
            "parameters": {
                "operation": {
                    "type": "string",
                    "enum": ["embed", "batch_embed", "similarity", "info"],
                    "description": "Simple embedding operation to perform"
                },
                "texts": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Texts to embed"
                },
                "batch_size": {
                    "type": "integer",
                    "description": "Batch size for embedding generation",
                    "default": 32
                },
                "embedding1": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "First embedding for similarity computation"
                },
                "embedding2": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "Second embedding for similarity computation"
                }
            }
        }
    
    # Convenience methods
    async def embed_text(self, text: str) -> ToolResponse:
        """Embed single text with convenience method"""
        return await self.execute(operation="embed", texts=[text])
    
    async def embed_texts(self, texts: List[str]) -> ToolResponse:
        """Embed multiple texts with convenience method"""
        return await self.execute(operation="embed", texts=texts)
    
    async def batch_embed_texts(self, texts: List[str], batch_size: int = 32) -> ToolResponse:
        """Embed texts in batches with convenience method"""
        return await self.execute(operation="batch_embed", texts=texts, batch_size=batch_size)
    
    async def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> ToolResponse:
        """Compute similarity between embeddings with convenience method"""
        return await self.execute(operation="similarity", embedding1=embedding1, embedding2=embedding2)
    
    async def get_info(self) -> ToolResponse:
        """Get tool info with convenience method"""
        return await self.execute(operation="info") 