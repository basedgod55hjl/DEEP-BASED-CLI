#!/usr/bin/env python3
"""
🚀 BASED CODER CLI - Enhanced AI-Powered Command Line Interface
Made by @Lucariolucario55 on Telegram

Features:
- Rainbow CLI interface with colorful agents
- Multi-round conversations with context caching
- Function calls and reasoning capabilities
- FIM and prefix completion
- Local and cloud embedding systems
- RAG pipeline with vector search
- Memory and persona management
- DeepSeek integration with all features
- Full PC access with OS operations
- Prefix commands for quick access
"""

import asyncio
import json
import logging
import sys
import os
import subprocess
import platform
import psutil
import shutil
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
import numpy as np

# Initialize colorama for Windows compatibility
colorama.init()

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

# Import our tools and systems
from tools.unified_agent_system import UnifiedAgentSystem
from tools.simple_embedding_tool import SimpleEmbeddingTool
from tools.sql_database_tool import SQLDatabaseTool
from tools.llm_query_tool import LLMQueryTool
from tools.fim_completion_tool import FIMCompletionTool
from tools.prefix_completion_tool import PrefixCompletionTool
from tools.rag_pipeline_tool import RAGPipelineTool
from tools.reasoning_engine import ReasoningEngine
from tools.memory_tool import MemoryTool
from tools.vector_database_tool import VectorDatabaseTool
from tools.deepseek_coder_tool import DeepSeekCoderTool
from tools.tool_manager import ToolManager

# Set up rich console
console = Console()

