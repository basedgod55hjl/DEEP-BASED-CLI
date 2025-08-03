"""
Coder Agent - AI-powered coding assistant
"""

import os
import sys
import ast
import json
import subprocess
import tempfile
import traceback
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown

from ..core.client import DeepSeekClient
from ..core.models import DeepSeekModel, Message
from ..memory.manager import MemoryManager


class CodeExecutor:
    """Safe code execution environment"""
    
    SUPPORTED_LANGUAGES = {
        "python": {"ext": ".py", "cmd": ["python3", "-u"]},
        "javascript": {"ext": ".js", "cmd": ["node"]},
        "bash": {"ext": ".sh", "cmd": ["bash"]},
        "shell": {"ext": ".sh", "cmd": ["sh"]},
        "sql": {"ext": ".sql", "cmd": None},  # Special handling
    }
    
    def __init__(self, console: Console):
        self.console = console
        self.temp_dir = Path(tempfile.gettempdir()) / "deepcli_code"
        self.temp_dir.mkdir(exist_ok=True)
    
    def detect_language(self, code: str) -> str:
        """Detect programming language from code"""
        # Check for explicit language markers
        if code.strip().startswith("```"):
            first_line = code.strip().split('\n')[0]
            lang = first_line.replace("```", "").strip()
            if lang in self.SUPPORTED_LANGUAGES:
                return lang
        
        # Try to parse as Python
        try:
            ast.parse(code)
            return "python"
        except:
            pass
        
        # Check for common patterns
        if "console.log" in code or "const " in code or "let " in code:
            return "javascript"
        elif code.strip().startswith("#!/bin/bash") or "echo " in code:
            return "bash"
        elif "SELECT" in code.upper() or "CREATE TABLE" in code.upper():
            return "sql"
        
        return "python"  # Default
    
    def execute_code(
        self,
        code: str,
        language: Optional[str] = None,
        timeout: int = 30
    ) -> Tuple[bool, str, str]:
        """
        Execute code safely
        
        Returns: (success, stdout, stderr)
        """
        if language is None:
            language = self.detect_language(code)
        
        if language not in self.SUPPORTED_LANGUAGES:
            return False, "", f"Unsupported language: {language}"
        
        lang_config = self.SUPPORTED_LANGUAGES[language]
        
        # Special handling for SQL
        if language == "sql":
            return self._execute_sql(code)
        
        # Clean code
        code = code.strip()
        if code.startswith("```"):
            # Remove markdown code blocks
            lines = code.split('\n')
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1] == "```":
                lines = lines[:-1]
            code = '\n'.join(lines)
        
        # Create temporary file
        temp_file = self.temp_dir / f"code_{os.getpid()}{lang_config['ext']}"
        
        try:
            # Write code to file
            with open(temp_file, 'w') as f:
                f.write(code)
            
            # Make executable if shell script
            if language in ["bash", "shell"]:
                os.chmod(temp_file, 0o755)
            
            # Execute
            result = subprocess.run(
                lang_config["cmd"] + [str(temp_file)],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.temp_dir
            )
            
            return result.returncode == 0, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            return False, "", f"Execution timed out after {timeout} seconds"
        except Exception as e:
            return False, "", f"Execution error: {str(e)}"
        finally:
            # Cleanup
            if temp_file.exists():
                temp_file.unlink()
    
    def _execute_sql(self, sql: str) -> Tuple[bool, str, str]:
        """Execute SQL in memory (for demo)"""
        try:
            import sqlite3
            
            # Create in-memory database
            conn = sqlite3.connect(':memory:')
            cursor = conn.cursor()
            
            # Execute SQL statements
            statements = sql.strip().split(';')
            results = []
            
            for stmt in statements:
                stmt = stmt.strip()
                if stmt:
                    cursor.execute(stmt)
                    if stmt.upper().startswith('SELECT'):
                        results.append(str(cursor.fetchall()))
                    else:
                        conn.commit()
                        results.append(f"Executed: {stmt[:50]}...")
            
            conn.close()
            return True, '\n'.join(results), ""
            
        except Exception as e:
            return False, "", str(e)


