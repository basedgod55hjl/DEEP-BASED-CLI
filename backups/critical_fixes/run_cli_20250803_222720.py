#!/usr/bin/env python3
"""
Simple CLI Runner for DEEP-CLI
Uses the available tools to provide basic functionality
"""

import sys
from typing import List, Dict, Any, Optional, Tuple

import asyncio
import logging
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from tools.tool_manager import ToolManager
from tools.simple_embedding_tool import SimpleEmbeddingTool
from tools.sql_database_tool import SQLDatabaseTool
from tools.llm_query_tool import LLMQueryTool

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleCLI:
    """Simple CLI interface for DEEP-CLI"""
    
    def __init__(self) -> Any:
        self.tool_manager = ToolManager()
        self.embedding_tool = SimpleEmbeddingTool()
        self.sql_tool = SQLDatabaseTool()
        self.llm_tool = LLMQueryTool()
        
        # Initialize tools
        self.initialize_tools()
    
    def initialize_tools(self) -> Any:
        """Initialize all tools"""
        try:
            # Register tools with manager
            self.tool_manager.register_tool("embedding", self.embedding_tool)
            self.tool_manager.register_tool("database", self.sql_tool)
            self.tool_manager.register_tool("llm", self.llm_tool)
            
            logger.info("✅ Tools initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize tools: {e}")
    
    async def test_embedding(self) -> Any:
        """Test the embedding system"""
        try:
            logger.info("Testing embedding system...")
            
            result = await self.embedding_tool.embed_texts([
                "Hello world",
                "This is a test",
                "Embedding system working"
            ])
            
            if result.success:
                logger.info(f"✅ Embedding test passed: {result.data['total_generated']} embeddings created")
                return True
            else:
                logger.error(f"❌ Embedding test failed: {result.error}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Embedding test error: {e}")
            return False
    
    async def test_database(self) -> Any:
        """Test the database system"""
        try:
            logger.info("Testing database system...")
            
            # Test persona storage
            persona_data = {
                "name": "Deanna",
                "description": "AI Assistant",
                "personality": "Helpful and knowledgeable"
            }
            
            result = await self.sql_tool.store_persona(persona_data)
            
            if result.success:
                logger.info("✅ Database test passed")
                return True
            else:
                logger.error(f"❌ Database test failed: {result.error}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Database test error: {e}")
            return False
    
    async def test_llm(self) -> Any:
        """Test the LLM system"""
        try:
            logger.info("Testing LLM system...")
            
            # Test a simple query
            result = await self.llm_tool.execute(
                query="What is 2 + 2?",
                max_tokens=50
            )
            
            if result.success:
                logger.info("✅ LLM test passed")
                return True
            else:
                logger.error(f"❌ LLM test failed: {result.error}")
                return False
                
        except Exception as e:
            logger.error(f"❌ LLM test error: {e}")
            return False
    
    async def run_tests(self) -> Any:
        """Run all system tests"""
        logger.info("🚀 Running DEEP-CLI system tests...")
        
        tests = [
            ("Embedding System", self.test_embedding),
            ("Database System", self.test_database),
            ("LLM System", self.test_llm)
        ]
        
        results = []
        for test_name, test_func in tests:
            logger.info(f"\n--- Testing {test_name} ---")
            result = await test_func()
            results.append((test_name, result))
        
        # Print summary
        logger.info("\n" + "="*50)
        logger.info("📊 TEST RESULTS SUMMARY")
        logger.info("="*50)
        
        passed = 0
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"{test_name}: {status}")
            if result:
                passed += 1
        
        logger.info(f"\nOverall: {passed}/{len(results)} tests passed")
        
        if passed == len(results):
            logger.info("🎉 All tests passed! System is ready to use.")
        else:
            logger.info("⚠️  Some tests failed. Check logs for details.")
    
    async def interactive_mode(self) -> Any:
        """Run interactive mode"""
        logger.info("🤖 DEEP-CLI Interactive Mode")
        logger.info("Type 'quit' to exit, 'help' for commands")
        
        while True:
            try:
                user_input = input("\n> ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    logger.info("Goodbye!")
                    break
                
                elif user_input.lower() == 'help':
                    self.show_help()
                
                elif user_input.lower() == 'test':
                    await self.run_tests()
                
                elif user_input.lower().startswith('embed '):
                    text = user_input[6:]  # Remove 'embed ' prefix
                    result = await self.embedding_tool.embed_texts([text])
                    if result.success:
                        logger.info(f"Embedding created: {len(result.data['embeddings'][0])} dimensions")
                    else:
                        logger.error(f"Failed: {result.error}")
                
                elif user_input.lower().startswith('chat '):
                    query = user_input[5:]  # Remove 'chat ' prefix
                    result = await self.llm_tool.execute(query=query)
                    if result.success:
                        logger.info(f"Response: {result.data.get('response', 'No response')}")
                    else:
                        logger.error(f"Failed: {result.error}")
                
                else:
                    logger.info("Unknown command. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                logger.info("\nGoodbye!")
                break
            except Exception as e:
                logger.error(f"Error: {e}")
    
    def show_help(self) -> Any:
        """Show available commands"""
        help_text = """
Available Commands:
- help: Show this help
- test: Run system tests
- embed <text>: Create embedding for text
- chat <message>: Send message to LLM
- quit/exit/q: Exit the program
        """
        logger.info(help_text)

async def main() -> None:
    """Main function"""
    cli = SimpleCLI()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "test":
            await cli.run_tests()
        elif command == "interactive":
            await cli.interactive_mode()
        else:
            logger.info("Usage: python run_cli.py [test|interactive]")
    else:
        # Default to interactive mode
        await cli.interactive_mode()

if __name__ == "__main__":
    asyncio.run(main()) 