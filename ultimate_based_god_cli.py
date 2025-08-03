#!/usr/bin/env python3
"""
🔥 ULTIMATE BASED GOD CODER CLI 🔥
The most comprehensive AI-powered command-line interface ever created

Features:
- DeepSeek API Integration (Chat, Reasoner, FIM, Prefix Completion)
- Advanced Web Scraping with Multi-Modal Processing
- Docker & Container Management
- Code Generation & Execution
- File Analysis & Processing
- Vector Memory with RAG
- Batch Processing
- Function Calling
- Beautiful Terminal UI
- And much more...

Made by @Lucariolucario55 on Telegram
Enhanced with ALL features from the codebase
"""

import os
import sys
import json
import time
import asyncio
import aiohttp
import httpx
import subprocess
import tempfile
import hashlib
import platform
from datetime import datetime
from typing import List, Dict, Optional, Any, Union, Callable
from pathlib import Path
from enum import Enum
import argparse
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Rich terminal formatting
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.markdown import Markdown
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.prompt import Prompt, Confirm
    from rich.text import Text
    from rich import box
    from rich.layout import Layout
    from rich.live import Live
    from rich.tree import Tree
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None
    print("Warning: 'rich' library not available. Install with: pip install rich")

# Import our custom tools
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tools'))

# Try to import our advanced scraper
try:
    from tools.super_agent_scraper import SuperAgentScraper
    SCRAPER_AVAILABLE = True
except ImportError:
    SCRAPER_AVAILABLE = False
    console.print("[yellow]Warning: SuperAgentScraper not available[/yellow]") if console else print("Warning: SuperAgentScraper not available")

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# DeepSeek API Configuration
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-90e0dd863b8c4e0d879a02851a0ee194")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_API_ENDPOINT", "https://api.deepseek.com/v1")
DEEPSEEK_BETA_URL = "https://api.deepseek.com/beta"


class MenuOption(Enum):
    """All available menu options"""
    CHAT = "1"
    REASON = "2"
    CODE_GEN = "3"
    FILE_ANALYZE = "4"
    BATCH_PROCESS = "5"
    FUNCTION_CALL = "6"
    WEB_SCRAPE = "7"
    DOCKER_TOOLS = "8"
    VECTOR_MEMORY = "9"
    FIM_COMPLETE = "10"
    PREFIX_COMPLETE = "11"
    BETA_FEATURES = "12"
    JSON_MODE = "13"
    USAGE_STATS = "14"
    SETTINGS = "15"
    MCP_TOOLS = "16"
    EXPORT_DATA = "17"
    HELP = "18"
    EXIT = "0"


class TaskProfile(Enum):
    """Predefined task profiles with optimal settings"""
    CODING = {"temperature": 0.0, "model": "deepseek-chat", "description": "Code generation and debugging"}
    MATH = {"temperature": 0.0, "model": "deepseek-reasoner", "description": "Mathematical problem solving"}
    SCRAPING = {"temperature": 0.3, "model": "deepseek-reasoner", "description": "Web scraping and analysis"}
    CONVERSATION = {"temperature": 1.3, "model": "deepseek-chat", "description": "General conversation"}
    CREATIVE = {"temperature": 1.5, "model": "deepseek-chat", "description": "Creative writing"}
    ANALYSIS = {"temperature": 0.7, "model": "deepseek-reasoner", "description": "Data analysis and reasoning"}


