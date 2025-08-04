#!/usr/bin/env python3
"""
DEEP-BASED-CODER IDE Integration
Advanced IDE integration system inspired by Claude Code architecture
Powered by DeepSeek models exclusively with Qwen 3 embeddings
"""

import asyncio
import json
import logging
import os
import sys
import time
import subprocess
import tempfile
import shlex
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable, AsyncGenerator, Tuple
from dataclasses import dataclass, field
from enum import Enum
import traceback
import hashlib
import difflib

# Third-party imports
import rich
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.layout import Layout
from rich.align import Align
from rich.columns import Columns
from rich.tree import Tree
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm
from rich.status import Status
import openai
import aiohttp
import aiosqlite
import chardet
import psutil
from colorama import Fore, Back, Style, init

# Import our core CLI
from deep_based_coder_cli import (
    DeepBasedCoderCore, AdvancedFileManager, DeepSeekReasoningEngine, 
    QwenEmbeddingEngine, ToolResult, ToolLocation, StreamingState
)

# Initialize
init(autoreset=True)
console = Console(color_system="auto", force_terminal=True)
logger = logging.getLogger(__name__)

class CommandType(Enum):
    """Types of commands available in DEEP-BASED-CODER"""
    FILE_OPERATION = "file_op"
    CODE_ANALYSIS = "code_analysis"
    CODE_GENERATION = "code_generation"
    GIT_OPERATION = "git_op"
    SEARCH_OPERATION = "search_op"
    SYSTEM_OPERATION = "system_op"
    CHAT_OPERATION = "chat_op"
    IDE_INTEGRATION = "ide_integration"

class ExecutionMode(Enum):
    """Execution modes for different environments"""
    TERMINAL = "terminal"
    VSCODE = "vscode"
    IDE_PLUGIN = "ide_plugin"
    GITHUB_INTEGRATION = "github"

@dataclass
class Command:
    """Command definition inspired by Claude Code"""
    name: str
    description: str
    command_type: CommandType
    allowed_tools: List[str] = field(default_factory=list)
    execution_mode: ExecutionMode = ExecutionMode.TERMINAL
    requires_confirmation: bool = False
    streaming_enabled: bool = True
    auto_save: bool = False

@dataclass
class IDEContext:
    """IDE context information"""
    current_file: Optional[str] = None
    current_directory: Optional[str] = None
    selected_text: Optional[str] = None
    cursor_position: Optional[Tuple[int, int]] = None
    open_files: List[str] = field(default_factory=list)
    git_branch: Optional[str] = None
    git_status: Optional[str] = None
    project_type: Optional[str] = None

@dataclass
class CodeEdit:
    """Represents a code edit operation"""
    file_path: str
    start_line: int
    end_line: int
    original_content: str
    new_content: str
    edit_type: str  # "replace", "insert", "delete"
    confidence: float = 1.0

