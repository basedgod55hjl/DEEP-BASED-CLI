#!/usr/bin/env python3
"""
Enhanced BASED GOD CLI - Advanced AI-Powered Command Line Interface
Upgraded with FIM completion, prefix completion, streaming, and unified agent system
"""

import asyncio
import json
import logging
import sys
import os
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import argparse
import signal
import threading
from pathlib import Path

# Rich for beautiful terminal output
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax

# Import our enhanced tools
from tools.llm_query_tool import LLMQueryTool
from tools.fim_completion_tool import FIMCompletionTool
from tools.prefix_completion_tool import PrefixCompletionTool
from tools.unified_agent_system import UnifiedAgentSystem
from tools.vector_database_tool import VectorDatabaseTool
from tools.sql_database_tool import SQLDatabaseTool
from tools.rag_pipeline_tool import RAGPipelineTool
from tools.tool_manager import ToolManager

# Configuration
from config.deepcli_config import get_config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/enhanced_cli.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class EnhancedBASEDGODCLI:
    """
    Enhanced BASED GOD CLI with advanced AI capabilities
    """
    
    def __init__(self):
        """Initialize the enhanced CLI"""
        self.console = Console()
        self.config = get_config()
        
        # Initialize tools (will be properly initialized in async setup)
        self.llm_tool = None
        self.fim_tool = None
        self.prefix_tool = None
        self.unified_agent = None
        self.vector_db = None
        self.sql_db = None
        self.rag_pipeline = None
        self.tool_manager = None
        
        # Session state
        self.session_data = {
            "conversation_history": [],
            "current_mode": "chat",
            "active_tools": [],
            "performance_metrics": {},
            "user_preferences": {}
        }
        
        # Streaming state
        self.is_streaming = False
        self.streaming_task = None
        
        # Signal handling
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    async def _initialize_tools(self):
        """Initialize all tools asynchronously"""
        try:
            self.console.print("[yellow]Initializing tools...[/yellow]")
            
            # Initialize tools that don't require async setup
            self.fim_tool = FIMCompletionTool()
            self.prefix_tool = PrefixCompletionTool()
            
            # Initialize tools that require async setup
            self.llm_tool = LLMQueryTool()
            self.unified_agent = UnifiedAgentSystem()
            self.sql_db = SQLDatabaseTool()
            self.tool_manager = ToolManager()
            
            # Initialize optional tools (vector database and RAG)
            try:
                self.vector_db = VectorDatabaseTool()
                self.rag_pipeline = RAGPipelineTool()
                self.console.print("[green]✅ Vector database and RAG initialized[/green]")
            except Exception as e:
                self.console.print(f"[yellow]⚠️ Vector database/RAG not available: {str(e)}[/yellow]")
                self.vector_db = None
                self.rag_pipeline = None
            
            self.console.print("[green]✅ Core tools initialized successfully[/green]")
            
        except Exception as e:
            self.console.print(f"[red]❌ Core tool initialization failed: {str(e)}[/red]")
            raise
    
    def _display_welcome(self):
        """Display enhanced welcome message"""
        welcome_text = """
[bold cyan]🚀 Enhanced BASED GOD CLI v2.0[/bold cyan]

[bold green]Advanced AI-Powered Command Line Interface[/bold green]

[bold yellow]✨ New Features:[/bold yellow]
• [bold]FIM Completion[/bold] - Fill-in-middle code completion
• [bold]Prefix Completion[/bold] - Smart text and code continuation  
• [bold]Real-time Streaming[/bold] - Live response streaming
• [bold]Unified Agent System[/bold] - Advanced AI with memory and learning
• [bold]Vector Database[/bold] - Semantic search and RAG
• [bold]Multi-modal Support[/bold] - Text, code, and structured data
• [bold]Advanced Reasoning[/bold] - Chain-of-thought and logical analysis

[bold blue]🎯 Quick Start:[/bold blue]
• Type your message for chat
• Use "fim: [prefix] [suffix]" for FIM completion
• Use "prefix: [text]" for prefix completion
• Use "stream: [message]" for streaming responses
• Use "agent: [task]" for unified agent operations
• Type "help" for complete command reference

[bold magenta]🔧 Available Modes:[/bold magenta]
• [bold]chat[/bold] - General conversation
• [bold]fim[/bold] - Fill-in-middle completion
• [bold]prefix[/bold] - Prefix completion
• [bold]stream[/bold] - Streaming responses
• [bold]agent[/bold] - Unified agent system
• [bold]rag[/bold] - Retrieval-augmented generation
• [bold]tools[/bold] - Tool management

[bold green]Ready to assist you with advanced AI capabilities![/bold green]
        """
        
        self.console.print(Panel(welcome_text, title="[bold cyan]Enhanced BASED GOD CLI[/bold cyan]", border_style="cyan"))
    
    def _signal_handler(self, signum, frame):
        """Handle interrupt signals gracefully"""
        self.console.print("\n[bold red]Shutting down gracefully...[/bold red]")
        
        # Stop streaming if active
        if self.is_streaming and self.streaming_task:
            self.streaming_task.cancel()
        
        # Save session data
        self._save_session_data()
        
        self.console.print("[bold green]Goodbye![/bold green]")
        sys.exit(0)
    
    def _save_session_data(self):
        """Save session data for persistence"""
        try:
            session_file = Path("data/session_data.json")
            session_file.parent.mkdir(exist_ok=True)
            
            with open(session_file, 'w') as f:
                json.dump(self.session_data, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Failed to save session data: {str(e)}")
    
    def _load_session_data(self):
        """Load previous session data"""
        try:
            session_file = Path("data/session_data.json")
            if session_file.exists():
                with open(session_file, 'r') as f:
                    self.session_data = json.load(f)
                    
        except Exception as e:
            logger.error(f"Failed to load session data: {str(e)}")
    
    async def run(self):
        """Main CLI loop with enhanced capabilities"""
        # Initialize tools asynchronously
        await self._initialize_tools()
        
        # Display welcome message
        self._display_welcome()
        
        # Load session data
        self._load_session_data()
        
        while True:
            try:
                # Get user input with enhanced prompt
                prompt_text = self._get_prompt_text()
                user_input = Prompt.ask(prompt_text)
                
                if not user_input.strip():
                    continue
                
                # Handle special commands
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    self._save_session_data()
                    self.console.print("[bold green]Goodbye![/bold green]")
                    break
                
                if user_input.lower() == 'help':
                    self._display_help()
                    continue
                
                if user_input.lower() == 'clear':
                    self.console.clear()
                    self._display_welcome()
                    continue
                
                if user_input.lower() == 'status':
                    self._display_status()
                    continue
                
                if user_input.lower() == 'tools':
                    self._display_tools()
                    continue
                
                # Process user input with enhanced parsing
                await self._process_user_input(user_input)
                
            except KeyboardInterrupt:
                self.console.print("\n[bold yellow]Use 'quit' to exit gracefully[/bold yellow]")
            except Exception as e:
                logger.error(f"Error in main loop: {str(e)}")
                self.console.print(f"[bold red]Error: {str(e)}[/bold red]")
    
    def _get_prompt_text(self) -> str:
        """Get enhanced prompt text based on current mode"""
        mode = self.session_data.get("current_mode", "chat")
        
        if mode == "fim":
            return "[bold cyan]FIM[/bold cyan] > "
        elif mode == "prefix":
            return "[bold green]PREFIX[/bold green] > "
        elif mode == "stream":
            return "[bold magenta]STREAM[/bold magenta] > "
        elif mode == "agent":
            return "[bold yellow]AGENT[/bold yellow] > "
        elif mode == "rag":
            return "[bold blue]RAG[/bold blue] > "
        else:
            return "[bold white]Enhanced CLI[/bold white] > "
    
    async def _process_user_input(self, user_input: str):
        """Process user input with enhanced parsing and routing"""
        try:
            # Enhanced input parsing
            parsed_input = self._parse_user_input(user_input)
            
            if parsed_input["mode"] == "stream":
                await self._handle_streaming_request(parsed_input)
            elif parsed_input["mode"] == "fim":
                await self._handle_fim_request(parsed_input)
            elif parsed_input["mode"] == "prefix":
                await self._handle_prefix_request(parsed_input)
            elif parsed_input["mode"] == "agent":
                await self._handle_agent_request(parsed_input)
            elif parsed_input["mode"] == "rag":
                await self._handle_rag_request(parsed_input)
            elif parsed_input["mode"] == "tools":
                await self._handle_tools_request(parsed_input)
            else:
                await self._handle_chat_request(parsed_input)
        
        except Exception as e:
            logger.error(f"Error processing user input: {str(e)}")
            self.console.print(f"[bold red]Error processing input: {str(e)}[/bold red]")
    
    def _parse_user_input(self, user_input: str) -> Dict[str, Any]:
        """Enhanced input parsing with multiple detection methods"""
        input_lower = user_input.lower().strip()
        
        # Mode switching commands
        if input_lower.startswith("mode:"):
            mode = input_lower.split(":", 1)[1].strip()
            self.session_data["current_mode"] = mode
            self.console.print(f"[bold green]Switched to {mode} mode[/bold green]")
            return {"mode": "mode_switch", "new_mode": mode}
        
        # Streaming detection
        if (input_lower.startswith("stream:") or 
            input_lower.startswith("live:") or
            "stream" in input_lower and ":" in input_lower):
            content = user_input.split(":", 1)[1].strip()
            return {
                "mode": "stream",
                "content": content,
                "model": self._extract_model(user_input),
                "temperature": self._extract_temperature(user_input)
            }
        
        # FIM detection with enhanced patterns
        if (input_lower.startswith("fim:") or
            input_lower.startswith("fill:") or
            "fim" in input_lower and ":" in input_lower or
            "fill in middle" in input_lower or
            "complete between" in input_lower):
            
            # Extract prefix and suffix
            if ":" in user_input:
                content = user_input.split(":", 1)[1].strip()
                parts = content.split("|")
                if len(parts) >= 2:
                    prefix = parts[0].strip()
                    suffix = parts[1].strip()
                else:
                    prefix = content
                    suffix = ""
            else:
                # Try to extract from natural language
                prefix, suffix = self._extract_fim_from_natural_language(user_input)
            
            return {
                "mode": "fim",
                "prefix": prefix,
                "suffix": suffix,
                "language": self._extract_language(user_input),
                "model": self._extract_model(user_input) or "deepseek-coder"
            }
        
        # Prefix detection with enhanced patterns
        if (input_lower.startswith("prefix:") or
            input_lower.startswith("continue:") or
            "prefix" in input_lower and ":" in input_lower or
            "continue from" in input_lower or
            "complete" in input_lower and not "fim" in input_lower):
            
            if ":" in user_input:
                content = user_input.split(":", 1)[1].strip()
            else:
                content = user_input
            
            return {
                "mode": "prefix",
                "prefix": content,
                "model": self._extract_model(user_input),
                "temperature": self._extract_temperature(user_input)
            }
        
        # Agent detection
        if (input_lower.startswith("agent:") or
            input_lower.startswith("ai:") or
            "agent" in input_lower and ":" in input_lower):
            
            content = user_input.split(":", 1)[1].strip()
            return {
                "mode": "agent",
                "content": content,
                "operation": self._extract_agent_operation(content)
            }
        
        # RAG detection
        if (input_lower.startswith("rag:") or
            input_lower.startswith("search:") or
            "rag" in input_lower and ":" in input_lower):
            
            content = user_input.split(":", 1)[1].strip()
            return {
                "mode": "rag",
                "query": content,
                "persona": self._extract_persona(user_input)
            }
        
        # Tools detection
        if (input_lower.startswith("tools:") or
            input_lower.startswith("tool:") or
            "tools" in input_lower and ":" in input_lower):
            
            content = user_input.split(":", 1)[1].strip()
            return {
                "mode": "tools",
                "command": content
            }
        
        # Default to chat mode
        return {
            "mode": "chat",
            "message": user_input,
            "model": self._extract_model(user_input),
            "temperature": self._extract_temperature(user_input),
            "system_message": self._extract_system_message(user_input)
        }
    
    def _extract_fim_from_natural_language(self, text: str) -> Tuple[str, str]:
        """Extract FIM prefix and suffix from natural language"""
        text_lower = text.lower()
        
        # Common patterns
        if "between" in text_lower and "and" in text_lower:
            parts = text.split("between", 1)[1].split("and", 1)
            if len(parts) >= 2:
                return parts[0].strip(), parts[1].strip()
        
        if "fill in" in text_lower:
            # Try to extract from "fill in X and Y"
            fill_part = text.split("fill in", 1)[1]
            if "and" in fill_part:
                parts = fill_part.split("and", 1)
                return parts[0].strip(), parts[1].strip()
        
        # Default: treat as prefix only
        return text, ""
    
    def _extract_model(self, text: str) -> Optional[str]:
        """Extract model specification from text"""
        text_lower = text.lower()
        
        if "deepseek-chat" in text_lower or "chat" in text_lower:
            return "deepseek-chat"
        elif "deepseek-coder" in text_lower or "coder" in text_lower:
            return "deepseek-coder"
        elif "deepseek-reasoner" in text_lower or "reasoner" in text_lower:
            return "deepseek-reasoner"
        
        return None
    
    def _extract_temperature(self, text: str) -> Optional[float]:
        """Extract temperature from text"""
        import re
        
        temp_match = re.search(r'temp[:\s]*([0-9]*\.?[0-9]+)', text.lower())
        if temp_match:
            return float(temp_match.group(1))
        
        return None
    
    def _extract_language(self, text: str) -> Optional[str]:
        """Extract programming language from text"""
        text_lower = text.lower()
        
        languages = ["python", "javascript", "java", "cpp", "c++", "c#", "rust", "go", "php", "ruby", "swift"]
        for lang in languages:
            if lang in text_lower:
                return lang
        
        return "python"  # Default
    
    def _extract_agent_operation(self, text: str) -> str:
        """Extract agent operation from text"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["conversation", "chat", "talk"]):
            return "conversation"
        elif any(word in text_lower for word in ["tool", "use", "execute"]):
            return "tool_use"
        elif any(word in text_lower for word in ["memory", "remember", "recall"]):
            return "memory_retrieval"
        elif any(word in text_lower for word in ["learn", "learning"]):
            return "learning"
        elif any(word in text_lower for word in ["reason", "reasoning", "think"]):
            return "reasoning"
        elif any(word in text_lower for word in ["plan", "planning"]):
            return "planning"
        else:
            return "conversation"
    
    def _extract_persona(self, text: str) -> Optional[str]:
        """Extract persona from text"""
        text_lower = text.lower()
        
        if "deanna" in text_lower:
            return "deanna"
        elif "assistant" in text_lower:
            return "assistant"
        elif "expert" in text_lower:
            return "expert"
        
        return None
    
    def _extract_system_message(self, text: str) -> Optional[str]:
        """Extract system message from text"""
        if text.startswith("system:"):
            return text.split(":", 1)[1].strip()
        return None
    
    async def _handle_streaming_request(self, parsed_input: Dict[str, Any]):
        """Handle streaming request with real-time output"""
        try:
            self.console.print("[bold magenta]Starting streaming response...[/bold magenta]")
            
            # Create streaming display
            with Live(Panel("", title="[bold magenta]Streaming Response[/bold magenta]"), refresh_per_second=10) as live:
                self.is_streaming = True
                
                # Start streaming task
                self.streaming_task = asyncio.create_task(
                    self._stream_response(parsed_input, live)
                )
                
                try:
                    await self.streaming_task
                except asyncio.CancelledError:
                    self.console.print("[bold yellow]Streaming cancelled[/bold yellow]")
                finally:
                    self.is_streaming = False
                    
        except Exception as e:
            self.console.print(f"[bold red]Streaming error: {str(e)}[/bold red]")
            self.is_streaming = False
    
    async def _stream_response(self, parsed_input: Dict[str, Any], live):
        """Stream response in real-time"""
        try:
            content = parsed_input["content"]
            model = parsed_input.get("model", "deepseek-chat")
            temperature = parsed_input.get("temperature", 0.7)
            
            # Use LLM tool for streaming
            response = await self.llm_tool.stream_completion(
                prompt=content,
                model=model,
                temperature=temperature
            )
            
            if response.success:
                streamed_text = response.data.get("response", "")
                
                # Display streamed content
                live.update(Panel(
                    streamed_text,
                    title="[bold magenta]Streaming Response[/bold magenta]",
                    border_style="magenta"
                ))
                
                # Update session data
                self.session_data["conversation_history"].append({
                    "role": "user",
                    "content": content,
                    "timestamp": datetime.now().isoformat()
                })
                self.session_data["conversation_history"].append({
                    "role": "assistant", 
                    "content": streamed_text,
                    "timestamp": datetime.now().isoformat()
                })
                
            else:
                live.update(Panel(
                    f"[bold red]Error: {response.message}[/bold red]",
                    title="[bold red]Streaming Error[/bold red]",
                    border_style="red"
                ))
                
        except Exception as e:
            live.update(Panel(
                f"[bold red]Streaming failed: {str(e)}[/bold red]",
                title="[bold red]Streaming Error[/bold red]",
                border_style="red"
            ))
    
    async def _handle_fim_request(self, parsed_input: Dict[str, Any]):
        """Handle FIM completion request"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Generating FIM completion...", total=None)
                
                response = await self.fim_tool.execute(
                    prefix=parsed_input["prefix"],
                    suffix=parsed_input["suffix"],
                    language=parsed_input.get("language", "python"),
                    model=parsed_input.get("model", "deepseek-coder")
                )
                
                progress.update(task, completed=True)
            
            if response.success:
                completion = response.data.get("completion", "")
                mode = response.data.get("mode", "text")
                
                # Display result with appropriate formatting
                if mode == "code":
                    syntax = Syntax(completion, "python", theme="monokai")
                    self.console.print(Panel(
                        syntax,
                        title="[bold cyan]FIM Completion[/bold cyan]",
                        border_style="cyan"
                    ))
                else:
                    self.console.print(Panel(
                        completion,
                        title="[bold cyan]FIM Completion[/bold cyan]",
                        border_style="cyan"
                    ))
                
                # Show metadata
                self._display_completion_metadata(response.data)
                
            else:
                self.console.print(f"[bold red]FIM completion failed: {response.message}[/bold red]")
                
        except Exception as e:
            self.console.print(f"[bold red]FIM completion error: {str(e)}[/bold red]")
    
    async def _handle_prefix_request(self, parsed_input: Dict[str, Any]):
        """Handle prefix completion request"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Generating prefix completion...", total=None)
                
                response = await self.prefix_tool.execute(
                    prefix=parsed_input["prefix"],
                    model=parsed_input.get("model", "deepseek-chat"),
                    temperature=parsed_input.get("temperature", 0.7)
                )
                
                progress.update(task, completed=True)
            
            if response.success:
                completion = response.data.get("completion", "")
                mode = response.data.get("mode", "text")
                
                # Display result with appropriate formatting
                if mode == "code":
                    syntax = Syntax(completion, "python", theme="monokai")
                    self.console.print(Panel(
                        syntax,
                        title="[bold green]Prefix Completion (Code)[/bold green]",
                        border_style="green"
                    ))
                else:
                    self.console.print(Panel(
                        completion,
                        title="[bold green]Prefix Completion (Text)[/bold green]",
                        border_style="green"
                    ))
                
                # Show metadata
                self._display_completion_metadata(response.data)
                
            else:
                self.console.print(f"[bold red]Prefix completion failed: {response.message}[/bold red]")
            
        except Exception as e:
            self.console.print(f"[bold red]Prefix completion error: {str(e)}[/bold red]")
    
    async def _handle_agent_request(self, parsed_input: Dict[str, Any]):
        """Handle unified agent request"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Processing with unified agent...", total=None)
                
                response = await self.unified_agent.execute(
                    operation=parsed_input.get("operation", "conversation"),
                    message=parsed_input["content"],
                    context=self.session_data
                )
                
                progress.update(task, completed=True)
            
            if response.success:
                agent_response = response.data.get("response", "")
                context_used = response.data.get("context_used", {})
                
                # Display agent response
                self.console.print(Panel(
                    agent_response,
                    title="[bold yellow]Unified Agent Response[/bold yellow]",
                    border_style="yellow"
                ))
                
                # Show context information
                if context_used:
                    self._display_agent_context(context_used)
                
            else:
                self.console.print(f"[bold red]Agent request failed: {response.message}[/bold red]")
            
        except Exception as e:
            self.console.print(f"[bold red]Agent request error: {str(e)}[/bold red]")
    
    async def _handle_rag_request(self, parsed_input: Dict[str, Any]):
        """Handle RAG request"""
        try:
            if not self.rag_pipeline:
                self.console.print("[bold red]RAG pipeline not initialized. Please ensure Qdrant is running and configured.[/bold red]")
                return
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Retrieving information with RAG...", total=None)
                
                response = await self.rag_pipeline.execute(
                    query=parsed_input["query"],
                    persona=parsed_input.get("persona")
                )
                
                progress.update(task, completed=True)
            
            if response.success:
                rag_response = response.data.get("response", "")
                sources = response.data.get("sources", [])
                
                # Display RAG response
                self.console.print(Panel(
                    rag_response,
                    title="[bold blue]RAG Response[/bold blue]",
                    border_style="blue"
                ))
                
                # Display sources
                if sources:
                    self._display_rag_sources(sources)
                
            else:
                self.console.print(f"[bold red]RAG request failed: {response.message}[/bold red]")
            
        except Exception as e:
            self.console.print(f"[bold red]RAG request error: {str(e)}[/bold red]")
    
    async def _handle_tools_request(self, parsed_input: Dict[str, Any]):
        """Handle tool execution request"""
        try:
            command = parsed_input["command"]
            
            # Example: parse command like "execute tool_name arg1=val1 arg2=val2"
            parts = command.split(" ", 2)
            if len(parts) < 2 or parts[0].lower() != "execute":
                self.console.print("[bold red]Invalid tool command format. Use: execute tool_name [args][/bold red]")
                return
            
            tool_name = parts[1]
            tool_args = {}
            if len(parts) > 2:
                # Simple arg parsing (e.g., arg1=val1 arg2=val2)
                arg_string = parts[2]
                for arg in arg_string.split():
                    if '=' in arg:
                        key, value = arg.split('=', 1)
                        tool_args[key] = value
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task(f"Executing tool [bold magenta]{tool_name}[/bold magenta]...", total=None)
                
                response = await self.tool_manager.execute_tool(tool_name, **tool_args)
                
                progress.update(task, completed=True)
            
            if response.success:
                self.console.print(Panel(
                    str(response.data),
                    title="[bold green]Tool Execution Result[/bold green]",
                    border_style="green"
                ))
            else:
                self.console.print(f"[bold red]Tool execution failed: {response.message}[/bold red]")
            
        except Exception as e:
            self.console.print(f"[bold red]Tool execution error: {str(e)}[/bold red]")
    
    async def _handle_chat_request(self, parsed_input: Dict[str, Any]):
        """Handle chat request"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Generating chat response...", total=None)
                
                response = await self.llm_tool.execute(
                    operation="chat_completion",
                    messages=[
                        {"role": "user", "content": parsed_input["message"]}
                    ],
                    model=parsed_input.get("model", "deepseek-chat"),
                    temperature=parsed_input.get("temperature", 0.7),
                    system_message=parsed_input.get("system_message")
                )
                
                progress.update(task, completed=True)
            
            if response.success:
                chat_response = response.data.get("response", "")
                self.console.print(Panel(
                    chat_response,
                    title="[bold blue]AI Response[/bold blue]",
                    border_style="blue"
                ))
                
                self.session_data["conversation_history"].append({
                    "role": "user",
                    "content": parsed_input["message"],
                    "timestamp": datetime.now().isoformat()
                })
                self.session_data["conversation_history"].append({
                    "role": "assistant", 
                    "content": chat_response,
                    "timestamp": datetime.now().isoformat()
                })
            else:
                self.console.print(f"[bold red]Chat failed: {response.message}[/bold red]")
            
        except Exception as e:
            logger.error(f"Chat error: {str(e)}")
            self.console.print(f"[bold red]Chat error: {str(e)}[/bold red]")
    
    def _display_completion_metadata(self, data: Dict[str, Any]):
        """Display completion metadata"""
        table = Table(title="Completion Metadata")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        if "model" in data:
            table.add_row("Model", data["model"])
        if "language" in data:
            table.add_row("Language", data["language"])
        if "mode" in data:
            table.add_row("Mode", data["mode"])
        if "tokens_used" in data:
            table.add_row("Tokens Used", str(data["tokens_used"]))
        if "timestamp" in data:
            table.add_row("Timestamp", data["timestamp"])
        
        self.console.print(table)
    
    def _display_agent_context(self, context: Dict[str, Any]):
        """Display agent context information"""
        table = Table(title="Agent Context")
        table.add_column("Context Type", style="cyan")
        table.add_column("Details", style="green")
        
        if "relevant_memories" in context:
            table.add_row("Relevant Memories", str(len(context["relevant_memories"])))
        if "relevant_contacts" in context:
            table.add_row("Relevant Contacts", str(len(context["relevant_contacts"])))
        if "conversation_history" in context:
            table.add_row("Conversation History", str(len(context["conversation_history"])))
        if "current_persona" in context:
            table.add_row("Current Persona", context["current_persona"])
        
        self.console.print(table)
    
    def _display_rag_sources(self, sources: List[Dict[str, Any]]):
        """Display RAG sources"""
        table = Table(title="RAG Sources")
        table.add_column("Source", style="cyan")
        table.add_column("Relevance", style="green")
        table.add_column("Content", style="white")
        
        for source in sources[:5]:  # Show top 5 sources
            table.add_row(
                source.get("source", "Unknown"),
                f"{source.get('relevance', 0):.2f}",
                source.get("content", "")[:100] + "..." if len(source.get("content", "")) > 100 else source.get("content", "")
            )
        
        self.console.print(table)
    
    def _display_help(self):
        """Display enhanced help information"""
        help_text = """
