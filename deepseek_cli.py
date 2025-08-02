#!/usr/bin/env python3
"""
DeepSeek CLI - A comprehensive command-line interface for DeepSeek API

Features:
- Beautiful interactive menu with colors
- Both chat and reasoning models
- Streaming support
- Function calling
- File operations
- Batch processing
- Usage tracking
- Export functionality
"""

import os
import sys
import json
import time
import asyncio
import readline
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path
import argparse
from enum import Enum

# For colored output
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.markdown import Markdown
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import Prompt, Confirm
    from rich.live import Live
    from rich.layout import Layout
    from rich.text import Text
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Warning: 'rich' library not available. Install with: pip install rich")
    print("Falling back to basic output.\n")

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from deepseek_integration import (
        DeepSeekClient, 
        DeepSeekModel, 
        ResponseFormat,
        DeepSeekConfig,
        DeepSeekError,
        RateLimitError
    )
except ImportError:
    print("Error: deepseek_integration module not found!")
    print("Make sure deepseek_integration.py is in the same directory as this script.")
    sys.exit(1)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()


class MenuOption(Enum):
    """Menu options for the CLI"""
    CHAT = "1"
    REASON = "2"
    CODE_GEN = "3"
    FILE_ANALYZE = "4"
    BATCH_PROCESS = "5"
    FUNCTION_CALL = "6"
    USAGE_STATS = "7"
    SETTINGS = "8"
    HELP = "9"
    EXIT = "0"