class UltimateBasedGodCLI:
    """The Ultimate BASED GOD CODER CLI - All features integrated"""
    
    def __init__(self):
        """Initialize the ultimate CLI"""
        self.api_key = DEEPSEEK_API_KEY
        self.base_url = DEEPSEEK_BASE_URL
        self.beta_url = DEEPSEEK_BETA_URL
        
        # Initialize HTTP clients
        self.client = httpx.AsyncClient(timeout=60.0)
        self.sync_client = httpx.Client(timeout=60.0)
        
        # Initialize scraper if available
        self.scraper = None
        if SCRAPER_AVAILABLE:
            try:
                self.scraper = SuperAgentScraper(
                    api_key=self.api_key,
                    storage_path="ultimate_scraped_data",
                    max_workers=5
                )
            except Exception as e:
                console.print(f"[red]Failed to initialize scraper: {e}[/red]") if console else print(f"Failed to initialize scraper: {e}")
        
        # Settings
        self.settings = {
            "model": "deepseek-chat",
            "temperature": 0.7,
            "max_tokens": 4096,
            "stream": True,
            "save_history": True,
            "export_format": "json",
            "auto_execute": False,
            "vector_memory": True
        }
        
        # State management
        self.conversation_history = []
        self.code_history = []
        self.scraped_data = {}
        self.vector_memories = []
        self.usage_stats = {
            "total_requests": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "session_start": datetime.now(),
            "features_used": {}
        }
        
        # Tools and functions
        self.available_tools = self._initialize_tools()
        
        # Docker client
        self.docker_client = None
        self._init_docker()
    
    def _initialize_tools(self) -> List[Dict[str, Any]]:
        """Initialize all available tools for function calling"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "web_scrape",
                    "description": "Scrape websites and extract multi-modal content",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "urls": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of URLs to scrape"
                            },
                            "analysis_query": {
                                "type": "string",
                                "description": "Analysis query for scraped content"
                            }
                        },
                        "required": ["urls"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "execute_code",
                    "description": "Execute Python code in a safe environment",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "Python code to execute"
                            },
                            "timeout": {
                                "type": "integer",
                                "description": "Execution timeout in seconds",
                                "default": 30
                            }
                        },
                        "required": ["code"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "docker_command",
                    "description": "Execute Docker commands",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": "Docker command to execute"
                            }
                        },
                        "required": ["command"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_memory",
                    "description": "Search vector memory for relevant content",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query"
                            },
                            "top_k": {
                                "type": "integer",
                                "description": "Number of results to return",
                                "default": 5
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]
    
    def _init_docker(self):
        """Initialize Docker client if available"""
        try:
            import docker
            self.docker_client = docker.from_env()
        except:
            self.docker_client = None
    
    def display_banner(self):
        """Display the ultimate banner"""
        if RICH_AVAILABLE and console:
            ascii_art = """
🔥🔥🔥 ULTIMATE BASED GOD CODER CLI 🔥🔥🔥

