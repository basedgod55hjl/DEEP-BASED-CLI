"""
Base command class and command registry
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import re

from ..core.models import CommandContext


class Command(ABC):
    """Base class for all commands"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Command name (e.g., 'deep:implement')"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Command description"""
        pass
    
    @property
    def aliases(self) -> List[str]:
        """Command aliases"""
        return []
    
    @property
    def usage(self) -> str:
        """Usage information"""
        return f"/{self.name} <args>"
    
    @abstractmethod
    async def execute(self, context: CommandContext) -> str:
        """Execute the command"""
        pass
    
    def validate_args(self, args: List[str]) -> bool:
        """Validate command arguments"""
        return True


class CommandRegistry:
    """Registry for managing commands"""
    
    def __init__(self):
        self.commands: Dict[str, Command] = {}
        self.aliases: Dict[str, str] = {}
    
    def register(self, command: Command) -> None:
        """Register a command and its aliases"""
        self.commands[command.name] = command
        
        # Register aliases
        for alias in command.aliases:
            self.aliases[alias] = command.name
    
    def unregister(self, name: str) -> None:
        """Unregister a command"""
        if name in self.commands:
            command = self.commands[name]
            # Remove aliases
            for alias in command.aliases:
                self.aliases.pop(alias, None)
            # Remove command
            del self.commands[name]
    
    def get(self, name: str) -> Optional[Command]:
        """Get a command by name or alias"""
        # Check direct name
        if name in self.commands:
            return self.commands[name]
        
        # Check aliases
        if name in self.aliases:
            return self.commands[self.aliases[name]]
        
        return None
    
    def list_commands(self) -> List[Command]:
        """List all registered commands"""
        return list(self.commands.values())
    
    def parse_command(self, input_str: str) -> tuple[Optional[str], List[str]]:
        """
        Parse command string into command name and arguments
        
        Returns:
            Tuple of (command_name, arguments) or (None, []) if not a command
        """
        # Check if it's a command (starts with /)
        if not input_str.startswith('/'):
            return None, []
        
        # Remove leading slash
        input_str = input_str[1:]
        
        # Pattern: command:subcommand arg1 arg2 --flag value
        pattern = r'^(\w+(?::\w+)?)\s*(.*)?$'
        match = re.match(pattern, input_str)
        
        if not match:
            return None, []
        
        command_name = match.group(1)
        args_str = match.group(2) or ''
        
        # Parse arguments (simple split for now)
        args = args_str.split() if args_str else []
        
        return command_name, args
    
    async def execute(self, input_str: str, context: CommandContext) -> Optional[str]:
        """
        Execute a command from input string
        
        Returns:
            Command output or None if not a command
        """
        command_name, args = self.parse_command(input_str)
        
        if not command_name:
            return None
        
        command = self.get(command_name)
        if not command:
            return f"Unknown command: /{command_name}. Type /help for available commands."
        
        # Update context with parsed args
        context.args = args
        
        # Validate arguments
        if not command.validate_args(args):
            return f"Invalid arguments. Usage: {command.usage}"
        
        # Execute command
        try:
            return await command.execute(context)
        except Exception as e:
            return f"Command failed: {str(e)}"


# Global command registry
command_registry = CommandRegistry()