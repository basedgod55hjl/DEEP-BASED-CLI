#!/usr/bin/env python3
"""
🚀 Enhanced BASED GOD CLI - Anthropic Cookbook Integration
Made by @Lucariolucario55 on Telegram

Enhanced CLI with Anthropic Cookbook-inspired features:
- Enhanced Tool Integration
- JSON Mode Support
- Prompt Caching System
- Sub-Agent Architecture
- Advanced RAG Implementation
"""

import asyncio
import logging
import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import argparse
import colorama
from colorama import Fore, Back, Style
import rich
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.layout import Layout
from rich.live import Live
import numpy as np
from dotenv import load_dotenv

# Initialize colorama for Windows compatibility
colorama.init()

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

# Import enhanced tools and systems
from tools.json_mode_support import JSONModeManager, JSONModeLLMIntegration, CommonSchemas
from tools.prompt_caching_system import PromptCache, CachedLLMClient, CacheStrategy
from tools.sub_agent_architecture import SubAgentSystem, AgentType, TaskPriority

# Import existing tools
from config import get_config, validate_deepseek_key, validate_huggingface_token
from tools.unified_agent_system import UnifiedAgentSystem
from tools.simple_embedding_tool import SimpleEmbeddingTool
from tools.qwen_embedding_tool import QwenEmbeddingTool
from tools.sql_database_tool import SQLDatabaseTool
from tools.llm_query_tool import LLMQueryTool
from tools.fim_completion_tool import FIMCompletionTool
from tools.prefix_completion_tool import PrefixCompletionTool
from tools.rag_pipeline_tool import RAGPipelineTool
from tools.reasoning_engine import FastReasoningEngine as ReasoningEngine
from tools.memory_tool import MemoryTool
from tools.json_memory_tool import JSONMemoryTool
from tools.vector_database_tool import VectorDatabaseTool
from tools.deepseek_coder_tool import DeepSeekCoderTool
from tools.unified_tool_manager import UnifiedToolManager

