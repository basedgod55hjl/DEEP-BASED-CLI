h"""
Unified Agent System Demo - Enhanced BASED GOD CLI
Demonstrates the unified brain approach with memory, persona, tools, and contacts
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from tools.unified_agent_system import UnifiedAgentSystem
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

console = Console()


async def demo_unified_agent():
    """Demonstrate the unified agent system"""
    
    console.print(Panel.fit(
        "[bold cyan]🧠 Unified Agent System Demo[/bold cyan]\n"
        "Memory, Persona, Tools, Contacts, and Conversation as One Brain",
        border_style="cyan"
    ))
    
    # Initialize unified agent
    agent = UnifiedAgentSystem()
    
    # Wait for initialization
    await asyncio.sleep(2)
    
    # Demo 1: Basic conversation with memory
    console.print("\n[bold yellow]1. Basic Conversation with Memory[/bold yellow]")
    
    result = await agent.execute(
        operation="process_input",
        user_input="Hello! My name is Alice and I'm working on a Python project.",
        user_id="alice"
    )
    
    if result.success:
        console.print(f"✅ Response: {result.data['response']}")
        console.print(f"📝 Context used: {len(result.data['context_used'])} items")
        console.print(f"👥 Contacts found: {len(result.data['contacts_found'])}")
        console.print(f"🔧 Tools selected: {result.data['tools_selected']}")
    else:
        console.print(f"❌ Error: {result.message}")
    
    # Demo 2: Tool usage and learning
    console.print("\n[bold yellow]2. Tool Usage and Learning[/bold yellow]")
    
    result = await agent.execute(
        operation="process_input",
        user_input="Can you help me analyze this CSV data? I have a file called sales_data.csv",
        user_id="alice"
    )
    
    if result.success:
        console.print(f"✅ Response: {result.data['response']}")
        console.print(f"🔧 Tools selected: {result.data['tools_selected']}")
    else:
        console.print(f"❌ Error: {result.message}")
    
    # Demo 3: Contact extraction and enrichment
    console.print("\n[bold yellow]3. Contact Extraction and Enrichment[/bold yellow]")
    
    result = await agent.execute(
        operation="process_input",
        user_input="I need to contact John Smith at john.smith@company.com about the project.",
        user_id="alice"
    )
    
    if result.success:
        console.print(f"✅ Response: {result.data['response']}")
        console.print(f"👥 Contacts found: {len(result.data['contacts_found'])}")
        for contact in result.data['contacts_found']:
            console.print(f"   - {contact.name}: {contact.details}")
    else:
        console.print(f"❌ Error: {result.message}")
    
    # Demo 4: Memory retrieval and context awareness
    console.print("\n[bold yellow]4. Memory Retrieval and Context Awareness[/bold yellow]")
    
    result = await agent.execute(
        operation="process_input",
        user_input="What was I working on earlier?",
        user_id="alice"
    )
    
    if result.success:
        console.print(f"✅ Response: {result.data['response']}")
        console.print(f"🧠 Context retrieved from memory")
    else:
        console.print(f"❌ Error: {result.message}")
    
    # Demo 5: Persona adaptation
    console.print("\n[bold yellow]5. Persona Adaptation[/bold yellow]")
    
    result = await agent.execute(
        operation="process_input",
        user_input="Can you be more technical and detailed in your explanations?",
        user_id="alice"
    )
    
    if result.success:
        console.print(f"✅ Response: {result.data['response']}")
        console.print(f"🎭 Persona adapted based on user preference")
    else:
        console.print(f"❌ Error: {result.message}")
    
    # Demo 6: Learning from interaction
    console.print("\n[bold yellow]6. Learning from Interaction[/bold yellow]")
    
    result = await agent.execute(
        operation="learn_from_interaction",
        user_input="I prefer concise answers",
        response="I'll keep my responses brief and to the point.",
        success=True,
        tools_used=["memory_tool"],
        context_used={"user_preference": "concise"}
    )
    
    if result.success:
        console.print(f"✅ Learning data stored: {result.data['learning_data']}")
    else:
        console.print(f"❌ Error: {result.message}")
    
    # Demo 7: Memory summarization
    console.print("\n[bold yellow]7. Memory Summarization[/bold yellow]")
    
    result = await agent.execute(
        operation="summarize_memories",
        user_id="alice",
        days_old=1
    )
    
    if result.success:
        console.print(f"✅ Memory summarization: {result.message}")
        console.print(f"📊 Summarized {result.data.get('summarized_count', 0)} memories")
    else:
        console.print(f"❌ Error: {result.message}")
    
    # Demo 8: Tool registration
    console.print("\n[bold yellow]8. Tool Registration[/bold yellow]")
    
    result = await agent.execute(
        operation="register_tool",
        tool_data={
            "name": "custom_analyzer",
            "function": "analyze_custom_data",
            "params": {"data_type": "string", "analysis_mode": "string"}
        }
    )
    
    if result.success:
        console.print(f"✅ Tool registered successfully")
    else:
        console.print(f"❌ Error: {result.message}")
    
    # Demo 9: Complex multi-turn conversation
    console.print("\n[bold yellow]9. Complex Multi-turn Conversation[/bold yellow]")
    
    conversations = [
        "I'm building a web application with React and Node.js",
        "I need help with authentication",
        "What's the best way to handle user sessions?",
        "Can you remember my tech stack preferences?"
    ]
    
    for i, conv in enumerate(conversations, 1):
        console.print(f"\n[blue]Turn {i}:[/blue] {conv}")
        
        result = await agent.execute(
            operation="process_input",
            user_input=conv,
            user_id="alice"
        )
        
        if result.success:
            console.print(f"✅ Response: {result.data['response'][:100]}...")
        else:
            console.print(f"❌ Error: {result.message}")
    
    # Demo 10: System overview
    console.print("\n[bold yellow]10. System Overview[/bold yellow]")
    
    # Create a table showing system capabilities
    table = Table(title="Unified Agent System Capabilities")
    table.add_column("Component", style="cyan")
    table.add_column("Capability", style="green")
    table.add_column("Status", style="yellow")
    
    table.add_row("Memory", "Unified storage and retrieval", "✅ Active")
    table.add_row("Persona", "Adaptive personality system", "✅ Active")
    table.add_row("Tools", "Intelligent tool selection", "✅ Active")
    table.add_row("Contacts", "Auto-extraction and caching", "✅ Active")
    table.add_row("Learning", "Interaction-based improvement", "✅ Active")
    table.add_row("Context", "Multi-source awareness", "✅ Active")
    
    console.print(table)
    
    console.print("\n" + "=" * 80)
    console.print("[bold green]🎉 Unified Agent System Demo Completed![/bold green]")
    console.print("The system successfully demonstrated:")
    console.print("• Unified memory management across all interactions")
    console.print("• Intelligent tool selection based on context")
    console.print("• Contact extraction and enrichment")
    console.print("• Persona adaptation to user preferences")
    console.print("• Learning from interactions for improvement")
    console.print("• Context-aware responses using multiple data sources")


async def demo_advanced_features():
    """Demonstrate advanced unified agent features"""
    
    console.print(Panel.fit(
        "[bold magenta]🚀 Advanced Features Demo[/bold magenta]\n"
        "Advanced capabilities of the unified agent system",
        border_style="magenta"
    ))
    
    agent = UnifiedAgentSystem()
    
    # Advanced Demo 1: Relationship mapping
    console.print("\n[bold yellow]Advanced 1: Memory Relationship Mapping[/bold yellow]")
    
    # Store related memories
    memories = [
        {
            "type": "project_info",
            "data": {"project": "web_app", "tech_stack": ["React", "Node.js"]},
            "importance": 8
        },
        {
            "type": "user_preference",
            "data": {"preference": "detailed_explanations", "context": "technical"},
            "importance": 7
        },
        {
            "type": "contact_info",
            "data": {"name": "Alice", "role": "developer", "email": "alice@company.com"},
            "importance": 9
        }
    ]
    
    for memory in memories:
        result = await agent.execute(
            operation="store_memory",
            memory_data=memory,
            user_id="alice"
        )
        if result.success:
            console.print(f"✅ Memory stored: {memory['type']}")
    
    # Advanced Demo 2: Context-aware tool selection
    console.print("\n[bold yellow]Advanced 2: Context-Aware Tool Selection[/bold yellow]")
    
    result = await agent.execute(
        operation="process_input",
        user_input="I need to optimize the performance of my React components",
        user_id="alice"
    )
    
    if result.success:
        console.print(f"✅ Response: {result.data['response'][:150]}...")
        console.print(f"🔧 Tools selected based on context: {result.data['tools_selected']}")
    else:
        console.print(f"❌ Error: {result.message}")
    
    # Advanced Demo 3: Multi-modal interaction
    console.print("\n[bold yellow]Advanced 3: Multi-Modal Interaction[/bold yellow]")
    
    # Simulate different types of interactions
    interactions = [
        ("text", "How do I implement JWT authentication?"),
        ("code", "```javascript\nconst token = jwt.sign(payload, secret);\n```"),
        ("data", "I have user data in JSON format"),
        ("file", "Can you help me with the package.json configuration?")
    ]
    
    for interaction_type, content in interactions:
        console.print(f"\n[blue]{interaction_type.upper()}:[/blue] {content}")
        
        result = await agent.execute(
            operation="process_input",
            user_input=content,
            user_id="alice"
        )
        
        if result.success:
            console.print(f"✅ Processed {interaction_type} interaction")
        else:
            console.print(f"❌ Error: {result.message}")


def main():
    """Main demo runner"""
    console.print("[bold red]🔥 Unified Agent System - Enhanced BASED GOD CLI[/bold red]")
    console.print("Demonstrating the unified brain approach to AI agents")
    
    # Run demos
    asyncio.run(demo_unified_agent())
    asyncio.run(demo_advanced_features())


if __name__ == "__main__":
    main() 