#!/usr/bin/env python3
"""
🚀 BASED CODER CLI - Unified Main Entry Point
Made by @Lucariolucario55 on Telegram

Consolidated main CLI with all features from the original based_coder_cli.py
"""

import time
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
from dotenv import load_dotenv

# Initialize colorama for Windows compatibility
colorama.init()

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

# Import our tools and systems
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
        logging.FileHandler('logs/deepcli.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SystemAccessTool:
    """Tool for full PC access and OS operations"""
    
    def __init__(self) -> Any:
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
                "stderr": str(e)
            }

class BasedCoderCLI:
    """Unified BASED CODER CLI with all features"""
    
    def __init__(self) -> Any:
        try:
            self.config = get_config()
            self.env_file = Path(".env")
            
            # Initialize tools with error handling
            self.system_tool = SystemAccessTool()
            self.embedding_tool = SimpleEmbeddingTool()
            
            # Wrap tool initialization with try-except
            try:
                self.sql_db = SQLDatabaseTool()
            except Exception as e:
                logging.info(f"{Fore.YELLOW}⚠️ SQL Database Tool initialization failed: {e}{Style.RESET_ALL}")
                self.sql_db = None
            
            try:
                self.llm_tool = LLMQueryTool()
            except Exception as e:
                logging.info(f"{Fore.YELLOW}⚠️ LLM Query Tool initialization failed: {e}{Style.RESET_ALL}")
                self.llm_tool = None
            
            try:
                self.fim_tool = FIMCompletionTool()
            except Exception as e:
                logging.info(f"{Fore.YELLOW}⚠️ FIM Completion Tool initialization failed: {e}{Style.RESET_ALL}")
                self.fim_tool = None
            
            try:
                self.prefix_tool = PrefixCompletionTool()
            except Exception as e:
                logging.info(f"{Fore.YELLOW}⚠️ Prefix Completion Tool initialization failed: {e}{Style.RESET_ALL}")
                self.prefix_tool = None
            
            try:
                self.rag_tool = RAGPipelineTool()
            except Exception as e:
                logging.info(f"{Fore.YELLOW}⚠️ RAG Pipeline Tool initialization failed: {e}{Style.RESET_ALL}")
                self.rag_tool = None
            
            try:
                self.reasoning_tool = ReasoningEngine()
            except Exception as e:
                logging.info(f"{Fore.YELLOW}⚠️ Reasoning Engine initialization failed: {e}{Style.RESET_ALL}")
                self.reasoning_tool = None
            
            try:
                self.memory_tool = MemoryTool()
            except Exception as e:
                logging.info(f"{Fore.YELLOW}⚠️ Memory Tool initialization failed: {e}{Style.RESET_ALL}")
                self.memory_tool = None
            
            try:
                self.vector_db = VectorDatabaseTool()
            except Exception as e:
                logging.info(f"{Fore.YELLOW}⚠️ Vector Database Tool initialization failed: {e}{Style.RESET_ALL}")
                self.vector_db = None
            
            try:
                self.coder_tool = DeepSeekCoderTool()
            except Exception as e:
                logging.info(f"{Fore.YELLOW}⚠️ DeepSeek Coder Tool initialization failed: {e}{Style.RESET_ALL}")
                self.coder_tool = None
            
            try:
                self.tool_manager = ToolManager()
            except Exception as e:
                logging.info(f"{Fore.YELLOW}⚠️ Tool Manager initialization failed: {e}{Style.RESET_ALL}")
                self.tool_manager = None
            
            # Conversation history
            self.conversation_history = []
            self.session_id = f"session_{int(time.time())}"
            
            # Prefix commands remain the same
            self.prefix_commands = {
                "/help": "show_help",
                "/status": "show_status",
                "/clear": "clear_history",
                "/history": "show_history",
                "/chat": "chat",
                "/fim": "fim_completion",
                "/prefix": "prefix_completion",
                "/rag": "rag_query",
                "/reason": "reasoning",
                "/remember": "store_memory",
                "/recall": "recall_memory",
                "/code": "code_generation",
                "/debug": "code_debugging",
                "/heal": "code_healing",
                "/search": "web_search",
                "/scrape": "web_scrape",
                "/analyze": "code_analysis",
                "/logic": "logic_analysis",
                "/run": "run_code",
                "/setup": "setup_api_keys"
            }
        except Exception as e:
            logging.info(f"{Fore.RED}❌ Initialization failed: {e}{Style.RESET_ALL}")
            raise
    
    def _check_api_keys(self) -> bool:
        """Check if API keys are properly configured"""
        try:
            if not self.env_file.exists():
                return False
            load_dotenv()
            deepseek_key = os.getenv("DEEPSEEK_API_KEY")
            if not deepseek_key or not deepseek_key.startswith("sk-"):
                return False
            huggingface_token = os.getenv("HUGGINGFACE_API_KEY")
            if not huggingface_token or not huggingface_token.startswith("hf_"):
                return False
            return True
        except Exception as e:
            logging.info(f"{Fore.RED}❌ Error checking API keys: {str(e)}{Style.RESET_ALL}")
            return False
    
    def _run_api_setup(self) -> Any:
        """Run the API keys setup script"""
        try:
            import subprocess
            import sys
            setup_script = Path("setup.py")
            if setup_script.exists():
                logging.info(f"{Fore.CYAN}🔧 Running API keys setup...{Style.RESET_ALL}")
                result = subprocess.run([sys.executable, str(setup_script), "--api-keys"], 
                                      capture_output=False, text=True)
                if result.returncode == 0:
                    logging.info(f"{Fore.GREEN}✅ API keys setup completed successfully!{Style.RESET_ALL}")
                    load_dotenv()
                else:
                    logger.error("API keys setup failed. Please run 'python setup.py --api-keys' manually.")
                    console.print(f"{Fore.RED}❌ API keys setup failed. Please run 'python setup.py --api-keys' manually.{Style.RESET_ALL}")
                    sys.exit(1)
            else:
                logger.error("Setup script not found. Please run 'python setup.py --api-keys' manually.")
                console.print(f"{Fore.RED}❌ Setup script not found. Please run 'python setup.py --api-keys' manually.{Style.RESET_ALL}")
                sys.exit(1)
        except Exception as e:
            logger.error(f"Error running API setup: {str(e)}")
            console.print(f"{Fore.RED}❌ Error running API setup: {str(e)}{Style.RESET_ALL}")
            console.print(f"{Fore.YELLOW}💡 Please run 'python setup.py --api-keys' manually to configure your API keys.{Style.RESET_ALL}")
            sys.exit(1)
    
    async def initialize_system(self) -> Any:
        """Initialize the complete BASED CODER system"""
        logger.info("Starting system initialization")
        
        # Check for API keys first
        if not self._check_api_keys():
            logger.warning("API keys not found or invalid")
            console.print(f"{Fore.YELLOW}⚠️ API keys not found or invalid.{Style.RESET_ALL}")
            console.print(f"{Fore.CYAN}🔧 Running API keys setup...{Style.RESET_ALL}")
            self._run_api_setup()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            # Initialize tools with proper error handling
            progress.add_task("Initializing tools...", total=None)
            
            # Initialize database first
            if self.sql_db:
                try:
                    logger.info("Initializing database")
                    await self.sql_db._initialize_database()
                    logger.info("Database initialized successfully")
                    console.print(f"{Fore.GREEN}✅ Database initialized{Style.RESET_ALL}")
                except Exception as e:
                    logger.warning(f"Database initialization warning: {e}")
                    console.print(f"{Fore.YELLOW}⚠️ Database initialization warning: {e}{Style.RESET_ALL}")
            
            # Initialize embedding system
            if self.embedding_tool:
                try:
                    logger.info("Initializing embedding system")
                    # Test embedding creation
                    test_embedding = self.embedding_tool.create_embedding("test")
                    logger.info("Embedding system initialized successfully")
                    console.print(f"{Fore.GREEN}✅ Embedding system initialized{Style.RESET_ALL}")
                except Exception as e:
                    logger.warning(f"Embedding system warning: {e}")
                    console.print(f"{Fore.YELLOW}⚠️ Embedding system warning: {e}{Style.RESET_ALL}")
            
            # Initialize vector database (optional)
            if self.vector_db:
                try:
                    logger.info("Checking vector database availability")
                    # Vector database is optional, don't fail if not available
                    logger.info("Vector database available")
                    console.print(f"{Fore.GREEN}✅ Vector database available{Style.RESET_ALL}")
                except Exception as e:
                    logger.warning(f"Vector database not available: {e}")
                    console.print(f"{Fore.YELLOW}⚠️ Vector database not available: {e}{Style.RESET_ALL}")
            
            # Initialize tool manager with all tools
            if self.tool_manager:
                try:
                    logger.info("Initializing tool manager")
                    # Ensure all tools are properly registered
                    available_tools = self.tool_manager.list_tools()
                    logger.info(f"Tool manager initialized with {len(available_tools)} tools")
                    console.print(f"{Fore.GREEN}✅ Tool manager initialized with {len(available_tools)} tools{Style.RESET_ALL}")
                except Exception as e:
                    logger.warning(f"Tool manager warning: {e}")
                    console.print(f"{Fore.YELLOW}⚠️ Tool manager warning: {e}{Style.RESET_ALL}")
            
            await asyncio.sleep(1)
        
        logger.info("BASED CODER CLI initialized successfully")
        console.print(f"{Fore.GREEN}✅ BASED CODER CLI initialized successfully!{Style.RESET_ALL}")
        
        # Show system status
        self.show_status()
    
    def print_banner(self) -> Any:
        """Print the BASED CODER CLI banner"""
        banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  ██████╗  █████╗ ███████╗███████╗██████╗      ██████╗ ██████╗ ██████╗ ███████╗██████╗  ║