# Set up rich console
console = Console()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/enhanced_deepcli.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnhancedBasedCoderCLI:
    """Enhanced BASED CODER CLI with Anthropic Cookbook features"""
    
    def __init__(self):
        self.config = get_config()
        self.console = console
        self.is_initialized = False
        
        # Core systems
        self.tool_manager = None
        self.llm_tool = None
        self.memory_tool = None
        self.json_memory_tool = None
        self.sql_tool = None
        self.rag_tool = None
        self.reasoning_engine = None
        self.fim_tool = None
        self.prefix_tool = None
        self.unified_agent = None
        self.embedding_tool = None
        self.qwen_embedding_tool = None
        self.vector_tool = None
        self.coder_tool = None

        # Enhanced systems
        self.json_mode_manager = None
        self.prompt_cache = None
        self.sub_agent_system = None
        
        # Performance tracking
        self.start_time = datetime.now()
        self.command_history = []
        
    async def initialize_system(self):
        """Initialize all systems progressively"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            
            # Initialize core systems
            task1 = progress.add_task("Initializing core systems...", total=None)
            
            # Initialize LLM tool
            progress.update(task1, description="Initializing LLM tool...")
            self.llm_tool = LLMQueryTool()
            
            # Initialize memory tool
            progress.update(task1, description="Initializing memory tool...")
            self.memory_tool = MemoryTool()
            
            # Initialize SQL database tool
            progress.update(task1, description="Initializing SQL database tool...")
            self.sql_tool = SQLDatabaseTool()
            
            # Initialize embedding tools
            progress.update(task1, description="Initializing simple embedding tool...")
            self.embedding_tool = SimpleEmbeddingTool()
            
            progress.update(task1, description="Initializing Qwen embedding tool...")
            self.qwen_embedding_tool = QwenEmbeddingTool()
            
            # Initialize memory tools
            progress.update(task1, description="Initializing JSON memory tool...")
            self.json_memory_tool = JSONMemoryTool()
            
            # Initialize FIM completion tool
            progress.update(task1, description="Initializing FIM completion tool...")
            self.fim_tool = FIMCompletionTool()
            
            # Initialize prefix completion tool
            progress.update(task1, description="Initializing prefix completion tool...")
            self.prefix_tool = PrefixCompletionTool()
            
            # Initialize reasoning engine
            progress.update(task1, description="Initializing reasoning engine...")
            self.reasoning_engine = ReasoningEngine(llm_tool=self.llm_tool)
            
            # Initialize unified agent system
            progress.update(task1, description="Initializing unified agent system...")
            self.unified_agent = UnifiedAgentSystem()
            
            # Initialize unified tool manager
            progress.update(task1, description="Initializing unified tool manager...")
            self.tool_manager = UnifiedToolManager()
            
            # Initialize optional tools
            task2 = progress.add_task("Setting up optional systems...", total=None)
            
            try:
                progress.update(task2, description="Initializing vector database tool...")
                self.vector_tool = VectorDatabaseTool()
            except Exception as e:
                logger.warning(f"Vector database tool not available: {e}")
                
            try:
                progress.update(task2, description="Initializing RAG pipeline tool...")
                self.rag_tool = RAGPipelineTool()
            except Exception as e:
                logger.warning(f"RAG pipeline tool not available: {e}")
                
            try:
                progress.update(task2, description="Initializing DeepSeek coder tool...")
                self.coder_tool = DeepSeekCoderTool()
            except Exception as e:
                logger.warning(f"DeepSeek coder tool not available: {e}")
            
            # Initialize enhanced systems
            task3 = progress.add_task("Setting up enhanced features...", total=None)

            try:
                progress.update(task3, description="Initializing JSON mode support...")
                self.json_mode_manager = JSONModeManager()
            except Exception as e:
                logger.warning(f"JSON mode support not available: {e}")
                
            try:
                progress.update(task3, description="Initializing prompt caching system...")
                self.prompt_cache = PromptCache()
            except Exception as e:
                logger.warning(f"Prompt caching system not available: {e}")
                
            try:
                progress.update(task3, description="Setting up sub-agent architecture...")
                self.sub_agent_system = SubAgentSystem(
                    llm_client=self.llm_tool,
                    search_tool=None  # Will be set up later if needed
                )
            except Exception as e:
                logger.warning(f"Sub-agent system not available: {e}")
            
            # Final initialization
            task4 = progress.add_task("Finalizing initialization...", total=None)
            progress.update(task4, description="Connecting sub-agent system...")
            
            self.is_initialized = True
            logger.info("✅ Enhanced BASED CODER CLI initialized successfully!")
    
    def print_banner(self):
        """Print enhanced banner"""
        banner_text = Text()
        banner_text.append("🚀 Enhanced BASED GOD CLI\n", style="bold cyan")
        banner_text.append("Anthropic Cookbook Integration\n", style="italic green")
        banner_text.append("Made by @Lucariolucario55 on Telegram\n", style="yellow")
        banner_text.append(f"Initialized: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}", style="dim")
        
        panel = Panel(
            banner_text,
            title="Enhanced AI Assistant",
            border_style="blue",
            padding=(1, 2)
        )
        self.console.print(panel)
    
    def show_status(self):
        """Show comprehensive system status"""
        table = Table(title="Enhanced BASED CODER CLI Status")
        table.add_column("Component", style="cyan", no_wrap=True)
        table.add_column("Status", style="green")
        table.add_column("Details", style="white")
        
        # Core systems
        table.add_row("System Initialized", "✅ Yes" if self.is_initialized else "❌ No", "All systems ready")
        table.add_row("Enhanced Features", "✅ Enabled", "Anthropic Cookbook upgrades active")
        table.add_row("Tool Manager", "✅ Active" if self.tool_manager else "❌ No", "Unified tool system")
        table.add_row("JSON Mode Support", "✅ Active" if self.json_mode_manager else "⚠️ Limited", "Ready" if self.json_mode_manager else "Not available")
        table.add_row("Prompt Caching", "✅ Active" if self.prompt_cache else "⚠️ Limited", "Ready" if self.prompt_cache else "Not available")
        table.add_row("Sub-Agent System", "✅ Active" if self.sub_agent_system else "⚠️ Limited", "Ready" if self.sub_agent_system else "Not available")
        table.add_row("Unified Agent", "✅ Active" if self.unified_agent else "❌ No", "Ready" if self.unified_agent else "Not available")
        table.add_row("LLM Tool", "✅ Active" if self.llm_tool else "❌ No", "Ready" if self.llm_tool else "Not available")
        table.add_row("Qwen Embedding", "✅ Active" if self.qwen_embedding_tool else "⚠️ Limited", "Ready" if self.qwen_embedding_tool else "Not available")
        table.add_row("JSON Memory", "✅ Active" if self.json_memory_tool else "⚠️ Limited", "Ready" if self.json_memory_tool else "Not available")
        table.add_row("RAG Pipeline", "✅ Active" if self.rag_tool else "⚠️ Limited", "Ready" if self.rag_tool else "Not available")
        
        self.console.print(table)
    
    def show_help(self):
        """Show enhanced help"""
        help_text = """
