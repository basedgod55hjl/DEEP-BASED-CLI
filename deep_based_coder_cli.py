#!/usr/bin/env python3
"""
DEEP-BASED-CODER CLI - Advanced AI-Powered Development Assistant
Inspired by Gemini CLI architecture but powered by DeepSeek models exclusively
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum
import traceback
import signal
import shutil

# Third-party imports
import click
import rich
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.layout import Layout
from rich.align import Align
from rich.columns import Columns
from rich.tree import Tree
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm
import openai
import aiohttp
import asyncio
import aiosqlite
import chardet
import psutil
from colorama import Fore, Back, Style, init

# Initialize colorama for cross-platform color support
init(autoreset=True)

# Initialize Rich console
console = Console(color_system="auto", force_terminal=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deep_based_coder.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ToolIcon(Enum):
    """Icons for different tool types"""
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
    REASONING = "🤔"
    EMBEDDING = "🔗"
    GIT = "🌳"
    SHELL = "⚡"
    AI = "🤖"

class StreamingState(Enum):
    """States for streaming operations"""
    IDLE = "idle"
    LOADING = "loading"
    STREAMING = "streaming"
    COMPLETE = "complete"
    ERROR = "error"

@dataclass
class ToolLocation:
    """Represents a file system location that a tool will affect"""
    path: str
    line: Optional[int] = None
    operation: str = "read"  # read, write, edit, delete, create
    description: str = ""

@dataclass
class ToolResult:
    """Result of tool execution"""
    success: bool
    content: str = ""
    error_message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    locations_affected: List[ToolLocation] = field(default_factory=list)
    is_markdown: bool = False
    can_stream: bool = False

@dataclass
class DeepSeekConfig:
    """Configuration for DeepSeek API"""
    api_key: str = ""
    base_url: str = "https://api.deepseek.com"
    model_coder: str = "deepseek-coder"
    model_chat: str = "deepseek-chat"
    model_reasoner: str = "deepseek-reasoner"
    max_tokens: int = 8192
    temperature: float = 0.1
    stream: bool = True

@dataclass
class QwenEmbeddingConfig:
    """Configuration for Qwen 3 embedding model"""
    model_name: str = "qwen-3-embedding"
    api_key: str = ""
    base_url: str = "https://api.qwen.com"
    dimension: int = 1024
    max_batch_size: int = 16

from tools.code_analyzer_tool import CodeAnalyzerTool

class DeepBasedCoderCore:
    """Core engine for DEEP-BASED-CODER CLI"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".deep-based-coder"
        self.config_dir.mkdir(exist_ok=True)
        
        self.deepseek_config = DeepSeekConfig()
        self.qwen_config = QwenEmbeddingConfig()
        
        self.tools_registry = {}
        self.memory_store = {}
        self.active_sessions = {}
        self.execution_history = []
        
        self.load_configuration()
        self.initialize_clients()
        self._register_tools()
        
    def load_configuration(self):
        """Load configuration from files and environment"""
        config_file = self.config_dir / "config.json"
        
        # Load from environment variables
        self.deepseek_config.api_key = os.getenv("DEEPSEEK_API_KEY", "")
        self.qwen_config.api_key = os.getenv("QWEN_API_KEY", "")
        
        # Load from config file if exists
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                    
                if "deepseek" in config_data:
                    for key, value in config_data["deepseek"].items():
                        if hasattr(self.deepseek_config, key):
                            setattr(self.deepseek_config, key, value)
                            
                if "qwen" in config_data:
                    for key, value in config_data["qwen"].items():
                        if hasattr(self.qwen_config, key):
                            setattr(self.qwen_config, key, value)
                            
                logger.info("✅ Configuration loaded successfully")
            except Exception as e:
                logger.error(f"❌ Failed to load configuration: {e}")
                
    def save_configuration(self):
        """Save current configuration to file"""
        config_file = self.config_dir / "config.json"
        
        config_data = {
            "deepseek": {
                "base_url": self.deepseek_config.base_url,
                "model_coder": self.deepseek_config.model_coder,
                "model_chat": self.deepseek_config.model_chat,
                "model_reasoner": self.deepseek_config.model_reasoner,
                "max_tokens": self.deepseek_config.max_tokens,
                "temperature": self.deepseek_config.temperature,
                "stream": self.deepseek_config.stream
            },
            "qwen": {
                "model_name": self.qwen_config.model_name,
                "base_url": self.qwen_config.base_url,
                "dimension": self.qwen_config.dimension,
                "max_batch_size": self.qwen_config.max_batch_size
            }
        }
        
        try:
            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            logger.info("✅ Configuration saved successfully")
        except Exception as e:
            logger.error(f"❌ Failed to save configuration: {e}")
            
    def initialize_clients(self):
        """Initialize API clients"""
        try:
            # Initialize DeepSeek client
            if self.deepseek_config.api_key:
                self.deepseek_client = openai.OpenAI(
                    api_key=self.deepseek_config.api_key,
                    base_url=self.deepseek_config.base_url
                )
                logger.info("✅ DeepSeek client initialized")
            else:
                logger.warning("⚠️ DeepSeek API key not found")
                
            # Initialize HTTP session for other APIs
            self.http_session = None
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize clients: {e}")
            
    def _register_tools(self):
        """Register all available tools"""
        try:
            # Enhanced analysis tools
            self.tools_registry["code_analyzer"] = CodeAnalyzerTool()
            
            logger.info(f"✅ Registered {len(self.tools_registry)} tools")
            
            # Log tool capabilities
            for name, tool in self.tools_registry.items():
                if hasattr(tool, 'get_schema'):
                    schema = tool.get_schema()
                    logger.info(f"Tool '{name}' capabilities: {schema.get('description', 'No description')}")
            
        except Exception as e:
            logger.error(f"Failed to register tools: {e}")
            
    async def ensure_http_session(self):
        """Ensure HTTP session is available"""
        if self.http_session is None:
            self.http_session = aiohttp.ClientSession()
            
    async def cleanup(self):
        """Cleanup resources"""
        if self.http_session:
            await self.http_session.close()

