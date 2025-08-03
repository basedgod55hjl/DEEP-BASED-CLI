"""
SQL Database Tool - SQLite Integration for DEEP-CLI
Provides persistent storage for conversations, personas, memory, and more
"""

import os
import json
import sqlite3
import asyncio
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import aiosqlite
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from tools.base_tool import BaseTool, ToolResponse, ToolStatus


@dataclass
class Conversation:
    """Represents a conversation"""
    id: Optional[int] = None
    session_id: str = ""
    user_input: str = ""
    assistant_response: str = ""
    timestamp: str = ""
    persona_id: Optional[int] = None
    context: Optional[str] = None
    metadata: Optional[str] = None


@dataclass
class Persona:
    """Represents a persona (like Deanna)"""
    id: Optional[int] = None
    name: str = ""
    description: str = ""
    personality_traits: str = ""
    knowledge_base: str = ""
    conversation_style: str = ""
    created_at: str = ""
    updated_at: str = ""
    is_active: bool = True


@dataclass
class Memory:
    """Represents a memory entry"""
    id: Optional[int] = None
    category: str = ""
    content: str = ""
    importance: int = 5
    access_count: int = 0
    created_at: str = ""
    last_accessed: str = ""
    persona_id: Optional[int] = None
    tags: Optional[str] = None


@dataclass
class Context:
    """Represents contextual information"""
    id: Optional[int] = None
    session_id: str = ""
    context_type: str = ""
    context_data: str = ""
    timestamp: str = ""
    relevance_score: float = 0.0


