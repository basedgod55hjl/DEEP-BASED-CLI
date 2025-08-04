#!/usr/bin/env python3
"""
🚀 Enhanced BASED CODER CLI - Anthropic Cookbook Integration
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
from tools.enhanced_tool_integration import EnhancedToolManager, ToolDefinition, ToolType
from tools.json_mode_support import JSONModeManager, JSONModeLLMIntegration, CommonSchemas
from tools.prompt_caching_system import PromptCache, CachedLLMClient, CacheStrategy
from tools.sub_agent_architecture import SubAgentSystem, AgentType, TaskPriority

# Import existing tools
from config import get_config, validate_deepseek_key, validate_huggingface_token
from tools.unified_agent_system import UnifiedAgentSystem
from tools.simple_embedding_tool import SimpleEmbeddingTool
from tools.sql_database_tool import SQLDatabaseTool
from tools.llm_query_tool import LLMQueryTool
from tools.fim_completion_tool import FIMCompletionTool
from tools.prefix_completion_tool import PrefixCompletionTool
from tools.rag_pipeline_tool import RAGPipelineTool
from tools.reasoning_engine import FastReasoningEngine as ReasoningEngine
from tools.memory_tool import MemoryTool
from tools.vector_database_tool import VectorDatabaseTool
from tools.deepseek_coder_tool import DeepSeekCoderTool
from tools.tool_manager import ToolManager

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
        self.console = Console()
        
        # Initialize enhanced systems
        self.enhanced_tool_manager = None
        self.json_mode_manager = None
        self.cached_llm_client = None
        self.sub_agent_system = None
        
        # Initialize existing systems
        self.unified_agent = None
        self.embedding_tool = None
        self.sql_tool = None
        self.llm_tool = None
        self.fim_tool = None
        self.prefix_tool = None
        self.rag_tool = None
        self.reasoning_engine = None
        self.memory_tool = None
        self.vector_tool = None
        self.coder_tool = None
        self.tool_manager = None
        
        # System status
        self.system_initialized = False
        self.enhanced_features_enabled = False
    
    async def initialize_system(self):
        """Initialize all systems with enhanced features"""
        try:
            console.print("[bold blue]🚀 Initializing Enhanced BASED CODER CLI...[/bold blue]")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                
                # Initialize enhanced features
                task = progress.add_task("Initializing enhanced features...", total=4)
                
                # 1. Enhanced Tool Integration
                progress.update(task, description="Setting up enhanced tool integration...")
                self.enhanced_tool_manager = EnhancedToolManager()
                progress.advance(task)
                
                # 2. JSON Mode Support
                progress.update(task, description="Setting up JSON mode support...")
                self.json_mode_manager = JSONModeManager()
                self._register_json_schemas()
                progress.advance(task)
                
                # 3. Prompt Caching System
                progress.update(task, description="Setting up prompt caching system...")
                cache_config = {
                    "max_size_mb": 100,
                    "strategy": CacheStrategy.HYBRID,
                    "default_ttl_hours": 24
                }
                self.cached_llm_client = CachedLLMClient(None, cache_config)  # Will be set later
                progress.advance(task)
                
                # 4. Sub-Agent Architecture
                progress.update(task, description="Setting up sub-agent architecture...")
                self.sub_agent_system = SubAgentSystem(None, None)  # Will be set later
                progress.advance(task)
                
                # Initialize existing systems
                task = progress.add_task("Initializing existing systems...", total=8)
                
                # Initialize existing tools
                progress.update(task, description="Initializing unified agent system...")
                self.unified_agent = UnifiedAgentSystem()
                progress.advance(task)
                
                progress.update(task, description="Initializing embedding tool...")
                self.embedding_tool = SimpleEmbeddingTool()
                progress.advance(task)
                
                progress.update(task, description="Initializing SQL database tool...")
                self.sql_tool = SQLDatabaseTool()
                progress.advance(task)
                
                progress.update(task, description="Initializing LLM query tool...")
                self.llm_tool = LLMQueryTool()
                progress.advance(task)
                
                progress.update(task, description="Initializing FIM completion tool...")
                self.fim_tool = FIMCompletionTool()
                progress.advance(task)
                
                progress.update(task, description="Initializing prefix completion tool...")
                self.prefix_tool = PrefixCompletionTool()
                progress.advance(task)
                
                progress.update(task, description="Initializing RAG pipeline tool...")
                self.rag_tool = RAGPipelineTool()
                progress.advance(task)
                
                progress.update(task, description="Initializing reasoning engine...")
                self.reasoning_engine = ReasoningEngine()
                progress.advance(task)
                
                # Initialize remaining tools
                task = progress.add_task("Initializing remaining tools...", total=3)
                
                progress.update(task, description="Initializing memory tool...")
                self.memory_tool = MemoryTool()
                progress.advance(task)
                
                progress.update(task, description="Initializing vector database tool...")
                self.vector_tool = VectorDatabaseTool()
                progress.advance(task)
                
                progress.update(task, description="Initializing tool manager...")
                self.tool_manager = ToolManager()
                progress.advance(task)
                
                # Set up enhanced system connections
                task = progress.add_task("Setting up enhanced system connections...", total=2)
                
                progress.update(task, description="Connecting cached LLM client...")
                self.cached_llm_client.llm_client = self.llm_tool
                progress.advance(task)
                
                progress.update(task, description="Connecting sub-agent system...")
                self.sub_agent_system.llm_client = self.llm_tool
                self.sub_agent_system.search_tool = self.rag_tool
                progress.advance(task)
            
            self.system_initialized = True
            self.enhanced_features_enabled = True
            
            console.print("[bold green]✅ Enhanced BASED CODER CLI initialized successfully![/bold green]")
            
        except Exception as e:
            console.print(f"[bold red]❌ Failed to initialize system: {e}[/bold red]")
            logger.error(f"System initialization failed: {e}")
            raise
    
    def _register_json_schemas(self):
        """Register common JSON schemas"""
        schemas = [
            ("code_analysis", CommonSchemas.get_code_analysis_schema()),
            ("search_results", CommonSchemas.get_search_results_schema()),
            ("code_generation", CommonSchemas.get_code_generation_schema())
        ]
        
        for name, schema in schemas:
            self.json_mode_manager.register_schema(name, schema)
    
    def print_enhanced_banner(self):
        """Print enhanced banner with new features"""
        banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  🚀 ENHANCED BASED CODER CLI - Anthropic Cookbook Integration              ║
║                                                                              ║
║  ✨ Enhanced Tool Integration    🔧 JSON Mode Support                       ║
║  🧠 Prompt Caching System       🤖 Sub-Agent Architecture                  ║
║  🔍 Advanced RAG Pipeline       📊 Performance Monitoring                  ║
║                                                                              ║
║  Made by @Lucariolucario55 on Telegram                                      ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """
        console.print(Panel(banner, style="bold blue"))
    
    def print_enhanced_help(self):
        """Print enhanced help menu"""
        help_text = """
[bold blue]Enhanced BASED CODER CLI Commands[/bold blue]

[bold green]Enhanced Features (New):[/bold green]
  /enhanced-tools          - Show enhanced tool integration status
  /json-mode <schema>      - Enable JSON mode with schema validation
  /cache-stats             - Show prompt caching statistics
  /sub-agents              - Show sub-agent system status
  /complex-task <desc>     - Execute complex task with sub-agents

[bold yellow]Existing Commands:[/bold yellow]
  /help                    - Show this help menu
  /status                  - Show system status
  /clear                   - Clear conversation history
  /chat <message>          - Chat with AI
  /code <prompt>           - Generate code
  /debug <code>            - Debug and fix code
  /search <query>          - Web search
  /rag <query>             - RAG pipeline query
  /reason <question>       - Reasoning engine
  /memory <operation>      - Memory operations

[bold cyan]Enhanced JSON Mode Examples:[/bold cyan]
  /json-mode code_analysis - Analyze code with structured JSON output
  /json-mode search_results - Search with structured results
  /json-mode code_generation - Generate code with metadata

[bold magenta]Sub-Agent Examples:[/bold magenta]
  /complex-task "Create a web scraper with analysis"
  /complex-task "Generate API with security review"
        """
        console.print(Panel(help_text, title="Enhanced Help", style="bold blue"))
    
    async def handle_enhanced_tools(self):
        """Handle enhanced tools command"""
        if not self.enhanced_features_enabled:
            console.print("[red]Enhanced features not enabled[/red]")
            return
        
        tools = self.enhanced_tool_manager.get_available_tools()
        stats = self.enhanced_tool_manager.get_statistics()
        
        table = Table(title="Enhanced Tools Status")
        table.add_column("Tool Name", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Description", style="green")
        table.add_column("Status", style="yellow")
        
        for tool in tools:
            table.add_row(
                tool["name"],
                tool.get("tool_type", "N/A"),
                tool["description"][:50] + "..." if len(tool["description"]) > 50 else tool["description"],
                "✅ Active"
            )
        
        console.print(table)
        
        # Show statistics
        stats_table = Table(title="Tool Usage Statistics")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="green")
        
        for key, value in stats.items():
            stats_table.add_row(key, str(value))
        
        console.print(stats_table)
    
    async def handle_json_mode(self, schema_name: str):
        """Handle JSON mode command"""
        if not self.enhanced_features_enabled:
            console.print("[red]Enhanced features not enabled[/red]")
            return
        
        if schema_name not in self.json_mode_manager.schemas:
            console.print(f"[red]Schema '{schema_name}' not found[/red]")
            console.print(f"Available schemas: {list(self.json_mode_manager.schemas.keys())}")
            return
        
        console.print(f"[green]JSON mode enabled with schema: {schema_name}[/green]")
        
        # Show schema information
        schema = self.json_mode_manager.schemas[schema_name]
        console.print(f"Description: {schema.description}")
        console.print(f"Required fields: {', '.join(schema.required_fields)}")
        console.print(f"Optional fields: {', '.join(schema.optional_fields)}")
    
    async def handle_cache_stats(self):
        """Handle cache statistics command"""
        if not self.enhanced_features_enabled:
            console.print("[red]Enhanced features not enabled[/red]")
            return
        
        stats = self.cached_llm_client.get_cache_stats()
        
        # Memory cache stats
        memory_stats = stats["memory_cache"]
        memory_table = Table(title="Memory Cache Statistics")
        memory_table.add_column("Metric", style="cyan")
        memory_table.add_column("Value", style="green")
        
        for key, value in memory_stats.items():
            memory_table.add_row(key, str(value))
        
        console.print(memory_table)
        
        # Database cache stats
        db_stats = stats["database_cache"]
        db_table = Table(title="Database Cache Statistics")
        db_table.add_column("Metric", style="cyan")
        db_table.add_column("Value", style="green")
        
        for key, value in db_stats.items():
            db_table.add_row(key, str(value))
        
        console.print(db_table)
    
    async def handle_sub_agents(self):
        """Handle sub-agents command"""
        if not self.enhanced_features_enabled:
            console.print("[red]Enhanced features not enabled[/red]")
            return
        
        status = self.sub_agent_system.get_system_status()
        
        # Coordinator status
        coordinator = status["coordinator"]
        coord_table = Table(title="Coordinator Agent Status")
        coord_table.add_column("Metric", style="cyan")
        coord_table.add_column("Value", style="green")
        
        for key, value in coordinator.items():
            coord_table.add_row(key, str(value))
        
        console.print(coord_table)
        
        # Sub-agents status
        sub_agents = status["sub_agents"]
        agents_table = Table(title="Sub-Agents Status")
        agents_table.add_column("Agent ID", style="cyan")
        agents_table.add_column("Type", style="magenta")
        agents_table.add_column("Status", style="yellow")
        agents_table.add_column("Success Rate", style="green")
        
        for agent_id, agent_status in sub_agents.items():
            agents_table.add_row(
                agent_id,
                agent_status["agent_type"],
                "🟢 Active" if not agent_status["is_busy"] else "🟡 Busy",
                f"{agent_status['performance_metrics']['success_rate']:.2%}"
            )
        
        console.print(agents_table)
    
    async def handle_complex_task(self, description: str):
        """Handle complex task command"""
        if not self.enhanced_features_enabled:
            console.print("[red]Enhanced features not enabled[/red]")
            return
        
        console.print(f"[bold blue]Executing complex task: {description}[/bold blue]")
        
        # Define subtasks based on description
        subtasks = [
            {
                "type": "code_generation",
                "description": f"Generate code for: {description}",
                "agent_type": "coder",
                "priority": 3,
                "input_data": {
                    "requirements": description,
                    "language": "python"
                }
            },
            {
                "type": "code_analysis",
                "description": "Analyze the generated code",
                "agent_type": "analyzer",
                "priority": 2,
                "input_data": {
                    "code": "{{code_generation.output}}",
                    "language": "python"
                },
                "dependencies": ["code_generation"]
            },
            {
                "type": "security_analysis",
                "description": "Perform security analysis",
                "agent_type": "analyzer",
                "priority": 2,
                "input_data": {
                    "code": "{{code_generation.output}}",
                    "language": "python"
                },
                "dependencies": ["code_generation"]
            }
        ]
        
        try:
            result = await self.sub_agent_system.execute_complex_task(description, subtasks)
            
            console.print("[bold green]✅ Complex task completed successfully![/bold green]")
            
            # Display results
            for subtask_id, subtask_result in result["subtask_results"].items():
                if subtask_result.success:
                    console.print(f"[green]✓ {subtask_id}: Success[/green]")
                    console.print(f"Output: {subtask_result.output[:200]}...")
                else:
                    console.print(f"[red]✗ {subtask_id}: Failed - {subtask_result.error_message}[/red]")
            
            console.print(f"Total execution time: {result['total_execution_time']:.2f}s")
            
        except Exception as e:
            console.print(f"[bold red]❌ Complex task failed: {e}[/bold red]")
    
    async def interactive_mode(self):
        """Enhanced interactive mode"""
        self.print_enhanced_banner()
        
        if not self.system_initialized:
            await self.initialize_system()
        
        console.print("[bold green]Enhanced BASED CODER CLI ready! Type /help for commands.[/bold green]")
        
        while True:
            try:
                user_input = Prompt.ask("\n[bold cyan]Enhanced BASED GOD CLI[/bold cyan]")
                
                if not user_input.strip():
                    continue
                
                # Handle enhanced commands
                if user_input.startswith("/enhanced-tools"):
                    await self.handle_enhanced_tools()
                
                elif user_input.startswith("/json-mode"):
                    parts = user_input.split(" ", 1)
                    if len(parts) > 1:
                        await self.handle_json_mode(parts[1])
                    else:
                        console.print("[red]Please specify a schema name[/red]")
                
                elif user_input.startswith("/cache-stats"):
                    await self.handle_cache_stats()
                
                elif user_input.startswith("/sub-agents"):
                    await self.handle_sub_agents()
                
                elif user_input.startswith("/complex-task"):
                    parts = user_input.split(" ", 1)
                    if len(parts) > 1:
                        await self.handle_complex_task(parts[1])
                    else:
                        console.print("[red]Please provide a task description[/red]")
                
                elif user_input == "/help":
                    self.print_enhanced_help()
                
                elif user_input == "/status":
                    await self.show_enhanced_status()
                
                elif user_input == "/exit":
                    console.print("[bold blue]Goodbye![/bold blue]")
                    break
                
                else:
                    # Handle existing commands (simplified for demo)
                    console.print(f"[yellow]Processing: {user_input}[/yellow]")
                    # Here you would integrate with existing command handlers
                
            except KeyboardInterrupt:
                console.print("\n[bold blue]Goodbye![/bold blue]")
                break
            except Exception as e:
                console.print(f"[bold red]Error: {e}[/bold red]")
                logger.error(f"Interactive mode error: {e}")
    
    async def show_enhanced_status(self):
        """Show enhanced system status"""
        status_table = Table(title="Enhanced BASED CODER CLI Status")
        status_table.add_column("Component", style="cyan")
        status_table.add_column("Status", style="green")
        status_table.add_column("Details", style="yellow")
        
        # System status
        status_table.add_row(
            "System Initialized",
            "✅ Yes" if self.system_initialized else "❌ No",
            "All systems ready" if self.system_initialized else "Systems not ready"
        )
        
        # Enhanced features
        status_table.add_row(
            "Enhanced Features",
            "✅ Enabled" if self.enhanced_features_enabled else "❌ Disabled",
            "Anthropic Cookbook upgrades active" if self.enhanced_features_enabled else "Standard mode"
        )
        
        # Individual components
        components = [
            ("Enhanced Tool Integration", self.enhanced_tool_manager),
            ("JSON Mode Support", self.json_mode_manager),
            ("Prompt Caching", self.cached_llm_client),
            ("Sub-Agent System", self.sub_agent_system),
            ("Unified Agent", self.unified_agent),
            ("LLM Tool", self.llm_tool),
            ("RAG Pipeline", self.rag_tool)
        ]
        
        for name, component in components:
            status = "✅ Active" if component else "❌ Inactive"
            details = "Ready" if component else "Not initialized"
            status_table.add_row(name, status, details)
        
        console.print(status_table)

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Enhanced BASED CODER CLI")
    parser.add_argument("--init", action="store_true", help="Initialize system only")
    parser.add_argument("--status", action="store_true", help="Show system status")
    parser.add_argument("--test", action="store_true", help="Run tests")
    
    args = parser.parse_args()
    
    cli = EnhancedBasedCoderCLI()
    
    try:
        if args.init:
            await cli.initialize_system()
            console.print("[bold green]System initialized successfully![/bold green]")
        
        elif args.status:
            await cli.initialize_system()
            await cli.show_enhanced_status()
        
        elif args.test:
            await cli.initialize_system()
            console.print("[bold blue]Running enhanced features test...[/bold blue]")
            
            # Test enhanced tools
            await cli.handle_enhanced_tools()
            
            # Test JSON mode
            await cli.handle_json_mode("code_analysis")
            
            # Test cache stats
            await cli.handle_cache_stats()
            
            # Test sub-agents
            await cli.handle_sub_agents()
            
            console.print("[bold green]All tests completed![/bold green]")
        
        else:
            await cli.interactive_mode()
    
    except Exception as e:
        console.print(f"[bold red]Fatal error: {e}[/bold red]")
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 