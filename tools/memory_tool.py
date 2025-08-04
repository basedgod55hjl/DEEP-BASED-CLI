"""
Memory Tool - Enhanced BASED GOD CLI
Persistent memory and learning system inspired by Agent Zero
"""

import json
import logging

import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import asdict

from .base_tool import BaseTool, ToolResponse, ToolStatus

class MemoryTool(BaseTool):
    """
    Advanced memory and learning system
    """
    
    def __init__(self, memory_file: str = "based_god_memory.json"):
    """__init__ function."""
        super().__init__(
            name="Memory Tool",
            description="Persistent memory and learning system for storing conversations, patterns, and insights",
            capabilities=[
                "Conversation history storage and retrieval",
                "Pattern learning and recognition",
                "Knowledge base management",
                "Experience-based recommendations",
                "Memory search and filtering",
                "Automated insight generation"
            ]
        )
        self.memory_file = memory_file
        self.memory_data = self._load_memory()
    
    async def execute(self, **kwargs) -> ToolResponse:
        """Execute memory operation"""
        
        operation = kwargs.get("operation", "store").lower()
        
        try:
            if operation == "store":
                return await self._store_memory(kwargs)
            elif operation == "retrieve":
                return await self._retrieve_memory(kwargs)
            elif operation == "search":
                return await self._search_memory(kwargs)
            elif operation == "analyze":
                return await self._analyze_patterns(kwargs)
            elif operation == "export":
                return await self._export_memory(kwargs)
            elif operation == "stats":
                return await self._get_memory_stats()
            else:
                return ToolResponse(
                    success=False,
                    message=f"Unsupported operation: {operation}",
                    status=ToolStatus.FAILED
                )
                
        except Exception as e:
            return ToolResponse(
                success=False,
                message=f"Memory operation failed: {str(e)}",
                status=ToolStatus.FAILED
            )
    
    def get_schema(self) -> Dict[str, Any]:
        """Get parameter schema for memory tool"""
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["store", "retrieve", "search", "analyze", "export", "stats"],
                    "description": "Memory operation to perform",
                    "default": "store"
                },
                "content": {
                    "type": "string",
                    "description": "Content to store in memory"
                },
                "category": {
                    "type": "string",
                    "enum": ["conversation", "pattern", "insight", "tool_usage", "error", "success"],
                    "description": "Category of memory entry",
                    "default": "conversation"
                },
                "metadata": {
                    "type": "object",
                    "description": "Additional metadata for memory entry"
                },
                "query": {
                    "type": "string",
                    "description": "Search query for retrieve/search operations"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return",
                    "default": 10,
                    "minimum": 1,
                    "maximum": 100
                },
                "time_range": {
                    "type": "string",
                    "enum": ["hour", "day", "week", "month", "all"],
                    "description": "Time range for search",
                    "default": "all"
                }
            }
        }
    
    async def _store_memory(self, kwargs: Dict[str, Any]) -> ToolResponse:
        """Store a memory entry"""
        
        content = kwargs.get("content")
        category = kwargs.get("category", "conversation")
        metadata = kwargs.get("metadata", {})
        
        if not content:
            return ToolResponse(
                success=False,
                message="Content is required for storing memory",
                status=ToolStatus.FAILED
            )
        
        # Create memory entry
        memory_entry = {
            "id": self._generate_memory_id(),
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "content": content,
            "metadata": metadata,
            "access_count": 0,
            "last_accessed": None
        }
        
        # Store in appropriate category
        if category not in self.memory_data:
            self.memory_data[category] = []
        
        self.memory_data[category].append(memory_entry)
        
        # Update global stats
        self.memory_data["stats"]["total_entries"] += 1
        self.memory_data["stats"]["entries_by_category"][category] = \
            self.memory_data["stats"]["entries_by_category"].get(category, 0) + 1
        
        # Save to file
        self._save_memory()
        
        return ToolResponse(
            success=True,
            message=f"Successfully stored memory entry in category: {category}",
            data={
                "memory_id": memory_entry["id"],
                "category": category,
                "timestamp": memory_entry["timestamp"],
                "content_length": len(content)
            }
        )
    
    async def _retrieve_memory(self, kwargs: Dict[str, Any]) -> ToolResponse:
        """Retrieve memory entries"""
        
        category = kwargs.get("category")
        limit = kwargs.get("limit", 10)
        time_range = kwargs.get("time_range", "all")
        
        # Get entries from category or all categories
        if category:
            entries = self.memory_data.get(category, [])
        else:
            entries = []
            for cat in self.memory_data:
                if cat != "stats":
                    entries.extend(self.memory_data[cat])
        
        # Filter by time range
        filtered_entries = self._filter_by_time_range(entries, time_range)
        
        # Sort by timestamp (newest first) and limit
        sorted_entries = sorted(filtered_entries, key=lambda x: x["timestamp"], reverse=True)
        limited_entries = sorted_entries[:limit]
        
        # Update access counts
        for entry in limited_entries:
            entry["access_count"] += 1
            entry["last_accessed"] = datetime.now().isoformat()
        
        self._save_memory()
        
        return ToolResponse(
            success=True,
            message=f"Retrieved {len(limited_entries)} memory entries",
            data={
                "entries": limited_entries,
                "total_found": len(filtered_entries),
                "category": category,
                "time_range": time_range
            }
        )
    
    async def _search_memory(self, kwargs: Dict[str, Any]) -> ToolResponse:
        """Search memory entries"""
        
        query = kwargs.get("query", "").lower()
        category = kwargs.get("category")
        limit = kwargs.get("limit", 10)
        time_range = kwargs.get("time_range", "all")
        
        if not query:
            return ToolResponse(
                success=False,
                message="Query is required for search operation",
                status=ToolStatus.FAILED
            )
        
        # Get entries to search
        if category:
            entries = self.memory_data.get(category, [])
        else:
            entries = []
            for cat in self.memory_data:
                if cat != "stats":
                    entries.extend(self.memory_data[cat])
        
        # Filter by time range
        filtered_entries = self._filter_by_time_range(entries, time_range)
        
        # Search in content and metadata
        matching_entries = []
        for entry in filtered_entries:
            content_match = query in entry["content"].lower()
            metadata_match = any(query in str(v).lower() for v in entry.get("metadata", {}).values())
            
            if content_match or metadata_match:
                # Calculate relevance score
                relevance_score = 0
                if content_match:
                    relevance_score += entry["content"].lower().count(query)
                if metadata_match:
                    relevance_score += 1
                
                entry["relevance_score"] = relevance_score
                matching_entries.append(entry)
        
        # Sort by relevance and limit
        sorted_entries = sorted(matching_entries, key=lambda x: x["relevance_score"], reverse=True)
        limited_entries = sorted_entries[:limit]
        
        # Update access counts
        for entry in limited_entries:
            entry["access_count"] += 1
            entry["last_accessed"] = datetime.now().isoformat()
        
        self._save_memory()
        
        return ToolResponse(
            success=True,
            message=f"Found {len(limited_entries)} matching memory entries",
            data={
                "entries": limited_entries,
                "total_matches": len(matching_entries),
                "query": query,
                "category": category
            }
        )
    
    async def _analyze_patterns(self, kwargs: Dict[str, Any]) -> ToolResponse:
        """Analyze patterns in memory data"""
        
        analysis = {
            "usage_patterns": self._analyze_usage_patterns(),
            "content_patterns": self._analyze_content_patterns(),
            "temporal_patterns": self._analyze_temporal_patterns(),
            "category_distribution": self._analyze_category_distribution(),
            "insights": self._generate_insights()
        }
        
        return ToolResponse(
            success=True,
            message="Memory pattern analysis completed",
            data=analysis
        )
    
    async def _export_memory(self, kwargs: Dict[str, Any]) -> ToolResponse:
        """Export memory data"""
        
        export_format = kwargs.get("format", "json")
        category = kwargs.get("category")
        
        # Get data to export
        if category:
            export_data = {
                category: self.memory_data.get(category, []),
                "stats": self.memory_data["stats"]
            }
        else:
            export_data = self.memory_data.copy()
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"memory_export_{timestamp}.{export_format}"
        
        try:
            if export_format == "json":
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
            else:
                return ToolResponse(
                    success=False,
                    message=f"Unsupported export format: {export_format}",
                    status=ToolStatus.FAILED
                )
            
            return ToolResponse(
                success=True,
                message=f"Memory data exported to: {filename}",
                data={
                    "filename": filename,
                    "format": export_format,
                    "entries_exported": sum(len(v) for k, v in export_data.items() if k != "stats")
                }
            )
            
        except Exception as e:
            return ToolResponse(
                success=False,
                message=f"Export failed: {str(e)}",
                status=ToolStatus.FAILED
            )
    
    async def _get_memory_stats(self) -> ToolResponse:
        """Get memory statistics"""
        
        stats = self.memory_data["stats"].copy()
        
        # Add dynamic stats
        total_content_length = 0
        most_accessed = None
        max_access_count = 0
        
        for category, entries in self.memory_data.items():
            if category == "stats":
                continue
            
            for entry in entries:
                total_content_length += len(entry["content"])
                if entry["access_count"] > max_access_count:
                    max_access_count = entry["access_count"]
                    most_accessed = entry
        
        stats["total_content_length"] = total_content_length
        stats["average_content_length"] = total_content_length / max(1, stats["total_entries"])
        stats["most_accessed_entry"] = most_accessed["id"] if most_accessed else None
        stats["max_access_count"] = max_access_count
        
        return ToolResponse(
            success=True,
            message="Memory statistics retrieved",
            data=stats
        )
    
    def _load_memory(self) -> Dict[str, Any]:
        """Load memory data from file"""
        
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logging.info(f"Error loading memory file: {e}")
        
        # Return default structure
        return {
            "stats": {
                "created_at": datetime.now().isoformat(),
                "total_entries": 0,
                "entries_by_category": {},
                "last_updated": datetime.now().isoformat()
            }
        }
    
    def _save_memory(self) -> Any:
        """Save memory data to file"""
        
        self.memory_data["stats"]["last_updated"] = datetime.now().isoformat()
        
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.info(f"Error saving memory file: {e}")
    
    def _generate_memory_id(self) -> str:
        """Generate unique memory ID"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def _filter_by_time_range(self, entries: List[Dict], time_range: str) -> List[Dict]:
        """Filter entries by time range"""
        
        if time_range == "all":
            return entries
        
        from datetime import timedelta
        
        now = datetime.now()
        time_deltas = {
            "hour": timedelta(hours=1),
            "day": timedelta(days=1),
            "week": timedelta(weeks=1),
            "month": timedelta(days=30)
        }
        
        cutoff_time = now - time_deltas.get(time_range, timedelta(0))
        
        filtered = []
        for entry in entries:
            entry_time = datetime.fromisoformat(entry["timestamp"])
            if entry_time >= cutoff_time:
                filtered.append(entry)
        
        return filtered
    
    def _analyze_usage_patterns(self) -> Dict[str, Any]:
        """Analyze memory usage patterns"""
        
        total_accesses = 0
        access_distribution = {}
        
        for category, entries in self.memory_data.items():
            if category == "stats":
                continue
                
            category_accesses = sum(entry["access_count"] for entry in entries)
            total_accesses += category_accesses
            access_distribution[category] = category_accesses
        
        return {
            "total_accesses": total_accesses,
            "access_by_category": access_distribution,
            "most_accessed_category": max(access_distribution, key=access_distribution.get) if access_distribution else None
        }
    
    def _analyze_content_patterns(self) -> Dict[str, Any]:
        """Analyze content patterns"""
        
        word_frequency = {}
        total_words = 0
        
        for category, entries in self.memory_data.items():
            if category == "stats":
                continue
                
            for entry in entries:
                words = entry["content"].lower().split()
                total_words += len(words)
                
                for word in words:
                    # Clean word
                    word = word.strip('.,!?";:()[]{}')
                    if len(word) > 3:  # Only meaningful words
                        word_frequency[word] = word_frequency.get(word, 0) + 1
        
        # Get top words
        top_words = sorted(word_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "total_words": total_words,
            "unique_words": len(word_frequency),
            "top_words": top_words,
            "vocabulary_richness": len(word_frequency) / max(1, total_words)
        }
    
    def _analyze_temporal_patterns(self) -> Dict[str, Any]:
        """Analyze temporal patterns"""
        
        hourly_distribution = {}
        daily_distribution = {}
        
        for category, entries in self.memory_data.items():
            if category == "stats":
                continue
                
            for entry in entries:
                timestamp = datetime.fromisoformat(entry["timestamp"])
                hour = timestamp.hour
                day = timestamp.strftime("%A")
                
                hourly_distribution[hour] = hourly_distribution.get(hour, 0) + 1
                daily_distribution[day] = daily_distribution.get(day, 0) + 1
        
        return {
            "hourly_distribution": hourly_distribution,
            "daily_distribution": daily_distribution,
            "peak_hour": max(hourly_distribution, key=hourly_distribution.get) if hourly_distribution else None,
            "peak_day": max(daily_distribution, key=daily_distribution.get) if daily_distribution else None
        }
    
    def _analyze_category_distribution(self) -> Dict[str, Any]:
        """Analyze category distribution"""
        
        return self.memory_data["stats"]["entries_by_category"].copy()
    
    def _generate_insights(self) -> List[str]:
        """Generate insights from memory analysis"""
        
        insights = []
        stats = self.memory_data["stats"]
        
        # Total entries insight
        total = stats["total_entries"]
        if total > 100:
            insights.append(f"Memory system has grown to {total} entries - showing extensive usage")
        elif total > 50:
            insights.append(f"Memory system is actively used with {total} entries")
        elif total > 10:
            insights.append(f"Memory system is building up with {total} entries")
        
        # Category insights
        categories = stats["entries_by_category"]
        if categories:
            top_category = max(categories, key=categories.get)
            insights.append(f"Most active category is '{top_category}' with {categories[top_category]} entries")
        
        # Usage insights
        usage_patterns = self._analyze_usage_patterns()
        if usage_patterns["total_accesses"] > total * 2:
            insights.append("High memory retrieval activity - entries are being accessed frequently")
        
        return insights