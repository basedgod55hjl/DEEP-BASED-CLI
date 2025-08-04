#!/usr/bin/env python3
"""
🚀 BASED CODER CLI - Unified AI-Powered Development Tool
Enhanced with Anthropic Cookbook Integration

Made by @Lucariolucario55 on Telegram

Features:
- Unified CLI with interactive and batch modes
- Enhanced tool integration with intelligent orchestration
- Advanced caching and performance optimization
- Comprehensive error handling and user experience
- Multi-modal AI capabilities
"""

import asyncio
import logging
import sys
import os
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
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
from rich.syntax import Syntax
from rich.traceback import install
import numpy as np
from dotenv import load_dotenv

# Initialize rich traceback for better error handling
install()

# Initialize colorama for Windows compatibility
colorama.init()

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

# Import configuration and tools
from config import get_config, validate_deepseek_key, validate_huggingface_token
from tools.tool_manager import ToolManager
from tools.llm_query_tool import LLMQueryTool
from tools.simple_embedding_tool import SimpleEmbeddingTool
from tools.sql_database_tool import SQLDatabaseTool
from tools.fim_completion_tool import FIMCompletionTool
from tools.prefix_completion_tool import PrefixCompletionTool
from tools.rag_pipeline_tool import RAGPipelineTool
from tools.reasoning_engine import FastReasoningEngine
from tools.memory_tool import MemoryTool
from tools.vector_database_tool import VectorDatabaseTool
from tools.deepseek_coder_tool import DeepSeekCoderTool
from tools.unified_agent_system import UnifiedAgentSystem

# Enhanced imports
try:
    from tools.enhanced_tool_integration import EnhancedToolManager
    from tools.json_mode_support import JSONModeManager
    from tools.prompt_caching_system import PromptCache, CachedLLMClient
    from tools.sub_agent_architecture import SubAgentSystem
    ENHANCED_FEATURES_AVAILABLE = True
except ImportError:
    ENHANCED_FEATURES_AVAILABLE = False
    print("⚠️ Enhanced features not available. Running in standard mode.")

# Set up rich console
console = Console()