class SystemAccessTool:
    """Tool for full PC access and OS operations"""
    
    def __init__(self):
        self.system_info = self._get_system_info()
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        return {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "architecture": platform.architecture(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "disk_usage": psutil.disk_usage('/').total if os.path.exists('/') else psutil.disk_usage('C:\\').total
        }
    
    async def execute_command(self, command: str, shell: bool = True) -> Dict[str, Any]:
        """Execute system command"""
        try:
            result = subprocess.run(
                command, 
                shell=shell, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": str(e),
                "returncode": -1
            }
    
    async def get_file_info(self, path: str) -> Dict[str, Any]:
        """Get file information"""
        try:
            file_path = Path(path)
            if file_path.exists():
                stat = file_path.stat()
                return {
                    "exists": True,
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "is_file": file_path.is_file(),
                    "is_dir": file_path.is_dir(),
                    "permissions": oct(stat.st_mode)[-3:]
                }
            else:
                return {"exists": False}
        except Exception as e:
            return {"exists": False, "error": str(e)}
    
    async def list_directory(self, path: str = ".") -> Dict[str, Any]:
        """List directory contents"""
        try:
            dir_path = Path(path)
            if dir_path.exists() and dir_path.is_dir():
                items = []
                for item in dir_path.iterdir():
                    try:
                        stat = item.stat()
                        items.append({
                            "name": item.name,
                            "type": "file" if item.is_file() else "directory",
                            "size": stat.st_size if item.is_file() else None,
                            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                        })
                    except:
                        continue
                return {"success": True, "items": items}
            else:
                return {"success": False, "error": "Directory not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def read_file(self, path: str) -> Dict[str, Any]:
        """Read file contents"""
        try:
            file_path = Path(path)
            if file_path.exists() and file_path.is_file():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return {"success": True, "content": content}
            else:
                return {"success": False, "error": "File not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def write_file(self, path: str, content: str) -> Dict[str, Any]:
        """Write content to file"""
        try:
            file_path = Path(path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def create_directory(self, path: str) -> Dict[str, Any]:
        """Create directory"""
        try:
            dir_path = Path(path)
            dir_path.mkdir(parents=True, exist_ok=True)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def delete_file(self, path: str) -> Dict[str, Any]:
        """Delete file or directory"""
        try:
            item_path = Path(path)
            if item_path.exists():
                if item_path.is_file():
                    item_path.unlink()
                else:
                    shutil.rmtree(item_path)
                return {"success": True}
            else:
                return {"success": False, "error": "File not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_process_info(self) -> Dict[str, Any]:
        """Get running processes information"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except:
                    continue
            return {"success": True, "processes": processes}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        try:
            return {
                "success": True,
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent if os.path.exists('/') else psutil.disk_usage('C:\\').percent,
                "system_info": self.system_info
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

class RainbowCLI:
    """Rainbow CLI interface with colorful agents and enhanced features"""
    
    def __init__(self):
        self.console = console
        self.tool_manager = ToolManager()
        self.agent_system = None
        self.current_session = None
        self.conversation_history = []
        self.context_cache = {}
        self.rainbow_colors = [
            Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, 
            Fore.BLUE, Fore.MAGENTA, Fore.WHITE
        ]
        
        # Initialize tools
        self.embedding_tool = SimpleEmbeddingTool()
        self.sql_tool = SQLDatabaseTool()
        self.llm_tool = LLMQueryTool()
        self.fim_tool = FIMCompletionTool()
        self.prefix_tool = PrefixCompletionTool()
        self.rag_tool = RAGPipelineTool()
        self.reasoning_engine = ReasoningEngine()
        self.memory_tool = MemoryTool()
        self.vector_tool = VectorDatabaseTool()
        self.system_tool = SystemAccessTool()
        self.coder_tool = DeepSeekCoderTool()
        
        # Session management
        self.session_id = None
        self.user_preferences = {}
        self.active_persona = "Deanna"
        
        # API key management
        self.env_file = Path(".env")
        
        # Prefix commands mapping
        self.prefix_commands = {
            "/chat": "chat",
            "/fim": "fim",
            "/prefix": "prefix",
            "/rag": "rag",
            "/reason": "reason",
            "/remember": "remember",
            "/recall": "recall",
            "/status": "status",
            "/help": "help",
            "/exit": "exit",
            "/clear": "clear",
            "/history": "history",
            "/embed": "embed",
            "/persona": "persona",
            "/personas": "personas",
            "/ls": "list_directory",
            "/cat": "read_file",
            "/write": "write_file",
            "/mkdir": "create_directory",
            "/rm": "delete_file",
            "/ps": "get_processes",
            "/stats": "get_system_stats",
            "/exec": "execute_command",
            "/info": "get_file_info",
            # DeepSeek Coder commands
            "/code": "generate_code",
            "/debug": "debug_code",
            "/heal": "self_heal_code",
            "/fimcode": "fim_code_completion",
            "/search": "web_search",
            "/scrape": "web_scrape",
            "/analyze": "analyze_code",
            "/logic": "analyze_logic",
            "/idea": "store_idea",
            "/store": "store_code",
            "/learn": "learn_from_code",
            "/run": "run_code",
            "/setup": "setup_api_keys"
        }
        
    async def initialize_system(self):
        """Initialize the complete BASED CODER system"""
        # Check for API keys first
        if not self._check_api_keys():
            print(f"{Fore.YELLOW}⚠️ API keys not found or invalid.{Style.RESET_ALL}")
            print(f"{Fore.CYAN}🔧 Running API keys setup...{Style.RESET_ALL}")
            self._run_api_setup()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            
            task = progress.add_task("Initializing BASED CODER...", total=10)
            
            # Initialize tool manager
            progress.update(task, description="Setting up tool manager...")
            await self.tool_manager.initialize()
            progress.advance(task)
            
            # Initialize agent system
            progress.update(task, description="Loading unified agent system...")
            self.agent_system = UnifiedAgentSystem()
            await self.agent_system._initialize_system()
            progress.advance(task)
            
            # Initialize embedding system
            progress.update(task, description="Loading embedding models...")
            await self.embedding_tool.initialize()
            progress.advance(task)
            
            # Initialize database
            progress.update(task, description="Setting up database...")
            await self.sql_tool.initialize()
            progress.advance(task)
            
            # Initialize RAG pipeline
            progress.update(task, description="Setting up RAG pipeline...")
            await self.rag_tool.initialize()
            progress.advance(task)
            
            # Initialize reasoning engine
            progress.update(task, description="Loading reasoning engine...")
            await self.reasoning_engine.initialize()
            progress.advance(task)
            
            # Initialize memory system
            progress.update(task, description="Setting up memory system...")
            await self.memory_tool.initialize()
            progress.advance(task)
            
            # Initialize system access tool
            progress.update(task, description="Setting up system access...")
            # System tool is already initialized
            progress.advance(task)
            
            # Initialize DeepSeek Coder tool
            progress.update(task, description="Setting up DeepSeek Coder...")
            await self.coder_tool.initialize()
            progress.advance(task)
            
            # Create session
            progress.update(task, description="Creating session...")
            self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            progress.advance(task)
    
    def print_banner(self):
        """Print the rainbow BASED CODER banner"""
        banner_text = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  ██████╗  █████╗ ███████╗███████╗██████╗      ██████╗ ██████╗ ██████╗ ███████╗██████╗  ║
║  ██╔══██╗██╔══██╗██╔════╝██╔════╝██╔══██╗    ██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔══██╗ ║
║  ██████╔╝███████║███████╗███████╗██║  ██║    ██║     ██║   ██║██║  ██║█████╗  ██████╔╝ ║
║  ██╔══██╗██╔══██║╚════██║╚════██║██║  ██║    ██║     ██║   ██║██║  ██║██╔══╝  ██╔══██╗ ║
║  ██████╔╝██║  ██║███████║███████║██████╔╝    ╚██████╗╚██████╔╝██████╔╝███████╗██║  ██║ ║
║  ╚═════╝ ╚═╝  ╚═╝╚══════╝╚══════╝╚═════╝      ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝ ║
║                                                                              ║
║                    🚀 Enhanced AI-Powered Command Line Interface              ║
║                                                                              ║
║                    Made by @Lucariolucario55 on Telegram                     ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """
        
        # Print rainbow banner
        lines = banner_text.strip().split('\n')
        for i, line in enumerate(lines):
            color = self.rainbow_colors[i % len(self.rainbow_colors)]
            print(f"{color}{line}{Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}🎯 Session ID: {self.session_id}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}🌟 Active Persona: {self.active_persona}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}🔧 Tools Loaded: {len(self.tool_manager.tools) + 2}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}💻 System Access: Full PC Control Enabled{Style.RESET_ALL}")
        print(f"{Fore.BLUE}🚀 DeepSeek Coder: Advanced Code Generation & Analysis{Style.RESET_ALL}")
        print()
    
    def print_help(self):
        """Print colorful help menu"""
        help_text = f"""
{Fore.CYAN}🎯 BASED CODER CLI Commands:{Style.RESET_ALL}

{Fore.GREEN}💬 Chat Commands:{Style.RESET_ALL}
  chat <message>           - Start a conversation
  continue                 - Continue the last conversation
  history                  - Show conversation history
  clear                    - Clear conversation history

{Fore.YELLOW}🧠 Memory & Learning:{Style.RESET_ALL}
  remember <info>          - Store information in memory
  recall <query>           - Search memories
  learn <topic>            - Learn about a topic
  forget <memory_id>       - Remove a memory

{Fore.MAGENTA}🔧 Tool Operations:{Style.RESET_ALL}
  embed <text>             - Generate embeddings
  fim <prefix> <suffix>    - FIM completion
  prefix <text>            - Prefix completion
  rag <query>              - RAG pipeline query
  reason <question>        - Use reasoning engine

{Fore.BLUE}👤 Persona Management:{Style.RESET_ALL}
  persona <name>           - Switch persona
  personas                 - List available personas
  create-persona <name>    - Create new persona

{Fore.RED}⚙️ System Commands:{Style.RESET_ALL}
  status                   - Show system status
  tools                    - List available tools
  config                   - Show configuration
  help                     - Show this help
  exit                     - Exit the CLI

{Fore.WHITE}🎨 Special Features:{Style.RESET_ALL}
  rainbow                  - Enable rainbow mode
  color <on/off>           - Toggle colors
  verbose <on/off>         - Toggle verbose mode

{Fore.CYAN}💻 System Access Commands:{Style.RESET_ALL}
  /ls <path>               - List directory contents
  /cat <file>              - Read file contents
  /write <file> <content>  - Write to file
  /mkdir <path>            - Create directory
  /rm <path>               - Delete file/directory
  /ps                      - Show running processes
  /stats                   - Show system statistics
  /exec <command>          - Execute system command
  /info <path>             - Get file information

{Fore.BLUE}🚀 DeepSeek Coder Commands:{Style.RESET_ALL}
  /code <prompt>           - Generate code
  /debug <code>            - Debug and fix code
  /heal <code>             - Self-heal code
  /fimcode <prefix> <suffix> - FIM code completion
  /search <query>          - Web search
  /scrape <url>            - Web scraping
  /analyze <code>          - Code analysis
  /logic <code>            - Logic analysis
  /idea <idea>             - Store programming idea
  /store <code>            - Store code example
  /learn <code>            - Learn from code
  /run <code>              - Execute code
  /setup                   - Setup API keys

{Fore.YELLOW}🚀 Prefix Commands (Quick Access):{Style.RESET_ALL}
  /chat <message>          - Quick chat
  /fim <prefix> <suffix>   - Quick FIM
  /prefix <text>           - Quick prefix
  /rag <query>             - Quick RAG
  /reason <question>       - Quick reasoning
  /remember <info>         - Quick memory store
  /recall <query>          - Quick memory search
  /status                  - Quick status
  /help                    - Quick help
  /exit                    - Quick exit
  /clear                   - Quick clear
  /history                 - Quick history
  /embed <text>            - Quick embedding
  /persona <name>          - Quick persona switch
  /personas                - Quick personas list
"""
        print(help_text)
    
    def _check_api_keys(self) -> bool:
        """Check if API keys are properly configured"""
        try:
            # Check if .env file exists
            if not self.env_file.exists():
                return False
            
            # Load environment variables
            from dotenv import load_dotenv
            load_dotenv()
            
            # Check DeepSeek API key
            deepseek_key = os.getenv("DEEPSEEK_API_KEY")
            if not deepseek_key or not deepseek_key.startswith("sk-"):
                return False
            
            # Check HuggingFace token
            huggingface_token = os.getenv("HUGGINGFACE_API_KEY")
            if not huggingface_token or not huggingface_token.startswith("hf_"):
                return False
            
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error checking API keys: {str(e)}{Style.RESET_ALL}")
            return False
    
    def _run_api_setup(self):
        """Run the API keys setup script"""
        try:
            import subprocess
            import sys
            
            setup_script = Path("setup_api_keys.py")
            if setup_script.exists():
                print(f"{Fore.CYAN}🔧 Running API keys setup script...{Style.RESET_ALL}")
                result = subprocess.run([sys.executable, str(setup_script)], 
                                      capture_output=False, text=True)
                
                if result.returncode == 0:
                    print(f"{Fore.GREEN}✅ API keys setup completed successfully!{Style.RESET_ALL}")
                    # Reload environment variables
                    from dotenv import load_dotenv
                    load_dotenv()
                else:
                    print(f"{Fore.RED}❌ API keys setup failed. Please run 'python setup_api_keys.py' manually.{Style.RESET_ALL}")
                    sys.exit(1)
            else:
                print(f"{Fore.RED}❌ API keys setup script not found. Please run 'python setup_api_keys.py' manually.{Style.RESET_ALL}")
                sys.exit(1)
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error running API setup: {str(e)}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}💡 Please run 'python setup_api_keys.py' manually to configure your API keys.{Style.RESET_ALL}")
            sys.exit(1)
    
    def parse_prefix_command(self, user_input: str) -> tuple:
        """Parse prefix commands and return (command, args)"""
        parts = user_input.strip().split()
        if not parts:
            return None, []
        
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # Check if it's a prefix command
        if command in self.prefix_commands:
            return self.prefix_commands[command], args
        
        return None, []
    
    async def handle_system_command(self, command: str, args: List[str]) -> str:
        """Handle system access commands"""
        try:
            if command == "list_directory":
                path = args[0] if args else "."
                result = await self.system_tool.list_directory(path)
                if result["success"]:
                    items = result["items"]
                    output = f"📁 Directory listing for '{path}':\n"
                    for item in items[:20]:  # Limit to 20 items
                        icon = "📄" if item["type"] == "file" else "📁"
                        size = f"({item['size']} bytes)" if item["size"] else ""
                        output += f"  {icon} {item['name']} {size}\n"
                    if len(items) > 20:
                        output += f"  ... and {len(items) - 20} more items\n"
                    return output
                else:
                    return f"❌ Error: {result.get('error', 'Unknown error')}"
            
            elif command == "read_file":
                if not args:
                    return "❌ Usage: /cat <file_path>"
                file_path = args[0]
                result = await self.system_tool.read_file(file_path)
                if result["success"]:
                    content = result["content"]
                    if len(content) > 1000:
                        content = content[:1000] + "\n... (truncated)"
                    return f"📄 File contents of '{file_path}':\n{content}"
                else:
                    return f"❌ Error: {result.get('error', 'Unknown error')}"
            
            elif command == "write_file":
                if len(args) < 2:
                    return "❌ Usage: /write <file_path> <content>"
                file_path = args[0]
                content = " ".join(args[1:])
                result = await self.system_tool.write_file(file_path, content)
                if result["success"]:
                    return f"✅ Successfully wrote to '{file_path}'"
                else:
                    return f"❌ Error: {result.get('error', 'Unknown error')}"
            
            elif command == "create_directory":
                if not args:
                    return "❌ Usage: /mkdir <directory_path>"
                dir_path = args[0]
                result = await self.system_tool.create_directory(dir_path)
                if result["success"]:
                    return f"✅ Successfully created directory '{dir_path}'"
                else:
                    return f"❌ Error: {result.get('error', 'Unknown error')}"
            
            elif command == "delete_file":
                if not args:
                    return "❌ Usage: /rm <path>"
                path = args[0]
                result = await self.system_tool.delete_file(path)
                if result["success"]:
                    return f"✅ Successfully deleted '{path}'"
                else:
                    return f"❌ Error: {result.get('error', 'Unknown error')}"
            
            elif command == "get_processes":
                result = await self.system_tool.get_process_info()
                if result["success"]:
                    processes = result["processes"][:10]  # Show top 10
                    output = "🖥️ Running processes (top 10):\n"
                    for proc in processes:
                        output += f"  PID {proc['pid']}: {proc['name']} (CPU: {proc['cpu_percent']:.1f}%, MEM: {proc['memory_percent']:.1f}%)\n"
                    return output
                else:
                    return f"❌ Error: {result.get('error', 'Unknown error')}"
            
            elif command == "get_system_stats":
                result = await self.system_tool.get_system_stats()
                if result["success"]:
                    stats = result
                    output = "📊 System Statistics:\n"
                    output += f"  CPU Usage: {stats['cpu_percent']:.1f}%\n"
                    output += f"  Memory Usage: {stats['memory_percent']:.1f}%\n"
                    output += f"  Disk Usage: {stats['disk_percent']:.1f}%\n"
                    output += f"  Platform: {stats['system_info']['platform']}\n"
                    output += f"  Python: {stats['system_info']['python_version']}\n"
                    return output
                else:
                    return f"❌ Error: {result.get('error', 'Unknown error')}"
            
            elif command == "execute_command":
                if not args:
                    return "❌ Usage: /exec <command>"
                cmd = " ".join(args)
                result = await self.system_tool.execute_command(cmd)
                if result["success"]:
                    output = f"✅ Command executed successfully:\n{result['stdout']}"
                    if result["stderr"]:
                        output += f"\n⚠️ Warnings:\n{result['stderr']}"
                    return output
                else:
                    return f"❌ Command failed:\n{result['stderr']}"
            
            elif command == "get_file_info":
                if not args:
                    return "❌ Usage: /info <file_path>"
                file_path = args[0]
                result = await self.system_tool.get_file_info(file_path)
                if result["exists"]:
                    output = f"📄 File information for '{file_path}':\n"
                    output += f"  Size: {result['size']} bytes\n"
                    output += f"  Type: {'File' if result['is_file'] else 'Directory'}\n"
                    output += f"  Modified: {result['modified']}\n"
                    output += f"  Permissions: {result['permissions']}\n"
                    return output
                else:
                    return f"❌ File not found: {file_path}"
            
            else:
                return f"❌ Unknown system command: {command}"
                
        except Exception as e:
            return f"❌ Error executing system command: {str(e)}"
    
    async def handle_coder_command(self, command: str, args: List[str]) -> str:
        """Handle DeepSeek Coder commands"""
        try:
            if command == "generate_code":
                if not args:
                    return "❌ Usage: /code <prompt>"
                prompt = " ".join(args)
                result = await self.coder_tool.execute(
                    operation="code_generation",
                    prompt=prompt,
                    language="python"
                )
                if result.success:
                    return f"✅ Code generated:\n{result.data.get('code', '')}"
                else:
                    return f"❌ Code generation failed: {result.message}"
            
            elif command == "debug_code":
                if not args:
                    return "❌ Usage: /debug <code>"
                code = " ".join(args)
                result = await self.coder_tool.execute(
                    operation="code_debugging",
                    code=code,
                    language="python"
                )
                if result.success:
                    return f"✅ Code debugged:\n{result.data.get('fixed_code', '')}"
                else:
                    return f"❌ Code debugging failed: {result.message}"
            
            elif command == "self_heal_code":
                if not args:
                    return "❌ Usage: /heal <code>"
                code = " ".join(args)
                result = await self.coder_tool.execute(
                    operation="self_healing",
                    code=code,
                    language="python"
                )
                if result.success:
                    return f"✅ Code self-healed:\n{result.data.get('healed_code', '')}"
                else:
                    return f"❌ Self-healing failed: {result.message}"
            
            elif command == "fim_code_completion":
                if len(args) < 2:
                    return "❌ Usage: /fimcode <prefix> <suffix>"
                prefix = args[0]
                suffix = args[1]
                result = await self.coder_tool.execute(
                    operation="fim_completion",
                    prefix=prefix,
                    suffix=suffix,
                    language="python"
                )
                if result.success:
                    return f"✅ FIM completion:\n{result.data.get('completion', '')}"
                else:
                    return f"❌ FIM completion failed: {result.message}"
            
            elif command == "web_search":
                if not args:
                    return "❌ Usage: /search <query>"
                query = " ".join(args)
                result = await self.coder_tool.execute(
                    operation="web_search",
                    query=query,
                    engine="duckduckgo"
                )
                if result.success:
                    results = result.data.get('results', [])
                    output = f"🔍 Search results for '{query}':\n"
                    for i, res in enumerate(results[:5], 1):
                        output += f"  {i}. {res.title}\n     {res.url}\n     {res.snippet[:100]}...\n\n"
                    return output
                else:
                    return f"❌ Web search failed: {result.message}"
            
            elif command == "web_scrape":
                if not args:
                    return "❌ Usage: /scrape <url>"
                url = args[0]
                result = await self.coder_tool.execute(
                    operation="web_scraping",
                    url=url
                )
                if result.success:
                    data = result.data.get('scraped_data', {})
                    output = f"📄 Scraped data from '{url}':\n"
                    if 'text' in data:
                        output += f"Text: {data['text'][:200]}...\n"
                    if 'links' in data:
                        output += f"Links found: {len(data['links'])}\n"
                    return output
                else:
                    return f"❌ Web scraping failed: {result.message}"
            
            elif command == "analyze_code":
                if not args:
                    return "❌ Usage: /analyze <code>"
                code = " ".join(args)
                result = await self.coder_tool.execute(
                    operation="code_analysis",
                    code=code,
                    language="python"
                )
                if result.success:
                    analysis = result.data.get('analysis', {})
                    output = f"🔍 Code analysis:\n"
                    output += f"Language: {analysis.language}\n"
                    output += f"Complexity: {analysis.complexity}\n"
                    if analysis.issues:
                        output += f"Issues: {', '.join(analysis.issues)}\n"
                    if analysis.suggestions:
                        output += f"Suggestions: {', '.join(analysis.suggestions)}\n"
                    return output
                else:
                    return f"❌ Code analysis failed: {result.message}"
            
            elif command == "analyze_logic":
                if not args:
                    return "❌ Usage: /logic <code>"
                code = " ".join(args)
                result = await self.coder_tool.execute(
                    operation="logic_analysis",
                    code=code,
                    language="python"
                )
                if result.success:
                    return f"🧠 Logic analysis:\n{result.data.get('analysis', '')}"
                else:
                    return f"❌ Logic analysis failed: {result.message}"
            
            elif command == "store_idea":
                if not args:
                    return "❌ Usage: /idea <idea>"
                idea = " ".join(args)
                result = await self.coder_tool.execute(
                    operation="store_idea",
                    idea=idea,
                    category="programming"
                )
                if result.success:
                    return f"💡 Idea stored: {result.data.get('idea_id', '')}"
                else:
                    return f"❌ Failed to store idea: {result.message}"
            
            elif command == "store_code":
                if not args:
                    return "❌ Usage: /store <code>"
                code = " ".join(args)
                result = await self.coder_tool.execute(
                    operation="store_code",
                    code=code,
                    language="python",
                    description="Stored via CLI"
                )
                if result.success:
                    return f"💾 Code stored: {result.data.get('example_id', '')}"
                else:
                    return f"❌ Failed to store code: {result.message}"
            
            elif command == "learn_from_code":
                if not args:
                    return "❌ Usage: /learn <code>"
                code = " ".join(args)
                result = await self.coder_tool.execute(
                    operation="learn_from_code",
                    code=code,
                    language="python"
                )
                if result.success:
                    return f"🎓 Learning insights:\n{result.data.get('insights', '')}"
                else:
                    return f"❌ Learning failed: {result.message}"
            
            elif command == "run_code":
                if not args:
                    return "❌ Usage: /run <code>"
                code = " ".join(args)
                result = await self.coder_tool.execute(
                    operation="run_code",
                    code=code,
                    language="python"
                )
                if result.success:
                    output = f"▶️ Code execution result:\n"
                    output += f"STDOUT: {result.data.get('stdout', '')}\n"
                    if result.data.get('stderr'):
                        output += f"STDERR: {result.data.get('stderr', '')}\n"
                    return output
                else:
                    return f"❌ Code execution failed: {result.message}"
            
            else:
                return f"❌ Unknown coder command: {command}"
                
        except Exception as e:
            return f"❌ Error executing coder command: {str(e)}"
    
    async def handle_chat(self, message: str):
        """Handle chat conversation with context caching"""
        try:
            # Get context from cache and history
            context = await self._build_context(message)
            
            # Use reasoning engine to determine approach
            reasoning_result = await self.reasoning_engine.execute(
                query=message,
                context=context,
                operation="analyze"
            )
            
            # Generate response using unified agent system
            response = await self.agent_system.execute(
                operation="conversation",
                user_message=message,
                context=context,
                reasoning_chain=reasoning_result.data.get("reasoning_chain", [])
            )
            
            # Cache the context for next interaction
            self.context_cache[self.session_id] = {
                "last_message": message,
                "last_response": response.data.get("response", ""),
                "timestamp": datetime.now().isoformat(),
                "context": context
            }
            
            # Add to conversation history
            self.conversation_history.append({
                "user": message,
                "assistant": response.data.get("response", ""),
                "timestamp": datetime.now().isoformat(),
                "session_id": self.session_id
            })
            
            return response.data.get("response", "I'm sorry, I couldn't generate a response.")
            
        except Exception as e:
            return f"Error in chat: {str(e)}"
    
    async def _build_context(self, message: str) -> Dict[str, Any]:
        """Build comprehensive context for the conversation"""
        context = {
            "session_id": self.session_id,
            "active_persona": self.active_persona,
            "conversation_history": self.conversation_history[-10:],  # Last 10 messages
            "cached_context": self.context_cache.get(self.session_id, {}),
            "user_preferences": self.user_preferences,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add relevant memories
        try:
            memories = await self.memory_tool.execute(
                operation="search",
                query=message,
                limit=5
            )
            context["relevant_memories"] = memories.data.get("memories", [])
        except:
            context["relevant_memories"] = []
        
        # Add RAG results
        try:
            rag_results = await self.rag_tool.execute(
                operation="search",
                query=message,
                limit=3
            )
            context["rag_context"] = rag_results.data.get("results", [])
        except:
            context["rag_context"] = []
        
        return context
    
    async def handle_fim_completion(self, prefix: str, suffix: str):
        """Handle FIM (Fill-in-Middle) completion"""
        try:
            result = await self.fim_tool.execute(
                prefix=prefix,
                suffix=suffix
            )
            return result.data.get("completion", "")
        except Exception as e:
            return f"Error in FIM completion: {str(e)}"
    
    async def handle_prefix_completion(self, prefix: str):
        """Handle prefix completion"""
        try:
            result = await self.prefix_tool.execute(
                prefix=prefix
            )
            return result.data.get("completion", "")
        except Exception as e:
            return f"Error in prefix completion: {str(e)}"
    
    async def handle_rag_query(self, query: str):
        """Handle RAG pipeline query"""
        try:
            result = await self.rag_tool.execute(
                operation="query",
                query=query,
                include_context=True
            )
            return result.data.get("response", "")
        except Exception as e:
            return f"Error in RAG query: {str(e)}"
    
    async def handle_reasoning(self, question: str):
        """Handle reasoning engine query"""
        try:
            result = await self.reasoning_engine.execute(
                query=question,
                operation="reason"
            )
            return result.data.get("reasoning", "")
        except Exception as e:
            return f"Error in reasoning: {str(e)}"
    
    async def handle_memory_operation(self, operation: str, **kwargs):
        """Handle memory operations"""
        try:
            result = await self.memory_tool.execute(
                operation=operation,
                **kwargs
            )
            return result.data
        except Exception as e:
            return f"Error in memory operation: {str(e)}"
    
    def print_status(self):
        """Print colorful system status"""
        status_table = Table(title="🚀 BASED CODER System Status")
        status_table.add_column("Component", style="cyan")
        status_table.add_column("Status", style="green")
        status_table.add_column("Details", style="yellow")
        
        # Add status rows
        status_table.add_row("Agent System", "✅ Active", f"Session: {self.session_id}")
        status_table.add_row("Embedding Tool", "✅ Loaded", "Qwen3 Model Ready")
        status_table.add_row("Database", "✅ Connected", "SQLite Active")
        status_table.add_row("RAG Pipeline", "✅ Ready", "Vector Search Active")
        status_table.add_row("Reasoning Engine", "✅ Active", "Chain-of-Thought Ready")
        status_table.add_row("Memory System", "✅ Active", f"{len(self.conversation_history)} conversations")
        status_table.add_row("Context Cache", "✅ Active", f"{len(self.context_cache)} cached contexts")
        status_table.add_row("System Access", "✅ Active", "Full PC Control Enabled")
        status_table.add_row("Prefix Commands", "✅ Active", f"{len(self.prefix_commands)} commands available")
        status_table.add_row("DeepSeek Coder", "✅ Active", "Advanced Code Generation & Analysis")
        
        self.console.print(status_table)
    
    async def interactive_mode(self):
        """Run interactive CLI mode"""
        self.print_banner()
        
        while True:
            try:
                # Get user input with colorful prompt
                user_input = Prompt.ask(
                    f"{Fore.GREEN}🎯 BASED CODER{Style.RESET_ALL}",
                    default="help"
                )
                
                if user_input.lower() in ['exit', 'quit', 'q']:
                    print(f"{Fore.YELLOW}👋 Goodbye! Thanks for using BASED CODER!{Style.RESET_ALL}")
                    break
                
                # Check for prefix commands first
                prefix_command, prefix_args = self.parse_prefix_command(user_input)
                if prefix_command:
                    if prefix_command in ["list_directory", "read_file", "write_file", "create_directory", 
                                       "delete_file", "get_processes", "get_system_stats", "execute_command", 
                                       "get_file_info"]:
                        # Handle system commands
                        response = await self.handle_system_command(prefix_command, prefix_args)
                        print(f"{Fore.CYAN}💻 {response}{Style.RESET_ALL}")
                        continue
                    elif prefix_command in ["generate_code", "debug_code", "self_heal_code", "fim_code_completion",
                                       "web_search", "web_scrape", "analyze_code", "analyze_logic",
                                       "store_idea", "store_code", "learn_from_code", "run_code"]:
                        # Handle DeepSeek Coder commands
                        response = await self.handle_coder_command(prefix_command, prefix_args)
                        print(f"{Fore.BLUE}🚀 {response}{Style.RESET_ALL}")
                        continue
                    elif prefix_command == "setup_api_keys":
                        # Handle API setup command
                        print(f"{Fore.CYAN}🔧 Running API keys setup...{Style.RESET_ALL}")
                        self._run_api_setup()
                        continue
                    else:
                        # Handle regular prefix commands
                        command = prefix_command
                        args = prefix_args
                else:
                    # Parse regular command
                    parts = user_input.split()
                    command = parts[0].lower()
                    args = parts[1:] if len(parts) > 1 else []
                
                if command == "help":
                    self.print_help()
                
                elif command == "chat":
                    if not args:
                        message = Prompt.ask("💬 Enter your message")
                    else:
                        message = " ".join(args)
                    
                    print(f"{Fore.CYAN}🤖 Processing...{Style.RESET_ALL}")
                    response = await self.handle_chat(message)
                    print(f"{Fore.GREEN}💬 Response: {response}{Style.RESET_ALL}")
                
                elif command == "fim":
                    if len(args) < 2:
                        print(f"{Fore.RED}❌ Usage: fim <prefix> <suffix>{Style.RESET_ALL}")
                        continue
                    
                    prefix = args[0]
                    suffix = args[1]
                    result = await self.handle_fim_completion(prefix, suffix)
                    print(f"{Fore.MAGENTA}🔧 FIM Result: {result}{Style.RESET_ALL}")
                
                elif command == "prefix":
                    if not args:
                        print(f"{Fore.RED}❌ Usage: prefix <text>{Style.RESET_ALL}")
                        continue
                    
                    prefix_text = " ".join(args)
                    result = await self.handle_prefix_completion(prefix_text)
                    print(f"{Fore.MAGENTA}🔧 Prefix Result: {result}{Style.RESET_ALL}")
                
                elif command == "rag":
                    if not args:
                        print(f"{Fore.RED}❌ Usage: rag <query>{Style.RESET_ALL}")
                        continue
                    
                    query = " ".join(args)
                    result = await self.handle_rag_query(query)
                    print(f"{Fore.BLUE}🔍 RAG Result: {result}{Style.RESET_ALL}")
                
                elif command == "reason":
                    if not args:
                        print(f"{Fore.RED}❌ Usage: reason <question>{Style.RESET_ALL}")
                        continue
                    
                    question = " ".join(args)
                    result = await self.handle_reasoning(question)
                    print(f"{Fore.YELLOW}🧠 Reasoning: {result}{Style.RESET_ALL}")
                
                elif command == "remember":
                    if not args:
                        print(f"{Fore.RED}❌ Usage: remember <information>{Style.RESET_ALL}")
                        continue
                    
                    info = " ".join(args)
                    result = await self.handle_memory_operation("store", content=info)
                    print(f"{Fore.GREEN}💾 Memory stored: {result}{Style.RESET_ALL}")
                
                elif command == "recall":
                    if not args:
                        print(f"{Fore.RED}❌ Usage: recall <query>{Style.RESET_ALL}")
                        continue
                    
                    query = " ".join(args)
                    result = await self.handle_memory_operation("search", query=query)
                    print(f"{Fore.CYAN}🔍 Memory search: {result}{Style.RESET_ALL}")
                
                elif command == "status":
                    self.print_status()
                
                elif command == "history":
                    if self.conversation_history:
                        print(f"{Fore.CYAN}📜 Conversation History:{Style.RESET_ALL}")
                        for i, conv in enumerate(self.conversation_history[-5:], 1):
                            print(f"{Fore.YELLOW}{i}. User: {conv['user'][:50]}...{Style.RESET_ALL}")
                            print(f"{Fore.GREEN}   Assistant: {conv['assistant'][:50]}...{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.YELLOW}📜 No conversation history yet.{Style.RESET_ALL}")
                
                elif command == "clear":
                    self.conversation_history = []
                    self.context_cache = {}
                    print(f"{Fore.GREEN}🧹 Conversation history and cache cleared.{Style.RESET_ALL}")
                
                else:
                    print(f"{Fore.RED}❌ Unknown command: {command}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}💡 Type 'help' for available commands.{Style.RESET_ALL}")
                
                print()  # Add spacing between commands
                
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}👋 Goodbye! Thanks for using BASED CODER!{Style.RESET_ALL}")
                break
            except Exception as e:
                print(f"{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}")

async def main():
    """Main entry point for BASED CODER CLI"""
    parser = argparse.ArgumentParser(description="🚀 BASED CODER CLI - Enhanced AI-Powered Command Line Interface")
    parser.add_argument("--init", action="store_true", help="Initialize the system")
    parser.add_argument("--chat", type=str, help="Send a single chat message")
    parser.add_argument("--fim", nargs=2, metavar=("PREFIX", "SUFFIX"), help="FIM completion")
    parser.add_argument("--prefix", type=str, help="Prefix completion")
    parser.add_argument("--rag", type=str, help="RAG query")
    parser.add_argument("--reason", type=str, help="Reasoning query")
    parser.add_argument("--status", action="store_true", help="Show system status")
    parser.add_argument("--exec", type=str, help="Execute system command")
    parser.add_argument("--ls", type=str, help="List directory contents")
    parser.add_argument("--cat", type=str, help="Read file contents")
    
    args = parser.parse_args()
    
    # Create CLI instance
    cli = RainbowCLI()
    
    # Initialize system
    await cli.initialize_system()
    
    if args.status:
        cli.print_status()
        return
    
    if args.chat:
        response = await cli.handle_chat(args.chat)
        print(f"Response: {response}")
        return
    
    if args.fim:
        result = await cli.handle_fim_completion(args.fim[0], args.fim[1])
        print(f"FIM Result: {result}")
        return
    
    if args.prefix:
        result = await cli.handle_prefix_completion(args.prefix)
        print(f"Prefix Result: {result}")
        return
    
    if args.rag:
        result = await cli.handle_rag_query(args.rag)
        print(f"RAG Result: {result}")
        return
    
    if args.reason:
        result = await cli.handle_reasoning(args.reason)
        print(f"Reasoning: {result}")
        return
    
    if args.exec:
        result = await cli.handle_system_command("execute_command", [args.exec])
        print(result)
        return
    
    if args.ls:
        result = await cli.handle_system_command("list_directory", [args.ls])
        print(result)
        return
    
    if args.cat:
        result = await cli.handle_system_command("read_file", [args.cat])
        print(result)
        return
    
    # Interactive mode
    await cli.interactive_mode()

if __name__ == "__main__":
    asyncio.run(main()) 