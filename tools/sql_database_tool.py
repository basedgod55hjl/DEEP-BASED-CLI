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
            elif operation == 'store_persona':
                return await self._store_persona(kwargs)
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
    
    async def store_conversation(self, conversation_data: Dict[str, Any]) -> ToolResponse:
        """Store conversation in database"""
        try:
            conversation_id = conversation_data.get("id")
            user_id = conversation_data.get("user_id", "default")
            messages = conversation_data.get("messages", [])
            persona_id = conversation_data.get("persona_id")
            metadata = conversation_data.get("metadata", {})
            
            async with aiosqlite.connect(self.db_path) as db:
                # Store conversation
                await db.execute("""
                    INSERT OR REPLACE INTO conversations 
                    (id, user_id, persona_id, metadata, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    conversation_id,
                    user_id,
                    persona_id,
                    json.dumps(metadata),
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))
                
                # Store messages
                for i, message in enumerate(messages):
                    await db.execute("""
                        INSERT INTO conversation_messages 
                        (conversation_id, message_index, role, content, timestamp)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        conversation_id,
                        i,
                        message.get("role", "user"),
                        message.get("content", ""),
                        message.get("timestamp", datetime.now().isoformat())
                    ))
                
                await db.commit()
            
            return ToolResponse(
                success=True,
                data={
                    "conversation_id": conversation_id,
                    "messages_stored": len(messages),
                    "user_id": user_id
                },
                message=f"Successfully stored conversation with {len(messages)} messages"
            )
            
        except Exception as e:
            self.console.print(f"[red]Failed to store conversation: {str(e)}[/red]")
            return ToolResponse(
                success=False,
                data={"error": str(e)},
                message=f"Failed to store conversation: {str(e)}"
            )
    
    async def get_conversation(self, conversation_id: str) -> ToolResponse:
        """Get conversation by ID"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Get conversation
                async with db.execute("""
                    SELECT id, user_id, persona_id, metadata, created_at, updated_at
                    FROM conversations WHERE id = ?
                """, (conversation_id,)) as cursor:
                    conversation_row = await cursor.fetchone()
                
                if not conversation_row:
                    return ToolResponse(
                        success=False,
                        data={"error": "Conversation not found"},
                        message=f"Conversation {conversation_id} not found"
                    )
                
                # Get messages
                async with db.execute("""
                    SELECT role, content, timestamp
                    FROM conversation_messages 
                    WHERE conversation_id = ?
                    ORDER BY message_index
                """, (conversation_id,)) as cursor:
                    message_rows = await cursor.fetchall()
                
                messages = []
                for row in message_rows:
                    messages.append({
                        "role": row[0],
                        "content": row[1],
                        "timestamp": row[2]
                    })
                
                conversation_data = {
                    "id": conversation_row[0],
                    "user_id": conversation_row[1],
                    "persona_id": conversation_row[2],
                    "metadata": json.loads(conversation_row[3]) if conversation_row[3] else {},
                    "created_at": conversation_row[4],
                    "updated_at": conversation_row[5],
                    "messages": messages
                }
                
                return ToolResponse(
                    success=True,
                    data=conversation_data,
                    message=f"Retrieved conversation {conversation_id}"
                )
                
        except Exception as e:
            self.console.print(f"[red]Failed to get conversation: {str(e)}[/red]")
            return ToolResponse(
                success=False,
                data={"error": str(e)},
                message=f"Failed to get conversation: {str(e)}"
            )
    
    async def list_conversations(self, user_id: str = None, limit: int = 50) -> ToolResponse:
        """List conversations"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                if user_id:
                    async with db.execute("""
                        SELECT id, user_id, persona_id, created_at, updated_at
                        FROM conversations 
                        WHERE user_id = ?
                        ORDER BY updated_at DESC
                        LIMIT ?
                    """, (user_id, limit)) as cursor:
                        rows = await cursor.fetchall()
                else:
                    async with db.execute("""
                        SELECT id, user_id, persona_id, created_at, updated_at
                        FROM conversations 
                        ORDER BY updated_at DESC
                        LIMIT ?
                    """, (limit,)) as cursor:
                        rows = await cursor.fetchall()
                
                conversations = []
                for row in rows:
                    conversations.append({
                        "id": row[0],
                        "user_id": row[1],
                        "persona_id": row[2],
                        "created_at": row[3],
                        "updated_at": row[4]
                    })
                
                return ToolResponse(
                    success=True,
                    data={
                        "conversations": conversations,
                        "total": len(conversations)
                    },
                    message=f"Retrieved {len(conversations)} conversations"
                )
                
        except Exception as e:
            self.console.print(f"[red]Failed to list conversations: {str(e)}[/red]")
            return ToolResponse(
                success=False,
                data={"error": str(e)},
                message=f"Failed to list conversations: {str(e)}"
            )
    
    async def delete_conversation(self, conversation_id: str) -> ToolResponse:
        """Delete conversation by ID"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Delete messages first
                await db.execute("""
                    DELETE FROM conversation_messages WHERE conversation_id = ?
                """, (conversation_id,))
                
                # Delete conversation
                await db.execute("""
                    DELETE FROM conversations WHERE id = ?
                """, (conversation_id,))
                
                await db.commit()
            
            return ToolResponse(
                success=True,
                data={"conversation_id": conversation_id},
                message=f"Successfully deleted conversation {conversation_id}"
            )
            
        except Exception as e:
            self.console.print(f"[red]Failed to delete conversation: {str(e)}[/red]")
            return ToolResponse(
                success=False,
                data={"error": str(e)},
                message=f"Failed to delete conversation: {str(e)}"
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
    
    async def _store_persona(self, kwargs: Dict[str, Any]) -> ToolResponse:
        """Store a persona"""
        persona = Persona(
            name=kwargs.get('name', ''),
            description=kwargs.get('description', ''),
            personality_traits=json.dumps(kwargs.get('personality_traits', {})),
            knowledge_base=json.dumps(kwargs.get('knowledge_base', {})),
            conversation_style=json.dumps(kwargs.get('conversation_style', {})),
            is_active=kwargs.get('is_active', True)
        )
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO personas (name, description, personality_traits, knowledge_base, conversation_style, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (persona.name, persona.description, persona.personality_traits, 
                  persona.knowledge_base, persona.conversation_style, persona.is_active))
            
            await db.commit()
            persona.id = cursor.lastrowid
        
        return ToolResponse(
            success=True,
            message="Persona stored successfully",
            data={"persona_id": persona.id}
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
<<<<<<< Current (Your changes)
=======
    SQL Database Tool for local data storage and retrieval
    """
    
    def __init__(self, db_path: str = "data/deepcli_database.db"):
        super().__init__(
            name="sql_database",
            description="SQL database operations for local storage",
            capabilities=["query", "store", "retrieve", "update", "delete"]
        )
        self.db_path = db_path
    
    async def execute(self, **kwargs) -> ToolResponse:
        """Execute SQL database operations"""
        operation = kwargs.get("operation", "query")
        
        try:
            if operation == "query":
                return await self._execute_query(kwargs)
            elif operation == "store":
                return await self._store_data(kwargs)
            elif operation == "retrieve":
                return await self._retrieve_data(kwargs)
            else:
                return ToolResponse(
                    success=False,
                    message=f"Unknown operation: {operation}"
                )
        except Exception as e:
            return ToolResponse(
                success=False,
                message=f"Database error: {str(e)}"
            )
    
    async def _execute_query(self, kwargs: Dict[str, Any]) -> ToolResponse:
        """Execute a query"""
        query = kwargs.get("query", "")
        params = kwargs.get("params", [])
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute(query, params) as cursor:
                    rows = await cursor.fetchall()
                    columns = [description[0] for description in cursor.description] if cursor.description else []
                    
                    results = []
                    for row in rows:
                        results.append(dict(zip(columns, row)))
                    
                    return ToolResponse(
                        success=True,
                        message=f"Query executed successfully. Found {len(results)} results.",
                        data={"results": results}
                    )
        except Exception as e:
            return ToolResponse(
                success=False,
                message=f"Query error: {str(e)}"
            )
    
    async def _store_data(self, kwargs: Dict[str, Any]) -> ToolResponse:
        """Store data in the database"""
        table = kwargs.get("table", "")
        data = kwargs.get("data", {})
        
        if not table or not data:
            return ToolResponse(
                success=False,
                message="Table name and data are required"
            )
        
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?" for _ in data])
        values = list(data.values())
        
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(query, values)
                await db.commit()
                
                return ToolResponse(
                    success=True,
                    message=f"Data stored successfully in {table}",
                    data={"table": table, "inserted": True}
                )
        except Exception as e:
            return ToolResponse(
                success=False,
                message=f"Store error: {str(e)}"
            )
    
    async def _retrieve_data(self, kwargs: Dict[str, Any]) -> ToolResponse:
        """Retrieve data from the database"""
        table = kwargs.get("table", "")
        conditions = kwargs.get("conditions", {})
        limit = kwargs.get("limit", 100)
        
        if not table:
            return ToolResponse(
                success=False,
                message="Table name is required"
            )
        
        where_clause = ""
        values = []
        if conditions:
            where_parts = []
            for key, value in conditions.items():
                where_parts.append(f"{key} = ?")
                values.append(value)
            where_clause = " WHERE " + " AND ".join(where_parts)
        
        query = f"SELECT * FROM {table}{where_clause} LIMIT ?"
        values.append(limit)
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute(query, values) as cursor:
                    rows = await cursor.fetchall()
                    columns = [description[0] for description in cursor.description] if cursor.description else []
                    
                    results = []
                    for row in rows:
                        results.append(dict(zip(columns, row)))
                    
                    return ToolResponse(
                        success=True,
                        message=f"Retrieved {len(results)} records from {table}",
                        data={"results": results}
                    )
        except Exception as e:
            return ToolResponse(
                success=False,
                message=f"Retrieve error: {str(e)}"
            )
    
    def get_schema(self) -> Dict[str, Any]:
        """Get the tool schema"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "operation": {
                    "type": "string",
                    "description": "Operation to perform",
                    "enum": ["query", "store", "retrieve", "update", "delete"]
                },
                "query": {
                    "type": "string",
                    "description": "SQL query to execute (for query operation)"
                },
                "table": {
                    "type": "string",
                    "description": "Table name (for store/retrieve operations)"
                },
                "data": {
                    "type": "object",
                    "description": "Data to store (for store operation)"
                },
                "conditions": {
                    "type": "object",
                    "description": "Conditions for retrieval (for retrieve operation)"
                }
            }
        } 
>>>>>>> Incoming (Background Agent changes)
>>>>>>> d56552d76c9eaadc6392dfb8e6c57491de43475f
=======
>>>>>>> Incoming (Background Agent changes)