[bold cyan]Enhanced BASED GOD CLI - Complete Command Reference[/bold cyan]

[bold yellow]🎯 Core Commands:[/bold yellow]
• [bold]help[/bold] - Show this help message
• [bold]quit/exit/bye[/bold] - Exit the CLI gracefully
• [bold]clear[/bold] - Clear the screen
• [bold]status[/bold] - Show system status
• [bold]tools[/bold] - Show available tools

[bold green]💬 Chat & Conversation:[/bold green]
• [bold]Regular text[/bold] - General conversation
• [bold]system: [message][/bold] - With system message
• [bold]model: [model] [message][/bold] - Specify model (deepseek-chat, deepseek-coder, deepseek-reasoner)
• [bold]temp: [value] [message][/bold] - Specify temperature (0.0-2.0)

[bold cyan]🔧 FIM Completion:[/bold cyan]
• [bold]fim: [prefix] | [suffix][/bold] - Fill-in-middle completion
• [bold]fill: [prefix] | [suffix][/bold] - Alternative FIM syntax
• [bold]fim: [prefix] | [suffix] lang: [language][/bold] - With language specification
• [bold]fim: [prefix] | [suffix] model: deepseek-coder[/bold] - With model specification

[bold green]📝 Prefix Completion:[/bold green]
• [bold]prefix: [text][/bold] - Prefix completion
• [bold]continue: [text][/bold] - Alternative prefix syntax
• [bold]prefix: [text] model: [model][/bold] - With model specification
• [bold]prefix: [text] temp: [value][/bold] - With temperature

