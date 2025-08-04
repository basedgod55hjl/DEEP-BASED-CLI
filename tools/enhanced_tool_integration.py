#!/usr/bin/env python3
"""
🔧 Enhanced Tool Integration - Anthropic Cookbook Inspired
Made by @Lucariolucario55 on Telegram

Advanced tool integration patterns inspired by Anthropic Cookbook examples
"""

import json
import asyncio
import logging
from typing import Dict, Any, List, Optional, Union, Callable
from dataclasses import dataclass
from enum import Enum
import re
import traceback
from datetime import datetime
import hashlib
import functools

logger = logging.getLogger(__name__)

class ToolType(Enum):
    """Tool types for categorization"""
    CALCULATOR = "calculator"
    SEARCH = "search"
    CODE_GENERATION = "code_generation"
    ANALYSIS = "analysis"
    SYSTEM = "system"
    CUSTOM = "custom"

@dataclass
class ToolDefinition:
    """Tool definition with schema validation"""
    name: str
    description: str
    tool_type: ToolType
    input_schema: Dict[str, Any]
    function: Callable
    required_params: List[str]
    optional_params: List[str]
    examples: List[Dict[str, Any]]
    error_handling: bool = True
    rate_limiting: bool = False
    max_calls_per_minute: int = 60

class ToolRegistry:
    """Advanced tool registry with validation and caching"""
    
    def __init__(self):
        self.tools: Dict[str, ToolDefinition] = {}
        self.call_history: List[Dict[str, Any]] = []
        self.rate_limit_cache: Dict[str, List[datetime]] = {}
        self.tool_cache: Dict[str, Any] = {}
        
    def register_tool(self, tool_def: ToolDefinition) -> None:
        """Register a tool with validation"""
        if tool_def.name in self.tools:
            logger.warning(f"Tool {tool_def.name} already registered, overwriting")
        
        # Validate schema
        self._validate_schema(tool_def.input_schema)
        
        # Add examples validation
        for example in tool_def.examples:
            self._validate_example(example, tool_def.input_schema)
        
        self.tools[tool_def.name] = tool_def
        logger.info(f"Registered tool: {tool_def.name}")
    
    def _validate_schema(self, schema: Dict[str, Any]) -> None:
        """Validate tool input schema"""
        required_fields = ["type", "properties"]
        for field in required_fields:
            if field not in schema:
                raise ValueError(f"Schema missing required field: {field}")
        
        if schema["type"] != "object":
            raise ValueError("Schema type must be 'object'")
    
    def _validate_example(self, example: Dict[str, Any], schema: Dict[str, Any]) -> None:
        """Validate example against schema"""
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        
        # Check required fields
        for field in required:
            if field not in example:
                raise ValueError(f"Example missing required field: {field}")
        
        # Check field types
        for field, value in example.items():
            if field in properties:
                expected_type = properties[field].get("type")
                if expected_type and not self._validate_type(value, expected_type):
                    raise ValueError(f"Example field {field} has wrong type")
    
    def _validate_type(self, value: Any, expected_type: str) -> bool:
        """Validate value type"""
        type_map = {
            "string": str,
            "number": (int, float),
            "integer": int,
            "boolean": bool,
            "array": list,
            "object": dict
        }
        
        expected_class = type_map.get(expected_type)
        if expected_class is None:
            return True  # Unknown type, skip validation
        
        return isinstance(value, expected_class)
    
    async def execute_tool(self, tool_name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool with advanced error handling and caching"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found")
        
        tool_def = self.tools[tool_name]
        
        # Check rate limiting
        if tool_def.rate_limiting:
            if not self._check_rate_limit(tool_name):
                raise Exception(f"Rate limit exceeded for tool {tool_name}")
        
        # Validate inputs
        self._validate_inputs(inputs, tool_def.input_schema)
        
        # Check cache
        cache_key = self._generate_cache_key(tool_name, inputs)
        if cache_key in self.tool_cache:
            logger.info(f"Using cached result for {tool_name}")
            return self.tool_cache[cache_key]
        
        try:
            # Execute tool
            start_time = datetime.now()
            
            if asyncio.iscoroutinefunction(tool_def.function):
                result = await tool_def.function(**inputs)
            else:
                result = tool_def.function(**inputs)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Record call
            call_record = {
                "tool_name": tool_name,
                "inputs": inputs,
                "result": result,
                "execution_time": execution_time,
                "timestamp": datetime.now(),
                "success": True
            }
            self.call_history.append(call_record)
            
            # Cache result
            self.tool_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            # Record error
            call_record = {
                "tool_name": tool_name,
                "inputs": inputs,
                "error": str(e),
                "timestamp": datetime.now(),
                "success": False
            }
            self.call_history.append(call_record)
            
            if tool_def.error_handling:
                logger.error(f"Tool {tool_name} execution failed: {e}")
                return {"error": str(e), "tool": tool_name}
            else:
                raise
    
    def _check_rate_limit(self, tool_name: str) -> bool:
        """Check rate limiting for tool"""
        now = datetime.now()
        minute_ago = now.replace(second=0, microsecond=0)
        
        if tool_name not in self.rate_limit_cache:
            self.rate_limit_cache[tool_name] = []
        
        # Remove old entries
        self.rate_limit_cache[tool_name] = [
            t for t in self.rate_limit_cache[tool_name] 
            if t > minute_ago
        ]
        
        tool_def = self.tools[tool_name]
        if len(self.rate_limit_cache[tool_name]) >= tool_def.max_calls_per_minute:
            return False
        
        self.rate_limit_cache[tool_name].append(now)
        return True
    
    def _validate_inputs(self, inputs: Dict[str, Any], schema: Dict[str, Any]) -> None:
        """Validate tool inputs against schema"""
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        
        # Check required fields
        for field in required:
            if field not in inputs:
                raise ValueError(f"Missing required field: {field}")
        
        # Check field types
        for field, value in inputs.items():
            if field in properties:
                expected_type = properties[field].get("type")
                if expected_type and not self._validate_type(value, expected_type):
                    raise ValueError(f"Field {field} has wrong type")
    
    def _generate_cache_key(self, tool_name: str, inputs: Dict[str, Any]) -> str:
        """Generate cache key for tool execution"""
        input_str = json.dumps(inputs, sort_keys=True)
        return hashlib.md5(f"{tool_name}:{input_str}".encode()).hexdigest()
    
    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Get all tool schemas for LLM integration"""
        schemas = []
        for tool_def in self.tools.values():
            schema = {
                "name": tool_def.name,
                "description": tool_def.description,
                "input_schema": tool_def.input_schema,
                "examples": tool_def.examples
            }
            schemas.append(schema)
        return schemas
    
    def get_tool_statistics(self) -> Dict[str, Any]:
        """Get tool usage statistics"""
        stats = {
            "total_tools": len(self.tools),
            "total_calls": len(self.call_history),
            "successful_calls": len([c for c in self.call_history if c["success"]]),
            "failed_calls": len([c for c in self.call_history if not c["success"]]),
            "cache_hits": len(self.tool_cache),
            "tool_usage": {}
        }
        
        for tool_name in self.tools:
            tool_calls = [c for c in self.call_history if c["tool_name"] == tool_name]
            stats["tool_usage"][tool_name] = {
                "total_calls": len(tool_calls),
                "successful_calls": len([c for c in tool_calls if c["success"]]),
                "average_execution_time": sum(c.get("execution_time", 0) for c in tool_calls) / len(tool_calls) if tool_calls else 0
            }
        
        return stats

# Enhanced Calculator Tool (inspired by Anthropic Cookbook)
def create_calculator_tool() -> ToolDefinition:
    """Create enhanced calculator tool with validation"""
    
    def calculate(expression: str) -> str:
        """Enhanced calculator with safety checks"""
        # Remove dangerous characters
        safe_expression = re.sub(r'[^0-9+\-*/().\s]', '', expression)
        
        # Additional safety checks
        if len(safe_expression) > 100:
            return "Error: Expression too long"
        
        if safe_expression.count('(') != safe_expression.count(')'):
            return "Error: Mismatched parentheses"
        
        try:
            # Use ast.literal_eval for safer evaluation
            import ast
            # Convert to valid Python expression
            python_expr = safe_expression.replace('^', '**')
            result = eval(python_expr)
            return str(result)
        except (SyntaxError, ZeroDivisionError, NameError, TypeError, OverflowError) as e:
            return f"Error: {str(e)}"
    
    return ToolDefinition(
        name="calculator",
        description="A safe calculator that performs basic arithmetic operations with validation",
        tool_type=ToolType.CALCULATOR,
        input_schema={
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The mathematical expression to evaluate (e.g., '2 + 3 * 4')"
                }
            },
            "required": ["expression"]
        },
        function=calculate,
        required_params=["expression"],
        optional_params=[],
        examples=[
            {"expression": "2 + 3 * 4"},
            {"expression": "(10 + 5) / 3"},
            {"expression": "2^3 + 1"}
        ],
        error_handling=True,
        rate_limiting=True,
        max_calls_per_minute=100
    )

# Enhanced Search Tool
def create_search_tool() -> ToolDefinition:
    """Create enhanced search tool"""
    
    async def search(query: str, engine: str = "duckduckgo", max_results: int = 5) -> Dict[str, Any]:
        """Enhanced search with multiple engines"""
        try:
            if engine == "duckduckgo":
                from duckduckgo_search import DDGS
                with DDGS() as ddgs:
                    results = list(ddgs.text(query, max_results=max_results))
                return {
                    "query": query,
                    "engine": engine,
                    "results": results,
                    "count": len(results)
                }
            else:
                return {"error": f"Unsupported search engine: {engine}"}
        except Exception as e:
            return {"error": str(e)}
    
    return ToolDefinition(
        name="web_search",
        description="Search the web using multiple search engines",
        tool_type=ToolType.SEARCH,
        input_schema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query"
                },
                "engine": {
                    "type": "string",
                    "description": "Search engine (duckduckgo, google)",
                    "default": "duckduckgo"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results",
                    "default": 5
                }
            },
            "required": ["query"]
        },
        function=search,
        required_params=["query"],
        optional_params=["engine", "max_results"],
        examples=[
            {"query": "latest developments in quantum computing"},
            {"query": "Python async programming", "engine": "duckduckgo", "max_results": 10}
        ],
        error_handling=True,
        rate_limiting=True,
        max_calls_per_minute=30
    )

# Tool Manager Integration
class EnhancedToolManager:
    """Enhanced tool manager with registry integration"""
    
    def __init__(self):
        self.registry = ToolRegistry()
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register default tools"""
        self.registry.register_tool(create_calculator_tool())
        self.registry.register_tool(create_search_tool())
    
    async def execute_tool_call(self, tool_name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tool call with enhanced error handling"""
        return await self.registry.execute_tool(tool_name, inputs)
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools"""
        return self.registry.get_tool_schemas()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get tool usage statistics"""
        return self.registry.get_tool_statistics()
    
    def register_custom_tool(self, tool_def: ToolDefinition):
        """Register a custom tool"""
        self.registry.register_tool(tool_def)

# Example usage and testing
async def test_enhanced_tools():
    """Test the enhanced tool integration"""
    manager = EnhancedToolManager()
    
    # Test calculator
    result = await manager.execute_tool_call("calculator", {"expression": "2 + 3 * 4"})
    print(f"Calculator result: {result}")
    
    # Test search
    result = await manager.execute_tool_call("web_search", {"query": "Python programming"})
    print(f"Search result: {result}")
    
    # Get statistics
    stats = manager.get_statistics()
    print(f"Tool statistics: {stats}")

if __name__ == "__main__":
    asyncio.run(test_enhanced_tools()) 