"""
Enhanced Base Tool - Inspired by Google Gemini CLI
A sophisticated tool system with proper validation, streaming, and MCP support
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Callable, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import json
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class ToolErrorType(Enum):
    """Types of tool execution errors"""
    VALIDATION_ERROR = "validation_error"
    EXECUTION_ERROR = "execution_error"
    PERMISSION_ERROR = "permission_error"
    TIMEOUT_ERROR = "timeout_error"
    NETWORK_ERROR = "network_error"
    RESOURCE_ERROR = "resource_error"

@dataclass
class ToolLocation:
    """Represents a file system location that a tool will affect"""
    path: str
    operation: str  # "read", "write", "delete", "create", etc.
    description: str = ""

@dataclass
class ToolResult:
    """Result of tool execution"""
    success: bool
    content: str = ""
    error_message: str = ""
    error_type: Optional[ToolErrorType] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    locations_affected: List[ToolLocation] = field(default_factory=list)

@dataclass
class ToolCallConfirmationDetails:
    """Details for tool confirmation prompt"""
    title: str
    description: str
    locations: List[ToolLocation] = field(default_factory=list)
    risk_level: str = "medium"  # "low", "medium", "high"
    
@dataclass
class ToolSchema:
    """Schema definition for tool parameters"""
    name: str
    description: str
    parameters: Dict[str, Any]
    required: List[str] = field(default_factory=list)

class Icon(Enum):
    """Icons for tools (can be extended for UI)"""
    FILE = "📄"
    FOLDER = "📁"
    EDIT = "✏️"
    SEARCH = "🔍"
    TERMINAL = "💻"
    WEB = "🌐"
    MEMORY = "🧠"
    CODE = "💾"
    TOOLS = "🔧"
    CHAT = "💬"

class EnhancedBaseTool(ABC):
    """
    Enhanced base tool class inspired by Gemini CLI
    Provides sophisticated tool functionality with validation, streaming, and MCP support
    """
    
    def __init__(self) -> None:
        self.execution_history: List[Dict[str, Any]] = []
        self._is_streaming = False
        self._update_callback: Optional[Callable[[str], None]] = None
        
    @property
    @abstractmethod
    def name(self) -> str:
        """Internal name of the tool"""
        pass
    
    @property
    @abstractmethod
    def display_name(self) -> str:
        """User-friendly display name"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what the tool does"""
        pass
    
    @property
    @abstractmethod
    def icon(self) -> Icon:
        """Icon for the tool"""
        pass
    
    @property
    @abstractmethod
    def schema(self) -> ToolSchema:
        """Parameter schema for the tool"""
        pass
    
    @property
    def is_output_markdown(self) -> bool:
        """Whether output should be rendered as markdown"""
        return False
    
    @property
    def can_update_output(self) -> bool:
        """Whether tool supports streaming/live output"""
        return False
    
    @property
    def supports_streaming(self) -> bool:
        """Whether tool supports streaming responses"""
        return self.can_update_output
    
    def validate_tool_params(self, params: Dict[str, Any]) -> Optional[str]:
        """
        Validate tool parameters
        Returns error message if invalid, None if valid
        """
        try:
            schema = self.schema
            required_params = schema.required
            
            # Check required parameters
            for param in required_params:
                if param not in params:
                    return f"Missing required parameter: {param}"
                    
            # Check parameter types based on schema
            param_defs = schema.parameters.get("properties", {})
            for param_name, param_value in params.items():
                if param_name in param_defs:
                    param_def = param_defs[param_name]
                    expected_type = param_def.get("type", "string")
                    
                    if expected_type == "string" and not isinstance(param_value, str):
                        return f"Parameter {param_name} must be a string"
                    elif expected_type == "integer" and not isinstance(param_value, int):
                        return f"Parameter {param_name} must be an integer"
                    elif expected_type == "boolean" and not isinstance(param_value, bool):
                        return f"Parameter {param_name} must be a boolean"
                    elif expected_type == "array" and not isinstance(param_value, list):
                        return f"Parameter {param_name} must be an array"
                        
            return None
            
        except Exception as e:
            return f"Validation error: {str(e)}"
    
    def get_description(self, params: Dict[str, Any]) -> str:
        """Get pre-execution description"""
        return f"Executing {self.display_name} with parameters: {params}"
    
    def tool_locations(self, params: Dict[str, Any]) -> List[ToolLocation]:
        """Get list of file system locations this tool will affect"""
        return []
    
    async def should_confirm_execute(
        self, 
        params: Dict[str, Any], 
        abort_signal: Optional[asyncio.Event] = None
    ) -> Union[ToolCallConfirmationDetails, bool]:
        """
        Determine if tool execution should be confirmed
        Returns confirmation details if confirmation needed, False otherwise
        """
        # Validate parameters first
        validation_error = self.validate_tool_params(params)
        if validation_error:
            return False
            
        # Check if tool affects sensitive locations
        locations = self.tool_locations(params)
        sensitive_operations = ["delete", "write", "modify"]
        
        for location in locations:
            if location.operation in sensitive_operations:
                return ToolCallConfirmationDetails(
                    title=f"Confirm {self.display_name}",
                    description=self.get_description(params),
                    locations=locations,
                    risk_level="medium"
                )
                
        return False
    
    @abstractmethod
    async def execute(
        self,
        params: Dict[str, Any],
        signal: Optional[asyncio.Event] = None,
        update_output: Optional[Callable[[str], None]] = None
    ) -> ToolResult:
        """Execute the tool with given parameters"""
        pass
    
    def _record_execution(
        self, 
        params: Dict[str, Any], 
        result: ToolResult,
        start_time: float
    ) -> None:
        """Record tool execution in history"""
        execution_record = {
            "tool_name": self.name,
            "timestamp": datetime.now().isoformat(),
            "params": params,
            "success": result.success,
            "execution_time": result.execution_time,
            "error_type": result.error_type.value if result.error_type else None,
            "locations_affected": [
                {"path": loc.path, "operation": loc.operation} 
                for loc in result.locations_affected
            ]
        }
        self.execution_history.append(execution_record)
        
        # Keep only last 100 executions
        if len(self.execution_history) > 100:
            self.execution_history = self.execution_history[-100:]
    
    async def execute_with_validation(
        self,
        params: Dict[str, Any],
        signal: Optional[asyncio.Event] = None,
        update_output: Optional[Callable[[str], None]] = None,
        require_confirmation: bool = True
    ) -> ToolResult:
        """
        Execute tool with full validation and confirmation flow
        """
        start_time = time.time()
        
        try:
            # Validate parameters
            validation_error = self.validate_tool_params(params)
            if validation_error:
                result = ToolResult(
                    success=False,
                    error_message=validation_error,
                    error_type=ToolErrorType.VALIDATION_ERROR,
                    execution_time=time.time() - start_time
                )
                self._record_execution(params, result, start_time)
                return result
            
            # Check for confirmation if required
            if require_confirmation:
                confirmation = await self.should_confirm_execute(params, signal)
                if confirmation and confirmation is not False:
                    logger.info(f"Tool {self.name} requires confirmation: {confirmation.description}")
                    # In a real implementation, this would prompt the user
                    # For now, we'll proceed assuming confirmation
            
            # Set up streaming callback
            self._update_callback = update_output
            self._is_streaming = update_output is not None and self.supports_streaming
            
            # Execute the tool
            result = await self.execute(params, signal, update_output)
            result.execution_time = time.time() - start_time
            
            # Record execution
            self._record_execution(params, result, start_time)
            
            return result
            
        except asyncio.CancelledError:
            result = ToolResult(
                success=False,
                error_message="Tool execution was cancelled",
                error_type=ToolErrorType.EXECUTION_ERROR,
                execution_time=time.time() - start_time
            )
            self._record_execution(params, result, start_time)
            raise
            
        except Exception as e:
            result = ToolResult(
                success=False,
                error_message=f"Unexpected error: {str(e)}",
                error_type=ToolErrorType.EXECUTION_ERROR,
                execution_time=time.time() - start_time
            )
            self._record_execution(params, result, start_time)
            return result
    
    def _stream_output(self, content: str) -> None:
        """Stream output if streaming is enabled"""
        if self._is_streaming and self._update_callback:
            self._update_callback(content)
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics for this tool"""
        if not self.execution_history:
            return {"total_executions": 0}
            
        total_executions = len(self.execution_history)
        successful_executions = sum(1 for ex in self.execution_history if ex["success"])
        failed_executions = total_executions - successful_executions
        
        execution_times = [ex["execution_time"] for ex in self.execution_history]
        avg_execution_time = sum(execution_times) / len(execution_times)
        
        error_types = {}
        for ex in self.execution_history:
            if not ex["success"] and ex["error_type"]:
                error_types[ex["error_type"]] = error_types.get(ex["error_type"], 0) + 1
        
        return {
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "failed_executions": failed_executions,
            "success_rate": successful_executions / total_executions,
            "average_execution_time": avg_execution_time,
            "error_types": error_types,
            "last_execution": self.execution_history[-1]["timestamp"] if self.execution_history else None
        }

class ToolRegistry:
    """Registry for managing enhanced tools"""
    
    def __init__(self) -> None:
        self._tools: Dict[str, EnhancedBaseTool] = {}
        self._aliases: Dict[str, str] = {}
    
    def register_tool(self, tool: EnhancedBaseTool, aliases: Optional[List[str]] = None) -> None:
        """Register a tool with optional aliases"""
        self._tools[tool.name] = tool
        
        if aliases:
            for alias in aliases:
                self._aliases[alias] = tool.name
                
        logger.info(f"Registered tool: {tool.name} ({tool.display_name})")
    
    def get_tool(self, name: str) -> Optional[EnhancedBaseTool]:
        """Get tool by name or alias"""
        # Check direct name first
        if name in self._tools:
            return self._tools[name]
            
        # Check aliases
        if name in self._aliases:
            return self._tools[self._aliases[name]]
            
        return None
    
    def list_tools(self) -> List[EnhancedBaseTool]:
        """Get list of all registered tools"""
        return list(self._tools.values())
    
    def get_tool_schemas(self) -> Dict[str, ToolSchema]:
        """Get schemas for all tools"""
        return {name: tool.schema for name, tool in self._tools.items()}
    
    def get_tools_by_category(self, category: str) -> List[EnhancedBaseTool]:
        """Get tools by category (based on icon or name pattern)"""
        category_mapping = {
            "file": [Icon.FILE, Icon.FOLDER, Icon.EDIT],
            "system": [Icon.TERMINAL, Icon.TOOLS],
            "web": [Icon.WEB],
            "memory": [Icon.MEMORY],
            "code": [Icon.CODE],
            "chat": [Icon.CHAT]
        }
        
        target_icons = category_mapping.get(category.lower(), [])
        return [tool for tool in self._tools.values() if tool.icon in target_icons]

# Global tool registry instance
tool_registry = ToolRegistry()