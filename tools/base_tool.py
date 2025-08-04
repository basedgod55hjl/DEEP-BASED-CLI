"""
Base Tool Class for Enhanced BASED GOD CLI
Inspired by Agent Zero's tool architecture
"""

import asyncio
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum

class ToolStatus(Enum):
    """Tool execution status"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"

@dataclass
class ToolResponse:
    """Standardized tool response following Agent Zero patterns"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    status: ToolStatus = ToolStatus.SUCCESS
    execution_time: float = 0.0
    metadata: Optional[Dict[str, Any]] = None
    break_loop: bool = False

class BaseTool(ABC):
    """
    Base class for all tools in the Enhanced BASED GOD CLI
    Follows Agent Zero's tool architecture patterns
    """
    
    def __init__(self, name: str, description: str, capabilities: List[str] = None):
    """__init__ function."""
        self.name = name
        self.description = description
        self.capabilities = capabilities or []
        self.usage_count = 0
        self.total_execution_time = 0.0
        self.last_used = None
        self.success_count = 0
        self.error_count = 0
        
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResponse:
        """
        Execute the tool with given parameters
        Must be implemented by each tool
        """
        pass
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """
        Get the tool's parameter schema
        Used for validation and documentation
        """
        pass
    
    async def safe_execute(self, **kwargs) -> ToolResponse:
        """
        Safe execution wrapper with error handling and timing
        """
        start_time = time.time()
        self.usage_count += 1
        self.last_used = datetime.now()
        
        try:
            # Validate parameters
            validation_result = self.validate_parameters(kwargs)
            if not validation_result["valid"]:
                return ToolResponse(
                    success=False,
                    message=f"Parameter validation failed: {validation_result['error']}",
                    status=ToolStatus.FAILED,
                    execution_time=time.time() - start_time
                )
            
            # Execute the tool
            result = await self.execute(**kwargs)
            
            # Update statistics
            execution_time = time.time() - start_time
            result.execution_time = execution_time
            self.total_execution_time += execution_time
            
            if result.success:
                self.success_count += 1
            else:
                self.error_count += 1
            
            return result
            
        except asyncio.TimeoutError:
            self.error_count += 1
            return ToolResponse(
                success=False,
                message="Tool execution timed out",
                status=ToolStatus.TIMEOUT,
                execution_time=time.time() - start_time
            )
        except Exception as e:
            self.error_count += 1
            return ToolResponse(
                success=False,
                message=f"Tool execution failed: {str(e)}",
                status=ToolStatus.FAILED,
                execution_time=time.time() - start_time,
                metadata={"error_type": type(e).__name__}
            )
    
    def validate_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate tool parameters against schema
        """
        schema = self.get_schema()
        required_params = schema.get("required", [])
        
        # Check required parameters
        missing_params = [param for param in required_params if param not in params]
        if missing_params:
            return {
                "valid": False,
                "error": f"Missing required parameters: {', '.join(missing_params)}"
            }
        
        # Additional validation can be added here
        return {"valid": True}
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get tool usage statistics"""
        return {
            "name": self.name,
            "usage_count": self.usage_count,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "success_rate": self.success_count / max(1, self.usage_count) * 100,
            "total_execution_time": self.total_execution_time,
            "average_execution_time": self.total_execution_time / max(1, self.usage_count),
            "last_used": self.last_used.isoformat() if self.last_used else None
        }
    
    def get_help(self) -> str:
        """Get tool help information"""
        schema = self.get_schema()
        
        help_text = f"""
**{self.name}**
{self.description}

**Capabilities:**
{chr(10).join(f"• {cap}" for cap in self.capabilities)}

**Parameters:**
"""
        
        for param, info in schema.get("properties", {}).items():
            required = param in schema.get("required", [])
            param_type = info.get("type", "any")
            description = info.get("description", "No description")
            
            help_text += f"• **{param}** ({param_type})"
            if required:
                help_text += " *[Required]*"
            help_text += f": {description}\n"
        
        return help_text
    
    def __str__(self) -> str:
        return f"{self.name}: {self.description}"
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}', usage={self.usage_count})>"