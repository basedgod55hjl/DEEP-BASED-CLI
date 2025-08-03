# DEEP-CLI Enhancement Implementation Guide

This guide provides detailed implementation steps for adding high-priority features to DEEP-CLI.

## 1. MCP Server Integration

### Overview
Model Context Protocol (MCP) servers enable external tool integration with standardized interfaces.

### Implementation Steps

#### 1.1 Create MCP Client
```python
# mcp_client.py
import asyncio
import json
from typing import Dict, Any, List, Optional
import httpx
from dataclasses import dataclass

@dataclass
class MCPServer:
    name: str
    command: str
    args: List[str]
    env: Optional[Dict[str, str]] = None
    type: str = "stdio"

class MCPClient:
    def __init__(self):
        self.servers: Dict[str, MCPServer] = {}
        self.processes: Dict[str, asyncio.subprocess.Process] = {}
        
    async def register_server(self, name: str, config: Dict[str, Any]):
        """Register an MCP server configuration"""
        server = MCPServer(
            name=name,
            command=config['command'],
            args=config.get('args', []),
            env=config.get('env', {})
        )
        self.servers[name] = server
        
    async def start_server(self, name: str):
        """Start an MCP server process"""
        if name not in self.servers:
            raise ValueError(f"Server {name} not registered")
            
        server = self.servers[name]
        env = {**os.environ, **(server.env or {})}
        
        process = await asyncio.create_subprocess_exec(
            server.command,
            *server.args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env
        )
        
        self.processes[name] = process
        
    async def call_tool(self, server_name: str, tool_name: str, params: Dict[str, Any]):
        """Call a tool on an MCP server"""
        process = self.processes.get(server_name)
        if not process:
            await self.start_server(server_name)
            process = self.processes[server_name]
            
        # Send JSON-RPC request
        request = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": f"tools/{tool_name}",
            "params": params
        }
        
        process.stdin.write(json.dumps(request).encode() + b'\n')
        await process.stdin.drain()
        
        # Read response
        response_line = await process.stdout.readline()
        response = json.loads(response_line.decode())
        
        return response.get('result')
```

#### 1.2 MCP OAuth Support
```python
# mcp_oauth.py
from datetime import datetime, timedelta
import secrets
import webbrowser
from urllib.parse import urlencode

class MCPOAuthProvider:
    def __init__(self, client_id: str, client_secret: str, auth_url: str, token_url: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_url = auth_url
        self.token_url = token_url
        self.tokens: Dict[str, Dict[str, Any]] = {}
        
    async def authenticate(self, server_name: str, scopes: List[str]):
        """OAuth flow for MCP server authentication"""
        state = secrets.token_urlsafe(16)
        
        # Build authorization URL
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'state': state,
            'scope': ' '.join(scopes),
            'redirect_uri': 'http://localhost:8080/callback'
        }
        
        auth_url = f"{self.auth_url}?{urlencode(params)}"
        webbrowser.open(auth_url)
        
        # Start local server to receive callback
        code = await self._wait_for_callback(state)
        
        # Exchange code for token
        token = await self._exchange_code(code)
        self.tokens[server_name] = {
            'access_token': token['access_token'],
            'expires_at': datetime.now() + timedelta(seconds=token['expires_in'])
        }
        
    async def get_token(self, server_name: str) -> str:
        """Get valid access token for server"""
        token_data = self.tokens.get(server_name)
        if not token_data:
            raise ValueError(f"No token for {server_name}")
            
        if datetime.now() >= token_data['expires_at']:
            # Token expired, refresh needed
            await self.refresh_token(server_name)
            
        return self.tokens[server_name]['access_token']
```