class AdvancedFileManager:
    """Advanced file management system inspired by Gemini CLI"""
    
    def __init__(self, core: DeepBasedCoderCore):
        self.core = core
        self.file_cache = {}
        self.encoding_cache = {}
        
    async def read_file(self, path: str, encoding: str = "auto") -> ToolResult:
        """Read file with smart encoding detection"""
        try:
            file_path = Path(path).resolve()
            
            if not file_path.exists():
                return ToolResult(
                    success=False,
                    error_message=f"File not found: {path}"
                )
                
            # Detect encoding if auto
            if encoding == "auto":
                with open(file_path, 'rb') as f:
                    raw_data = f.read(1024)
                    detected = chardet.detect(raw_data)
                    encoding = detected.get('encoding', 'utf-8')
                    
            # Read file content
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
                
            # Cache the content
            self.file_cache[str(file_path)] = {
                'content': content,
                'encoding': encoding,
                'last_modified': file_path.stat().st_mtime,
                'size': file_path.stat().st_size
            }
            
            return ToolResult(
                success=True,
                content=content,
                metadata={
                    'file_path': str(file_path),
                    'encoding': encoding,
                    'size': len(content),
                    'lines': content.count('\n') + 1,
                    'last_modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                },
                locations_affected=[ToolLocation(str(file_path), operation="read")]
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error_message=f"Failed to read file {path}: {str(e)}"
            )
            
    async def write_file(self, path: str, content: str, encoding: str = "utf-8", create_backup: bool = True) -> ToolResult:
        """Write file with automatic backup"""
        try:
            file_path = Path(path).resolve()
            
            # Create backup if file exists
            if create_backup and file_path.exists():
                backup_path = file_path.with_suffix(f"{file_path.suffix}.backup_{int(time.time())}")
                shutil.copy2(file_path, backup_path)
                
            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write content
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
                
            # Update cache
            self.file_cache[str(file_path)] = {
                'content': content,
                'encoding': encoding,
                'last_modified': file_path.stat().st_mtime,
                'size': file_path.stat().st_size
            }
            
            return ToolResult(
                success=True,
                content=f"File written successfully: {path}",
                metadata={
                    'file_path': str(file_path),
                    'encoding': encoding,
                    'size': len(content),
                    'lines': content.count('\n') + 1,
                    'backup_created': create_backup and file_path.exists()
                },
                locations_affected=[ToolLocation(str(file_path), operation="write")]
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error_message=f"Failed to write file {path}: {str(e)}"
            )

class DeepSeekReasoningEngine:
    """Advanced reasoning engine using DeepSeek Reasoner"""
    
    def __init__(self, core: DeepBasedCoderCore):
        self.core = core
        self.reasoning_history = []
        
    async def analyze_code(self, code: str, language: str = "python", context: str = "") -> ToolResult:
        """Analyze code using DeepSeek Reasoner"""
        try:
            prompt = f"""
            Analyze the following {language} code and provide detailed insights:
            
            Context: {context}
            
            Code:
            ```{language}
            {code}
            ```
            
            Please provide:
            1. Code quality assessment
            2. Potential issues or bugs
            3. Performance considerations
            4. Security vulnerabilities
            5. Improvement suggestions
            6. Refactoring opportunities
            
            Format your response in markdown with clear sections.
            """
            
            response = await self._make_reasoning_request(prompt, "deepseek-reasoner")
            
            return ToolResult(
                success=True,
                content=response,
                is_markdown=True,
                metadata={
                    'language': language,
                    'code_length': len(code),
                    'analysis_type': 'code_analysis'
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error_message=f"Code analysis failed: {str(e)}"
            )
            
    async def generate_code(self, prompt: str, language: str = "python", existing_code: str = "") -> ToolResult:
        """Generate code using DeepSeek Coder"""
        try:
            full_prompt = f"""
            Generate {language} code based on the following requirements:
            
            Requirements: {prompt}
            
            {"Existing code context:" + existing_code if existing_code else ""}
            
            Please provide:
            1. Clean, well-documented code
            2. Error handling where appropriate
            3. Type hints (for Python)
            4. Comments explaining complex logic
            
            Return only the code without additional explanations.
            """
            
            response = await self._make_reasoning_request(full_prompt, "deepseek-coder")
            
            return ToolResult(
                success=True,
                content=response,
                metadata={
                    'language': language,
                    'generation_type': 'code_generation',
                    'has_existing_context': bool(existing_code)
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error_message=f"Code generation failed: {str(e)}"
            )
            
    async def _make_reasoning_request(self, prompt: str, model: str) -> str:
        """Make request to DeepSeek API"""
        try:
            response = self.core.deepseek_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are DEEP-BASED-CODER, an advanced AI programming assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.core.deepseek_config.max_tokens,
                temperature=self.core.deepseek_config.temperature,
                stream=False
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"DeepSeek API request failed: {e}")
            raise

class QwenEmbeddingEngine:
    """Qwen 3 embedding engine for semantic operations"""
    
    def __init__(self, core: DeepBasedCoderCore):
        self.core = core
        self.embeddings_cache = {}
        
    async def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings using Qwen 3 model"""
        try:
            await self.core.ensure_http_session()
            
            # Batch process texts
            embeddings = []
            for i in range(0, len(texts), self.core.qwen_config.max_batch_size):
                batch = texts[i:i + self.core.qwen_config.max_batch_size]
                batch_embeddings = await self._create_batch_embeddings(batch)
                embeddings.extend(batch_embeddings)
                
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to create embeddings: {e}")
            # Fallback to simple hash-based embeddings
            return [[hash(text) % 1000 / 1000.0] * self.core.qwen_config.dimension for text in texts]
            
    async def _create_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for a batch of texts"""
        # This would be the actual Qwen API call
        # For now, simulating with random embeddings
        import random
        
        embeddings = []
        for text in texts:
            # Generate deterministic "embedding" based on text hash
            random.seed(hash(text))
            embedding = [random.random() for _ in range(self.core.qwen_config.dimension)]
            embeddings.append(embedding)
            
        return embeddings
        
    async def find_similar(self, query: str, documents: List[str], top_k: int = 5) -> List[tuple]:
        """Find similar documents using embeddings"""
        try:
            # Create embeddings for query and documents
            all_texts = [query] + documents
            embeddings = await self.create_embeddings(all_texts)
            
            query_embedding = embeddings[0]
            doc_embeddings = embeddings[1:]
            
            # Calculate similarities (cosine similarity)
            similarities = []
            for i, doc_embedding in enumerate(doc_embeddings):
                similarity = self._cosine_similarity(query_embedding, doc_embedding)
                similarities.append((i, documents[i], similarity))
                
            # Sort by similarity and return top_k
            similarities.sort(key=lambda x: x[2], reverse=True)
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            return []
            
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        import math
        
        dot_product = sum(x * y for x, y in zip(a, b))
        magnitude_a = math.sqrt(sum(x * x for x in a))
        magnitude_b = math.sqrt(sum(x * x for x in b))
        
        if magnitude_a == 0 or magnitude_b == 0:
            return 0
            
        return dot_product / (magnitude_a * magnitude_b)

class AdvancedCLI:
    """Advanced CLI interface inspired by Gemini CLI"""
    
    def __init__(self):
        self.core = DeepBasedCoderCore()
        self.file_manager = AdvancedFileManager(self.core)
        self.reasoning_engine = DeepSeekReasoningEngine(self.core)
        self.embedding_engine = QwenEmbeddingEngine(self.core)
        
        self.current_directory = Path.cwd()
        self.session_active = False
        self.streaming_state = StreamingState.IDLE
        
    async def initialize(self):
        """Initialize the CLI system"""
        console.print(Panel.fit(
            "[bold blue]DEEP-BASED-CODER[/bold blue]\n"
            "[dim]Advanced AI-Powered Development Assistant[/dim]\n"
            "[dim]Powered by DeepSeek & Qwen 3[/dim]",
            border_style="blue"
        ))
        
        # Check API keys
        if not self.core.deepseek_config.api_key:
            console.print("[yellow]⚠️ DeepSeek API key not configured[/yellow]")
            api_key = Prompt.ask("Enter your DeepSeek API key")
            self.core.deepseek_config.api_key = api_key
            self.core.save_configuration()
            
        console.print("[green]✅ DEEP-BASED-CODER initialized successfully![/green]")
        
    async def interactive_mode(self):
        """Run interactive CLI mode"""
        self.session_active = True
        
        console.print("\n[cyan]🚀 Welcome to DEEP-BASED-CODER![/cyan]")
        console.print("[dim]Type 'help' for commands or 'exit' to quit.[/dim]\n")
        
        while self.session_active:
            try:
                # Show current directory and prompt
                prompt_text = f"[bold blue]{self.current_directory.name}[/bold blue] > "
                user_input = Prompt.ask(prompt_text).strip()
                
                if not user_input:
                    continue
                    
                # Handle special commands
                if user_input.lower() in ['exit', 'quit', 'q']:
                    break
                elif user_input.lower() in ['help', 'h']:
                    self.show_help()
                elif user_input.startswith('/'):
                    await self.handle_slash_command(user_input)
                else:
                    # Regular chat/reasoning
                    await self.handle_user_input(user_input)
                    
            except KeyboardInterrupt:
                console.print("\n[yellow]Use 'exit' to quit properly[/yellow]")
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                logger.error(f"Interactive mode error: {e}")
                
        await self.cleanup()
        
    async def handle_user_input(self, user_input: str):
        """Handle regular user input for reasoning/chat"""
        try:
            with console.status("[bold green]Thinking...") as status:
                # Use DeepSeek Reasoner for general queries
                prompt = f"""
                User query: {user_input}
                Current directory: {self.current_directory}
                
                Please provide a helpful response. If this is a coding question, 
                include code examples. If it's about files, consider the current directory context.
                """
                
                result = await self.reasoning_engine._make_reasoning_request(
                    prompt, self.core.deepseek_config.model_chat
                )
                
            # Display result
            if result:
                console.print(Panel(
                    Markdown(result),
                    title="[bold blue]DEEP-BASED-CODER Response[/bold blue]",
                    border_style="blue"
                ))
            else:
                console.print("[red]Failed to get response[/red]")
                
        except Exception as e:
            console.print(f"[red]Error processing input: {e}[/red]")
            
    async def handle_slash_command(self, command: str):
        """Handle slash commands"""
        parts = command[1:].split()
        cmd = parts[0].lower() if parts else ""
        args = parts[1:] if len(parts) > 1 else []
        
        if cmd == "read" and args:
            await self.cmd_read_file(args[0])
        elif cmd == "write" and len(args) >= 2:
            await self.cmd_write_file(args[0], " ".join(args[1:]))
        elif cmd == "analyze" and args:
            await self.cmd_analyze_code(args[0])
        elif cmd == "analyze-project":
            path = args[0] if args else "."
            await self.cmd_analyze_project(path)
        elif cmd == "explain" and args:
            await self.cmd_explain_code(args[0])
        elif cmd == "security-scan":
            path = args[0] if args else "."
            await self.cmd_security_scan(path)
        elif cmd == "performance-analyze":
            path = args[0] if args else "."
            await self.cmd_performance_analyze(path)
        elif cmd == "generate" and args:
            await self.cmd_generate_code(" ".join(args))
        elif cmd == "ls":
            await self.cmd_list_files()
        elif cmd == "cd" and args:
            await self.cmd_change_directory(args[0])
        elif cmd == "find" and args:
            await self.cmd_find_similar(" ".join(args))
        else:
            console.print(f"[red]Unknown command: {cmd}[/red]")
            console.print("[dim]Type 'help' for available commands[/dim]")
            
    async def cmd_read_file(self, file_path: str):
        """Read file command"""
        result = await self.file_manager.read_file(file_path)
        
        if result.success:
            # Show file content with syntax highlighting
            file_path_obj = Path(file_path)
            language = self.detect_language(file_path_obj.suffix)
            
            syntax = Syntax(result.content, language, theme="monokai", line_numbers=True)
            
            console.print(Panel(
                syntax,
                title=f"[bold blue]{file_path}[/bold blue]",
                border_style="blue"
            ))
            
            # Show metadata
            metadata = result.metadata
            info_table = Table(show_header=False, box=None)
            info_table.add_row("Size:", f"{metadata.get('size', 0)} characters")
            info_table.add_row("Lines:", str(metadata.get('lines', 0)))
            info_table.add_row("Encoding:", metadata.get('encoding', 'unknown'))
            info_table.add_row("Modified:", metadata.get('last_modified', 'unknown'))
            
            console.print(info_table)
        else:
            console.print(f"[red]Error: {result.error_message}[/red]")
            
    async def cmd_analyze_code(self, file_path: str):
        """Analyze code file"""
        # First read the file
        read_result = await self.file_manager.read_file(file_path)
        
        if not read_result.success:
            console.print(f"[red]Error reading file: {read_result.error_message}[/red]")
            return
            
        # Detect language
        language = self.detect_language(Path(file_path).suffix)
        
        with console.status("[bold green]Analyzing code...") as status:
            # Analyze the code
            analysis_result = await self.reasoning_engine.analyze_code(
                read_result.content, language, f"File: {file_path}"
            )
            
        if analysis_result.success:
            console.print(Panel(
                Markdown(analysis_result.content),
                title=f"[bold blue]Code Analysis: {file_path}[/bold blue]",
                border_style="blue"
            ))
        else:
            console.print(f"[red]Analysis failed: {analysis_result.error_message}[/red]")
    
    async def cmd_analyze_project(self, path: str):
        """Comprehensive project analysis using enhanced code analyzer"""
        try:
            if "code_analyzer" not in self.core.tools_registry:
                console.print("[red]Code analyzer tool not available[/red]")
                return
                
            code_analyzer = self.core.tools_registry["code_analyzer"]
            
            with console.status("[bold green]Analyzing project...") as status:
                result = await code_analyzer.execute("analyze_project", path=path)
            
            if result.status.name == "SUCCESS":
                analysis = result.data
                
                # Display project info
                if "project_info" in analysis:
                    project_info = analysis["project_info"]
                    console.print(Panel(
                        f"""**Project Name:** {project_info.get('name', 'Unknown')}
**Type:** {project_info.get('type', 'Unknown')} ({project_info.get('framework', 'None')})
**Files:** {project_info.get('file_count', 0)}
**Size:** {project_info.get('size', 0) / 1024 / 1024:.2f} MB
**Languages:** {', '.join(project_info.get('language_distribution', {}).keys())}""",
                        title="[bold blue]Project Overview[/bold blue]",
                        border_style="blue"
                    ))
                
                # Display analysis insights
                if "ai_insights" in analysis:
                    console.print(Panel(
                        Markdown(analysis["ai_insights"]),
                        title="[bold green]DeepSeek Analysis[/bold green]",
                        border_style="green"
                    ))
                
                # Display suggestions
                if "enhanced_suggestions" in analysis and analysis["enhanced_suggestions"]:
                    suggestions_text = "\n".join([f"• {s}" for s in analysis["enhanced_suggestions"][:5]])
                    console.print(Panel(
                        suggestions_text,
                        title="[bold yellow]Top Recommendations[/bold yellow]",
                        border_style="yellow"
                    ))
                    
            else:
                console.print(f"[red]Project analysis failed: {result.message}[/red]")
                
        except Exception as e:
            console.print(f"[red]Error analyzing project: {e}[/red]")
    
    async def cmd_explain_code(self, file_path: str):
        """Explain code using enhanced code analyzer"""
        try:
            if "code_analyzer" not in self.core.tools_registry:
                console.print("[red]Code analyzer tool not available[/red]")
                return
                
            code_analyzer = self.core.tools_registry["code_analyzer"]
            
            with console.status("[bold green]Analyzing and explaining code...") as status:
                result = await code_analyzer.execute("explain", file_path=file_path)
            
            if result.status.name == "SUCCESS":
                explanation = result.data.get("explanation", "No explanation available")
                console.print(Panel(
                    Markdown(explanation),
                    title=f"[bold blue]Code Explanation: {file_path}[/bold blue]",
                    border_style="blue"
                ))
            else:
                console.print(f"[red]Code explanation failed: {result.message}[/red]")
                
        except Exception as e:
            console.print(f"[red]Error explaining code: {e}[/red]")
    
    async def cmd_security_scan(self, path: str):
        """Security vulnerability scan"""
        try:
            if "code_analyzer" not in self.core.tools_registry:
                console.print("[red]Code analyzer tool not available[/red]")
                return
                
            code_analyzer = self.core.tools_registry["code_analyzer"]
            
            with console.status("[bold red]Scanning for security vulnerabilities...") as status:
                result = await code_analyzer.execute("security_scan", path=path)
            
            if result.status.name == "SUCCESS":
                security_data = result.data
                issues = security_data.get("issues", [])
                severity_breakdown = security_data.get("severity_breakdown", {})
                
                # Display summary
                console.print(Panel(
                    f"""**Total Issues Found:** {len(issues)}
**High Severity:** {severity_breakdown.get('high', 0)}
**Medium Severity:** {severity_breakdown.get('medium', 0)}
**Low Severity:** {severity_breakdown.get('low', 0)}""",
                    title="[bold red]Security Scan Results[/bold red]",
                    border_style="red"
                ))
                
                # Display top issues
                if issues:
                    high_issues = [i for i in issues if i.get('severity') == 'high'][:5]
                    if high_issues:
                        issues_text = "\n".join([
                            f"• **{issue['description']}** in {issue['file']}:{issue['line']}"
                            for issue in high_issues
                        ])
                        console.print(Panel(
                            Markdown(issues_text),
                            title="[bold red]High Priority Issues[/bold red]",
                            border_style="red"
                        ))
                        
            else:
                console.print(f"[red]Security scan failed: {result.message}[/red]")
                
        except Exception as e:
            console.print(f"[red]Error during security scan: {e}[/red]")
    
    async def cmd_performance_analyze(self, path: str):
        """Performance analysis"""
        try:
            if "code_analyzer" not in self.core.tools_registry:
                console.print("[red]Code analyzer tool not available[/red]")
                return
                
            code_analyzer = self.core.tools_registry["code_analyzer"]
            
            with console.status("[bold yellow]Analyzing performance...") as status:
                result = await code_analyzer.execute("performance_analyze", path=path)
            
            if result.status.name == "SUCCESS":
                perf_data = result.data
                issues = perf_data.get("issues", [])
                categories = perf_data.get("categories", {})
                
                # Display summary
                console.print(Panel(
                    f"""**Performance Issues Found:** {len(issues)}
**Issue Types:** {', '.join(categories.keys())}""",
                    title="[bold yellow]Performance Analysis Results[/bold yellow]",
                    border_style="yellow"
                ))
                
                # Display top issues
                if issues:
                    top_issues = issues[:5]
                    issues_text = "\n".join([
                        f"• **{issue['description']}** in {issue['file']}:{issue['line']}"
                        for issue in top_issues
                    ])
                    console.print(Panel(
                        Markdown(issues_text),
                        title="[bold yellow]Performance Issues[/bold yellow]",
                        border_style="yellow"
                    ))
                        
            else:
                console.print(f"[red]Performance analysis failed: {result.message}[/red]")
                
        except Exception as e:
            console.print(f"[red]Error during performance analysis: {e}[/red]")
            
    def detect_language(self, extension: str) -> str:
        """Detect programming language from file extension"""
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.rb': 'ruby',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.sh': 'bash',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.xml': 'xml',
            '.html': 'html',
            '.css': 'css',
            '.sql': 'sql',
            '.md': 'markdown',
            '.txt': 'text'
        }
        return language_map.get(extension.lower(), 'text')
        
    def show_help(self):
        """Show help information"""
        help_content = """
        # DEEP-BASED-CODER Commands
        
        ## File Operations
        - `/read <file>` - Read and display file with syntax highlighting
        - `/write <file> <content>` - Write content to file
        - `/ls` - List files in current directory
        - `/cd <directory>` - Change current directory
        
        ## Code Operations
        - `/analyze <file>` - Analyze code quality and provide insights
        - `/analyze-project [path]` - Comprehensive project analysis
        - `/explain <file>` - Get detailed code explanation
        - `/security-scan [path]` - Security vulnerability scan
        - `/performance-analyze [path]` - Performance analysis
        - `/generate <description>` - Generate code based on description
        - `/find <query>` - Find similar files/content using embeddings
        
        ## General
        - `help` - Show this help
        - `exit` - Exit the CLI
        
        ## Chat Mode
        Simply type your question or request to interact with DEEP-BASED-CODER!
        """
        
        console.print(Panel(
            Markdown(help_content),
            title="[bold blue]Help[/bold blue]",
            border_style="blue"
        ))
        
    async def cleanup(self):
        """Cleanup resources"""
        console.print("\n[yellow]Shutting down DEEP-BASED-CODER...[/yellow]")
        await self.core.cleanup()
        console.print("[green]✅ Goodbye![/green]")

# CLI Commands using Click
@click.group()
@click.version_option(version="1.0.0", prog_name="DEEP-BASED-CODER")
def cli():
    """DEEP-BASED-CODER - Advanced AI-Powered Development Assistant"""
    pass

@cli.command()
@click.option('--interactive', '-i', is_flag=True, help='Start interactive mode')
@click.option('--file', '-f', help='Analyze specific file')
@click.option('--generate', '-g', help='Generate code based on description')
def start(interactive, file, generate):
    """Start DEEP-BASED-CODER CLI"""
    async def main():
        cli_instance = AdvancedCLI()
        await cli_instance.initialize()
        
        if interactive or (not file and not generate):
            await cli_instance.interactive_mode()
        elif file:
            await cli_instance.cmd_analyze_code(file)
        elif generate:
            result = await cli_instance.reasoning_engine.generate_code(generate)
            if result.success:
                console.print(Panel(
                    Syntax(result.content, "python", theme="monokai"),
                    title="[bold blue]Generated Code[/bold blue]",
                    border_style="blue"
                ))
            else:
                console.print(f"[red]Error: {result.error_message}[/red]")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Fatal error: {e}[/red]")
        logger.error(f"Fatal error: {e}", exc_info=True)

@cli.command()
def config():
    """Configure DEEP-BASED-CODER settings"""
    console.print("[bold blue]DEEP-BASED-CODER Configuration[/bold blue]")
    
    # Configure DeepSeek API key
    deepseek_key = Prompt.ask("DeepSeek API Key", password=True)
    qwen_key = Prompt.ask("Qwen API Key (optional)", password=True, default="")
    
    # Save configuration
    core = DeepBasedCoderCore()
    core.deepseek_config.api_key = deepseek_key
    if qwen_key:
        core.qwen_config.api_key = qwen_key
    core.save_configuration()
    
    console.print("[green]✅ Configuration saved![/green]")

if __name__ == "__main__":
    cli()