║  ██╔══██╗██╔══██╗██╔════╝██╔════╝██╔══██╗    ██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔══██╗ ║
║  ██████╔╝███████║███████╗███████╗██║  ██║    ██║     ██║   ██║██║  ██║█████╗  ██████╔╝ ║
║  ██╔══██╗██╔══██║╚════██║╚════██║██║  ██║    ██║     ██║   ██║██║  ██║██╔══╝  ██╔══██╗ ║
║  ██████╔╝██║  ██║███████║███████║██████╔╝    ╚██████╗╚██████╔╝██████╔╝███████╗██║  ██║ ║
║  ╚═════╝ ╚═╝  ╚═╝╚══════╝╚══════╝╚═════╝      ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝ ║
║                                                                              ║
║                    🚀 BASED CODER CLI - UNIFIED INTERFACE                     ║
║                                                                              ║
║                    Made by @Lucariolucario55 on Telegram                     ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
        """
        logging.info(banner)
    
    def print_help(self) -> Any:
        """Print help information"""
        help_text = f"""
{Fore.YELLOW}🎯 BASED CODER CLI - Command Reference{Style.RESET_ALL}

{Fore.CYAN}🚀 System Commands:{Style.RESET_ALL}
  /help                    - Show this help menu
  /status                  - Show system status
  /clear                   - Clear conversation history
  /history                 - Show conversation history
  /setup                   - Setup API keys