#### 1.3 Integration with DeepSeek CLI
```python
# Update deepseek_cli.py
class DeepSeekCLI:
    def __init__(self):
        # ... existing init code ...
        self.mcp_client = MCPClient()
        self.oauth_provider = MCPOAuthProvider(
            client_id=os.getenv('MCP_CLIENT_ID'),
            client_secret=os.getenv('MCP_CLIENT_SECRET'),
            auth_url=os.getenv('MCP_AUTH_URL'),
            token_url=os.getenv('MCP_TOKEN_URL')
        )
        
    async def load_mcp_config(self):
        """Load MCP server configurations from config file"""
        config_path = Path.home() / '.deepseek' / 'mcp_servers.json'
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
                
            for name, server_config in config.items():
                await self.mcp_client.register_server(name, server_config)
                
    async def execute_mcp_tool(self, server: str, tool: str, params: Dict[str, Any]):
        """Execute MCP tool with authentication if needed"""
        try:
            # Check if server needs auth
            if server in self.oauth_provider.tokens:
                token = await self.oauth_provider.get_token(server)
                params['_auth_token'] = token
                
            result = await self.mcp_client.call_tool(server, tool, params)
            return result
        except Exception as e:
            console.print(f"[red]MCP Error: {str(e)}[/red]")
            return None
```

## 2. Slash Command System

### Implementation

#### 2.1 Command Registry
```python
# commands/command_registry.py
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import re

class Command(ABC):
    """Base class for all commands"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass
        
    @property
    @abstractmethod
    def description(self) -> str:
        pass
        
    @property
    def aliases(self) -> List[str]:
        return []
        
    @abstractmethod
    async def execute(self, args: List[str], context: Dict[str, Any]) -> str:
        pass

class CommandRegistry:
    def __init__(self):
        self.commands: Dict[str, Command] = {}
        self.aliases: Dict[str, str] = {}
        
    def register(self, command: Command):
        """Register a command and its aliases"""
        self.commands[command.name] = command
        
        # Register aliases
        for alias in command.aliases:
            self.aliases[alias] = command.name
            
    def parse_command(self, input_str: str) -> tuple[Optional[str], List[str]]:
        """Parse command string into command name and arguments"""
        # Pattern: /command:subcommand arg1 arg2 --flag value
        pattern = r'^/(\w+(?::\w+)?)\s*(.*)?$'
        match = re.match(pattern, input_str)
        
        if not match:
            return None, []
            
        command_name = match.group(1)
        args_str = match.group(2) or ''
        
        # Parse arguments (simple implementation)
        args = args_str.split() if args_str else []
        
        # Resolve aliases
        if command_name in self.aliases:
            command_name = self.aliases[command_name]
            
        return command_name, args
        
    async def execute(self, input_str: str, context: Dict[str, Any]) -> Optional[str]:
        """Execute a command from input string"""
        command_name, args = self.parse_command(input_str)
        
        if not command_name or command_name not in self.commands:
            return None
            
        command = self.commands[command_name]
        return await command.execute(args, context)
```

#### 2.2 Implement Commands
```python
# commands/implement_command.py
class ImplementCommand(Command):
    @property
    def name(self) -> str:
        return "deep:implement"
        
    @property
    def description(self) -> str:
        return "Implement a feature or functionality"
        
    @property
    def aliases(self) -> List[str]:
        return ["impl", "build"]
        
    async def execute(self, args: List[str], context: Dict[str, Any]) -> str:
        if not args:
            return "Usage: /deep:implement <feature_description>"
            
        feature_description = ' '.join(args)
        
        # Create implementation prompt
        prompt = f"""
        As an expert software engineer, implement the following feature:
        
        Feature: {feature_description}
        
        Context:
        - Current directory: {context.get('cwd', '.')}
        - Project type: {context.get('project_type', 'unknown')}
        
        Please provide:
        1. Implementation plan
        2. Code implementation
        3. Tests if applicable
        """
        
        # Use existing AI client to generate implementation
        response = await context['ai_client'].generate(prompt)
        
        return response

# commands/analyze_command.py
class AnalyzeCommand(Command):
    @property
    def name(self) -> str:
        return "deep:analyze"
        
    @property
    def description(self) -> str:
        return "Analyze code or system design"
        
    async def execute(self, args: List[str], context: Dict[str, Any]) -> str:
        analysis_type = args[0] if args else "general"
        
        prompts = {
            "security": "Perform a security analysis of the codebase",
            "performance": "Analyze performance bottlenecks",
            "architecture": "Analyze the system architecture",
            "general": "Provide a general code analysis"
        }
        
        prompt = prompts.get(analysis_type, prompts["general"])
        
        # Include relevant files in context
        files_to_analyze = context.get('files', [])
        if files_to_analyze:
            prompt += f"\n\nFiles to analyze: {', '.join(files_to_analyze)}"
            
        response = await context['ai_client'].generate(prompt)
        return response
```

