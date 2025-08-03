#!/usr/bin/env python3
"""
Test the interactive CLI features
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Test that we can run the main CLI
from deepcli.main import cli, console


def test_cli_help():
    """Test CLI help command"""
    console.print("\n[bold cyan]Testing CLI Help Command[/bold cyan]\n")
    
    # We'll test the CLI by importing and calling functions directly
    # since we can't easily test interactive mode in this environment
    
    from click.testing import CliRunner
    
    runner = CliRunner()
    
    # Test help
    result = runner.invoke(cli, ['--help'])
    console.print("[yellow]Help Output:[/yellow]")
    console.print(result.output)
    
    # Test version
    result = runner.invoke(cli, ['version'])
    console.print("\n[yellow]Version Output:[/yellow]")
    console.print(result.output)
    
    # Test config
    result = runner.invoke(cli, ['config'])
    console.print("\n[yellow]Config Output:[/yellow]")
    console.print(result.output)


if __name__ == "__main__":
    test_cli_help()