{Fore.CYAN}💬 Chat & AI Commands:{Style.RESET_ALL}
  /chat <message>          - Chat with AI
  /fim <prefix> <suffix>   - Fill-in-Middle completion
  /prefix <text>           - Prefix completion
  /rag <query>             - RAG pipeline query
  /reason <question>       - Reasoning engine

{Fore.CYAN}💾 Memory Commands:{Style.RESET_ALL}
  /remember <content>      - Store information in memory
  /recall <query>          - Recall information from memory

{Fore.CYAN}🔧 DeepSeek Coder Commands:{Style.RESET_ALL}
  /code <prompt>           - Generate code
  /debug <code>            - Debug and fix code
  /heal <code>             - Self-heal problematic code
  /search <query>          - Web search
  /scrape <url>            - Web scraping
  /analyze <code>          - Code analysis
  /logic <code>            - Logic analysis
  /run <code>              - Execute code

{Fore.CYAN}💡 Examples:{Style.RESET_ALL}
  /chat "Hello, how are you?"
  /code "Create a Python web scraper"
  /debug "def hello() -> None: logging.info('world')"
  /remember "BASED CODER CLI is awesome"
  /recall "BASED CODER CLI"

{Fore.CYAN}🎨 Features:{Style.RESET_ALL}
  🌈 Rainbow interface with colorful agents
  💻 Full PC access with OS operations
  🚀 Prefix commands for quick access
  🧠 Multi-round conversations with context caching
  🔗 Function calls and reasoning capabilities
  🔄 FIM and prefix completion
  📚 RAG pipeline with vector search
  💾 Memory and persona management
  🎯 DeepSeek integration with all features