class DeepBasedCoderIDE:
    """Advanced IDE integration system inspired by Claude Code"""
    
    def __init__(self):
        self.core = DeepBasedCoderCore()
        self.file_manager = AdvancedFileManager(self.core)
        self.reasoning_engine = DeepSeekReasoningEngine(self.core)
        self.embedding_engine = QwenEmbeddingEngine(self.core)
        
        self.commands = {}
        self.hooks = {}
        self.context = IDEContext()
        self.session_history = []
        self.active_edits = []
        
        self.register_commands()
        self.setup_hooks()
        
    def register_commands(self):
        """Register all available commands"""
        commands = [
            Command(
                name="analyze",
                description="Analyze code quality, bugs, and improvements",
                command_type=CommandType.CODE_ANALYSIS,
                allowed_tools=["file_read", "deepseek_reasoner"],
                streaming_enabled=True
            ),
            Command(
                name="generate",
                description="Generate code based on natural language description",
                command_type=CommandType.CODE_GENERATION,
                allowed_tools=["deepseek_coder", "file_write"],
                requires_confirmation=True,
                auto_save=True
            ),
            Command(
                name="refactor",
                description="Refactor code to improve quality and maintainability",
                command_type=CommandType.CODE_ANALYSIS,
                allowed_tools=["file_read", "deepseek_coder", "file_write"],
                requires_confirmation=True,
                auto_save=True
            ),
            Command(
                name="explain",
                description="Explain complex code sections in detail",
                command_type=CommandType.CODE_ANALYSIS,
                allowed_tools=["file_read", "deepseek_reasoner"],
                streaming_enabled=True
            ),
            Command(
                name="debug",
                description="Find and fix bugs in code",
                command_type=CommandType.CODE_ANALYSIS,
                allowed_tools=["file_read", "deepseek_reasoner", "file_write"],
                requires_confirmation=True
            ),
            Command(
                name="optimize",
                description="Optimize code for performance",
                command_type=CommandType.CODE_ANALYSIS,
                allowed_tools=["file_read", "deepseek_coder", "file_write"],
                requires_confirmation=True
            ),
            Command(
                name="search",
                description="Search codebase using semantic similarity",
                command_type=CommandType.SEARCH_OPERATION,
                allowed_tools=["qwen_embedding", "file_search"],
                streaming_enabled=True
            ),
            Command(
                name="commit",
                description="Generate commit messages and handle git operations",
                command_type=CommandType.GIT_OPERATION,
                allowed_tools=["git", "deepseek_chat"],
                requires_confirmation=True
            ),
            Command(
                name="test",
                description="Generate and run tests for code",
                command_type=CommandType.CODE_GENERATION,
                allowed_tools=["deepseek_coder", "file_write", "bash"],
                requires_confirmation=True
            ),
            Command(
                name="docs",
                description="Generate documentation for code",
                command_type=CommandType.CODE_GENERATION,
                allowed_tools=["file_read", "deepseek_coder", "file_write"],
                auto_save=True
            )
        ]
        
        for cmd in commands:
            self.commands[cmd.name] = cmd
            
    def setup_hooks(self):
        """Setup command hooks for safety and validation"""
        # Pre-execution hooks
        self.hooks["pre_execute"] = [
            self.validate_file_permissions,
            self.backup_files,
            self.check_git_status
        ]
        
        # Post-execution hooks
        self.hooks["post_execute"] = [
            self.update_context,
            self.log_execution,
            self.trigger_auto_save
        ]
        
    async def execute_command(self, command_name: str, args: Dict[str, Any]) -> ToolResult:
        """Execute a command with full validation and hooks"""
        if command_name not in self.commands:
            return ToolResult(
                success=False,
                error_message=f"Unknown command: {command_name}"
            )
            
        command = self.commands[command_name]
        
        try:
            # Run pre-execution hooks
            for hook in self.hooks.get("pre_execute", []):
                hook_result = await hook(command, args)
                if not hook_result.success:
                    return hook_result
                    
            # Execute the actual command
            result = await self._execute_command_internal(command, args)
            
            # Run post-execution hooks
            for hook in self.hooks.get("post_execute", []):
                await hook(command, args, result)
                
            return result
            
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return ToolResult(
                success=False,
                error_message=f"Command execution failed: {str(e)}"
            )
            
    async def _execute_command_internal(self, command: Command, args: Dict[str, Any]) -> ToolResult:
        """Internal command execution logic"""
        if command.command_type == CommandType.CODE_ANALYSIS:
            return await self._handle_code_analysis(command, args)
        elif command.command_type == CommandType.CODE_GENERATION:
            return await self._handle_code_generation(command, args)
        elif command.command_type == CommandType.SEARCH_OPERATION:
            return await self._handle_search_operation(command, args)
        elif command.command_type == CommandType.GIT_OPERATION:
            return await self._handle_git_operation(command, args)
        else:
            return await self._handle_generic_command(command, args)
            
    async def _handle_code_analysis(self, command: Command, args: Dict[str, Any]) -> ToolResult:
        """Handle code analysis commands"""
        file_path = args.get("file_path") or self.context.current_file
        
        if not file_path:
            return ToolResult(
                success=False,
                error_message="No file specified for analysis"
            )
            
        # Read the file
        read_result = await self.file_manager.read_file(file_path)
        if not read_result.success:
            return read_result
            
        # Determine the specific analysis based on command
        if command.name == "analyze":
            prompt = f"""
            Analyze this code for:
            1. Code quality and best practices
            2. Potential bugs and issues
            3. Performance considerations
            4. Security vulnerabilities
            5. Maintainability concerns
            6. Specific improvement suggestions
            
            File: {file_path}
            Code:
            ```
            {read_result.content}
            ```
            
            Provide detailed analysis with specific line references where applicable.
            """
        elif command.name == "explain":
            selected_text = args.get("selected_text") or self.context.selected_text
            if selected_text:
                prompt = f"""
                Explain this specific code section in detail:
                
                Selected code:
                ```
                {selected_text}
                ```
                
                Full file context: {file_path}
                
                Provide a comprehensive explanation covering:
                1. What this code does
                2. How it works step by step
                3. Why it's implemented this way
                4. Potential edge cases or considerations
                """
            else:
                prompt = f"""
                Explain this entire file in detail:
                
                File: {file_path}
                Code:
                ```
                {read_result.content}
                ```
                
                Provide a comprehensive explanation of the code's purpose, structure, and functionality.
                """
        elif command.name == "debug":
            error_context = args.get("error_context", "")
            prompt = f"""
            Debug this code and find potential issues:
            
            File: {file_path}
            Error context: {error_context}
            
            Code:
            ```
            {read_result.content}
            ```
            
            Please:
            1. Identify potential bugs and issues
            2. Suggest specific fixes with line numbers
            3. Explain the root cause of problems
            4. Provide corrected code if needed
            """
        else:
            prompt = f"Analyze this code: {read_result.content}"
            
        # Use DeepSeek Reasoner for analysis
        analysis_result = await self.reasoning_engine._make_reasoning_request(
            prompt, "deepseek-reasoner"
        )
        
        return ToolResult(
            success=True,
            content=analysis_result,
            is_markdown=True,
            metadata={
                "command": command.name,
                "file_path": file_path,
                "analysis_type": "code_analysis"
            }
        )
        
    async def _handle_code_generation(self, command: Command, args: Dict[str, Any]) -> ToolResult:
        """Handle code generation commands"""
        if command.name == "generate":
            description = args.get("description", "")
            language = args.get("language", "python")
            context_files = args.get("context_files", [])
            
            # Build context from related files
            context = ""
            for file_path in context_files:
                file_result = await self.file_manager.read_file(file_path)
                if file_result.success:
                    context += f"\n\nFile: {file_path}\n```\n{file_result.content}\n```"
                    
            prompt = f"""
            Generate {language} code based on this description:
            
            Description: {description}
            Language: {language}
            
            Context from existing files: {context}
            
            Please provide:
            1. Clean, well-documented code
            2. Proper error handling
            3. Type hints (where applicable)
            4. Unit tests (if requested)
            5. Usage examples
            
            Return only the code without additional explanations unless specifically requested.
            """
            
        elif command.name == "refactor":
            file_path = args.get("file_path") or self.context.current_file
            refactor_goals = args.get("goals", ["improve readability", "reduce complexity"])
            
            read_result = await self.file_manager.read_file(file_path)
            if not read_result.success:
                return read_result
                
            prompt = f"""
            Refactor this code to achieve the following goals: {', '.join(refactor_goals)}
            
            Original code:
            ```
            {read_result.content}
            ```
            
            Please:
            1. Maintain the same functionality
            2. Improve code structure and readability
            3. Follow best practices for the language
            4. Add comments where helpful
            5. Preserve existing API if it's a public interface
            
            Return the refactored code.
            """
            
        elif command.name == "test":
            file_path = args.get("file_path") or self.context.current_file
            test_type = args.get("test_type", "unit")
            
            read_result = await self.file_manager.read_file(file_path)
            if not read_result.success:
                return read_result
                
            prompt = f"""
            Generate {test_type} tests for this code:
            
            Code to test:
            ```
            {read_result.content}
            ```
            
            Please provide:
            1. Comprehensive test coverage
            2. Edge case testing
            3. Mock objects where needed
            4. Clear test names and descriptions
            5. Setup and teardown if required
            
            Use appropriate testing framework for the language.
            """
            
        elif command.name == "docs":
            file_path = args.get("file_path") or self.context.current_file
            doc_type = args.get("doc_type", "api")
            
            read_result = await self.file_manager.read_file(file_path)
            if not read_result.success:
                return read_result
                
            prompt = f"""
            Generate {doc_type} documentation for this code:
            
            Code:
            ```
            {read_result.content}
            ```
            
            Please provide:
            1. Clear API documentation
            2. Usage examples
            3. Parameter descriptions
            4. Return value descriptions
            5. Exception information
            6. Code examples
            
            Format as markdown documentation.
            """
        else:
            return ToolResult(
                success=False,
                error_message=f"Unknown generation command: {command.name}"
            )
            
        # Use DeepSeek Coder for generation
        generation_result = await self.reasoning_engine._make_reasoning_request(
            prompt, "deepseek-coder"
        )
        
        # If auto_save is enabled and we have a target file, save the result
        if command.auto_save and args.get("output_file"):
            output_file = args["output_file"]
            write_result = await self.file_manager.write_file(
                output_file, generation_result
            )
            if write_result.success:
                return ToolResult(
                    success=True,
                    content=f"Code generated and saved to {output_file}",
                    metadata={
                        "generated_code": generation_result,
                        "output_file": output_file,
                        "command": command.name
                    }
                )
                
        return ToolResult(
            success=True,
            content=generation_result,
            metadata={
                "command": command.name,
                "generation_type": "code_generation"
            }
        )
        
    async def _handle_search_operation(self, command: Command, args: Dict[str, Any]) -> ToolResult:
        """Handle search operations using embeddings"""
        query = args.get("query", "")
        search_path = args.get("search_path", self.context.current_directory or ".")
        file_types = args.get("file_types", [".py", ".js", ".ts", ".java", ".cpp", ".c"])
        
        if not query:
            return ToolResult(
                success=False,
                error_message="No search query provided"
            )
            
        # Find all relevant files
        search_files = []
        search_path_obj = Path(search_path)
        
        for file_type in file_types:
            search_files.extend(search_path_obj.rglob(f"*{file_type}"))
            
        # Read file contents for similarity search
        file_contents = []
        file_paths = []
        
        for file_path in search_files[:50]:  # Limit to 50 files for performance
            try:
                read_result = await self.file_manager.read_file(str(file_path))
                if read_result.success:
                    file_contents.append(read_result.content)
                    file_paths.append(str(file_path))
            except Exception as e:
                logger.warning(f"Failed to read file {file_path}: {e}")
                
        if not file_contents:
            return ToolResult(
                success=False,
                error_message="No files found to search"
            )
            
        # Use embedding engine for similarity search
        similar_results = await self.embedding_engine.find_similar(
            query, file_contents, top_k=10
        )
        
        # Format results
        results_text = f"# Search Results for: {query}\n\n"
        
        for idx, (file_idx, content, similarity) in enumerate(similar_results, 1):
            file_path = file_paths[file_idx]
            results_text += f"## {idx}. {file_path} (Similarity: {similarity:.3f})\n\n"
            
            # Show relevant snippet
            lines = content.split('\n')
            snippet_lines = lines[:10] if len(lines) > 10 else lines
            results_text += f"```\n" + '\n'.join(snippet_lines) + f"\n```\n\n"
            
        return ToolResult(
            success=True,
            content=results_text,
            is_markdown=True,
            metadata={
                "query": query,
                "results_count": len(similar_results),
                "search_path": search_path
            }
        )
        
    async def _handle_git_operation(self, command: Command, args: Dict[str, Any]) -> ToolResult:
        """Handle git operations"""
        if command.name == "commit":
            # Get git status
            try:
                result = subprocess.run(
                    ["git", "status", "--porcelain"],
                    capture_output=True,
                    text=True,
                    cwd=self.context.current_directory
                )
                
                if result.returncode != 0:
                    return ToolResult(
                        success=False,
                        error_message="Not in a git repository or git error"
                    )
                    
                changes = result.stdout.strip()
                if not changes:
                    return ToolResult(
                        success=False,
                        error_message="No changes to commit"
                    )
                    
                # Get diff for context
                diff_result = subprocess.run(
                    ["git", "diff", "--cached"],
                    capture_output=True,
                    text=True,
                    cwd=self.context.current_directory
                )
                
                if not diff_result.stdout.strip():
                    # If nothing staged, show working directory changes
                    diff_result = subprocess.run(
                        ["git", "diff"],
                        capture_output=True,
                        text=True,
                        cwd=self.context.current_directory
                    )
                    
                diff_content = diff_result.stdout
                
                # Generate commit message using DeepSeek
                prompt = f"""
                Generate a concise, descriptive commit message for these changes:
                
                Git status:
                {changes}
                
                Git diff:
                {diff_content[:2000]}  # Limit diff size
                
                Follow conventional commit format:
                - feat: new feature
                - fix: bug fix
                - docs: documentation
                - style: formatting
                - refactor: code restructuring
                - test: adding tests
                - chore: maintenance
                
                Provide just the commit message, nothing else.
                """
                
                commit_message = await self.reasoning_engine._make_reasoning_request(
                    prompt, "deepseek-chat"
                )
                
                return ToolResult(
                    success=True,
                    content=f"Suggested commit message:\n\n{commit_message}",
                    metadata={
                        "commit_message": commit_message,
                        "changes": changes,
                        "diff_size": len(diff_content)
                    }
                )
                
            except Exception as e:
                return ToolResult(
                    success=False,
                    error_message=f"Git operation failed: {str(e)}"
                )
        else:
            return ToolResult(
                success=False,
                error_message=f"Unknown git command: {command.name}"
            )
            
    async def _handle_generic_command(self, command: Command, args: Dict[str, Any]) -> ToolResult:
        """Handle generic commands"""
        return ToolResult(
            success=False,
            error_message=f"Generic handler not implemented for {command.name}"
        )
        
    # Hook implementations
    async def validate_file_permissions(self, command: Command, args: Dict[str, Any]) -> ToolResult:
        """Validate file permissions before execution"""
        file_path = args.get("file_path") or args.get("output_file")
        
        if file_path:
            file_obj = Path(file_path)
            
            # Check if we can write to the directory
            if not file_obj.parent.exists():
                return ToolResult(
                    success=False,
                    error_message=f"Directory does not exist: {file_obj.parent}"
                )
                
            if file_obj.exists() and not os.access(file_obj, os.W_OK):
                return ToolResult(
                    success=False,
                    error_message=f"No write permission for file: {file_path}"
                )
                
        return ToolResult(success=True)
        
    async def backup_files(self, command: Command, args: Dict[str, Any]) -> ToolResult:
        """Create backups of files that will be modified"""
        if command.command_type in [CommandType.CODE_GENERATION] and "output_file" in args:
            file_path = args["output_file"]
            if Path(file_path).exists():
                backup_path = f"{file_path}.backup_{int(time.time())}"
                try:
                    import shutil
                    shutil.copy2(file_path, backup_path)
                    logger.info(f"Created backup: {backup_path}")
                except Exception as e:
                    logger.warning(f"Failed to create backup: {e}")
                    
        return ToolResult(success=True)
        
    async def check_git_status(self, command: Command, args: Dict[str, Any]) -> ToolResult:
        """Check git status before making changes"""
        if command.requires_confirmation:
            try:
                result = subprocess.run(
                    ["git", "status", "--porcelain"],
                    capture_output=True,
                    text=True,
                    cwd=self.context.current_directory
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    self.context.git_status = result.stdout.strip()
                    logger.info(f"Git status: {len(result.stdout.strip().split())} changes detected")
            except Exception:
                pass  # Not in git repo or git not available
                
        return ToolResult(success=True)
        
    async def update_context(self, command: Command, args: Dict[str, Any], result: ToolResult):
        """Update IDE context after command execution"""
        if result.success:
            # Update current file if we worked on one
            if "file_path" in args:
                self.context.current_file = args["file_path"]
            elif "output_file" in args:
                self.context.current_file = args["output_file"]
                
            # Update open files list
            if self.context.current_file and self.context.current_file not in self.context.open_files:
                self.context.open_files.append(self.context.current_file)
                
    async def log_execution(self, command: Command, args: Dict[str, Any], result: ToolResult):
        """Log command execution for session history"""
        execution_record = {
            "timestamp": datetime.now().isoformat(),
            "command": command.name,
            "args": args,
            "success": result.success,
            "execution_time": result.execution_time,
            "error": result.error_message if not result.success else None
        }
        
        self.session_history.append(execution_record)
        
        # Keep only last 100 executions
        if len(self.session_history) > 100:
            self.session_history = self.session_history[-100:]
            
    async def trigger_auto_save(self, command: Command, args: Dict[str, Any], result: ToolResult):
        """Trigger auto-save if enabled"""
        if command.auto_save and result.success and "output_file" in args:
            logger.info(f"Auto-saved file: {args['output_file']}")
            
    def update_ide_context(self, context_data: Dict[str, Any]):
        """Update IDE context from external source (VS Code extension, etc.)"""
        if "current_file" in context_data:
            self.context.current_file = context_data["current_file"]
        if "current_directory" in context_data:
            self.context.current_directory = context_data["current_directory"]
        if "selected_text" in context_data:
            self.context.selected_text = context_data["selected_text"]
        if "cursor_position" in context_data:
            self.context.cursor_position = tuple(context_data["cursor_position"])
        if "open_files" in context_data:
            self.context.open_files = context_data["open_files"]
        if "git_branch" in context_data:
            self.context.git_branch = context_data["git_branch"]
            
    async def get_command_suggestions(self, partial_input: str) -> List[str]:
        """Get command suggestions based on partial input and context"""
        suggestions = []
        
        # Filter commands by partial match
        matching_commands = [
            cmd for cmd in self.commands.keys()
            if cmd.startswith(partial_input.lower())
        ]
        
        # Add context-aware suggestions
        if self.context.current_file:
            file_ext = Path(self.context.current_file).suffix
            if file_ext in ['.py', '.js', '.ts', '.java']:
                suggestions.extend(['analyze', 'refactor', 'test', 'docs'])
                
        if self.context.selected_text:
            suggestions.extend(['explain', 'refactor'])
            
        if self.context.git_status:
            suggestions.append('commit')
            
        # Combine and deduplicate
        all_suggestions = list(set(matching_commands + suggestions))
        return sorted(all_suggestions)
        
    async def export_session(self, output_path: str) -> ToolResult:
        """Export current session data"""
        session_data = {
            "timestamp": datetime.now().isoformat(),
            "context": {
                "current_file": self.context.current_file,
                "current_directory": self.context.current_directory,
                "open_files": self.context.open_files,
                "git_branch": self.context.git_branch
            },
            "history": self.session_history,
            "active_edits": self.active_edits
        }
        
        try:
            with open(output_path, 'w') as f:
                json.dump(session_data, f, indent=2)
                
            return ToolResult(
                success=True,
                content=f"Session exported to {output_path}",
                metadata={"output_path": output_path}
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error_message=f"Failed to export session: {str(e)}"
            )

# CLI Interface for IDE Integration
async def main():
    """Main CLI interface for IDE integration"""
    ide = DeepBasedCoderIDE()
    
    console.print(Panel.fit(
        "[bold blue]DEEP-BASED-CODER IDE[/bold blue]\n"
        "[dim]Advanced IDE Integration System[/dim]\n"
        "[dim]Powered by DeepSeek & Qwen 3[/dim]",
        border_style="blue"
    ))
    
    # Example usage
    while True:
        try:
            command_input = Prompt.ask("\n[bold blue]DEEP-IDE[/bold blue] > ").strip()
            
            if command_input.lower() in ['exit', 'quit']:
                break
                
            if command_input.startswith('/'):
                # Parse command
                parts = command_input[1:].split()
                if not parts:
                    continue
                    
                command_name = parts[0]
                
                # Simple argument parsing (in real implementation, use proper parser)
                args = {}
                for i in range(1, len(parts), 2):
                    if i + 1 < len(parts):
                        args[parts[i]] = parts[i + 1]
                        
                # Execute command
                with console.status(f"[bold green]Executing {command_name}..."):
                    result = await ide.execute_command(command_name, args)
                    
                if result.success:
                    if result.is_markdown:
                        console.print(Panel(
                            Markdown(result.content),
                            title=f"[bold green]✅ {command_name.title()}[/bold green]",
                            border_style="green"
                        ))
                    else:
                        console.print(f"[green]✅ {result.content}[/green]")
                else:
                    console.print(f"[red]❌ {result.error_message}[/red]")
            else:
                # Regular chat
                result = await ide.reasoning_engine._make_reasoning_request(
                    command_input, "deepseek-chat"
                )
                console.print(Panel(
                    Markdown(result),
                    title="[bold blue]DEEP-BASED-CODER[/bold blue]",
                    border_style="blue"
                ))
                
        except KeyboardInterrupt:
            console.print("\n[yellow]Use 'exit' to quit[/yellow]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            
    console.print("[green]✅ DEEP-BASED-CODER IDE session ended[/green]")

if __name__ == "__main__":
    asyncio.run(main())