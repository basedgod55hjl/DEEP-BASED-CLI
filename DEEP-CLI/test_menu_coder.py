#!/usr/bin/env python3
"""
Test script for the new menu system and coder agent
"""

import sys
import os
import asyncio

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from deepcli.ui.menu import MenuSystem
from deepcli.agents.coder import CoderAgent, CodeExecutor
from deepcli.core.client import DeepSeekClient
from deepcli.core.config import get_config
from deepcli.memory.manager import MemoryManager
from rich.console import Console
from rich.panel import Panel

console = Console()


async def test_menu():
    """Test the menu system"""
    console.print("\n[bold cyan]Testing Menu System[/bold cyan]\n")
    
    menu = MenuSystem(console)
    menu.display_menu("main")
    
    console.print("\n[green]✓ Menu displayed successfully![/green]")
    console.print("[dim]Note: In real usage, the menu would be interactive[/dim]")


async def test_code_executor():
    """Test the code executor"""
    console.print("\n[bold cyan]Testing Code Executor[/bold cyan]\n")
    
    executor = CodeExecutor(console)
    
    # Test Python code
    python_code = """
print("Hello from BASED GOD CODER CLI!")
for i in range(1, 4):
    print(f"Count: {i}")
"""
    
    console.print("[yellow]Testing Python execution:[/yellow]")
    success, stdout, stderr = executor.execute_code(python_code, "python")
    
    if success:
        console.print(Panel(stdout, title="✅ Python Output", border_style="green"))
    else:
        console.print(Panel(stderr, title="❌ Error", border_style="red"))
    
    # Test JavaScript code
    js_code = """
console.log("Hello from JavaScript!");
const numbers = [1, 2, 3];
numbers.forEach(n => console.log(`Number: ${n}`));
"""
    
    console.print("\n[yellow]Testing JavaScript execution:[/yellow]")
    success, stdout, stderr = executor.execute_code(js_code, "javascript")
    
    if success:
        console.print(Panel(stdout, title="✅ JavaScript Output", border_style="green"))
    else:
        console.print(Panel(stderr, title="❌ Error", border_style="red"))


async def test_coder_agent_demo():
    """Demo the coder agent capabilities"""
    console.print("\n[bold cyan]Coder Agent Demo[/bold cyan]\n")
    
    config = get_config()
    client = DeepSeekClient(config)
    memory = MemoryManager(config.memory_db_path)
    
    agent = CoderAgent(client, memory, console)
    
    # Simulate some coder agent features
    console.print(Panel(
        "[bold cyan]🧑‍💻 Coder Agent Features[/bold cyan]\n\n"
        "The Coder Agent can:\n"
        "• Generate code from natural language\n"
        "• Debug and fix errors\n"
        "• Execute code safely\n"
        "• Explain complex concepts\n"
        "• Convert between languages\n"
        "• Generate tests and documentation\n\n"
        "Example request: 'Create a Python function to calculate fibonacci numbers'",
        border_style="green"
    ))
    
    # Demo code generation
    console.print("\n[yellow]Example: Generating Fibonacci function...[/yellow]")
    
    # Simulated response
    generated_code = """def fibonacci(n):
    \"\"\"Calculate the nth Fibonacci number\"\"\"
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b

# Test the function
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")"""
    
    from rich.syntax import Syntax
    syntax = Syntax(generated_code, "python", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title="Generated Code", border_style="green"))
    
    # Execute the generated code
    console.print("\n[yellow]Executing generated code...[/yellow]")
    executor = CodeExecutor(console)
    success, stdout, stderr = executor.execute_code(generated_code, "python")
    
    if success:
        console.print(Panel(stdout, title="✅ Execution Result", border_style="green"))


async def main():
    """Main test function"""
    console.print(Panel(
        "[bold red]BASED GOD CODER CLI[/bold red]\n"
        "[dim]Test Suite[/dim]",
        border_style="blue"
    ))
    
    # Test menu
    await test_menu()
    
    # Test code executor
    await test_code_executor()
    
    # Demo coder agent
    await test_coder_agent_demo()
    
    console.print("\n[bold green]✅ All tests completed![/bold green]")
    console.print("\nTo run the full CLI: [cyan]python3 src/deepcli/main.py[/cyan]")


if __name__ == "__main__":
    asyncio.run(main())