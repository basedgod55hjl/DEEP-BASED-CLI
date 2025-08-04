"""
Node.js Bridge Tool - Enhanced BASED GOD CLI
Bridge to Node.js DeepSeek agents for advanced capabilities
"""

import subprocess
import logging

import json
import asyncio
import os
from typing import Any, Dict, List, Optional
from datetime import datetime

from .base_tool import BaseTool, ToolResponse, ToolStatus

class NodeJSBridgeTool(BaseTool):
    """Bridge tool for executing Node.js agents from Python CLI"""
    
    def __init__(self) -> Any:
        super().__init__(
            name="Node.js Bridge",
            description="Bridge to Node.js DeepSeek agents for advanced automation, scraping, and security tasks",
            capabilities=[
                "Execute Node.js DeepSeek agents",
                "Stealth web scraping with Puppeteer",
                "Advanced automation scripts",
                "Security reconnaissance tools",
                "Multi-threaded task processing",
                "Continue CLI integration"
            ]
        )
        self.node_scripts_dir = "nodejs_agents"
        self._ensure_node_environment()
    
    def _ensure_node_environment(self) -> Any:
        """Ensure Node.js environment is available"""
        try:
            result = subprocess.run(
                ["node", "--version"], 
                capture_output=True, 
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                self.node_available = True
                logging.info(f"✅ Node.js detected: {result.stdout.strip()}")
            else:
                self.node_available = False
                logging.info("❌ Node.js not found - install Node.js to use bridge features")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.node_available = False
            logging.info("❌ Node.js not available - install Node.js to use bridge features")
    
    def get_schema(self) -> Dict[str, Any]:
        """Get the tool's parameter schema"""
        return {
            "type": "object",
            "properties": {
                "script_path": {
                    "type": "string",
                    "description": "Path to the Node.js script to execute"
                },
                "agent_type": {
                    "type": "string",
                    "description": "Type of predefined agent to run",
                    "enum": ["scraper", "chat", "analyzer", "automation", "security", "recon"]
                },
                "args": {
                    "type": "object",
                    "description": "Arguments to pass to the Node.js script"
                },
                "timeout": {
                    "type": "number",
                    "description": "Execution timeout in seconds",
                    "default": 60
                }
            },
            "oneOf": [
                {"required": ["script_path"]},
                {"required": ["agent_type"]}
            ]
        }
    
    async def execute(self, **kwargs) -> ToolResponse:
        """Execute Node.js agent script"""
        
        if not self.node_available:
            return ToolResponse(
                success=False,
                message="Node.js not available - please install Node.js to use bridge features",
                status=ToolStatus.FAILED
            )
        
        script_path = kwargs.get("script_path")
        agent_type = kwargs.get("agent_type", "chat")
        args = kwargs.get("args", {})
        timeout = kwargs.get("timeout", 60)
        
        if not script_path and not agent_type:
            return ToolResponse(
                success=False,
                message="Either script_path or agent_type parameter is required",
                status=ToolStatus.FAILED
            )
        
        start_time = datetime.now()
        
        try:
            # If agent_type is provided, use predefined scripts
            if agent_type and not script_path:
                script_path = self._get_agent_script(agent_type)
            
            # Prepare the command
            cmd = ["node", script_path]
            
            # Add arguments as JSON string
            if args:
                cmd.append(json.dumps(args))
            
            # Execute the Node.js script
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=os.path.dirname(script_path) if os.path.dirname(script_path) else "."
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                return ToolResponse(
                    success=False,
                    message=f"Node.js script timed out after {timeout} seconds",
                    status=ToolStatus.FAILED,
                    execution_time=(datetime.now() - start_time).total_seconds()
                )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            if process.returncode == 0:
                # Try to parse JSON output
                try:
                    result = json.loads(stdout.decode())
                    return ToolResponse(
                        success=True,
                        message="Node.js agent executed successfully",
                        data=result,
                        status=ToolStatus.COMPLETED,
                        execution_time=execution_time,
                        metadata={
                            "script_path": script_path,
                            "agent_type": agent_type,
                            "stdout_raw": stdout.decode(),
                            "stderr": stderr.decode() if stderr else None
                        }
                    )
                except json.JSONDecodeError:
                    # Return raw stdout if not JSON
                    return ToolResponse(
                        success=True,
                        message="Node.js agent executed successfully",
                        data={"output": stdout.decode()},
                        status=ToolStatus.COMPLETED,
                        execution_time=execution_time,
                        metadata={
                            "script_path": script_path,
                            "agent_type": agent_type,
                            "stderr": stderr.decode() if stderr else None
                        }
                    )
            else:
                return ToolResponse(
                    success=False,
                    message=f"Node.js agent failed with exit code {process.returncode}",
                    data={"stderr": stderr.decode(), "stdout": stdout.decode()},
                    status=ToolStatus.FAILED,
                    execution_time=execution_time
                )
        
        except Exception as e:
            return ToolResponse(
                success=False,
                message=f"Error executing Node.js agent: {str(e)}",
                status=ToolStatus.FAILED,
                execution_time=(datetime.now() - start_time).total_seconds()
            )
    
    def _get_agent_script(self, agent_type: str) -> str:
        """Get predefined agent script path"""
        agent_scripts = {
            "scraper": "stealth-scraper.js",
            "chat": "deepseek-chat.js", 
            "analyzer": "data-analyzer.js",
            "automation": "task-automation.js",
            "security": "security-scanner.js",
            "recon": "reconnaissance.js"
        }
        
        script_name = agent_scripts.get(agent_type, "deepseek-chat.js")
        return os.path.join(self.node_scripts_dir, script_name)
    
    async def create_agent_script(self, agent_type: str, script_content: str) -> ToolResponse:
        """Create a new Node.js agent script"""
        
        try:
            # Ensure scripts directory exists
            os.makedirs(self.node_scripts_dir, exist_ok=True)
            
            script_path = self._get_agent_script(agent_type)
            
            # Write the script content
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            return ToolResponse(
                success=True,
                message=f"Agent script created: {script_path}",
                data={"script_path": script_path, "agent_type": agent_type},
                status=ToolStatus.COMPLETED
            )
        
        except Exception as e:
            return ToolResponse(
                success=False,
                message=f"Error creating agent script: {str(e)}",
                status=ToolStatus.FAILED
            )
    
    async def list_agent_scripts(self) -> ToolResponse:
        """List available Node.js agent scripts"""
        
        try:
            if not os.path.exists(self.node_scripts_dir):
                return ToolResponse(
                    success=True,
                    message="No agent scripts directory found",
                    data={"scripts": []},
                    status=ToolStatus.COMPLETED
                )
            
            scripts = []
            for file in os.listdir(self.node_scripts_dir):
                if file.endswith('.js'):
                    script_path = os.path.join(self.node_scripts_dir, file)
                    stats = os.stat(script_path)
                    scripts.append({
                        "name": file,
                        "path": script_path,
                        "size": stats.st_size,
                        "modified": datetime.fromtimestamp(stats.st_mtime).isoformat()
                    })
            
            return ToolResponse(
                success=True,
                message=f"Found {len(scripts)} agent scripts",
                data={"scripts": scripts},
                status=ToolStatus.COMPLETED
            )
        
        except Exception as e:
            return ToolResponse(
                success=False,
                message=f"Error listing agent scripts: {str(e)}",
                status=ToolStatus.FAILED
            )

# Example usage functions
async def example_stealth_scraper() -> None:
    """Example: Run stealth web scraper"""
    bridge = NodeJSBridgeTool()
    
    result = await bridge.execute(
        agent_type="scraper",
        args={
            "url": "https://example.com",
            "extract_type": "text",
            "stealth": True,
            "user_agents": True
        },
        timeout=30
    )
    
    return result

async def example_security_scan() -> None:
    """Example: Run security reconnaissance"""
    bridge = NodeJSBridgeTool()
    
    result = await bridge.execute(
        agent_type="security",
        args={
            "target": "192.168.1.1",
            "scan_type": "port_scan",
            "ports": "1-1000",
            "stealth": True
        },
        timeout=120
    )
    
    return result

async def example_deepseek_chat() -> None:
    """Example: Chat with DeepSeek via Node.js"""
    bridge = NodeJSBridgeTool()
    
    result = await bridge.execute(
        agent_type="chat",
        args={
            "messages": [
                {"role": "user", "content": "Explain machine learning in simple terms"}
            ],
            "model": "deepseek-chat",
            "temperature": 0.7
        },
        timeout=30
    )
    
    return result