[bold magenta]🌊 Streaming Responses:[/bold magenta]
• [bold]stream: [message][/bold] - Real-time streaming response
• [bold]live: [message][/bold] - Alternative streaming syntax
• [bold]stream: [message] model: [model][/bold] - With model specification

[bold yellow]🤖 Unified Agent System:[/bold yellow]
• [bold]agent: [task][/bold] - Use unified agent system
• [bold]ai: [task][/bold] - Alternative agent syntax
• [bold]agent: conversation [message][/bold] - Agent conversation
• [bold]agent: tool_use [task][/bold] - Agent tool usage
• [bold]agent: memory_retrieval [query][/bold] - Agent memory retrieval
• [bold]agent: learning [data][/bold] - Agent learning
• [bold]agent: reasoning [problem][/bold] - Agent reasoning
• [bold]agent: planning [goal][/bold] - Agent planning

[bold blue]🔍 RAG (Retrieval-Augmented Generation):[/bold blue]
• [bold]rag: [query][/bold] - RAG query
• [bold]search: [query][/bold] - Alternative RAG syntax
• [bold]rag: [query] persona: deanna[/bold] - With persona specification

[bold white]🛠️ Tool Management:[/bold white]
• [bold]tools: list[/bold] - List available tools
• [bold]tools: status[/bold] - Show tool status
• [bold]tools: [tool_command][/bold] - Execute tool command

