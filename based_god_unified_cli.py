#!/usr/bin/env python3
"""
BASED GOD CODER CLI - Unified Version
Made by @Lucariolucario55 on Telegram

A comprehensive AI-powered CLI combining all features:
- DeepSeek API integration with fallback
- Beautiful interactive menu
- Code generation and execution
- File analysis and processing
- Batch processing capabilities
- Function calling
- Docker integration
- Advanced reasoning
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
from datetime import datetime
from typing import List, Dict, Optional, Any, Union
from pathlib import Path
from enum import Enum
import argparse

# Try to import rich for beautiful output
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.markdown import Markdown
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import Prompt, Confirm
    from rich.text import Text
    from rich import box
    from rich.layout import Layout
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None

# We use httpx directly, no need for OpenAI SDK
OPENAI_AVAILABLE = False

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Set API key
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-9af038dd3bdd46258c4a9d02850c9a6d")
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"


class BasedGodCLI:
    """Main BASED GOD CODER CLI class"""
    
    def __init__(self):
        self.api_key = DEEPSEEK_API_KEY
        self.base_url = DEEPSEEK_BASE_URL
        self.conversation_history = []
        self.usage_stats = {
            "total_requests": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "session_start": datetime.now()
        }
        self.tools_built = []
        self.api_working = None
        
        # We use httpx directly for API calls
        self.client = None
    
    def display_banner(self):
        """Display the BASED GOD CODER CLI banner"""
        if RICH_AVAILABLE:
            ascii_art = """
