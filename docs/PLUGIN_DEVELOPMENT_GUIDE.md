# DEEP-CLI Plugin Development Guide

## Overview

DEEP-CLI supports a powerful plugin system that allows you to extend its functionality seamlessly. This guide will walk you through creating, developing, and deploying plugins for DEEP-CLI.

## Table of Contents

1. [Plugin Architecture](#plugin-architecture)
2. [Creating Your First Plugin](#creating-your-first-plugin)
3. [Plugin Structure](#plugin-structure)
4. [Advanced Plugin Features](#advanced-plugin-features)
5. [Testing and Debugging](#testing-and-debugging)
6. [Deployment and Distribution](#deployment-and-distribution)
7. [Best Practices](#best-practices)

## Plugin Architecture

### Core Components

DEEP-CLI plugins are built around these core concepts:

- **Tools**: Individual functionality units
- **Workflows**: Orchestrated sequences of tools
- **Agents**: Intelligent decision-making components
- **Hooks**: System integration points

### Plugin Lifecycle

1. **Discovery**: System finds and loads plugins
2. **Initialization**: Plugin sets up resources
3. **Registration**: Tools and workflows are registered
4. **Execution**: Plugin components are used
5. **Cleanup**: Resources are released

## Creating Your First Plugin

### Basic Plugin Template

```python
# my_plugin/__init__.py
from typing import List, Dict, Any
from deep_cli.core.plugin import BasePlugin
from deep_cli.core.tool import BaseTool
from deep_cli.core.workflow import BaseWorkflow

class MyPlugin(BasePlugin):
    """My first DEEP-CLI plugin"""
    
    def __init__(self):
        super().__init__(
            name="my_plugin",
            version="1.0.0",
            description="A sample plugin for DEEP-CLI"
        )
    
    def get_tools(self) -> List[BaseTool]:
        """Return list of tools provided by this plugin"""
        return [MyCustomTool()]
    
    def get_workflows(self) -> List[BaseWorkflow]:
        """Return list of workflows provided by this plugin"""
        return [MyCustomWorkflow()]
    
    async def initialize(self) -> None:
        """Initialize plugin resources"""
        print("My plugin initialized!")
    
    async def cleanup(self) -> None:
        """Clean up plugin resources"""
        print("My plugin cleaned up!")

# Plugin entry point
def create_plugin() -> MyPlugin:
    return MyPlugin()
```

### Custom Tool Implementation

```python
# my_plugin/tools/custom_tool.py
from deep_cli.core.tool import BaseTool
from deep_cli.core.response import ToolResponse

class MyCustomTool(BaseTool):
    """A custom tool for specific tasks"""
    
    def __init__(self):
        super().__init__(
            name="my_custom_tool",
            description="Performs custom operations",
            capabilities=["custom_operation", "data_processing"]
        )
    
    async def execute(self, params: Dict[str, Any]) -> ToolResponse:
        """Execute the tool with given parameters"""
        try:
            # Your custom logic here
            result = self._process_data(params.get("data", ""))
            
            return ToolResponse(
                success=True,
                data={"result": result},
                message="Custom operation completed successfully"
            )
        except Exception as e:
            return ToolResponse(
                success=False,
                error=str(e),
                message="Custom operation failed"
            )
    
    def _process_data(self, data: str) -> str:
        """Process the input data"""
        return f"Processed: {data.upper()}"
    
    def get_schema(self) -> Dict[str, Any]:
        """Return tool parameter schema"""
        return {
            "type": "object",
            "properties": {
                "data": {
                    "type": "string",
                    "description": "Input data to process"
                }
            },
            "required": ["data"]
        }
```

### Custom Workflow Implementation

```python
# my_plugin/workflows/custom_workflow.py
from deep_cli.core.workflow import BaseWorkflow
from deep_cli.core.response import WorkflowResponse

class MyCustomWorkflow(BaseWorkflow):
    """A custom workflow that orchestrates multiple tools"""
    
    def __init__(self):
        super().__init__(
            name="my_custom_workflow",
            description="Orchestrates custom operations",
            steps=[
                {"tool": "my_custom_tool", "params": {"data": "{{input.data}}"}},
                {"tool": "data_analyzer", "params": {"input": "{{previous.result}}"}}
            ]
        )
    
    async def execute(self, context: Dict[str, Any]) -> WorkflowResponse:
        """Execute the workflow"""
        try:
            results = []
            current_context = context.copy()
            
            for step in self.steps:
                tool_name = step["tool"]
                tool = self.get_tool(tool_name)
                
                # Resolve parameters
                params = self._resolve_params(step["params"], current_context)
                
                # Execute tool
                result = await tool.execute(params)
                results.append(result)
                
                # Update context
                current_context[f"{tool_name}_result"] = result.data
            
            return WorkflowResponse(
                success=True,
                data={"results": results},
                message="Workflow completed successfully"
            )
        except Exception as e:
            return WorkflowResponse(
                success=False,
                error=str(e),
                message="Workflow execution failed"
            )
```

## Plugin Structure

### Recommended Directory Structure

```
my_plugin/
├── __init__.py              # Plugin entry point
├── manifest.json            # Plugin metadata
├── requirements.txt         # Dependencies
├── README.md               # Documentation
├── tools/                  # Tool implementations
│   ├── __init__.py
│   ├── custom_tool.py
│   └── another_tool.py
├── workflows/              # Workflow implementations
│   ├── __init__.py
│   └── custom_workflow.py
├── agents/                 # Agent implementations
│   ├── __init__.py
│   └── custom_agent.py
├── hooks/                  # System hooks
│   ├── __init__.py
│   └── event_hooks.py
├── config/                 # Configuration files
│   └── settings.json
├── tests/                  # Test files
│   ├── __init__.py
│   ├── test_tools.py
│   └── test_workflows.py
└── examples/               # Usage examples
    └── basic_usage.py
```

### Manifest File

```json
{
  "name": "my_plugin",
  "version": "1.0.0",
  "description": "A comprehensive plugin for DEEP-CLI",
  "author": "Your Name",
  "email": "your.email@example.com",
  "license": "MIT",
  "repository": "https://github.com/yourusername/my_plugin",
  "keywords": ["deep-cli", "plugin", "automation"],
  "dependencies": {
    "python": ">=3.8",
    "packages": [
      "requests>=2.25.0",
      "pandas>=1.3.0"
    ]
  },
  "tools": [
    "tools.custom_tool.MyCustomTool",
    "tools.another_tool.AnotherTool"
  ],
  "workflows": [
    "workflows.custom_workflow.MyCustomWorkflow"
  ],
  "agents": [
    "agents.custom_agent.MyCustomAgent"
  ],
  "hooks": [
    "hooks.event_hooks.MyEventHooks"
  ],
  "config_schema": {
    "api_key": {
      "type": "string",
      "description": "API key for external service",
      "required": true
    },
    "timeout": {
      "type": "integer",
      "description": "Request timeout in seconds",
      "default": 30
    }
  }
}
```

## Advanced Plugin Features

### Configuration Management

```python
# my_plugin/config/manager.py
from deep_cli.core.config import ConfigManager

class PluginConfigManager:
    """Manages plugin-specific configuration"""
    
    def __init__(self, plugin_name: str):
        self.config_manager = ConfigManager()
        self.plugin_name = plugin_name
    
    def get_config(self, key: str, default=None):
        """Get configuration value"""
        return self.config_manager.get(f"{self.plugin_name}.{key}", default)
    
    def set_config(self, key: str, value: Any):
        """Set configuration value"""
        self.config_manager.set(f"{self.plugin_name}.{key}", value)
    
    def validate_config(self) -> List[str]:
        """Validate configuration and return errors"""
        errors = []
        
        api_key = self.get_config("api_key")
        if not api_key:
            errors.append("API key is required")
        
        timeout = self.get_config("timeout", 30)
        if not isinstance(timeout, int) or timeout <= 0:
            errors.append("Timeout must be a positive integer")
        
        return errors
```

### Event Hooks

```python
# my_plugin/hooks/event_hooks.py
from deep_cli.core.hooks import BaseHooks
from deep_cli.core.events import EventType

class MyEventHooks(BaseHooks):
    """Plugin event hooks for system integration"""
    
    async def on_tool_execution_start(self, tool_name: str, params: Dict[str, Any]):
        """Called when a tool execution starts"""
        print(f"Tool {tool_name} execution started with params: {params}")
    
    async def on_tool_execution_complete(self, tool_name: str, result: Any):
        """Called when a tool execution completes"""
        print(f"Tool {tool_name} execution completed with result: {result}")
    
    async def on_workflow_start(self, workflow_name: str, context: Dict[str, Any]):
        """Called when a workflow starts"""
        print(f"Workflow {workflow_name} started with context: {context}")
    
    async def on_error(self, error: Exception, context: Dict[str, Any]):
        """Called when an error occurs"""
        print(f"Error occurred: {error} in context: {context}")
```

### Custom Agent

```python
# my_plugin/agents/custom_agent.py
from deep_cli.core.agent import BaseAgent
from deep_cli.core.response import AgentResponse

class MyCustomAgent(BaseAgent):
    """A custom agent with specialized decision-making"""
    
    def __init__(self):
        super().__init__(
            name="my_custom_agent",
            description="Specialized agent for custom tasks",
            capabilities=["decision_making", "task_planning"]
        )
    
    async def process_request(self, request: Dict[str, Any]) -> AgentResponse:
        """Process a user request and determine actions"""
        try:
            # Analyze the request
            intent = self._analyze_intent(request)
            
            # Plan actions
            actions = self._plan_actions(intent, request)
            
            # Execute actions
            results = await self._execute_actions(actions)
            
            return AgentResponse(
                success=True,
                data={"intent": intent, "actions": actions, "results": results},
                message="Request processed successfully"
            )
        except Exception as e:
            return AgentResponse(
                success=False,
                error=str(e),
                message="Failed to process request"
            )
    
    def _analyze_intent(self, request: Dict[str, Any]) -> str:
        """Analyze the intent of the request"""
        # Your intent analysis logic here
        return "custom_operation"
    
    def _plan_actions(self, intent: str, request: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Plan actions based on intent"""
        # Your action planning logic here
        return [
            {"tool": "my_custom_tool", "params": {"data": request.get("data", "")}}
        ]
    
    async def _execute_actions(self, actions: List[Dict[str, Any]]) -> List[Any]:
        """Execute planned actions"""
        results = []
        for action in actions:
            tool_name = action["tool"]
            tool = self.get_tool(tool_name)
            result = await tool.execute(action["params"])
            results.append(result)
        return results
```

## Testing and Debugging

### Unit Tests

```python
# my_plugin/tests/test_tools.py
import pytest
from unittest.mock import Mock, patch
from my_plugin.tools.custom_tool import MyCustomTool

class TestMyCustomTool:
    """Test cases for MyCustomTool"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.tool = MyCustomTool()
    
    def test_tool_initialization(self):
        """Test tool initialization"""
        assert self.tool.name == "my_custom_tool"
        assert "custom_operation" in self.tool.capabilities
    
    @pytest.mark.asyncio
    async def test_tool_execution_success(self):
        """Test successful tool execution"""
        params = {"data": "test data"}
        result = await self.tool.execute(params)
        
        assert result.success is True
        assert "Processed: TEST DATA" in result.data["result"]
    
    @pytest.mark.asyncio
    async def test_tool_execution_failure(self):
        """Test tool execution failure"""
        params = {"data": None}
        result = await self.tool.execute(params)
        
        assert result.success is False
        assert "error" in result.__dict__
```

### Integration Tests

```python
# my_plugin/tests/test_integration.py
import pytest
from deep_cli.core.plugin_manager import PluginManager
from my_plugin import create_plugin

class TestPluginIntegration:
    """Integration tests for the plugin"""
    
    @pytest.fixture
    async def plugin_manager(self):
        """Create plugin manager for testing"""
        manager = PluginManager()
        plugin = create_plugin()
        await manager.load_plugin(plugin)
        return manager
    
    @pytest.mark.asyncio
    async def test_plugin_loading(self, plugin_manager):
        """Test plugin loading and initialization"""
        assert "my_plugin" in plugin_manager.get_loaded_plugins()
        
        plugin = plugin_manager.get_plugin("my_plugin")
        assert plugin.name == "my_plugin"
        assert plugin.version == "1.0.0"
    
    @pytest.mark.asyncio
    async def test_tool_registration(self, plugin_manager):
        """Test tool registration"""
        tools = plugin_manager.get_tools()
        tool_names = [tool.name for tool in tools]
        
        assert "my_custom_tool" in tool_names
    
    @pytest.mark.asyncio
    async def test_workflow_execution(self, plugin_manager):
        """Test workflow execution"""
        workflow = plugin_manager.get_workflow("my_custom_workflow")
        context = {"input": {"data": "test data"}}
        
        result = await workflow.execute(context)
        assert result.success is True
```

### Debugging Tools

```python
# my_plugin/debug/debugger.py
import logging
from deep_cli.core.debug import Debugger

class PluginDebugger(Debugger):
    """Debugging utilities for plugins"""
    
    def __init__(self, plugin_name: str):
        super().__init__()
        self.plugin_name = plugin_name
        self.logger = logging.getLogger(f"plugin.{plugin_name}")
    
    def log_tool_execution(self, tool_name: str, params: Dict[str, Any], result: Any):
        """Log tool execution details"""
        self.logger.info(f"Tool {tool_name} executed with params: {params}")
        self.logger.info(f"Tool {tool_name} returned: {result}")
    
    def log_workflow_execution(self, workflow_name: str, context: Dict[str, Any], result: Any):
        """Log workflow execution details"""
        self.logger.info(f"Workflow {workflow_name} executed with context: {context}")
        self.logger.info(f"Workflow {workflow_name} returned: {result}")
    
    def log_error(self, error: Exception, context: Dict[str, Any]):
        """Log error details"""
        self.logger.error(f"Error in {self.plugin_name}: {error}")
        self.logger.error(f"Context: {context}")
```

## Deployment and Distribution

### Package Structure

```python
# setup.py
from setuptools import setup, find_packages

setup(
    name="deep-cli-my-plugin",
    version="1.0.0",
    description="A comprehensive plugin for DEEP-CLI",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/my_plugin",
    packages=find_packages(),
    install_requires=[
        "deep-cli>=1.0.0",
        "requests>=2.25.0",
        "pandas>=1.3.0"
    ],
    entry_points={
        "deep_cli.plugins": [
            "my_plugin = my_plugin:create_plugin"
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
)
```

### Installation Instructions

```markdown
# Installation

## From PyPI
```bash
pip install deep-cli-my-plugin
```

## From Source
```bash
git clone https://github.com/yourusername/my_plugin.git
cd my_plugin
pip install -e .
```

## Configuration
1. Set your API key:
```bash
deep-cli config set my_plugin.api_key YOUR_API_KEY
```

2. Verify installation:
```bash
deep-cli plugin list
```
```

## Best Practices

### Code Organization

1. **Separation of Concerns**: Keep tools, workflows, and agents separate
2. **Configuration Management**: Use proper configuration management
3. **Error Handling**: Implement comprehensive error handling
4. **Logging**: Use structured logging for debugging
5. **Testing**: Write comprehensive tests

### Performance Considerations

1. **Async Operations**: Use async/await for I/O operations
2. **Resource Management**: Properly manage resources and cleanup
3. **Caching**: Implement caching where appropriate
4. **Batch Processing**: Process data in batches for large datasets

### Security Guidelines

1. **Input Validation**: Validate all inputs
2. **API Key Management**: Secure API key storage
3. **Error Information**: Don't expose sensitive information in errors
4. **Rate Limiting**: Implement rate limiting for external APIs

### Documentation Standards

1. **Docstrings**: Use comprehensive docstrings
2. **Type Hints**: Use type hints throughout
3. **Examples**: Provide usage examples
4. **README**: Maintain up-to-date README

### Version Management

1. **Semantic Versioning**: Follow semantic versioning
2. **Changelog**: Maintain a changelog
3. **Backward Compatibility**: Maintain backward compatibility
4. **Migration Guides**: Provide migration guides for breaking changes

## Troubleshooting

### Common Issues

1. **Plugin Not Loading**: Check manifest.json and entry points
2. **Tool Not Found**: Verify tool registration
3. **Configuration Errors**: Validate configuration schema
4. **Import Errors**: Check dependencies and imports

### Debug Commands

```bash
# List loaded plugins
deep-cli plugin list

# Show plugin details
deep-cli plugin info my_plugin

# Test plugin
deep-cli plugin test my_plugin

# Debug mode
deep-cli --debug plugin load my_plugin
```

## Support and Community

- **Documentation**: [Plugin Development Docs](https://docs.deep-cli.dev/plugins)
- **Examples**: [Plugin Examples Repository](https://github.com/deep-cli/plugin-examples)
- **Discussions**: [GitHub Discussions](https://github.com/deep-cli/deep-cli/discussions)
- **Issues**: [GitHub Issues](https://github.com/deep-cli/deep-cli/issues)

---

*This guide is maintained by the DEEP-CLI team. For questions or contributions, please visit our [GitHub repository](https://github.com/deep-cli/deep-cli).* 