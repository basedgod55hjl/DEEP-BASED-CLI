"""
Tool Manager - Enhanced BASED GOD CLI
Centralized tool management and orchestration inspired by Agent Zero
"""

import asyncio
from typing import Any, Dict, List, Optional
from datetime import datetime

from .base_tool import BaseTool, ToolResponse, ToolStatus
from .web_scraper_tool import WebScraperTool
from .code_generator_tool import CodeGeneratorTool
from .data_analyzer_tool import DataAnalyzerTool
from .file_processor_tool import FileProcessorTool
from .memory_tool import MemoryTool
from .llm_query_tool import LLMQueryTool
from .reasoning_engine import FastReasoningEngine

class ToolManager:
    """
    Central tool manager for Enhanced BASED GOD CLI
    Manages tool registration, execution, and orchestration
    """
    
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self.execution_history: List[Dict[str, Any]] = []
        self.tool_dependencies: Dict[str, List[str]] = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register all default tools"""
        
        # Create LLM tool first so reasoning engine can reference it
        llm_tool = LLMQueryTool()
        
        default_tools = [
            WebScraperTool(),
            CodeGeneratorTool(),
            DataAnalyzerTool(),
            FileProcessorTool(),
            MemoryTool(),
            llm_tool,
            FastReasoningEngine(llm_tool=llm_tool)  # Pass LLM tool for fast consultations
        ]
        
        for tool in default_tools:
            self.register_tool(tool)
    
    def register_tool(self, tool: BaseTool) -> bool:
        """Register a new tool"""
        
        tool_name = tool.name.lower().replace(" ", "_")
        
        if tool_name in self.tools:
            print(f"Warning: Tool '{tool_name}' already registered, replacing...")
        
        self.tools[tool_name] = tool
        print(f"✅ Registered tool: {tool.name}")
        return True
    
    def unregister_tool(self, tool_name: str) -> bool:
        """Unregister a tool"""
        
        tool_name = tool_name.lower().replace(" ", "_")
        
        if tool_name in self.tools:
            del self.tools[tool_name]
            print(f"❌ Unregistered tool: {tool_name}")
            return True
        
        return False
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """Get a tool by name"""
        
        tool_name = tool_name.lower().replace(" ", "_")
        return self.tools.get(tool_name)
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List all registered tools"""
        
        tool_list = []
        
        for tool_name, tool in self.tools.items():
            stats = tool.get_statistics()
            
            tool_info = {
                "name": tool.name,
                "key": tool_name,
                "description": tool.description,
                "capabilities": tool.capabilities,
                "statistics": stats,
                "schema": tool.get_schema()
            }
            
            tool_list.append(tool_info)
        
        return tool_list
    
    async def execute_tool(self, tool_name: str, **kwargs) -> ToolResponse:
        """Execute a tool with parameters"""
        
        tool = self.get_tool(tool_name)
        
        if not tool:
            return ToolResponse(
                success=False,
                message=f"Tool not found: {tool_name}",
                status=ToolStatus.FAILED
            )
        
        # Record execution start
        execution_id = self._generate_execution_id()
        execution_record = {
            "execution_id": execution_id,
            "tool_name": tool_name,
            "parameters": kwargs,
            "started_at": datetime.now().isoformat(),
            "completed_at": None,
            "result": None,
            "success": False
        }
        
        try:
            # Execute tool
            result = await tool.safe_execute(**kwargs)
            
            # Record execution completion
            execution_record["completed_at"] = datetime.now().isoformat()
            execution_record["result"] = result
            execution_record["success"] = result.success
            
            # Add execution metadata
            result.metadata = result.metadata or {}
            result.metadata["execution_id"] = execution_id
            result.metadata["tool_name"] = tool_name
            
            return result
            
        except Exception as e:
            # Record execution failure
            execution_record["completed_at"] = datetime.now().isoformat()
            execution_record["error"] = str(e)
            
            return ToolResponse(
                success=False,
                message=f"Tool execution error: {str(e)}",
                status=ToolStatus.FAILED,
                metadata={"execution_id": execution_id, "tool_name": tool_name}
            )
        
        finally:
            self.execution_history.append(execution_record)
            
            # Keep only last 100 executions
            if len(self.execution_history) > 100:
                self.execution_history = self.execution_history[-100:]
    
    async def execute_workflow(self, workflow: List[Dict[str, Any]]) -> List[ToolResponse]:
        """Execute a workflow of multiple tools"""
        
        results = []
        context = {}
        
        for step in workflow:
            tool_name = step.get("tool")
            parameters = step.get("parameters", {})
            depends_on = step.get("depends_on", [])
            
            # Wait for dependencies
            if depends_on:
                await self._wait_for_dependencies(depends_on, results)
            
            # Use context from previous steps
            if "use_context" in step:
                context_keys = step["use_context"]
                for key in context_keys:
                    if key in context:
                        parameters[key] = context[key]
            
            # Execute tool
            result = await self.execute_tool(tool_name, **parameters)
            results.append(result)
            
            # Update context
            if result.success and result.data:
                step_name = step.get("name", f"step_{len(results)}")
                context[step_name] = result.data
        
        return results
    
    def suggest_tools(self, description: str) -> List[Dict[str, Any]]:
        """Suggest tools based on description"""
        
        description_lower = description.lower()
        suggestions = []
        
        # Keyword mapping for tool suggestions
        tool_keywords = {
            "web_scraper": ["scrape", "web", "html", "crawl", "extract", "website", "url"],
            "code_generator": ["code", "generate", "program", "function", "class", "script"],
            "data_analyzer": ["analyze", "data", "csv", "json", "statistics", "pattern"],
            "file_processor": ["file", "read", "write", "process", "directory"],
            "memory_tool": ["remember", "store", "memory", "recall", "search"],
            "llm_query_tool": ["ask", "question", "llm", "ai", "chat", "query"]
        }
        
        for tool_name, keywords in tool_keywords.items():
            score = sum(1 for keyword in keywords if keyword in description_lower)
            
            if score > 0:
                tool = self.get_tool(tool_name)
                if tool:
                    suggestions.append({
                        "tool": tool,
                        "score": score,
                        "matched_keywords": [kw for kw in keywords if kw in description_lower]
                    })
        
        # Sort by score
        suggestions.sort(key=lambda x: x["score"], reverse=True)
        
        return suggestions
    
    def get_tool_help(self, tool_name: str) -> Optional[str]:
        """Get help information for a tool"""
        
        tool = self.get_tool(tool_name)
        
        if tool:
            return tool.get_help()
        
        return None
    
    def get_execution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent execution history"""
        
        return self.execution_history[-limit:]
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get system-wide statistics"""
        
        stats = {
            "total_tools": len(self.tools),
            "total_executions": len(self.execution_history),
            "successful_executions": sum(1 for ex in self.execution_history if ex.get("success", False)),
            "failed_executions": sum(1 for ex in self.execution_history if not ex.get("success", False)),
            "tools": {}
        }
        
        # Tool-specific statistics
        for tool_name, tool in self.tools.items():
            tool_stats = tool.get_statistics()
            stats["tools"][tool_name] = tool_stats
        
        # Calculate success rate
        total_exec = stats["total_executions"]
        if total_exec > 0:
            stats["success_rate"] = (stats["successful_executions"] / total_exec) * 100
        else:
            stats["success_rate"] = 0
        
        return stats
    
    def create_dynamic_tool(self, name: str, description: str, function: callable) -> bool:
        """Create a dynamic tool from a function"""
        
        from .base_tool import BaseTool, ToolResponse
        
        class DynamicTool(BaseTool):
            def __init__(self, name, description, function):
                super().__init__(name, description)
                self.function = function
            
            async def execute(self, **kwargs) -> ToolResponse:
                try:
                    result = await self.function(**kwargs)
                    return ToolResponse(
                        success=True,
                        message=f"Dynamic tool '{self.name}' executed successfully",
                        data=result
                    )
                except Exception as e:
                    return ToolResponse(
                        success=False,
                        message=f"Dynamic tool error: {str(e)}",
                        status=ToolStatus.FAILED
                    )
            
            def get_schema(self) -> Dict[str, Any]:
                return {
                    "type": "object",
                    "properties": {
                        "input": {
                            "type": "string",
                            "description": "Input for dynamic tool"
                        }
                    }
                }
        
        dynamic_tool = DynamicTool(name, description, function)
        return self.register_tool(dynamic_tool)
    
    def export_tools_manifest(self) -> Dict[str, Any]:
        """Export tools manifest for external systems"""
        
        manifest = {
            "tool_manager_version": "1.0",
            "exported_at": datetime.now().isoformat(),
            "total_tools": len(self.tools),
            "tools": {}
        }
        
        for tool_name, tool in self.tools.items():
            manifest["tools"][tool_name] = {
                "name": tool.name,
                "description": tool.description,
                "capabilities": tool.capabilities,
                "schema": tool.get_schema(),
                "statistics": tool.get_statistics()
            }
        
        return manifest
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all tools"""
        
        health_status = {
            "overall_status": "healthy",
            "checked_at": datetime.now().isoformat(),
            "tools": {}
        }
        
        issues = []
        
        for tool_name, tool in self.tools.items():
            try:
                # Try to get tool schema (basic functionality test)
                schema = tool.get_schema()
                
                tool_health = {
                    "status": "healthy",
                    "schema_valid": bool(schema),
                    "last_used": tool.last_used.isoformat() if tool.last_used else None,
                    "usage_count": tool.usage_count,
                    "error_rate": tool.error_count / max(1, tool.usage_count) * 100
                }
                
                # Check error rate
                if tool_health["error_rate"] > 50:
                    tool_health["status"] = "unhealthy"
                    issues.append(f"Tool '{tool_name}' has high error rate: {tool_health['error_rate']:.1f}%")
                elif tool_health["error_rate"] > 20:
                    tool_health["status"] = "warning"
                
                health_status["tools"][tool_name] = tool_health
                
            except Exception as e:
                health_status["tools"][tool_name] = {
                    "status": "error",
                    "error": str(e)
                }
                issues.append(f"Tool '{tool_name}' health check failed: {str(e)}")
        
        # Overall status
        if issues:
            health_status["overall_status"] = "issues_detected"
            health_status["issues"] = issues
        
        return health_status
    
    def _generate_execution_id(self) -> str:
        """Generate unique execution ID"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    async def _wait_for_dependencies(self, depends_on: List[str], results: List[ToolResponse]):
        """Wait for workflow dependencies"""
        
        # Simple implementation - in production, this would be more sophisticated
        await asyncio.sleep(0.1)  # Small delay to ensure ordering
    
    def __str__(self) -> str:
        return f"ToolManager(tools={len(self.tools)}, executions={len(self.execution_history)})"
    
    def __repr__(self) -> str:
        return f"<ToolManager(tools={list(self.tools.keys())})>"