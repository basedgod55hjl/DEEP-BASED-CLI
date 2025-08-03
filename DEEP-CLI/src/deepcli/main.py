"""
Main CLI entry point for DeepCLI
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Optional

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .core.client import DeepSeekClient
from .core.config import get_config, update_config
from .core.models import DeepSeekModel, CommandContext
from .commands.base import command_registry
from .commands.implement import ImplementCommand
from .memory.manager import MemoryManager
from .ui.interactive import InteractiveCLI

# Load environment variables
load_dotenv()

# Initialize console
console = Console()


@click.group(invoke_without_command=True)
@click.option('--config', '-c', type=click.Path(), help='Config file path')
@click.option('--api-key', envvar='DEEPSEEK_API_KEY', help='DeepSeek API key')
@click.option('--model', type=click.Choice(['chat', 'reasoner']), help='Model to use')
@click.pass_context
def cli(ctx: click.Context, config: Optional[str], api_key: Optional[str], model: Optional[str]):
    """
    DeepCLI - A powerful AI-powered CLI for DeepSeek models
    
    Run without arguments to start interactive mode.
    """
    # Update configuration if provided
    if api_key:
        update_config(api_key=api_key)
    if model:
        update_config(default_model=DeepSeekModel.CHAT if model == 'chat' else DeepSeekModel.REASONER)
    
    # If no subcommand, launch interactive mode
    if ctx.invoked_subcommand is None:
        asyncio.run(interactive_mode())


@cli.command()
@click.argument('message', required=False)
@click.option('--stream', '-s', is_flag=True, help='Stream the response')
@click.option('--model', '-m', type=click.Choice(['chat', 'reasoner']), help='Model to use')
@click.option('--temperature', '-t', type=float, help='Temperature (0.0-2.0)')
async def chat(message: Optional[str], stream: bool, model: Optional[str], temperature: Optional[float]):
    """Send a chat message to DeepSeek"""
    config = get_config()
    client = DeepSeekClient(config)
    
    if not message:
        message = click.prompt("Enter your message")
    
    # Determine model
    model_enum = None
    if model:
        model_enum = DeepSeekModel.CHAT if model == 'chat' else DeepSeekModel.REASONER
    
    try:
        if stream:
            console.print("[yellow]Streaming response...[/yellow]")
            async for chunk in await client.chat(message, model=model_enum, temperature=temperature, stream=True):
                console.print(chunk, end='')
            console.print()
        else:
            with console.status("[yellow]Thinking...[/yellow]"):
                response = await client.chat(message, model=model_enum, temperature=temperature)
            
            if isinstance(response, dict) and 'function_calls' in response:
                # Handle function calls
                console.print(Panel(response['content'], title="Response", border_style="green"))
                console.print("\n[yellow]Function calls requested:[/yellow]")
                for func in response['function_calls']:
                    console.print(f"  • {func.name}({func.arguments})")
            else:
                console.print(Panel(str(response), title="Response", border_style="green"))
        
        # Show usage stats
        stats = client.get_usage_stats()
        console.print(f"\n[dim]Tokens: {stats['total_tokens']} | Cost: {stats['estimated_cost']}[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)


@cli.command()
@click.argument('prompt')
@click.option('--show-reasoning', '-r', is_flag=True, help='Show reasoning steps')
async def reason(prompt: str, show_reasoning: bool):
    """Use the reasoning model for complex tasks"""
    config = get_config()
    client = DeepSeekClient(config)
    
    try:
        with console.status("[yellow]Reasoning...[/yellow]"):
            result = await client.reasoning_chat(prompt)
        
        if show_reasoning and 'reasoning' in result:
            console.print(Panel("Reasoning Process", style="yellow"))
            for i, step in enumerate(result['reasoning'], 1):
                console.print(f"{i}. {step}")
            console.print()
        
        console.print(Panel(result['answer'], title="Answer", border_style="green"))
        
        # Show usage stats
        stats = client.get_usage_stats()
        console.print(f"\n[dim]Tokens: {stats['total_tokens']} | Cost: {stats['estimated_cost']}[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)


@cli.group()
def memory():
    """Memory management commands"""
    pass


@memory.command('store')
@click.argument('key')
@click.argument('value')
@click.option('--namespace', '-n', default='default', help='Memory namespace')
async def memory_store(key: str, value: str, namespace: str):
    """Store a value in memory"""
    config = get_config()
    memory = MemoryManager(config.memory_db_path)
    
    try:
        await memory.store(key, value, namespace)
        console.print(f"[green]✓ Stored '{key}' in namespace '{namespace}'[/green]")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)


@memory.command('recall')
@click.argument('key')
@click.option('--namespace', '-n', default='default', help='Memory namespace')
async def memory_recall(key: str, namespace: str):
    """Recall a value from memory"""
    config = get_config()
    memory = MemoryManager(config.memory_db_path)
    
    try:
        value = await memory.recall(key, namespace)
        if value:
            console.print(Panel(str(value), title=f"Memory: {key}", border_style="green"))
        else:
            console.print(f"[yellow]No memory found for key '{key}' in namespace '{namespace}'[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)


@memory.command('search')
@click.argument('query')
@click.option('--namespace', '-n', help='Memory namespace')
@click.option('--limit', '-l', default=10, help='Maximum results')
async def memory_search(query: str, namespace: Optional[str], limit: int):
    """Search memories"""
    config = get_config()
    memory = MemoryManager(config.memory_db_path)
    
    try:
        results = await memory.search(query, namespace, limit)
        
        if results:
            table = Table(title=f"Search Results for '{query}'")
            table.add_column("Key", style="cyan")
            table.add_column("Value", style="white")
            table.add_column("Namespace", style="yellow")
            table.add_column("Updated", style="dim")
            
            for r in results:
                value_str = str(r['value'])[:50] + "..." if len(str(r['value'])) > 50 else str(r['value'])
                table.add_row(r['key'], value_str, r['namespace'], r['updated_at'])
            
            console.print(table)
        else:
            console.print(f"[yellow]No memories found matching '{query}'[/yellow]")
            
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)


@memory.command('stats')
async def memory_stats():
    """Show memory statistics"""
    config = get_config()
    memory = MemoryManager(config.memory_db_path)
    
    try:
        stats = await memory.get_stats()
        
        # Overview
        console.print(Panel(f"Total Memories: {stats['total_memories']}", title="Memory Statistics", border_style="blue"))
        
        # Namespaces
        if stats['namespaces']:
            table = Table(title="Namespaces")
            table.add_column("Namespace", style="cyan")
            table.add_column("Count", style="white")
            
            for ns, count in stats['namespaces'].items():
                table.add_row(ns, str(count))
            
            console.print(table)
        
        # Most accessed
        if stats['most_accessed']:
            console.print("\n[yellow]Most Accessed:[/yellow]")
            for item in stats['most_accessed']:
                console.print(f"  • {item['key']} ({item['namespace']}): {item['count']} accesses")
        
        # Recent updates
        if stats['recent_updates']:
            console.print("\n[yellow]Recent Updates:[/yellow]")
            for item in stats['recent_updates']:
                console.print(f"  • {item['key']} ({item['namespace']}): {item['updated']}")
                
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)


@cli.command()
def config():
    """Show current configuration"""
    config = get_config()
    
    table = Table(title="DeepCLI Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="white")
    
    table.add_row("API Key", f"{'*' * 20}...{config.api_key[-4:]}" if config.api_key else "Not set")
    table.add_row("Default Model", config.default_model.value)
    table.add_row("Temperature", str(config.temperature))
    table.add_row("Max Tokens", str(config.max_tokens))
    table.add_row("Memory DB", str(config.memory_db_path))
    table.add_row("MCP Enabled", "Yes" if config.mcp_enabled else "No")
    table.add_row("GitHub Token", "Set" if config.github_token else "Not set")
    
    console.print(table)


@cli.command()
def version():
    """Show version information"""
    from . import __version__
    
    console.print(Panel(
        f"DeepCLI v{__version__}\n\n"
        "A powerful AI-powered CLI for DeepSeek models\n"
        "https://github.com/yourusername/deep-cli",
        title="About DeepCLI",
        border_style="blue"
    ))


async def interactive_mode():
    """Launch interactive mode"""
    console.print(Panel(
        "Welcome to [bold cyan]DeepCLI[/bold cyan] Interactive Mode!\n\n"
        "Type your messages or use commands:\n"
        "  • /help - Show available commands\n"
        "  • /exit - Exit the application\n"
        "  • /clear - Clear the screen\n",
        title="DeepCLI v2.0.0",
        border_style="blue"
    ))
    
    # Register commands
    command_registry.register(ImplementCommand())
    
    # Create and run interactive CLI
    interactive_cli = InteractiveCLI()
    await interactive_cli.run()


def main():
    """Main entry point"""
    cli()


if __name__ == "__main__":
    main()