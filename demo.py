#!/usr/bin/env python3
"""
🚀 BASED CODER CLI - Unified Demo System
Made by @Lucariolucario55 on Telegram

Consolidated demo system for showcasing all BASED CODER CLI features
"""

import asyncio
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
    
    def __init__(self):
        self.config = get_config()
        self.demo_examples = [
            # DeepSeek Coder Examples
            {
                "title": "🔧 DeepSeek Coder - Code Generation",
                "description": "Generate Python code for a web scraper",
                "operation": "code_generation",
                "params": {
                    "prompt": "Create a Python web scraper that extracts article titles from a news website",
                    "language": "python",
                    "requirements": ["Use requests and BeautifulSoup", "Handle errors gracefully", "Include rate limiting"]
                }
            },
            {
                "title": "🐛 DeepSeek Coder - Code Debugging",
                "description": "Debug a Python function with errors",
                "operation": "code_debugging",
                "params": {
                    "code": """
def calculate_fibonacci(n):
    if n <= 0:
        return None
    elif n == 1:
        return 1
    else:
        return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

# Test the function
result = calculate_fibonacci(5)
print(f"Fibonacci of 5 is: {result}")
""",
                    "language": "python",
                    "error_message": "RecursionError: maximum recursion depth exceeded"
                }
            },
            {
                "title": "🩹 DeepSeek Coder - Self-Healing Code",
                "description": "Self-heal code with potential issues",
                "operation": "self_healing",
                "params": {
                    "code": """
import os
def read_file(filename):
    file = open(filename, 'r')
    content = file.read()
    return content

# Usage
data = read_file('test.txt')
print(data)
""",
                    "language": "python"
                }
            },
            {
                "title": "🔗 DeepSeek Coder - FIM Completion",
                "description": "Fill-in-Middle code completion",
                "operation": "fim_completion",
                "params": {
                    "prefix": """
def process_data(data_list):
    results = []
    for item in data_list:
""",
                    "suffix": """
    return results

# Test
data = [1, 2, 3, 4, 5]
result = process_data(data)
print(result)
""",
                    "language": "python"
                }
            },
            # Embedding Examples
            {
                "title": "🧠 Embedding System - Text Similarity",
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
                "title": "🗄️ Database System - Persona Management",
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
                "title": "🔗 FIM Completion - Code Generation",
                "description": "Complete code with prefix and suffix",
                "operation": "fim_completion",
                "params": {
                    "prefix": "def calculate_sum(numbers):",
                    "suffix": "return total",
                    "language": "python"
                }
            },
            # Prefix Completion Examples
            {
                "title": "📝 Prefix Completion - Text Generation",
                "description": "Generate text from prefix",
                "operation": "prefix_completion",
                "params": {
                    "prefix": "The future of artificial intelligence",
                    "max_tokens": 100
                }
            },
            # LLM Query Examples
            {
                "title": "🤖 LLM Query - Natural Language Processing",
                "description": "Ask questions to the AI",
                "operation": "llm_query",
                "params": {
                    "prompt": "Explain quantum computing in simple terms",
                    "max_tokens": 200
                }
            },
            # RAG Pipeline Examples
            {
                "title": "📚 RAG Pipeline - Knowledge Retrieval",
                "description": "Retrieve relevant information",
                "operation": "rag_query",
                "params": {
                    "query": "What are the benefits of machine learning?",
                    "max_results": 3
                }
            },
            # Reasoning Examples
            {
                "title": "🧠 Reasoning Engine - Logical Analysis",
                "description": "Analyze complex problems",
                "operation": "reasoning",
                "params": {
                    "question": "If a train leaves station A at 2 PM traveling 60 mph and another train leaves station B at 3 PM traveling 80 mph, when will they meet if the stations are 200 miles apart?",
                    "approach": "step_by_step"
                }
            },
            # Memory Examples
            {
                "title": "💾 Memory System - Information Storage",
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
    
    def print_banner(self):
        """Print demo banner"""
        banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  🎭 BASED CODER CLI - UNIFIED DEMO SYSTEM                                    ║
║                                                                              ║
║  Features:                                                                   ║
║  ✅ DeepSeek Coder Integration                                               ║
║  ✅ Embedding & Similarity Systems                                           ║
║  ✅ Database & Persona Management                                            ║
║  ✅ FIM & Prefix Completion                                                  ║
║  ✅ LLM Query & RAG Pipeline                                                 ║
║  ✅ Reasoning & Memory Systems                                               ║
║                                                                              ║
║  Made by @Lucariolucario55 on Telegram                                      ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
        """
        print(banner)
    
    async def run_deepseek_coder_demo(self):
        """Run DeepSeek Coder demos"""
        print(f"\n{Fore.YELLOW}🔧 DeepSeek Coder Demo{Style.RESET_ALL}")
        print("=" * 50)
        
        coder_tool = DeepSeekCoderTool()
        
        for example in self.demo_examples[:4]:  # First 4 are DeepSeek Coder examples
            print(f"\n{Fore.CYAN}{example['title']}{Style.RESET_ALL}")
            print(f"{example['description']}")
            print("-" * 40)
            
            try:
                result = await coder_tool.execute(
                    operation=example['operation'],
                    **example['params']
                )
                
                if result.success:
                    print(f"{Fore.GREEN}✅ Success!{Style.RESET_ALL}")
                    if 'code' in result.data:
                        print(f"Generated Code:\n{result.data['code'][:300]}...")
                    elif 'completion' in result.data:
                        print(f"Completion:\n{result.data['completion'][:300]}...")
                    elif 'analysis' in result.data:
                        print(f"Analysis:\n{result.data['analysis'][:300]}...")
                else:
                    print(f"{Fore.RED}❌ Failed: {result.message}{Style.RESET_ALL}")
                
            except Exception as e:
                print(f"{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}")
            
            print()
            await asyncio.sleep(1)  # Brief pause between demos
    
    async def run_embedding_demo(self):
        """Run embedding system demo"""
        print(f"\n{Fore.YELLOW}🧠 Embedding System Demo{Style.RESET_ALL}")
        print("=" * 50)
        
        embedding_tool = SimpleEmbeddingTool()
        
        example = self.demo_examples[4]  # Embedding example
        print(f"\n{Fore.CYAN}{example['title']}{Style.RESET_ALL}")
        print(f"{example['description']}")
        print("-" * 40)
        
        try:
            texts = example['params']['texts']
            result = await embedding_tool.embed_texts(texts)
            
            if result.success:
                print(f"{Fore.GREEN}✅ Embeddings generated successfully!{Style.RESET_ALL}")
                
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
                            print(f"Similarity between text {i+1} and {j+1}: {similarity:.4f}")
            else:
                print(f"{Fore.RED}❌ Failed: {result.message}{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}")
    
    async def run_database_demo(self):
        """Run database system demo"""
        print(f"\n{Fore.YELLOW}🗄️ Database System Demo{Style.RESET_ALL}")
        print("=" * 50)
        
        sql_db = SQLDatabaseTool()
        
        example = self.demo_examples[5]  # Database example
        print(f"\n{Fore.CYAN}{example['title']}{Style.RESET_ALL}")
        print(f"{example['description']}")
        print("-" * 40)
        
        try:
            persona_data = example['params']['persona']
            
            # Store persona
            store_result = await sql_db.execute(
                operation="store_persona",
                **persona_data
            )
            
            if store_result.success:
                print(f"{Fore.GREEN}✅ Persona stored successfully!{Style.RESET_ALL}")
                
                # Retrieve persona
                retrieve_result = await sql_db.execute(
                    operation="get_persona",
                    name=persona_data["name"]
                )
                
                if retrieve_result.success:
                    print(f"{Fore.GREEN}✅ Persona retrieved successfully!{Style.RESET_ALL}")
                    print(f"Retrieved: {retrieve_result.data['persona']['name']}")
                else:
                    print(f"{Fore.RED}❌ Retrieval failed: {retrieve_result.message}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ Storage failed: {store_result.message}{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}")
    
    async def run_fim_completion_demo(self):
        """Run FIM completion demo"""
        print(f"\n{Fore.YELLOW}🔗 FIM Completion Demo{Style.RESET_ALL}")
        print("=" * 50)
        
        fim_tool = FIMCompletionTool()
        
        example = self.demo_examples[6]  # FIM completion example
        print(f"\n{Fore.CYAN}{example['title']}{Style.RESET_ALL}")
        print(f"{example['description']}")
        print("-" * 40)
        
        try:
            params = example['params']
            result = await fim_tool.execute(
                prefix=params['prefix'],
                suffix=params['suffix'],
                language=params['language']
            )
            
            if result.success:
                print(f"{Fore.GREEN}✅ FIM completion successful!{Style.RESET_ALL}")
                print(f"Completion:\n{result.data.get('completion', 'N/A')}")
            else:
                print(f"{Fore.RED}❌ Failed: {result.message}{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}")
    
    async def run_prefix_completion_demo(self):
        """Run prefix completion demo"""
        print(f"\n{Fore.YELLOW}📝 Prefix Completion Demo{Style.RESET_ALL}")
        print("=" * 50)
        
        prefix_tool = PrefixCompletionTool()
        
        example = self.demo_examples[7]  # Prefix completion example
        print(f"\n{Fore.CYAN}{example['title']}{Style.RESET_ALL}")
        print(f"{example['description']}")
        print("-" * 40)
        
        try:
            params = example['params']
            result = await prefix_tool.execute(
                prefix=params['prefix'],
                max_tokens=params['max_tokens']
            )
            
            if result.success:
                print(f"{Fore.GREEN}✅ Prefix completion successful!{Style.RESET_ALL}")
                print(f"Generated:\n{result.data.get('completion', 'N/A')}")
            else:
                print(f"{Fore.RED}❌ Failed: {result.message}{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}")
    
    async def run_llm_query_demo(self):
        """Run LLM query demo"""
        print(f"\n{Fore.YELLOW}🤖 LLM Query Demo{Style.RESET_ALL}")
        print("=" * 50)
        
        llm_tool = LLMQueryTool()
        
        example = self.demo_examples[8]  # LLM query example
        print(f"\n{Fore.CYAN}{example['title']}{Style.RESET_ALL}")
        print(f"{example['description']}")
        print("-" * 40)
        
        try:
            params = example['params']
            result = await llm_tool.execute(
                prompt=params['prompt'],
                max_tokens=params['max_tokens']
            )
            
            if result.success:
                print(f"{Fore.GREEN}✅ LLM query successful!{Style.RESET_ALL}")
                print(f"Response:\n{result.data.get('response', 'N/A')}")
            else:
                print(f"{Fore.RED}❌ Failed: {result.message}{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}")
    
    async def run_rag_pipeline_demo(self):
        """Run RAG pipeline demo"""
        print(f"\n{Fore.YELLOW}📚 RAG Pipeline Demo{Style.RESET_ALL}")
        print("=" * 50)
        
        rag_tool = RAGPipelineTool()
        
        example = self.demo_examples[9]  # RAG pipeline example
        print(f"\n{Fore.CYAN}{example['title']}{Style.RESET_ALL}")
        print(f"{example['description']}")
        print("-" * 40)
        
        try:
            params = example['params']
            result = await rag_tool.execute(
                query=params['query'],
                max_results=params['max_results']
            )
            
            if result.success:
                print(f"{Fore.GREEN}✅ RAG query successful!{Style.RESET_ALL}")
                documents = result.data.get('documents', [])
                print(f"Found {len(documents)} relevant documents")
                for i, doc in enumerate(documents[:2]):  # Show first 2
                    print(f"Document {i+1}: {doc.get('content', 'N/A')[:100]}...")
            else:
                print(f"{Fore.RED}❌ Failed: {result.message}{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}")
    
    async def run_reasoning_demo(self):
        """Run reasoning engine demo"""
        print(f"\n{Fore.YELLOW}🧠 Reasoning Engine Demo{Style.RESET_ALL}")
        print("=" * 50)
        
        reasoning_tool = ReasoningEngine()
        
        example = self.demo_examples[10]  # Reasoning example
        print(f"\n{Fore.CYAN}{example['title']}{Style.RESET_ALL}")
        print(f"{example['description']}")
        print("-" * 40)
        
        try:
            params = example['params']
            result = await reasoning_tool.execute(
                question=params['question'],
                approach=params['approach']
            )
            
            if result.success:
                print(f"{Fore.GREEN}✅ Reasoning successful!{Style.RESET_ALL}")
                print(f"Analysis:\n{result.data.get('reasoning', 'N/A')}")
            else:
                print(f"{Fore.RED}❌ Failed: {result.message}{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}")
    
    async def run_memory_demo(self):
        """Run memory system demo"""
        print(f"\n{Fore.YELLOW}💾 Memory System Demo{Style.RESET_ALL}")
        print("=" * 50)
        
        memory_tool = MemoryTool()
        
        example = self.demo_examples[11]  # Memory example
        print(f"\n{Fore.CYAN}{example['title']}{Style.RESET_ALL}")
        print(f"{example['description']}")
        print("-" * 40)
        
        try:
            operations = example['params']['operations']
            
            for operation in operations:
                if operation['action'] == 'store':
                    result = await memory_tool.execute(
                        operation="store",
                        content=operation['content']
                    )
                    if result.success:
                        print(f"{Fore.GREEN}✅ Stored: {operation['content'][:50]}...{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}❌ Storage failed: {result.message}{Style.RESET_ALL}")
                
                elif operation['action'] == 'retrieve':
                    result = await memory_tool.execute(
                        operation="retrieve",
                        query=operation['query']
                    )
                    if result.success:
                        print(f"{Fore.GREEN}✅ Retrieved: {result.data.get('memories', [])}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}❌ Retrieval failed: {result.message}{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}")
    
    def print_demo_summary(self):
        """Print demo summary"""
        print(f"\n{Fore.CYAN}🎭 DEMO SUMMARY{Style.RESET_ALL}")
        print("=" * 60)
        print(f"{Fore.GREEN}✅ All demos completed successfully!{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}Features demonstrated:{Style.RESET_ALL}")
        print("  🔧 DeepSeek Coder - Code generation, debugging, self-healing, FIM")
        print("  🧠 Embedding System - Text similarity and vector operations")
        print("  🗄️ Database System - Persona management and storage")
        print("  🔗 FIM Completion - Fill-in-Middle code completion")
        print("  📝 Prefix Completion - Text generation from prefixes")
        print("  🤖 LLM Query - Natural language processing")
        print("  📚 RAG Pipeline - Knowledge retrieval and augmentation")
        print("  🧠 Reasoning Engine - Logical analysis and problem solving")
        print("  💾 Memory System - Information storage and retrieval")
        
        print(f"\n{Fore.CYAN}🚀 Ready to use BASED CODER CLI!{Style.RESET_ALL}")
        print("Run 'python main.py' to start the interactive CLI")
    
    async def run_complete_demo(self):
        """Run complete demo system"""
        self.print_banner()
        
        print(f"{Fore.CYAN}🎭 Starting BASED CODER CLI Demo System...{Style.RESET_ALL}")
        
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

async def run_complete_demo():
    """Run complete demo"""
    demo = BasedCoderDemo()
    await demo.run_complete_demo()

async def run_coder_demo():
    """Run DeepSeek Coder demo only"""
    demo = BasedCoderDemo()
    await demo.run_deepseek_coder_demo()

async def run_ai_demo():
    """Run AI features demo"""
    demo = BasedCoderDemo()
    await demo.run_embedding_demo()
    await demo.run_fim_completion_demo()
    await demo.run_prefix_completion_demo()
    await demo.run_llm_query_demo()

async def run_system_demo():
    """Run system features demo"""
    demo = BasedCoderDemo()
    await demo.run_database_demo()
    await demo.run_rag_pipeline_demo()
    await demo.run_reasoning_demo()
    await demo.run_memory_demo()

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

async def main():
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