[bold cyan]🎛️ Mode Switching:[/bold cyan]
• [bold]mode: chat[/bold] - Switch to chat mode
• [bold]mode: fim[/bold] - Switch to FIM mode
• [bold]mode: prefix[/bold] - Switch to prefix mode
• [bold]mode: stream[/bold] - Switch to streaming mode
• [bold]mode: agent[/bold] - Switch to agent mode
• [bold]mode: rag[/bold] - Switch to RAG mode

[bold green]📊 Examples:[/bold green]
• [bold]fim: def calculate_sum(a, b): | return a + b[/bold]
• [bold]prefix: The future of artificial intelligence[/bold]
• [bold]stream: Explain quantum computing in simple terms[/bold]
• [bold]agent: Help me plan a software project[/bold]
• [bold]rag: What are the latest developments in machine learning?[/bold]
• [bold]model: deepseek-coder temp: 0.3 Write a Python function[/bold]

[bold yellow]💡 Tips:[/bold yellow]
• Use Ctrl+C to cancel streaming responses
• Combine multiple parameters for fine-tuned control
• The system remembers conversation context automatically
• All responses are saved for learning and improvement
        """
        
        self.console.print(Panel(help_text, title="[bold cyan]Enhanced CLI Help[/bold cyan]", border_style="cyan"))
    
    def _display_status(self):
        """Display system status"""
        status_text = f"""
