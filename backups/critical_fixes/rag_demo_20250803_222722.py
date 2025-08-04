"""
DEEP-CLI RAG Demo
Demonstrates all enhanced features: Vector DB, SQL, RAG, and Deanna persona
"""

import asyncio
from typing import List, Dict, Any, Optional, Tuple

import logging

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from enhanced_based_god_cli import EnhancedBasedGodCLI
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()

async def demo_rag_features() -> None:
    """Demonstrate RAG and enhanced features"""
    
    # Initialize CLI
    cli = EnhancedBasedGodCLI()
    
    console.print(Panel.fit(
        "[bold cyan]DEEP-CLI Enhanced Features Demo[/bold cyan]\n"
        "Featuring: Vector DB, SQL, RAG, and Deanna Persona",
        border_style="cyan"
    ))
    
    # 1. Store knowledge in vector database
    console.logging.info("\n[bold yellow]1. Storing Knowledge in Vector Database[/bold yellow]")
    
    knowledge_texts = [
        "DeepSeek is an advanced AI company that creates powerful language models like DeepSeek-V3 and DeepSeek-R1.",
        "Qdrant is a vector database that enables efficient similarity search and is perfect for RAG applications.",
        "RAG (Retrieval-Augmented Generation) combines retrieval systems with language models for better responses.",
        "Python is a versatile programming language widely used in AI, data science, and web development.",
        "The DEEP-CLI project integrates multiple AI technologies including vector search, SQL databases, and personas."
    ]
    
    # Store knowledge
    result = await cli.tool_manager.execute_tool(
        "rag_pipeline",
        operation="store_knowledge",
        texts=knowledge_texts,
        category="demo_knowledge",
        metadata=[
            {"topic": "AI", "subtopic": "DeepSeek"},
            {"topic": "Database", "subtopic": "Vector"},
            {"topic": "AI", "subtopic": "RAG"},
            {"topic": "Programming", "subtopic": "Python"},
            {"topic": "Project", "subtopic": "DEEP-CLI"}
        ],
        importance=8
    )
    
    if result.success:
        console.logging.info(f"[green]✓ Stored {len(knowledge_texts)} knowledge items[/green]")
    
    # 2. Test Deanna persona
    console.logging.info("\n[bold yellow]2. Interacting with Deanna Persona[/bold yellow]")
    
    # Get Deanna's introduction
    intro_result = await cli.tool_manager.execute_tool(
        "sql_database",
        operation="get_persona",
        name="Deanna"
    )
    
    if intro_result.success:
        persona = intro_result.data['persona']
        console.print(Panel(
            f"[cyan]Name:[/cyan] {persona['name']}\n"
            f"[cyan]Description:[/cyan] {persona['description']}",
            title="Deanna Persona",
            border_style="cyan"
        ))
    
    # 3. Test RAG queries
    console.logging.info("\n[bold yellow]3. Testing RAG Queries[/bold yellow]")
    
    test_queries = [
        "What is DeepSeek and what models do they offer?",
        "How does RAG work with vector databases?",
        "Tell me about the DEEP-CLI project features"
    ]
    
    for query in test_queries:
        console.logging.info(f"\n[cyan]Query:[/cyan] {query}")
        
        # Execute RAG query with Deanna persona
        response = await cli.chat(query)
        
        console.print(Panel(
            Markdown(response),
            title="Deanna's Response",
            border_style="green"
        ))
        
        # Small delay between queries
        await asyncio.sleep(1)
    
    # 4. Test hybrid search
    console.logging.info("\n[bold yellow]4. Testing Hybrid Search[/bold yellow]")
    
    search_result = await cli.tool_manager.execute_tool(
        "rag_pipeline",
        operation="hybrid_search",
        query="AI language models",
        limit=5
    )
    
    if search_result.success:
        results = search_result.data['results']
        counts = search_result.data['counts']
        
        console.logging.info(f"\n[green]Found {len(results)} results:[/green]")
        console.logging.info(f"  • Vectors: {counts['vectors']}")
        console.logging.info(f"  • Memories: {counts['memories']}")
        console.logging.info(f"  • Conversations: {counts['conversations']}")
        
        for i, result in enumerate(results[:3], 1):
            console.logging.info(f"\n[cyan]{i}. {result['type'].upper()} (Score: {result['score']:.3f})[/cyan]")
            console.logging.info(f"   {result['text'][:100]}...")
    
    # 5. Store and retrieve conversation with context
    console.logging.info("\n[bold yellow]5. Context-Aware Conversation[/bold yellow]")
    
    # Have a multi-turn conversation
    conversation = [
        "Can you explain what makes DEEP-CLI special?",
        "How does it integrate with DeepSeek models?",
        "What are the main components of the RAG pipeline?"
    ]
    
    session_id = cli.session_data["session_id"]
    
    for turn, question in enumerate(conversation, 1):
        console.logging.info(f"\n[cyan]Turn {turn}:[/cyan] {question}")
        
        response = await cli.chat(question)
        
        console.print(Panel(
            Markdown(response[:300] + "..." if len(response) > 300 else response),
            title=f"Response {turn}",
            border_style="green"
        ))
        
        await asyncio.sleep(1)
    
    # 6. Show analytics
    console.logging.info("\n[bold yellow]6. Analytics and Statistics[/bold yellow]")
    
    # Get analytics
    analytics_result = await cli.tool_manager.execute_tool(
        "sql_database",
        operation="get_analytics",
        days=1
    )
    
    if analytics_result.success:
        summary = analytics_result.data['summary']
        console.logging.info("\n[green]Event Summary:[/green]")
        for event_type, count in summary.items():
            console.logging.info(f"  • {event_type}: {count}")
    
    # Show memory stats
    cli.show_memory_stats()
    
    # Show tool usage
    cli.show_tools()
    
    console.logging.info("\n[bold green]✨ Demo Complete![/bold green]")
    console.logging.info("\nThe DEEP-CLI now features:")
    console.logging.info("  • Vector database for semantic search")
    console.logging.info("  • SQL database for structured data")
    console.logging.info("  • RAG pipeline for enhanced responses")
    console.logging.info("  • Deanna persona for consistent interactions")
    console.logging.info("  • Context-aware conversations")
    console.logging.info("  • Comprehensive analytics")

async def main() -> None:
    """Main demo function"""
    try:
        await demo_rag_features()
    except KeyboardInterrupt:
        console.logging.info("\n[yellow]Demo interrupted by user[/yellow]")
    except Exception as e:
        console.logging.info(f"\n[red]Error: {str(e)}[/red]")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
<<<<<<< Current (Your changes)
=======
 
>>>>>>> d56552d76c9eaadc6392dfb8e6c57491de43475f
=======
>>>>>>> Incoming (Background Agent changes)
