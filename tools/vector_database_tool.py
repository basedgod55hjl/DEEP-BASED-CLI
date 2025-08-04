"""
Vector Database Tool - Qdrant Integration for DEEP-CLI
Provides vector storage, similarity search, and RAG capabilities
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from datetime import datetime
import os

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    logging.info("⚠️ Qdrant not available. Install with: pip install qdrant-client")

from .base_tool import BaseTool, ToolResponse
from .simple_embedding_tool import SimpleEmbeddingTool

@dataclass
class EmbeddingResult:
    """Result of embedding generation"""
    text: str
    embedding: List[float]
    metadata: Dict[str, Any]
    timestamp: datetime

class VectorDatabaseTool(BaseTool):
    """
    Vector Database Tool with Qdrant integration and local embeddings
    Provides embeddings storage, similarity search, and RAG support
    """
    
    def __init__(self, 
                 host: str = "localhost",
                 port: int = 6333,
                 api_key: Optional[str] = None,
                 collection_name: str = "deepcli_vectors",
                 embedding_model: str = "all-MiniLM-L6-v2"):
    """__init__ function."""
        """Initialize Vector Database Tool"""
        super().__init__(
            name="Vector Database",
            description="Store and search vector embeddings for RAG and similarity search",
            capabilities=[
                "vector_storage",
                "similarity_search", 
                "semantic_search",
                "rag_retrieval",
                "collection_management",
                "embedding_generation"
            ]
        )
        
        self.host = host
        self.port = port
        self.api_key = api_key
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        
        # Initialize components
        self.client = None
        self.embedding_tool = None
        self.logger = logging.getLogger(__name__)
        
        # Initialize if Qdrant is available
        if QDRANT_AVAILABLE:
            self._initialize_components()
        else:
            self.logger.warning("Qdrant not available - vector database features disabled")
    
    def _initialize_components(self) -> Any:
        """Initialize Qdrant client and local embedding model"""
        try:
            # Initialize Qdrant client
            self.client = QdrantClient(
                host=self.host,
                port=self.port,
                api_key=self.api_key,
            )
            
            # Initialize simple embedding tool
            self.embedding_tool = SimpleEmbeddingTool(
                embedding_dimension=384
            )
            
            # Create collection if it doesn't exist
            try:
                self._ensure_collection_exists()
            except Exception as e:
                self.logger.warning(f"Could not ensure collection exists: {e}")
            
            self.logger.info("Vector database initialized successfully")
            
        except Exception as e:
            self.logger.warning(f"❌ Vector database initialization failed: {str(e)}")
            # Set client and embedding tool to None to prevent further operations
            self.client = None
            self.embedding_tool = None
    
    def _ensure_collection_exists(self) -> Any:
        """Ensure the collection exists with proper configuration"""
        try:
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                # Use fixed embedding dimension for simple embeddings
                embedding_dim = 384  # Fixed dimension for simple embeddings
                
                # Create collection with proper vector configuration
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=embedding_dim,
                        distance=Distance.COSINE
                    )
                )
                self.logger.info(f"Created collection: {self.collection_name}")
            else:
                self.logger.info(f"Collection already exists: {self.collection_name}")
                
        except Exception as e:
            self.logger.error(f"Error ensuring collection exists: {str(e)}")
            raise
    
    async def execute(self, **kwargs) -> ToolResponse:
        """Execute vector database operation"""
        if not QDRANT_AVAILABLE or self.client is None:
            return ToolResponse(
                success=False,
                data={"error": "Qdrant not available or not initialized"},
                message="Vector database features require Qdrant installation and initialization"
            )
        
        operation = kwargs.get("operation", "store")
        
        try:
            if operation == "store":
                return await self._store_embeddings(**kwargs)
            elif operation == "search":
                return await self._search_embeddings(**kwargs)
            elif operation == "delete":
                return await self._delete_embeddings(**kwargs)
            elif operation == "list":
                return await self._list_collections(**kwargs)
            elif operation == "update":
                return await self._update_embeddings(**kwargs)
            else:
                return ToolResponse(
                    success=False,
                    data={"error": f"Unknown operation: {operation}"},
                    message=f"Unknown vector database operation: {operation}"
                )
                
        except Exception as e:
            self.logger.error(f"Vector database operation failed: {str(e)}")
            return ToolResponse(
                success=False,
                data={"error": str(e)},
                message=f"Vector database operation failed: {str(e)}"
            )
    
    async def _store_embeddings(self, **kwargs) -> ToolResponse:
        """Store embeddings in vector database"""
        try:
            texts = kwargs.get("texts", [])
            metadata = kwargs.get("metadata", [])
        
            if not texts:
                return ToolResponse(
                    success=False,
                    data={"error": "No texts provided"},
                    message="No texts provided for embedding storage"
                )
            
            # Generate embeddings using local embedding tool
            embedding_response = await self.embedding_tool.embed_texts(texts)
            if not embedding_response.success:
                return embedding_response
            
            embeddings_data = embedding_response.data.get("embeddings", [])
            
            # Prepare points for storage
            points = []
            for i, embedding_data in enumerate(embeddings_data):
                text = embedding_data["text"]
                embedding = embedding_data["embedding"]
                meta = metadata[i] if i < len(metadata) else {}
                
                point = PointStruct(
                    id=i,
                    vector=embedding,
                    payload={
                        "text": text,
                        "metadata": meta,
                        "timestamp": datetime.now().isoformat()
                    }
                )
                points.append(point)
            
            # Store in Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            return ToolResponse(
                success=True,
                data={
                    "stored_count": len(texts),
                    "collection": self.collection_name,
                    "embeddings_generated": len(embeddings_data)
                },
                message=f"Successfully stored {len(texts)} embeddings"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to store embeddings: {str(e)}")
            return ToolResponse(
                success=False,
                data={"error": str(e)},
                message=f"Failed to store embeddings: {str(e)}"
            )
    
    async def _search_embeddings(self, **kwargs) -> ToolResponse:
        """Search embeddings in vector database"""
        try:
            query = kwargs.get("query", "")
            limit = kwargs.get("limit", 10)
            score_threshold = kwargs.get("score_threshold", 0.7)
            
            if not query:
                return ToolResponse(
                    success=False,
                    data={"error": "No query provided"},
                    message="No query provided for search"
                )
            
            # Generate query embedding using local embedding tool
            query_response = await self.embedding_tool.embed_text(query)
            if not query_response.success:
                return query_response
            
            query_embedding = query_response.data.get("embeddings", [{}])[0].get("embedding", [])
            
            # Search in Qdrant
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                score_threshold=score_threshold
            )
            
            # Format results
            results = []
            for result in search_results:
                results.append({
                    "id": result.id,
                    "score": result.score,
                    "text": result.payload.get("text", ""),
                    "metadata": result.payload.get("metadata", {}),
                    "timestamp": result.payload.get("timestamp", "")
                })
            
            return ToolResponse(
                success=True,
                data={
                    "query": query,
                    "results": results,
                    "total_found": len(results),
                    "collection": self.collection_name
                },
                message=f"Found {len(results)} similar embeddings"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to search embeddings: {str(e)}")
            return ToolResponse(
                success=False,
                data={"error": str(e)},
                message=f"Failed to search embeddings: {str(e)}"
            )
    
    async def _delete_embeddings(self, **kwargs) -> ToolResponse:
        """Delete embeddings from vector database"""
        try:
            ids = kwargs.get("ids", [])
            
            if not ids:
                return ToolResponse(
                    success=False,
                    data={"error": "No IDs provided"},
                    message="No IDs provided for deletion"
                )
            
            # Delete from Qdrant
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=ids
            )
            
            return ToolResponse(
                success=True,
                data={
                    "deleted_count": len(ids),
                    "collection": self.collection_name
                },
                message=f"Successfully deleted {len(ids)} embeddings"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to delete embeddings: {str(e)}")
            return ToolResponse(
                success=False,
                data={"error": str(e)},
                message=f"Failed to delete embeddings: {str(e)}"
            )
    
    async def _list_collections(self, **kwargs) -> ToolResponse:
        """List all collections in vector database"""
        try:
            collections = self.client.get_collections()
            collection_info = []
            
            for collection in collections.collections:
                collection_info.append({
                    "name": collection.name,
                    "vectors_count": collection.vectors_count,
                    "status": collection.status
                })
            
            return ToolResponse(
                success=True,
                data={
                    "collections": collection_info,
                    "total_collections": len(collection_info)
                },
                message=f"Found {len(collection_info)} collections"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to list collections: {str(e)}")
            return ToolResponse(
                success=False,
                data={"error": str(e)},
                message=f"Failed to list collections: {str(e)}"
            )
    
    async def _update_embeddings(self, **kwargs) -> ToolResponse:
        """Update embeddings in vector database"""
        try:
            id = kwargs.get("id")
            text = kwargs.get("text")
            metadata = kwargs.get("metadata", {})
            
            if not id or not text:
                return ToolResponse(
                    success=False,
                    data={"error": "ID and text required"},
                    message="ID and text required for update"
                )
            
            # Generate new embedding using local embedding tool
            embedding_response = await self.embedding_tool.embed_text(text)
            if not embedding_response.success:
                return embedding_response
            
            embedding = embedding_response.data.get("embeddings", [{}])[0].get("embedding", [])
            
            # Update in Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=[PointStruct(
                    id=id,
                    vector=embedding,
                    payload={
                        "text": text,
                        "metadata": metadata,
                        "timestamp": datetime.now().isoformat()
                    }
                )]
            )
            
            return ToolResponse(
                success=True,
                data={
                    "updated_id": id,
                    "collection": self.collection_name
                },
                message=f"Successfully updated embedding with ID {id}"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to update embedding: {str(e)}")
            return ToolResponse(
                success=False,
                data={"error": str(e)},
                message=f"Failed to update embedding: {str(e)}"
            )
    
    def get_schema(self) -> Dict[str, Any]:
        """Get parameter schema for vector database operations"""
        return {
            "name": "Vector Database",
            "description": "Vector database operations for embeddings and similarity search",
            "parameters": {
                "operation": {
                    "type": "string",
                    "enum": ["store", "search", "delete", "list", "update"],
                    "description": "Vector database operation to perform"
                },
                "texts": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Texts to embed and store"
                },
                "query": {
                    "type": "string",
                    "description": "Query text for similarity search"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return",
                    "default": 10
                },
                "score_threshold": {
                    "type": "number",
                    "description": "Minimum similarity score threshold",
                    "default": 0.7
                },
                "ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "IDs of embeddings to delete"
                },
                "id": {
                    "type": "integer",
                    "description": "ID of embedding to update"
                },
                "metadata": {
                    "type": "object",
                    "description": "Metadata to associate with embeddings"
                }
            }
        }
    
    # Convenience methods for RAG operations
    async def store_embeddings(self, texts: List[str], metadata: List[Dict[str, Any]] = None) -> ToolResponse:
        """Store embeddings with convenience method"""
        if metadata is None:
            metadata = [{} for _ in texts]
        return await self.execute(operation="store", texts=texts, metadata=metadata)
    
    async def search_embeddings(self, query: str, limit: int = 10, score_threshold: float = 0.7) -> ToolResponse:
        """Search embeddings with convenience method"""
        return await self.execute(operation="search", query=query, limit=limit, score_threshold=score_threshold)
    
    async def delete_embeddings(self, ids: List[int]) -> ToolResponse:
        """Delete embeddings with convenience method"""
        return await self.execute(operation="delete", ids=ids)
    
    async def list_collections(self) -> ToolResponse:
        """List collections with convenience method"""
        return await self.execute(operation="list")
    
    async def update_embeddings(self, id: int, text: str, metadata: Dict[str, Any] = None) -> ToolResponse:
        """Update embeddings with convenience method"""
        if metadata is None:
            metadata = {}
        return await self.execute(operation="update", id=id, text=text, metadata=metadata)