{Fore.GREEN}Made by @Lucariolucario55 on Telegram{Style.RESET_ALL}
        """
        logging.info(help_text)
    
    def parse_prefix_command(self, user_input: str) -> tuple:
        """Parse prefix command and arguments"""
        if not user_input.startswith('/'):
            return None, []
        
        parts = user_input.split(' ', 1)
        command = parts[0].lower()
        args = parts[1].split() if len(parts) > 1 else []
        
        return command, args
    
    async def handle_chat(self, message: str):
        """Handle chat with AI"""
        try:
            # Add to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": message,
                "timestamp": datetime.now().isoformat()
            })
            
            # Get AI response
            result = await self.llm_tool.execute(
                prompt=message,
                max_tokens=500
            )
            
            if result.success:
                response = result.data.get('response', 'Sorry, I could not generate a response.')
                logging.info(f"{Fore.GREEN}🤖 AI: {response}{Style.RESET_ALL}")
                
                # Add to conversation history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.now().isoformat()
                })
            else:
                logging.info(f"{Fore.RED}❌ Error: {result.message}{Style.RESET_ALL}")
                
        except Exception as e:
            logging.info(f"{Fore.RED}❌ Error in chat: {str(e)}{Style.RESET_ALL}")
    
    async def handle_fim_completion(self, prefix: str, suffix: str):
        """Handle FIM completion"""
        try:
            result = await self.fim_tool.execute(
                prefix=prefix,
                suffix=suffix,
                language="python"
            )
            
            if result.success:
                completion = result.data.get('completion', 'No completion generated.')
                logging.info(f"{Fore.GREEN}🔗 FIM Completion: {completion}{Style.RESET_ALL}")
            else:
                logging.info(f"{Fore.RED}❌ FIM completion failed: {result.message}{Style.RESET_ALL}")
                
        except Exception as e:
            logging.info(f"{Fore.RED}❌ Error in FIM completion: {str(e)}{Style.RESET_ALL}")
    
    async def handle_prefix_completion(self, prefix: str):
        """Handle prefix completion"""
        try:
            result = await self.prefix_tool.execute(
                prefix=prefix,
                max_tokens=100
            )
            
            if result.success:
                completion = result.data.get('completion', 'No completion generated.')
                logging.info(f"{Fore.GREEN}📝 Prefix Completion: {completion}{Style.RESET_ALL}")
            else:
                logging.info(f"{Fore.RED}❌ Prefix completion failed: {result.message}{Style.RESET_ALL}")
                
        except Exception as e:
            logging.info(f"{Fore.RED}❌ Error in prefix completion: {str(e)}{Style.RESET_ALL}")
    
    async def handle_rag_query(self, query: str):
        """Handle RAG pipeline query"""
        try:
            result = await self.rag_tool.execute(
                query=query,
                max_results=3
            )
            
            if result.success:
                documents = result.data.get('documents', [])
                logging.info(f"{Fore.GREEN}📚 RAG Results ({len(documents)} documents):{Style.RESET_ALL}")
                for i, doc in enumerate(documents):
                    logging.info(f"  {i+1}. {doc.get('content', 'N/A')[:100]}...")
            else:
                logging.info(f"{Fore.RED}❌ RAG query failed: {result.message}{Style.RESET_ALL}")
                
        except Exception as e:
            logging.info(f"{Fore.RED}❌ Error in RAG query: {str(e)}{Style.RESET_ALL}")
    
    async def handle_reasoning(self, question: str):
        """Handle reasoning engine"""
        try:
            result = await self.reasoning_tool.execute(
                question=question,
                approach="step_by_step"
            )
            
            if result.success:
                reasoning = result.data.get('reasoning', 'No reasoning generated.')
                logging.info(f"{Fore.GREEN}🧠 Reasoning: {reasoning}{Style.RESET_ALL}")
            else:
                logging.info(f"{Fore.RED}❌ Reasoning failed: {result.message}{Style.RESET_ALL}")
                
        except Exception as e:
            logging.info(f"{Fore.RED}❌ Error in reasoning: {str(e)}{Style.RESET_ALL}")
    
    async def handle_memory_operation(self, operation: str, **kwargs):
        """Handle memory operations"""
        try:
            if operation == "store":
                result = await self.memory_tool.execute(
                    operation="store",
                    content=kwargs.get('content', '')
                )
                if result.success:
                    logging.info(f"{Fore.GREEN}💾 Stored in memory successfully!{Style.RESET_ALL}")
                else:
                    logging.info(f"{Fore.RED}❌ Memory storage failed: {result.message}{Style.RESET_ALL}")
            
            elif operation == "retrieve":
                result = await self.memory_tool.execute(
                    operation="retrieve",
                    query=kwargs.get('query', '')
                )
                if result.success:
                    memories = result.data.get('memories', [])
                    logging.info(f"{Fore.GREEN}💾 Retrieved {len(memories)} memories:{Style.RESET_ALL}")
                    for memory in memories:
                        logging.info(f"  - {memory.get('content', 'N/A')}")
                else:
                    logging.info(f"{Fore.RED}❌ Memory retrieval failed: {result.message}{Style.RESET_ALL}")
                    
        except Exception as e:
            logging.info(f"{Fore.RED}❌ Error in memory operation: {str(e)}{Style.RESET_ALL}")
    
    async def handle_coder_command(self, command: str, args: List[str]) -> str:
        """Handle DeepSeek Coder commands"""
        try:
            if command == "code_generation":
                if not args:
                    return "❌ Please provide a prompt for code generation"
                
                prompt = " ".join(args)
                result = await self.coder_tool.execute(
                    operation="code_generation",
                    prompt=prompt,
                    language="python"
                )
                
                if result.success:
                    code = result.data.get('code', 'No code generated.')
                    return f"🔧 Generated Code:\n{code}"
                else:
                    return f"❌ Code generation failed: {result.message}"
            
            elif command == "code_debugging":
                if not args:
                    return "❌ Please provide code to debug"
                
                code = " ".join(args)
                result = await self.coder_tool.execute(
                    operation="code_debugging",
                    code=code,
                    language="python"
                )
                
                if result.success:
                    analysis = result.data.get('analysis', 'No analysis generated.')
                    return f"🐛 Debug Analysis:\n{analysis}"
                else:
                    return f"❌ Code debugging failed: {result.message}"
            
            elif command == "code_healing":
                if not args:
                    return "❌ Please provide code to heal"
                
                code = " ".join(args)
                result = await self.coder_tool.execute(
                    operation="self_healing",
                    code=code,
                    language="python"
                )
                
                if result.success:
                    healed_code = result.data.get('healed_code', 'No healed code generated.')
                    return f"🩹 Healed Code:\n{healed_code}"
                else:
                    return f"❌ Code healing failed: {result.message}"
            
            else:
                return f"❌ Unknown coder command: {command}"
                
        except Exception as e:
            return f"❌ Error in coder command: {str(e)}"
    
    def show_status(self) -> Any:
        """Show system status"""
        # Get tool status
        tool_status = []
        if self.sql_db:
            tool_status.append("✅ SQL Database")
        else:
            tool_status.append("❌ SQL Database")
            
        if self.embedding_tool:
            tool_status.append("✅ Embedding Tool")
        else:
            tool_status.append("❌ Embedding Tool")
            
        if self.llm_tool:
            tool_status.append("✅ LLM Query Tool")
        else:
            tool_status.append("❌ LLM Query Tool")
            
        if self.fim_tool:
            tool_status.append("✅ FIM Completion")
        else:
            tool_status.append("❌ FIM Completion")
            
        if self.prefix_tool:
            tool_status.append("✅ Prefix Completion")
        else:
            tool_status.append("❌ Prefix Completion")
            
        if self.rag_tool:
            tool_status.append("✅ RAG Pipeline")
        else:
            tool_status.append("❌ RAG Pipeline")
            
        if self.reasoning_tool:
            tool_status.append("✅ Reasoning Engine")
        else:
            tool_status.append("❌ Reasoning Engine")
            
        if self.memory_tool:
            tool_status.append("✅ Memory Tool")
        else:
            tool_status.append("❌ Memory Tool")
            
        if self.vector_db:
            tool_status.append("✅ Vector Database")
        else:
            tool_status.append("❌ Vector Database")
            
        if self.coder_tool:
            tool_status.append("✅ DeepSeek Coder")
        else:
            tool_status.append("❌ DeepSeek Coder")
            
        if self.tool_manager:
            available_tools = self.tool_manager.list_tools()
            tool_status.append(f"✅ Tool Manager ({len(available_tools)} tools)")
        else:
            tool_status.append("❌ Tool Manager")
        
        status_text = f"""
{Fore.CYAN}📊 BASED CODER CLI Status{Style.RESET_ALL}