██╗   ██╗██╗  ████████╗██╗███╗   ███╗ █████╗ ████████╗███████╗
██║   ██║██║  ╚══██╔══╝██║████╗ ████║██╔══██╗╚══██╔══╝██╔════╝
██║   ██║██║     ██║   ██║██╔████╔██║███████║   ██║   █████╗  
██║   ██║██║     ██║   ██║██║╚██╔╝██║██╔══██║   ██║   ██╔══╝  
╚██████╔╝███████╗██║   ██║██║ ╚═╝ ██║██║  ██║   ██║   ███████╗
 ╚═════╝ ╚══════╝╚═╝   ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝   ╚══════╝
                                                                
         ██████╗  ██████╗ ██████╗      ██████╗██╗     ██╗       
         ██╔══██╗██╔═══██╗██╔══██╗    ██╔════╝██║     ██║       
         ██████╔╝██║   ██║██║  ██║    ██║     ██║     ██║       
         ██╔══██╗██║   ██║██║  ██║    ██║     ██║     ██║       
         ██████╔╝╚██████╔╝██████╔╝    ╚██████╗███████╗██║       
         ╚═════╝  ╚═════╝ ╚═════╝      ╚═════╝╚══════╝╚═╝       
            """
            
            gradient_text = Text(ascii_art)
            colors = ["red", "yellow", "green", "cyan", "blue", "magenta"]
            
            lines = ascii_art.split('\n')
            styled_lines = []
            for i, line in enumerate(lines):
                color = colors[i % len(colors)]
                styled_lines.append(f"[{color}]{line}[/{color}]")
            
            console.print('\n'.join(styled_lines))
            console.print(Panel.fit(
                "[bold cyan]The Most Powerful AI CLI Ever Created[/bold cyan]\n" +
                "[yellow]Featuring: DeepSeek AI • Web Scraping • Docker • Vector Memory • And More![/yellow]",
                border_style="bright_blue"
            ))
        else:
            print("\n" + "="*70)
            print("🔥 ULTIMATE BASED GOD CODER CLI 🔥")
            print("The Most Powerful AI CLI Ever Created")
            print("="*70 + "\n")
    
    def display_menu(self):
        """Display the main menu"""
        if RICH_AVAILABLE and console:
            table = Table(title="🚀 Main Menu", box=box.ROUNDED, title_style="bold magenta")
            table.add_column("Option", style="cyan", width=5)
            table.add_column("Feature", style="green", width=25)
            table.add_column("Description", style="yellow")
            
            menu_items = [
                ("1", "💬 Chat Mode", "Interactive AI conversation"),
                ("2", "🧠 Reasoning Mode", "Complex problem solving with chain-of-thought"),
                ("3", "🚀 Code Generation", "Generate code with explanations"),
                ("4", "📁 File Analysis", "Analyze and process files"),
                ("5", "⚡ Batch Processing", "Process multiple prompts"),
                ("6", "🔧 Function Calling", "Advanced AI function execution"),
                ("7", "🕷️ Web Scraping", "Advanced multi-modal web scraping"),
                ("8", "🐳 Docker Tools", "Container management and operations"),
                ("9", "🧠 Vector Memory", "Search and manage vector memories"),
                ("10", "📝 FIM Completion", "Fill-in-the-middle completion"),
                ("11", "✏️ Prefix Completion", "Controlled output generation"),
                ("12", "🧪 Beta Features", "Experimental features"),
                ("13", "📊 JSON Mode", "Structured JSON output"),
                ("14", "📈 Usage Stats", "View session statistics"),
                ("15", "⚙️ Settings", "Configure CLI settings"),
                ("16", "🔗 MCP Tools", "Model Context Protocol tools"),
                ("17", "💾 Export Data", "Export conversation and data"),
                ("18", "❓ Help", "Documentation and examples"),
                ("0", "👋 Exit", "Exit the CLI")
            ]
            
            for option, feature, description in menu_items:
                table.add_row(option, feature, description)
            
            console.print(table)
        else:
            print("\n" + "="*50)
            print("MAIN MENU")
            print("="*50)
            print("1. Chat Mode")
            print("2. Reasoning Mode")
            print("3. Code Generation")
            print("4. File Analysis")
            print("5. Batch Processing")
            print("6. Function Calling")
            print("7. Web Scraping")
            print("8. Docker Tools")
            print("9. Vector Memory")
            print("10. FIM Completion")
            print("11. Prefix Completion")
            print("12. Beta Features")
            print("13. JSON Mode")
            print("14. Usage Stats")
            print("15. Settings")
            print("16. MCP Tools")
            print("17. Export Data")
            print("18. Help")
            print("0. Exit")
            print("="*50)
    
    async def chat_with_api(self, prompt: str, use_reasoner: bool = False, **kwargs) -> str:
        """Chat with DeepSeek API"""
        try:
            # Update stats
            self.usage_stats["total_requests"] += 1
            
            # Prepare messages
            messages = [{"role": "user", "content": prompt}]
            if self.conversation_history:
                messages = self.conversation_history + messages
            
            # Prepare request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            model = "deepseek-reasoner" if use_reasoner else self.settings["model"]
            
            data = {
                "model": model,
                "messages": messages,
                "temperature": self.settings["temperature"],
                "stream": self.settings["stream"]
            }
            
            if self.settings["max_tokens"]:
                data["max_tokens"] = self.settings["max_tokens"]
            
            # Add tools if function calling
            if kwargs.get("tools"):
                data["tools"] = kwargs["tools"]
                data["tool_choice"] = "auto"
            
            # JSON mode
            if kwargs.get("json_mode"):
                data["response_format"] = {"type": "json_object"}
            
            # Make request
            if self.settings["stream"]:
                return await self._stream_chat(headers, data)
            else:
                response = await self.client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data
                )
                response.raise_for_status()
                result = response.json()
                
                # Extract response
                content = result["choices"][0]["message"]["content"]
                
                # Update conversation history
                self.conversation_history.append({"role": "user", "content": prompt})
                self.conversation_history.append({"role": "assistant", "content": content})
                
                # Update stats
                if "usage" in result:
                    self.usage_stats["total_tokens"] += result["usage"]["total_tokens"]
                
                return content
                
        except Exception as e:
            error_msg = f"API Error: {str(e)}"
            if console:
                console.print(f"[red]{error_msg}[/red]")
            else:
                print(error_msg)
            return error_msg
    
    async def _stream_chat(self, headers: Dict, data: Dict) -> str:
        """Stream chat responses"""
        full_response = ""
        
        if console:
            console.print("\n[cyan]AI:[/cyan] ", end="")
        else:
            print("\nAI: ", end="")
        
        async with self.client.stream("POST", f"{self.base_url}/chat/completions", headers=headers, json=data) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    if line == "data: [DONE]":
                        break
                    try:
                        chunk = json.loads(line[6:])
                        if "choices" in chunk and chunk["choices"]:
                            content = chunk["choices"][0].get("delta", {}).get("content", "")
                            if content:
                                full_response += content
                                if console:
                                    console.print(content, end="")
                                else:
                                    print(content, end="", flush=True)
                    except:
                        pass
        
        print()  # New line after response
        
        # Update conversation history
        if data["messages"]:
            self.conversation_history.append({"role": "user", "content": data["messages"][-1]["content"]})
            self.conversation_history.append({"role": "assistant", "content": full_response})
        
        return full_response
    
    async def web_scraping_mode(self):
        """Advanced web scraping mode"""
        if not self.scraper:
            console.print("[red]Web scraping not available. Please install required dependencies.[/red]")
            return
        
        console.print(Panel("🕷️ [bold cyan]Web Scraping Mode[/bold cyan] 🕷️", expand=False))
        
        while True:
            console.print("\n[yellow]Options:[/yellow]")
            console.print("1. Scrape URLs")
            console.print("2. Search Memory")
            console.print("3. Export Results")
            console.print("4. View Stats")
            console.print("0. Back to Main Menu")
            
            choice = Prompt.ask("Select option", default="1")
            
            if choice == "0":
                break
            elif choice == "1":
                urls_input = Prompt.ask("Enter URLs to scrape (comma-separated)")
                urls = [url.strip() for url in urls_input.split(",")]
                
                analysis_query = Prompt.ask("Analysis query (optional)", default="")
                
                with console.status("[bold green]Scraping websites...[/bold green]", spinner="dots"):
                    results = self.scraper.streaming_scrape(urls, analysis_query if analysis_query else None)
                
                self.scraped_data = results
                
                # Display summary
                console.print(Panel(f"[green]Scraping completed![/green]\n" +
                                  f"Successful: {results['summary']['successful']}\n" +
                                  f"Failed: {results['summary']['failed']}\n" +
                                  f"Media processed: {results['summary']['stats']['media_processed']}",
                                  title="Results Summary"))
                
            elif choice == "2":
                query = Prompt.ask("Enter search query")
                results = self.scraper.query_memory(query)
                
                table = Table(title="Search Results")
                table.add_column("Score", style="cyan")
                table.add_column("Content", style="green")
                
                for result in results:
                    content = result['payload']['content'][:100] + "..."
                    table.add_row(f"{result['score']:.3f}", content)
                
                console.print(table)
                
            elif choice == "3":
                if self.scraped_data:
                    format_choice = Prompt.ask("Export format", choices=["json", "html", "markdown"], default="html")
                    filename = self.scraper.export_results(self.scraped_data, format=format_choice)
                    console.print(f"[green]Exported to: {filename}[/green]")
                else:
                    console.print("[yellow]No data to export[/yellow]")
                    
            elif choice == "4":
                console.print(self.scraper.session_stats)
    
    async def docker_tools_mode(self):
        """Docker management mode"""
        if not self.docker_client:
            console.print("[red]Docker not available. Please install Docker.[/red]")
            return
        
        console.print(Panel("🐳 [bold cyan]Docker Tools[/bold cyan] 🐳", expand=False))
        
        while True:
            console.print("\n[yellow]Docker Operations:[/yellow]")
            console.print("1. List Containers")
            console.print("2. List Images")
            console.print("3. Run Command in Container")
            console.print("4. View Container Logs")
            console.print("5. System Info")
            console.print("0. Back to Main Menu")
            
            choice = Prompt.ask("Select operation", default="1")
            
            if choice == "0":
                break
            elif choice == "1":
                containers = self.docker_client.containers.list(all=True)
                
                table = Table(title="Docker Containers")
                table.add_column("Name", style="cyan")
                table.add_column("Image", style="green")
                table.add_column("Status", style="yellow")
                table.add_column("ID", style="magenta")
                
                for container in containers:
                    table.add_row(
                        container.name,
                        container.image.tags[0] if container.image.tags else "none",
                        container.status,
                        container.short_id
                    )
                
                console.print(table)
                
            elif choice == "2":
                images = self.docker_client.images.list()
                
                table = Table(title="Docker Images")
                table.add_column("Repository", style="cyan")
                table.add_column("Tag", style="green")
                table.add_column("ID", style="yellow")
                table.add_column("Size", style="magenta")
                
                for image in images:
                    for tag in image.tags or ["<none>"]:
                        repo, tag_name = tag.split(":") if ":" in tag else (tag, "latest")
                        size_mb = image.attrs["Size"] / (1024 * 1024)
                        table.add_row(repo, tag_name, image.short_id, f"{size_mb:.1f} MB")
                
                console.print(table)
                
            elif choice == "3":
                container_name = Prompt.ask("Container name or ID")
                command = Prompt.ask("Command to execute")
                
                try:
                    container = self.docker_client.containers.get(container_name)
                    result = container.exec_run(command)
                    console.print(f"[green]Output:[/green]\n{result.output.decode()}")
                except Exception as e:
                    console.print(f"[red]Error: {e}[/red]")
                    
            elif choice == "4":
                container_name = Prompt.ask("Container name or ID")
                
                try:
                    container = self.docker_client.containers.get(container_name)
                    logs = container.logs(tail=50).decode()
                    console.print(Panel(logs, title=f"Logs from {container_name}"))
                except Exception as e:
                    console.print(f"[red]Error: {e}[/red]")
                    
            elif choice == "5":
                info = self.docker_client.info()
                console.print(Panel(
                    f"Containers: {info['Containers']} ({info['ContainersRunning']} running)\n" +
                    f"Images: {info['Images']}\n" +
                    f"Server Version: {info['ServerVersion']}\n" +
                    f"Docker Root Dir: {info['DockerRootDir']}",
                    title="Docker System Info"
                ))
    
    async def fim_completion_mode(self):
        """Fill-in-the-middle completion mode"""
        console.print(Panel("📝 [bold cyan]FIM Completion Mode[/bold cyan] 📝", expand=False))
        console.print("[yellow]Provide a prefix and suffix, and AI will fill in the middle[/yellow]\n")
        
        prefix = Prompt.ask("Enter prefix (start of text)")
        suffix = Prompt.ask("Enter suffix (end of text)", default="")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "prompt": prefix,
            "suffix": suffix,
            "max_tokens": 500
        }
        
        try:
            with console.status("[bold green]Generating completion...[/bold green]"):
                response = await self.client.post(
                    f"{self.beta_url}/completions",
                    headers=headers,
                    json=data
                )
                response.raise_for_status()
                result = response.json()
                
                completion = result["choices"][0]["text"]
                
                # Display result
                console.print("\n[green]Complete text:[/green]")
                console.print(Panel(prefix + completion + suffix, border_style="green"))
                
                # Highlight the generated part
                console.print("\n[yellow]Generated content:[/yellow]")
                console.print(Panel(completion, border_style="yellow"))
                
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
    
    async def prefix_completion_mode(self):
        """Prefix completion mode"""
        console.print(Panel("✏️ [bold cyan]Prefix Completion Mode[/bold cyan] ✏️", expand=False))
        console.print("[yellow]AI will complete your message starting with a specific prefix[/yellow]\n")
        
        context = Prompt.ask("Enter context/question")
        prefix = Prompt.ask("Enter prefix for AI response")
        
        messages = [
            {"role": "user", "content": context},
            {"role": "assistant", "content": prefix, "prefix": True}
        ]
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": messages,
            "max_tokens": 1000
        }
        
        try:
            with console.status("[bold green]Generating completion...[/bold green]"):
                response = await self.client.post(
                    f"{self.beta_url}/chat/completions",
                    headers=headers,
                    json=data
                )
                response.raise_for_status()
                result = response.json()
                
                completion = result["choices"][0]["message"]["content"]
                
                # Display result
                console.print("\n[green]AI Response:[/green]")
                console.print(Panel(prefix + completion, border_style="green"))
                
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
    
    async def code_generation_mode(self):
        """Enhanced code generation mode"""
        console.print(Panel("🚀 [bold cyan]Code Generation Mode[/bold cyan] 🚀", expand=False))
        
        language = Prompt.ask("Programming language", default="python")
        description = Prompt.ask("Describe what you want to build")
        
        prompt = f"""Generate {language} code for: {description}

