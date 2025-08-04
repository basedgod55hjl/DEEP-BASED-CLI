#!/usr/bin/env python3
"""
🚀 BASED CODER CLI - Unified Test Suite
Made by @Lucariolucario55 on Telegram

Consolidated testing system for the entire BASED CODER CLI
"""

import asyncio
import logging
import time
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import colorama
from colorama import Fore, Style
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax

# Import our configuration and tools
from config import get_config, validate_deepseek_key, validate_huggingface_token
from tools.simple_embedding_tool import SimpleEmbeddingTool
from tools.sql_database_tool import SQLDatabaseTool
from tools.fim_completion_tool import FIMCompletionTool
from tools.prefix_completion_tool import PrefixCompletionTool
from tools.llm_query_tool import LLMQueryTool
from tools.deepseek_coder_tool import DeepSeekCoderTool

# Initialize colorama
colorama.init()

logger = logging.getLogger(__name__)
console = Console()

class BasedCoderTestSuite:
    """Unified test suite for BASED CODER CLI"""
    
    def __init__(self):
        self.config = get_config()
        self.test_results = {}
        self.console = Console()
        
        # Initialize tools for testing
        self.embedding_tool = SimpleEmbeddingTool()
        self.sql_db = SQLDatabaseTool()
        self.fim_tool = FIMCompletionTool()
        self.prefix_tool = PrefixCompletionTool()
        self.llm_tool = LLMQueryTool()
        self.coder_tool = DeepSeekCoderTool()
    
    def print_banner(self):
        """Print test suite banner"""
        banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  🧪 BASED CODER CLI - UNIFIED TEST SUITE                                     ║