class SQLDatabaseTool(BaseTool):
    """
    SQL Database Tool with SQLite for persistent storage
    Manages conversations, personas, memory, and context
    """
    
    def __init__(self, db_path: str = "deepcli_database.db"):
        """Initialize SQL Database Tool"""
        super().__init__(
            name="SQL Database",
            description="Persistent storage for conversations, personas, memory, and context",
            capabilities=[
                "conversation_storage",
                "persona_management",
                "memory_storage",
                "context_tracking",
                "query_execution",
                "analytics"
            ]
        )
        
        self.db_path = db_path
        self.console = Console()
        self._initialized = False
        
        # Initialize database
        asyncio.create_task(self._initialize_database())
    
    async def _initialize_database(self):
        """Initialize database with tables"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Enable foreign keys
                await db.execute("PRAGMA foreign_keys = ON")
                
                # Create personas table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS personas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL,
                        description TEXT,
                        personality_traits TEXT,
                        knowledge_base TEXT,
                        conversation_style TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT 1
                    )
                """)
                
                # Create conversations table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS conversations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        user_input TEXT NOT NULL,
                        assistant_response TEXT NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        persona_id INTEGER,
                        context TEXT,
                        metadata TEXT,
                        FOREIGN KEY (persona_id) REFERENCES personas(id)
                    )
                """)
                
                # Create memory table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS memory (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        category TEXT NOT NULL,
                        content TEXT NOT NULL,
                        importance INTEGER DEFAULT 5,
                        access_count INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        persona_id INTEGER,
                        tags TEXT,
                        FOREIGN KEY (persona_id) REFERENCES personas(id)
                    )
                """)
                
                # Create context table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS context (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        context_type TEXT NOT NULL,
                        context_data TEXT NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        relevance_score REAL DEFAULT 0.0
                    )
                """)
                
                # Create analytics table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS analytics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        event_type TEXT NOT NULL,
                        event_data TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        session_id TEXT,
                        persona_id INTEGER,
                        FOREIGN KEY (persona_id) REFERENCES personas(id)
                    )
                """)
                
                # Create indexes
                await db.execute("CREATE INDEX IF NOT EXISTS idx_conversations_session ON conversations(session_id)")
                await db.execute("CREATE INDEX IF NOT EXISTS idx_conversations_persona ON conversations(persona_id)")
                await db.execute("CREATE INDEX IF NOT EXISTS idx_memory_category ON memory(category)")
                await db.execute("CREATE INDEX IF NOT EXISTS idx_memory_persona ON memory(persona_id)")
                await db.execute("CREATE INDEX IF NOT EXISTS idx_context_session ON context(session_id)")
                
                await db.commit()
                
                # Initialize default Deanna persona
                await self._create_deanna_persona(db)
                
                self._initialized = True
                
        except Exception as e:
            self.console.print(f"[red]Database initialization failed: {str(e)}[/red]")
            self._initialized = False
    
    async def _create_deanna_persona(self, db):
        """Create the default Deanna persona"""
        try:
            # Check if Deanna already exists
            cursor = await db.execute("SELECT id FROM personas WHERE name = 'Deanna'")
            existing = await cursor.fetchone()
            
            if not existing:
                deanna = Persona(
                    name="Deanna",
                    description="An advanced AI assistant with deep knowledge in technology, programming, and problem-solving. Friendly, helpful, and always eager to learn.",
                    personality_traits=json.dumps({
                        "traits": ["intelligent", "curious", "helpful", "patient", "creative", "analytical"],
                        "communication_style": "professional yet friendly",
                        "humor": "subtle and witty",
                        "learning_approach": "adaptive and contextual"
                    }),
                    knowledge_base=json.dumps({
                        "domains": ["programming", "AI/ML", "data science", "web development", "system design"],
                        "languages": ["Python", "JavaScript", "SQL", "TypeScript", "Rust"],
                        "frameworks": ["React", "Django", "FastAPI", "TensorFlow", "PyTorch"],
                        "specialties": ["RAG systems", "vector databases", "LLM integration", "code generation"]
                    }),
                    conversation_style=json.dumps({
                        "greeting": "Hello! I'm Deanna, your AI assistant. How can I help you today?",
                        "acknowledgment": "I understand. Let me help you with that.",
                        "thinking": "Let me think about this for a moment...",
                        "clarification": "Could you provide more details about",
                        "completion": "I've completed the task. Is there anything else you'd like me to help with?"
                    }),
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                )
                
                await db.execute("""
                    INSERT INTO personas (name, description, personality_traits, knowledge_base, conversation_style, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (deanna.name, deanna.description, deanna.personality_traits, 
                      deanna.knowledge_base, deanna.conversation_style, deanna.created_at, deanna.updated_at))
                
                await db.commit()
                self.console.print("[green]Created Deanna persona[/green]")
                
        except Exception as e:
            self.console.print(f"[yellow]Failed to create Deanna persona: {str(e)}[/yellow]")
    
    async def execute(self, **kwargs) -> ToolResponse:
        """Execute database operations"""
        if not self._initialized:
            await self._initialize_database()
            
        operation = kwargs.get('operation', 'query')
        
        try:
            if operation == 'store_conversation':
                return await self._store_conversation(kwargs)
            elif operation == 'get_conversations':
                return await self._get_conversations(kwargs)
            elif operation == 'store_memory':
                return await self._store_memory(kwargs)
            elif operation == 'get_memory':
                return await self._get_memory(kwargs)
            elif operation == 'update_persona':
                return await self._update_persona(kwargs)
            elif operation == 'get_persona':
                return await self._get_persona(kwargs)
            elif operation == 'store_context':
                return await self._store_context(kwargs)
            elif operation == 'get_context':
                return await self._get_context(kwargs)
            elif operation == 'execute_query':
                return await self._execute_query(kwargs)
            elif operation == 'get_analytics':
                return await self._get_analytics(kwargs)
            else:
                return ToolResponse(
                    success=False,
                    message=f"Unknown operation: {operation}",
                    status=ToolStatus.FAILED
                )
                
        except Exception as e:
            return ToolResponse(
                success=False,
                message=f"Database error: {str(e)}",
                status=ToolStatus.FAILED
            )
    
    async def _store_conversation(self, kwargs: Dict[str, Any]) -> ToolResponse:
        """Store a conversation"""
        conversation = Conversation(
            session_id=kwargs.get('session_id', ''),
            user_input=kwargs.get('user_input', ''),
            assistant_response=kwargs.get('assistant_response', ''),
            timestamp=kwargs.get('timestamp', datetime.now().isoformat()),
            persona_id=kwargs.get('persona_id'),
            context=kwargs.get('context'),
            metadata=json.dumps(kwargs.get('metadata', {}))
        )
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO conversations (session_id, user_input, assistant_response, timestamp, persona_id, context, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (conversation.session_id, conversation.user_input, conversation.assistant_response,
                  conversation.timestamp, conversation.persona_id, conversation.context, conversation.metadata))
            
            await db.commit()
            conversation.id = cursor.lastrowid
            
            # Log analytics event
            await db.execute("""
                INSERT INTO analytics (event_type, event_data, session_id, persona_id)
                VALUES (?, ?, ?, ?)
            """, ('conversation_stored', json.dumps({'conversation_id': conversation.id}), 
                  conversation.session_id, conversation.persona_id))
            
            await db.commit()
        
        return ToolResponse(
            success=True,
            message="Conversation stored successfully",
            data={"conversation_id": conversation.id}
        )
    
    async def _get_conversations(self, kwargs: Dict[str, Any]) -> ToolResponse:
        """Get conversations with filters"""
        session_id = kwargs.get('session_id')
        persona_id = kwargs.get('persona_id')
        limit = kwargs.get('limit', 10)
        offset = kwargs.get('offset', 0)
        
        query = "SELECT * FROM conversations WHERE 1=1"
        params = []
        
        if session_id:
            query += " AND session_id = ?"
            params.append(session_id)
        
        if persona_id:
            query += " AND persona_id = ?"
            params.append(persona_id)
        
        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(query, params)
            rows = await cursor.fetchall()
            
            conversations = []
            for row in rows:
                conv = dict(row)
                if conv['metadata']:
                    conv['metadata'] = json.loads(conv['metadata'])
                conversations.append(conv)
        
        return ToolResponse(
            success=True,
            message=f"Retrieved {len(conversations)} conversations",
            data={"conversations": conversations}
        )
    
    async def _store_memory(self, kwargs: Dict[str, Any]) -> ToolResponse:
        """Store a memory entry"""
        memory = Memory(
            category=kwargs.get('category', 'general'),
            content=kwargs.get('content', ''),
            importance=kwargs.get('importance', 5),
            persona_id=kwargs.get('persona_id'),
            tags=json.dumps(kwargs.get('tags', []))
        )
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO memory (category, content, importance, persona_id, tags)
                VALUES (?, ?, ?, ?, ?)
            """, (memory.category, memory.content, memory.importance, memory.persona_id, memory.tags))
            
            await db.commit()
            memory.id = cursor.lastrowid
        
        return ToolResponse(
            success=True,
            message="Memory stored successfully",
            data={"memory_id": memory.id}
        )
    
    async def _get_memory(self, kwargs: Dict[str, Any]) -> ToolResponse:
        """Get memory entries with filters"""
        category = kwargs.get('category')
        persona_id = kwargs.get('persona_id')
        importance_min = kwargs.get('importance_min', 0)
        limit = kwargs.get('limit', 10)
        
        query = "SELECT * FROM memory WHERE importance >= ?"
        params = [importance_min]
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        if persona_id:
            query += " AND persona_id = ?"
            params.append(persona_id)
        
        query += " ORDER BY importance DESC, last_accessed DESC LIMIT ?"
        params.append(limit)
        
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(query, params)
            rows = await cursor.fetchall()
            
            memories = []
            for row in rows:
                mem = dict(row)
                if mem['tags']:
                    mem['tags'] = json.loads(mem['tags'])
                memories.append(mem)
                
                # Update access count
                await db.execute(
                    "UPDATE memory SET access_count = access_count + 1, last_accessed = ? WHERE id = ?",
                    (datetime.now().isoformat(), row['id'])
                )
            
            await db.commit()
        
        return ToolResponse(
            success=True,
            message=f"Retrieved {len(memories)} memories",
            data={"memories": memories}
        )
    
    async def _update_persona(self, kwargs: Dict[str, Any]) -> ToolResponse:
        """Update persona information"""
        persona_name = kwargs.get('name', 'Deanna')
        updates = kwargs.get('updates', {})
        
        if not updates:
            return ToolResponse(
                success=False,
                message="No updates provided",
                status=ToolStatus.FAILED
            )
        
        # Build update query
        set_clauses = []
        params = []
        
        for key, value in updates.items():
            if key in ['description', 'personality_traits', 'knowledge_base', 'conversation_style']:
                set_clauses.append(f"{key} = ?")
                params.append(json.dumps(value) if isinstance(value, (dict, list)) else value)
        
        if not set_clauses:
            return ToolResponse(
                success=False,
                message="No valid fields to update",
                status=ToolStatus.FAILED
            )
        
        set_clauses.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        
        query = f"UPDATE personas SET {', '.join(set_clauses)} WHERE name = ?"
        params.append(persona_name)
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(query, params)
            await db.commit()
        
        return ToolResponse(
            success=True,
            message=f"Updated persona: {persona_name}",
            data={"persona": persona_name}
        )
    
    async def _get_persona(self, kwargs: Dict[str, Any]) -> ToolResponse:
        """Get persona information"""
        persona_name = kwargs.get('name', 'Deanna')
        
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM personas WHERE name = ? AND is_active = 1",
                (persona_name,)
            )
            row = await cursor.fetchone()
            
            if not row:
                return ToolResponse(
                    success=False,
                    message=f"Persona not found: {persona_name}",
                    status=ToolStatus.FAILED
                )
            
            persona = dict(row)
            # Parse JSON fields
            for field in ['personality_traits', 'knowledge_base', 'conversation_style']:
                if persona[field]:
                    persona[field] = json.loads(persona[field])
        
        return ToolResponse(
            success=True,
            message=f"Retrieved persona: {persona_name}",
            data={"persona": persona}
        )
    
    async def _store_context(self, kwargs: Dict[str, Any]) -> ToolResponse:
        """Store contextual information"""
        context = Context(
            session_id=kwargs.get('session_id', ''),
            context_type=kwargs.get('context_type', 'general'),
            context_data=json.dumps(kwargs.get('context_data', {})),
            timestamp=kwargs.get('timestamp', datetime.now().isoformat()),
            relevance_score=kwargs.get('relevance_score', 0.0)
        )
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO context (session_id, context_type, context_data, timestamp, relevance_score)
                VALUES (?, ?, ?, ?, ?)
            """, (context.session_id, context.context_type, context.context_data, 
                  context.timestamp, context.relevance_score))
            
            await db.commit()
            context.id = cursor.lastrowid
        
        return ToolResponse(
            success=True,
            message="Context stored successfully",
            data={"context_id": context.id}
        )
    
    async def _get_context(self, kwargs: Dict[str, Any]) -> ToolResponse:
        """Get contextual information"""
        session_id = kwargs.get('session_id')
        context_type = kwargs.get('context_type')
        min_relevance = kwargs.get('min_relevance', 0.0)
        limit = kwargs.get('limit', 10)
        
        query = "SELECT * FROM context WHERE relevance_score >= ?"
        params = [min_relevance]
        
        if session_id:
            query += " AND session_id = ?"
            params.append(session_id)
        
        if context_type:
            query += " AND context_type = ?"
            params.append(context_type)
        
        query += " ORDER BY relevance_score DESC, timestamp DESC LIMIT ?"
        params.append(limit)
        
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(query, params)
            rows = await cursor.fetchall()
            
            contexts = []
            for row in rows:
                ctx = dict(row)
                if ctx['context_data']:
                    ctx['context_data'] = json.loads(ctx['context_data'])
                contexts.append(ctx)
        
        return ToolResponse(
            success=True,
            message=f"Retrieved {len(contexts)} contexts",
            data={"contexts": contexts}
        )
    
    async def _execute_query(self, kwargs: Dict[str, Any]) -> ToolResponse:
        """Execute a custom SQL query (read-only)"""
        query = kwargs.get('query', '')
        params = kwargs.get('params', [])
        
        if not query:
            return ToolResponse(
                success=False,
                message="No query provided",
                status=ToolStatus.FAILED
            )
        
        # Only allow SELECT queries for safety
        if not query.strip().upper().startswith('SELECT'):
            return ToolResponse(
                success=False,
                message="Only SELECT queries are allowed",
                status=ToolStatus.FAILED
            )
        
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(query, params)
            rows = await cursor.fetchall()
            
            results = [dict(row) for row in rows]
        
        return ToolResponse(
            success=True,
            message=f"Query executed, returned {len(results)} rows",
            data={"results": results}
        )
    
    async def _get_analytics(self, kwargs: Dict[str, Any]) -> ToolResponse:
        """Get analytics data"""
        event_type = kwargs.get('event_type')
        session_id = kwargs.get('session_id')
        persona_id = kwargs.get('persona_id')
        days = kwargs.get('days', 7)
        
        # Calculate date threshold
        date_threshold = datetime.now().timestamp() - (days * 24 * 60 * 60)
        date_threshold_str = datetime.fromtimestamp(date_threshold).isoformat()
        
        query = "SELECT * FROM analytics WHERE timestamp >= ?"
        params = [date_threshold_str]
        
        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)
        
        if session_id:
            query += " AND session_id = ?"
            params.append(session_id)
        
        if persona_id:
            query += " AND persona_id = ?"
            params.append(persona_id)
        
        query += " ORDER BY timestamp DESC"
        
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(query, params)
            rows = await cursor.fetchall()
            
            events = []
            for row in rows:
                evt = dict(row)
                if evt['event_data']:
                    evt['event_data'] = json.loads(evt['event_data'])
                events.append(evt)
            
            # Generate summary statistics
            event_counts = {}
            for event in events:
                event_type = event['event_type']
                event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        return ToolResponse(
            success=True,
            message=f"Retrieved {len(events)} analytics events",
            data={
                "events": events,
                "summary": event_counts,
                "period_days": days
            }
        )
    
    def get_schema(self) -> Dict[str, Any]:
        """Get tool schema"""
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["store_conversation", "get_conversations", "store_memory", 
                            "get_memory", "update_persona", "get_persona", "store_context",
                            "get_context", "execute_query", "get_analytics"],
                    "description": "Database operation to perform"
                },
                "session_id": {"type": "string", "description": "Session identifier"},
                "user_input": {"type": "string", "description": "User input text"},
                "assistant_response": {"type": "string", "description": "Assistant response text"},
                "persona_id": {"type": "integer", "description": "Persona ID"},
                "persona_name": {"type": "string", "description": "Persona name"},
                "category": {"type": "string", "description": "Category for memory/context"},
                "content": {"type": "string", "description": "Content to store"},
                "importance": {"type": "integer", "description": "Importance level (1-10)"},
                "context_type": {"type": "string", "description": "Type of context"},
                "context_data": {"type": "object", "description": "Context data object"},
                "relevance_score": {"type": "number", "description": "Relevance score (0-1)"},
                "query": {"type": "string", "description": "SQL query to execute"},
                "params": {"type": "array", "description": "Query parameters"},
                "limit": {"type": "integer", "description": "Result limit"},
                "offset": {"type": "integer", "description": "Result offset"},
                "updates": {"type": "object", "description": "Updates to apply"},
                "tags": {"type": "array", "items": {"type": "string"}, "description": "Tags"},
                "metadata": {"type": "object", "description": "Additional metadata"}
            },
            "required": ["operation"]
        }