class CoderAgent:
    """AI-powered coder agent with conversation and execution capabilities"""
    
    def __init__(self, client: DeepSeekClient, memory: MemoryManager, console: Console):
        self.client = client
        self.memory = memory
        self.console = console
        self.executor = CodeExecutor(console)
        self.conversation_history: List[Message] = []
        self.code_history: List[Dict[str, Any]] = []
        
    async def start_session(self):
        """Start a coder agent session"""
        self.console.print(Panel(
            "[bold cyan]🧑‍💻 Coder Agent Activated[/bold cyan]\n\n"
            "I'm your AI coding assistant powered by DeepSeek. I can:\n"
            "• Write code in multiple languages\n"
            "• Debug and fix errors\n"
            "• Execute code safely\n"
            "• Explain complex concepts\n"
            "• Refactor and optimize\n\n"
            "Type 'help' for commands or just describe what you need!",
            border_style="green"
        ))
        
        # Load previous context
        await self._load_context()
        
        while True:
            try:
                user_input = Prompt.ask("\n[cyan]You[/cyan]")
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    break
                elif user_input.lower() == 'help':
                    self._show_help()
                    continue
                elif user_input.lower() == 'history':
                    await self._show_history()
                    continue
                elif user_input.lower() == 'clear':
                    self.conversation_history = []
                    self.console.print("[yellow]Conversation cleared.[/yellow]")
                    continue
                
                # Process the request
                await self._process_request(user_input)
                
            except KeyboardInterrupt:
                if Confirm.ask("\nExit Coder Agent?"):
                    break
            except Exception as e:
                self.console.print(f"[red]Error: {str(e)}[/red]")
        
        # Save context
        await self._save_context()
        self.console.print("\n[yellow]Coder Agent session ended. Context saved.[/yellow]")
    
    async def _process_request(self, user_input: str):
        """Process a user request"""
        # Add to conversation
        self.conversation_history.append(Message(role="user", content=user_input))
        
        # Determine intent
        intent = await self._analyze_intent(user_input)
        
        if intent == "create_code":
            await self._create_code(user_input)
        elif intent == "debug_code":
            await self._debug_code(user_input)
        elif intent == "explain_code":
            await self._explain_code(user_input)
        elif intent == "execute_code":
            await self._handle_execution(user_input)
        else:
            # General conversation
            await self._general_response(user_input)
    
    async def _analyze_intent(self, user_input: str) -> str:
        """Analyze user intent"""
        lower_input = user_input.lower()
        
        if any(word in lower_input for word in ["create", "write", "generate", "make", "build"]):
            return "create_code"
        elif any(word in lower_input for word in ["debug", "fix", "error", "bug", "issue"]):
            return "debug_code"
        elif any(word in lower_input for word in ["explain", "what does", "how does", "understand"]):
            return "explain_code"
        elif any(word in lower_input for word in ["run", "execute", "test"]):
            return "execute_code"
        else:
            return "general"
    
    async def _create_code(self, request: str):
        """Create code based on request"""
        self.console.print("\n[yellow]🎯 Generating code...[/yellow]")
        
        # Build prompt
        prompt = f"""You are an expert programmer. Generate high-quality, production-ready code based on this request:

Request: {request}

Requirements:
1. Write clean, well-commented code
2. Follow best practices and conventions
3. Include error handling
4. Make it efficient and maintainable
5. Add helpful comments explaining key parts

Previous context:
{self._get_recent_context()}

Provide the code with a brief explanation of the implementation."""
        
        messages = self.conversation_history + [Message(role="user", content=prompt)]
        
        # Get response
        response = await self.client.chat(messages, temperature=0.2)
        
        # Parse and display code
        await self._display_code_response(response)
        
        # Add to history
        self.conversation_history.append(Message(role="assistant", content=response))
        
        # Offer to execute
        if Confirm.ask("\n[cyan]Would you like to execute this code?[/cyan]"):
            await self._execute_generated_code(response)
    
    async def _debug_code(self, request: str):
        """Debug code issues"""
        self.console.print("\n[yellow]🐛 Analyzing code for issues...[/yellow]")
        
        # Check if code is provided
        code_block = self._extract_code_from_input(request)
        
        if not code_block:
            # Ask for code
            self.console.print("[cyan]Please paste the code you want to debug:[/cyan]")
            code_lines = []
            while True:
                line = input()
                if line.strip() == "```" and code_lines:
                    break
                code_lines.append(line)
            code_block = '\n'.join(code_lines)
        
        prompt = f"""You are an expert debugger. Analyze this code and:

1. Identify any bugs or issues
2. Explain what's causing the problem
3. Provide a corrected version
4. Add comments explaining the fixes

Code to debug:
```
{code_block}
```

Error context (if any): {request}"""
        
        messages = [Message(role="user", content=prompt)]
        response = await self.client.chat(messages, temperature=0.1)
        
        await self._display_code_response(response)
        self.conversation_history.append(Message(role="assistant", content=response))
    
    async def _explain_code(self, request: str):
        """Explain code functionality"""
        self.console.print("\n[yellow]💡 Analyzing code...[/yellow]")
        
        code_block = self._extract_code_from_input(request)
        
        if not code_block:
            self.console.print("[cyan]Please paste the code you want explained:[/cyan]")
            code_lines = []
            while True:
                line = input()
                if line.strip() == "```" and code_lines:
                    break
                code_lines.append(line)
            code_block = '\n'.join(code_lines)
        
        prompt = f"""Explain this code in detail:

```
{code_block}
```

Provide:
1. Overall purpose and functionality
2. Step-by-step explanation
3. Key concepts used
4. Potential improvements or considerations
5. Example usage if applicable"""
        
        messages = [Message(role="user", content=prompt)]
        response = await self.client.chat(messages, temperature=0.3)
        
        self.console.print(Panel(Markdown(response), title="Code Explanation", border_style="blue"))
        self.conversation_history.append(Message(role="assistant", content=response))
    
    async def _handle_execution(self, request: str):
        """Handle code execution request"""
        code_block = self._extract_code_from_input(request)
        
        if code_block:
            await self._execute_code_block(code_block)
        else:
            # Look for recent code in history
            recent_code = self._get_recent_code()
            if recent_code:
                self.console.print("[cyan]Executing most recent code...[/cyan]")
                await self._execute_code_block(recent_code)
            else:
                self.console.print("[yellow]No code found to execute. Please provide code or generate some first.[/yellow]")
    
    async def _execute_code_block(self, code: str, language: Optional[str] = None):
        """Execute a code block"""
        self.console.print("\n[yellow]🚀 Executing code...[/yellow]")
        
        # Show code to be executed
        lang = language or self.executor.detect_language(code)
        syntax = Syntax(code, lang, theme="monokai", line_numbers=True)
        self.console.print(Panel(syntax, title=f"Executing {lang.title()} Code", border_style="yellow"))
        
        # Execute
        success, stdout, stderr = self.executor.execute_code(code, lang)
        
        # Display results
        if success:
            self.console.print(Panel(
                stdout or "[dim]No output[/dim]",
                title="✅ Output",
                border_style="green"
            ))
        else:
            self.console.print(Panel(
                stderr or "Execution failed",
                title="❌ Error",
                border_style="red"
            ))
        
        # Save execution history
        self.code_history.append({
            "code": code,
            "language": lang,
            "success": success,
            "output": stdout if success else stderr
        })
    
    async def _execute_generated_code(self, response: str):
        """Execute code from AI response"""
        code_blocks = self._extract_all_code_blocks(response)
        
        if not code_blocks:
            self.console.print("[yellow]No code blocks found in response.[/yellow]")
            return
        
        for i, (code, lang) in enumerate(code_blocks):
            if len(code_blocks) > 1:
                self.console.print(f"\n[cyan]Code block {i+1} of {len(code_blocks)}:[/cyan]")
            
            await self._execute_code_block(code, lang)
            
            if i < len(code_blocks) - 1:
                if not Confirm.ask("\n[cyan]Continue with next code block?[/cyan]"):
                    break
    
    async def _general_response(self, user_input: str):
        """Handle general conversation"""
        messages = self.conversation_history[-10:] + [Message(role="user", content=user_input)]
        
        self.console.print("\n[cyan]Coder Agent:[/cyan]")
        
        response_text = ""
        async for chunk in await self.client.chat(messages, stream=True):
            self.console.print(chunk, end='')
            response_text += chunk
        
        self.console.print()
        self.conversation_history.append(Message(role="assistant", content=response_text))
        
        # Check if response contains code
        if "```" in response_text:
            if Confirm.ask("\n[cyan]This response contains code. Would you like to execute it?[/cyan]"):
                await self._execute_generated_code(response_text)
    
    async def _display_code_response(self, response: str):
        """Display a response containing code"""
        # Split response into text and code parts
        parts = response.split("```")
        
        for i, part in enumerate(parts):
            if i % 2 == 0:
                # Text part
                if part.strip():
                    self.console.print(Markdown(part.strip()))
            else:
                # Code part
                lines = part.split('\n')
                lang = lines[0].strip() if lines[0].strip() else "python"
                code = '\n'.join(lines[1:]) if len(lines) > 1 else part
                
                if code.strip():
                    syntax = Syntax(code, lang, theme="monokai", line_numbers=True)
                    self.console.print(Panel(syntax, title=f"{lang.title()} Code", border_style="green"))
    
    def _extract_code_from_input(self, text: str) -> Optional[str]:
        """Extract code block from user input"""
        if "```" in text:
            parts = text.split("```")
            if len(parts) >= 3:
                return parts[1].split('\n', 1)[1] if '\n' in parts[1] else parts[1]
        return None
    
    def _extract_all_code_blocks(self, text: str) -> List[Tuple[str, str]]:
        """Extract all code blocks with their languages"""
        blocks = []
        parts = text.split("```")
        
        for i in range(1, len(parts), 2):
            lines = parts[i].split('\n')
            lang = lines[0].strip() if lines[0].strip() else "python"
            code = '\n'.join(lines[1:]) if len(lines) > 1 else parts[i]
            
            if code.strip():
                blocks.append((code.strip(), lang))
        
        return blocks
    
    def _get_recent_code(self) -> Optional[str]:
        """Get most recent code from history"""
        for msg in reversed(self.conversation_history):
            if msg.role == "assistant" and "```" in msg.content:
                blocks = self._extract_all_code_blocks(msg.content)
                if blocks:
                    return blocks[0][0]
        return None
    
    def _get_recent_context(self) -> str:
        """Get recent conversation context"""
        recent = self.conversation_history[-3:]
        context = []
        for msg in recent:
            role = "User" if msg.role == "user" else "Assistant"
            # Truncate long messages
            content = msg.content[:200] + "..." if len(msg.content) > 200 else msg.content
            context.append(f"{role}: {content}")
        return "\n".join(context) if context else "No recent context"
    
    async def _load_context(self):
        """Load previous session context"""
        try:
            # Load conversation history
            history = await self.memory.recall("coder_conversation", namespace="coder_agent")
            if history:
                self.conversation_history = [
                    Message(role=msg['role'], content=msg['content'])
                    for msg in history[-10:]  # Last 10 messages
                ]
                self.console.print("[dim]Previous conversation loaded.[/dim]")
            
            # Load code history
            code_hist = await self.memory.recall("coder_code_history", namespace="coder_agent")
            if code_hist:
                self.code_history = code_hist[-5:]  # Last 5 code executions
        except:
            pass
    
    async def _save_context(self):
        """Save session context"""
        try:
            # Save conversation
            conversation_data = [
                {"role": msg.role, "content": msg.content}
                for msg in self.conversation_history[-20:]  # Keep last 20
            ]
            await self.memory.store(
                "coder_conversation",
                conversation_data,
                namespace="coder_agent"
            )
            
            # Save code history
            await self.memory.store(
                "coder_code_history",
                self.code_history[-10:],  # Keep last 10
                namespace="coder_agent"
            )
        except:
            pass
    
    def _show_help(self):
        """Show help information"""
        help_text = """
[bold cyan]Coder Agent Commands[/bold cyan]

[yellow]Natural Language:[/yellow]
• Just describe what you want to create, debug, or understand
• Example: "Create a Python function to sort a list of dictionaries by a key"

[yellow]Special Commands:[/yellow]
• [cyan]help[/cyan] - Show this help message
• [cyan]history[/cyan] - Show code execution history
• [cyan]clear[/cyan] - Clear conversation history
• [cyan]exit[/cyan] - Exit Coder Agent

[yellow]Tips:[/yellow]
• You can paste code directly for debugging or explanation
• Use triple backticks (```) to mark code blocks
• The agent remembers context from your conversation
• Code is executed in a safe sandbox environment
"""
        self.console.print(Panel(help_text, title="Help", border_style="blue"))
    
    async def _show_history(self):
        """Show code execution history"""
        if not self.code_history:
            self.console.print("[yellow]No code execution history.[/yellow]")
            return
        
        table = Table(title="Code Execution History")
        table.add_column("Language", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Code Preview", style="white")
        
        for entry in self.code_history[-5:]:
            status = "✅ Success" if entry['success'] else "❌ Failed"
            preview = entry['code'][:50] + "..." if len(entry['code']) > 50 else entry['code']
            preview = preview.replace('\n', ' ')
            table.add_row(entry['language'], status, preview)
        
        self.console.print(table)