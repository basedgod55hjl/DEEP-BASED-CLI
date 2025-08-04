#!/usr/bin/env python3
"""
Local Embedding Tool
Uses sentence-transformers for local embedding generation without external API calls
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from datetime import datetime
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logging.warning("⚠️ Sentence Transformers not available. Install with: pip install sentence-transformers")

from .base_tool import BaseTool, ToolResponse

@dataclass
class EmbeddingResult:
    """Result of embedding generation"""
    text: str
    embedding: List[float]
    metadata: Dict[str, Any]
    timestamp: datetime

class LocalEmbeddingTool(BaseTool):
    """
    Local Embedding Tool using sentence-transformers
    Provides local embedding generation without external API calls
    """
    
    def __init__(self, 
                 model_name: str = "all-MiniLM-L6-v2",
                 cache_dir: str = "./embeddings_cache"):
    
        """Initialize Local Embedding Tool"""
        super().__init__(
            name="Local Embedding",
            description="Generate embeddings locally using sentence-transformers",
            capabilities=[
                "local_embedding_generation",
                "batch_embedding",
                "similarity_computation",
                "embedding_caching"
            ]
        )
        
        self.model_name = model_name
        self.cache_dir = cache_dir
        self.model = None
        self.logger = logging.getLogger(__name__)
        
        # Initialize if sentence-transformers is available
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            self._initialize_model()
        else:
            self.logger.warning("Sentence Transformers not available - local embedding features disabled")
    
    def _initialize_model(self) -> Any:
        """Initialize sentence-transformers model"""
        try:
            self.model = SentenceTransformer(self.model_name, cache_folder=self.cache_dir)
            self.logger.info(f"Local embedding model initialized: {self.model_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize local embedding model: {str(e)}")
            raise
    
    async def execute(self, **kwargs) -> ToolResponse:
        """Execute local embedding operation"""
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            return ToolResponse(
                success=False,
                data={"error": "Sentence Transformers not available"},
                message="Local embedding features require sentence-transformers installation"
            )
        
        operation = kwargs.get("operation", "embed")
        
        try:
            if operation == "embed":
                return await self._generate_embeddings(**kwargs)
            elif operation == "batch_embed":
                return await self._batch_generate_embeddings(**kwargs)
            elif operation == "similarity":
                return await self._compute_similarity(**kwargs)
            elif operation == "info":
                return await self._get_model_info(**kwargs)
            else:
                return ToolResponse(
                    success=False,
                    data={"error": f"Unknown operation: {operation}"},
                    message=f"Unknown local embedding operation: {operation}"
                )
                
        except Exception as e:
            self.logger.error(f"Local embedding operation failed: {str(e)}")
            return ToolResponse(
                success=False,
                data={"error": str(e)},
                message=f"Local embedding operation failed: {str(e)}"
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
            embeddings = self.model.encode(texts, convert_to_tensor=False)
            
            # Convert to list format
            embedding_list = embeddings.tolist() if hasattr(embeddings, 'tolist') else embeddings
            
            # Prepare results
            results = []
            for i, (text, embedding) in enumerate(zip(texts, embedding_list)):
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
                    "model": self.model_name,
                    "total_generated": len(texts),
                    "embedding_dimension": len(embedding_list[0]) if embedding_list else 0
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
                batch_embeddings = self.model.encode(batch_texts, convert_to_tensor=False)
                all_embeddings.extend(batch_embeddings.tolist())
            
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
                    "model": self.model_name,
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
    
    async def _get_model_info(self, **kwargs) -> ToolResponse:
        """Get model information"""
        try:
            info = {
                "model_name": self.model_name,
                "max_seq_length": getattr(self.model, 'max_seq_length', 'Unknown'),
                "embedding_dimension": self.model.get_sentence_embedding_dimension(),
                "cache_dir": self.cache_dir,
                "available": SENTENCE_TRANSFORMERS_AVAILABLE
            }
            
            return ToolResponse(
                success=True,
                data=info,
                message=f"Model info retrieved for {self.model_name}"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get model info: {str(e)}")
            return ToolResponse(
                success=False,
                data={"error": str(e)},
                message=f"Failed to get model info: {str(e)}"
            )
    
    def get_schema(self) -> Dict[str, Any]:
        """Get parameter schema for local embedding operations"""
        return {
            "name": "Local Embedding",
            "description": "Local embedding generation using sentence-transformers",
            "parameters": {
                "operation": {
                    "type": "string",
                    "enum": ["embed", "batch_embed", "similarity", "info"],
                    "description": "Local embedding operation to perform"
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
        """Get model info with convenience method"""
        return await self.execute(operation="info") 