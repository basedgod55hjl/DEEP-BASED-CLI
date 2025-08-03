"""
SQLite-based memory management system
"""

import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiosqlite

from ..core.exceptions import MemoryError


SCHEMA = """
-- Main memories table
CREATE TABLE IF NOT EXISTS memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    namespace TEXT DEFAULT 'default',
    embedding BLOB,
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    access_count INTEGER DEFAULT 0,
    UNIQUE(key, namespace)
);

-- Sessions table
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE NOT NULL,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    summary TEXT,
    metadata TEXT
);

-- Contexts table for session data
CREATE TABLE IF NOT EXISTS contexts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    context_type TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

-- Patterns table for learning
CREATE TABLE IF NOT EXISTS patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_name TEXT UNIQUE NOT NULL,
    pattern_data TEXT NOT NULL,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    last_used TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_memories_namespace ON memories(namespace);
CREATE INDEX IF NOT EXISTS idx_memories_key ON memories(key);
CREATE INDEX IF NOT EXISTS idx_memories_updated ON memories(updated_at);
CREATE INDEX IF NOT EXISTS idx_contexts_session ON contexts(session_id);
CREATE INDEX IF NOT EXISTS idx_patterns_name ON patterns(pattern_name);
"""


class MemoryManager:
    """Manages persistent memory storage using SQLite"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize database with schema"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.executescript(SCHEMA)
                conn.commit()
        except Exception as e:
            raise MemoryError(f"Failed to initialize memory database: {e}")
    
    async def store(
        self,
        key: str,
        value: Any,
        namespace: str = "default",
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Store a memory item"""
        try:
            # Convert value to JSON string
            if not isinstance(value, str):
                value = json.dumps(value)
            
            metadata_json = json.dumps(metadata) if metadata else None
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO memories 
                    (key, value, namespace, metadata, updated_at)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (key, value, namespace, metadata_json))
                await db.commit()
                
        except Exception as e:
            raise MemoryError(f"Failed to store memory: {e}")
    
    async def recall(
        self,
        key: str,
        namespace: str = "default"
    ) -> Optional[Any]:
        """Recall a memory item by key"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Update access stats
                await db.execute("""
                    UPDATE memories 
                    SET accessed_at = CURRENT_TIMESTAMP,
                        access_count = access_count + 1
                    WHERE key = ? AND namespace = ?
                """, (key, namespace))
                
                # Fetch the memory
                cursor = await db.execute("""
                    SELECT value, metadata FROM memories
                    WHERE key = ? AND namespace = ?
                """, (key, namespace))
                
                row = await cursor.fetchone()
                if row:
                    value, metadata = row
                    try:
                        return json.loads(value)
                    except json.JSONDecodeError:
                        return value
                
                return None
                
        except Exception as e:
            raise MemoryError(f"Failed to recall memory: {e}")
    
    async def search(
        self,
        query: str,
        namespace: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search memories by pattern"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                if namespace:
                    cursor = await db.execute("""
                        SELECT key, value, namespace, metadata, updated_at
                        FROM memories
                        WHERE (key LIKE ? OR value LIKE ?) AND namespace = ?
                        ORDER BY access_count DESC, updated_at DESC
                        LIMIT ?
                    """, (f'%{query}%', f'%{query}%', namespace, limit))
                else:
                    cursor = await db.execute("""
                        SELECT key, value, namespace, metadata, updated_at
                        FROM memories
                        WHERE key LIKE ? OR value LIKE ?
                        ORDER BY access_count DESC, updated_at DESC
                        LIMIT ?
                    """, (f'%{query}%', f'%{query}%', limit))
                
                results = []
                async for row in cursor:
                    key, value, ns, metadata, updated = row
                    try:
                        value = json.loads(value)
                    except json.JSONDecodeError:
                        pass
                    
                    results.append({
                        'key': key,
                        'value': value,
                        'namespace': ns,
                        'metadata': json.loads(metadata) if metadata else {},
                        'updated_at': updated
                    })
                
                return results
                
        except Exception as e:
            raise MemoryError(f"Failed to search memories: {e}")
    
    async def forget(
        self,
        key: str,
        namespace: str = "default"
    ) -> bool:
        """Delete a memory item"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    DELETE FROM memories WHERE key = ? AND namespace = ?
                """, (key, namespace))
                await db.commit()
                
                return cursor.rowcount > 0
                
        except Exception as e:
            raise MemoryError(f"Failed to forget memory: {e}")
    
    async def clear_namespace(self, namespace: str) -> int:
        """Clear all memories in a namespace"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    DELETE FROM memories WHERE namespace = ?
                """, (namespace,))
                await db.commit()
                
                return cursor.rowcount
                
        except Exception as e:
            raise MemoryError(f"Failed to clear namespace: {e}")
    
    async def get_namespaces(self) -> List[str]:
        """Get all namespaces"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT DISTINCT namespace FROM memories ORDER BY namespace
                """)
                
                return [row[0] for row in await cursor.fetchall()]
                
        except Exception as e:
            raise MemoryError(f"Failed to get namespaces: {e}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Total memories
                cursor = await db.execute("SELECT COUNT(*) FROM memories")
                total_memories = (await cursor.fetchone())[0]
                
                # Memories by namespace
                cursor = await db.execute("""
                    SELECT namespace, COUNT(*) FROM memories 
                    GROUP BY namespace ORDER BY COUNT(*) DESC
                """)
                namespace_counts = {row[0]: row[1] for row in await cursor.fetchall()}
                
                # Most accessed
                cursor = await db.execute("""
                    SELECT key, namespace, access_count FROM memories
                    ORDER BY access_count DESC LIMIT 5
                """)
                most_accessed = [
                    {"key": row[0], "namespace": row[1], "count": row[2]}
                    for row in await cursor.fetchall()
                ]
                
                # Recently updated
                cursor = await db.execute("""
                    SELECT key, namespace, updated_at FROM memories
                    ORDER BY updated_at DESC LIMIT 5
                """)
                recent_updates = [
                    {"key": row[0], "namespace": row[1], "updated": row[2]}
                    for row in await cursor.fetchall()
                ]
                
                return {
                    "total_memories": total_memories,
                    "namespaces": namespace_counts,
                    "most_accessed": most_accessed,
                    "recent_updates": recent_updates
                }
                
        except Exception as e:
            raise MemoryError(f"Failed to get stats: {e}")
    
    async def export_namespace(
        self,
        namespace: str,
        output_path: Path
    ) -> None:
        """Export a namespace to JSON file"""
        try:
            memories = await self.search('', namespace=namespace, limit=100000)
            
            export_data = {
                'namespace': namespace,
                'exported_at': datetime.now().isoformat(),
                'count': len(memories),
                'memories': memories
            }
            
            with open(output_path, 'w') as f:
                json.dump(export_data, f, indent=2)
                
        except Exception as e:
            raise MemoryError(f"Failed to export namespace: {e}")
    
    async def import_namespace(
        self,
        input_path: Path,
        namespace: Optional[str] = None
    ) -> int:
        """Import memories from JSON file"""
        try:
            with open(input_path) as f:
                data = json.load(f)
            
            target_namespace = namespace or data.get('namespace', 'default')
            imported = 0
            
            for memory in data.get('memories', []):
                await self.store(
                    key=memory['key'],
                    value=memory['value'],
                    namespace=target_namespace,
                    metadata=memory.get('metadata')
                )
                imported += 1
            
            return imported
            
        except Exception as e:
            raise MemoryError(f"Failed to import namespace: {e}")