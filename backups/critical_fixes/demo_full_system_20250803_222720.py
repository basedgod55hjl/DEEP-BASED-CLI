import logging
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)
#!/usr/bin/env python3
"""
🚀 BASED CODER CLI - Full System Demo
Demonstrates all features including prefix commands and system access
Made by @Lucariolucario55 on Telegram
"""

import asyncio
import sys
from pathlib import Path
import colorama
from colorama import Fore, Style
import json

# Initialize colorama
colorama.init()

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from based_coder_cli import RainbowCLI

class SystemDemo:
    """Demo class for showcasing BASED CODER features"""
    
    def __init__(self) -> Any:
        self.cli = RainbowCLI()
        self.demo_commands = [
            # Basic CLI commands
            ("help", "Show help menu"),
            ("status", "Show system status"),
            
            # Chat and AI features
            ("chat Hello, I'm testing BASED CODER!", "Basic chat"),
            ("fim def hello() -> None:" "logger.info('world')", "FIM completion"),
            ("prefix The quick brown fox", "Prefix completion"),
            ("rag What is machine learning?", "RAG pipeline"),
            ("reason Why is the sky blue?", "Reasoning engine"),
            
            # Memory features
            ("remember BASED CODER is an amazing AI CLI", "Store memory"),
            ("recall BASED CODER", "Recall memory"),
            
            # System access commands
            ("/stats", "Show system statistics"),
            ("/ps", "Show running processes"),
            ("/ls .", "List current directory"),
            ("/info based_coder_cli.py", "Get file info"),
            ("/write demo_test.txt Hello from BASED CODER!", "Write file"),
            ("/cat demo_test.txt", "Read file"),
            ("/mkdir demo_folder", "Create directory"),
            ("/exec echo 'BASED CODER is awesome!'", "Execute command"),
            ("/rm demo_test.txt", "Delete file"),
            
            # Prefix commands (quick access)
            ("/chat How are you today?", "Quick chat"),
            ("/fim def greet() -> None:" "logger.info('Hello')", "Quick FIM"),
            ("/prefix Machine learning is", "Quick prefix"),
            ("/rag Explain neural networks", "Quick RAG"),
            ("/reason How do computers work?", "Quick reasoning"),
            ("/remember Neural networks are powerful", "Quick memory store"),
            ("/recall neural", "Quick memory recall"),
            ("/status", "Quick status"),
            ("/history", "Quick history"),
            ("/clear", "Quick clear"),
        ]
    
    def print_demo_banner(self) -> Any:
        """Print demo banner"""
        banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  🚀 BASED CODER CLI - FULL SYSTEM DEMO                                      ║
