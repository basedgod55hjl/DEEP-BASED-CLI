#!/usr/bin/env python3
"""
Enhanced Memory Manager - Complete Rewrite Example
Demonstrates Claude 4's analytical approach to codebase improvement

This file shows how to rewrite the memory manager with:
- Vector similarity search implementation
- Async database operations
- Proper error handling and logging
- Type hints throughout
- Performance optimizations
- Caching strategies
"""

import asyncio
import json
import logging
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import aiosqlite
from dataclasses import dataclass, asdict
from functools import lru_cache
import hashlib

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class MemoryEntry:
    """Structured memory entry with type safety"""
    id: Optional[int]
    category: str
    content: str
    importance: int
    tags: str
    embedding: Optional[np.ndarray]
    access_count: int
    last_accessed: str
    created_at: str
    updated_at: str

@dataclass
class SearchResult:
    """Structured search result"""
    entry: MemoryEntry
    similarity_score: float
    relevance_score: float

class EnhancedMemoryManager:
    """
    Enhanced memory manager with vector similarity search, async operations,
    and intelligent caching
    """
    
    def __init__(self, data_dir: str = "data", max_cache_size: int = 1000):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.db_path = self.data_dir / "deanna_memory.db"
        self.embedding_cache: Dict[str, np.ndarray] = {}
        self.search_cache: Dict[str, List[SearchResult]] = {}
        self.max_cache_size = max_cache_size
        
        # Performance tracking
        self.stats = {
            'total_searches': 0,
            'cache_hits': 0,
            'vector_searches': 0,
            'text_searches': 0,
            'avg_search_time': 0.0
        }
        
        # Initialize database
        asyncio.create_task(self._init_database())
    
    async def _init_database(self) -> None:
        """Initialize database with enhanced schema"""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS memory_entries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        category TEXT NOT NULL,
                        content TEXT NOT NULL,
                        importance INTEGER DEFAULT 5,
                        tags TEXT DEFAULT '',
                        embedding BLOB,
                        access_count INTEGER DEFAULT 0,
                        last_accessed TEXT,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        content_hash TEXT UNIQUE
                    )
                ''')
                
                await conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_category ON memory_entries(category)
                ''')
                
                await conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_tags ON memory_entries(tags)
                ''')
                
                await conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_importance ON memory_entries(importance DESC)
                ''')
                
                await conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_last_accessed ON memory_entries(last_accessed DESC)
                ''')
                
                await conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Database initialization failed: {e}", exc_info=True)
            raise
    
    def _get_content_hash(self, content: str) -> str:
        """Generate content hash for deduplication"""
        return hashlib.sha256(content.encode()).hexdigest()
    
    async def store_memory_entry(
        self, 
        category: str, 
        content: str, 
        importance: int = 5, 
        tags: str = "",
        embedding: Optional[np.ndarray] = None
    ) -> int:
        """
        Store memory entry with enhanced error handling and validation
        
        Args:
            category: Memory category
            content: Memory content
            importance: Importance score (1-10)
            tags: Comma-separated tags
            embedding: Optional vector embedding
            
        Returns:
            Memory entry ID
            
        Raises:
            ValueError: If validation fails
            DatabaseError: If database operation fails
        """
        try:
            # Validate inputs
            if not category or not content:
                raise ValueError("Category and content are required")
            
            if not (1 <= importance <= 10):
                raise ValueError("Importance must be between 1 and 10")
            
            # Generate content hash
            content_hash = self._get_content_hash(content)
            
            # Prepare embedding data
            embedding_blob = None
            if embedding is not None:
                embedding_blob = embedding.tobytes()
                # Cache embedding
                self.embedding_cache[content_hash] = embedding
            
            # Store in database
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.execute('''
                    INSERT OR REPLACE INTO memory_entries 
                    (category, content, importance, tags, embedding, created_at, updated_at, content_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    category, content, importance, tags, embedding_blob,
                    datetime.now().isoformat(), datetime.now().isoformat(), content_hash
                ))
                
                await conn.commit()
                memory_id = cursor.lastrowid
                
                logger.info(f"Stored memory entry {memory_id} in category '{category}'")
                return memory_id
                
        except aiosqlite.IntegrityError as e:
            logger.warning(f"Duplicate content detected: {e}")
            # Return existing entry ID
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.execute(
                    'SELECT id FROM memory_entries WHERE content_hash = ?',
                    (content_hash,)
                )
                result = await cursor.fetchone()
                return result[0] if result else None
                
        except Exception as e:
            logger.error(f"Failed to store memory entry: {e}", exc_info=True)
            raise
    
    async def search_memory(
        self, 
        query: str, 
        limit: int = 10,
        use_vector_search: bool = True,
        min_similarity: float = 0.7
    ) -> List[SearchResult]:
        """
        Enhanced memory search with vector similarity and intelligent fallback
        
        Args:
            query: Search query
            limit: Maximum results to return
            use_vector_search: Whether to use vector similarity search
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of search results with similarity scores
        """
        start_time = time.time()
        self.stats['total_searches'] += 1
        
        try:
            # Check cache first
            cache_key = f"{query}_{limit}_{use_vector_search}_{min_similarity}"
            if cache_key in self.search_cache:
                self.stats['cache_hits'] += 1
                logger.debug(f"Cache hit for query: {query}")
                return self.search_cache[cache_key]
            
            results = []
            
            if use_vector_search:
                # Try vector similarity search
                vector_results = await self._vector_similarity_search(
                    query, limit, min_similarity
                )
                if vector_results:
                    self.stats['vector_searches'] += 1
                    results = vector_results
                else:
                    logger.info("Vector search failed, falling back to text search")
                    results = await self._text_similarity_search(query, limit)
                    self.stats['text_searches'] += 1
            else:
                # Use text-based search
                results = await self._text_similarity_search(query, limit)
                self.stats['text_searches'] += 1
            
            # Cache results
            if len(self.search_cache) >= self.max_cache_size:
                # Remove oldest entry
                oldest_key = next(iter(self.search_cache))
                del self.search_cache[oldest_key]
            
            self.search_cache[cache_key] = results
            
            # Update performance stats
            search_time = time.time() - start_time
            self.stats['avg_search_time'] = (
                (self.stats['avg_search_time'] * (self.stats['total_searches'] - 1) + search_time) 
                / self.stats['total_searches']
            )
            
            logger.info(f"Search completed in {search_time:.3f}s, found {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {e}", exc_info=True)
            # Fallback to basic search
            return await self._basic_search(query, limit)
    
    async def _vector_similarity_search(
        self, 
        query: str, 
        limit: int, 
        min_similarity: float
    ) -> List[SearchResult]:
        """Perform vector similarity search"""
        try:
            # Get query embedding
            query_embedding = await self._get_query_embedding(query)
            if query_embedding is None:
                logger.warning("Could not generate query embedding")
                return []
            
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.execute('''
                    SELECT id, category, content, importance, tags, embedding, 
                           access_count, last_accessed, created_at, updated_at
                    FROM memory_entries 
                    WHERE embedding IS NOT NULL
                ''')
                
                results = []
                async for row in cursor:
                    memory_id, category, content, importance, tags, embedding_blob, \
                    access_count, last_accessed, created_at, updated_at = row
                    
                    if embedding_blob:
                        # Convert blob to numpy array
                        embedding = np.frombuffer(embedding_blob, dtype=np.float32)
                        
                        # Calculate cosine similarity
                        similarity = self._cosine_similarity(query_embedding, embedding)
                        
                        if similarity >= min_similarity:
                            # Calculate relevance score (combination of similarity and importance)
                            relevance = (similarity * 0.7) + (importance / 10 * 0.3)
                            
                            entry = MemoryEntry(
                                id=memory_id,
                                category=category,
                                content=content,
                                importance=importance,
                                tags=tags,
                                embedding=embedding,
                                access_count=access_count,
                                last_accessed=last_accessed,
                                created_at=created_at,
                                updated_at=updated_at
                            )
                            
                            results.append(SearchResult(
                                entry=entry,
                                similarity_score=similarity,
                                relevance_score=relevance
                            ))
                
                # Sort by relevance and return top results
                results.sort(key=lambda x: x.relevance_score, reverse=True)
                return results[:limit]
                
        except Exception as e:
            logger.error(f"Vector similarity search failed: {e}", exc_info=True)
            return []
    
    async def _text_similarity_search(self, query: str, limit: int) -> List[SearchResult]:
        """Perform text-based similarity search"""
        try:
            query_lower = query.lower()
            query_words = set(query_lower.split())
            
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.execute('''
                    SELECT id, category, content, importance, tags, embedding,
                           access_count, last_accessed, created_at, updated_at
                    FROM memory_entries
                ''')
                
                results = []
                async for row in cursor:
                    memory_id, category, content, importance, tags, embedding_blob, \
                    access_count, last_accessed, created_at, updated_at = row
                    
                    # Calculate text similarity
                    content_lower = content.lower()
                    content_words = set(content_lower.split())
                    
                    # Jaccard similarity
                    intersection = len(query_words & content_words)
                    union = len(query_words | content_words)
                    
                    if union > 0:
                        similarity = intersection / union
                        
                        # Additional relevance factors
                        tag_match = any(tag.strip().lower() in query_lower 
                                       for tag in tags.split(',')) if tags else False
                        category_match = category.lower() in query_lower
                        
                        # Boost similarity for tag/category matches
                        if tag_match:
                            similarity += 0.2
                        if category_match:
                            similarity += 0.1
                        
                        if similarity > 0.1:  # Minimum text similarity threshold
                            relevance = (similarity * 0.6) + (importance / 10 * 0.4)
                            
                            entry = MemoryEntry(
                                id=memory_id,
                                category=category,
                                content=content,
                                importance=importance,
                                tags=tags,
                                embedding=np.frombuffer(embedding_blob, dtype=np.float32) if embedding_blob else None,
                                access_count=access_count,
                                last_accessed=last_accessed,
                                created_at=created_at,
                                updated_at=updated_at
                            )
                            
                            results.append(SearchResult(
                                entry=entry,
                                similarity_score=similarity,
                                relevance_score=relevance
                            ))
                
                # Sort by relevance and return top results
                results.sort(key=lambda x: x.relevance_score, reverse=True)
                return results[:limit]
                
        except Exception as e:
            logger.error(f"Text similarity search failed: {e}", exc_info=True)
            return []
    
    async def _basic_search(self, query: str, limit: int) -> List[SearchResult]:
        """Basic fallback search"""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.execute('''
                    SELECT id, category, content, importance, tags, embedding,
                           access_count, last_accessed, created_at, updated_at
                    FROM memory_entries 
                    WHERE content LIKE ? OR tags LIKE ? OR category LIKE ?
                    ORDER BY importance DESC, last_accessed DESC
                    LIMIT ?
                ''', (f'%{query}%', f'%{query}%', f'%{query}%', limit))
                
                results = []
                async for row in cursor:
                    memory_id, category, content, importance, tags, embedding_blob, \
                    access_count, last_accessed, created_at, updated_at = row
                    
                    entry = MemoryEntry(
                        id=memory_id,
                        category=category,
                        content=content,
                        importance=importance,
                        tags=tags,
                        embedding=np.frombuffer(embedding_blob, dtype=np.float32) if embedding_blob else None,
                        access_count=access_count,
                        last_accessed=last_accessed,
                        created_at=created_at,
                        updated_at=updated_at
                    )
                    
                    results.append(SearchResult(
                        entry=entry,
                        similarity_score=0.5,  # Default similarity for basic search
                        relevance_score=importance / 10
                    ))
                
                return results
                
        except Exception as e:
            logger.error(f"Basic search failed: {e}", exc_info=True)
            return []
    
    async def _get_query_embedding(self, query: str) -> Optional[np.ndarray]:
        """Get embedding for query text"""
        try:
            # Check cache first
            query_hash = self._get_content_hash(query)
            if query_hash in self.embedding_cache:
                return self.embedding_cache[query_hash]
            
            # Generate embedding (this would integrate with your embedding system)
            # For now, return None to trigger fallback
            logger.debug("Query embedding not available, using text search")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get query embedding: {e}")
            return None
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
            
        except Exception as e:
            logger.error(f"Cosine similarity calculation failed: {e}")
            return 0.0
    
    async def get_memory_stats(self) -> Dict[str, Any]:
        """Get comprehensive memory system statistics"""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                # Count memory entries
                cursor = await conn.execute('SELECT COUNT(*) FROM memory_entries')
                memory_count = (await cursor.fetchone())[0]
                
                # Count entries with embeddings
                cursor = await conn.execute('SELECT COUNT(*) FROM memory_entries WHERE embedding IS NOT NULL')
                embedding_count = (await cursor.fetchone())[0]
                
                # Average importance
                cursor = await conn.execute('SELECT AVG(importance) FROM memory_entries')
                avg_importance = (await cursor.fetchone())[0] or 0.0
                
                # Most accessed entries
                cursor = await conn.execute('''
                    SELECT content, access_count 
                    FROM memory_entries 
                    ORDER BY access_count DESC 
                    LIMIT 5
                ''')
                top_accessed = [(row[0][:50] + "...", row[1]) async for row in cursor]
                
                return {
                    'total_entries': memory_count,
                    'entries_with_embeddings': embedding_count,
                    'embedding_coverage': (embedding_count / memory_count * 100) if memory_count > 0 else 0,
                    'average_importance': round(avg_importance, 2),
                    'top_accessed_entries': top_accessed,
                    'cache_size': len(self.embedding_cache),
                    'search_cache_size': len(self.search_cache),
                    'search_stats': self.stats,
                    'cache_hit_rate': (
                        (self.stats['cache_hits'] / self.stats['total_searches'] * 100) 
                        if self.stats['total_searches'] > 0 else 0
                    )
                }
                
        except Exception as e:
            logger.error(f"Failed to get memory stats: {e}", exc_info=True)
            return {}
    
    async def cleanup_old_cache(self, max_age_hours: int = 24) -> None:
        """Clean up old cache entries"""
        try:
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            # Clean search cache
            keys_to_remove = []
            for key in self.search_cache.keys():
                # Simple heuristic: remove if cache is getting too large
                if len(self.search_cache) > self.max_cache_size * 0.8:
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del self.search_cache[key]
            
            logger.info(f"Cleaned up {len(keys_to_remove)} cache entries")
            
        except Exception as e:
            logger.error(f"Cache cleanup failed: {e}", exc_info=True)
    
    async def export_memory_data(self, export_path: str) -> None:
        """Export memory data to JSON file"""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.execute('''
                    SELECT id, category, content, importance, tags, 
                           access_count, last_accessed, created_at, updated_at
                    FROM memory_entries
                    ORDER BY created_at DESC
                ''')
                
                data = []
                async for row in cursor:
                    memory_id, category, content, importance, tags, \
                    access_count, last_accessed, created_at, updated_at = row
                    
                    data.append({
                        'id': memory_id,
                        'category': category,
                        'content': content,
                        'importance': importance,
                        'tags': tags,
                        'access_count': access_count,
                        'last_accessed': last_accessed,
                        'created_at': created_at,
                        'updated_at': updated_at
                    })
                
                # Write to file
                export_file = Path(export_path)
                export_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(export_file, 'w') as f:
                    json.dump({
                        'export_date': datetime.now().isoformat(),
                        'total_entries': len(data),
                        'entries': data
                    }, f, indent=2)
                
                logger.info(f"Exported {len(data)} memory entries to {export_path}")
                
        except Exception as e:
            logger.error(f"Memory export failed: {e}", exc_info=True)
            raise

# Example usage and testing
async def main() -> None:
    """Example usage of the enhanced memory manager"""
    memory_manager = EnhancedMemoryManager()
    
    # Store some test entries
    await memory_manager.store_memory_entry(
        category="code",
        content="Python async programming with asyncio",
        importance=8,
        tags="python,async,programming"
    )
    
    await memory_manager.store_memory_entry(
        category="concept",
        content="Vector similarity search using cosine similarity",
        importance=9,
        tags="vectors,similarity,search,cosine"
    )
    
    # Search for entries
    results = await memory_manager.search_memory("python programming", limit=5)
    
    logging.info(f"Found {len(results)} results:")
    for result in results:
        logging.info(f"- {result.entry.content[:50]}... (similarity: {result.similarity_score:.3f})")
    
    # Get statistics
    stats = await memory_manager.get_memory_stats()
    logging.info(f"\nMemory Stats: {stats}")

if __name__ == "__main__":
    asyncio.run(main()) 