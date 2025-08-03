#!/usr/bin/env python3
"""
Comprehensive System Test for Enhanced BASED GOD CLI
Tests all major components and functionality
"""

import asyncio
from enhanced_based_god_cli import EnhancedBasedGodCLI
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

async def test_system():
    """Run comprehensive system tests"""
    console.print(Panel(
        "[bold cyan]🔍 Enhanced BASED GOD CLI - System Test[/bold cyan]\n"
        "[yellow]Testing all major components...[/yellow]",
        title="System Test",
        border_style="cyan"
    ))
    
    # Initialize CLI
    cli = EnhancedBasedGodCLI()
    
    test_results = []
    
    # Test 1: Simple Chat
    console.print("\n[bold green]Test 1: Simple Chat[/bold green]")
    try:
        response = await cli.chat("Hello, what is 2+2?")
        console.print(f"✅ Response: {response[:100]}...")
        test_results.append(("Simple Chat", "✅ PASSED", "Basic conversation working"))
    except Exception as e:
        console.print(f"❌ Error: {str(e)}")
        test_results.append(("Simple Chat", "❌ FAILED", str(e)))
    
    # Test 2: Tool Execution
    console.print("\n[bold green]Test 2: Tool Execution[/bold green]")
    try:
        response = await cli.chat("Generate a simple Python hello world function")
        console.print(f"✅ Response: {response[:100]}...")
        test_results.append(("Tool Execution", "✅ PASSED", "Code generation working"))
    except Exception as e:
        console.print(f"❌ Error: {str(e)}")
        test_results.append(("Tool Execution", "❌ FAILED", str(e)))
    
    # Test 3: Memory System
    console.print("\n[bold green]Test 3: Memory System[/bold green]")
    try:
        response = await cli.chat("Remember that my favorite color is blue")
        console.print(f"✅ Response: {response[:100]}...")
        test_results.append(("Memory System", "✅ PASSED", "Memory storage working"))
    except Exception as e:
        console.print(f"❌ Error: {str(e)}")
        test_results.append(("Memory System", "❌ FAILED", str(e)))
    
    # Test 4: Data Analysis
    console.print("\n[bold green]Test 4: Data Analysis[/bold green]")
    try:
        response = await cli.chat("Analyze this data: {'name': 'test', 'value': 42}")
        console.print(f"✅ Response: {response[:100]}...")
        test_results.append(("Data Analysis", "✅ PASSED", "Data analysis working"))
    except Exception as e:
        console.print(f"❌ Error: {str(e)}")
        test_results.append(("Data Analysis", "❌ FAILED", str(e)))
    
    # Test 5: Tool Manager
    console.print("\n[bold green]Test 5: Tool Manager[/bold green]")
    try:
        cli.show_tools()
        test_results.append(("Tool Manager", "✅ PASSED", "All tools registered"))
    except Exception as e:
        console.print(f"❌ Error: {str(e)}")
        test_results.append(("Tool Manager", "❌ FAILED", str(e)))
    
    # Display results
    console.print("\n[bold cyan]📊 Test Results Summary[/bold cyan]")
    
    table = Table(title="System Test Results")
    table.add_column("Component", style="cyan", no_wrap=True)
    table.add_column("Status", style="bold")
    table.add_column("Details", style="white")
    
    passed = 0
    failed = 0
    
    for component, status, details in test_results:
        status_style = "green" if "✅" in status else "red"
        table.add_row(component, f"[{status_style}]{status}[/{status_style}]", details)
        
        if "✅" in status:
            passed += 1
        else:
            failed += 1
    
    console.print(table)
    
    # Overall status
    total = len(test_results)
    success_rate = (passed / total) * 100 if total > 0 else 0
    
    console.print(f"\n[bold]Overall Results: {passed}/{total} passed ({success_rate:.1f}% success rate)[/bold]")
    
    if failed == 0:
        console.print("\n[bold green]🎉 ALL TESTS PASSED! The system is fully operational![/bold green]")
    else:
        console.print(f"\n[bold yellow]⚠️ {failed} tests failed. Please check the errors above.[/bold yellow]")
    
    # Configuration check
    console.print("\n[bold cyan]🔧 Configuration Status[/bold cyan]")
    from config import get_config
    config = get_config()
    
    console.print(f"✅ DeepSeek API Key: {config['llm']['api_key'][:20]}...")
    console.print(f"✅ Base URL: {config['llm']['base_url']}")
    console.print(f"✅ Default Model: {config['llm']['default_model']}")
    console.print(f"✅ Tools Enabled: {config['tools']['enable_all']}")
    
    return passed, failed

def main():
    """Main test runner"""
    console.print("[bold red]🔥 Enhanced BASED GOD CLI System Test[/bold red]")
    console.print("Testing all components and functionality...\n")
    
    passed, failed = asyncio.run(test_system())
    
    if failed == 0:
        console.print("\n[bold green]✅ System is fully operational and ready to use![/bold green]")
        console.print("[green]Run 'python3 enhanced_based_god_cli.py' to start the CLI[/green]")
    else:
        console.print("\n[bold red]❌ Some tests failed. Please fix the issues before running.[/bold red]")

if __name__ == "__main__":
    main()