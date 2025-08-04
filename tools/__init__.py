from typing import List, Dict, Any, Optional, Tuple

"""
Enhanced BASED GOD CLI Tools Package
Modular tool architecture inspired by Agent Zero
"""

from .base_tool import BaseTool, ToolResponse
from .memory_tool import MemoryTool
from .llm_query_tool import LLMQueryTool
from .reasoning_engine import FastReasoningEngine
from .tool_manager import ToolManager
from .fim_completion_tool import FIMCompletionTool
from .prefix_completion_tool import PrefixCompletionTool
from .unified_agent_system import UnifiedAgentSystem, EnhancedContact, EnhancedMemory
from .vector_database_tool import VectorDatabaseTool
from .sql_database_tool import SQLDatabaseTool
from .rag_pipeline_tool import RAGPipelineTool
from .simple_embedding_tool import SimpleEmbeddingTool
from .deepseek_coder_tool import DeepSeekCoderTool

# Enhanced tools (new)
from .enhanced_tool_integration import EnhancedToolManager, ToolDefinition, ToolType
from .json_mode_support import JSONModeManager, JSONModeLLMIntegration, CommonSchemas
from .prompt_caching_system import PromptCache, CachedLLMClient, CacheStrategy
from .sub_agent_architecture import SubAgentSystem, AgentType, TaskPriority

__all__ = [
    'BaseTool',
    'ToolResponse', 
    'MemoryTool',
    'LLMQueryTool',
    'FastReasoningEngine',
    'ToolManager',
    'FIMCompletionTool',
    'PrefixCompletionTool',
    'UnifiedAgentSystem',
    'EnhancedContact',
    'EnhancedMemory',
    'VectorDatabaseTool',
    'SQLDatabaseTool',
    'RAGPipelineTool',
    'SimpleEmbeddingTool',
    'DeepSeekCoderTool',
    
    # Enhanced tools
    'EnhancedToolManager',
    'ToolDefinition', 
    'ToolType',
    'JSONModeManager',
    'JSONModeLLMIntegration',
    'CommonSchemas',
    'PromptCache',
    'CachedLLMClient',
    'CacheStrategy',
    'SubAgentSystem',
    'AgentType',
    'TaskPriority'
]