#!/usr/bin/env python3
"""
🔧 Prompt Caching System - Anthropic Cookbook Inspired
Made by @Lucariolucario55 on Telegram

Advanced prompt caching with TTL, compression, and intelligent management
"""

import json
import asyncio
import logging
import hashlib
import gzip
import pickle
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import os
import sqlite3
from pathlib import Path
import threading
import time

logger = logging.getLogger(__name__)

class CacheStrategy(Enum):
    """Cache strategies"""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live
    HYBRID = "hybrid"  # Combination of strategies

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    value: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int
    ttl: Optional[timedelta]
    size_bytes: int
    compressed: bool = False

class PromptCache:
    """Advanced prompt caching system with multiple strategies"""
    
    def __init__(self, 
                 max_size_mb: int = 100,
                 strategy: CacheStrategy = CacheStrategy.HYBRID,
                 default_ttl_hours: int = 24,
                 compression_threshold_kb: int = 1,
                 db_path: str = "data/prompt_cache.db"):
        
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.strategy = strategy
        self.default_ttl = timedelta(hours=default_ttl_hours)
        self.compression_threshold = compression_threshold_kb * 1024
        
        # Cache storage
        self.memory_cache: Dict[str, CacheEntry] = {}
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "compressions": 0,
            "total_size_bytes": 0
        }
        
        # Thread safety
        self.lock = threading.RLock()
        
        # Initialize database
        self._init_database()
        
        # Start cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_worker, daemon=True)
        self.cleanup_thread.start()
    
    def _init_database(self):
        """Initialize SQLite database for persistent cache"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS prompt_cache (
                    key TEXT PRIMARY KEY,
                    value BLOB,
                    created_at TEXT,
                    last_accessed TEXT,
                    access_count INTEGER,
                    ttl_hours INTEGER,
                    size_bytes INTEGER,
                    compressed BOOLEAN
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_last_accessed ON prompt_cache(last_accessed)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_access_count ON prompt_cache(access_count)")
    
    def _generate_key(self, prompt: str, model: str, parameters: Dict[str, Any]) -> str:
        """Generate cache key from prompt and parameters"""
        # Create a deterministic string representation
        key_data = {
            "prompt": prompt,
            "model": model,
            "parameters": sorted(parameters.items())
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    def _compress_data(self, data: Any) -> Tuple[bytes, bool]:
        """Compress data if it exceeds threshold"""
        serialized = pickle.dumps(data)
        
        if len(serialized) > self.compression_threshold:
            compressed = gzip.compress(serialized)
            if len(compressed) < len(serialized):
                self.stats["compressions"] += 1
                return compressed, True
        
        return serialized, False
    
    def _decompress_data(self, data: bytes, compressed: bool) -> Any:
        """Decompress data if it was compressed"""
        if compressed:
            data = gzip.decompress(data)
        return pickle.loads(data)
    
    def _store_in_database(self, entry: CacheEntry):
        """Store cache entry in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO prompt_cache 
                    (key, value, created_at, last_accessed, access_count, ttl_hours, size_bytes, compressed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entry.key,
                    entry.value,
                    entry.created_at.isoformat(),
                    entry.last_accessed.isoformat(),
                    entry.access_count,
                    entry.ttl.total_seconds() / 3600 if entry.ttl else None,
                    entry.size_bytes,
                    entry.compressed
                ))
        except Exception as e:
            logger.error(f"Failed to store in database: {e}")
    
    def _load_from_database(self, key: str) -> Optional[CacheEntry]:
        """Load cache entry from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT value, created_at, last_accessed, access_count, ttl_hours, size_bytes, compressed
                    FROM prompt_cache WHERE key = ?
                """, (key,))
                
                row = cursor.fetchone()
                if row:
                    value, created_at, last_accessed, access_count, ttl_hours, size_bytes, compressed = row
                    
                    # Decompress if needed
                    value = self._decompress_data(value, compressed)
                    
                    return CacheEntry(
                        key=key,
                        value=value,
                        created_at=datetime.fromisoformat(created_at),
                        last_accessed=datetime.fromisoformat(last_accessed),
                        access_count=access_count,
                        ttl=timedelta(hours=ttl_hours) if ttl_hours else None,
                        size_bytes=size_bytes,
                        compressed=compressed
                    )
        except Exception as e:
            logger.error(f"Failed to load from database: {e}")
        
        return None
    
    def _update_database_access(self, key: str):
        """Update access statistics in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE prompt_cache 
                    SET last_accessed = ?, access_count = access_count + 1
                    WHERE key = ?
                """, (datetime.now().isoformat(), key))
        except Exception as e:
            logger.error(f"Failed to update database access: {e}")
    
    def _evict_entries(self, target_size_bytes: int):
        """Evict entries based on strategy"""
        with self.lock:
            current_size = self.stats["total_size_bytes"]
            
            if current_size <= target_size_bytes:
                return
            
            # Sort entries by strategy
            if self.strategy == CacheStrategy.LRU:
                sorted_entries = sorted(
                    self.memory_cache.items(),
                    key=lambda x: x[1].last_accessed
                )
            elif self.strategy == CacheStrategy.LFU:
                sorted_entries = sorted(
                    self.memory_cache.items(),
                    key=lambda x: x[1].access_count
                )
            elif self.strategy == CacheStrategy.TTL:
                sorted_entries = sorted(
                    self.memory_cache.items(),
                    key=lambda x: x[1].created_at
                )
            else:  # HYBRID
                sorted_entries = sorted(
                    self.memory_cache.items(),
                    key=lambda x: (x[1].access_count, x[1].last_accessed)
                )
            
            # Evict entries until we're under target size
            for key, entry in sorted_entries:
                if self.stats["total_size_bytes"] <= target_size_bytes:
                    break
                
                del self.memory_cache[key]
                self.stats["total_size_bytes"] -= entry.size_bytes
                self.stats["evictions"] += 1
                
                # Remove from database
                try:
                    with sqlite3.connect(self.db_path) as conn:
                        conn.execute("DELETE FROM prompt_cache WHERE key = ?", (key,))
                except Exception as e:
                    logger.error(f"Failed to remove from database: {e}")
    
    def _cleanup_worker(self):
        """Background cleanup worker"""
        while True:
            try:
                time.sleep(300)  # Run every 5 minutes
                self._cleanup_expired()
            except Exception as e:
                logger.error(f"Cleanup worker error: {e}")
    
    def _cleanup_expired(self):
        """Remove expired entries"""
        now = datetime.now()
        expired_keys = []
        
        with self.lock:
            for key, entry in self.memory_cache.items():
                if entry.ttl and (now - entry.created_at) > entry.ttl:
                    expired_keys.append(key)
            
            for key in expired_keys:
                entry = self.memory_cache[key]
                del self.memory_cache[key]
                self.stats["total_size_bytes"] -= entry.size_bytes
                
                # Remove from database
                try:
                    with sqlite3.connect(self.db_path) as conn:
                        conn.execute("DELETE FROM prompt_cache WHERE key = ?", (key,))
                except Exception as e:
                    logger.error(f"Failed to remove expired entry from database: {e}")
    
    def get(self, prompt: str, model: str, parameters: Dict[str, Any]) -> Optional[Any]:
        """Get cached response for prompt"""
        key = self._generate_key(prompt, model, parameters)
        
        with self.lock:
            # Check memory cache first
            if key in self.memory_cache:
                entry = self.memory_cache[key]
                
                # Check if expired
                if entry.ttl and (datetime.now() - entry.created_at) > entry.ttl:
                    del self.memory_cache[key]
                    self.stats["total_size_bytes"] -= entry.size_bytes
                    self.stats["misses"] += 1
                    return None
                
                # Update access statistics
                entry.last_accessed = datetime.now()
                entry.access_count += 1
                self._update_database_access(key)
                
                self.stats["hits"] += 1
                return entry.value
            
            # Check database
            entry = self._load_from_database(key)
            if entry:
                # Check if expired
                if entry.ttl and (datetime.now() - entry.created_at) > entry.ttl:
                    try:
                        with sqlite3.connect(self.db_path) as conn:
                            conn.execute("DELETE FROM prompt_cache WHERE key = ?", (key,))
                    except Exception as e:
                        logger.error(f"Failed to remove expired entry: {e}")
                    self.stats["misses"] += 1
                    return None
                
                # Move to memory cache
                self.memory_cache[key] = entry
                self.stats["total_size_bytes"] += entry.size_bytes
                
                # Update access statistics
                entry.last_accessed = datetime.now()
                entry.access_count += 1
                self._update_database_access(key)
                
                self.stats["hits"] += 1
                return entry.value
        
        self.stats["misses"] += 1
        return None
    
    def set(self, prompt: str, model: str, parameters: Dict[str, Any], 
            response: Any, ttl: Optional[timedelta] = None) -> None:
        """Cache response for prompt"""
        key = self._generate_key(prompt, model, parameters)
        
        # Compress if needed
        compressed_data, is_compressed = self._compress_data(response)
        size_bytes = len(compressed_data)
        
        entry = CacheEntry(
            key=key,
            value=compressed_data,
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            access_count=1,
            ttl=ttl or self.default_ttl,
            size_bytes=size_bytes,
            compressed=is_compressed
        )
        
        with self.lock:
            # Check if we need to evict entries
            if self.stats["total_size_bytes"] + size_bytes > self.max_size_bytes:
                target_size = self.max_size_bytes * 0.8  # Leave 20% buffer
                self._evict_entries(target_size)
            
            # Store in memory cache
            self.memory_cache[key] = entry
            self.stats["total_size_bytes"] += size_bytes
            
            # Store in database
            self._store_in_database(entry)
    
    def clear(self):
        """Clear all cache entries"""
        with self.lock:
            self.memory_cache.clear()
            self.stats["total_size_bytes"] = 0
            
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("DELETE FROM prompt_cache")
            except Exception as e:
                logger.error(f"Failed to clear database: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            hit_rate = (self.stats["hits"] / (self.stats["hits"] + self.stats["misses"])) if (self.stats["hits"] + self.stats["misses"]) > 0 else 0
            
            return {
                **self.stats,
                "hit_rate": hit_rate,
                "memory_entries": len(self.memory_cache),
                "max_size_mb": self.max_size_bytes / (1024 * 1024),
                "current_size_mb": self.stats["total_size_bytes"] / (1024 * 1024),
                "utilization_percent": (self.stats["total_size_bytes"] / self.max_size_bytes) * 100
            }
    
    def get_database_statistics(self) -> Dict[str, Any]:
        """Get database cache statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM prompt_cache")
                total_entries = cursor.fetchone()[0]
                
                cursor = conn.execute("SELECT SUM(size_bytes) FROM prompt_cache")
                total_size = cursor.fetchone()[0] or 0
                
                cursor = conn.execute("SELECT AVG(access_count) FROM prompt_cache")
                avg_access = cursor.fetchone()[0] or 0
                
                return {
                    "database_entries": total_entries,
                    "database_size_mb": total_size / (1024 * 1024),
                    "average_access_count": avg_access
                }
        except Exception as e:
            logger.error(f"Failed to get database statistics: {e}")
            return {}

# Enhanced LLM Integration with Caching
class CachedLLMClient:
    """LLM client with integrated prompt caching"""
    
    def __init__(self, llm_client, cache_config: Dict[str, Any] = None):
        self.llm_client = llm_client
        self.cache = PromptCache(**(cache_config or {}))
    
    async def generate_response(self, prompt: str, model: str = "deepseek-chat", 
                              parameters: Dict[str, Any] = None, 
                              use_cache: bool = True) -> str:
        """Generate response with caching"""
        parameters = parameters or {}
        
        if use_cache:
            # Try to get from cache
            cached_response = self.cache.get(prompt, model, parameters)
            if cached_response is not None:
                logger.info("Using cached response")
                return cached_response
        
        # Generate new response
        response = await self.llm_client.generate_response(prompt, model, parameters)
        
        if use_cache:
            # Cache the response
            self.cache.set(prompt, model, parameters, response)
        
        return response
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "memory_cache": self.cache.get_statistics(),
            "database_cache": self.cache.get_database_statistics()
        }
    
    def clear_cache(self):
        """Clear all cached responses"""
        self.cache.clear()

# Example usage
async def test_prompt_caching():
    """Test the prompt caching system"""
    
    # Mock LLM client
    class MockLLMClient:
        async def generate_response(self, prompt: str, model: str = "deepseek-chat", parameters: Dict[str, Any] = None) -> str:
            await asyncio.sleep(0.1)  # Simulate API call
            return f"Response to: {prompt[:50]}..."
    
    # Create cached client
    cache_config = {
        "max_size_mb": 10,
        "strategy": CacheStrategy.HYBRID,
        "default_ttl_hours": 1
    }
    
    client = CachedLLMClient(MockLLMClient(), cache_config)
    
    # Test caching
    prompt = "What is the capital of France?"
    parameters = {"temperature": 0.7}
    
    # First call (cache miss)
    start_time = time.time()
    response1 = await client.generate_response(prompt, "deepseek-chat", parameters)
    time1 = time.time() - start_time
    
    # Second call (cache hit)
    start_time = time.time()
    response2 = await client.generate_response(prompt, "deepseek-chat", parameters)
    time2 = time.time() - start_time
    
    print(f"First call (cache miss): {time1:.3f}s")
    print(f"Second call (cache hit): {time2:.3f}s")
    print(f"Speedup: {time1/time2:.1f}x")
    
    # Get statistics
    stats = client.get_cache_stats()
    print(f"Cache statistics: {stats}")

if __name__ == "__main__":
    asyncio.run(test_prompt_caching()) 