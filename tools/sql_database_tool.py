"""
SQL Database Tool - Local SQLite database integration
"""

import sqlite3
import aiosqlite
from typing import Dict, Any, List, Optional
from datetime import datetime
from .base_tool import BaseTool, ToolResponse


class SQLDatabaseTool(BaseTool):
    """
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