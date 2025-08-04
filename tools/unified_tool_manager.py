"""
Unified Tool Manager
--------------------
Combines the Base ``ToolManager`` with the ``EnhancedToolManager`` from
``enhanced_tool_integration`` to present a single interface for executing
all tools in the system.

This allows the CLI to work with both ``BaseTool`` implementations and
function based tools registered through the enhanced registry.
"""

from typing import Any, Dict, List, Optional

from .base_tool import ToolResponse, ToolStatus
from .tool_manager import ToolManager as BaseToolManager
from .enhanced_tool_integration import EnhancedToolManager


class UnifiedToolManager:
    """Wrapper that exposes tools from both managers through one API."""

    def __init__(self) -> None:
        self.base_manager = BaseToolManager()
        self.enhanced_manager = EnhancedToolManager()

    # ------------------------------------------------------------------
    # Tool listing
    def list_tools(self) -> List[Dict[str, Any]]:
        """Return metadata for all available tools."""
        tools = self.base_manager.list_tools()

        # Normalise enhanced tool schemas to match ``ToolManager`` style
        for tool in self.enhanced_manager.get_available_tools():
            tools.append(
                {
                    "name": tool["name"],
                    "key": tool["name"],
                    "description": tool["description"],
                    "capabilities": [tool["name"]],
                    "schema": tool.get("input_schema", {}),
                    "statistics": {},
                }
            )

        return tools

    # ------------------------------------------------------------------
    def get_tool(self, tool_name: str) -> Optional[Any]:
        """Return a BaseTool if it exists in the base manager."""
        return self.base_manager.get_tool(tool_name)

    # ------------------------------------------------------------------
    async def execute_tool(self, tool_name: str, **kwargs: Any) -> ToolResponse:
        """Execute a tool by name, trying base then enhanced managers."""
        tool = self.base_manager.get_tool(tool_name)
        if tool:
            return await self.base_manager.execute_tool(tool_name, **kwargs)

        try:
            result = await self.enhanced_manager.execute_tool_call(tool_name, kwargs)
            success = "error" not in result
            message = (
                "Tool executed successfully" if success else result.get("error", "Execution failed")
            )
            data = result if success else None
            status = ToolStatus.SUCCESS if success else ToolStatus.FAILED
            return ToolResponse(success=success, message=message, data=data, status=status)
        except Exception as exc:  # pragma: no cover - defensive
            return ToolResponse(
                success=False,
                message=f"Enhanced tool error: {exc}",
                status=ToolStatus.FAILED,
            )

    # ------------------------------------------------------------------
    def get_execution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Delegate to base manager for execution history."""
        return self.base_manager.get_execution_history(limit)

    # ------------------------------------------------------------------
    def get_system_statistics(self) -> Dict[str, Any]:
        """Combine statistics from both managers."""
        stats = self.base_manager.get_system_statistics()
        enhanced_stats = self.enhanced_manager.get_statistics()
        stats["enhanced"] = enhanced_stats
        return stats
