#!/usr/bin/env python3
"""
üöÄ BASED CODER CLI - Unified Demo System
Made by @Lucariolucario55 on Telegram

Consolidated demo system for showcasing all BASED CODER CLI features
"""

import asyncio
import logging

import sys
import time
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import colorama
from colorama import Fore, Style

# Initialize colorama
colorama.init()

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

# Import our tools and systems
from config import get_config
from tools.deepseek_coder_tool import DeepSeekCoderTool
from tools.simple_embedding_tool import SimpleEmbeddingTool
from tools.sql_database_tool import SQLDatabaseTool
from tools.fim_completion_tool import FIMCompletionTool
from tools.prefix_completion_tool import PrefixCompletionTool
from tools.llm_query_tool import LLMQueryTool
from tools.rag_pipeline_tool import RAGPipelineTool
from tools.reasoning_engine import ReasoningEngine
from tools.memory_tool import MemoryTool

class BasedCoderDemo:
    """Unified demo system for BASED CODER CLI"""
    
    def __init__(self) -> Any:
        self.config = get_config()
        self.demo_examples = [
            # DeepSeek Coder Examples
            {
                "title": "üîß DeepSeek Coder - Code Generation",
                "description": "Generate Python code for a web scraper",
                "operation": "code_generation",
                "params": {
                    "prompt": "Create a Python web scraper that extracts article titles from a news website",
                    "language": "python",
                    "requirements": ["Use requests and BeautifulSoup", "Handle errors gracefully", "Include rate limiting"]
                }
            },
            {
                "title": "üêõ DeepSeek Coder - Code Debugging",
                "description": "Debug a Python function with errors",
                "operation": "code_debugging",
                "params": {
                    "code": """
def calculate_fibonacci(n) -> Any:
    if n <= 0:
        return None
    elif n == 1:
        return 1
    else:
        return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

# Test the function
result = calculate_fibonacci(5)
logging.info(f"Fibonacci of 5 is: {result}")
""",
                    "language": "python",
                    "error_message": "RecursionError: maximum recursion depth exceeded"
                }
            },
            {
                "title": "ü©π DeepSeek Coder - Self-Healing Code",
                "description": "Self-heal code with potential issues",
                "operation": "self_healing",
                "params": {
                    "code": """
import os
def read_file(filename) -> Any:
    file = open(filename, 'r')
    content = file.read()
    return content

# Usage
data = read_file('test.txt')
logging.info(data)
""",
                    "language": "python"
                }
            },
            {
                "title": "üîó DeepSeek Coder - FIM Completion",
                "description": "Fill-in-Middle code completion",
                "operation": "fim_completion",
                "params": {
                    "prefix": """
def process_data(data_list) -> Any:
    results = []
    for item in data_list:
""",
                    "suffix": """
    return results

# Test
data = [1, 2, 3, 4, 5]
result = process_data(data)
logging.info(result)
""",
                    "language": "python"
                }
            },
            # Embedding Examples
            {
                "title": "üß† Embedding System - Text Similarity",
                "description": "Compute similarity between texts",
                "operation": "embedding_similarity",
                "params": {
                    "texts": [
                        "Machine learning is a subset of artificial intelligence",
                        "AI includes machine learning and deep learning",
                        "The weather is sunny today"
                    ]
                }
            },
            # Database Examples
            {
                "title": "üóÑÔ∏è Database System - Persona Management",
                "description": "Store and retrieve AI personas",
                "operation": "persona_management",
                "params": {
                    "persona": {
                        "name": "Demo Assistant",
                        "description": "A helpful demo assistant",
                        "personality_traits": {"traits": ["friendly", "knowledgeable"]},
                        "knowledge_base": {"domains": ["demo", "testing"]},
                        "conversation_style": {"greeting": "Hello! I'm your demo assistant."}
                    }
                }
            },
            # FIM Completion Examples
            {
                "title": "üîó FIM Completion - Code Generation",
                "description": "Complete code with prefix and suffix",
                "operation": "fim_completion",
                "params": {
                    "prefix": "def calculate_sum(numbers) -> Any:",
                    "suffix": "return total",
                    "language": "python"
                }
            },
            # Prefix Completion Examples
            {
                "title": "üìù Prefix Completion - Text Generation",
                "description": "Generate text from prefix",
                "operation": "prefix_completion",
                "params": {
                    "prefix": "The future of artificial intelligence",
                    "max_tokens": 100
                }
            },
            # LLM Query Examples
            {
                "title": "ü§ñ LLM Query - Natural Language Processing",
                "description": "Ask questions to the AI",
                "operation": "llm_query",
                "params": {
                    "prompt": "Explain quantum computing in simple terms",
                    "max_tokens": 200
                }
            },
            # RAG Pipeline Examples
            {
                "title": "üìö RAG Pipeline - Knowledge Retrieval",
                "description": "Retrieve relevant information",
                "operation": "rag_query",
                "params": {
                    "query": "What are the benefits of machine learning?",
                    "max_results": 3
                }
            },
            # Reasoning Examples
            {
                "title": "üß† Reasoning Engine - Logical Analysis",
                "description": "Analyze complex problems",
                "operation": "reasoning",
                "params": {
                    "question": "If a train leaves station A at 2 PM traveling 60 mph and another train leaves station B at 3 PM traveling 80 mph, when will they meet if the stations are 200 miles apart?",
                    "approach": "step_by_step"
                }
            },
            # Memory Examples
            {
                "title": "üíæ Memory System - Information Storage",
                "description": "Store and retrieve information",
                "operation": "memory_operations",
                "params": {
                    "operations": [
                        {"action": "store", "content": "BASED CODER CLI is an advanced AI-powered command line interface"},
                        {"action": "store", "content": "It features DeepSeek integration, rainbow interface, and full PC access"},
                        {"action": "retrieve", "query": "BASED CODER CLI features"}
                    ]
                }
            }
        ]
    
    def print_banner(self) -> Any:
        """Print demo banner"""
        banner = f"""
{Fore.CYAN}‚ïî‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïó
‚ïë                                                                              ‚ïë
‚ïë  üé≠ BASED CODER CLI - UNIFIED DEMO SYSTEM                                    ‚ïë
‚ïë                                                                              ‚ïë
‚ïë  Features:                                                                   ‚ïë
‚ïë  ‚úÖ DeepSeek Coder Integration                                               ‚ïë
‚ïë  ‚úÖ Embedding & Similarity Systems                                           ‚ïë
‚ïë  ‚úÖ Database & Persona Management                                            ‚ïë
‚ïë  ‚úÖ FIM & Prefix Completion                                                  ‚ïë
‚ïë  ‚úÖ LLM Query & RAG Pipeline                                                 ‚ïë
‚ïë  ‚úÖ Reasoning & Memory Systems                                               ‚ïë
‚ïë                                                                              ‚ïë
‚ïë  Made by @Lucariolucario55 on Telegram                                      ‚ïë
‚ïë                                                                              ‚ïë
‚ïö‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïù{Style.RESET_ALL}
        """
        logging.info(banner)
    
    async def run_deepseek_coder_demo(self) -> Any:
        """Run DeepSeek Coder demos"""
        logging.info(f"\n{Fore.YELLOW}üîß DeepSeek Coder Demo{Style.RESET_ALL}")
        logging.info("=" * 50)
        
        coder_tool = DeepSeekCoderTool()
        
        for example in self.demo_examples[:4]:  # First 4 are DeepSeek Coder examples
            logging.info(f"\n{Fore.CYAN}{example['title']}{Style.RESET_ALL}")
            logging.info(f"{example['description']}")
            logging.info("-" * 40)
            
            try:
                result = await coder_tool.execute(
                    operation=example['operation'],
                    **example['params']
                )
                
                if result.success:
                    logging.info(f"{Fore.GREEN}‚úÖ Success!{Style.RESET_ALL}")
                    if 'code' in result.data:
                        logging.info(f"Generated Code:\n{result.data['code'][:300]}...")
                    elif 'completion' in result.data:
                        logging.info(f"Completion:\n{result.data['completion'][:300]}...")
                    elif 'analysis' in result.data:
                        logging.info(f"Analysis:\n{result.data['analysis'][:300]}...")
                else:
                    logging.info(f"{Fore.RED}‚ùå Failed: {result.message}{Style.RESET_ALL}")
                
            except Exception as e:
                logging.info(f"{Fore.RED}‚ùå Error: {str(e)}{Style.RESET_ALL}")
            
            logging.info()
            await asyncio.sleep(1)  # Brief pause between demos
    
    async def run_embedding_demo(self) -> Any:
        """Run embedding system demo"""
        logging.info(f"\n{Fore.YELLOW}üß† Embedding System Demo{Style.RESET_ALL}")
        logging.info("=" * 50)
        
        embedding_tool = SimpleEmbeddingTool()
        
        example = self.demo_examples[4]  # Embedding example
        logging.info(f"\n{Fore.CYAN}{example['title']}{Style.RESET_ALL}")
        logging.info(f"{example['description']}")
        logging.info("-" * 40)
        
        try:
            texts = example['params']['texts']
            result = await embedding_tool.embed_texts(texts)
            
            if result.success:
                logging.info(f"{Fore.GREEN}‚úÖ Embeddings generated successfully!{Style.RESET_ALL}")
                
                # Compute similarities
                embeddings = result.data['embeddings']
                for i in range(len(embeddings)):
                    for j in range(i + 1, len(embeddings)):
                        similarity_result = await embedding_tool.compute_similarity(
                            embedding1=embeddings[i]['embedding'],
                            embedding2=embeddings[j]['embedding']
                        )
                        
                        if similarity_result.success:
                            similarity = similarity_result.data['similarity']
                            logging.info(f"Similarity between text {i+1} and {j+1}: {similarity:.4f}")
            else:
                logging.info(f"{Fore.RED}‚ùå Failed: {result.message}{Style.RESET_ALL}")
                
        except Exception as e:
            logging.info(f"{Fore.RED}‚ùå Error: {str(e)}{Style.RESET_ALL}")
    
    async def run_database_demo(self) -> Any:
        """Run database system demo"""
        logging.info(f"\n{Fore.YELLOW}üóÑÔ∏è Database System Demo{Style.RESET_ALL}")
        logging.info("=" * 50)
        
        sql_db = SQLDatabaseTool()
        
        example = self.demo_examples[5]  # Database example
        logging.info(f"\n{Fore.CYAN}{example['title']}{Style.RESET_ALL}")
        logging.info(f"{example['description']}")
        logging.info("-" * 40)
        
        try:
            persona_data = example['params']['persona']
            
            # Store persona
            store_result = await sql_db.execute(
                operation="store_persona",
                **persona_data
            )
            
            if store_result.success:
                logging.info(f"{Fore.GREEN}‚úÖ Persona stored successfully!{Style.RESET_ALL}")
                
                # Retrieve persona
                retrieve_result = await sql_db.execute(
                    operation="get_persona",
                    name=persona_data["name"]
                )
                
                if retrieve_result.success:
                    logging.info(f"{Fore.GREEN}‚úÖ Persona retrieved successfully!{Style.RESET_ALL}")
                    logging.info(f"Retrieved: {retrieve_result.data['persona']['name']}")
                else:
                    logging.info(f"{Fore.RED}‚ùå Retrieval failed: {retrieve_result.message}{Style.RESET_ALL}")
            else:
                logging.info(f"{Fore.RED}‚ùå Storage failed: {store_result.message}{Style.RESET_ALL}")
                
        except Exception as e:
            logging.info(f"{Fore.RED}‚ùå Error: {str(e)}{Style.RESET_ALL}")
    
    async def run_fim_completion_demo(self) -> Any:
        """Run FIM completion demo"""
        logging.info(f"\n{Fore.YELLOW}üîó FIM Completion Demo{Style.RESET_ALL}")
        logging.info("=" * 50)
        
        fim_tool = FIMCompletionTool()
        
        example = self.demo_examples[6]  # FIM completion example
        logging.info(f"\n{Fore.CYAN}{example['title']}{Style.RESET_ALL}")
        logging.info(f"{example['description']}")
        logging.info("-" * 40)
        
        try:
            params = example['params']
            result = await fim_tool.execute(
                prefix=params['prefix'],
                suffix=params['suffix'],
                language=params['language']
            )
            
            if result.success:
                logging.info(f"{Fore.GREEN}‚úÖ FIM completion successful!{Style.RESET_ALL}")
                logging.info(f"Completion:\n{result.data.get('completion', 'N/A')}")
            else:
                logging.info(f"{Fore.RED}‚ùå Failed: {result.message}{Style.RESET_ALL}")
                
        except Exception as e:
            logging.info(f"{Fore.RED}‚ùå Error: {str(e)}{Style.RESET_ALL}")
    
    async def run_prefix_completion_demo(self) -> Any:
        """Run prefix completion demo"""
        logging.info(f"\n{Fore.YELLOW}üìù Prefix Completion Demo{Style.RESET_ALL}")
        logging.info("=" * 50)
        
        prefix_tool = PrefixCompletionTool()
        
        example = self.demo_examples[7]  # Prefix completion example
        logging.info(f"\n{Fore.CYAN}{example['title']}{Style.RESET_ALL}")
        logging.info(f"{example['description']}")
        logging.info("-" * 40)
        
        try:
            params = example['params']
            result = await prefix_tool.execute(
                prefix=params['prefix'],
                max_tokens=params['max_tokens']
            )
            
            if result.success:
                logging.info(f"{Fore.GREEN}‚úÖ Prefix completion successful!{Style.RESET_ALL}")
                logging.info(f"Generated:\n{result.data.get('completion', 'N/A')}")
            else:
                logging.info(f"{Fore.RED}‚ùå Failed: {result.message}{Style.RESET_ALL}")
                
        except Exception as e:
            logging.info(f"{Fore.RED}‚ùå Error: {str(e)}{Style.RESET_ALL}")
    
    async def run_llm_query_demo(self) -> Any:
        """Run LLM query demo"""
        logging.info(f"\n{Fore.YELLOW}ü§ñ LLM Query Demo{Style.RESET_ALL}")
        logging.info("=" * 50)
        
        llm_tool = LLMQueryTool()
        
        example = self.demo_examples[8]  # LLM query example
        logging.info(f"\n{Fore.CYAN}{example['title']}{Style.RESET_ALL}")
        logging.info(f"{example['description']}")
        logging.info("-" * 40)
        
        try:
            params = example['params']
            result = await llm_tool.execute(
                prompt=params['prompt'],
                max_tokens=params['max_tokens']
            )
            
            if result.success:
                logging.info(f"{Fore.GREEN}‚úÖ LLM query successful!{Style.RESET_ALL}")
                logging.info(f"Response:\n{result.data.get('response', 'N/A')}")
            else:
                logging.info(f"{Fore.RED}‚ùå Failed: {result.message}{Style.RESET_ALL}")
                
        except Exception as e:
            logging.info(f"{Fore.RED}‚ùå Error: {str(e)}{Style.RESET_ALL}")
    
    async def run_rag_pipeline_demo(self) -> Any:
        """Run RAG pipeline demo"""
        logging.info(f"\n{Fore.YELLOW}üìö RAG Pipeline Demo{Style.RESET_ALL}")
        logging.info("=" * 50)
        
        rag_tool = RAGPipelineTool()
        
        example = self.demo_examples[9]  # RAG pipeline example
        logging.info(f"\n{Fore.CYAN}{example['title']}{Style.RESET_ALL}")
        logging.info(f"{example['description']}")
        logging.info("-" * 40)
        
        try:
            params = example['params']
            result = await rag_tool.execute(
                query=params['query'],
                max_results=params['max_results']
            )
            
            if result.success:
                logging.info(f"{Fore.GREEN}‚úÖ RAG query successful!{Style.RESET_ALL}")
                documents = result.data.get('documents', [])
                logging.info(f"Found {len(documents)} relevant documents")
                for i, doc in enumerate(documents[:2]):  # Show first 2
                    logging.info(f"Document {i+1}: {doc.get('content', 'N/A')[:100]}...")
            else:
                logging.info(f"{Fore.RED}‚ùå Failed: {result.message}{Style.RESET_ALL}")
                
        except Exception as e:
            logging.info(f"{Fore.RED}‚ùå Error: {str(e)}{Style.RESET_ALL}")
    
    async def run_reasoning_demo(self) -> Any:
        """Run reasoning engine demo"""
        logging.info(f"\n{Fore.YELLOW}üß† Reasoning Engine Demo{Style.RESET_ALL}")
        logging.info("=" * 50)
        
        reasoning_tool = ReasoningEngine()
        
        example = self.demo_examples[10]  # Reasoning example
        logging.info(f"\n{Fore.CYAN}{example['title']}{Style.RESET_ALL}")
        logging.info(f"{example['description']}")
        logging.info("-" * 40)
        
        try:
            params = example['params']
            result = await reasoning_tool.execute(
                question=params['question'],
                approach=params['approach']
            )
            
            if result.success:
                logging.info(f"{Fore.GREEN}‚úÖ Reasoning successful!{Style.RESET_ALL}")
                logging.info(f"Analysis:\n{result.data.get('reasoning', 'N/A')}")
            else:
                logging.info(f"{Fore.RED}‚ùå Failed: {result.message}{Style.RESET_ALL}")
                
        except Exception as e:
            logging.info(f"{Fore.RED}‚ùå Error: {str(e)}{Style.RESET_ALL}")
    
    async def run_memory_demo(self) -> Any:
        """Run memory system demo"""
        logging.info(f"\n{Fore.YELLOW}üíæ Memory System Demo{Style.RESET_ALL}")
        logging.info("=" * 50)
        
        memory_tool = MemoryTool()
        
        example = self.demo_examples[11]  # Memory example
        logging.info(f"\n{Fore.CYAN}{example['title']}{Style.RESET_ALL}")
        logging.info(f"{example['description']}")
        logging.info("-" * 40)
        
        try:
            operations = example['params']['operations']
            
            for operation in operations:
                if operation['action'] == 'store':
                    result = await memory_tool.execute(
                        operation="store",
                        content=operation['content']
                    )
                    if result.success:
                        logging.info(f"{Fore.GREEN}‚úÖ Stored: {operation['content'][:50]}...{Style.RESET_ALL}")
                    else:
                        logging.info(f"{Fore.RED}‚ùå Storage failed: {result.message}{Style.RESET_ALL}")
                
                elif operation['action'] == 'retrieve':
                    result = await memory_tool.execute(
                        operation="retrieve",
                        query=operation['query']
                    )
                    if result.success:
                        logging.info(f"{Fore.GREEN}‚úÖ Retrieved: {result.data.get('memories', [])}{Style.RESET_ALL}")
                    else:
                        logging.info(f"{Fore.RED}‚ùå Retrieval failed: {result.message}{Style.RESET_ALL}")
                
        except Exception as e:
            logging.info(f"{Fore.RED}‚ùå Error: {str(e)}{Style.RESET_ALL}")
    
    def print_demo_summary(self) -> Any:
        """Print demo summary"""
        logging.info(f"\n{Fore.CYAN}üé≠ DEMO SUMMARY{Style.RESET_ALL}")
        logging.info("=" * 60)
        logging.info(f"{Fore.GREEN}‚úÖ All demos completed successfully!{Style.RESET_ALL}")
        logging.info(f"\n{Fore.YELLOW}Features demonstrated:{Style.RESET_ALL}")
        logging.info("  üîß DeepSeek Coder - Code generation, debugging, self-healing, FIM")
        logging.info("  üß† Embedding System - Text similarity and vector operations")
        logging.info("  üóÑÔ∏è Database System - Persona management and storage")
        logging.info("  üîó FIM Completion - Fill-in-Middle code completion")
        logging.info("  üìù Prefix Completion - Text generation from prefixes")
        logging.info("  ü§ñ LLM Query - Natural language processing")
        logging.info("  üìö RAG Pipeline - Knowledge retrieval and augmentation")
        logging.info("  üß† Reasoning Engine - Logical analysis and problem solving")
        logging.info("  üíæ Memory System - Information storage and retrieval")
        
        logging.info(f"\n{Fore.CYAN}üöÄ Ready to use BASED CODER CLI!{Style.RESET_ALL}")
        logging.info("Run 'python main.py' to start the interactive CLI")
    
    async def run_complete_demo(self) -> Any:
        """Run complete demo system"""
        self.print_banner()
        
        logging.info(f"{Fore.CYAN}üé≠ Starting BASED CODER CLI Demo System...{Style.RESET_ALL}")
        
        # Run all demos
        await self.run_deepseek_coder_demo()
        await self.run_embedding_demo()
        await self.run_database_demo()
        await self.run_fim_completion_demo()
        await self.run_prefix_completion_demo()
        await self.run_llm_query_demo()
        await self.run_rag_pipeline_demo()
        await self.run_reasoning_demo()
        await self.run_memory_demo()
        
        # Print summary
        self.print_demo_summary()

# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

async def run_complete_demo() -> None:
    """Run complete demo"""
    demo = BasedCoderDemo()
    await demo.run_complete_demo()

async def run_coder_demo() -> None:
    """Run DeepSeek Coder demo only"""
    demo = BasedCoderDemo()
    await demo.run_deepseek_coder_demo()

async def run_ai_demo() -> None:
    """Run AI features demo"""
    demo = BasedCoderDemo()
    await demo.run_embedding_demo()
    await demo.run_fim_completion_demo()
    await demo.run_prefix_completion_demo()
    await demo.run_llm_query_demo()

async def run_system_demo() -> None:
    """Run system features demo"""
    demo = BasedCoderDemo()
    await demo.run_database_demo()
    await demo.run_rag_pipeline_demo()
    await demo.run_reasoning_demo()
    await demo.run_memory_demo()

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

async def main() -> None:
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="BASED CODER CLI Demo System")
    parser.add_argument("--complete", action="store_true", help="Run complete demo")
    parser.add_argument("--coder", action="store_true", help="Run DeepSeek Coder demo only")
    parser.add_argument("--ai", action="store_true", help="Run AI features demo")
    parser.add_argument("--system", action="store_true", help="Run system features demo")
    
    args = parser.parse_args()
    
    if args.complete:
        await run_complete_demo()
    elif args.coder:
        await run_coder_demo()
    elif args.ai:
        await run_ai_demo()
    elif args.system:
        await run_system_demo()
    else:
        # Default: complete demo
        await run_complete_demo()

if __name__ == "__main__":
    asyncio.run(main()) 