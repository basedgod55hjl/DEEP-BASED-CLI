#!/usr/bin/env python3
"""
Comprehensive Memory Manager for DEEP-CLI
Handles DEANNA_MEMORY.JSON, DeepSeek context caching, embeddings, and data storage
"""

import json
import sqlite3
import os
import hashlib
import pickle
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import numpy as np
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/deanna_memory.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DeannaMemoryManager:
    """Comprehensive memory manager for Deanna persona"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialize subdirectories
        self.memory_dir = self.data_dir / "memory"
        self.embeddings_dir = self.data_dir / "embeddings"
        self.chats_dir = self.data_dir / "chats"
        self.logs_dir = self.data_dir / "logs"
        self.cache_dir = self.data_dir / "cache"
        
        for dir_path in [self.memory_dir, self.embeddings_dir, self.chats_dir, self.logs_dir, self.cache_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # Initialize database
        self.db_path = self.data_dir / "deanna_memory.db"
        self.init_database()
        
        # Load Deanna memory
        self.deanna_memory = self.load_deanna_memory()
        
        # Initialize embedding cache
        self.embedding_cache = {}
        self.load_embedding_cache()
        
        logger.info("DeannaMemoryManager initialized successfully")
    
    def init_database(self) -> Any:
        """Initialize SQLite database with all required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Core memory table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                content TEXT NOT NULL,
                embedding_hash TEXT,
                importance INTEGER DEFAULT 5,
                access_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tags TEXT,
                metadata TEXT
            )
        ''')
        
        # Chat history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                user_input TEXT NOT NULL,
                deanna_response TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                context_hash TEXT,
                emotion_score REAL DEFAULT 0.0,
                tags TEXT
            )
        ''')
        
        # DeepSeek context cache table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deepseek_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt_hash TEXT UNIQUE NOT NULL,
                response TEXT NOT NULL,
                model_used TEXT,
                tokens_used INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                cost REAL DEFAULT 0.0,
                context_length INTEGER
            )
        ''')
        
        # Embedding vectors table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_hash TEXT UNIQUE NOT NULL,
                vector_data BLOB NOT NULL,
                dimension INTEGER,
                model_used TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Persona configuration table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS persona_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                config_data TEXT NOT NULL,
                version TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Memory access logs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS access_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_id INTEGER,
                access_type TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                session_id TEXT,
                metadata TEXT,
                FOREIGN KEY (memory_id) REFERENCES memory_entries(id)
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_category ON memory_entries(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_tags ON memory_entries(tags)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_chat_session ON chat_history(session_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_cache_hash ON deepseek_cache(prompt_hash)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_embeddings_hash ON embeddings(content_hash)')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized with all tables")
    
    def load_deanna_memory(self) -> Dict[str, Any]:
        """Load DEANNA_MEMORY.JSON file"""
        json_path = self.data_dir / "DEANNA_MEMORY.JSON"
        
        if not json_path.exists():
            logger.error(f"DEANNA_MEMORY.JSON not found at {json_path}")
            return {}
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                memory_data = json.load(f)
            
            # Store in database
            self.store_persona_config("DEANNA", memory_data)
            
            # Extract and store key components as memory entries
            self.extract_memory_components(memory_data)
            
            logger.info(f"Successfully loaded DEANNA_MEMORY.JSON ({len(memory_data)} keys)")
            return memory_data
        
        except Exception as e:
            logger.error(f"Error loading DEANNA_MEMORY.JSON: {e}")
            return {}
    
    def store_persona_config(self, name: str, config_data: Dict[str, Any]):
        """Store persona configuration in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO persona_config (name, config_data, version, updated_at)
            VALUES (?, ?, ?, ?)
        ''', (
            name,
            json.dumps(config_data),
            config_data.get('version', '1.0.0'),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        logger.info(f"Stored persona config for {name}")
    
    def extract_memory_components(self, memory_data: Dict[str, Any]):
        """Extract key components from memory data and store as separate entries"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Store system prompt
        if 'system_prompt' in memory_data:
            self.store_memory_entry(
                'system_prompt',
                memory_data['system_prompt'],
                importance=10,
                tags='core,personality,deanna'
            )
        
        # Store personality traits
        if 'personality_traits' in memory_data:
            self.store_memory_entry(
                'personality_traits',
                json.dumps(memory_data['personality_traits']),
                importance=9,
                tags='personality,deanna'
            )
        
        # Store conversation style
        if 'conversation_style' in memory_data:
            self.store_memory_entry(
                'conversation_style',
                json.dumps(memory_data['conversation_style']),
                importance=9,
                tags='conversation,style,deanna'
            )
        
        # Store additional context sections
        if 'additional_context' in memory_data:
            for key, value in memory_data['additional_context'].items():
                self.store_memory_entry(
                    f'context_{key}',
                    json.dumps(value),
                    importance=8,
                    tags=f'context,{key},deanna'
                )
        
        # Store behavioral patterns
        if 'behavioral_patterns' in memory_data:
            self.store_memory_entry(
                'behavioral_patterns',
                json.dumps(memory_data['behavioral_patterns']),
                importance=9,
                tags='behavior,patterns,deanna'
            )
        
        # Store response preferences
        if 'response_preferences' in memory_data:
            self.store_memory_entry(
                'response_preferences',
                json.dumps(memory_data['response_preferences']),
                importance=9,
                tags='responses,preferences,deanna'
            )
        
        conn.close()
        logger.info("Extracted and stored memory components")
    
    def store_memory_entry(self, category: str, content: str, importance: int = 5, tags: str = ""):
        """Store a memory entry"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        content_hash = hashlib.md5(content.encode()).hexdigest()
        
        cursor.execute('''
            INSERT OR REPLACE INTO memory_entries 
            (category, content, embedding_hash, importance, tags, last_accessed)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            category,
            content,
            content_hash,
            importance,
            tags,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def store_chat_history(self, session_id: str, user_input: str, deanna_response: str, 
                          context_hash: str = None, emotion_score: float = 0.0, tags: str = ""):
        """Store chat history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO chat_history 
            (session_id, user_input, deanna_response, context_hash, emotion_score, tags)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            session_id,
            user_input,
            deanna_response,
            context_hash,
            emotion_score,
            tags
        ))
        
        conn.commit()
        conn.close()
        
        # Also save to file for backup
        chat_file = self.chats_dir / f"{session_id}.json"
        chat_data = {
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'deanna_response': deanna_response,
            'context_hash': context_hash,
            'emotion_score': emotion_score,
            'tags': tags
        }
        
        with open(chat_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(chat_data) + '\n')
    
    def cache_deepseek_response(self, prompt: str, response: str, model_used: str = "deepseek-chat",
                               tokens_used: int = 0, cost: float = 0.0, context_length: int = 0):
        """Cache DeepSeek API response"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
        
        cursor.execute('''
            INSERT OR REPLACE INTO deepseek_cache 
            (prompt_hash, response, model_used, tokens_used, cost, context_length)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            prompt_hash,
            response,
            model_used,
            tokens_used,
            cost,
            context_length
        ))
        
        conn.commit()
        conn.close()
        
        # Also save to file cache
        cache_file = self.cache_dir / f"{prompt_hash}.json"
        cache_data = {
            'prompt': prompt,
            'response': response,
            'model_used': model_used,
            'tokens_used': tokens_used,
            'cost': cost,
            'context_length': context_length,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2)
    
    def get_cached_response(self, prompt: str) -> Optional[str]:
        """Get cached DeepSeek response"""
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
        
        # Check file cache first
        cache_file = self.cache_dir / f"{prompt_hash}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                return cache_data['response']
            except Exception as e:
                pass
        
        # Check database cache
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT response FROM deepseek_cache WHERE prompt_hash = ?', (prompt_hash,))
        result = cursor.fetchone()
        
        conn.close()
        
        return result[0] if result else None
    
    def store_embedding(self, content: str, vector: np.ndarray, model_used: str = "local"):
        """Store embedding vector"""
        content_hash = hashlib.md5(content.encode()).hexdigest()
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        vector_blob = pickle.dumps(vector)
        
        cursor.execute('''
            INSERT OR REPLACE INTO embeddings 
            (content_hash, vector_data, dimension, model_used)
            VALUES (?, ?, ?, ?)
        ''', (
            content_hash,
            vector_blob,
            len(vector),
            model_used
        ))
        
        conn.commit()
        conn.close()
        
        # Store in file cache
        embedding_file = self.embeddings_dir / f"{content_hash}.npy"
        np.save(embedding_file, vector)
        
        # Update memory entry with embedding hash
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE memory_entries 
            SET embedding_hash = ? 
            WHERE content = ?
        ''', (content_hash, content))
        
        conn.commit()
        conn.close()
        
        self.embedding_cache[content_hash] = vector
        logger.info(f"Stored embedding for content hash: {content_hash}")
    
    def get_embedding(self, content_hash: str) -> Optional[np.ndarray]:
        """Get embedding vector"""
        # Check memory cache first
        if content_hash in self.embedding_cache:
            return self.embedding_cache[content_hash]
        
        # Check file cache
        embedding_file = self.embeddings_dir / f"{content_hash}.npy"
        if embedding_file.exists():
            vector = np.load(embedding_file)
            self.embedding_cache[content_hash] = vector
            return vector
        
        # Check database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT vector_data FROM embeddings WHERE content_hash = ?', (content_hash,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            vector = pickle.loads(result[0])
            self.embedding_cache[content_hash] = vector
            return vector
        
        return None
    
    def load_embedding_cache(self) -> Any:
        """Load embedding cache from files"""
        for embedding_file in self.embeddings_dir.glob("*.npy"):
            content_hash = embedding_file.stem
            vector = np.load(embedding_file)
            self.embedding_cache[content_hash] = vector
        
        logger.info(f"Loaded {len(self.embedding_cache)} embeddings into cache")
    
    def search_memory(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search memory entries by content similarity"""
        # Simple text-based search for now
        # FIXME: [PRIORITY]  [PRIORITY]  Implement vector similarity search when embeddings are available
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT category, content, importance, tags, last_accessed
            FROM memory_entries 
            WHERE content LIKE ? OR tags LIKE ?
            ORDER BY importance DESC, last_accessed DESC
            LIMIT ?
        ''', (f'%{query}%', f'%{query}%', limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'category': row[0],
                'content': row[1],
                'importance': row[2],
                'tags': row[3],
                'last_accessed': row[4]
            })
        
        conn.close()
        return results
    
    def get_persona_config(self, name: str = "DEANNA") -> Dict[str, Any]:
        """Get persona configuration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT config_data FROM persona_config WHERE name = ?', (name,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            return json.loads(result[0])
        return {}
    
    def log_access(self, memory_id: int, access_type: str, session_id: str = None, metadata: str = None):
        """Log memory access"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO access_logs (memory_id, access_type, session_id, metadata)
            VALUES (?, ?, ?, ?)
        ''', (memory_id, access_type, session_id, metadata))
        
        # Update access count and last accessed
        cursor.execute('''
            UPDATE memory_entries 
            SET access_count = access_count + 1, last_accessed = ?
            WHERE id = ?
        ''', (datetime.now().isoformat(), memory_id))
        
        conn.commit()
        conn.close()
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Count memory entries
        cursor.execute('SELECT COUNT(*) FROM memory_entries')
        memory_count = cursor.fetchone()[0]
        
        # Count chat entries
        cursor.execute('SELECT COUNT(*) FROM chat_history')
        chat_count = cursor.fetchone()[0]
        
        # Count cached responses
        cursor.execute('SELECT COUNT(*) FROM deepseek_cache')
        cache_count = cursor.fetchone()[0]
        
        # Count embeddings
        cursor.execute('SELECT COUNT(*) FROM embeddings')
        embedding_count = cursor.fetchone()[0]
        
        # Get total cost
        cursor.execute('SELECT SUM(cost) FROM deepseek_cache')
        total_cost = cursor.fetchone()[0] or 0.0
        
        conn.close()
        
        return {
            'memory_entries': memory_count,
            'chat_entries': chat_count,
            'cached_responses': cache_count,
            'embeddings': embedding_count,
            'total_cost': total_cost,
            'embedding_cache_size': len(self.embedding_cache)
        }
    
    def cleanup_old_cache(self, days: int = 30):
        """Clean up old cache entries"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clean up old chat history
        cursor.execute('''
            DELETE FROM chat_history 
            WHERE timestamp < ?
        ''', (cutoff_date.isoformat(),))
        
        # Clean up old cache entries
        cursor.execute('''
            DELETE FROM deepseek_cache 
            WHERE timestamp < ?
        ''', (cutoff_date.isoformat(),))
        
        # Clean up old access logs
        cursor.execute('''
            DELETE FROM access_logs 
            WHERE timestamp < ?
        ''', (cutoff_date.isoformat(),))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Cleaned up cache entries older than {days} days")
    
    def export_memory_data(self, export_path: str):
        """Export all memory data to JSON"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'memory_entries': [],
            'chat_history': [],
            'persona_configs': [],
            'statistics': self.get_memory_stats()
        }
        
        # Export memory entries
        cursor.execute('SELECT * FROM memory_entries')
        for row in cursor.fetchall():
            export_data['memory_entries'].append({
                'id': row[0],
                'category': row[1],
                'content': row[2],
                'embedding_hash': row[3],
                'importance': row[4],
                'access_count': row[5],
                'created_at': row[6],
                'last_accessed': row[7],
                'tags': row[8],
                'metadata': row[9]
            })
        
        # Export chat history
        cursor.execute('SELECT * FROM chat_history')
        for row in cursor.fetchall():
            export_data['chat_history'].append({
                'id': row[0],
                'session_id': row[1],
                'user_input': row[2],
                'deanna_response': row[3],
                'timestamp': row[4],
                'context_hash': row[5],
                'emotion_score': row[6],
                'tags': row[7]
            })
        
        # Export persona configs
        cursor.execute('SELECT * FROM persona_config')
        for row in cursor.fetchall():
            export_data['persona_configs'].append({
                'id': row[0],
                'name': row[1],
                'config_data': json.loads(row[2]),
                'version': row[3],
                'created_at': row[4],
                'updated_at': row[5]
            })
        
        conn.close()
        
        # Save to file
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"Exported memory data to {export_path}")

# Global instance
memory_manager = DeannaMemoryManager()

if __name__ == "__main__":
    # Test the memory manager
    logging.info("Testing DeannaMemoryManager...")
    
    # Get stats
    stats = memory_manager.get_memory_stats()
    logging.info(f"Memory Stats: {stats}")
    
    # Search for some memory
    results = memory_manager.search_memory("personality")
    logging.info(f"Found {len(results)} personality-related entries")
    
    logging.info("Memory manager test completed!") 