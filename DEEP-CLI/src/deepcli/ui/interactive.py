"""
Interactive CLI interface for DeepCLI
"""

import asyncio
import os
from typing import List, Optional

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

from ..commands.base import command_registry
from ..core.client import DeepSeekClient
from ..core.config import get_config
from ..core.models import CommandContext, Message
from ..memory.manager import MemoryManager


class InteractiveCLI:
    """Interactive command-line interface"""
    
    def __init__(self):
        self.config = get_config()
        self.client = DeepSeekClient(self.config)
        self.memory = MemoryManager(self.config.memory_db_path)
        self.console = Console()
        self.messages: List[Message] = []
        self.session_id = None
        
        # Setup prompt session with history
        history_file = self.config.memory_db_path.parent / "history.txt"
        self.prompt_session = PromptSession(
            history=FileHistory(str(history_file)),
            style=Style.from_dict({
                'prompt': '#00aa00 bold',
                'completion': 'bg:#333333 #ffffff',
            })
        )
        
        # Setup command completer
        commands = [f"/{cmd}" for cmd in command_registry.commands.keys()]
        commands.extend(["/help", "/exit", "/clear", "/stats", "/history"])
        self.completer = WordCompleter(commands, ignore_case=True)
    
    async def run(self):
        """Run the interactive CLI"""
        try:
            while True:
                try:
                    # Get user input
                    user_input = await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: self.prompt_session.prompt(
                            "You> ",
                            completer=self.completer,
                            complete_while_typing=True
                        )
                    )
                    
                    if not user_input.strip():
                        continue
                    
                    # Handle special commands
                    if user_input.lower() == "/exit":
                        self.console.print("[yellow]Goodbye![/yellow]")
                        break
                    elif user_input.lower() == "/clear":
                        os.system('clear' if os.name != 'nt' else 'cls')
                        continue
                    elif user_input.lower() == "/help":
                        self.show_help()
                        continue
                    elif user_input.lower() == "/stats":
                        await self.show_stats()
                        continue
                    elif user_input.lower() == "/history":
                        await self.show_history()
                        continue
                    
                    # Try to execute as command
                    if user_input.startswith('/'):
                        context = CommandContext(
                            command_type=None,  # Will be set by command
                            args=[],
                            cwd=os.getcwd(),
                            project_type=self.detect_project_type(),
                            files=self.get_context_files(),
                            memory_namespace="interactive",
                            session_id=self.session_id
                        )
                        
                        result = await command_registry.execute(user_input, context)
                        if result:
                            self.console.print(Panel(result, title="Command Result", border_style="blue"))
                            continue
                    
                    # Regular chat
                    await self.handle_chat(user_input)
                    
                except KeyboardInterrupt:
                    self.console.print("\n[yellow]Use /exit to quit[/yellow]")
                    continue
                except EOFError:
                    self.console.print("\n[yellow]Goodbye![/yellow]")
                    break
                except Exception as e:
                    self.console.print(f"[red]Error: {str(e)}[/red]")
                    
        finally:
            # Save session summary
            await self.save_session()
    
    async def handle_chat(self, user_input: str):
        """Handle regular chat messages"""
        # Add user message
        self.messages.append(Message(role="user", content=user_input))
        
        # Store in memory
        await self.memory.store(
            key=f"msg_{len(self.messages)}",
            value={"role": "user", "content": user_input},
            namespace="chat_history"
        )
        
        try:
            # Stream response
            self.console.print("\n[bold cyan]Assistant:[/bold cyan]")
            
            response_text = ""
            async for chunk in await self.client.chat(self.messages, stream=True):
                self.console.print(chunk, end='')
                response_text += chunk
            
            self.console.print("\n")
            
            # Add assistant message
            self.messages.append(Message(role="assistant", content=response_text))
            
            # Store in memory
            await self.memory.store(
                key=f"msg_{len(self.messages)}",
                value={"role": "assistant", "content": response_text},
                namespace="chat_history"
            )
            
            # Show usage
            stats = self.client.get_usage_stats()
            self.console.print(
                f"[dim]Tokens: {stats['total_tokens']} | "
                f"Cost: {stats['estimated_cost']} | "
                f"Cache: {stats['cache_hit_rate']}[/dim]\n"
            )
            
        except Exception as e:
            self.console.print(f"[red]Chat error: {str(e)}[/red]")
    
    def show_help(self):
        """Show help information"""
        help_text = """
[bold cyan]DeepCLI Interactive Mode[/bold cyan]

[yellow]Chat Commands:[/yellow]
  Just type your message to chat with the AI

[yellow]Slash Commands:[/yellow]"""
        
        # Add registered commands
        for cmd in command_registry.list_commands():
            help_text += f"\n  /{cmd.name:<20} - {cmd.description}"
        
        help_text += """

[yellow]System Commands:[/yellow]
  /help                - Show this help message
  /clear               - Clear the screen
  /stats               - Show usage statistics
  /history             - Show recent chat history
  /exit                - Exit the application

[yellow]Tips:[/yellow]
  • Use Tab for command completion
  • Use Up/Down arrows for history
  • Commands support aliases (e.g., /impl for /deep:implement)
"""
        
        self.console.print(Panel(help_text, title="Help", border_style="blue"))
    
    async def show_stats(self):
        """Show usage statistics"""
        # API usage stats
        api_stats = self.client.get_usage_stats()
        
        table = Table(title="Usage Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Prompt Tokens", str(api_stats['prompt_tokens']))
        table.add_row("Completion Tokens", str(api_stats['completion_tokens']))
        table.add_row("Total Tokens", str(api_stats['total_tokens']))
        table.add_row("Cache Hit Tokens", str(api_stats['cache_hit_tokens']))
        table.add_row("Cache Hit Rate", api_stats['cache_hit_rate'])
        table.add_row("Estimated Cost", api_stats['estimated_cost'])
        
        self.console.print(table)
        
        # Memory stats
        memory_stats = await self.memory.get_stats()
        self.console.print(f"\n[yellow]Memory:[/yellow] {memory_stats['total_memories']} items across {len(memory_stats['namespaces'])} namespaces")
    
    async def show_history(self):
        """Show recent chat history"""
        recent = await self.memory.search("", namespace="chat_history", limit=10)
        
        if recent:
            self.console.print(Panel("Recent Chat History", style="yellow"))
            for item in reversed(recent):
                msg = item['value']
                role_color = "cyan" if msg['role'] == "user" else "green"
                content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
                self.console.print(f"[{role_color}]{msg['role'].title()}:[/{role_color}] {content}")
        else:
            self.console.print("[yellow]No chat history found[/yellow]")
    
    async def save_session(self):
        """Save session summary"""
        if self.messages:
            summary = f"Session with {len(self.messages)} messages"
            await self.memory.store(
                key=f"session_{self.session_id or 'interactive'}",
                value={
                    "message_count": len(self.messages),
                    "start_message": self.messages[0].content if self.messages else None,
                    "end_message": self.messages[-1].content if self.messages else None
                },
                namespace="sessions"
            )
    
    def detect_project_type(self) -> Optional[str]:
        """Detect the type of project in current directory"""
        cwd = os.getcwd()
        
        # Check for common project files
        if os.path.exists(os.path.join(cwd, "package.json")):
            return "node"
        elif os.path.exists(os.path.join(cwd, "requirements.txt")) or os.path.exists(os.path.join(cwd, "pyproject.toml")):
            return "python"
        elif os.path.exists(os.path.join(cwd, "go.mod")):
            return "go"
        elif os.path.exists(os.path.join(cwd, "Cargo.toml")):
            return "rust"
        elif os.path.exists(os.path.join(cwd, "pom.xml")):
            return "java"
        
        return None
    
    def get_context_files(self) -> List[str]:
        """Get relevant files from current directory"""
        # For now, return empty list
        # In full implementation, this would intelligently select relevant files
        return []