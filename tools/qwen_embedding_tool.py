#!/usr/bin/env python3
"""
Qwen Embedding Tool - Enhanced BASED GOD CLI
High-quality embedding generation using Qwen3 models
"""

import asyncio
import json
import logging
import hashlib
import numpy as np
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from datetime import datetime
import os
from pathlib import Path

from .base_tool import BaseTool, ToolResponse

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logging.warning("SentenceTransformers not available. Install with: pip install sentence-transformers")

@dataclass
class QwenEmbeddingResult:
    """Result of Qwen embedding generation"""
    text: str
    embedding: List[float]
    metadata: Dict[str, Any]
    timestamp: datetime
    model_info: Dict[str, Any]

class QwenEmbeddingTool(BaseTool):
    """
    Qwen Embedding Tool using Qwen3 models
    Provides high-quality embedding generation with Qwen3-Embedding-0.6B
    """
    
    def __init__(self, 
                 model_path: str = "data/models/qwen3_embedding",
                 embedding_dimension: int = 1024,
                 use_gpu: bool = False,
                 normalize_embeddings: bool = True):
    
        """Initialize Qwen Embedding Tool"""
        super().__init__(
            name="Qwen Embedding",
            description="Generate high-quality embeddings using Qwen3 models",
            capabilities=[
                "qwen_embedding_generation",
                "batch_embedding",
                "similarity_computation",
                "semantic_search",
                "text_analysis",
                "vector_operations"
            ]
        )
        
        self.model_path = Path(model_path)
        self.embedding_dimension = embedding_dimension
        self.use_gpu = use_gpu
        self.normalize_embeddings = normalize_embeddings
        self.logger = logging.getLogger(__name__)
        
        # Initialize model
        self.model = None
        self.model_info = {}
        self._initialize_model()
        
    def _initialize_model(self):
        """Initialize the Qwen embedding model"""
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            self.logger.error("SentenceTransformers not available. Please install: pip install sentence-transformers")
            return
        
        try:
            if self.model_path.exists():
                self.logger.info(f"Loading Qwen model from: {self.model_path}")
                self.model = SentenceTransformer(
                    str(self.model_path),
                    device='cuda' if self.use_gpu else 'cpu'
                )
                
                # Get model info
                self.model_info = {
                    "model_path": str(self.model_path),
                    "embedding_dimension": self.model.get_sentence_embedding_dimension(),
                    "model_type": "Qwen3-Embedding-0.6B",
                    "normalize_embeddings": self.normalize_embeddings,
                    "device": "cuda" if self.use_gpu else "cpu",
                    "status": "loaded"
                }
                
                self.logger.info(f"Qwen embedding model loaded successfully. Dimension: {self.model_info['embedding_dimension']}")
            else:
                self.logger.warning(f"Qwen model not found at: {self.model_path}")
                self.logger.info("Falling back to default sentence-transformers model")
                
                # Fallback to a default model
                self.model = SentenceTransformer(
                    'all-MiniLM-L6-v2',
                    device='cuda' if self.use_gpu else 'cpu'
                )
                
                self.model_info = {
                    "model_path": "all-MiniLM-L6-v2",
                    "embedding_dimension": self.model.get_sentence_embedding_dimension(),
                    "model_type": "fallback",
                    "normalize_embeddings": self.normalize_embeddings,
                    "device": "cuda" if self.use_gpu else "cpu",
                    "status": "fallback"
                }
                
        except Exception as e:
            self.logger.error(f"Failed to initialize Qwen model: {e}")
            self.model = None
            self.model_info = {
                "status": "failed",
                "error": str(e)
            }
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for embedding generation"""
        if not text:
            return ""
        
        # Basic preprocessing
        text = text.strip()
        
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        return text
    
    def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for a single text"""
        if not self.model:
            self.logger.error("Model not initialized")
            return None
        
        try:
            # Preprocess text
            processed_text = self._preprocess_text(text)
            
            if not processed_text:
                self.logger.warning("Empty text after preprocessing")
                return None
            
            # Generate embedding
            embedding = self.model.encode(
                processed_text,
                normalize_embeddings=self.normalize_embeddings,
                convert_to_numpy=True
            )
            
            # Convert to list
            embedding_list = embedding.tolist()
            
            return embedding_list
            
        except Exception as e:
            self.logger.error(f"Error generating embedding: {e}")
            return None
    
    def _batch_generate_embeddings(self, texts: List[str], batch_size: int = 32) -> List[Optional[List[float]]]:
        """Generate embeddings for multiple texts"""
        if not self.model:
            self.logger.error("Model not initialized")
            return [None] * len(texts)
        
        try:
            # Preprocess texts
            processed_texts = [self._preprocess_text(text) for text in texts]
            
            # Filter out empty texts
            valid_texts = []
            valid_indices = []
            
            for i, text in enumerate(processed_texts):
                if text:
                    valid_texts.append(text)
                    valid_indices.append(i)
            
            if not valid_texts:
                self.logger.warning("No valid texts for embedding generation")
                return [None] * len(texts)
            
            # Generate embeddings in batches
            embeddings = []
            for i in range(0, len(valid_texts), batch_size):
                batch_texts = valid_texts[i:i + batch_size]
                batch_embeddings = self.model.encode(
                    batch_texts,
                    normalize_embeddings=self.normalize_embeddings,
                    convert_to_numpy=True
                )
                embeddings.extend(batch_embeddings.tolist())
            
            # Reconstruct full list with None for empty texts
            result = [None] * len(texts)
            for idx, embedding in zip(valid_indices, embeddings):
                result[idx] = embedding
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in batch embedding generation: {e}")
            return [None] * len(texts)
    
    def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Compute cosine similarity between two embeddings"""
        try:
            if not embedding1 or not embedding2:
                return 0.0
            
            # Convert to numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Compute cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            self.logger.error(f"Error computing similarity: {e}")
            return 0.0
    
    async def execute(self, **kwargs) -> ToolResponse:
        """Execute Qwen embedding operation"""
        
        operation = kwargs.get("operation", "embed").lower()
        
        try:
            if operation == "embed":
                return await self._generate_embeddings(kwargs)
            elif operation == "batch_embed":
                return await self._batch_generate_embeddings_operation(kwargs)
            elif operation == "similarity":
                return await self._compute_similarity_operation(kwargs)
            elif operation == "search":
                return await self._semantic_search(kwargs)
            elif operation == "info":
                return await self._get_tool_info(kwargs)
            else:
                return ToolResponse(
                    success=False,
                    message=f"Unsupported operation: {operation}",
                    status="failed"
                )
                
        except Exception as e:
            return ToolResponse(
                success=False,
                message=f"Qwen embedding operation failed: {str(e)}",
                status="failed"
            )
    
    async def _generate_embeddings(self, kwargs: Dict[str, Any]) -> ToolResponse:
        """Generate embeddings for text"""
        text = kwargs.get("text", "")
        
        if not text:
            return ToolResponse(
                success=False,
                message="No text provided for embedding generation",
                status="failed"
            )
        
        embedding = self._generate_embedding(text)
        
        if embedding is None:
            return ToolResponse(
                success=False,
                message="Failed to generate embedding",
                status="failed"
            )
        
        result = QwenEmbeddingResult(
            text=text,
            embedding=embedding,
            metadata={
                "model_info": self.model_info,
                "text_length": len(text),
                "embedding_dimension": len(embedding)
            },
            timestamp=datetime.now(),
            model_info=self.model_info
        )
        
        return ToolResponse(
            success=True,
            message="Embedding generated successfully",
            data={
                "embedding": embedding,
                "text": text,
                "metadata": result.metadata,
                "model_info": self.model_info
            },
            status="success"
        )
    
    async def _batch_generate_embeddings_operation(self, kwargs: Dict[str, Any]) -> ToolResponse:
        """Generate embeddings for multiple texts"""
        texts = kwargs.get("texts", [])
        batch_size = kwargs.get("batch_size", 32)
        
        if not texts:
            return ToolResponse(
                success=False,
                message="No texts provided for batch embedding generation",
                status="failed"
            )
        
        embeddings = self._batch_generate_embeddings(texts, batch_size)
        
        # Count successful embeddings
        successful_count = sum(1 for emb in embeddings if emb is not None)
        
        return ToolResponse(
            success=successful_count > 0,
            message=f"Generated {successful_count}/{len(texts)} embeddings successfully",
            data={
                "embeddings": embeddings,
                "texts": texts,
                "successful_count": successful_count,
                "total_count": len(texts),
                "model_info": self.model_info
            },
            status="success" if successful_count > 0 else "failed"
        )
    
    async def _compute_similarity_operation(self, kwargs: Dict[str, Any]) -> ToolResponse:
        """Compute similarity between embeddings"""
        embedding1 = kwargs.get("embedding1", [])
        embedding2 = kwargs.get("embedding2", [])
        
        if not embedding1 or not embedding2:
            return ToolResponse(
                success=False,
                message="Both embeddings are required for similarity computation",
                status="failed"
            )
        
        similarity = self.compute_similarity(embedding1, embedding2)
        
        return ToolResponse(
            success=True,
            message="Similarity computed successfully",
            data={
                "similarity": similarity,
                "embedding1_length": len(embedding1),
                "embedding2_length": len(embedding2)
            },
            status="success"
        )
    
    async def _semantic_search(self, kwargs: Dict[str, Any]) -> ToolResponse:
        """Perform semantic search"""
        query = kwargs.get("query", "")
        embeddings = kwargs.get("embeddings", [])
        texts = kwargs.get("texts", [])
        top_k = kwargs.get("top_k", 5)
        
        if not query or not embeddings or not texts:
            return ToolResponse(
                success=False,
                message="Query, embeddings, and texts are required for semantic search",
                status="failed"
            )
        
        # Generate query embedding
        query_embedding = self._generate_embedding(query)
        
        if query_embedding is None:
            return ToolResponse(
                success=False,
                message="Failed to generate query embedding",
                status="failed"
            )
        
        # Compute similarities
        similarities = []
        for i, embedding in enumerate(embeddings):
            if embedding is not None:
                similarity = self.compute_similarity(query_embedding, embedding)
                similarities.append((similarity, i, texts[i]))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[0], reverse=True)
        
        # Get top-k results
        top_results = similarities[:top_k]
        
        return ToolResponse(
            success=True,
            message=f"Semantic search completed. Found {len(top_results)} results",
            data={
                "query": query,
                "results": [
                    {
                        "similarity": float(sim),
                        "index": idx,
                        "text": text
                    }
                    for sim, idx, text in top_results
                ],
                "total_candidates": len(embeddings),
                "top_k": top_k
            },
            status="success"
        )
    
    async def _get_tool_info(self, kwargs: Dict[str, Any]) -> ToolResponse:
        """Get tool information"""
        return ToolResponse(
            success=True,
            message="Qwen embedding tool information",
            data={
                "name": self.name,
                "description": self.description,
                "capabilities": self.capabilities,
                "model_info": self.model_info,
                "embedding_dimension": self.embedding_dimension,
                "normalize_embeddings": self.normalize_embeddings,
                "use_gpu": self.use_gpu
            },
            status="success"
        )
    
    def get_schema(self) -> Dict[str, Any]:
        """Get parameter schema for Qwen embedding tool"""
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["embed", "batch_embed", "similarity", "search", "info"],
                    "description": "Qwen embedding operation to perform",
                    "default": "embed"
                },
                "text": {
                    "type": "string",
                    "description": "Text to generate embedding for"
                },
                "texts": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of texts for batch embedding generation"
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
                },
                "query": {
                    "type": "string",
                    "description": "Query text for semantic search"
                },
                "embeddings": {
                    "type": "array",
                    "items": {"type": "array", "items": {"type": "number"}},
                    "description": "List of embeddings for semantic search"
                },
                "batch_size": {
                    "type": "integer",
                    "description": "Batch size for embedding generation",
                    "default": 32
                },
                "top_k": {
                    "type": "integer",
                    "description": "Number of top results for semantic search",
                    "default": 5
                }
            },
            "required": ["operation"]
        }
    
    # Convenience methods
    async def embed_text(self, text: str) -> ToolResponse:
        """Generate embedding for a single text"""
        return await self.execute(operation="embed", text=text)
    
    async def embed_texts(self, texts: List[str]) -> ToolResponse:
        """Generate embeddings for multiple texts"""
        return await self.execute(operation="batch_embed", texts=texts)
    
    async def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> ToolResponse:
        """Compute similarity between two embeddings"""
        return await self.execute(operation="similarity", embedding1=embedding1, embedding2=embedding2)
    
    async def semantic_search(self, query: str, embeddings: List[List[float]], texts: List[str], top_k: int = 5) -> ToolResponse:
        """Perform semantic search"""
        return await self.execute(operation="search", query=query, embeddings=embeddings, texts=texts, top_k=top_k)
    
    async def get_info(self) -> ToolResponse:
        """Get tool information"""
        return await self.execute(operation="info") 