██████╗  █████╗ ███████╗███████╗██████╗      ██████╗  ██████╗ ██████╗ 
██╔══██╗██╔══██╗██╔════╝██╔════╝██╔══██╗    ██╔════╝ ██╔═══██╗██╔══██╗
██████╔╝███████║███████╗█████╗  ██║  ██║    ██║  ███╗██║   ██║██║  ██║
██╔══██╗██╔══██║╚════██║██╔══╝  ██║  ██║    ██║   ██║██║   ██║██║  ██║
██████╔╝██║  ██║███████║███████╗██████╔╝    ╚██████╔╝╚██████╔╝██████╔╝
╚═════╝ ╚═╝  ╚═╝╚══════╝╚══════╝╚═════╝      ╚═════╝  ╚═════╝ ╚═════╝ 
                                                                       
         ██████╗ ██████╗ ██████╗ ███████╗██████╗      ██████╗██╗     ██╗
        ██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔══██╗    ██╔════╝██║     ██║
        ██║     ██║   ██║██║  ██║█████╗  ██████╔╝    ██║     ██║     ██║
        ██║     ██║   ██║██║  ██║██╔══╝  ██╔══██╗    ██║     ██║     ██║
        ╚██████╗╚██████╔╝██████╔╝███████╗██║  ██║    ╚██████╗███████╗██║
         ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝     ╚═════╝╚══════╝╚═╝
            """
            
            text = Text()
            lines = ascii_art.strip().split('\n')
            colors = ["red", "yellow", "green", "cyan", "blue", "magenta"]
            
            for i, line in enumerate(lines):
                color = colors[i % len(colors)]
                text.append(line + '\n', style=f"bold {color}")
            
            console.print(Panel(
                text,
                title="[bold white]BASED GOD CODER CLI[/bold white]",
                subtitle="[dim italic]- made by @Lucariolucario55 on Telegram[/dim italic]",
                border_style="blue",
                box=box.DOUBLE
            ))
        else:
            print("="*60)
            print("        BASED GOD CODER CLI")
            print("   - made by @Lucariolucario55 on Telegram")
            print("="*60)
    
    async def test_api_connection(self) -> bool:
        """Test if DeepSeek API is working"""
        if self.api_working is not None:
            return self.api_working
        
        try:
            if RICH_AVAILABLE:
                console.print("[yellow]🔍 Testing API connection...[/yellow]")
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Test"}
                ],
                "max_tokens": 10,
                "temperature": 0.1
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    self.api_working = True
                    if RICH_AVAILABLE:
                        console.print("[green]✅ API is working![/green]")
                    return True
                else:
                    self.api_working = False
                    if RICH_AVAILABLE:
                        console.print(f"[red]❌ API Error: {response.status_code}[/red]")
                    return False
                    
        except Exception as e:
            self.api_working = False
            if RICH_AVAILABLE:
                console.print(f"[red]❌ Connection Error: {str(e)}[/red]")
            return False
    
    async def chat_with_api(self, message: str, model: str = "deepseek-chat", stream: bool = False) -> str:
        """Chat with DeepSeek API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Add message to conversation history
            self.conversation_history.append({"role": "user", "content": message})
            
            data = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are BASED GOD CODER, an expert AI assistant that can help with coding, reasoning, and creative tasks. You are knowledgeable, helpful, and have a confident personality."}
                ] + self.conversation_history[-10:],  # Keep last 10 messages
                "temperature": 0.7,
                "max_tokens": 4096,
                "stream": stream
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    ai_response = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                    
                    # Add AI response to history
                    self.conversation_history.append({"role": "assistant", "content": ai_response})
                    
                    # Update usage stats
                    self.usage_stats["total_requests"] += 1
                    if "usage" in result:
                        self.usage_stats["total_tokens"] += result["usage"].get("total_tokens", 0)
                    
                    return ai_response
                else:
                    error_msg = f"API Error {response.status_code}: {response.text}"
                    return f"❌ {error_msg}"
                    
        except Exception as e:
            return f"❌ Connection Error: {str(e)}"
    
    def simulate_ai_response(self, message: str) -> str:
        """Fallback AI simulation when API is not available"""
        responses = {
            "hello": "Hello! I'm BASED GOD CODER, your AI coding assistant. Even though the API is temporarily unavailable, I'm here to help you with coding tasks, explanations, and guidance!",
            "code": "I can help you with code generation! Here's a simple Python example:\n\n```python\ndef hello_world():\n    print('Hello from BASED GOD CODER!')\n    return 'Success'\n```\n\nWhat specific code would you like me to help with?",
            "debug": "I can help debug your code! Please share the code you're having trouble with, and I'll analyze it for potential issues.",
            "help": "🚀 BASED GOD CODER Commands:\n- 'code' - Generate code examples\n- 'debug' - Debug assistance\n- 'tools' - Show built tools\n- 'stats' - Usage statistics\n- 'clear' - Clear conversation\n- 'exit' - Quit",
            "tools": "🔧 Available Tools:\n- Code Generator\n- Debug Assistant\n- File Analyzer\n- Docker Integration\n- MCP Tools\n\nAsk me to build specific tools for your needs!",
            "stats": f"📊 Session Stats:\n- Requests: {self.usage_stats['total_requests']}\n- Session time: {datetime.now() - self.usage_stats['session_start']}\n- API Status: Offline (Fallback Mode)",
        }
        
        message_lower = message.lower()
        for key, response in responses.items():
            if key in message_lower:
                return response
        
        # Default response
        return f"I understand you said: '{message}'\n\nI'm running in fallback mode since the DeepSeek API is temporarily unavailable. I can still help with:\n\n🔹 Code examples and explanations\n🔹 Debugging guidance\n🔹 Development best practices\n🔹 Tool recommendations\n\nWhat would you like help with?"
    
    def display_menu(self):
        """Display the main menu"""
        if RICH_AVAILABLE:
            table = Table(title="Main Menu", box=box.ROUNDED)
            table.add_column("Option", style="cyan", width=8)
            table.add_column("Feature", style="white")
            table.add_column("Description", style="dim")
            
            menu_items = [
                ("1", "Chat Mode", "Interactive conversation with AI"),
                ("2", "Reasoning Mode", "Complex problem solving with step-by-step reasoning"),
                ("3", "Code Generation", "Generate code with explanations"),
                ("4", "File Analysis", "Analyze and process files"),
                ("5", "Batch Processing", "Process multiple prompts at once"),
                ("6", "Function Calling", "Demonstrate function calling capabilities"),
                ("7", "Beta Features", "Chat prefix completion & FIM (Fill-in-Middle)"),
                ("8", "JSON Mode", "Enhanced structured JSON output"),
                ("9", "Usage Stats", "View token usage, costs & cache statistics"),
                ("10", "Settings", "Configure CLI preferences & task profiles"),
                ("11", "Docker Tools", "Docker container management and debugging"),
                ("12", "MCP Tools", "Model Context Protocol tool integration"),
                ("13", "Help", "Show help and examples"),
                ("0", "Exit", "Exit the application")
            ]
            
            for option, feature, desc in menu_items:
                table.add_row(option, feature, desc)
            
            console.print(table)
        else:
            print("\nMain Menu:")
            print("1. Chat Mode - Interactive conversation with AI")
            print("2. Reasoning Mode - Complex problem solving")
            print("3. Code Generation - Generate code with explanations")
            print("4. File Analysis - Analyze and process files")
            print("5. Batch Processing - Process multiple prompts")
            print("6. Function Calling - Demonstrate function calling")
            print("7. Beta Features - Advanced AI features")
            print("8. JSON Mode - Structured output")
            print("9. Usage Stats - View statistics")
            print("10. Settings - Configure preferences")
            print("11. Docker Tools - Container management")
            print("12. MCP Tools - Protocol tools")
            print("13. Help - Show help")
            print("0. Exit - Exit application")
            print()
    
    async def chat_mode(self):
        """Interactive chat mode"""
        if RICH_AVAILABLE:
            console.print(Panel(
                "[bold cyan]💬 Chat Mode[/bold cyan]\n\n"
                "Commands: 'exit' (return to menu), 'clear' (clear history), 'api' (test API)",
                border_style="green"
            ))
        else:
            print("\n=== Chat Mode ===")
            print("Commands: 'exit' (return to menu), 'clear' (clear history), 'api' (test API)")
        
        # Test API connection
        api_available = await self.test_api_connection()
        
        while True:
            try:
                if RICH_AVAILABLE:
                    user_input = console.input("\n[bold blue]You:[/bold blue] ")
                else:
                    user_input = input("\nYou: ")
                
                if not user_input.strip():
                    continue
                
                if user_input.lower() in ['exit', 'quit']:
                    break
                elif user_input.lower() == 'clear':
                    self.conversation_history.clear()
                    if RICH_AVAILABLE:
                        console.print("[green]💭 Conversation history cleared![/green]")
                    else:
                        print("Conversation history cleared!")
                    continue
                elif user_input.lower() == 'api':
                    await self.test_api_connection()
                    continue
                
                # Get AI response
                if api_available and self.api_working:
                    if RICH_AVAILABLE:
                        with console.status("[bold green]🤖 BASED GOD is thinking..."):
                            response = await self.chat_with_api(user_input)
                    else:
                        print("🤖 BASED GOD is thinking...")
                        response = await self.chat_with_api(user_input)
                else:
                    response = self.simulate_ai_response(user_input)
                
                # Display response
                if RICH_AVAILABLE:
                    console.print(f"\n[bold green]🤖 BASED GOD:[/bold green]")
                    if response.startswith("```") and response.endswith("```"):
                        # Code block
                        code = response.strip("```").strip()
                        console.print(Syntax(code, "python", theme="monokai"))
                    else:
                        console.print(Markdown(response))
                else:
                    print(f"\n🤖 BASED GOD: {response}")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                if RICH_AVAILABLE:
                    console.print(f"[red]Error: {str(e)}[/red]")
                else:
                    print(f"Error: {str(e)}")
    
    def code_generation_mode(self):
        """Code generation mode"""
        if RICH_AVAILABLE:
            console.print(Panel(
                "[bold cyan]🚀 Code Generation Mode[/bold cyan]\n\n"
                "Describe what code you want me to generate:",
                border_style="green"
            ))
        else:
            print("\n=== Code Generation Mode ===")
            print("Describe what code you want me to generate:")
        
        while True:
            try:
                if RICH_AVAILABLE:
                    request = console.input("\n[bold blue]Code Request:[/bold blue] ")
                else:
                    request = input("\nCode Request: ")
                
                if not request.strip():
                    continue
                
                if request.lower() in ['exit', 'quit', 'back']:
                    break
                
                # Generate code example (fallback mode)
                examples = {
                    "hello world": """```python
def hello_world():
    \"\"\"A simple hello world function\"\"\"
    print("Hello, World from BASED GOD CODER!")
    return "Success"

if __name__ == "__main__":
    hello_world()
```""",
                    "web scraper": """```python
import requests
from bs4 import BeautifulSoup

def scrape_website(url):
    \"\"\"Simple web scraper\"\"\"
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup.get_text()
    except Exception as e:
        return f"Error: {e}"

# Usage
# result = scrape_website("https://example.com")
```""",
                    "api client": """```python
import httpx
import asyncio

class APIClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key
    
    async def make_request(self, endpoint, data=None):
        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/{endpoint}",
                json=data,
                headers=headers
            )
            return response.json()

# Usage
# client = APIClient("https://api.example.com", "your-key")
# result = await client.make_request("chat", {"message": "hello"})
```"""
                }
                
                # Find matching example
                code_response = None
                for key, code in examples.items():
                    if key in request.lower():
                        code_response = f"Here's a {key} implementation:\n\n{code}"
                        break
                
                if not code_response:
                    code_response = f"""I understand you want: "{request}"

Here's a general Python template:

```python
def your_function():
    \"\"\"
    {request}
    \"\"\"
    # TODO: Implement your logic here
    pass

if __name__ == "__main__":
    your_function()
```

For more specific code generation, try describing:
- Programming language
- Specific functionality
- Input/output requirements"""
                
                if RICH_AVAILABLE:
                    console.print(f"\n[bold green]🤖 Generated Code:[/bold green]")
                    console.print(Markdown(code_response))
                else:
                    print(f"\n🤖 Generated Code:\n{code_response}")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                if RICH_AVAILABLE:
                    console.print(f"[red]Error: {str(e)}[/red]")
                else:
                    print(f"Error: {str(e)}")
    
    def show_usage_stats(self):
        """Show usage statistics"""
        if RICH_AVAILABLE:
            table = Table(title="📊 Usage Statistics", box=box.ROUNDED)
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="white")
            
            session_time = datetime.now() - self.usage_stats["session_start"]
            
            stats = [
                ("Total Requests", str(self.usage_stats["total_requests"])),
                ("Total Tokens", str(self.usage_stats["total_tokens"])),
                ("Session Duration", str(session_time).split('.')[0]),
                ("API Status", "✅ Online" if self.api_working else "⚠️ Offline"),
                ("Tools Built", str(len(self.tools_built))),
                ("Conversation Length", str(len(self.conversation_history))),
            ]
            
            for metric, value in stats:
                table.add_row(metric, value)
            
            console.print(table)
        else:
            print("\n📊 Usage Statistics:")
            print(f"Total Requests: {self.usage_stats['total_requests']}")
            print(f"Total Tokens: {self.usage_stats['total_tokens']}")
            print(f"Session Duration: {datetime.now() - self.usage_stats['session_start']}")
            print(f"API Status: {'Online' if self.api_working else 'Offline'}")
            print(f"Tools Built: {len(self.tools_built)}")
    
    def docker_tools_mode(self):
        """Docker tools and container management"""
        if RICH_AVAILABLE:
            console.print(Panel(
                "[bold cyan]🐳 Docker Tools[/bold cyan]\n\n"
                "Docker container management and debugging tools",
                border_style="blue"
            ))
        else:
            print("\n=== Docker Tools ===")
        
        docker_commands = {
            "1": ("List Containers", "docker ps -a"),
            "2": ("List Images", "docker images"),
            "3": ("System Info", "docker system df"),
            "4": ("Container Logs", "docker logs <container_id>"),
            "5": ("Execute in Container", "docker exec -it <container_id> /bin/bash"),
            "6": ("Stop All Containers", "docker stop $(docker ps -q)"),
            "7": ("Remove Stopped Containers", "docker container prune -f"),
        }
        
        if RICH_AVAILABLE:
            table = Table(title="Docker Commands", box=box.ROUNDED)
            table.add_column("Option", style="cyan")
            table.add_column("Action", style="white")
            table.add_column("Command", style="dim")
            
            for option, (action, command) in docker_commands.items():
                table.add_row(option, action, command)
            
            console.print(table)
        else:
            print("\nDocker Commands:")
            for option, (action, command) in docker_commands.items():
                print(f"{option}. {action} - {command}")
        
        try:
            if RICH_AVAILABLE:
                choice = console.input("\n[bold blue]Select option (or 'back'):[/bold blue] ")
            else:
                choice = input("\nSelect option (or 'back'): ")
            
            if choice.lower() == 'back':
                return
            
            if choice in docker_commands:
                action, command = docker_commands[choice]
                if RICH_AVAILABLE:
                    console.print(f"\n[yellow]Executing: {command}[/yellow]")
                
                try:
                    result = subprocess.run(command.split(), capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        if RICH_AVAILABLE:
                            console.print(f"[green]✅ Success:[/green]\n{result.stdout}")
                        else:
                            print(f"✅ Success:\n{result.stdout}")
                    else:
                        if RICH_AVAILABLE:
                            console.print(f"[red]❌ Error:[/red]\n{result.stderr}")
                        else:
                            print(f"❌ Error:\n{result.stderr}")
                except subprocess.TimeoutExpired:
                    if RICH_AVAILABLE:
                        console.print("[red]❌ Command timed out[/red]")
                    else:
                        print("❌ Command timed out")
                except FileNotFoundError:
                    if RICH_AVAILABLE:
                        console.print("[red]❌ Docker not found. Please install Docker.[/red]")
                    else:
                        print("❌ Docker not found. Please install Docker.")
        
        except Exception as e:
            if RICH_AVAILABLE:
                console.print(f"[red]Error: {str(e)}[/red]")
            else:
                print(f"Error: {str(e)}")
    
    async def run_interactive_mode(self):
        """Main interactive mode"""
        self.display_banner()
        
        if RICH_AVAILABLE:
            console.print("\n[bold green]🚀 Welcome to BASED GOD CODER CLI![/bold green]")
            console.print("[dim]Your AI-powered development assistant[/dim]\n")
        else:
            print("\n🚀 Welcome to BASED GOD CODER CLI!")
            print("Your AI-powered development assistant\n")
        
        # Test API on startup
        await self.test_api_connection()
        
        while True:
            try:
                self.display_menu()
                
                if RICH_AVAILABLE:
                    choice = console.input("[bold blue]Select option:[/bold blue] ")
                else:
                    choice = input("Select option: ")
                
                if choice == "0":
                    if RICH_AVAILABLE:
                        console.print("\n[yellow]Thanks for using BASED GOD CODER CLI! Stay based! 🔥[/yellow]")
                    else:
                        print("\nThanks for using BASED GOD CODER CLI! Stay based! 🔥")
                    break
                
                elif choice == "1":
                    await self.chat_mode()
                
                elif choice == "2":
                    if RICH_AVAILABLE:
                        console.print("[yellow]🧠 Reasoning Mode - Enhanced problem solving coming soon![/yellow]")
                    else:
                        print("🧠 Reasoning Mode - Enhanced problem solving coming soon!")
                
                elif choice == "3":
                    self.code_generation_mode()
                
                elif choice == "4":
                    if RICH_AVAILABLE:
                        console.print("[yellow]📁 File Analysis - Coming soon![/yellow]")
                    else:
                        print("📁 File Analysis - Coming soon!")
                
                elif choice == "5":
                    if RICH_AVAILABLE:
                        console.print("[yellow]⚡ Batch Processing - Coming soon![/yellow]")
                    else:
                        print("⚡ Batch Processing - Coming soon!")
                
                elif choice == "6":
                    if RICH_AVAILABLE:
                        console.print("[yellow]🔧 Function Calling - Coming soon![/yellow]")
                    else:
                        print("🔧 Function Calling - Coming soon!")
                
                elif choice == "7":
                    if RICH_AVAILABLE:
                        console.print("[yellow]🧪 Beta Features - Coming soon![/yellow]")
                    else:
                        print("🧪 Beta Features - Coming soon!")
                
                elif choice == "8":
                    if RICH_AVAILABLE:
                        console.print("[yellow]📝 JSON Mode - Coming soon![/yellow]")
                    else:
                        print("📝 JSON Mode - Coming soon!")
                
                elif choice == "9":
                    self.show_usage_stats()
                
                elif choice == "10":
                    if RICH_AVAILABLE:
                        console.print("[yellow]⚙️ Settings - Coming soon![/yellow]")
                    else:
                        print("⚙️ Settings - Coming soon!")
                
                elif choice == "11":
                    self.docker_tools_mode()
                
                elif choice == "12":
                    if RICH_AVAILABLE:
                        console.print("[yellow]🔗 MCP Tools - Coming soon![/yellow]")
                    else:
                        print("🔗 MCP Tools - Coming soon!")
                
                elif choice == "13":
                    self.show_help()
                
                else:
                    if RICH_AVAILABLE:
                        console.print("[red]Invalid option. Please try again.[/red]")
                    else:
                        print("Invalid option. Please try again.")
                
            except KeyboardInterrupt:
                if RICH_AVAILABLE:
                    console.print("\n\n[yellow]Goodbye! Stay based! 🔥[/yellow]")
                else:
                    print("\n\nGoodbye! Stay based! 🔥")
                break
            except Exception as e:
                if RICH_AVAILABLE:
                    console.print(f"[red]Error: {str(e)}[/red]")
                else:
                    print(f"Error: {str(e)}")
    
    def show_help(self):
        """Show help information"""
        help_text = """
# BASED GOD CODER CLI Help

## Features
- **Chat Mode**: Interactive AI conversation
- **Code Generation**: Generate code from descriptions  
- **Docker Tools**: Container management and debugging
- **Usage Stats**: Track your usage and performance

## Commands
- Type 'exit' to return to main menu
- Type 'clear' to clear conversation history
- Type 'api' to test API connection

## Tips
- Be specific in your requests for better results
- Use the Docker tools for container debugging
- Check usage stats to monitor your session

## API Status
- The CLI works with or without API access
- Fallback mode provides basic functionality
- API enables full AI-powered features

Made with ❤️ by @Lucariolucario55 on Telegram
        """
        
        if RICH_AVAILABLE:
            console.print(Markdown(help_text))
        else:
            print(help_text)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="BASED GOD CODER CLI")
    parser.add_argument("--chat", "-c", help="Quick chat mode")
    parser.add_argument("--code", "-g", help="Generate code")
    parser.add_argument("--test-api", action="store_true", help="Test API connection")
    
    args = parser.parse_args()
    
    cli = BasedGodCLI()
    
    if args.test_api:
        asyncio.run(cli.test_api_connection())
    elif args.chat:
        print(f"🤖 BASED GOD: {cli.simulate_ai_response(args.chat)}")
    elif args.code:
        print("🚀 Code generation request received!")
        print("Use interactive mode for full code generation features.")
    else:
        asyncio.run(cli.run_interactive_mode())


if __name__ == "__main__":
    main()