🚀 Enhanced BASED GOD CLI Commands:

Core Commands:
  /help              - Show this help message
  /status            - Show system status
  /chat <message>    - Start a conversation
  /exit              - Exit the CLI

Enhanced Features:
  /tools             - List available tools
  /json-mode <task>  - Use JSON mode for structured output
  /cache-stats       - Show prompt cache statistics
  /sub-agents        - Show sub-agent system status
  /complex-task      - Execute complex multi-agent task
  /qwen-embed        - Use Qwen for embeddings
  /json-memory       - JSON memory operations

Code Operations:
  /generate <desc>   - Generate code from description
  /debug <code>      - Debug code issues
  /heal <code>       - Self-heal code problems
  /fim <prefix> <suffix> - Fill-in-middle completion
  /prefix <text>     - Prefix completion
  /analyze <code>    - Analyze code quality

AI Operations:
  /rag <query>       - RAG-powered query
  /reason <question> - Advanced reasoning
  /search <query>    - Web search
  /scrape <url>      - Web scraping
  /execute <code>    - Execute code safely

Memory Operations:
  /store <content>   - Store in memory
  /recall <query>    - Recall from memory
  /history           - Show command history
  /clear             - Clear history

Setup & Configuration:
  /setup             - Initial setup wizard
  /config            - Show configuration
  /validate          - Validate system
        """
        
        panel = Panel(help_text, title="Enhanced BASED GOD CLI Help", border_style="green")
        self.console.print(panel)
    
    async def handle_chat(self, message: str):
        """Handle chat interactions"""
        if not self.is_initialized:
            return "❌ System not initialized. Please run /setup first."
        
        try:
            # Use unified agent for chat
            if self.unified_agent:
                response = await self.unified_agent.execute(
                    operation="conversation",
                    user_message=message
                )
                return response.data.get("response", "No response generated")
            else:
                # Fallback to LLM tool
                response = await self.llm_tool.execute(
                    operation="chat_completion",
                    messages=[{"role": "user", "content": message}]
                )
                return response.data.get("content", "No response generated")
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return f"❌ Error: {str(e)}"
    
    async def handle_tools(self):
        """Display all available tools from the unified manager."""
        if not self.tool_manager:
            return "❌ Tool manager not available"

        tools = self.tool_manager.list_tools()

        table = Table(title="Available Tools")
        table.add_column("Tool", style="cyan")
        table.add_column("Description", style="white")

        for tool in tools:
            table.add_row(tool["name"], tool["description"])

        self.console.print(table)
        return "Tools ready for use"
    
    async def handle_json_mode(self, task: str):
        """Handle JSON mode operations"""
        if not self.json_mode_manager:
            return "❌ JSON mode support not available"
        
        try:
            # Use JSON mode for structured output
            schemas = self.json_mode_manager.get_available_schemas()
            
            table = Table(title="Available JSON Schemas")
            table.add_column("Schema", style="cyan")
            table.add_column("Description", style="white")
            
            for schema_name in schemas:
                schema = self.json_mode_manager.get_schema(schema_name)
                table.add_row(schema_name, schema.description)
            
            self.console.print(table)
            return f"JSON mode ready for task: {task}"
        except Exception as e:
            return f"❌ JSON mode error: {str(e)}"
    
    async def handle_cache_stats(self):
        """Show cache statistics"""
        if not self.prompt_cache:
            return "❌ Prompt caching not available"
        
        try:
            stats = self.prompt_cache.get_statistics()
            
            table = Table(title="Prompt Cache Statistics")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            
            for key, value in stats.items():
                table.add_row(key, str(value))
            
            self.console.print(table)
            return "Cache statistics displayed"
        except Exception as e:
            return f"❌ Cache stats error: {str(e)}"
    
    async def handle_sub_agents(self):
        """Show sub-agent system status"""
        if not self.sub_agent_system:
            return "❌ Sub-agent system not available"
        
        try:
            status = self.sub_agent_system.get_system_status()
            
            table = Table(title="Sub-Agent System Status")
            table.add_column("Agent", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Tasks", style="white")
            
            for agent_id, agent_status in status["agents"].items():
                table.add_row(
                    agent_id,
                    agent_status["status"],
                    str(agent_status["task_count"])
                )
            
            self.console.print(table)
            return "Sub-agent system status displayed"
        except Exception as e:
            return f"❌ Sub-agent error: {str(e)}"
    
    async def handle_complex_task(self, description: str):
        """Handle complex multi-agent tasks"""
        if not self.sub_agent_system:
            return "❌ Sub-agent system not available"
        
        try:
            result = await self.sub_agent_system.execute_complex_task(description)
            return f"✅ Complex task completed: {result}"
        except Exception as e:
            return f"❌ Complex task error: {str(e)}"
    
    async def handle_qwen_embedding(self, text: str):
        """Handle Qwen embedding operations"""
        if not self.qwen_embedding_tool:
            return "❌ Qwen embedding tool not available"
        
        try:
            response = await self.qwen_embedding_tool.embed_text(text)
            if response.success:
                embedding = response.data["embedding"]
                return f"✅ Qwen embedding generated. Dimension: {len(embedding)}"
            else:
                return f"❌ Qwen embedding failed: {response.message}"
        except Exception as e:
            return f"❌ Qwen embedding error: {str(e)}"
    
    async def handle_json_memory(self, operation: str, **kwargs):
        """Handle JSON memory operations"""
        if not self.json_memory_tool:
            return "❌ JSON memory tool not available"
        
        try:
            if operation == "store":
                content = kwargs.get("content", "")
                category = kwargs.get("category", "general")
                tags = kwargs.get("tags", [])
                importance = kwargs.get("importance", 1.0)
                
                response = await self.json_memory_tool.store(
                    content=content,
                    category=category,
                    tags=tags,
                    importance=importance
                )
                
                if response.success:
                    return f"✅ Memory stored. ID: {response.data['entry_id']}"
                else:
                    return f"❌ Memory storage failed: {response.message}"
                    
            elif operation == "search":
                query = kwargs.get("query", "")
                category = kwargs.get("category")
                tags = kwargs.get("tags", [])
                limit = kwargs.get("limit", 5)
                
                response = await self.json_memory_tool.search(
                    query=query,
                    category=category,
                    tags=tags,
                    limit=limit
                )
                
                if response.success:
                    results = response.data["results"]
                    return f"✅ Found {len(results)} memory entries"
                else:
                    return f"❌ Memory search failed: {response.message}"
                    
            elif operation == "analytics":
                response = await self.json_memory_tool.get_analytics()
                
                if response.success:
                    analytics = response.data
                    return f"✅ Memory analytics: {analytics['total_entries']} total entries"
                else:
                    return f"❌ Memory analytics failed: {response.message}"
                    
            else:
                return f"❌ Unknown JSON memory operation: {operation}"
                
        except Exception as e:
            return f"❌ JSON memory error: {str(e)}"
    
    async def interactive_mode(self):
        """Enhanced interactive mode"""
        await self.initialize_system()
        self.print_banner()
        self.show_help()
        
        while True:
            try:
                user_input = Prompt.ask("\n[bold cyan]Enhanced BASED GOD CLI[/bold cyan]")
                
                if not user_input.strip():
                    continue
                
                if user_input.lower() in ['exit', 'quit', '/exit', '/quit']:
                    self.console.print("👋 Goodbye!")
                    break
                
                if user_input.startswith('/'):
                    # Handle commands
                    parts = user_input[1:].split(' ', 1)
                    command = parts[0].lower()
                    args = parts[1] if len(parts) > 1 else ""
                    
                    if command == 'help':
                        self.show_help()
                    elif command == 'status':
                        self.show_status()
                    elif command == 'chat':
                        response = await self.handle_chat(args)
                        self.console.print(f"🤖 {response}")
                    elif command == 'tools':
                        response = await self.handle_tools()
                        self.console.print(response)
                    elif command == 'json-mode':
                        response = await self.handle_json_mode(args)
                        self.console.print(response)
                    elif command == 'cache-stats':
                        response = await self.handle_cache_stats()
                        self.console.print(response)
                    elif command == 'sub-agents':
                        response = await self.handle_sub_agents()
                        self.console.print(response)
                    elif command == 'complex-task':
                        response = await self.handle_complex_task(args)
                        self.console.print(response)
                    elif command == 'qwen-embed':
                        response = await self.handle_qwen_embedding(args)
                        self.console.print(response)
                    elif command == 'json-memory':
                        # Parse JSON memory command: /json-memory store "content" category tags importance
                        # or /json-memory search "query" category tags limit
                        # or /json-memory analytics
                        parts = args.split(' ', 1) if args else ['analytics']
                        sub_op = parts[0]
                        
                        if sub_op == 'store' and len(parts) > 1:
                            # Parse store command
                            store_args = parts[1].split('"')
                            if len(store_args) >= 3:
                                content = store_args[1]
                                remaining = store_args[2].strip().split()
                                category = remaining[0] if remaining else "general"
                                tags = remaining[1].split(',') if len(remaining) > 1 else []
                                importance = float(remaining[2]) if len(remaining) > 2 else 1.0
                                
                                response = await self.handle_json_memory("store", content=content, category=category, tags=tags, importance=importance)
                                self.console.print(response)
                            else:
                                self.console.print("❌ Invalid store format. Use: /json-memory store \"content\" category tags importance")
                        elif sub_op == 'search' and len(parts) > 1:
                            # Parse search command
                            search_args = parts[1].split('"')
                            if len(search_args) >= 3:
                                query = search_args[1]
                                remaining = search_args[2].strip().split()
                                category = remaining[0] if remaining else None
                                tags = remaining[1].split(',') if len(remaining) > 1 else []
                                limit = int(remaining[2]) if len(remaining) > 2 else 5
                                
                                response = await self.handle_json_memory("search", query=query, category=category, tags=tags, limit=limit)
                                self.console.print(response)
                            else:
                                self.console.print("❌ Invalid search format. Use: /json-memory search \"query\" category tags limit")
                        elif sub_op == 'analytics':
                            response = await self.handle_json_memory("analytics")
                            self.console.print(response)
                        else:
                            self.console.print("❌ Invalid JSON memory command. Use: /json-memory [store|search|analytics]")
                    else:
                        self.console.print(f"❓ Unknown command: {command}. Type /help for available commands.")
                else:
                    # Treat as chat message
                    response = await self.handle_chat(user_input)
                    self.console.print(f"🤖 {response}")
                    
            except KeyboardInterrupt:
                self.console.print("\n👋 Goodbye!")
                break
            except Exception as e:
                logger.error(f"Interactive mode error: {e}")
                self.console.print(f"❌ Error: {str(e)}")

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Enhanced BASED GOD CLI")
    parser.add_argument("--status", action="store_true", help="Show system status")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--interactive", "-i", action="store_true", help="Start interactive mode")
    
    args = parser.parse_args()
    
    cli = EnhancedBasedCoderCLI()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if args.status:
        await cli.initialize_system()
        cli.show_status()
    elif args.interactive:
        await cli.interactive_mode()
    else:
        # Default to interactive mode
        await cli.interactive_mode()

if __name__ == "__main__":
    asyncio.run(main()) 