║                                                                              ║
║  Features:                                                                   ║
║  ✅ Rainbow Interface & Colorful Agents                                      ║
║  ✅ Multi-Round Conversations with Context Caching                           ║
║  ✅ Function Calls and Reasoning Capabilities                                ║
║  ✅ FIM and Prefix Completion                                                ║
║  ✅ RAG Pipeline with Vector Search                                          ║
║  ✅ Memory and Persona Management                                            ║
║  ✅ Full PC Access with OS Operations                                        ║
║  ✅ Prefix Commands for Quick Access                                         ║
║                                                                              ║
║  Made by @Lucariolucario55 on Telegram                                      ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
        """
        logger.info(banner)
    
    async def run_demo(self) -> Any:
        """Run the full system demo"""
        self.print_demo_banner()
        
        logger.info(f"{Fore.GREEN}🎯 Initializing BASED CODER system...{Style.RESET_ALL}")
        await self.cli.initialize_system()
        
        logger.info(f"{Fore.GREEN}✅ System initialized successfully!{Style.RESET_ALL}")
        logger.info(f"{Fore.YELLOW}🚀 Starting demo...{Style.RESET_ALL}\n")
        
        # Run demo commands
        for i, (command, description) in enumerate(self.demo_commands, 1):
            logger.info(f"{Fore.CYAN}📋 Demo {i}/{len(self.demo_commands)}: {description}{Style.RESET_ALL}")
            logger.info(f"{Fore.YELLOW}💻 Command: {command}{Style.RESET_ALL}")
            
            try:
                # Parse and execute command
                if command.startswith('/'):
                    # Handle prefix commands
                    prefix_command, prefix_args = self.cli.parse_prefix_command(command)
                    if prefix_command:
                        if prefix_command in ["list_directory", "read_file", "write_file", "create_directory", 
                                           "delete_file", "get_processes", "get_system_stats", "execute_command", 
                                           "get_file_info"]:
                            response = await self.cli.handle_system_command(prefix_command, prefix_args)
                        else:
                            # Handle regular prefix commands
                            if prefix_command == "chat":
                                response = await self.cli.handle_chat(" ".join(prefix_args))
                            elif prefix_command == "fim":
                                if len(prefix_args) >= 2:
                                    response = await self.cli.handle_fim_completion(prefix_args[0], prefix_args[1])
                                else:
                                    response = "❌ Usage: /fim <prefix> <suffix>"
                            elif prefix_command == "prefix":
                                response = await self.cli.handle_prefix_completion(" ".join(prefix_args))
                            elif prefix_command == "rag":
                                response = await self.cli.handle_rag_query(" ".join(prefix_args))
                            elif prefix_command == "reason":
                                response = await self.cli.handle_reasoning(" ".join(prefix_args))
                            elif prefix_command == "remember":
                                response = await self.cli.handle_memory_operation("store", content=" ".join(prefix_args))
                            elif prefix_command == "recall":
                                response = await self.cli.handle_memory_operation("search", query=" ".join(prefix_args))
                            elif prefix_command == "status":
                                self.cli.print_status()
                                response = "Status displayed"
                            elif prefix_command == "history":
                                response = f"Conversation history: {len(self.cli.conversation_history)} messages"
                            elif prefix_command == "clear":
                                self.cli.conversation_history = []
                                self.cli.context_cache = {}
                                response = "History and cache cleared"
                            else:
                                response = f"❌ Unknown prefix command: {prefix_command}"
                    else:
                        response = f"❌ Unknown command: {command}"
                else:
                    # Handle regular commands
                    parts = command.split()
                    cmd = parts[0].lower()
                    args = parts[1:] if len(parts) > 1 else []
                    
                    if cmd == "help":
                        self.cli.print_help()
                        response = "Help displayed"
                    elif cmd == "status":
                        self.cli.print_status()
                        response = "Status displayed"
                    elif cmd == "chat":
                        message = " ".join(args)
                        response = await self.cli.handle_chat(message)
                    elif cmd == "fim":
                        if len(args) >= 2:
                            response = await self.cli.handle_fim_completion(args[0], args[1])
                        else:
                            response = "❌ Usage: fim <prefix> <suffix>"
                    elif cmd == "prefix":
                        response = await self.cli.handle_prefix_completion(" ".join(args))
                    elif cmd == "rag":
                        response = await self.cli.handle_rag_query(" ".join(args))
                    elif cmd == "reason":
                        response = await self.cli.handle_reasoning(" ".join(args))
                    elif cmd == "remember":
                        response = await self.cli.handle_memory_operation("store", content=" ".join(args))
                    elif cmd == "recall":
                        response = await self.cli.handle_memory_operation("search", query=" ".join(args))
                    else:
                        response = f"❌ Unknown command: {cmd}"
                
                # Display response
                logger.info(f"{Fore.GREEN}✅ Response:{Style.RESET_ALL}")
                if isinstance(response, dict):
                    logger.info(f"{Fore.WHITE}{json.dumps(response, indent=2)}{Style.RESET_ALL}")
                else:
                    logger.info(f"{Fore.WHITE}{response}{Style.RESET_ALL}")
                
            except Exception as e:
                logger.info(f"{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}")
            
            logger.info(f"{Fore.BLUE}{'='*80}{Style.RESET_ALL}\n")
            
            # Small delay between commands
            await asyncio.sleep(1)
        
        logger.info(f"{Fore.GREEN}🎉 Demo completed successfully!{Style.RESET_ALL}")
        logger.info(f"{Fore.YELLOW}💡 Try running the CLI interactively: python based_coder_cli.py{Style.RESET_ALL}")

async def main() -> None:
    """Main demo function"""
    demo = SystemDemo()
    await demo.run_demo()

if __name__ == "__main__":
    asyncio.run(main()) 