[bold cyan]Enhanced BASED GOD CLI Status[/bold cyan]

[bold green]System Information:[/bold green]
• [bold]Current Mode:[/bold] {self.session_data.get('current_mode', 'chat')}
• [bold]Conversation History:[/bold] {len(self.session_data.get('conversation_history', []))} messages
• [bold]Active Tools:[/bold] {len(self.session_data.get('active_tools', []))}
• [bold]Streaming Active:[/bold] {self.is_streaming}

[bold yellow]Performance Metrics:[/bold yellow]
• [bold]Total Interactions:[/bold] {self.session_data.get('performance_metrics', {}).get('total_interactions', 0)}
• [bold]Successful Tool Uses:[/bold] {self.session_data.get('performance_metrics', {}).get('successful_tool_uses', 0)}
• [bold]Learning Events:[/bold] {self.session_data.get('performance_metrics', {}).get('learning_events', 0)}

[bold blue]Available Models:[/bold blue]
• [bold]deepseek-chat[/bold] - General conversation and completion
• [bold]deepseek-coder[/bold] - Code generation and analysis
• [bold]deepseek-reasoner[/bold] - Advanced reasoning and problem solving

[bold magenta]Active Features:[/bold magenta]
• [bold]FIM Completion:[/bold] ✅ Enabled
• [bold]Prefix Completion:[/bold] ✅ Enabled
• [bold]Streaming:[/bold] ✅ Enabled
• [bold]Unified Agent:[/bold] ✅ Enabled
• [bold]RAG Pipeline:[/bold] ✅ Enabled
• [bold]Vector Database:[/bold] ✅ Enabled
• [bold]SQL Database:[/bold] ✅ Enabled
        """
        
        self.console.print(Panel(status_text, title="[bold cyan]System Status[/bold cyan]", border_style="cyan"))
    
    def _display_tools(self):
        """Display available tools"""
        tools = self.tool_manager.get_available_tools()
        
        table = Table(title="Available Tools")
        table.add_column("Tool Name", style="cyan")
        table.add_column("Description", style="green")
        table.add_column("Capabilities", style="yellow")
        
        for tool in tools:
            capabilities = ", ".join(tool.capabilities[:3])  # Show first 3 capabilities
            if len(tool.capabilities) > 3:
                capabilities += "..."
            
            table.add_row(tool.name, tool.description, capabilities)
        
        self.console.print(table)
    
    def _display_tool_status(self):
        """Display tool status"""
        tools = self.tool_manager.get_available_tools()
        
        table = Table(title="Tool Status")
        table.add_column("Tool Name", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Last Used", style="yellow")
        
        for tool in tools:
            status = "✅ Active" if hasattr(tool, 'is_active') and tool.is_active else "❌ Inactive"
            last_used = getattr(tool, 'last_used', 'Never')
            
            table.add_row(tool.name, status, str(last_used))
        
        self.console.print(table)

# Backward compatibility alias for older imports
EnhancedBasedGodCLI = EnhancedBASEDGODCLI

def main():
    """Main entry point for the enhanced CLI"""
    try:
        # Create and run the enhanced CLI
        cli = EnhancedBASEDGODCLI()
        
        # Run the CLI
        asyncio.run(cli.run())
        
    except KeyboardInterrupt:
        print("\n[bold green]Goodbye![/bold green]")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        print(f"[bold red]Fatal error: {str(e)}[/bold red]")
        sys.exit(1)

if __name__ == "__main__":
    main()