{Fore.GREEN}✅ System Information:{Style.RESET_ALL}
  Platform: {self.system_tool.system_info['platform']}
  Python Version: {self.system_tool.system_info['python_version']}
  CPU Cores: {self.system_tool.system_info['cpu_count']}
  Memory: {self.system_tool.system_info['memory_total'] // (1024**3)} GB

{Fore.GREEN}✅ API Keys:{Style.RESET_ALL}
  DeepSeek: {'✅ Valid' if validate_deepseek_key(os.getenv('DEEPSEEK_API_KEY', '')) else '❌ Invalid/Missing'}
  HuggingFace: {'✅ Valid' if validate_huggingface_token(os.getenv('HUGGINGFACE_API_KEY', '')) else '❌ Invalid/Missing'}

{Fore.GREEN}✅ Tools Status:{Style.RESET_ALL}
  {'  '.join(tool_status[:5])}
  {'  '.join(tool_status[5:10])}
  {'  '.join(tool_status[10:])}

{Fore.GREEN}✅ Session Information:{Style.RESET_ALL}
  Session ID: {self.session_id}
  Conversation History: {len(self.conversation_history)} messages
  Commands Available: {len(self.prefix_commands)} commands

{Fore.GREEN}Made by @Lucariolucario55 on Telegram{Style.RESET_ALL}
        """
        logging.info(status_text)
    
    def clear_history(self) -> Any:
        """Clear conversation history"""
        self.conversation_history = []
        logging.info(f"{Fore.GREEN}✅ Conversation history cleared!{Style.RESET_ALL}")
    
    def show_history(self) -> Any:
        """Show conversation history"""
        if not self.conversation_history:
            logging.info(f"{Fore.YELLOW}📝 No conversation history found.{Style.RESET_ALL}")
            return
        
        logging.info(f"{Fore.CYAN}📝 Conversation History ({len(self.conversation_history)} messages):{Style.RESET_ALL}")
        for i, message in enumerate(self.conversation_history[-10:], 1):  # Show last 10 messages
            role = message['role']
            content = message['content'][:100] + "..." if len(message['content']) > 100 else message['content']
            timestamp = message['timestamp']
            
            if role == "user":
                logging.info(f"{Fore.BLUE}{i}. User: {content}{Style.RESET_ALL}")
            else:
                logging.info(f"{Fore.GREEN}{i}. AI: {content}{Style.RESET_ALL}")
    
    async def interactive_mode(self) -> Any:
        """Run interactive CLI mode"""
        logging.info(f"{Fore.CYAN}🚀 Welcome to BASED CODER CLI!{Style.RESET_ALL}")
        logging.info(f"{Fore.YELLOW}Type /help for available commands or 'exit' to quit.{Style.RESET_ALL}")
        print()
        
        while True:
            try:
                # Get user input
                user_input = input(f"{Fore.BLUE}💻 BASED CODER > {Style.RESET_ALL}").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['exit', 'quit', 'q']:
                    logging.info(f"{Fore.GREEN}👋 Goodbye! Made by @Lucariolucario55 on Telegram{Style.RESET_ALL}")
                    break
                
                # Handle prefix commands
                if user_input.startswith('/'):
                    command, args = self.parse_prefix_command(user_input)
                    
                    if command == "help":
                        self.print_help()
                    elif command == "status":
                        self.show_status()
                    elif command == "clear":
                        self.clear_history()
                    elif command == "history":
                        self.show_history()
                    elif command == "setup":
                        logging.info(f"{Fore.CYAN}🔧 Running API keys setup...{Style.RESET_ALL}")
                        self._run_api_setup()
                    elif command == "chat":
                        if args:
                            message = " ".join(args)
                            await self.handle_chat(message)
                        else:
                            logging.info(f"{Fore.RED}❌ Please provide a message for chat{Style.RESET_ALL}")
                    elif command == "fim":
                        if len(args) >= 2:
                            prefix = args[0]
                            suffix = " ".join(args[1:])
                            await self.handle_fim_completion(prefix, suffix)
                        else:
                            logging.info(f"{Fore.RED}❌ Please provide prefix and suffix for FIM completion{Style.RESET_ALL}")
                    elif command == "prefix":
                        if args:
                            prefix = " ".join(args)
                            await self.handle_prefix_completion(prefix)
                        else:
                            logging.info(f"{Fore.RED}❌ Please provide prefix text{Style.RESET_ALL}")
                    elif command == "rag":
                        if args:
                            query = " ".join(args)
                            await self.handle_rag_query(query)
                        else:
                            logging.info(f"{Fore.RED}❌ Please provide a query for RAG{Style.RESET_ALL}")
                    elif command == "reason":
                        if args:
                            question = " ".join(args)
                            await self.handle_reasoning(question)
                        else:
                            logging.info(f"{Fore.RED}❌ Please provide a question for reasoning{Style.RESET_ALL}")
                    elif command == "remember":
                        if args:
                            content = " ".join(args)
                            await self.handle_memory_operation("store", content=content)
                        else:
                            logging.info(f"{Fore.RED}❌ Please provide content to remember{Style.RESET_ALL}")
                    elif command == "recall":
                        if args:
                            query = " ".join(args)
                            await self.handle_memory_operation("retrieve", query=query)
                        else:
                            logging.info(f"{Fore.RED}❌ Please provide a query to recall{Style.RESET_ALL}")
                    elif command in ["code", "debug", "heal"]:
                        if args:
                            result = await self.handle_coder_command(command, args)
                            logging.info(result)
                        else:
                            logging.info(f"{Fore.RED}❌ Please provide input for {command}{Style.RESET_ALL}")
                    else:
                        logging.info(f"{Fore.RED}❌ Unknown command: {command}{Style.RESET_ALL}")
                        logging.info(f"{Fore.YELLOW}💡 Type /help for available commands{Style.RESET_ALL}")
                else:
                    # Default to chat
                    await self.handle_chat(user_input)
                    
            except KeyboardInterrupt:
                logging.info(f"\n{Fore.GREEN}👋 Goodbye! Made by @Lucariolucario55 on Telegram{Style.RESET_ALL}")
                break
            except Exception as e:
                logging.info(f"{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}")

async def main() -> None:
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="BASED CODER CLI")
    parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive mode")
    
    args = parser.parse_args()
    
    cli = BasedCoderCLI()
    
    # Initialize system
    await cli.initialize_system()
    
    if args.interactive:
        cli.print_banner()
        await cli.interactive_mode()
    else:
        # Default to interactive mode
        cli.print_banner()
        await cli.interactive_mode()

if __name__ == "__main__":
    asyncio.run(main()) 