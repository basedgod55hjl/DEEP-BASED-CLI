#!/usr/bin/env python3
"""
DeepCLI Demo Script
Showcases the main features of the refactored DeepCLI
"""

import sys
import os
import asyncio

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from deepcli.core.client import DeepSeekClient
from deepcli.core.config import get_config
from deepcli.core.models import DeepSeekModel
from deepcli.memory.manager import MemoryManager
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


async def demo():
    """Run the demo"""
    console.print(Panel.fit(
        "[bold cyan]DeepCLI v2.0 Demo[/bold cyan]\n"
        "Showcasing the refactored architecture",
        border_style="blue"
    ))
    
    # Initialize components
    config = get_config()
    client = DeepSeekClient(config)
    memory = MemoryManager(config.memory_db_path)
    
    # Demo 1: Basic Chat
    console.print("\n[bold yellow]1. Basic Chat Example[/bold yellow]")
    response = await client.chat("What is DeepCLI? Answer in one sentence.")
    console.print(f"Response: {response}\n")
    
    # Demo 2: Memory System
    console.print("[bold yellow]2. Memory System Demo[/bold yellow]")
    
    # Store some project context
    await memory.store("project_type", "Python CLI Tool", namespace="demo")
    await memory.store("main_feature", "AI-powered command line interface", namespace="demo")
    await memory.store("version", "2.0.0", namespace="demo")
    
    # Search memories
    results = await memory.search("", namespace="demo")
    
    table = Table(title="Stored Memories")
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="white")
    
    for result in results:
        table.add_row(result['key'], str(result['value']))
    
    console.print(table)
    
    # Demo 3: Streaming Response
    console.print("\n[bold yellow]3. Streaming Response Demo[/bold yellow]")
    console.print("Streaming: ", end="")
    
    async for chunk in await client.chat(
        "List 3 key features of a good CLI tool",
        stream=True
    ):
        console.print(chunk, end="")
    console.print("\n")
    
    # Demo 4: Usage Statistics
    console.print("[bold yellow]4. Usage Statistics[/bold yellow]")
    stats = client.get_usage_stats()
    
    stats_table = Table(title="API Usage")
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Value", style="white")
    
    for key, value in stats.items():
        stats_table.add_row(key.replace('_', ' ').title(), str(value))
    
    console.print(stats_table)
    
    # Demo 5: Command System Preview
    console.print("\n[bold yellow]5. Command System Preview[/bold yellow]")
    console.print("Available slash commands in interactive mode:")
    console.print("  • /deep:implement - Implement features with AI personas")
    console.print("  • /deep:analyze - Analyze code or systems")
    console.print("  • /deep:design - Design architectures")
    console.print("  • /memory - Manage persistent memories")
    console.print("  • /help - Show all available commands")
    
    console.print("\n[bold green]✅ Demo Complete![/bold green]")
    console.print("\nTo start interactive mode, run: [cyan]python -m deepcli[/cyan]")


if __name__ == "__main__":
    asyncio.run(demo())