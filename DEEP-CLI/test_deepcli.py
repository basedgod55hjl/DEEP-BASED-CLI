#!/usr/bin/env python3
"""
Test script for DeepCLI
"""

import sys
import os
import asyncio

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from deepcli.core.client import DeepSeekClient
from deepcli.core.config import DeepCLIConfig, get_config
from deepcli.core.models import DeepSeekModel, Message
from deepcli.memory.manager import MemoryManager
from rich.console import Console

console = Console()


async def test_basic_functionality():
    """Test basic DeepCLI functionality"""
    
    console.print("[bold cyan]Testing DeepCLI Basic Functionality[/bold cyan]\n")
    
    # Test 1: Configuration
    console.print("[yellow]1. Testing Configuration...[/yellow]")
    try:
        config = get_config()
        console.print(f"   ✓ API Key: {'*' * 20}...{config.api_key[-4:]}")
        console.print(f"   ✓ Default Model: {config.default_model.value}")
        console.print(f"   ✓ Base URL: {config.base_url}")
        console.print("[green]   Configuration test passed![/green]\n")
    except Exception as e:
        console.print(f"[red]   ✗ Configuration test failed: {e}[/red]\n")
        return
    
    # Test 2: Client Initialization
    console.print("[yellow]2. Testing Client Initialization...[/yellow]")
    try:
        client = DeepSeekClient(config)
        console.print("   ✓ Client initialized successfully")
        console.print("[green]   Client test passed![/green]\n")
    except Exception as e:
        console.print(f"[red]   ✗ Client test failed: {e}[/red]\n")
        return
    
    # Test 3: Memory System
    console.print("[yellow]3. Testing Memory System...[/yellow]")
    try:
        memory = MemoryManager(config.memory_db_path)
        
        # Store a test value
        await memory.store("test_key", "test_value", namespace="test")
        console.print("   ✓ Memory store successful")
        
        # Recall the value
        value = await memory.recall("test_key", namespace="test")
        assert value == "test_value", f"Expected 'test_value', got '{value}'"
        console.print("   ✓ Memory recall successful")
        
        # Search
        results = await memory.search("test", namespace="test")
        assert len(results) > 0, "No search results found"
        console.print("   ✓ Memory search successful")
        
        # Cleanup
        await memory.forget("test_key", namespace="test")
        console.print("[green]   Memory test passed![/green]\n")
    except Exception as e:
        console.print(f"[red]   ✗ Memory test failed: {e}[/red]\n")
    
    # Test 4: Simple Chat (non-streaming)
    console.print("[yellow]4. Testing Simple Chat...[/yellow]")
    try:
        response = await client.chat("Say 'Hello, DeepCLI is working!' and nothing else.")
        console.print(f"   Response: {response}")
        console.print("[green]   Chat test passed![/green]\n")
        
        # Show usage stats
        stats = client.get_usage_stats()
        console.print("[dim]Usage Stats:[/dim]")
        console.print(f"   Tokens: {stats['total_tokens']}")
        console.print(f"   Cost: {stats['estimated_cost']}")
        console.print(f"   Cache Hit Rate: {stats['cache_hit_rate']}\n")
        
    except Exception as e:
        console.print(f"[red]   ✗ Chat test failed: {e}[/red]\n")
    
    # Test 5: Streaming Chat
    console.print("[yellow]5. Testing Streaming Chat...[/yellow]")
    try:
        console.print("   Streaming response: ", end="")
        async for chunk in await client.chat("Count from 1 to 5", stream=True):
            console.print(chunk, end="")
        console.print("\n[green]   Streaming test passed![/green]\n")
    except Exception as e:
        console.print(f"[red]   ✗ Streaming test failed: {e}[/red]\n")
    
    console.print("[bold green]All tests completed![/bold green]")


async def test_command_system():
    """Test the command system"""
    from deepcli.commands.base import command_registry
    from deepcli.commands.implement import ImplementCommand
    from deepcli.core.models import CommandContext
    
    console.print("\n[bold cyan]Testing Command System[/bold cyan]\n")
    
    # Register command
    command_registry.register(ImplementCommand())
    
    # Test command parsing
    console.print("[yellow]Testing command parsing...[/yellow]")
    cmd_name, args = command_registry.parse_command("/deep:implement test feature")
    console.print(f"   Command: {cmd_name}")
    console.print(f"   Args: {args}")
    
    # Test command execution
    context = CommandContext(
        command_type=None,
        args=["test", "feature"],
        cwd=os.getcwd()
    )
    
    result = await command_registry.execute("/deep:implement test feature", context)
    console.print(f"\n[green]Command Result:[/green]\n{result}\n")


async def main():
    """Main test function"""
    console.print("\n" + "="*60)
    console.print("[bold magenta]DeepCLI Test Suite[/bold magenta]")
    console.print("="*60 + "\n")
    
    # Run basic tests
    await test_basic_functionality()
    
    # Run command system tests
    await test_command_system()
    
    console.print("\n" + "="*60)
    console.print("[bold green]Testing Complete![/bold green]")
    console.print("="*60 + "\n")


if __name__ == "__main__":
    # Run the tests
    asyncio.run(main())