class DeepSeekCLI:
    """Main CLI application for DeepSeek"""
    
    def __init__(self):
        """Initialize the CLI"""
        # Initialize console first
        self.console = Console() if RICH_AVAILABLE else None
        
        # Check for API key
        if not os.getenv("DEEPSEEK_API_KEY"):
            self._setup_api_key()
        
        # Initialize client
        try:
            self.client = DeepSeekClient()
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error initializing DeepSeek client: {e}[/red]")
            else:
                print(f"Error initializing DeepSeek client: {e}")
            sys.exit(1)
        
        # Settings
        self.settings = {
            "model": DeepSeekModel.CHAT,
            "temperature": 0.7,
            "max_tokens": None,
            "stream": True,
            "save_history": True,
            "export_format": "txt"
        }
        
        # Conversation history
        self.conversation_history = []
        self.current_session_file = None
        
        # File analysis cache
        self.analyzed_files = {}
        
    def _setup_api_key(self):
        """Interactive API key setup"""
        if self.console and RICH_AVAILABLE:
            self.console.print("\n[yellow]DeepSeek API key not found![/yellow]")
            self.console.print("Please visit [link]https://platform.deepseek.com/api_keys[/link] to get your API key.\n")
            
            api_key = Prompt.ask("Enter your DeepSeek API key", password=True)
            
            if Confirm.ask("Save API key to .env file?"):
                with open(".env", "a") as f:
                    f.write(f"\nDEEPSEEK_API_KEY={api_key}\n")
                self.console.print("[green]✓ API key saved to .env file[/green]")
            
            os.environ["DEEPSEEK_API_KEY"] = api_key
        else:
            print("\nDeepSeek API key not found!")
            print("Please visit https://platform.deepseek.com/api_keys to get your API key.\n")
            
            api_key = input("Enter your DeepSeek API key: ")
            
            save = input("Save API key to .env file? (y/n): ").lower() == 'y'
            if save:
                with open(".env", "a") as f:
                    f.write(f"\nDEEPSEEK_API_KEY={api_key}\n")
                print("✓ API key saved to .env file")
            
            os.environ["DEEPSEEK_API_KEY"] = api_key
    
    def _print_header(self):
        """Print the CLI header"""
        if self.console and RICH_AVAILABLE:
            header = Panel(
                "[bold cyan]DeepSeek CLI[/bold cyan]\n"
                "[dim]AI-powered command-line assistant[/dim]",
                box=box.DOUBLE,
                expand=False,
                padding=(1, 2)
            )
            self.console.print(header)
        else:
            print("\n" + "="*50)
            print("DeepSeek CLI")
            print("AI-powered command-line assistant")
            print("="*50 + "\n")
    
    def _print_menu(self):
        """Print the main menu"""
        if self.console and RICH_AVAILABLE:
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
                ("7", "Usage Stats", "View token usage and costs"),
                ("8", "Settings", "Configure CLI preferences"),
                ("9", "Help", "Show help and examples"),
                ("0", "Exit", "Exit the application")
            ]
            
            for option, feature, desc in menu_items:
                table.add_row(option, feature, desc)
            
            self.console.print(table)
        else:
            print("\nMain Menu:")
            print("1. Chat Mode - Interactive conversation with AI")
            print("2. Reasoning Mode - Complex problem solving")
            print("3. Code Generation - Generate code with explanations")
            print("4. File Analysis - Analyze and process files")
            print("5. Batch Processing - Process multiple prompts")
            print("6. Function Calling - Demonstrate function calling")
            print("7. Usage Stats - View token usage and costs")
            print("8. Settings - Configure CLI preferences")
            print("9. Help - Show help and examples")
            print("0. Exit - Exit the application")
            print()
    
    def _chat_mode(self):
        """Interactive chat mode"""
        self._print_section_header("Chat Mode")
        
        if self.console and RICH_AVAILABLE:
            self.console.print("[dim]Type 'exit' to return to main menu[/dim]")
            self.console.print("[dim]Type 'clear' to clear conversation history[/dim]\n")
        else:
            print("Type 'exit' to return to main menu")
            print("Type 'clear' to clear conversation history\n")
        
        while True:
            # Get user input
            try:
                if self.console and RICH_AVAILABLE:
                    user_input = Prompt.ask("[bold green]You[/bold green]")
                else:
                    user_input = input("You: ")
            except (KeyboardInterrupt, EOFError):
                break
            
            if user_input.lower() in ['exit', 'quit']:
                break
            elif user_input.lower() == 'clear':
                self.conversation_history.clear()
                self._print_success("Conversation history cleared")
                continue
            elif not user_input.strip():
                continue
            
            # Add to history
            self.conversation_history.append({"role": "user", "content": user_input})
            
            # Get response
            try:
                if self.settings["stream"]:
                    self._stream_response(user_input)
                else:
                    response = self.client.chat(
                        self.conversation_history[-10:],  # Last 10 messages for context
                        model=self.settings["model"],
                        temperature=self.settings["temperature"],
                        max_tokens=self.settings["max_tokens"]
                    )
                    self.conversation_history.append({"role": "assistant", "content": response})
                    self._print_ai_response(response)
                    
            except Exception as e:
                self._print_error(f"Error: {str(e)}")
    
    def _stream_response(self, prompt: str):
        """Stream response with live update"""
        if self.console and RICH_AVAILABLE:
            self.console.print("\n[bold blue]AI:[/bold blue]", end=" ")
            
            full_response = ""
            try:
                for chunk in self.client.chat(
                    self.conversation_history[-10:] if len(self.conversation_history) > 1 else prompt,
                    model=self.settings["model"],
                    temperature=self.settings["temperature"],
                    max_tokens=self.settings["max_tokens"],
                    stream=True
                ):
                    self.console.print(chunk, end="")
                    full_response += chunk
                
                self.console.print()  # New line after response
                self.conversation_history.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                self._print_error(f"Streaming error: {str(e)}")
        else:
            # Fallback for non-rich environment
            print("\nAI: ", end="", flush=True)
            full_response = ""
            try:
                for chunk in self.client.chat(
                    self.conversation_history[-10:] if len(self.conversation_history) > 1 else prompt,
                    model=self.settings["model"],
                    temperature=self.settings["temperature"],
                    max_tokens=self.settings["max_tokens"],
                    stream=True
                ):
                    print(chunk, end="", flush=True)
                    full_response += chunk
                
                print()  # New line after response
                self.conversation_history.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                print(f"\nError: {str(e)}")
    
    def _reasoning_mode(self):
        """Reasoning mode for complex problems"""
        self._print_section_header("Reasoning Mode")
        
        if self.console and RICH_AVAILABLE:
            self.console.print("[dim]Enter a complex problem or question[/dim]\n")
            
            problem = Prompt.ask("[bold green]Problem[/bold green]")
            
            effort_level = Prompt.ask(
                "Reasoning effort",
                choices=["low", "medium", "high"],
                default="medium"
            )
            
            with self.console.status("[bold green]Thinking...[/bold green]", spinner="dots"):
                try:
                    result = self.client.reason(
                        problem,
                        reasoning_effort=effort_level,
                        show_reasoning=True
                    )
                    
                    # Display reasoning steps
                    if "reasoning" in result and result["reasoning"]:
                        reasoning_panel = Panel(
                            result["reasoning"],
                            title="[bold yellow]Reasoning Process[/bold yellow]",
                            border_style="yellow",
                            padding=(1, 2)
                        )
                        self.console.print(reasoning_panel)
                    
                    # Display answer
                    answer_panel = Panel(
                        result["answer"],
                        title="[bold green]Answer[/bold green]",
                        border_style="green",
                        padding=(1, 2)
                    )
                    self.console.print(answer_panel)
                    
                except Exception as e:
                    self._print_error(f"Error: {str(e)}")
        else:
            # Fallback for non-rich environment
            print("Enter a complex problem or question\n")
            problem = input("Problem: ")
            
            print("\nReasoning effort (low/medium/high): ", end="")
            effort_level = input() or "medium"
            
            print("\nThinking...", end="", flush=True)
            try:
                result = self.client.reason(
                    problem,
                    reasoning_effort=effort_level,
                    show_reasoning=True
                )
                
                print("\r" + " "*20 + "\r", end="")  # Clear "Thinking..."
                
                if "reasoning" in result and result["reasoning"]:
                    print("\n--- Reasoning Process ---")
                    print(result["reasoning"])
                    print("------------------------\n")
                
                print("--- Answer ---")
                print(result["answer"])
                print("--------------")
                
            except Exception as e:
                print(f"\nError: {str(e)}")
    
    def _code_generation_mode(self):
        """Code generation mode"""
        self._print_section_header("Code Generation")
        
        if self.console and RICH_AVAILABLE:
            self.console.print("[dim]Describe what code you need[/dim]\n")
            
            request = Prompt.ask("[bold green]Code request[/bold green]")
            
            language = Prompt.ask(
                "Programming language",
                default="python"
            )
            
            with self.console.status("[bold green]Generating code...[/bold green]", spinner="dots"):
                try:
                    prompt = f"""Generate {language} code for: {request}
                    
Requirements:
- Include detailed comments
- Add error handling
- Follow best practices
- Include example usage"""
                    
                    response = self.client.chat(
                        prompt,
                        model=DeepSeekModel.CHAT,
                        temperature=0.2,  # Lower temperature for code
                        system_prompt="You are an expert programmer. Generate clean, well-documented code."
                    )
                    
                    # Display code with syntax highlighting
                    syntax = Syntax(
                        response,
                        language,
                        theme="monokai",
                        line_numbers=True
                    )
                    
                    code_panel = Panel(
                        syntax,
                        title=f"[bold cyan]{language.title()} Code[/bold cyan]",
                        border_style="cyan",
                        padding=(1, 1)
                    )
                    self.console.print(code_panel)
                    
                    # Ask if user wants to save
                    if Confirm.ask("\nSave code to file?"):
                        filename = Prompt.ask("Filename", default=f"generated_code.{self._get_extension(language)}")
                        with open(filename, 'w') as f:
                            f.write(response)
                        self._print_success(f"Code saved to {filename}")
                        
                except Exception as e:
                    self._print_error(f"Error: {str(e)}")
        else:
            # Fallback for non-rich environment
            print("Describe what code you need\n")
            request = input("Code request: ")
            language = input("Programming language (default: python): ") or "python"
            
            print("\nGenerating code...", end="", flush=True)
            try:
                prompt = f"""Generate {language} code for: {request}
                
Requirements:
- Include detailed comments
- Add error handling
- Follow best practices
- Include example usage"""
                
                response = self.client.chat(
                    prompt,
                    model=DeepSeekModel.CHAT,
                    temperature=0.2,
                    system_prompt="You are an expert programmer. Generate clean, well-documented code."
                )
                
                print("\r" + " "*20 + "\r", end="")  # Clear "Generating..."
                
                print(f"\n--- {language.title()} Code ---")
                print(response)
                print("-------------------")
                
                save = input("\nSave code to file? (y/n): ").lower() == 'y'
                if save:
                    filename = input(f"Filename (default: generated_code.{self._get_extension(language)}): ")
                    if not filename:
                        filename = f"generated_code.{self._get_extension(language)}"
                    
                    with open(filename, 'w') as f:
                        f.write(response)
                    print(f"✓ Code saved to {filename}")
                    
            except Exception as e:
                print(f"\nError: {str(e)}")
    
    def _file_analysis_mode(self):
        """File analysis mode"""
        self._print_section_header("File Analysis")
        
        if self.console and RICH_AVAILABLE:
            self.console.print("[dim]Analyze files with AI[/dim]\n")
            
            filepath = Prompt.ask("[bold green]File path[/bold green]")
            
            if not os.path.exists(filepath):
                self._print_error(f"File not found: {filepath}")
                return
            
            # Read file
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                file_info = {
                    "name": os.path.basename(filepath),
                    "size": os.path.getsize(filepath),
                    "lines": len(content.splitlines())
                }
                
                # Show file info
                info_table = Table(title="File Information", box=box.MINIMAL)
                info_table.add_column("Property", style="cyan")
                info_table.add_column("Value", style="white")
                
                info_table.add_row("Filename", file_info["name"])
                info_table.add_row("Size", f"{file_info['size']:,} bytes")
                info_table.add_row("Lines", str(file_info["lines"]))
                
                self.console.print(info_table)
                
                # Ask what to do
                action = Prompt.ask(
                    "\nWhat would you like to do?",
                    choices=["summarize", "analyze", "improve", "explain", "custom"],
                    default="analyze"
                )
                
                if action == "custom":
                    custom_prompt = Prompt.ask("Enter your custom request")
                    prompt = f"File content:\n\n{content}\n\nRequest: {custom_prompt}"
                else:
                    prompts = {
                        "summarize": f"Summarize this file:\n\n{content}",
                        "analyze": f"Analyze this file and provide insights:\n\n{content}",
                        "improve": f"Suggest improvements for this file:\n\n{content}",
                        "explain": f"Explain what this file does:\n\n{content}"
                    }
                    prompt = prompts[action]
                
                with self.console.status(f"[bold green]{action.title()}ing file...[/bold green]", spinner="dots"):
                    response = self.client.chat(
                        prompt,
                        model=self.settings["model"],
                        temperature=0.5
                    )
                
                # Display response
                result_panel = Panel(
                    Markdown(response),
                    title=f"[bold cyan]{action.title()} Results[/bold cyan]",
                    border_style="cyan",
                    padding=(1, 2)
                )
                self.console.print(result_panel)
                
                # Save analysis
                if Confirm.ask("\nSave analysis to file?"):
                    output_file = Prompt.ask("Output filename", default=f"{file_info['name']}_analysis.md")
                    with open(output_file, 'w') as f:
                        f.write(f"# {action.title()} of {file_info['name']}\n\n")
                        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                        f.write(response)
                    self._print_success(f"Analysis saved to {output_file}")
                    
            except Exception as e:
                self._print_error(f"Error: {str(e)}")
        else:
            # Fallback implementation
            print("Analyze files with AI\n")
            filepath = input("File path: ")
            
            if not os.path.exists(filepath):
                print(f"Error: File not found: {filepath}")
                return
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                print(f"\nFile: {os.path.basename(filepath)}")
                print(f"Size: {os.path.getsize(filepath):,} bytes")
                print(f"Lines: {len(content.splitlines())}")
                
                print("\nWhat would you like to do?")
                print("1. Summarize")
                print("2. Analyze")
                print("3. Improve")
                print("4. Explain")
                print("5. Custom request")
                
                choice = input("\nChoice (1-5): ")
                
                if choice == "5":
                    custom_prompt = input("Enter your custom request: ")
                    prompt = f"File content:\n\n{content}\n\nRequest: {custom_prompt}"
                else:
                    actions = {
                        "1": ("summarize", f"Summarize this file:\n\n{content}"),
                        "2": ("analyze", f"Analyze this file and provide insights:\n\n{content}"),
                        "3": ("improve", f"Suggest improvements for this file:\n\n{content}"),
                        "4": ("explain", f"Explain what this file does:\n\n{content}")
                    }
                    action, prompt = actions.get(choice, ("analyze", f"Analyze this file:\n\n{content}"))
                
                print(f"\n{action.title()}ing file...", end="", flush=True)
                response = self.client.chat(
                    prompt,
                    model=self.settings["model"],
                    temperature=0.5
                )
                
                print("\r" + " "*20 + "\r", end="")
                print(f"\n--- {action.title()} Results ---")
                print(response)
                print("-------------------------")
                
                save = input("\nSave analysis to file? (y/n): ").lower() == 'y'
                if save:
                    output_file = input(f"Output filename (default: {os.path.basename(filepath)}_analysis.md): ")
                    if not output_file:
                        output_file = f"{os.path.basename(filepath)}_analysis.md"
                    
                    with open(output_file, 'w') as f:
                        f.write(f"# {action.title()} of {os.path.basename(filepath)}\n\n")
                        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                        f.write(response)
                    print(f"✓ Analysis saved to {output_file}")
                    
            except Exception as e:
                print(f"Error: {str(e)}")
    
    def _batch_processing_mode(self):
        """Batch processing mode"""
        self._print_section_header("Batch Processing")
        
        if self.console and RICH_AVAILABLE:
            self.console.print("[dim]Process multiple prompts at once[/dim]\n")
            
            # Get prompts
            prompts = []
            self.console.print("Enter prompts (empty line to finish):")
            
            i = 1
            while True:
                prompt = Prompt.ask(f"[bold green]Prompt {i}[/bold green]", default="")
                if not prompt:
                    break
                prompts.append(prompt)
                i += 1
            
            if not prompts:
                self._print_warning("No prompts entered")
                return
            
            # Confirm processing
            self.console.print(f"\n[cyan]Ready to process {len(prompts)} prompts[/cyan]")
            
            if not Confirm.ask("Continue?"):
                return
            
            # Process with progress bar
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True
            ) as progress:
                task = progress.add_task("Processing prompts...", total=len(prompts))
                
                try:
                    responses = []
                    for i, prompt in enumerate(prompts):
                        progress.update(task, description=f"Processing prompt {i+1}/{len(prompts)}...")
                        
                        response = self.client.chat(
                            prompt,
                            model=self.settings["model"],
                            temperature=self.settings["temperature"]
                        )
                        responses.append(response)
                        progress.advance(task)
                    
                    # Display results
                    self.console.print("\n[bold green]✓ Batch processing complete![/bold green]\n")
                    
                    for i, (prompt, response) in enumerate(zip(prompts, responses), 1):
                        result_panel = Panel(
                            f"[bold]Prompt:[/bold] {prompt}\n\n"
                            f"[bold]Response:[/bold]\n{response}",
                            title=f"Result {i}",
                            border_style="cyan",
                            padding=(1, 2)
                        )
                        self.console.print(result_panel)
                    
                    # Save results
                    if Confirm.ask("\nSave results to file?"):
                        filename = Prompt.ask("Filename", default="batch_results.json")
                        
                        results = [
                            {
                                "prompt": prompt,
                                "response": response,
                                "timestamp": datetime.now().isoformat()
                            }
                            for prompt, response in zip(prompts, responses)
                        ]
                        
                        with open(filename, 'w') as f:
                            json.dump(results, f, indent=2)
                        
                        self._print_success(f"Results saved to {filename}")
                        
                except Exception as e:
                    self._print_error(f"Error: {str(e)}")
        else:
            # Fallback implementation
            print("Process multiple prompts at once\n")
            
            prompts = []
            print("Enter prompts (empty line to finish):")
            
            i = 1
            while True:
                prompt = input(f"Prompt {i}: ")
                if not prompt:
                    break
                prompts.append(prompt)
                i += 1
            
            if not prompts:
                print("No prompts entered")
                return
            
            print(f"\nReady to process {len(prompts)} prompts")
            if input("Continue? (y/n): ").lower() != 'y':
                return
            
            print("\nProcessing...", end="", flush=True)
            
            try:
                responses = self.client.batch_chat(
                    prompts,
                    model=self.settings["model"],
                    temperature=self.settings["temperature"],
                    max_concurrent=3
                )
                
                print("\r" + " "*20 + "\r", end="")
                print("✓ Batch processing complete!\n")
                
                for i, (prompt, response) in enumerate(zip(prompts, responses), 1):
                    print(f"--- Result {i} ---")
                    print(f"Prompt: {prompt}")
                    print(f"Response: {response}")
                    print("-" * 40)
                
                save = input("\nSave results to file? (y/n): ").lower() == 'y'
                if save:
                    filename = input("Filename (default: batch_results.json): ") or "batch_results.json"
                    
                    results = [
                        {
                            "prompt": prompt,
                            "response": response,
                            "timestamp": datetime.now().isoformat()
                        }
                        for prompt, response in zip(prompts, responses)
                    ]
                    
                    with open(filename, 'w') as f:
                        json.dump(results, f, indent=2)
                    
                    print(f"✓ Results saved to {filename}")
                    
            except Exception as e:
                print(f"\nError: {str(e)}")
    
    def _function_calling_demo(self):
        """Demonstrate function calling capabilities"""
        self._print_section_header("Function Calling Demo")
        
        # Define sample functions
        functions = [
            self.client.create_function_tool(
                name="get_weather",
                description="Get the current weather in a location",
                parameters={
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The unit for temperature"
                    }
                },
                required=["location"]
            ),
            self.client.create_function_tool(
                name="search_web",
                description="Search the web for information",
                parameters={
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of results to return",
                        "default": 5
                    }
                },
                required=["query"]
            ),
            self.client.create_function_tool(
                name="calculate",
                description="Perform mathematical calculations",
                parameters={
                    "expression": {
                        "type": "string",
                        "description": "The mathematical expression to evaluate"
                    }
                },
                required=["expression"]
            )
        ]
        
        if self.console and RICH_AVAILABLE:
            self.console.print("[dim]Available functions: get_weather, search_web, calculate[/dim]\n")
            
            # Show function details
            func_table = Table(title="Available Functions", box=box.MINIMAL)
            func_table.add_column("Function", style="cyan")
            func_table.add_column("Description", style="white")
            func_table.add_column("Parameters", style="dim")
            
            for func in functions:
                name = func["function"]["name"]
                desc = func["function"]["description"]
                params = ", ".join(func["function"]["parameters"]["properties"].keys())
                func_table.add_row(name, desc, params)
            
            self.console.print(func_table)
            self.console.print()
            
            # Get user query
            query = Prompt.ask("[bold green]What would you like to know?[/bold green]")
            
            with self.console.status("[bold green]Processing...[/bold green]", spinner="dots"):
                try:
                    response = self.client.chat(
                        query,
                        tools=functions,
                        tool_choice="auto"
                    )
                    
                    # Display function calls
                    if isinstance(response, list):
                        self.console.print("\n[bold cyan]Function Calls:[/bold cyan]")
                        
                        for call in response:
                            call_panel = Panel(
                                f"[bold]Function:[/bold] {call.function.name}\n"
                                f"[bold]Arguments:[/bold] {call.function.arguments}",
                                border_style="yellow",
                                padding=(1, 2)
                            )
                            self.console.print(call_panel)
                        
                        # Simulate function execution
                        self.console.print("\n[dim]Note: In a real application, these functions would be executed[/dim]")
                        self.console.print("[dim]and their results would be passed back to the AI.[/dim]")
                    else:
                        self._print_ai_response(response)
                        
                except Exception as e:
                    self._print_error(f"Error: {str(e)}")
        else:
            # Fallback implementation
            print("Available functions: get_weather, search_web, calculate\n")
            
            print("Function Details:")
            print("- get_weather: Get current weather (params: location, unit)")
            print("- search_web: Search the web (params: query, num_results)")
            print("- calculate: Perform calculations (params: expression)")
            print()
            
            query = input("What would you like to know? ")
            
            print("\nProcessing...", end="", flush=True)
            
            try:
                response = self.client.chat(
                    query,
                    tools=functions,
                    tool_choice="auto"
                )
                
                print("\r" + " "*20 + "\r", end="")
                
                if isinstance(response, list):
                    print("\nFunction Calls:")
                    for i, call in enumerate(response, 1):
                        print(f"\n{i}. Function: {call.function.name}")
                        print(f"   Arguments: {call.function.arguments}")
                    
                    print("\nNote: In a real application, these functions would be executed")
                    print("and their results would be passed back to the AI.")
                else:
                    print(f"\nAI: {response}")
                    
            except Exception as e:
                print(f"\nError: {str(e)}")
    
    def _show_usage_stats(self):
        """Show usage statistics"""
        self._print_section_header("Usage Statistics")
        
        usage = self.client.get_usage_summary()
        
        if self.console and RICH_AVAILABLE:
            # Create usage table
            usage_table = Table(title="Token Usage", box=box.ROUNDED)
            usage_table.add_column("Metric", style="cyan")
            usage_table.add_column("Value", justify="right", style="white")
            
            usage_table.add_row("Prompt Tokens", f"{usage['usage']['prompt_tokens']:,}")
            usage_table.add_row("Completion Tokens", f"{usage['usage']['completion_tokens']:,}")
            usage_table.add_row("Total Tokens", f"{usage['usage']['total_tokens']:,}")
            usage_table.add_row("Cache Hit Tokens", f"{usage['usage']['cache_hit_tokens']:,}")
            usage_table.add_row("Cache Miss Tokens", f"{usage['usage']['cache_miss_tokens']:,}")
            
            if usage['usage']['reasoning_tokens'] > 0:
                usage_table.add_row("Reasoning Tokens", f"{usage['usage']['reasoning_tokens']:,}")
            
            self.console.print(usage_table)
            
            # Create cost table
            cost_table = Table(title="Cost Analysis", box=box.ROUNDED)
            cost_table.add_column("Type", style="cyan")
            cost_table.add_column("Amount", justify="right", style="white")
            
            cost_table.add_row("Prompt Cost", f"${usage['costs']['prompt_cost']:.4f}")
            cost_table.add_row("Completion Cost", f"${usage['costs']['completion_cost']:.4f}")
            cost_table.add_row("Total Cost", f"${usage['costs']['total_cost']:.4f}")
            cost_table.add_row("Cache Savings", f"${usage['costs']['cache_savings']:.4f}")
            
            self.console.print(cost_table)
            
            # Efficiency metrics
            eff_panel = Panel(
                f"Cache Hit Rate: [bold green]{usage['efficiency']['cache_hit_rate']}%[/bold green]",
                title="Efficiency",
                border_style="green",
                padding=(1, 2)
            )
            self.console.print(eff_panel)
            
            # Reset option
            if usage['usage']['total_tokens'] > 0:
                if Confirm.ask("\nReset usage statistics?"):
                    self.client.reset_usage()
                    self._print_success("Usage statistics reset")
        else:
            # Fallback implementation
            print("\n--- Token Usage ---")
            print(f"Prompt Tokens: {usage['usage']['prompt_tokens']:,}")
            print(f"Completion Tokens: {usage['usage']['completion_tokens']:,}")
            print(f"Total Tokens: {usage['usage']['total_tokens']:,}")
            print(f"Cache Hit Tokens: {usage['usage']['cache_hit_tokens']:,}")
            print(f"Cache Miss Tokens: {usage['usage']['cache_miss_tokens']:,}")
            
            if usage['usage']['reasoning_tokens'] > 0:
                print(f"Reasoning Tokens: {usage['usage']['reasoning_tokens']:,}")
            
            print("\n--- Cost Analysis ---")
            print(f"Prompt Cost: ${usage['costs']['prompt_cost']:.4f}")
            print(f"Completion Cost: ${usage['costs']['completion_cost']:.4f}")
            print(f"Total Cost: ${usage['costs']['total_cost']:.4f}")
            print(f"Cache Savings: ${usage['costs']['cache_savings']:.4f}")
            
            print("\n--- Efficiency ---")
            print(f"Cache Hit Rate: {usage['efficiency']['cache_hit_rate']}%")
            
            if usage['usage']['total_tokens'] > 0:
                reset = input("\nReset usage statistics? (y/n): ").lower() == 'y'
                if reset:
                    self.client.reset_usage()
                    print("✓ Usage statistics reset")
    
    def _settings_menu(self):
        """Settings configuration menu"""
        self._print_section_header("Settings")
        
        if self.console and RICH_AVAILABLE:
            while True:
                # Show current settings
                settings_table = Table(title="Current Settings", box=box.MINIMAL)
                settings_table.add_column("Setting", style="cyan")
                settings_table.add_column("Value", style="white")
                
                settings_table.add_row("Model", self.settings["model"].value)
                settings_table.add_row("Temperature", str(self.settings["temperature"]))
                settings_table.add_row("Max Tokens", str(self.settings["max_tokens"] or "Auto"))
                settings_table.add_row("Streaming", "Enabled" if self.settings["stream"] else "Disabled")
                settings_table.add_row("Save History", "Enabled" if self.settings["save_history"] else "Disabled")
                settings_table.add_row("Export Format", self.settings["export_format"])
                
                self.console.print(settings_table)
                
                # Options
                self.console.print("\n[bold]Options:[/bold]")
                self.console.print("1. Change Model")
                self.console.print("2. Adjust Temperature")
                self.console.print("3. Set Max Tokens")
                self.console.print("4. Toggle Streaming")
                self.console.print("5. Toggle History Saving")
                self.console.print("6. Change Export Format")
                self.console.print("0. Back to Main Menu")
                
                choice = Prompt.ask("\n[bold green]Choice[/bold green]", choices=["0", "1", "2", "3", "4", "5", "6"])
                
                if choice == "0":
                    break
                elif choice == "1":
                    model = Prompt.ask(
                        "Select model",
                        choices=["chat", "reasoner"],
                        default="chat"
                    )
                    self.settings["model"] = DeepSeekModel.CHAT if model == "chat" else DeepSeekModel.REASONER
                    self._print_success(f"Model changed to: {model}")
                    
                elif choice == "2":
                    temp = float(Prompt.ask("Temperature (0.0-2.0)", default="0.7"))
                    self.settings["temperature"] = max(0.0, min(2.0, temp))
                    self._print_success(f"Temperature set to: {self.settings['temperature']}")
                    
                elif choice == "3":
                    max_tokens = Prompt.ask("Max tokens (empty for auto)", default="")
                    self.settings["max_tokens"] = int(max_tokens) if max_tokens else None
                    self._print_success(f"Max tokens set to: {self.settings['max_tokens'] or 'Auto'}")
                    
                elif choice == "4":
                    self.settings["stream"] = not self.settings["stream"]
                    status = "enabled" if self.settings["stream"] else "disabled"
                    self._print_success(f"Streaming {status}")
                    
                elif choice == "5":
                    self.settings["save_history"] = not self.settings["save_history"]
                    status = "enabled" if self.settings["save_history"] else "disabled"
                    self._print_success(f"History saving {status}")
                    
                elif choice == "6":
                    format = Prompt.ask(
                        "Export format",
                        choices=["txt", "md", "json"],
                        default=self.settings["export_format"]
                    )
                    self.settings["export_format"] = format
                    self._print_success(f"Export format set to: {format}")
                
                self.console.print()
        else:
            # Fallback implementation
            while True:
                print("\n--- Current Settings ---")
                print(f"1. Model: {self.settings['model'].value}")
                print(f"2. Temperature: {self.settings['temperature']}")
                print(f"3. Max Tokens: {self.settings['max_tokens'] or 'Auto'}")
                print(f"4. Streaming: {'Enabled' if self.settings['stream'] else 'Disabled'}")
                print(f"5. Save History: {'Enabled' if self.settings['save_history'] else 'Disabled'}")
                print(f"6. Export Format: {self.settings['export_format']}")
                print("0. Back to Main Menu")
                
                choice = input("\nChoice (0-6): ")
                
                if choice == "0":
                    break
                elif choice == "1":
                    model = input("Select model (chat/reasoner): ").lower()
                    if model in ["chat", "reasoner"]:
                        self.settings["model"] = DeepSeekModel.CHAT if model == "chat" else DeepSeekModel.REASONER
                        print(f"✓ Model changed to: {model}")
                        
                elif choice == "2":
                    try:
                        temp = float(input("Temperature (0.0-2.0): "))
                        self.settings["temperature"] = max(0.0, min(2.0, temp))
                        print(f"✓ Temperature set to: {self.settings['temperature']}")
                    except ValueError:
                        print("Invalid temperature value")
                        
                elif choice == "3":
                    max_tokens = input("Max tokens (empty for auto): ")
                    self.settings["max_tokens"] = int(max_tokens) if max_tokens else None
                    print(f"✓ Max tokens set to: {self.settings['max_tokens'] or 'Auto'}")
                    
                elif choice == "4":
                    self.settings["stream"] = not self.settings["stream"]
                    status = "enabled" if self.settings["stream"] else "disabled"
                    print(f"✓ Streaming {status}")
                    
                elif choice == "5":
                    self.settings["save_history"] = not self.settings["save_history"]
                    status = "enabled" if self.settings["save_history"] else "disabled"
                    print(f"✓ History saving {status}")
                    
                elif choice == "6":
                    format = input("Export format (txt/md/json): ").lower()
                    if format in ["txt", "md", "json"]:
                        self.settings["export_format"] = format
                        print(f"✓ Export format set to: {format}")
    
    def _show_help(self):
        """Show help and examples"""
        self._print_section_header("Help & Examples")
        
        help_text = """
# DeepSeek CLI Help

## Features

1. **Chat Mode**: Interactive conversation with AI
   - Natural language conversations
   - Context-aware responses
   - Streaming support

2. **Reasoning Mode**: Complex problem solving
   - Step-by-step reasoning
   - Mathematical problems
   - Logical puzzles

3. **Code Generation**: Generate code with explanations
   - Multiple programming languages
   - Best practices included
   - Syntax highlighting

4. **File Analysis**: Analyze and process files
   - Summarize documents
   - Extract insights
   - Suggest improvements

5. **Batch Processing**: Process multiple prompts
   - Concurrent processing
   - Export results
   - Progress tracking

6. **Function Calling**: Demonstrate AI tool usage
   - Weather queries
   - Web search
   - Calculations

## Keyboard Shortcuts

- Ctrl+C: Cancel current operation
- Ctrl+D: Exit application
- Up/Down arrows: Navigate history (in chat mode)

## Tips

- Lower temperature (0.0-0.5) for factual responses
- Higher temperature (0.7-1.5) for creative content
- Use reasoning mode for math and logic problems
- Enable streaming for better user experience
"""
        
        if self.console and RICH_AVAILABLE:
            self.console.print(Markdown(help_text))
            
            # Show example prompts
            examples_panel = Panel(
                "[bold]Example Prompts:[/bold]\n\n"
                "• Explain quantum computing in simple terms\n"
                "• Write a Python function to find prime numbers\n"
                "• What are the main causes of climate change?\n"
                "• Help me debug this code: [code snippet]\n"
                "• Create a business plan outline for a coffee shop\n"
                "• Translate this text to Spanish: [text]",
                title="Examples",
                border_style="cyan",
                padding=(1, 2)
            )
            self.console.print(examples_panel)
        else:
            print(help_text)
            
            print("\n--- Example Prompts ---")
            print("• Explain quantum computing in simple terms")
            print("• Write a Python function to find prime numbers")
            print("• What are the main causes of climate change?")
            print("• Help me debug this code: [code snippet]")
            print("• Create a business plan outline for a coffee shop")
            print("• Translate this text to Spanish: [text]")
    
    # Helper methods
    def _print_section_header(self, title: str):
        """Print a section header"""
        if self.console and RICH_AVAILABLE:
            self.console.print(f"\n[bold magenta]═══ {title} ═══[/bold magenta]\n")
        else:
            print(f"\n═══ {title} ═══\n")
    
    def _print_ai_response(self, response: str):
        """Print AI response with formatting"""
        if self.console and RICH_AVAILABLE:
            self.console.print(f"\n[bold blue]AI:[/bold blue] {response}\n")
        else:
            print(f"\nAI: {response}\n")
    
    def _print_success(self, message: str):
        """Print success message"""
        if self.console and RICH_AVAILABLE:
            self.console.print(f"[green]✓ {message}[/green]")
        else:
            print(f"✓ {message}")
    
    def _print_error(self, message: str):
        """Print error message"""
        if self.console and RICH_AVAILABLE:
            self.console.print(f"[red]✗ {message}[/red]")
        else:
            print(f"✗ {message}")
    
    def _print_warning(self, message: str):
        """Print warning message"""
        if self.console and RICH_AVAILABLE:
            self.console.print(f"[yellow]⚠ {message}[/yellow]")
        else:
            print(f"⚠ {message}")
    
    def _get_extension(self, language: str) -> str:
        """Get file extension for language"""
        extensions = {
            "python": "py",
            "javascript": "js",
            "typescript": "ts",
            "java": "java",
            "c": "c",
            "cpp": "cpp",
            "c++": "cpp",
            "csharp": "cs",
            "c#": "cs",
            "go": "go",
            "rust": "rs",
            "ruby": "rb",
            "php": "php",
            "swift": "swift",
            "kotlin": "kt",
            "scala": "scala",
            "r": "r",
            "matlab": "m",
            "sql": "sql",
            "html": "html",
            "css": "css",
            "bash": "sh",
            "shell": "sh",
            "powershell": "ps1"
        }
        return extensions.get(language.lower(), "txt")
    
    def run(self):
        """Main application loop"""
        self._print_header()
        
        while True:
            try:
                self._print_menu()
                
                if self.console and RICH_AVAILABLE:
                    choice = Prompt.ask(
                        "[bold green]Select option[/bold green]",
                        choices=[opt.value for opt in MenuOption]
                    )
                else:
                    choice = input("Select option (0-9): ")
                
                # Clear screen for better UX
                if self.console and RICH_AVAILABLE:
                    self.console.clear()
                
                try:
                    option = MenuOption(choice)
                    
                    if option == MenuOption.EXIT:
                        if self.console and RICH_AVAILABLE:
                            if Confirm.ask("\n[yellow]Exit DeepSeek CLI?[/yellow]"):
                                self._print_success("Thank you for using DeepSeek CLI!")
                                break
                        else:
                            if input("\nExit DeepSeek CLI? (y/n): ").lower() == 'y':
                                print("Thank you for using DeepSeek CLI!")
                                break
                    
                    elif option == MenuOption.CHAT:
                        self._chat_mode()
                    elif option == MenuOption.REASON:
                        self._reasoning_mode()
                    elif option == MenuOption.CODE_GEN:
                        self._code_generation_mode()
                    elif option == MenuOption.FILE_ANALYZE:
                        self._file_analysis_mode()
                    elif option == MenuOption.BATCH_PROCESS:
                        self._batch_processing_mode()
                    elif option == MenuOption.FUNCTION_CALL:
                        self._function_calling_demo()
                    elif option == MenuOption.USAGE_STATS:
                        self._show_usage_stats()
                    elif option == MenuOption.SETTINGS:
                        self._settings_menu()
                    elif option == MenuOption.HELP:
                        self._show_help()
                        
                except ValueError:
                    self._print_error("Invalid option. Please try again.")
                
                # Pause before returning to menu
                if self.console and RICH_AVAILABLE:
                    self.console.print("\n[dim]Press Enter to continue...[/dim]")
                    input()
                else:
                    input("\nPress Enter to continue...")
                    
            except KeyboardInterrupt:
                if self.console and RICH_AVAILABLE:
                    self.console.print("\n[yellow]Use option 0 to exit properly[/yellow]")
                else:
                    print("\nUse option 0 to exit properly")
                continue
                
            except Exception as e:
                self._print_error(f"Unexpected error: {str(e)}")
                if self.console and RICH_AVAILABLE:
                    self.console.print("[dim]Please report this issue if it persists[/dim]")
                else:
                    print("Please report this issue if it persists")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="DeepSeek CLI - AI-powered command-line assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  deepseek-cli                    # Start interactive mode
  deepseek-cli --chat "Hello"     # Quick chat
  deepseek-cli --reason "2+2"     # Quick reasoning
  deepseek-cli --code "fizzbuzz"  # Generate code