#### 2.3 Integrate with Main CLI
```python
# Update deepseek_cli.py
class DeepSeekCLI:
    def __init__(self):
        # ... existing init code ...
        self.command_registry = CommandRegistry()
        self._register_commands()
        
    def _register_commands(self):
        """Register all available commands"""
        from commands import (
            ImplementCommand, AnalyzeCommand, DesignCommand,
            TestCommand, DocumentCommand, ReviewCommand
        )
        
        commands = [
            ImplementCommand(),
            AnalyzeCommand(),
            DesignCommand(),
            TestCommand(),
            DocumentCommand(),
            ReviewCommand(),
        ]
        
        for command in commands:
            self.command_registry.register(command)
            
    async def process_input(self, user_input: str):
        """Process user input, checking for commands first"""
        # Check if it's a command
        if user_input.startswith('/'):
            context = {
                'ai_client': self.client,
                'cwd': os.getcwd(),
                'project_type': self.detect_project_type(),
                'files': self.get_context_files()
            }
            
            result = await self.command_registry.execute(user_input, context)
            if result:
                console.print(Panel(result, title="Command Result", border_style="green"))
                return
            else:
                console.print("[yellow]Unknown command. Type /help for available commands.[/yellow]")
                return
                
        # ... existing chat processing ...
```

## 3. SQLite Memory System

### Implementation

#### 3.1 Memory Database Schema
```python
# memory/schema.py
MEMORY_SCHEMA = """
CREATE TABLE IF NOT EXISTS memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    namespace TEXT DEFAULT 'default',
    embedding BLOB,
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    access_count INTEGER DEFAULT 0,
    UNIQUE(key, namespace)
);

CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE NOT NULL,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    summary TEXT,
    metadata TEXT
);

CREATE TABLE IF NOT EXISTS contexts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    context_type TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

CREATE TABLE IF NOT EXISTS patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_name TEXT UNIQUE NOT NULL,
    pattern_data TEXT NOT NULL,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    last_used TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_memories_namespace ON memories(namespace);
CREATE INDEX IF NOT EXISTS idx_memories_key ON memories(key);
CREATE INDEX IF NOT EXISTS idx_contexts_session ON contexts(session_id);
"""
```