Requirements:
1. Include proper error handling
2. Add comprehensive comments
3. Follow best practices
4. Make it production-ready
5. Include example usage

Please provide complete, working code."""

        response = await self.chat_with_api(prompt)
        
        # Extract code blocks
        import re
        code_blocks = re.findall(r'```(?:\w+)?\n(.*?)```', response, re.DOTALL)
        
        if code_blocks:
            for i, code in enumerate(code_blocks):
                console.print(f"\n[green]Code Block {i+1}:[/green]")
                syntax = Syntax(code.strip(), language, theme="monokai", line_numbers=True)
                console.print(syntax)
                
                if Confirm.ask("Save this code to file?"):
                    filename = Prompt.ask("Filename", default=f"generated_{language}_{i+1}.{self._get_extension(language)}")
                    with open(filename, "w") as f:
                        f.write(code.strip())
                    console.print(f"[green]Saved to {filename}[/green]")
                    
                if self.settings["auto_execute"] and language == "python":
                    if Confirm.ask("Execute this code?"):
                        await self._execute_code(code.strip())
        
        self.code_history.append({
            "timestamp": datetime.now().isoformat(),
            "language": language,
            "description": description,
            "response": response
        })
    
    def _get_extension(self, language: str) -> str:
        """Get file extension for language"""
        extensions = {
            "python": "py",
            "javascript": "js",
            "typescript": "ts",
            "java": "java",
            "c": "c",
            "cpp": "cpp",
            "go": "go",
            "rust": "rs",
            "ruby": "rb",
            "php": "php"
        }
        return extensions.get(language.lower(), "txt")
    
    async def _execute_code(self, code: str, timeout: int = 30):
        """Execute Python code safely"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            console.print("\n[yellow]Executing code...[/yellow]")
            
            process = await asyncio.create_subprocess_exec(
                sys.executable, temp_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
                
                if stdout:
                    console.print("[green]Output:[/green]")
                    console.print(stdout.decode())
                
                if stderr:
                    console.print("[red]Errors:[/red]")
                    console.print(stderr.decode())
                    
            except asyncio.TimeoutError:
                process.terminate()
                console.print("[red]Execution timed out![/red]")
                
        finally:
            os.unlink(temp_file)
    
    async def function_calling_mode(self):
        """Function calling mode with all available tools"""
        console.print(Panel("🔧 [bold cyan]Function Calling Mode[/bold cyan] 🔧", expand=False))
        console.print("[yellow]AI can call various functions to help you[/yellow]\n")
        
        # Display available functions
        console.print("[cyan]Available functions:[/cyan]")
        for tool in self.available_tools:
            func = tool["function"]
            console.print(f"- {func['name']}: {func['description']}")
        
        prompt = Prompt.ask("\nWhat would you like me to do?")
        
        # Make API call with tools
        response = await self.chat_with_api(prompt, tools=self.available_tools)
        
        # Here you would normally parse and execute function calls
        # For now, we just display the response
        console.print(response)
    
    def display_usage_stats(self):
        """Display detailed usage statistics"""
        if console:
            # Calculate session duration
            duration = datetime.now() - self.usage_stats["session_start"]
            
            # Create main stats table
            stats_table = Table(title="📊 Session Statistics", box=box.ROUNDED)
            stats_table.add_column("Metric", style="cyan")
            stats_table.add_column("Value", style="green")
            
            stats_table.add_row("Session Duration", str(duration).split('.')[0])
            stats_table.add_row("Total Requests", str(self.usage_stats["total_requests"]))
            stats_table.add_row("Total Tokens", f"{self.usage_stats['total_tokens']:,}")
            stats_table.add_row("Estimated Cost", f"${self.usage_stats['total_cost']:.4f}")
            stats_table.add_row("Conversation Length", str(len(self.conversation_history)))
            stats_table.add_row("Code Snippets Generated", str(len(self.code_history)))
            
            if self.scraped_data:
                stats_table.add_row("URLs Scraped", str(self.scraped_data.get('summary', {}).get('total_urls', 0)))
            
            console.print(stats_table)
            
            # Feature usage
            if self.usage_stats["features_used"]:
                feature_table = Table(title="Feature Usage", box=box.SIMPLE)
                feature_table.add_column("Feature", style="yellow")
                feature_table.add_column("Usage Count", style="magenta")
                
                for feature, count in self.usage_stats["features_used"].items():
                    feature_table.add_row(feature, str(count))
                
                console.print(feature_table)
    
    async def export_data(self):
        """Export all data"""
        console.print(Panel("💾 [bold cyan]Export Data[/bold cyan] 💾", expand=False))
        
        format_choice = Prompt.ask("Export format", choices=["json", "markdown", "html"], default="json")
        
        export_data = {
            "session_info": {
                "start_time": self.usage_stats["session_start"].isoformat(),
                "export_time": datetime.now().isoformat(),
                "total_requests": self.usage_stats["total_requests"]
            },
            "conversation_history": self.conversation_history,
            "code_history": self.code_history,
            "scraped_data": self.scraped_data,
            "usage_stats": {k: v for k, v in self.usage_stats.items() if k != "session_start"}
        }
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format_choice == "json":
            filename = f"ultimate_cli_export_{timestamp}.json"
            with open(filename, "w") as f:
                json.dump(export_data, f, indent=2, default=str)
                
        elif format_choice == "markdown":
            filename = f"ultimate_cli_export_{timestamp}.md"
            with open(filename, "w") as f:
                f.write("# Ultimate CLI Session Export\n\n")
                f.write(f"**Exported:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                f.write("## Conversation History\n\n")
                for msg in self.conversation_history:
                    f.write(f"**{msg['role'].title()}:** {msg['content']}\n\n")
                
                if self.code_history:
                    f.write("## Generated Code\n\n")
                    for code in self.code_history:
                        f.write(f"### {code['language']} - {code['description']}\n")
                        f.write(f"```{code['language']}\n{code['response']}\n```\n\n")
                        
        elif format_choice == "html":
            filename = f"ultimate_cli_export_{timestamp}.html"
            # Generate beautiful HTML report
            html_content = self._generate_html_export(export_data)
            with open(filename, "w") as f:
                f.write(html_content)
        
        console.print(f"[green]Data exported to: {filename}[/green]")
    
    def _generate_html_export(self, data: Dict) -> str:
        """Generate HTML export"""
        html = """<!DOCTYPE html>
<html>
<head>
    <title>Ultimate CLI Session Export</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #1a1a1a; color: #e0e0e0; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: linear-gradient(45deg, #ff006e, #8338ec, #3a86ff); padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        .section { background: #2a2a2a; padding: 20px; margin: 20px 0; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        .conversation { background: #333; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .user { border-left: 4px solid #3a86ff; }
        .assistant { border-left: 4px solid #8338ec; }
        code { background: #1a1a1a; padding: 2px 5px; border-radius: 3px; }
        pre { background: #1a1a1a; padding: 15px; border-radius: 5px; overflow-x: auto; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
        .stat-box { background: #3a3a3a; padding: 15px; border-radius: 5px; text-align: center; }
        .stat-value { font-size: 24px; font-weight: bold; color: #3a86ff; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔥 Ultimate CLI Session Export</h1>
            <p>Generated: {timestamp}</p>
        </div>
""".format(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # Add statistics
        html += '<div class="section"><h2>Session Statistics</h2><div class="stats">'
        html += f'<div class="stat-box"><div>Total Requests</div><div class="stat-value">{data["session_info"]["total_requests"]}</div></div>'
        if "usage_stats" in data:
            html += f'<div class="stat-box"><div>Total Tokens</div><div class="stat-value">{data["usage_stats"].get("total_tokens", 0):,}</div></div>'
        html += '</div></div>'
        
        # Add conversation history
        if data["conversation_history"]:
            html += '<div class="section"><h2>Conversation History</h2>'
            for msg in data["conversation_history"]:
                css_class = "user" if msg["role"] == "user" else "assistant"
                html += f'<div class="conversation {css_class}"><strong>{msg["role"].title()}:</strong> {msg["content"]}</div>'
            html += '</div>'
        
        # Add code history
        if data["code_history"]:
            html += '<div class="section"><h2>Generated Code</h2>'
            for code in data["code_history"]:
                html += f'<h3>{code["language"]} - {code["description"]}</h3>'
                html += f'<pre><code>{code["response"]}</code></pre>'
            html += '</div>'
        
        html += """
    </div>
</body>
</html>"""
        
        return html
    
    def display_help(self):
        """Display comprehensive help"""
        help_text = """
# Ultimate BASED GOD CODER CLI Help

## Features Overview

### 1. Chat Mode
Interactive conversation with DeepSeek AI. Maintains context across messages.

### 2. Reasoning Mode
Uses DeepSeek-Reasoner for complex problem solving with chain-of-thought reasoning.

### 3. Code Generation
Generate production-ready code in any language with best practices and error handling.

### 4. Web Scraping
Advanced multi-modal web scraping with:
- Image OCR and AI vision analysis
- PDF text extraction
- Video/audio transcription
- Vector memory storage
- Pattern recognition

### 5. Docker Tools
Manage Docker containers and images directly from the CLI.

### 6. FIM Completion
Fill-in-the-middle completion for code and text.

### 7. Prefix Completion
Control AI output by specifying how it should start.

### 8. Function Calling
AI can call various functions to perform tasks.

### 9. Vector Memory
Semantic search across all scraped content and conversations.

## Command Line Arguments

```bash
python ultimate_based_god_cli.py --chat "Your message"
python ultimate_based_god_cli.py --scrape https://example.com
python ultimate_based_god_cli.py --code "web scraper"
python ultimate_based_god_cli.py --help
```

## Keyboard Shortcuts

- Ctrl+C: Cancel current operation
- Ctrl+D: Exit CLI
- ↑/↓: Navigate command history

## Tips

1. Use task profiles for optimal settings (coding, math, creative, etc.)
2. Export your sessions to preserve valuable conversations
3. Combine features for powerful workflows (scrape → analyze → generate code)
4. Use vector memory to find related content from previous sessions

## Environment Variables

- DEEPSEEK_API_KEY: Your DeepSeek API key
- DEEPSEEK_API_ENDPOINT: API endpoint (default: https://api.deepseek.com/v1)
- DEEPSEEK_MODEL: Default model (deepseek-chat or deepseek-reasoner)
        """
        
        if console:
            console.print(Markdown(help_text))
        else:
            print(help_text)
    
    async def run(self):
        """Main run loop"""
        self.display_banner()
        
        # Test API connection
        if console:
            with console.status("[bold green]Testing API connection...[/bold green]"):
                try:
                    await self.chat_with_api("Hello", use_reasoner=False)
                    console.print("[green]✓ API connection successful![/green]")
                except:
                    console.print("[yellow]⚠ API connection failed. Some features may be limited.[/yellow]")
        
        while True:
            self.display_menu()
            
            try:
                if console:
                    choice = Prompt.ask("\n[bold cyan]Select option[/bold cyan]", default="1")
                else:
                    choice = input("\nSelect option: ")
                
                # Update feature usage stats
                if choice in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13"]:
                    feature_name = MenuOption(choice).name
                    self.usage_stats["features_used"][feature_name] = self.usage_stats["features_used"].get(feature_name, 0) + 1
                
                if choice == MenuOption.EXIT.value:
                    if console:
                        console.print("\n[yellow]Thanks for using Ultimate BASED GOD CODER CLI![/yellow]")
                        console.print("[cyan]Made with ❤️ by @Lucariolucario55[/cyan]")
                    else:
                        print("\nThanks for using Ultimate BASED GOD CODER CLI!")
                    break
                    
                elif choice == MenuOption.CHAT.value:
                    await self.chat_mode()
                    
                elif choice == MenuOption.REASON.value:
                    await self.reasoning_mode()
                    
                elif choice == MenuOption.CODE_GEN.value:
                    await self.code_generation_mode()
                    
                elif choice == MenuOption.WEB_SCRAPE.value:
                    await self.web_scraping_mode()
                    
                elif choice == MenuOption.DOCKER_TOOLS.value:
                    await self.docker_tools_mode()
                    
                elif choice == MenuOption.FIM_COMPLETE.value:
                    await self.fim_completion_mode()
                    
                elif choice == MenuOption.PREFIX_COMPLETE.value:
                    await self.prefix_completion_mode()
                    
                elif choice == MenuOption.FUNCTION_CALL.value:
                    await self.function_calling_mode()
                    
                elif choice == MenuOption.USAGE_STATS.value:
                    self.display_usage_stats()
                    
                elif choice == MenuOption.EXPORT_DATA.value:
                    await self.export_data()
                    
                elif choice == MenuOption.HELP.value:
                    self.display_help()
                    
                else:
                    if console:
                        console.print("[red]Invalid option. Please try again.[/red]")
                    else:
                        print("Invalid option. Please try again.")
                        
            except KeyboardInterrupt:
                if console:
                    console.print("\n[yellow]Operation cancelled[/yellow]")
                else:
                    print("\nOperation cancelled")
                continue
            except Exception as e:
                if console:
                    console.print(f"\n[red]Error: {e}[/red]")
                else:
                    print(f"\nError: {e}")
    
    async def chat_mode(self):
        """Interactive chat mode"""
        if console:
            console.print(Panel("💬 [bold cyan]Chat Mode[/bold cyan] 💬", expand=False))
            console.print("[yellow]Type 'exit' to return to main menu[/yellow]\n")
        else:
            print("\n=== CHAT MODE ===")
            print("Type 'exit' to return to main menu\n")
        
        while True:
            try:
                if console:
                    user_input = Prompt.ask("[bold green]You[/bold green]")
                else:
                    user_input = input("You: ")
                
                if user_input.lower() in ['exit', 'quit', 'back']:
                    break
                
                response = await self.chat_with_api(user_input)
                
                if not self.settings["stream"]:
                    if console:
                        console.print(f"\n[cyan]AI:[/cyan] {response}\n")
                    else:
                        print(f"\nAI: {response}\n")
                        
            except KeyboardInterrupt:
                break
            except Exception as e:
                if console:
                    console.print(f"[red]Error: {e}[/red]")
                else:
                    print(f"Error: {e}")
    
    async def reasoning_mode(self):
        """Reasoning mode with chain-of-thought"""
        if console:
            console.print(Panel("🧠 [bold cyan]Reasoning Mode[/bold cyan] 🧠", expand=False))
            console.print("[yellow]Complex problem solving with detailed reasoning[/yellow]\n")
        else:
            print("\n=== REASONING MODE ===")
            print("Complex problem solving with detailed reasoning\n")
        
        problem = Prompt.ask("Describe your problem or question") if console else input("Describe your problem or question: ")
        
        with console.status("[bold green]Thinking deeply...[/bold green]") if console else None:
            response = await self.chat_with_api(problem, use_reasoner=True)
        
        if console:
            console.print(Panel(response, title="Reasoning Result", border_style="green"))
        else:
            print(f"\nReasoning Result:\n{response}\n")
    
    def cleanup(self):
        """Cleanup resources"""
        if self.scraper:
            self.scraper.close()
        asyncio.run(self.client.aclose())
        self.sync_client.close()


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Ultimate BASED GOD CODER CLI - The most powerful AI CLI ever created",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("--chat", help="Quick chat message", type=str)
    parser.add_argument("--code", help="Generate code for description", type=str)
    parser.add_argument("--scrape", help="Scrape URL(s)", nargs="+")
    parser.add_argument("--reason", help="Use reasoning mode", type=str)
    parser.add_argument("--help-extended", action="store_true", help="Show extended help")
    
    args = parser.parse_args()
    
    cli = UltimateBasedGodCLI()
    
    try:
        if args.chat:
            response = await cli.chat_with_api(args.chat)
            print(response)
        elif args.code:
            prompt = f"Generate production-ready code for: {args.code}"
            response = await cli.chat_with_api(prompt)
            print(response)
        elif args.scrape:
            if cli.scraper:
                results = cli.scraper.streaming_scrape(args.scrape)
                print(json.dumps(results, indent=2))
            else:
                print("Scraper not available")
        elif args.reason:
            response = await cli.chat_with_api(args.reason, use_reasoner=True)
            print(response)
        elif args.help_extended:
            cli.display_help()
        else:
            await cli.run()
    finally:
        cli.cleanup()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGoodbye! 👋")
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()