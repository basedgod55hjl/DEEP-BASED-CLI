"""
Implementation command for creating features
"""

from typing import List

from .base import Command
from ..core.models import CommandContext, CommandType, PersonaType, PERSONAS


class ImplementCommand(Command):
    """Command for implementing features and functionality"""
    
    @property
    def name(self) -> str:
        return "deep:implement"
    
    @property
    def description(self) -> str:
        return "Implement a feature or functionality"
    
    @property
    def aliases(self) -> List[str]:
        return ["impl", "build", "create"]
    
    @property
    def usage(self) -> str:
        return "/deep:implement <feature_description> [--persona <persona>]"
    
    def validate_args(self, args: List[str]) -> bool:
        """Ensure at least one argument is provided"""
        return len(args) > 0
    
    async def execute(self, context: CommandContext) -> str:
        """Execute the implementation command"""
        # Extract feature description
        feature_args = []
        persona_type = None
        
        # Parse arguments
        i = 0
        while i < len(context.args):
            if context.args[i] == "--persona" and i + 1 < len(context.args):
                persona_name = context.args[i + 1].upper()
                try:
                    persona_type = PersonaType[persona_name]
                except KeyError:
                    return f"Unknown persona: {context.args[i + 1]}. Available: {', '.join([p.value for p in PersonaType])}"
                i += 2
            else:
                feature_args.append(context.args[i])
                i += 1
        
        feature_description = " ".join(feature_args)
        
        # Select appropriate persona
        if not persona_type:
            # Auto-select based on keywords
            if any(word in feature_description.lower() for word in ["ui", "frontend", "react", "vue"]):
                persona_type = PersonaType.FRONTEND
            elif any(word in feature_description.lower() for word in ["api", "backend", "database", "server"]):
                persona_type = PersonaType.BACKEND
            elif any(word in feature_description.lower() for word in ["security", "auth", "encryption"]):
                persona_type = PersonaType.SECURITY
            else:
                persona_type = PersonaType.ARCHITECT
        
        persona = PERSONAS[persona_type]
        
        # Build the prompt
        prompt = f"""{persona.prompt_prefix}I need to implement the following feature:

Feature: {feature_description}

Context:
- Current directory: {context.cwd}
- Project type: {context.project_type or 'unknown'}
{f"- Related files: {', '.join(context.files)}" if context.files else ""}

Please provide:
1. Implementation plan with clear steps
2. Complete code implementation
3. Tests if applicable
4. Documentation updates
5. Any necessary configuration changes

Focus on {persona.style} approach and ensure the solution follows best practices."""
        
        # Return the prompt for now (in full implementation, this would call the AI client)
        return f"🎯 Using {persona.name} persona\n\n📋 Implementation request:\n{prompt}"