#### 3.2 Memory Manager
```python
# memory/memory_manager.py
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import numpy as np

class MemoryManager:
    def __init__(self, db_path: str = "~/.deepseek/memory.db"):
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        
    def _init_db(self):
        """Initialize database with schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(MEMORY_SCHEMA)
            conn.commit()
            
    def store(self, key: str, value: Any, namespace: str = "default", 
              metadata: Optional[Dict[str, Any]] = None):
        """Store a memory with optional metadata"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Convert value to JSON if not string
            if not isinstance(value, str):
                value = json.dumps(value)
                
            # Convert metadata to JSON
            metadata_json = json.dumps(metadata) if metadata else None
            
            cursor.execute("""
                INSERT OR REPLACE INTO memories 
                (key, value, namespace, metadata, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (key, value, namespace, metadata_json))
            
            conn.commit()
            
    def recall(self, key: str, namespace: str = "default") -> Optional[Any]:
        """Recall a memory by key"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE memories 
                SET accessed_at = CURRENT_TIMESTAMP,
                    access_count = access_count + 1
                WHERE key = ? AND namespace = ?
            """, (key, namespace))
            
            cursor.execute("""
                SELECT value, metadata FROM memories
                WHERE key = ? AND namespace = ?
            """, (key, namespace))
            
            result = cursor.fetchone()
            if result:
                value, metadata = result
                try:
                    return json.loads(value)
                except:
                    return value
            return None
            
    def search(self, query: str, namespace: Optional[str] = None, 
               limit: int = 10) -> List[Dict[str, Any]]:
        """Search memories by pattern"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if namespace:
                cursor.execute("""
                    SELECT key, value, namespace, metadata, updated_at
                    FROM memories
                    WHERE (key LIKE ? OR value LIKE ?) AND namespace = ?
                    ORDER BY access_count DESC, updated_at DESC
                    LIMIT ?
                """, (f'%{query}%', f'%{query}%', namespace, limit))
            else:
                cursor.execute("""
                    SELECT key, value, namespace, metadata, updated_at
                    FROM memories
                    WHERE key LIKE ? OR value LIKE ?
                    ORDER BY access_count DESC, updated_at DESC
                    LIMIT ?
                """, (f'%{query}%', f'%{query}%', limit))
                
            results = []
            for row in cursor.fetchall():
                key, value, ns, metadata, updated = row
                try:
                    value = json.loads(value)
                except:
                    pass
                    
                results.append({
                    'key': key,
                    'value': value,
                    'namespace': ns,
                    'metadata': json.loads(metadata) if metadata else {},
                    'updated_at': updated
                })
                
            return results
            
    def get_namespaces(self) -> List[str]:
        """Get all namespaces"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT namespace FROM memories")
            return [row[0] for row in cursor.fetchall()]
            
    def export_namespace(self, namespace: str, output_path: str):
        """Export a namespace to JSON file"""
        memories = self.search('', namespace=namespace, limit=10000)
        
        with open(output_path, 'w') as f:
            json.dump({
                'namespace': namespace,
                'exported_at': datetime.now().isoformat(),
                'memories': memories
            }, f, indent=2)
            
    def import_namespace(self, input_path: str, namespace: Optional[str] = None):
        """Import memories from JSON file"""
        with open(input_path) as f:
            data = json.load(f)
            
        target_namespace = namespace or data.get('namespace', 'default')
        
        for memory in data.get('memories', []):
            self.store(
                key=memory['key'],
                value=memory['value'],
                namespace=target_namespace,
                metadata=memory.get('metadata')
            )
```

#### 3.3 Session Management
```python
# memory/session_manager.py
import uuid
from datetime import datetime

class SessionManager:
    def __init__(self, memory_manager: MemoryManager):
        self.memory = memory_manager
        self.current_session_id = None
        
    def start_session(self, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Start a new session"""
        session_id = str(uuid.uuid4())
        
        with sqlite3.connect(self.memory.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO sessions (session_id, metadata)
                VALUES (?, ?)
            """, (session_id, json.dumps(metadata) if metadata else None))
            conn.commit()
            
        self.current_session_id = session_id
        return session_id
        
    def end_session(self, summary: Optional[str] = None):
        """End current session"""
        if not self.current_session_id:
            return
            
        with sqlite3.connect(self.memory.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE sessions
                SET end_time = CURRENT_TIMESTAMP, summary = ?
                WHERE session_id = ?
            """, (summary, self.current_session_id))
            conn.commit()
            
        self.current_session_id = None
        
    def add_context(self, context_type: str, content: Any):
        """Add context to current session"""
        if not self.current_session_id:
            self.start_session()
            
        with sqlite3.connect(self.memory.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO contexts (session_id, context_type, content)
                VALUES (?, ?, ?)
            """, (self.current_session_id, context_type, json.dumps(content)))
            conn.commit()
            
    def get_session_context(self, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all context for a session"""
        target_session = session_id or self.current_session_id
        if not target_session:
            return []
            
        with sqlite3.connect(self.memory.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT context_type, content, timestamp
                FROM contexts
                WHERE session_id = ?
                ORDER BY timestamp
            """, (target_session,))
            
            contexts = []
            for row in cursor.fetchall():
                context_type, content, timestamp = row
                contexts.append({
                    'type': context_type,
                    'content': json.loads(content),
                    'timestamp': timestamp
                })
                
            return contexts
```

