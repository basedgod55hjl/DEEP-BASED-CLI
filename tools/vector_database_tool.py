"""
Vector Database Tool - Qdrant Integration for DEEP-CLI
Provides vector storage, similarity search, and RAG capabilities
"""

import os
import json
import asyncio
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import numpy as np
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from tools.base_tool import BaseTool, ToolResponse, ToolStatus

try:
    from qdrant_client import QdrantClient, models
    from qdrant_client.models import Distance, VectorParams, PointStruct
    from fastembed import TextEmbedding
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    print("⚠️ Qdrant not available. Install with: pip install qdrant-client[fastembed]")


@dataclass
class VectorSearchResult:
    """Represents a vector search result"""
    id: str
    score: float
    payload: Dict[str, Any]
    text: str
    metadata: Optional[Dict[str, Any]] = None


class VectorDatabaseTool(BaseTool):
    """
    Vector Database Tool with Qdrant integration
    Provides embeddings storage, similarity search, and RAG support
    """
    
    def __init__(self, 
                 host: str = "localhost",
                 port: int = 6333,
                 api_key: Optional[str] = None,
                 collection_name: str = "deepcli_vectors",
                 embedding_model: str = "BAAI/bge-small-en-v1.5"):
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
        self.console = Console()
        
        # Initialize clients
        self.client = None
        self.embedder = None
        self._initialized = False
        
        if QDRANT_AVAILABLE:
            self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize Qdrant client and embedding model"""
        try:
            # Initialize Qdrant client
            if self.api_key:
                self.client = QdrantClient(
                    url=f"https://{self.host}",
                    api_key=self.api_key
                )
            else:
                self.client = QdrantClient(
                    host=self.host,
                    port=self.port
                )
            
            # Initialize embedding model
            self.embedder = TextEmbedding(model_name=self.embedding_model)
            
            # Create collection if it doesn't exist
            self._ensure_collection()
            self._initialized = True
            
        except Exception as e:
            self.console.print(f"[red]Failed to initialize vector database: {str(e)}[/red]")
            self._initialized = False
    
    def _ensure_collection(self):
        """Ensure the collection exists"""
        try:
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if self.collection_name not in collection_names:
                # Get embedding dimension
                test_embedding = list(self.embedder.embed(["test"]))[0]
                embedding_dim = len(test_embedding)
                
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=embedding_dim,
                        distance=Distance.COSINE
                    )
                )
                self.console.print(f"[green]Created collection: {self.collection_name}[/green]")
        except Exception as e:
            self.console.print(f"[yellow]Collection check failed: {str(e)}[/yellow]")
    
    async def execute(self, **kwargs) -> ToolResponse:
        """Execute vector database operations"""
        if not QDRANT_AVAILABLE:
            return ToolResponse(
                success=False,
                message="Qdrant not available. Install with: pip install qdrant-client[fastembed]",
                status=ToolStatus.FAILED
            )
        
        if not self._initialized:
            self._initialize_clients()
            if not self._initialized:
                return ToolResponse(
                    success=False,
                    message="Failed to initialize vector database",
                    status=ToolStatus.FAILED
                )
        
        operation = kwargs.get('operation', 'search')
        
        try:
            if operation == 'store':
                return await self._store_vectors(kwargs)
            elif operation == 'search':
                return await self._search_vectors(kwargs)
            elif operation == 'delete':
                return await self._delete_vectors(kwargs)
            elif operation == 'update':
                return await self._update_vectors(kwargs)
            elif operation == 'info':
                return await self._get_collection_info()
            elif operation == 'create_index':
                return await self._create_index(kwargs)
            elif operation == 'rag_retrieve':
                return await self._rag_retrieve(kwargs)
            else:
                return ToolResponse(
                    success=False,
                    message=f"Unknown operation: {operation}",
                    status=ToolStatus.FAILED
                )
                
        except Exception as e:
            return ToolResponse(
                success=False,
                message=f"Vector database error: {str(e)}",
                status=ToolStatus.FAILED
            )
    
    async def _store_vectors(self, kwargs: Dict[str, Any]) -> ToolResponse:
        """Store text documents as vectors"""
        texts = kwargs.get('texts', [])
        metadata = kwargs.get('metadata', [])
        category = kwargs.get('category', 'general')
        
        if not texts:
            return ToolResponse(
                success=False,
                message="No texts provided to store",
                status=ToolStatus.FAILED
            )
        
        # Ensure metadata list matches texts
        if len(metadata) < len(texts):
            metadata.extend([{}] * (len(texts) - len(metadata)))
        
        # Generate embeddings
        embeddings = list(self.embedder.embed(texts))
        
        # Create points
        points = []
        for i, (text, embedding, meta) in enumerate(zip(texts, embeddings, metadata)):
            point_id = f"{category}_{datetime.now().timestamp()}_{i}"
            
            payload = {
                "text": text,
                "category": category,
                "timestamp": datetime.now().isoformat(),
                "metadata": meta
            }
            
            points.append(PointStruct(
                id=point_id,
                vector=embedding.tolist(),
                payload=payload
            ))
        
        # Upload to Qdrant
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        
        return ToolResponse(
            success=True,
            message=f"Successfully stored {len(points)} vectors",
            data={
                "count": len(points),
                "collection": self.collection_name,
                "category": category,
                "ids": [p.id for p in points]
            }
        )
    
    async def _search_vectors(self, kwargs: Dict[str, Any]) -> ToolResponse:
        """Search for similar vectors"""
        query = kwargs.get('query', '')
        limit = kwargs.get('limit', 5)
        category = kwargs.get('category', None)
        score_threshold = kwargs.get('score_threshold', 0.0)
        
        if not query:
            return ToolResponse(
                success=False,
                message="No query provided for search",
                status=ToolStatus.FAILED
            )
        
        # Generate query embedding
        query_embedding = list(self.embedder.embed([query]))[0]
        
        # Build filter
        search_filter = None
        if category:
            search_filter = models.Filter(
                must=[
                    models.FieldCondition(
                        key="category",
                        match=models.MatchValue(value=category)
                    )
                ]
            )
        
        # Search
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding.tolist(),
            limit=limit,
            query_filter=search_filter,
            score_threshold=score_threshold
        )
        
        # Format results
        search_results = []
        for result in results:
            search_results.append(VectorSearchResult(
                id=result.id,
                score=result.score,
                payload=result.payload,
                text=result.payload.get('text', ''),
                metadata=result.payload.get('metadata', {})
            ))
        
        return ToolResponse(
            success=True,
            message=f"Found {len(search_results)} similar vectors",
            data={
                "query": query,
                "results": [
                    {
                        "id": r.id,
                        "score": r.score,
                        "text": r.text,
                        "category": r.payload.get('category'),
                        "metadata": r.metadata
                    }
                    for r in search_results
                ],
                "count": len(search_results)
            }
        )
    
    async def _delete_vectors(self, kwargs: Dict[str, Any]) -> ToolResponse:
        """Delete vectors by ID or filter"""
        ids = kwargs.get('ids', [])
        category = kwargs.get('category', None)
        
        if ids:
            # Delete by IDs
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(points=ids)
            )
            message = f"Deleted {len(ids)} vectors by ID"
        elif category:
            # Delete by category
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.FilterSelector(
                    filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                key="category",
                                match=models.MatchValue(value=category)
                            )
                        ]
                    )
                )
            )
            message = f"Deleted all vectors in category: {category}"
        else:
            return ToolResponse(
                success=False,
                message="No IDs or category specified for deletion",
                status=ToolStatus.FAILED
            )
        
        return ToolResponse(
            success=True,
            message=message,
            data={"deleted": True}
        )
    
    async def _update_vectors(self, kwargs: Dict[str, Any]) -> ToolResponse:
        """Update vector metadata"""
        updates = kwargs.get('updates', {})
        
        if not updates:
            return ToolResponse(
                success=False,
                message="No updates provided",
                status=ToolStatus.FAILED
            )
        
        for point_id, new_payload in updates.items():
            self.client.set_payload(
                collection_name=self.collection_name,
                payload=new_payload,
                points=[point_id]
            )
        
        return ToolResponse(
            success=True,
            message=f"Updated {len(updates)} vectors",
            data={"updated_count": len(updates)}
        )
    
    async def _get_collection_info(self) -> ToolResponse:
        """Get collection information"""
        try:
            info = self.client.get_collection(self.collection_name)
            
            return ToolResponse(
                success=True,
                message="Collection information retrieved",
                data={
                    "name": self.collection_name,
                    "vector_count": info.points_count,
                    "vector_size": info.config.params.vectors.size,
                    "distance": info.config.params.vectors.distance,
                    "status": info.status,
                    "optimizer_status": info.optimizer_status
                }
            )
        except Exception as e:
            return ToolResponse(
                success=False,
                message=f"Failed to get collection info: {str(e)}",
                status=ToolStatus.FAILED
            )
    
    async def _create_index(self, kwargs: Dict[str, Any]) -> ToolResponse:
        """Create or optimize collection index"""
        try:
            # Update collection optimizer
            self.client.update_collection(
                collection_name=self.collection_name,
                optimizer_config=models.OptimizersConfigDiff(
                    indexing_threshold=kwargs.get('indexing_threshold', 20000),
                    flush_interval_sec=kwargs.get('flush_interval', 5)
                )
            )
            
            return ToolResponse(
                success=True,
                message="Collection index optimized",
                data={"optimized": True}
            )
        except Exception as e:
            return ToolResponse(
                success=False,
                message=f"Failed to optimize index: {str(e)}",
                status=ToolStatus.FAILED
            )
    
    async def _rag_retrieve(self, kwargs: Dict[str, Any]) -> ToolResponse:
        """Retrieve context for RAG (Retrieval-Augmented Generation)"""
        query = kwargs.get('query', '')
        context_limit = kwargs.get('context_limit', 3)
        max_tokens = kwargs.get('max_tokens', 1000)
        include_metadata = kwargs.get('include_metadata', True)
        
        if not query:
            return ToolResponse(
                success=False,
                message="No query provided for RAG retrieval",
                status=ToolStatus.FAILED
            )
        
        # Search for relevant contexts
        search_result = await self._search_vectors({
            'query': query,
            'limit': context_limit * 2,  # Get more to filter
            'score_threshold': 0.5
        })
        
        if not search_result.success:
            return search_result
        
        # Build context
        contexts = []
        total_tokens = 0
        
        for result in search_result.data['results']:
            text = result['text']
            # Rough token estimation (4 chars per token)
            estimated_tokens = len(text) // 4
            
            if total_tokens + estimated_tokens > max_tokens:
                break
            
            context_item = {
                'text': text,
                'score': result['score']
            }
            
            if include_metadata:
                context_item['metadata'] = result['metadata']
                context_item['category'] = result['category']
            
            contexts.append(context_item)
            total_tokens += estimated_tokens
        
        # Format combined context
        combined_context = "\n\n".join([
            f"[Context {i+1} - Score: {c['score']:.3f}]\n{c['text']}"
            for i, c in enumerate(contexts)
        ])
        
        return ToolResponse(
            success=True,
            message=f"Retrieved {len(contexts)} contexts for RAG",
            data={
                "query": query,
                "contexts": contexts,
                "combined_context": combined_context,
                "total_contexts": len(contexts),
                "estimated_tokens": total_tokens
            }
        )
    
    def get_schema(self) -> Dict[str, Any]:
        """Get tool schema"""
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["store", "search", "delete", "update", "info", "create_index", "rag_retrieve"],
                    "description": "Operation to perform"
                },
                "texts": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Texts to store as vectors"
                },
                "query": {
                    "type": "string",
                    "description": "Search query"
                },
                "metadata": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Metadata for each text"
                },
                "category": {
                    "type": "string",
                    "description": "Category for filtering"
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of results to return"
                },
                "ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Vector IDs for deletion"
                },
                "updates": {
                    "type": "object",
                    "description": "Updates mapping ID to new payload"
                },
                "score_threshold": {
                    "type": "number",
                    "description": "Minimum similarity score"
                },
                "context_limit": {
                    "type": "integer",
                    "description": "Number of contexts for RAG"
                },
                "max_tokens": {
                    "type": "integer",
                    "description": "Maximum tokens in RAG context"
                }
            },
            "required": ["operation"]
        }
    
    async def close(self):
        """Close connections"""
        if self.client:
            self.client.close()