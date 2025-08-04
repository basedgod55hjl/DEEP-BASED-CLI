#!/usr/bin/env python3
"""
JSON Memory Tool - Enhanced BASED GOD CLI
Structured memory storage with JSON format and advanced querying
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
import uuid
from collections import defaultdict

from .base_tool import BaseTool, ToolResponse, ToolStatus

@dataclass
class MemoryEntry:
    """Memory entry with structured data"""
    id: str
    content: str
    category: str
    tags: List[str]
    metadata: Dict[str, Any]
    timestamp: datetime
    embedding: Optional[List[float]] = None
    importance: float = 1.0
    access_count: int = 0
    last_accessed: Optional[datetime] = None

class JSONMemoryTool(BaseTool):
    """
    Advanced JSON-based memory system with structured storage
    """
    
    def __init__(self, 
                 memory_file: str = "data/json_memory.json",
                 max_entries: int = 10000,
                 auto_backup: bool = True,
                 backup_interval: int = 100):
        super().__init__(
            name="JSON Memory Tool",
            description="Structured memory storage with JSON format and advanced querying capabilities",
            capabilities=[
                "structured_memory_storage",
                "json_based_queries",
                "semantic_search",
                "memory_analytics",
                "automatic_backup",
                "memory_compression",
                "tag_based_filtering",
                "importance_scoring"
            ]
        )
        
        self.memory_file = Path(memory_file)
        self.max_entries = max_entries
        self.auto_backup = auto_backup
        self.backup_interval = backup_interval
        self.logger = logging.getLogger(__name__)
        
        # Ensure directory exists
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load memory
        self.memory_data = self._load_memory()
        self.entry_count = 0
        
    def _load_memory(self) -> Dict[str, Any]:
        """Load memory from JSON file"""
        try:
            if self.memory_file.exists():
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.logger.info(f"Loaded {len(data.get('entries', {}))} memory entries")
                    return data
            else:
                # Initialize new memory structure
                initial_data = {
                    "metadata": {
                        "created": datetime.now().isoformat(),
                        "version": "1.0",
                        "total_entries": 0,
                        "categories": [],
                        "tags": []
                    },
                    "entries": {},
                    "indexes": {
                        "by_category": {},
                        "by_tag": {},
                        "by_timestamp": {},
                        "by_importance": {}
                    }
                }
                self._save_memory(initial_data)
                return initial_data
                
        except Exception as e:
            self.logger.error(f"Failed to load memory: {e}")
            return {
                "metadata": {"created": datetime.now().isoformat(), "version": "1.0", "total_entries": 0},
                "entries": {},
                "indexes": {"by_category": {}, "by_tag": {}, "by_timestamp": {}, "by_importance": {}}
            }
    
    def _save_memory(self, data: Optional[Dict[str, Any]] = None) -> bool:
        """Save memory to JSON file"""
        try:
            if data is None:
                data = self.memory_data
            
            # Create backup if needed
            if self.auto_backup and self.entry_count % self.backup_interval == 0:
                self._create_backup()
            
            # Save to file
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save memory: {e}")
            return False
    
    def _create_backup(self) -> None:
        """Create backup of memory file"""
        try:
            backup_file = self.memory_file.with_suffix(f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
            with open(self.memory_file, 'r', encoding='utf-8') as src:
                with open(backup_file, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
            self.logger.info(f"Memory backup created: {backup_file}")
        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
    
    def _generate_entry_id(self) -> str:
        """Generate unique entry ID"""
        return str(uuid.uuid4())
    
    def _update_indexes(self, entry: MemoryEntry, operation: str = "add") -> None:
        """Update memory indexes"""
        indexes = self.memory_data["indexes"]
        
        if operation == "add":
            # Update category index
            if entry.category not in indexes["by_category"]:
                indexes["by_category"][entry.category] = []
            indexes["by_category"][entry.category].append(entry.id)
            
            # Update tag index
            for tag in entry.tags:
                if tag not in indexes["by_tag"]:
                    indexes["by_tag"][tag] = []
                indexes["by_tag"][tag].append(entry.id)
            
            # Update timestamp index (by day)
            day_key = entry.timestamp.strftime("%Y-%m-%d")
            if day_key not in indexes["by_timestamp"]:
                indexes["by_timestamp"][day_key] = []
            indexes["by_timestamp"][day_key].append(entry.id)
            
            # Update importance index
            importance_key = f"{entry.importance:.1f}"
            if importance_key not in indexes["by_importance"]:
                indexes["by_importance"][importance_key] = []
            indexes["by_importance"][importance_key].append(entry.id)
            
        elif operation == "remove":
            # Remove from all indexes
            for index_name, index_data in indexes.items():
                for key, entry_ids in index_data.items():
                    if entry.id in entry_ids:
                        entry_ids.remove(entry.id)
                        if not entry_ids:
                            del index_data[key]
    
    async def execute(self, **kwargs) -> ToolResponse:
        """Execute JSON memory operation"""
        
        operation = kwargs.get("operation", "store").lower()
        
        try:
            if operation == "store":
                return await self._store_memory(kwargs)
            elif operation == "retrieve":
                return await self._retrieve_memory(kwargs)
            elif operation == "search":
                return await self._search_memory(kwargs)
            elif operation == "query":
                return await self._query_memory(kwargs)
            elif operation == "delete":
                return await self._delete_memory(kwargs)
            elif operation == "update":
                return await self._update_memory(kwargs)
            elif operation == "analytics":
                return await self._get_analytics(kwargs)
            elif operation == "export":
                return await self._export_memory(kwargs)
            elif operation == "backup":
                return await self._create_backup_operation(kwargs)
            else:
                return ToolResponse(
                    success=False,
                    message=f"Unsupported operation: {operation}",
                    status=ToolStatus.FAILED
                )
                
        except Exception as e:
            return ToolResponse(
                success=False,
                message=f"JSON memory operation failed: {str(e)}",
                status=ToolStatus.FAILED
            )
    
    async def _store_memory(self, kwargs: Dict[str, Any]) -> ToolResponse:
        """Store memory entry"""
        content = kwargs.get("content", "")
        category = kwargs.get("category", "general")
        tags = kwargs.get("tags", [])
        metadata = kwargs.get("metadata", {})
        importance = kwargs.get("importance", 1.0)
        embedding = kwargs.get("embedding")
        
        if not content:
            return ToolResponse(
                success=False,
                message="Content is required for memory storage",
                status=ToolStatus.FAILED
            )
        
        # Check if we're at capacity
        if len(self.memory_data["entries"]) >= self.max_entries:
            # Remove least important entry
            self._remove_least_important_entry()
        
        # Create memory entry
        entry = MemoryEntry(
            id=self._generate_entry_id(),
            content=content,
            category=category,
            tags=tags,
            metadata=metadata,
            timestamp=datetime.now(),
            embedding=embedding,
            importance=importance
        )
        
        # Store entry
        self.memory_data["entries"][entry.id] = asdict(entry)
        
        # Update indexes
        self._update_indexes(entry, "add")
        
        # Update metadata
        self.memory_data["metadata"]["total_entries"] = len(self.memory_data["entries"])
        if category not in self.memory_data["metadata"]["categories"]:
            self.memory_data["metadata"]["categories"].append(category)
        
        for tag in tags:
            if tag not in self.memory_data["metadata"]["tags"]:
                self.memory_data["metadata"]["tags"].append(tag)
        
        # Save to file
        if self._save_memory():
            self.entry_count += 1
            return ToolResponse(
                success=True,
                message=f"Memory stored successfully. ID: {entry.id}",
                data={
                    "entry_id": entry.id,
                    "content": content,
                    "category": category,
                    "tags": tags,
                    "timestamp": entry.timestamp.isoformat(),
                    "importance": importance
                },
                status=ToolStatus.SUCCESS
            )
        else:
            return ToolResponse(
                success=False,
                message="Failed to save memory to file",
                status=ToolStatus.FAILED
            )
    
    async def _retrieve_memory(self, kwargs: Dict[str, Any]) -> ToolResponse:
        """Retrieve memory entry by ID"""
        entry_id = kwargs.get("entry_id", "")
        
        if not entry_id:
            return ToolResponse(
                success=False,
                message="Entry ID is required for retrieval",
                status=ToolStatus.FAILED
            )
        
        entry_data = self.memory_data["entries"].get(entry_id)
        
        if not entry_data:
            return ToolResponse(
                success=False,
                message=f"Memory entry not found: {entry_id}",
                status=ToolStatus.FAILED
            )
        
        # Update access count
        entry_data["access_count"] += 1
        entry_data["last_accessed"] = datetime.now().isoformat()
        
        # Save changes
        self._save_memory()
        
        return ToolResponse(
            success=True,
            message="Memory retrieved successfully",
            data=entry_data,
            status=ToolStatus.SUCCESS
        )
    
    async def _search_memory(self, kwargs: Dict[str, Any]) -> ToolResponse:
        """Search memory using various criteria"""
        query = kwargs.get("query", "")
        category = kwargs.get("category")
        tags = kwargs.get("tags", [])
        limit = kwargs.get("limit", 10)
        min_importance = kwargs.get("min_importance", 0.0)
        
        results = []
        
        for entry_id, entry_data in self.memory_data["entries"].items():
            # Apply filters
            if category and entry_data["category"] != category:
                continue
            
            if tags and not any(tag in entry_data["tags"] for tag in tags):
                continue
            
            if entry_data["importance"] < min_importance:
                continue
            
            # Text search
            if query and query.lower() not in entry_data["content"].lower():
                continue
            
            results.append({
                "id": entry_id,
                **entry_data
            })
        
        # Sort by importance and access count
        results.sort(key=lambda x: (x["importance"], x["access_count"]), reverse=True)
        
        # Apply limit
        results = results[:limit]
        
        return ToolResponse(
            success=True,
            message=f"Found {len(results)} memory entries",
            data={
                "results": results,
                "total_found": len(results),
                "query": query,
                "filters": {
                    "category": category,
                    "tags": tags,
                    "min_importance": min_importance
                }
            },
            status=ToolStatus.SUCCESS
        )
    
    async def _query_memory(self, kwargs: Dict[str, Any]) -> ToolResponse:
        """Advanced query using JSON query language"""
        query_type = kwargs.get("query_type", "simple")
        
        if query_type == "by_category":
            category = kwargs.get("category", "")
            if not category:
                return ToolResponse(
                    success=False,
                    message="Category is required for category query",
                    status=ToolStatus.FAILED
                )
            
            entry_ids = self.memory_data["indexes"]["by_category"].get(category, [])
            results = [self.memory_data["entries"][entry_id] for entry_id in entry_ids if entry_id in self.memory_data["entries"]]
            
        elif query_type == "by_tag":
            tag = kwargs.get("tag", "")
            if not tag:
                return ToolResponse(
                    success=False,
                    message="Tag is required for tag query",
                    status=ToolStatus.FAILED
                )
            
            entry_ids = self.memory_data["indexes"]["by_tag"].get(tag, [])
            results = [self.memory_data["entries"][entry_id] for entry_id in entry_ids if entry_id in self.memory_data["entries"]]
            
        elif query_type == "by_date_range":
            start_date = kwargs.get("start_date")
            end_date = kwargs.get("end_date")
            
            if not start_date or not end_date:
                return ToolResponse(
                    success=False,
                    message="Start date and end date are required for date range query",
                    status=ToolStatus.FAILED
                )
            
            results = []
            for entry_data in self.memory_data["entries"].values():
                entry_date = datetime.fromisoformat(entry_data["timestamp"])
                if start_date <= entry_date <= end_date:
                    results.append(entry_data)
            
        elif query_type == "by_importance":
            min_importance = kwargs.get("min_importance", 0.0)
            max_importance = kwargs.get("max_importance", 10.0)
            
            results = []
            for entry_data in self.memory_data["entries"].values():
                if min_importance <= entry_data["importance"] <= max_importance:
                    results.append(entry_data)
            
        else:
            return ToolResponse(
                success=False,
                message=f"Unsupported query type: {query_type}",
                status=ToolStatus.FAILED
            )
        
        return ToolResponse(
            success=True,
            message=f"Query completed. Found {len(results)} entries",
            data={
                "results": results,
                "query_type": query_type,
                "total_found": len(results)
            },
            status=ToolStatus.SUCCESS
        )
    
    async def _delete_memory(self, kwargs: Dict[str, Any]) -> ToolResponse:
        """Delete memory entry"""
        entry_id = kwargs.get("entry_id", "")
        
        if not entry_id:
            return ToolResponse(
                success=False,
                message="Entry ID is required for deletion",
                status=ToolStatus.FAILED
            )
        
        if entry_id not in self.memory_data["entries"]:
            return ToolResponse(
                success=False,
                message=f"Memory entry not found: {entry_id}",
                status=ToolStatus.FAILED
            )
        
        # Get entry for index updates
        entry_data = self.memory_data["entries"][entry_id]
        entry = MemoryEntry(**entry_data)
        
        # Remove from indexes
        self._update_indexes(entry, "remove")
        
        # Remove entry
        del self.memory_data["entries"][entry_id]
        
        # Update metadata
        self.memory_data["metadata"]["total_entries"] = len(self.memory_data["entries"])
        
        # Save changes
        if self._save_memory():
            return ToolResponse(
                success=True,
                message=f"Memory entry deleted: {entry_id}",
                data={"deleted_entry_id": entry_id},
                status=ToolStatus.SUCCESS
            )
        else:
            return ToolResponse(
                success=False,
                message="Failed to save changes after deletion",
                status=ToolStatus.FAILED
            )
    
    async def _update_memory(self, kwargs: Dict[str, Any]) -> ToolResponse:
        """Update memory entry"""
        entry_id = kwargs.get("entry_id", "")
        
        if not entry_id:
            return ToolResponse(
                success=False,
                message="Entry ID is required for update",
                status=ToolStatus.FAILED
            )
        
        if entry_id not in self.memory_data["entries"]:
            return ToolResponse(
                success=False,
                message=f"Memory entry not found: {entry_id}",
                status=ToolStatus.FAILED
            )
        
        # Get current entry
        entry_data = self.memory_data["entries"][entry_id]
        entry = MemoryEntry(**entry_data)
        
        # Remove from indexes
        self._update_indexes(entry, "remove")
        
        # Update fields
        updateable_fields = ["content", "category", "tags", "metadata", "importance", "embedding"]
        for field in updateable_fields:
            if field in kwargs:
                setattr(entry, field, kwargs[field])
        
        # Update timestamp
        entry.timestamp = datetime.now()
        
        # Store updated entry
        self.memory_data["entries"][entry_id] = asdict(entry)
        
        # Update indexes
        self._update_indexes(entry, "add")
        
        # Save changes
        if self._save_memory():
            return ToolResponse(
                success=True,
                message=f"Memory entry updated: {entry_id}",
                data=asdict(entry),
                status=ToolStatus.SUCCESS
            )
        else:
            return ToolResponse(
                success=False,
                message="Failed to save changes after update",
                status=ToolStatus.FAILED
            )
    
    async def _get_analytics(self, kwargs: Dict[str, Any]) -> ToolResponse:
        """Get memory analytics"""
        analytics = {
            "total_entries": len(self.memory_data["entries"]),
            "categories": {},
            "tags": {},
            "importance_distribution": {},
            "access_patterns": {},
            "recent_activity": {}
        }
        
        # Category distribution
        for entry_data in self.memory_data["entries"].values():
            category = entry_data["category"]
            analytics["categories"][category] = analytics["categories"].get(category, 0) + 1
        
        # Tag distribution
        for entry_data in self.memory_data["entries"].values():
            for tag in entry_data["tags"]:
                analytics["tags"][tag] = analytics["tags"].get(tag, 0) + 1
        
        # Importance distribution
        for entry_data in self.memory_data["entries"].values():
            importance = entry_data["importance"]
            importance_key = f"{importance:.1f}"
            analytics["importance_distribution"][importance_key] = analytics["importance_distribution"].get(importance_key, 0) + 1
        
        # Access patterns
        total_access = sum(entry_data["access_count"] for entry_data in self.memory_data["entries"].values())
        analytics["access_patterns"]["total_accesses"] = total_access
        analytics["access_patterns"]["average_access_per_entry"] = total_access / len(self.memory_data["entries"]) if self.memory_data["entries"] else 0
        
        # Recent activity (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_entries = [
            entry_data for entry_data in self.memory_data["entries"].values()
            if datetime.fromisoformat(entry_data["timestamp"]) >= week_ago
        ]
        analytics["recent_activity"]["entries_last_7_days"] = len(recent_entries)
        
        return ToolResponse(
            success=True,
            message="Memory analytics generated",
            data=analytics,
            status=ToolStatus.SUCCESS
        )
    
    async def _export_memory(self, kwargs: Dict[str, Any]) -> ToolResponse:
        """Export memory to different formats"""
        export_format = kwargs.get("format", "json")
        filters = kwargs.get("filters", {})
        
        # Apply filters
        entries_to_export = []
        for entry_data in self.memory_data["entries"].values():
            include = True
            
            if "category" in filters and entry_data["category"] != filters["category"]:
                include = False
            
            if "tags" in filters and not any(tag in entry_data["tags"] for tag in filters["tags"]):
                include = False
            
            if "min_importance" in filters and entry_data["importance"] < filters["min_importance"]:
                include = False
            
            if include:
                entries_to_export.append(entry_data)
        
        if export_format == "json":
            export_data = {
                "metadata": self.memory_data["metadata"],
                "entries": entries_to_export,
                "export_timestamp": datetime.now().isoformat(),
                "total_exported": len(entries_to_export)
            }
            
        elif export_format == "csv":
            # Convert to CSV format
            csv_data = []
            for entry in entries_to_export:
                csv_data.append({
                    "id": entry["id"],
                    "content": entry["content"],
                    "category": entry["category"],
                    "tags": ",".join(entry["tags"]),
                    "importance": entry["importance"],
                    "access_count": entry["access_count"],
                    "timestamp": entry["timestamp"]
                })
            export_data = csv_data
            
        else:
            return ToolResponse(
                success=False,
                message=f"Unsupported export format: {export_format}",
                status=ToolStatus.FAILED
            )
        
        return ToolResponse(
            success=True,
            message=f"Memory exported in {export_format} format",
            data={
                "export_data": export_data,
                "format": export_format,
                "total_exported": len(entries_to_export)
            },
            status=ToolStatus.SUCCESS
        )
    
    async def _create_backup_operation(self, kwargs: Dict[str, Any]) -> ToolResponse:
        """Create manual backup"""
        try:
            self._create_backup()
            return ToolResponse(
                success=True,
                message="Manual backup created successfully",
                data={"backup_created": True},
                status=ToolStatus.SUCCESS
            )
        except Exception as e:
            return ToolResponse(
                success=False,
                message=f"Failed to create backup: {str(e)}",
                status=ToolStatus.FAILED
            )
    
    def _remove_least_important_entry(self) -> None:
        """Remove the least important entry when at capacity"""
        if not self.memory_data["entries"]:
            return
        
        # Find least important entry
        least_important_id = min(
            self.memory_data["entries"].keys(),
            key=lambda x: self.memory_data["entries"][x]["importance"]
        )
        
        # Remove it
        entry_data = self.memory_data["entries"][least_important_id]
        entry = MemoryEntry(**entry_data)
        self._update_indexes(entry, "remove")
        del self.memory_data["entries"][least_important_id]
        
        self.logger.info(f"Removed least important entry: {least_important_id}")
    
    def get_schema(self) -> Dict[str, Any]:
        """Get parameter schema for JSON memory tool"""
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["store", "retrieve", "search", "query", "delete", "update", "analytics", "export", "backup"],
                    "description": "JSON memory operation to perform",
                    "default": "store"
                },
                "content": {
                    "type": "string",
                    "description": "Content to store in memory"
                },
                "category": {
                    "type": "string",
                    "description": "Category of memory entry"
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Tags for memory entry"
                },
                "metadata": {
                    "type": "object",
                    "description": "Additional metadata for memory entry"
                },
                "importance": {
                    "type": "number",
                    "description": "Importance score (0.0 to 10.0)",
                    "minimum": 0.0,
                    "maximum": 10.0
                },
                "embedding": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "Vector embedding for semantic search"
                },
                "entry_id": {
                    "type": "string",
                    "description": "Memory entry ID for retrieve/delete/update operations"
                },
                "query": {
                    "type": "string",
                    "description": "Search query"
                },
                "query_type": {
                    "type": "string",
                    "enum": ["by_category", "by_tag", "by_date_range", "by_importance"],
                    "description": "Type of query to perform"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return",
                    "default": 10
                },
                "format": {
                    "type": "string",
                    "enum": ["json", "csv"],
                    "description": "Export format",
                    "default": "json"
                }
            },
            "required": ["operation"]
        }
    
    # Convenience methods
    async def store(self, content: str, category: str = "general", tags: List[str] = None, metadata: Dict[str, Any] = None, importance: float = 1.0, embedding: List[float] = None) -> ToolResponse:
        """Store a memory entry"""
        return await self.execute(
            operation="store",
            content=content,
            category=category,
            tags=tags or [],
            metadata=metadata or {},
            importance=importance,
            embedding=embedding
        )
    
    async def retrieve(self, entry_id: str) -> ToolResponse:
        """Retrieve a memory entry by ID"""
        return await self.execute(operation="retrieve", entry_id=entry_id)
    
    async def search(self, query: str = "", category: str = None, tags: List[str] = None, limit: int = 10) -> ToolResponse:
        """Search memory entries"""
        return await self.execute(
            operation="search",
            query=query,
            category=category,
            tags=tags or [],
            limit=limit
        )
    
    async def get_analytics(self) -> ToolResponse:
        """Get memory analytics"""
        return await self.execute(operation="analytics")
    
    async def export(self, format: str = "json", filters: Dict[str, Any] = None) -> ToolResponse:
        """Export memory"""
        return await self.execute(operation="export", format=format, filters=filters or {}) 