"""
    )
    
    parser.add_argument(
        "--chat", "-c",
        help="Quick chat mode with a single prompt",
        metavar="PROMPT"
    )
    
    parser.add_argument(
        "--reason", "-r",
        help="Quick reasoning mode with a problem",
        metavar="PROBLEM"
    )
    
    parser.add_argument(
        "--code", "-g",
        help="Generate code for a given request",
        metavar="REQUEST"
    )
    
    parser.add_argument(
        "--model", "-m",
        choices=["chat", "reasoner"],
        default="chat",
        help="Model to use (default: chat)"
    )
    
    parser.add_argument(
        "--temperature", "-t",
        type=float,
        default=0.7,
        help="Temperature for responses (0.0-2.0, default: 0.7)"
    )
    
    parser.add_argument(
        "--no-stream",
        action="store_true",
        help="Disable streaming responses"
    )
    
    args = parser.parse_args()
    
    # Quick mode handling
    if args.chat or args.reason or args.code:
        try:
            client = DeepSeekClient()
            model = DeepSeekModel.CHAT if args.model == "chat" else DeepSeekModel.REASONER
            
            if args.chat:
                response = client.chat(
                    args.chat,
                    model=model,
                    temperature=args.temperature,
                    stream=not args.no_stream
                )
                if args.no_stream:
                    print(response)
                else:
                    for chunk in response:
                        print(chunk, end='', flush=True)
                    print()
                    
            elif args.reason:
                result = client.reason(args.reason)
                if "reasoning" in result:
                    print("Reasoning:")
                    print(result["reasoning"])
                    print("\nAnswer:")
                print(result["answer"])
                
            elif args.code:
                prompt = f"Generate Python code for: {args.code}\nInclude comments and best practices."
                response = client.chat(
                    prompt,
                    model=DeepSeekModel.CHAT,
                    temperature=0.2
                )
                print(response)
                
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)
    else:
        # Interactive mode
        cli = DeepSeekCLI()
        cli.run()


if __name__ == "__main__":
    main()