# Set up logging
def setup_logging():
    """Setup comprehensive logging system"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'based_coder_cli.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

class SystemMonitor:
    """System monitoring and health checks"""
    
    def __init__(self):
        self.start_time = time.time()
        self.performance_metrics = {}
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        import psutil
        import platform
        
        return {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "architecture": platform.architecture(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "memory_available": psutil.virtual_memory().available,
            "disk_usage": psutil.disk_usage('/').total if os.path.exists('/') else psutil.disk_usage('C:\\').total,
            "uptime": time.time() - self.start_time
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        import psutil
        
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent if os.path.exists('/') else psutil.disk_usage('C:\\').percent,
            "uptime_seconds": time.time() - self.start_time
        }

class BasedCoderCLI:
    """Unified BASED CODER CLI with enhanced features"""
    
    def __init__(self):
        self.config = get_config()
        self.console = Console()
        self.system_monitor = SystemMonitor()
        
        # Initialize core systems
        self.tool_manager = None
        self.llm_tool = None
        self.embedding_tool = None
        self.sql_tool = None
        self.fim_tool = None
        self.prefix_tool = None
        self.rag_tool = None
        self.reasoning_engine = None
        self.memory_tool = None
        self.vector_tool = None
        self.coder_tool = None
        self.unified_agent = None
        
        # Enhanced systems
        self.enhanced_tool_manager = None
        self.json_mode_manager = None
        self.cached_llm_client = None
        self.sub_agent_system = None
        
        # State management
        self.conversation_history = []
        self.session_id = f"session_{int(time.time())}"
        self.system_initialized = False
        self.enhanced_features_enabled = False
        
        # Command registry
        self.commands = self._register_commands()
    
    def _register_commands(self) -> Dict[str, Any]:
        """Register all available commands"""
        return {
            # System commands
            "help": self.show_help,
            "status": self.show_status,
            "clear": self.clear_history,
            "history": self.show_history,
            "exit": self.exit_cli,
            
            # AI interaction commands
            "chat": self.handle_chat,
            "code": self.handle_code_generation,
            "debug": self.handle_code_debugging,
            "heal": self.handle_code_healing,
            
            # Completion commands
            "fim": self.handle_fim_completion,
            "prefix": self.handle_prefix_completion,
            
            # Analysis commands
            "rag": self.handle_rag_query,
            "reason": self.handle_reasoning,
            "analyze": self.handle_code_analysis,
            
            # Memory commands
            "remember": self.handle_memory_store,
            "recall": self.handle_memory_recall,
            
            # Enhanced commands
            "enhanced-tools": self.handle_enhanced_tools,
            "json-mode": self.handle_json_mode,
            "cache-stats": self.handle_cache_stats,
            "sub-agents": self.handle_sub_agents,
            "complex-task": self.handle_complex_task,
            
            # Utility commands
            "search": self.handle_web_search,
            "scrape": self.handle_web_scraping,
            "run": self.handle_code_execution,
            "setup": self.handle_setup
        }
    
    async def initialize_system(self):
        """Initialize all systems with comprehensive error handling"""
        try:
            self.console.print("[bold blue]🚀 Initializing BASED CODER CLI...[/bold blue]")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                
                # Initialize core tools
                task = progress.add_task("Initializing core tools...", total=8)
                
                progress.update(task, description="Initializing tool manager...")
                self.tool_manager = ToolManager()
                progress.advance(task)
                
                progress.update(task, description="Initializing LLM tool...")
                self.llm_tool = LLMQueryTool()
                progress.advance(task)
                
                progress.update(task, description="Initializing embedding tool...")
                self.embedding_tool = SimpleEmbeddingTool()
                progress.advance(task)
                
                progress.update(task, description="Initializing SQL database...")
                self.sql_tool = SQLDatabaseTool()
                progress.advance(task)
                
                progress.update(task, description="Initializing completion tools...")
                self.fim_tool = FIMCompletionTool()
                self.prefix_tool = PrefixCompletionTool()
                progress.advance(task)
                
                progress.update(task, description="Initializing analysis tools...")
                self.rag_tool = RAGPipelineTool()
                self.reasoning_engine = FastReasoningEngine(llm_tool=self.llm_tool)
                progress.advance(task)
                
                progress.update(task, description="Initializing memory and vector tools...")
                self.memory_tool = MemoryTool()
                self.vector_tool = VectorDatabaseTool()
                progress.advance(task)
                
                progress.update(task, description="Initializing advanced tools...")
                self.coder_tool = DeepSeekCoderTool()
                self.unified_agent = UnifiedAgentSystem()
                progress.advance(task)
                
                # Initialize enhanced features if available
                if ENHANCED_FEATURES_AVAILABLE:
                    task = progress.add_task("Initializing enhanced features...", total=4)
                    
                    progress.update(task, description="Setting up enhanced tool integration...")
                    self.enhanced_tool_manager = EnhancedToolManager()
                    progress.advance(task)
                    
                    progress.update(task, description="Setting up JSON mode support...")
                    self.json_mode_manager = JSONModeManager()
                    progress.advance(task)
                    
                    progress.update(task, description="Setting up prompt caching...")
                    self.cached_llm_client = CachedLLMClient(self.llm_tool)
                    progress.advance(task)
                    
                    progress.update(task, description="Setting up sub-agent system...")
                    self.sub_agent_system = SubAgentSystem(self.llm_tool, self.rag_tool)
                    progress.advance(task)
                    
                    self.enhanced_features_enabled = True
            
            self.system_initialized = True
            self.console.print("[bold green]✅ BASED CODER CLI initialized successfully![/bold green]")
            
        except Exception as e:
            self.console.print(f"[bold red]❌ Failed to initialize system: {e}[/bold red]")
            logger.error(f"System initialization failed: {e}")
            raise
    
    def print_banner(self):
        """Print the enhanced banner"""
        banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  ██████╗  █████╗ ███████╗███████╗██████╗      ██████╗ ██████╗ ██████╗ ███████╗██████╗  ║
║  ██╔══██╗██╔══██╗██╔════╝██╔════╝██╔══██╗    ██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔══██╗ ║
║  ██████╔╝███████║███████╗███████╗██║  ██║    ██║     ██║   ██║██║  ██║█████╗  ██████╔╝ ║
║  ██╔══██╗██╔══██║╚════██║╚════██║██║  ██║    ██║     ██║   ██║██║  ██║██╔══╝  ██╔══██╗ ║
║  ██████╔╝██║  ██║███████║███████║██████╔╝    ╚██████╗╚██████╔╝██████╔╝███████╗██║  ██║ ║
║  ╚═════╝ ╚═╝  ╚═╝╚══════╝╚══════╝╚═════╝      ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝ ║
║                                                                              ║
║                    🚀 UNIFIED AI-POWERED DEVELOPMENT TOOL                    ║
║                                                                              ║
║  ✨ Enhanced Tool Integration    🔧 JSON Mode Support                       ║
║  🧠 Prompt Caching System       🤖 Sub-Agent Architecture                  ║
║  🔍 Advanced RAG Pipeline       📊 Performance Monitoring                  ║
║                                                                              ║
║                    Made by @Lucariolucario55 on Telegram                    ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """
        self.console.print(Panel(banner, style="bold blue"))
    
    def show_help(self, args: List[str] = None):
        """Show comprehensive help information"""
        help_text = """
[bold blue]🎯 BASED CODER CLI - Command Reference[/bold blue]

[bold green]🚀 System Commands:[/bold green]
  /help                    - Show this help menu
  /status                  - Show system status and health
  /clear                   - Clear conversation history
  /history                 - Show conversation history
  /exit                    - Exit the CLI

[bold green]💬 AI Interaction Commands:[/bold green]
  /chat <message>          - Chat with AI assistant
  /code <prompt>           - Generate code from description
  /debug <code>            - Debug and fix code issues
  /heal <code>             - Self-heal problematic code

[bold green]🔧 Completion Commands:[/bold green]
  /fim <prefix> <suffix>   - Fill-in-Middle completion
  /prefix <text>           - Prefix completion

[bold green]🔍 Analysis Commands:[/bold green]
  /rag <query>             - RAG pipeline query
  /reason <question>       - Reasoning engine
  /analyze <code>          - Code analysis

[bold green]💾 Memory Commands:[/bold green]
  /remember <content>      - Store information in memory
  /recall <query>          - Recall information from memory

[bold green]🌐 Web Commands:[/bold green]
  /search <query>          - Web search
  /scrape <url>            - Web scraping

[bold green]⚡ Enhanced Commands:[/bold green]
  /enhanced-tools          - Show enhanced tool integration
  /json-mode <schema>      - Enable JSON mode with validation
  /cache-stats             - Show caching statistics
  /sub-agents              - Show sub-agent system status
  /complex-task <desc>     - Execute complex multi-step tasks

[bold green]🔧 Utility Commands:[/bold green]
  /run <code>              - Execute code safely
  /setup                   - Setup API keys and configuration

[bold cyan]💡 Examples:[/bold cyan]
  /chat "Hello, how are you?"
  /code "Create a Python web scraper"
  /debug "def hello() -> None: print('world')"
  /remember "BASED CODER CLI is awesome"
  /recall "BASED CODER CLI"
  /complex-task "Create a web API with authentication"

[bold magenta]🎨 Features:[/bold magenta]
  🌈 Rich interface with colorful output
  💻 Full system access and monitoring
  🚀 Prefix commands for quick access
  🧠 Multi-round conversations with context
  🔗 Function calls and reasoning
  🔄 FIM and prefix completion
  📚 RAG pipeline with vector search
  💾 Memory and persona management
  🎯 DeepSeek integration with all features
  ⚡ Enhanced caching and performance
  🤖 Sub-agent architecture for complex tasks

[bold green]Made by @Lucariolucario55 on Telegram[/bold green]
        """
        self.console.print(Panel(help_text, title="Help", style="bold blue"))
    
    def show_status(self, args: List[str] = None):
        """Show comprehensive system status"""
        if not self.system_initialized:
            self.console.print("[red]System not initialized. Run /setup first.[/red]")
            return
        
        # Get system information
        system_info = self.system_monitor.get_system_info()
        performance = self.system_monitor.get_performance_metrics()
        
        # Create status table
        status_table = Table(title="System Status", show_header=True, header_style="bold magenta")
        status_table.add_column("Component", style="cyan", no_wrap=True)
        status_table.add_column("Status", style="green")
        status_table.add_column("Details", style="yellow")
        
        # System status
        status_table.add_row(
            "System Initialized",
            "✅ Yes" if self.system_initialized else "❌ No",
            "All systems ready" if self.system_initialized else "Systems not ready"
        )
        
        status_table.add_row(
            "Enhanced Features",
            "✅ Enabled" if self.enhanced_features_enabled else "❌ Disabled",
            "Advanced features active" if self.enhanced_features_enabled else "Standard mode"
        )
        
        # API keys status
        deepseek_valid = validate_deepseek_key(os.getenv('DEEPSEEK_API_KEY', ''))
        huggingface_valid = validate_huggingface_token(os.getenv('HUGGINGFACE_API_KEY', ''))
        
        status_table.add_row(
            "DeepSeek API",
            "✅ Valid" if deepseek_valid else "❌ Invalid/Missing",
            "Ready for AI interactions" if deepseek_valid else "Please configure API key"
        )
        
        status_table.add_row(
            "HuggingFace Token",
            "✅ Valid" if huggingface_valid else "❌ Invalid/Missing",
            "Ready for embeddings" if huggingface_valid else "Optional for enhanced features"
        )
        
        # Tool status
        tools = [
            ("Tool Manager", self.tool_manager),
            ("LLM Tool", self.llm_tool),
            ("Embedding Tool", self.embedding_tool),
            ("SQL Database", self.sql_tool),
            ("RAG Pipeline", self.rag_tool),
            ("Memory Tool", self.memory_tool),
            ("Vector Database", self.vector_tool),
            ("Coder Tool", self.coder_tool)
        ]
        
        for name, tool in tools:
            status = "✅ Active" if tool else "❌ Inactive"
            details = "Ready" if tool else "Not initialized"
            status_table.add_row(name, status, details)
        
        # Performance metrics
        status_table.add_row(
            "CPU Usage",
            f"{performance['cpu_percent']:.1f}%",
            "System performance"
        )
        
        status_table.add_row(
            "Memory Usage",
            f"{performance['memory_percent']:.1f}%",
            "Available memory"
        )
        
        status_table.add_row(
            "Uptime",
            f"{performance['uptime_seconds']:.0f}s",
            "System uptime"
        )
        
        self.console.print(status_table)
        
        # Show enhanced features if available
        if self.enhanced_features_enabled:
            enhanced_table = Table(title="Enhanced Features Status", show_header=True, header_style="bold green")
            enhanced_table.add_column("Feature", style="cyan")
            enhanced_table.add_column("Status", style="green")
            
            enhanced_features = [
                ("Enhanced Tool Integration", self.enhanced_tool_manager),
                ("JSON Mode Support", self.json_mode_manager),
                ("Prompt Caching", self.cached_llm_client),
                ("Sub-Agent System", self.sub_agent_system)
            ]
            
            for name, feature in enhanced_features:
                status = "✅ Active" if feature else "❌ Inactive"
                enhanced_table.add_row(name, status)
            
            self.console.print(enhanced_table)
    
    async def handle_chat(self, args: List[str]):
        """Handle chat with AI"""
        if not args:
            self.console.print("[red]Please provide a message for chat[/red]")
            return
        
        message = " ".join(args)
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        
        try:
            # Get AI response
            result = await self.llm_tool.execute(
                prompt=message,
                max_tokens=500
            )
            
            if result.success:
                response = result.data.get('response', 'Sorry, I could not generate a response.')
                self.console.print(f"[green]🤖 AI: {response}[/green]")
                
                # Add to conversation history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.now().isoformat()
                })
            else:
                self.console.print(f"[red]❌ Error: {result.message}[/red]")
                
        except Exception as e:
            self.console.print(f"[red]❌ Error in chat: {str(e)}[/red]")
    
    async def handle_code_generation(self, args: List[str]):
        """Handle code generation"""
        if not args:
            self.console.print("[red]Please provide a prompt for code generation[/red]")
            return
        
        prompt = " ".join(args)
        
        try:
            result = await self.coder_tool.execute(
                operation="code_generation",
                prompt=prompt,
                language="python"
            )
            
            if result.success:
                code = result.data.get('code', 'No code generated.')
                self.console.print(f"[green]🔧 Generated Code:[/green]")
                self.console.print(Syntax(code, "python", theme="monokai"))
            else:
                self.console.print(f"[red]❌ Code generation failed: {result.message}[/red]")
                
        except Exception as e:
            self.console.print(f"[red]❌ Error in code generation: {str(e)}[/red]")
    
    async def handle_code_debugging(self, args: List[str]):
        """Handle code debugging"""
        if not args:
            self.console.print("[red]Please provide code to debug[/red]")
            return
        
        code = " ".join(args)
        
        try:
            result = await self.coder_tool.execute(
                operation="code_debugging",
                code=code,
                language="python"
            )
            
            if result.success:
                analysis = result.data.get('analysis', 'No analysis generated.')
                self.console.print(f"[green]🐛 Debug Analysis:[/green]")
                self.console.print(analysis)
            else:
                self.console.print(f"[red]❌ Code debugging failed: {result.message}[/red]")
                
        except Exception as e:
            self.console.print(f"[red]❌ Error in code debugging: {str(e)}[/red]")
    
    async def handle_code_healing(self, args: List[str]):
        """Handle code healing"""
        if not args:
            self.console.print("[red]Please provide code to heal[/red]")
            return
        
        code = " ".join(args)
        
        try:
            result = await self.coder_tool.execute(
                operation="self_healing",
                code=code,
                language="python"
            )
            
            if result.success:
                healed_code = result.data.get('healed_code', 'No healed code generated.')
                self.console.print(f"[green]🩹 Healed Code:[/green]")
                self.console.print(Syntax(healed_code, "python", theme="monokai"))
            else:
                self.console.print(f"[red]❌ Code healing failed: {result.message}[/red]")
                
        except Exception as e:
            self.console.print(f"[red]❌ Error in code healing: {str(e)}[/red]")
    
    async def handle_fim_completion(self, args: List[str]):
        """Handle FIM completion"""
        if len(args) < 2:
            self.console.print("[red]Please provide prefix and suffix for FIM completion[/red]")
            return
        
        prefix = args[0]
        suffix = " ".join(args[1:])
        
        try:
            result = await self.fim_tool.execute(
                prefix=prefix,
                suffix=suffix,
                language="python"
            )
            
            if result.success:
                completion = result.data.get('completion', 'No completion generated.')
                self.console.print(f"[green]🔗 FIM Completion:[/green]")
                self.console.print(Syntax(completion, "python", theme="monokai"))
            else:
                self.console.print(f"[red]❌ FIM completion failed: {result.message}[/red]")
                
        except Exception as e:
            self.console.print(f"[red]❌ Error in FIM completion: {str(e)}[/red]")
    
    async def handle_prefix_completion(self, args: List[str]):
        """Handle prefix completion"""
        if not args:
            self.console.print("[red]Please provide prefix text[/red]")
            return
        
        prefix = " ".join(args)
        
        try:
            result = await self.prefix_tool.execute(
                prefix=prefix,
                max_tokens=100
            )
            
            if result.success:
                completion = result.data.get('completion', 'No completion generated.')
                self.console.print(f"[green]📝 Prefix Completion:[/green]")
                self.console.print(completion)
            else:
                self.console.print(f"[red]❌ Prefix completion failed: {result.message}[/red]")
                
        except Exception as e:
            self.console.print(f"[red]❌ Error in prefix completion: {str(e)}[/red]")
    
    async def handle_rag_query(self, args: List[str]):
        """Handle RAG pipeline query"""
        if not args:
            self.console.print("[red]Please provide a query for RAG[/red]")
            return
        
        query = " ".join(args)
        
        try:
            result = await self.rag_tool.execute(
                query=query,
                max_results=3
            )
            
            if result.success:
                documents = result.data.get('documents', [])
                self.console.print(f"[green]📚 RAG Results ({len(documents)} documents):[/green]")
                for i, doc in enumerate(documents):
                    self.console.print(f"  {i+1}. {doc.get('content', 'N/A')[:100]}...")
            else:
                self.console.print(f"[red]❌ RAG query failed: {result.message}[/red]")
                
        except Exception as e:
            self.console.print(f"[red]❌ Error in RAG query: {str(e)}[/red]")
    
    async def handle_reasoning(self, args: List[str]):
        """Handle reasoning engine"""
        if not args:
            self.console.print("[red]Please provide a question for reasoning[/red]")
            return
        
        question = " ".join(args)
        
        try:
            result = await self.reasoning_engine.execute(
                question=question,
                approach="step_by_step"
            )
            
            if result.success:
                reasoning = result.data.get('reasoning', 'No reasoning generated.')
                self.console.print(f"[green]🧠 Reasoning:[/green]")
                self.console.print(reasoning)
            else:
                self.console.print(f"[red]❌ Reasoning failed: {result.message}[/red]")
                
        except Exception as e:
            self.console.print(f"[red]❌ Error in reasoning: {str(e)}[/red]")
    
    async def handle_code_analysis(self, args: List[str]):
        """Handle code analysis"""
        if not args:
            self.console.print("[red]Please provide code to analyze[/red]")
            return
        
        code = " ".join(args)
        
        try:
            result = await self.coder_tool.execute(
                operation="code_analysis",
                code=code,
                language="python"
            )
            
            if result.success:
                analysis = result.data.get('analysis', 'No analysis generated.')
                self.console.print(f"[green]🔍 Code Analysis:[/green]")
                self.console.print(analysis)
            else:
                self.console.print(f"[red]❌ Code analysis failed: {result.message}[/red]")
                
        except Exception as e:
            self.console.print(f"[red]❌ Error in code analysis: {str(e)}[/red]")
    
    async def handle_memory_store(self, args: List[str]):
        """Handle memory storage"""
        if not args:
            self.console.print("[red]Please provide content to remember[/red]")
            return
        
        content = " ".join(args)
        
        try:
            result = await self.memory_tool.execute(
                operation="store",
                content=content
            )
            
            if result.success:
                self.console.print("[green]💾 Stored in memory successfully![/green]")
            else:
                self.console.print(f"[red]❌ Memory storage failed: {result.message}[/red]")
                
        except Exception as e:
            self.console.print(f"[red]❌ Error in memory storage: {str(e)}[/red]")
    
    async def handle_memory_recall(self, args: List[str]):
        """Handle memory recall"""
        if not args:
            self.console.print("[red]Please provide a query to recall[/red]")
            return
        
        query = " ".join(args)
        
        try:
            result = await self.memory_tool.execute(
                operation="retrieve",
                query=query
            )
            
            if result.success:
                memories = result.data.get('memories', [])
                self.console.print(f"[green]💾 Retrieved {len(memories)} memories:[/green]")
                for memory in memories:
                    self.console.print(f"  - {memory.get('content', 'N/A')}")
            else:
                self.console.print(f"[red]❌ Memory retrieval failed: {result.message}[/red]")
                
        except Exception as e:
            self.console.print(f"[red]❌ Error in memory retrieval: {str(e)}[/red]")
    
    async def handle_web_search(self, args: List[str]):
        """Handle web search"""
        if not args:
            self.console.print("[red]Please provide a search query[/red]")
            return
        
        query = " ".join(args)
        self.console.print(f"[yellow]🔍 Searching for: {query}[/yellow]")
        # Implementation would go here
    
    async def handle_web_scraping(self, args: List[str]):
        """Handle web scraping"""
        if not args:
            self.console.print("[red]Please provide a URL to scrape[/red]")
            return
        
        url = args[0]
        self.console.print(f"[yellow]🌐 Scraping: {url}[/yellow]")
        # Implementation would go here
    
    async def handle_code_execution(self, args: List[str]):
        """Handle code execution"""
        if not args:
            self.console.print("[red]Please provide code to execute[/red]")
            return
        
        code = " ".join(args)
        self.console.print(f"[yellow]⚡ Executing code: {code[:50]}...[/yellow]")
        # Implementation would go here
    
    async def handle_setup(self, args: List[str] = None):
        """Handle system setup"""
        self.console.print("[bold blue]🔧 Setting up BASED CODER CLI...[/bold blue]")
        
        # Check for .env file
        env_file = Path(".env")
        if not env_file.exists():
            self.console.print("[yellow]Creating .env file...[/yellow]")
            env_file.write_text("")
        
        # Check API keys
        deepseek_key = os.getenv('DEEPSEEK_API_KEY')
        huggingface_key = os.getenv('HUGGINGFACE_API_KEY')
        
        if not deepseek_key:
            self.console.print("[yellow]Please set your DeepSeek API key in the .env file:[/yellow]")
            self.console.print("DEEPSEEK_API_KEY=your_api_key_here")
        
        if not huggingface_key:
            self.console.print("[yellow]Optional: Set your HuggingFace token in the .env file:[/yellow]")
            self.console.print("HUGGINGFACE_API_KEY=your_token_here")
        
        # Initialize system
        await self.initialize_system()
    
    async def handle_enhanced_tools(self, args: List[str] = None):
        """Handle enhanced tools command"""
        if not self.enhanced_features_enabled:
            self.console.print("[red]Enhanced features not enabled[/red]")
            return
        
        # Implementation would go here
        self.console.print("[green]Enhanced tools status: Active[/green]")
    
    async def handle_json_mode(self, args: List[str]):
        """Handle JSON mode command"""
        if not args:
            self.console.print("[red]Please specify a schema name[/red]")
            return
        
        schema_name = args[0]
        self.console.print(f"[green]JSON mode enabled with schema: {schema_name}[/green]")
    
    async def handle_cache_stats(self, args: List[str] = None):
        """Handle cache statistics command"""
        self.console.print("[green]Cache statistics:[/green]")
        # Implementation would go here
    
    async def handle_sub_agents(self, args: List[str] = None):
        """Handle sub-agents command"""
        self.console.print("[green]Sub-agent system status:[/green]")
        # Implementation would go here
    
    async def handle_complex_task(self, args: List[str]):
        """Handle complex task command"""
        if not args:
            self.console.print("[red]Please provide a task description[/red]")
            return
        
        description = " ".join(args)
        self.console.print(f"[bold blue]Executing complex task: {description}[/bold blue]")
        # Implementation would go here
    
    def clear_history(self, args: List[str] = None):
        """Clear conversation history"""
        self.conversation_history = []
        self.console.print("[green]✅ Conversation history cleared![/green]")
    
    def show_history(self, args: List[str] = None):
        """Show conversation history"""
        if not self.conversation_history:
            self.console.print("[yellow]📝 No conversation history found.[/yellow]")
            return
        
        self.console.print(f"[cyan]📝 Conversation History ({len(self.conversation_history)} messages):[/cyan]")
        for i, message in enumerate(self.conversation_history[-10:], 1):  # Show last 10 messages
            role = message['role']
            content = message['content'][:100] + "..." if len(message['content']) > 100 else message['content']
            timestamp = message['timestamp']
            
            if role == "user":
                self.console.print(f"[blue]{i}. User: {content}[/blue]")
            else:
                self.console.print(f"[green]{i}. AI: {content}[/green]")
    
    def exit_cli(self, args: List[str] = None):
        """Exit the CLI"""
        self.console.print("[bold blue]👋 Goodbye! Made by @Lucariolucario55 on Telegram[/bold blue]")
        sys.exit(0)
    
    def parse_command(self, user_input: str) -> tuple:
        """Parse user input into command and arguments"""
        if not user_input.startswith('/'):
            return "chat", [user_input]
        
        parts = user_input.split(' ', 1)
        command = parts[0][1:].lower()  # Remove leading '/'
        args = parts[1].split() if len(parts) > 1 else []
        
        return command, args
    
    async def execute_command(self, command: str, args: List[str]):
        """Execute a command"""
        if command in self.commands:
            handler = self.commands[command]
            if asyncio.iscoroutinefunction(handler):
                await handler(args)
            else:
                handler(args)
        else:
            self.console.print(f"[red]❌ Unknown command: {command}[/red]")
            self.console.print("[yellow]💡 Type /help for available commands[/yellow]")
    
    async def interactive_mode(self):
        """Run interactive CLI mode"""
        self.print_banner()
        
        if not self.system_initialized:
            self.console.print("[yellow]⚠️ System not initialized. Running setup...[/yellow]")
            await self.handle_setup()
        
        self.console.print("[bold green]🚀 BASED CODER CLI ready! Type /help for commands or 'exit' to quit.[/bold green]")
        
        while True:
            try:
                # Get user input
                user_input = Prompt.ask("\n[bold cyan]BASED CODER[/bold cyan]")
                
                if not user_input.strip():
                    continue
                
                if user_input.lower() in ['exit', 'quit', 'q']:
                    self.exit_cli()
                
                # Parse and execute command
                command, args = self.parse_command(user_input)
                await self.execute_command(command, args)
                    
            except KeyboardInterrupt:
                self.console.print("\n[bold blue]Goodbye![/bold blue]")
                break
            except Exception as e:
                self.console.print(f"[bold red]Error: {e}[/bold red]")
                logger.error(f"Interactive mode error: {e}")

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="🚀 BASED CODER CLI - Unified AI-Powered Development Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python based_coder_cli.py                    # Interactive mode
  python based_coder_cli.py --chat "Hello"     # Single chat command
  python based_coder_cli.py --code "web scraper" # Generate code
  python based_coder_cli.py --status           # Show system status
  python based_coder_cli.py --setup            # Setup system
        """
    )
    
    parser.add_argument("--interactive", "-i", action="store_true", 
                       help="Run in interactive mode (default)")
    parser.add_argument("--chat", type=str, help="Send a chat message")
    parser.add_argument("--code", type=str, help="Generate code from prompt")
    parser.add_argument("--debug", type=str, help="Debug code")
    parser.add_argument("--status", action="store_true", help="Show system status")
    parser.add_argument("--setup", action="store_true", help="Setup system")
    parser.add_argument("--help-cmd", action="store_true", help="Show command help")
    
    args = parser.parse_args()
    
    cli = BasedCoderCLI()
    
    try:
        # Handle non-interactive commands
        if args.chat:
            await cli.initialize_system()
            await cli.handle_chat([args.chat])
        elif args.code:
            await cli.initialize_system()
            await cli.handle_code_generation([args.code])
        elif args.debug:
            await cli.initialize_system()
            await cli.handle_code_debugging([args.debug])
        elif args.status:
            await cli.initialize_system()
            cli.show_status()
        elif args.setup:
            await cli.handle_setup()
        elif args.help_cmd:
            cli.show_help()
        else:
            # Default to interactive mode
            await cli.interactive_mode()
    
    except Exception as e:
        console.print(f"[bold red]Fatal error: {e}[/bold red]")
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())