║                                                                              ║
║  Features:                                                                   ║
║  ✅ Configuration Testing                                                     ║
║  ✅ API Keys Validation                                                       ║
║  ✅ Tool Functionality Testing                                                ║
║  ✅ Model Integration Testing                                                 ║
║  ✅ Database Operations Testing                                               ║
║  ✅ Performance & Reliability Testing                                         ║
║                                                                              ║
║  Made by @Lucariolucario55 on Telegram                                      ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
        """
        print(banner)
    
    async def test_configuration(self) -> bool:
        """Test configuration system"""
        self.console.print("\n[bold green]Testing Configuration System...[/bold green]")
        
        try:
            # Test config retrieval
            config = get_config()
            
            # Test basic config structure
            required_sections = ['database', 'llm', 'persona', 'rag', 'memory', 'tool', 'security', 'performance', 'logging', 'session', 'features', 'models']
            for section in required_sections:
                if hasattr(config, section):
                    self.console.print(f"✅ {section} configuration available")
                else:
                    self.console.print(f"❌ {section} configuration missing")
                    return False
            
            # Test config validation
            issues = self.config.validate_config()
            if issues:
                self.console.print(f"⚠️ Configuration issues found: {issues}")
                return False
            
            self.console.print("✅ Configuration system working correctly")
            self.test_results["configuration"] = True
            return True
            
        except Exception as e:
            self.console.print(f"❌ Configuration test failed: {str(e)}")
            self.test_results["configuration"] = False
            return False
    
    async def test_api_keys(self) -> bool:
        """Test API keys validation"""
        self.console.print("\n[bold green]Testing API Keys...[/bold green]")
        
        try:
            # Test DeepSeek API key
            deepseek_valid = validate_deepseek_key(self.config.llm.api_key)
            if deepseek_valid:
                self.console.print("✅ DeepSeek API key is valid")
            else:
                self.console.print("❌ DeepSeek API key is invalid")
                return False
            
            # Test HuggingFace token
            hf_valid = validate_huggingface_token(self.config.models.huggingface_token)
            if hf_valid:
                self.console.print("✅ HuggingFace token is valid")
            else:
                self.console.print("❌ HuggingFace token is invalid")
                return False
            
            self.test_results["api_keys"] = True
            return True
            
        except Exception as e:
            self.console.print(f"❌ API keys test failed: {str(e)}")
            self.test_results["api_keys"] = False
            return False
    
    async def test_simple_embeddings(self) -> bool:
        """Test simple embedding system"""
        self.console.print("\n[bold green]Testing Simple Embedding System...[/bold green]")
        
        try:
            # Test basic embedding
            test_texts = [
                "Hello, this is a test sentence.",
                "Another test sentence for embedding.",
                "The quick brown fox jumps over the lazy dog."
            ]
            
            result = await self.embedding_tool.embed_texts(test_texts)
            
            if result.success:
                self.console.print(f"✅ Simple embedding successful: {result.data['total_generated']} embeddings")
                self.console.print(f"   Dimension: {result.data['embedding_dimension']}")
                
                # Test similarity
                embeddings = result.data['embeddings']
                if len(embeddings) >= 2:
                    similarity_result = await self.embedding_tool.compute_similarity(
                        embedding1=embeddings[0]['embedding'],
                        embedding2=embeddings[1]['embedding']
                    )
                    
                    if similarity_result.success:
                        self.console.print(f"✅ Similarity computation: {similarity_result.data['similarity']:.4f}")
                    else:
                        self.console.print("❌ Similarity computation failed")
                        return False
                
                self.test_results["simple_embeddings"] = True
                return True
            else:
                self.console.print(f"❌ Simple embedding failed: {result.message}")
                self.test_results["simple_embeddings"] = False
                return False
                
        except Exception as e:
            self.console.print(f"❌ Simple embedding test error: {str(e)}")
            self.test_results["simple_embeddings"] = False
            return False
    
    async def test_sql_database(self) -> bool:
        """Test SQL database functionality"""
        self.console.print("\n[bold green]Testing SQL Database System...[/bold green]")
        
        try:
            # Test persona storage
            persona_data = {
                "name": f"Test Persona {int(time.time())}",
                "description": "A test persona for validation",
                "personality_traits": {"traits": ["helpful", "friendly"]},
                "knowledge_base": {"domains": ["testing"]},
                "conversation_style": {"greeting": "Hello!"}
            }
            
            result = await self.sql_db.execute(
                operation="store_persona",
                **persona_data
            )
            
            if result.success:
                self.console.print("✅ Persona storage successful")
                
                # Test persona retrieval
                retrieve_result = await self.sql_db.execute(
                    operation="get_persona",
                    name=persona_data["name"]
                )
                
                if retrieve_result.success:
                    self.console.print("✅ Persona retrieval successful")
                    
                    # Test persona search
                    search_result = await self.sql_db.execute(
                        operation="search_personas",
                        query="test",
                        limit=5
                    )
                    
                    if search_result.success:
                        self.console.print(f"✅ Persona search successful: {len(search_result.data['personas'])} results")
                        self.test_results["sql_database"] = True
                        return True
                    else:
                        self.console.print(f"❌ Persona search failed: {search_result.message}")
                        return False
                else:
                    self.console.print(f"❌ Persona retrieval failed: {retrieve_result.message}")
                    return False
            else:
                self.console.print(f"❌ Persona storage failed: {result.message}")
                self.test_results["sql_database"] = False
                return False
                
        except Exception as e:
            self.console.print(f"❌ SQL database test error: {str(e)}")
            self.test_results["sql_database"] = False
            return False
    
    async def test_fim_completion(self) -> bool:
        """Test FIM completion functionality"""
        self.console.print("\n[bold green]Testing FIM Completion...[/bold green]")
        
        try:
            # Test FIM completion
            prefix = "def hello_world():"
            suffix = "print('Hello, World!')"
            
            result = await self.fim_tool.execute(
                prefix=prefix,
                suffix=suffix,
                language="python"
            )
            
            if result.success:
                self.console.print("✅ FIM completion successful")
                self.console.print(f"   Generated: {result.data.get('completion', 'N/A')[:100]}...")
                self.test_results["fim_completion"] = True
                return True
            else:
                self.console.print(f"❌ FIM completion failed: {result.message}")
                self.test_results["fim_completion"] = False
                return False
                
        except Exception as e:
            self.console.print(f"❌ FIM completion test error: {str(e)}")
            self.test_results["fim_completion"] = False
            return False
    
    async def test_prefix_completion(self) -> bool:
        """Test prefix completion functionality"""
        self.console.print("\n[bold green]Testing Prefix Completion...[/bold green]")
        
        try:
            # Test prefix completion
            prefix = "The quick brown fox"
            
            result = await self.prefix_tool.execute(
                prefix=prefix,
                max_tokens=50
            )
            
            if result.success:
                self.console.print("✅ Prefix completion successful")
                self.console.print(f"   Generated: {result.data.get('completion', 'N/A')[:100]}...")
                self.test_results["prefix_completion"] = True
                return True
            else:
                self.console.print(f"❌ Prefix completion failed: {result.message}")
                self.test_results["prefix_completion"] = False
                return False
                
        except Exception as e:
            self.console.print(f"❌ Prefix completion test error: {str(e)}")
            self.test_results["prefix_completion"] = False
            return False
    
    async def test_llm_query(self) -> bool:
        """Test LLM query functionality"""
        self.console.print("\n[bold green]Testing LLM Query System...[/bold green]")
        
        try:
            # Test simple query
            result = await self.llm_tool.execute(
                prompt="What is 2 + 2?",
                max_tokens=50
            )
            
            if result.success:
                self.console.print("✅ LLM query successful")
                self.console.print(f"   Response: {result.data.get('response', 'N/A')[:100]}...")
                self.test_results["llm_query"] = True
                return True
            else:
                self.console.print(f"❌ LLM query failed: {result.message}")
                self.test_results["llm_query"] = False
                return False
                
        except Exception as e:
            self.console.print(f"❌ LLM query test error: {str(e)}")
            self.test_results["llm_query"] = False
            return False
    
    async def test_deepseek_coder(self) -> bool:
        """Test DeepSeek Coder functionality"""
        self.console.print("\n[bold green]Testing DeepSeek Coder...[/bold green]")
        
        try:
            # Test code generation
            result = await self.coder_tool.execute(
                operation="code_generation",
                prompt="Create a Python function to calculate fibonacci numbers",
                language="python"
            )
            
            if result.success:
                self.console.print("✅ DeepSeek Coder code generation successful")
                self.console.print(f"   Generated: {result.data.get('code', 'N/A')[:100]}...")
                self.test_results["deepseek_coder"] = True
                return True
            else:
                self.console.print(f"❌ DeepSeek Coder failed: {result.message}")
                self.test_results["deepseek_coder"] = False
                return False
                
        except Exception as e:
            self.console.print(f"❌ DeepSeek Coder test error: {str(e)}")
            self.test_results["deepseek_coder"] = False
            return False
    
    async def test_model_integration(self) -> bool:
        """Test model integration"""
        self.console.print("\n[bold green]Testing Model Integration...[/bold green]")
        
        try:
            # Check if Qwen model exists
            qwen_dir = Path("data/models/qwen3_embedding")
            if qwen_dir.exists():
                model_files = list(qwen_dir.glob("*.safetensors")) + list(qwen_dir.glob("*.bin"))
                if model_files:
                    self.console.print(f"✅ Qwen model found: {len(model_files)} files")
                    self.test_results["model_integration"] = True
                    return True
                else:
                    self.console.print("❌ Qwen model files not found")
                    return False
            else:
                self.console.print("❌ Qwen model directory not found")
                self.test_results["model_integration"] = False
                return False
                
        except Exception as e:
            self.console.print(f"❌ Model integration test error: {str(e)}")
            self.test_results["model_integration"] = False
            return False
    
    async def test_performance(self) -> bool:
        """Test system performance"""
        self.console.print("\n[bold green]Testing System Performance...[/bold green]")
        
        try:
            # Test embedding performance
            start_time = time.time()
            
            test_texts = ["Performance test sentence"] * 10
            result = await self.embedding_tool.embed_texts(test_texts)
            
            end_time = time.time()
            duration = end_time - start_time
            
            if result.success:
                self.console.print(f"✅ Performance test passed: {duration:.2f}s for {len(test_texts)} embeddings")
                self.test_results["performance"] = True
                return True
            else:
                self.console.print(f"❌ Performance test failed: {result.message}")
                self.test_results["performance"] = False
                return False
                
        except Exception as e:
            self.console.print(f"❌ Performance test error: {str(e)}")
            self.test_results["performance"] = False
            return False
    
    def print_test_summary(self):
        """Print test summary"""
        print(f"\n{Fore.CYAN}📊 TEST SUMMARY{Style.RESET_ALL}")
        print("=" * 60)
        
        for test_name, success in self.test_results.items():
            status_icon = "✅" if success else "❌"
            test_display_name = test_name.replace("_", " ").title()
            print(f"{status_icon} {test_display_name}")
        
        print("=" * 60)
        
        # Overall status
        success_count = sum(self.test_results.values())
        total_count = len(self.test_results)
        
        if success_count == total_count:
            print(f"{Fore.GREEN}🎉 All tests passed! ({success_count}/{total_count}){Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}⚠️ {success_count}/{total_count} tests passed{Style.RESET_ALL}")
            print(f"{Fore.RED}❌ {total_count - success_count} tests failed{Style.RESET_ALL}")
        
        # Failed tests
        failed_tests = [name for name, success in self.test_results.items() if not success]
        if failed_tests:
            print(f"\n{Fore.RED}Failed tests:{Style.RESET_ALL}")
            for test in failed_tests:
                print(f"  - {test.replace('_', ' ').title()}")
    
    async def run_all_tests(self) -> Dict[str, bool]:
        """Run all tests"""
        self.print_banner()
        
        print(f"{Fore.CYAN}🧪 Starting BASED CODER CLI Test Suite...{Style.RESET_ALL}")
        
        # Run all tests
        await self.test_configuration()
        await self.test_api_keys()
        await self.test_simple_embeddings()
        await self.test_sql_database()
        await self.test_fim_completion()
        await self.test_prefix_completion()
        await self.test_llm_query()
        await self.test_deepseek_coder()
        await self.test_model_integration()
        await self.test_performance()
        
        # Print summary
        self.print_test_summary()
        
        return self.test_results

# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

async def run_all_tests():
    """Run all tests"""
    test_suite = BasedCoderTestSuite()
    return await test_suite.run_all_tests()

async def test_core_features():
    """Test core features only"""
    test_suite = BasedCoderTestSuite()
    
    await test_suite.test_configuration()
    await test_suite.test_api_keys()
    await test_suite.test_simple_embeddings()
    await test_suite.test_sql_database()
    
    test_suite.print_test_summary()
    return test_suite.test_results

async def test_ai_features():
    """Test AI features only"""
    test_suite = BasedCoderTestSuite()
    
    await test_suite.test_fim_completion()
    await test_suite.test_prefix_completion()
    await test_suite.test_llm_query()
    await test_suite.test_deepseek_coder()
    
    test_suite.print_test_summary()
    return test_suite.test_results

async def test_integration():
    """Test integration features only"""
    test_suite = BasedCoderTestSuite()
    
    await test_suite.test_model_integration()
    await test_suite.test_performance()
    
    test_suite.print_test_summary()
    return test_suite.test_results

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="BASED CODER CLI Test Suite")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--core", action="store_true", help="Test core features only")
    parser.add_argument("--ai", action="store_true", help="Test AI features only")
    parser.add_argument("--integration", action="store_true", help="Test integration features only")
    
    args = parser.parse_args()
    
    if args.all:
        await run_all_tests()
    elif args.core:
        await test_core_features()
    elif args.ai:
        await test_ai_features()
    elif args.integration:
        await test_integration()
    else:
        # Default: run all tests
        await run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 