#### 3.4 Integration with CLI
```python
# Update deepseek_cli.py
class DeepSeekCLI:
    def __init__(self):
        # ... existing init code ...
        self.memory = MemoryManager()
        self.session = SessionManager(self.memory)
        
    async def start(self):
        """Start CLI session"""
        # Start new session
        session_id = self.session.start_session({
            'start_time': datetime.now().isoformat(),
            'cwd': os.getcwd()
        })
        
        console.print(f"[green]Session started: {session_id[:8]}...[/green]")
        
        # Load previous context if available
        self._load_context()
        
    def _load_context(self):
        """Load relevant context from memory"""
        # Get recent memories from current project
        project_name = Path.cwd().name
        recent_memories = self.memory.search(
            project_name, 
            namespace='projects',
            limit=5
        )
        
        if recent_memories:
            console.print("[yellow]Loading context from previous sessions...[/yellow]")
            for memory in recent_memories:
                self.session.add_context('previous_memory', memory)
                
    async def process_response(self, response: str):
        """Process and store AI response"""
        # Store significant responses in memory
        if len(response) > 100:  # Arbitrary threshold
            key = f"response_{datetime.now().timestamp()}"
            self.memory.store(
                key=key,
                value=response,
                namespace='responses',
                metadata={
                    'session_id': self.session.current_session_id,
                    'timestamp': datetime.now().isoformat()
                }
            )
            
        # Extract and store any code snippets
        code_blocks = self._extract_code_blocks(response)
        for i, block in enumerate(code_blocks):
            self.memory.store(
                key=f"code_{datetime.now().timestamp()}_{i}",
                value=block,
                namespace='code_snippets',
                metadata={
                    'language': block.get('language', 'unknown'),
                    'session_id': self.session.current_session_id
                }
            )
```

## 4. GitHub Integration

### Implementation

#### 4.1 GitHub Client
```python
# github/github_client.py
from github import Github
from github.PullRequest import PullRequest
from github.Issue import Issue
import asyncio

class GitHubIntegration:
    def __init__(self, token: str):
        self.github = Github(token)
        self.repo = None
        
    def set_repo(self, repo_name: str):
        """Set current repository"""
        self.repo = self.github.get_repo(repo_name)
        
    async def analyze_pr(self, pr_number: int) -> Dict[str, Any]:
        """Analyze a pull request"""
        pr = self.repo.get_pull(pr_number)
        
        analysis = {
            'title': pr.title,
            'description': pr.body,
            'files_changed': pr.changed_files,
            'additions': pr.additions,
            'deletions': pr.deletions,
            'commits': pr.commits,
            'files': []
        }
        
        # Analyze changed files
        for file in pr.get_files():
            file_analysis = {
                'filename': file.filename,
                'status': file.status,
                'additions': file.additions,
                'deletions': file.deletions,
                'patch': file.patch
            }
            analysis['files'].append(file_analysis)
            
        return analysis
        
    async def create_review(self, pr_number: int, review_comments: List[Dict[str, Any]]):
        """Create a PR review with comments"""
        pr = self.repo.get_pull(pr_number)
        
        # Create review
        review = pr.create_review(
            body="AI-powered code review",
            event="COMMENT"
        )
        
        # Add inline comments
        for comment in review_comments:
            pr.create_review_comment(
                body=comment['body'],
                path=comment['path'],
                line=comment['line']
            )
            
    async def create_issue(self, title: str, body: str, labels: List[str] = None):
        """Create a new issue"""
        issue = self.repo.create_issue(
            title=title,
            body=body,
            labels=labels or []
        )
        return issue.number
        
    async def update_issue(self, issue_number: int, comment: str):
        """Add comment to issue"""
        issue = self.repo.get_issue(issue_number)
        issue.create_comment(comment)
```

