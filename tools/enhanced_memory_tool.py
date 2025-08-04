"""
Enhanced Memory Tool - Inspired by Google Gemini CLI
Advanced memory management with semantic search and context-aware storage
"""

import asyncio
import logging
import json
import sqlite3
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import hashlib
import uuid

from .base_tool import BaseTool, ToolResponse
from .enhanced_base_tool import EnhancedBaseTool, ToolResult, ToolLocation, ToolSchema, Icon, ToolErrorType
from .simple_embedding_tool import SimpleEmbeddingTool

logger = logging.getLogger(__name__)

class MemoryType:
    """Types of memories that can be stored"""
    FACT = "fact"
    PROCEDURE = "procedure" 
    CONVERSATION = "conversation"
    CODE_SNIPPET = "code_snippet"
    FILE_REFERENCE = "file_reference"
    TASK = "task"
    INSIGHT = "insight"

class EnhancedMemoryTool(EnhancedBaseTool):
    """
    Enhanced memory tool inspired by Gemini CLI
    Provides sophisticated memory management with semantic search and categorization
    """
    
    def __init__(self, db_path: str = "data/enhanced_memory.db"):
        super().__init__()
        self.db_path = db_path
        self.embedding_tool = SimpleEmbeddingTool()
        self._initialize_database()
    
    @property
    def name(self) -> str:
        return "enhanced_memory_tool"
    
    @property
    def display_name(self) -> str:
        return "Enhanced Memory System"
    
    @property
    def description(self) -> str:
        return "Advanced memory management with semantic search, categorization, and context-aware retrieval"
    
    @property
    def icon(self) -> Icon:
        return Icon.MEMORY
    
    @property
    def schema(self) -> ToolSchema:
        return ToolSchema(
            name=self.name,
            description=self.description,
            parameters={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["store", "search", "retrieve", "update", "delete", "list", "analyze", "summarize"],
                        "description": "Memory operation to perform"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to store or search for"
                    },
                    "query": {
                        "type": "string",
                        "description": "Search query for retrieval"
                    },
                    "memory_type": {
                        "type": "string",
                        "enum": ["fact", "procedure", "conversation", "code_snippet", "file_reference", "task", "insight"],
                        "default": "fact",
                        "description": "Type of memory to store"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Tags for categorization"
                    },
                    "context": {
                        "type": "string",
                        "description": "Context or source of the memory"
                    },
                    "importance": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 10,
                        "default": 5,
                        "description": "Importance level (1-10)"
                    },
                    "limit": {
                        "type": "integer",
                        "default": 10,
                        "description": "Maximum number of results to return"
                    },
                    "similarity_threshold": {
                        "type": "number",
                        "default": 0.7,
                        "description": "Minimum similarity score for retrieval"
                    },
                    "memory_id": {
                        "type": "string",
                        "description": "ID of specific memory to update/delete"
                    }
                },
                "required": ["operation"]
            },
            required=["operation"]
        )
    
    @property
    def can_update_output(self) -> bool:
        return True
    
    def _initialize_database(self) -> None:
        """Initialize the enhanced memory database"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    tags TEXT,
                    context TEXT,
                    importance INTEGER DEFAULT 5,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TIMESTAMP,
                    embedding_hash TEXT,
                    metadata TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memory_embeddings (
                    memory_id TEXT PRIMARY KEY,
                    embedding BLOB,
                    FOREIGN KEY (memory_id) REFERENCES memories (id)
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(memory_type)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_memories_importance ON memories(importance)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_memories_created ON memories(created_at)
            """)
    
    async def execute(
        self,
        params: Dict[str, Any],
        signal: Optional[asyncio.Event] = None,
        update_output: Optional[callable] = None
    ) -> ToolResult:
        """Execute memory operation"""
        operation = params["operation"]
        
        try:
            if operation == "store":
                return await self._store_memory(params, update_output)
            elif operation == "search":
                return await self._search_memories(params, update_output)
            elif operation == "retrieve":
                return await self._retrieve_memories(params, update_output)
            elif operation == "update":
                return await self._update_memory(params, update_output)
            elif operation == "delete":
                return await self._delete_memory(params, update_output)
            elif operation == "list":
                return await self._list_memories(params, update_output)
            elif operation == "analyze":
                return await self._analyze_memories(params, update_output)
            elif operation == "summarize":
                return await self._summarize_memories(params, update_output)
            else:
                return ToolResult(
                    success=False,
                    error_message=f"Unknown operation: {operation}",
                    error_type=ToolErrorType.VALIDATION_ERROR
                )
                
        except Exception as e:
            logger.error(f"Memory operation {operation} failed: {str(e)}")
            return ToolResult(
                success=False,
                error_message=str(e),
                error_type=ToolErrorType.EXECUTION_ERROR
            )
    
    async def _store_memory(self, params: Dict[str, Any], update_output: Optional[callable]) -> ToolResult:
        """Store a new memory with embedding"""
        content = params.get("content", "")
        memory_type = params.get("memory_type", MemoryType.FACT)
        tags = params.get("tags", [])
        context = params.get("context", "")
        importance = params.get("importance", 5)
        
        if not content:
            return ToolResult(
                success=False,
                error_message="Content is required for storing memory",
                error_type=ToolErrorType.VALIDATION_ERROR
            )
        
        try:
            # Generate unique ID
            memory_id = str(uuid.uuid4())
            
            # Create embedding
            if update_output:
                update_output("🧠 Creating semantic embedding...")
            
            embedding = self.embedding_tool.create_embedding(content)
            embedding_hash = hashlib.md5(content.encode()).hexdigest()
            
            # Check for duplicate content
            existing_memory = self._find_duplicate_memory(embedding_hash)
            if existing_memory:
                return ToolResult(
                    success=False,
                    error_message=f"Similar memory already exists (ID: {existing_memory['id']})",
                    error_type=ToolErrorType.VALIDATION_ERROR,
                    metadata={"existing_memory": existing_memory}
                )
            
            # Store memory
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO memories 
                    (id, content, memory_type, tags, context, importance, embedding_hash, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    memory_id,
                    content,
                    memory_type,
                    json.dumps(tags),
                    context,
                    importance,
                    embedding_hash,
                    json.dumps({"length": len(content), "word_count": len(content.split())})
                ))
                
                # Store embedding
                conn.execute("""
                    INSERT INTO memory_embeddings (memory_id, embedding)
                    VALUES (?, ?)
                """, (memory_id, embedding.tobytes()))
            
            if update_output:
                update_output(f"✅ Stored memory with ID: {memory_id}")
            
            return ToolResult(
                success=True,
                content=f"Memory stored successfully",
                metadata={
                    "memory_id": memory_id,
                    "content_length": len(content),
                    "memory_type": memory_type,
                    "tags": tags,
                    "importance": importance
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error_message=f"Failed to store memory: {str(e)}",
                error_type=ToolErrorType.EXECUTION_ERROR
            )
    
    async def _search_memories(self, params: Dict[str, Any], update_output: Optional[callable]) -> ToolResult:
        """Search memories using semantic similarity"""
        query = params.get("query", params.get("content", ""))
        limit = params.get("limit", 10)
        similarity_threshold = params.get("similarity_threshold", 0.7)
        memory_type = params.get("memory_type")
        
        if not query:
            return ToolResult(
                success=False,
                error_message="Query is required for memory search",
                error_type=ToolErrorType.VALIDATION_ERROR
            )
        
        try:
            if update_output:
                update_output("🔍 Searching memories...")
            
            # Create query embedding
            query_embedding = self.embedding_tool.create_embedding(query)
            
            # Get all memories with embeddings
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                where_clause = ""
                params_list = []
                
                if memory_type:
                    where_clause = "WHERE m.memory_type = ?"
                    params_list.append(memory_type)
                
                cursor = conn.execute(f"""
                    SELECT m.*, e.embedding
                    FROM memories m
                    JOIN memory_embeddings e ON m.id = e.memory_id
                    {where_clause}
                    ORDER BY m.importance DESC, m.created_at DESC
                """, params_list)
                
                memories = cursor.fetchall()
            
            # Calculate similarities
            results = []
            for memory in memories:
                memory_embedding = np.frombuffer(memory["embedding"], dtype=np.float32)
                
                # Calculate cosine similarity
                similarity = np.dot(query_embedding, memory_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(memory_embedding)
                )
                
                if similarity >= similarity_threshold:
                    results.append({
                        "memory_id": memory["id"],
                        "content": memory["content"],
                        "memory_type": memory["memory_type"],
                        "tags": json.loads(memory["tags"] or "[]"),
                        "context": memory["context"],
                        "importance": memory["importance"],
                        "similarity": float(similarity),
                        "created_at": memory["created_at"],
                        "access_count": memory["access_count"]
                    })
            
            # Sort by similarity
            results.sort(key=lambda x: x["similarity"], reverse=True)
            results = results[:limit]
            
            # Update access counts
            if results:
                memory_ids = [r["memory_id"] for r in results]
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute(f"""
                        UPDATE memories 
                        SET access_count = access_count + 1, last_accessed = CURRENT_TIMESTAMP
                        WHERE id IN ({','.join(['?'] * len(memory_ids))})
                    """, memory_ids)
            
            # Format results
            result_text = f"# Memory Search Results\n\n"
            result_text += f"**Query**: {query}\n"
            result_text += f"**Found**: {len(results)} memories\n\n"
            
            for i, result in enumerate(results, 1):
                result_text += f"## {i}. Memory (ID: {result['memory_id'][:8]}...)\n"
                result_text += f"**Type**: {result['memory_type']} | **Similarity**: {result['similarity']:.3f} | **Importance**: {result['importance']}\n"
                result_text += f"**Content**: {result['content'][:200]}{'...' if len(result['content']) > 200 else ''}\n"
                if result['tags']:
                    result_text += f"**Tags**: {', '.join(result['tags'])}\n"
                if result['context']:
                    result_text += f"**Context**: {result['context']}\n"
                result_text += f"**Created**: {result['created_at']} | **Accessed**: {result['access_count']} times\n\n"
            
            if update_output:
                update_output(f"✅ Found {len(results)} relevant memories")
            
            return ToolResult(
                success=True,
                content=result_text,
                metadata={
                    "query": query,
                    "total_results": len(results),
                    "similarity_threshold": similarity_threshold,
                    "results": results
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error_message=f"Memory search failed: {str(e)}",
                error_type=ToolErrorType.EXECUTION_ERROR
            )
    
    async def _retrieve_memories(self, params: Dict[str, Any], update_output: Optional[callable]) -> ToolResult:
        """Retrieve memories by type, tags, or other criteria"""
        memory_type = params.get("memory_type")
        tags = params.get("tags", [])
        limit = params.get("limit", 10)
        importance_min = params.get("importance", 1)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                where_conditions = []
                params_list = []
                
                if memory_type:
                    where_conditions.append("memory_type = ?")
                    params_list.append(memory_type)
                
                if tags:
                    # Simple tag matching - in a production system, this would be more sophisticated
                    tag_conditions = []
                    for tag in tags:
                        tag_conditions.append("tags LIKE ?")
                        params_list.append(f"%{tag}%")
                    where_conditions.append(f"({' OR '.join(tag_conditions)})")
                
                if importance_min > 1:
                    where_conditions.append("importance >= ?")
                    params_list.append(importance_min)
                
                where_clause = ""
                if where_conditions:
                    where_clause = "WHERE " + " AND ".join(where_conditions)
                
                cursor = conn.execute(f"""
                    SELECT * FROM memories
                    {where_clause}
                    ORDER BY importance DESC, created_at DESC
                    LIMIT ?
                """, params_list + [limit])
                
                memories = cursor.fetchall()
            
            # Format results
            result_text = f"# Memory Retrieval\n\n"
            result_text += f"**Criteria**: Type={memory_type or 'any'}, Tags={tags or 'none'}, Min Importance={importance_min}\n"
            result_text += f"**Found**: {len(memories)} memories\n\n"
            
            results = []
            for memory in memories:
                memory_data = {
                    "memory_id": memory["id"],
                    "content": memory["content"],
                    "memory_type": memory["memory_type"],
                    "tags": json.loads(memory["tags"] or "[]"),
                    "context": memory["context"],
                    "importance": memory["importance"],
                    "created_at": memory["created_at"],
                    "access_count": memory["access_count"]
                }
                results.append(memory_data)
                
                result_text += f"## Memory (ID: {memory['id'][:8]}...)\n"
                result_text += f"**Type**: {memory['memory_type']} | **Importance**: {memory['importance']}\n"
                result_text += f"**Content**: {memory['content']}\n"
                if memory_data['tags']:
                    result_text += f"**Tags**: {', '.join(memory_data['tags'])}\n"
                if memory['context']:
                    result_text += f"**Context**: {memory['context']}\n"
                result_text += f"**Created**: {memory['created_at']}\n\n"
            
            if update_output:
                update_output(f"✅ Retrieved {len(memories)} memories")
            
            return ToolResult(
                success=True,
                content=result_text,
                metadata={
                    "total_results": len(memories),
                    "criteria": {
                        "memory_type": memory_type,
                        "tags": tags,
                        "importance_min": importance_min
                    },
                    "results": results
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error_message=f"Memory retrieval failed: {str(e)}",
                error_type=ToolErrorType.EXECUTION_ERROR
            )
    
    async def _analyze_memories(self, params: Dict[str, Any], update_output: Optional[callable]) -> ToolResult:
        """Analyze memory patterns and statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Get overall statistics
                stats_cursor = conn.execute("""
                    SELECT 
                        COUNT(*) as total_memories,
                        AVG(importance) as avg_importance,
                        MAX(access_count) as max_access_count,
                        AVG(access_count) as avg_access_count,
                        COUNT(DISTINCT memory_type) as unique_types
                    FROM memories
                """)
                stats = stats_cursor.fetchone()
                
                # Get type distribution
                type_cursor = conn.execute("""
                    SELECT memory_type, COUNT(*) as count
                    FROM memories
                    GROUP BY memory_type
                    ORDER BY count DESC
                """)
                type_distribution = type_cursor.fetchall()
                
                # Get most accessed memories
                popular_cursor = conn.execute("""
                    SELECT id, content, access_count, memory_type, importance
                    FROM memories
                    WHERE access_count > 0
                    ORDER BY access_count DESC
                    LIMIT 5
                """)
                popular_memories = popular_cursor.fetchall()
                
                # Get recent memories
                recent_cursor = conn.execute("""
                    SELECT id, content, memory_type, created_at
                    FROM memories
                    ORDER BY created_at DESC
                    LIMIT 5
                """)
                recent_memories = recent_cursor.fetchall()
            
            # Format analysis
            result_text = f"""# Memory System Analysis

## Overall Statistics
- **Total Memories**: {stats['total_memories']:,}
- **Average Importance**: {stats['avg_importance']:.2f}/10
- **Unique Types**: {stats['unique_types']}
- **Average Access Count**: {stats['avg_access_count']:.2f}
- **Most Accessed**: {stats['max_access_count']} times

## Memory Type Distribution
"""
            
            for type_info in type_distribution:
                percentage = (type_info['count'] / stats['total_memories'] * 100) if stats['total_memories'] > 0 else 0
                result_text += f"- **{type_info['memory_type']}**: {type_info['count']} ({percentage:.1f}%)\n"
            
            if popular_memories:
                result_text += f"\n## Most Accessed Memories\n"
                for memory in popular_memories:
                    content_preview = memory['content'][:100] + "..." if len(memory['content']) > 100 else memory['content']
                    result_text += f"- **{memory['id'][:8]}...** ({memory['access_count']} accesses): {content_preview}\n"
            
            if recent_memories:
                result_text += f"\n## Recent Memories\n"
                for memory in recent_memories:
                    content_preview = memory['content'][:100] + "..." if len(memory['content']) > 100 else memory['content']
                    result_text += f"- **{memory['created_at']}** ({memory['memory_type']}): {content_preview}\n"
            
            if update_output:
                update_output("✅ Memory analysis complete")
            
            return ToolResult(
                success=True,
                content=result_text,
                metadata={
                    "statistics": dict(stats),
                    "type_distribution": [dict(row) for row in type_distribution],
                    "popular_memories": [dict(row) for row in popular_memories],
                    "recent_memories": [dict(row) for row in recent_memories]
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error_message=f"Memory analysis failed: {str(e)}",
                error_type=ToolErrorType.EXECUTION_ERROR
            )
    
    def _find_duplicate_memory(self, embedding_hash: str) -> Optional[Dict[str, Any]]:
        """Find if a memory with similar content already exists"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT id, content, memory_type, created_at
                    FROM memories 
                    WHERE embedding_hash = ?
                """, (embedding_hash,))
                
                result = cursor.fetchone()
                return dict(result) if result else None
                
        except Exception:
            return None

# Legacy compatibility with existing DEEP-CLI structure
class EnhancedMemoryManager(BaseTool):
    """Legacy wrapper for enhanced memory tool"""
    
    def __init__(self):
        super().__init__()
        self.enhanced_tool = EnhancedMemoryTool()
    
    def get_schema(self) -> Dict[str, Any]:
        return self.enhanced_tool.schema.parameters
    
    async def execute(self, **kwargs) -> ToolResponse:
        """Execute with legacy ToolResponse format"""
        try:
            result = await self.enhanced_tool.execute_with_validation(
                kwargs, 
                require_confirmation=False
            )
            
            return ToolResponse(
                success=result.success,
                data={"content": result.content, "metadata": result.metadata},
                message=result.error_message if not result.success else "Memory operation completed successfully"
            )
            
        except Exception as e:
            return ToolResponse(
                success=False,
                message=f"Enhanced memory operation failed: {str(e)}"
            )