#### 4.2 PR Analysis Command
```python
# commands/github_commands.py
class PRAnalyzeCommand(Command):
    @property
    def name(self) -> str:
        return "deep:pr-analyze"
        
    @property
    def description(self) -> str:
        return "Analyze a GitHub pull request"
        
    async def execute(self, args: List[str], context: Dict[str, Any]) -> str:
        if not args:
            return "Usage: /deep:pr-analyze <pr_number>"
            
        pr_number = int(args[0])
        github = context.get('github_client')
        
        if not github:
            return "GitHub integration not configured"
            
        # Analyze PR
        analysis = await github.analyze_pr(pr_number)
        
        # Generate AI review
        prompt = f"""
        Analyze this pull request and provide a comprehensive review:
        
        Title: {analysis['title']}
        Description: {analysis['description']}
        Files changed: {analysis['files_changed']}
        Lines added: {analysis['additions']}
        Lines deleted: {analysis['deletions']}
        
        Changed files:
        {json.dumps(analysis['files'], indent=2)}
        
        Please provide:
        1. Summary of changes
        2. Code quality assessment
        3. Potential issues or bugs
        4. Suggestions for improvement
        5. Security considerations
        """
        
        review = await context['ai_client'].generate(prompt)
        
        # Store review in memory
        context['memory'].store(
            key=f"pr_review_{pr_number}",
            value={
                'pr_number': pr_number,
                'analysis': analysis,
                'review': review
            },
            namespace='github_reviews'
        )
        
        return review
```

## Usage Examples

### 1. Using MCP Servers
```python
# Example: Configure and use an MCP server
await cli.load_mcp_config()

# Use a web search MCP server
results = await cli.execute_mcp_tool(
    server="web-search",
    tool="search",
    params={"query": "Python async best practices"}
)
```

### 2. Using Slash Commands
```bash
# Implementation command
/deep:implement user authentication system with JWT

# Analysis command
/deep:analyze security

# Design command
/deep:design microservices architecture for e-commerce

# Test command
/deep:test utils.py

# Document command
/deep:document API endpoints
```

### 3. Using Memory System
```python
# Store project context
cli.memory.store(
    key="project_requirements",
    value={"auth": "JWT", "database": "PostgreSQL"},
    namespace="myproject"
)

# Recall context
requirements = cli.memory.recall("project_requirements", "myproject")

# Search memories
results = cli.memory.search("authentication", namespace="myproject")
```

### 4. GitHub Integration
```bash
# Analyze PR
/deep:pr-analyze 123

# Create automated issue
/deep:issue create "Bug: Login fails with special characters"

# Review and comment on PR
/deep:pr-review 123 --detailed
```

## Configuration Files

### MCP Servers Configuration
```json
// ~/.deepseek/mcp_servers.json
{
  "web-search": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-websearch"],
    "env": {
      "GOOGLE_API_KEY": "${GOOGLE_API_KEY}"
    }
  },
  "github": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-github"],
    "env": {
      "GITHUB_TOKEN": "${GITHUB_TOKEN}"
    }
  }
}
```

### Command Aliases
```json
// ~/.deepseek/command_aliases.json
{
  "impl": "deep:implement",
  "ana": "deep:analyze",
  "pr": "deep:pr-analyze",
  "test": "deep:test",
  "doc": "deep:document"
}
```

## Next Steps

1. Implement the basic structure for each feature
2. Add comprehensive error handling
3. Create unit tests for each component
4. Add configuration management
5. Implement progress indicators and feedback
6. Add documentation and help system
7. Create example workflows and templates