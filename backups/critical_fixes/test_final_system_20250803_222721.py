import logging
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)
#!/usr/bin/env python3
"""
Final System Test
Comprehensive test of all working components with clear guidance for fixes
"""

import asyncio
import logging
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
import time

from tools.simple_embedding_tool import SimpleEmbeddingTool
from tools.sql_database_tool import SQLDatabaseTool
from config.api_keys import print_api_status, is_deepseek_key_valid

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinalSystemTester:
    """Final comprehensive system test"""
    
    def __init__(self) -> Any:
        """Initialize the tester"""
        self.console = Console()
        self.test_results = []
    
    async def test_simple_embeddings(self) -> Any:
        """Test simple embedding system"""
        self.console.logger.info("\n[bold green]🧠 Testing Simple Embedding System...[/bold green]")
        
        try:
            embedding_tool = SimpleEmbeddingTool()
            
            # Test basic embedding
            test_texts = [
                "Hello, this is a test sentence.",
                "Another test sentence for embedding.",
                "The quick brown fox jumps over the lazy dog."
            ]
            
            result = await embedding_tool.embed_texts(test_texts)
            
            if result.success:
                self.console.logger.info(f"✅ Simple embedding successful: {result.data['total_generated']} embeddings")
                self.console.logger.info(f"   Dimension: {result.data['embedding_dimension']}")
                
                # Test similarity
                embeddings = result.data['embeddings']
                if len(embeddings) >= 2:
                    similarity_result = await embedding_tool.compute_similarity(
                        embedding1=embeddings[0]['embedding'],
                        embedding2=embeddings[1]['embedding']
                    )
                    
                    if similarity_result.success:
                        self.console.logger.info(f"✅ Similarity computation: {similarity_result.data['similarity']:.4f}")
                
                self.test_results.append({
                    "component": "Simple Embedding System",
                    "status": "✅ WORKING",
                    "details": f"Generated {result.data['total_generated']} embeddings with {result.data['embedding_dimension']} dimensions"
                })
            else:
                self.test_results.append({
                    "component": "Simple Embedding System",
                    "status": "❌ FAILED",
                    "details": result.message
                })
                
        except Exception as e:
            self.test_results.append({
                "component": "Simple Embedding System",
                "status": "❌ ERROR",
                "details": str(e)
            })
    
    async def test_sql_database(self) -> Any:
        """Test SQL database functionality"""
        self.console.logger.info("\n[bold green]🗄️ Testing SQL Database System...[/bold green]")
        
        try:
            sql_db = SQLDatabaseTool()
            
            # Test persona storage
            persona_data = {
                "name": f"Test Persona {int(time.time())}",  # Use timestamp for unique names
                "description": "A test persona for validation",
                "personality_traits": {"traits": ["helpful", "friendly"]},
                "knowledge_base": {"domains": ["testing"]},
                "conversation_style": {"greeting": "Hello!"}
            }
            
            result = await sql_db.execute(
                operation="store_persona",
                **persona_data
            )
            
            if result.success:
                self.console.logger.info(f"✅ Persona storage successful")
                
                # Test persona retrieval
                retrieve_result = await sql_db.execute(
                    operation="get_persona",
                    persona_id=result.data["persona_id"]
                )
                
                if retrieve_result.success:
                    self.console.logger.info(f"✅ Persona retrieval successful")
                    self.test_results.append({
                        "component": "SQL Database System",
                        "status": "✅ WORKING",
                        "details": "Persona storage and retrieval working correctly"
                    })
                else:
                    self.test_results.append({
                        "component": "SQL Database System",
                        "status": "⚠️ PARTIAL",
                        "details": f"Storage works, retrieval failed: {retrieve_result.message}"
                    })
            else:
                self.test_results.append({
                    "component": "SQL Database System",
                    "status": "❌ FAILED",
                    "details": result.message
                })
                
        except Exception as e:
            self.test_results.append({
                "component": "SQL Database System",
                "status": "❌ ERROR",
                "details": str(e)
            })
    
    def test_api_keys(self) -> Any:
        """Test API key configuration"""
        self.console.logger.info("\n[bold green]🔑 Testing API Key Configuration...[/bold green]")
        
        try:
            # Check DeepSeek API key
            deepseek_valid = is_deepseek_key_valid()
            
            if deepseek_valid:
                self.console.logger.info("✅ DeepSeek API key appears valid")
                self.test_results.append({
                    "component": "DeepSeek API Key",
                    "status": "✅ VALID",
                    "details": "API key format is correct"
                })
            else:
                self.console.logger.info("❌ DeepSeek API key is invalid or expired")
                self.test_results.append({
                    "component": "DeepSeek API Key",
                    "status": "❌ INVALID",
                    "details": "API key needs to be updated"
                })
                
        except Exception as e:
            self.test_results.append({
                "component": "API Key Configuration",
                "status": "❌ ERROR",
                "details": str(e)
            })
    
    def print_summary(self) -> Any:
        """Print comprehensive test summary"""
        self.console.logger.info("\n[bold cyan]📊 Final System Test Summary[/bold cyan]")
        
        table = Table(title="System Component Status")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Details", style="white")
        
        working_count = 0
        total_count = len(self.test_results)
        
        for result in self.test_results:
            status_style = "green" if "✅" in result["status"] else "red" if "❌" in result["status"] else "yellow"
            table.add_row(
                result["component"],
                f"[{status_style}]{result['status']}[/{status_style}]",
                result["details"]
            )
            
            if "✅" in result["status"]:
                working_count += 1
        
        self.console.logger.info(table)
        
        # Overall status
        success_rate = (working_count / total_count) * 100
        self.console.logger.info(f"\n[bold]Overall Status: {working_count}/{total_count} components working ({success_rate:.1f}%)[/bold]")
        
        if success_rate >= 80:
            self.console.logger.info("\n[bold green]🎉 System is mostly functional![/bold green]")
        elif success_rate >= 50:
            self.console.logger.info("\n[bold yellow]⚠️ System is partially functional. Some components need attention.[/bold yellow]")
        else:
            self.console.logger.info("\n[bold red]❌ System needs significant attention.[/bold red]")
    
    def print_fix_instructions(self) -> Any:
        """Print instructions for fixing issues"""
        self.console.logger.info("\n[bold cyan]🔧 Fix Instructions[/bold cyan]")
        
        # Check for specific issues
        has_api_issues = any("❌" in result["status"] and "API" in result["component"] for result in self.test_results)
        has_db_issues = any("❌" in result["status"] and "Database" in result["component"] for result in self.test_results)
        
        if has_api_issues:
            self.console.logger.info("\n[bold yellow]🔑 To fix API key issues:[/bold yellow]")
            self.console.logger.info("1. Run: python update_api_key.py")
            self.console.logger.info("2. Or set environment variable: DEEPSEEK_API_KEY=your_key_here")
            self.console.logger.info("3. Get a key from: https://platform.deepseek.com")
        
        if has_db_issues:
            self.console.logger.info("\n[bold yellow]🗄️ To fix database issues:[/bold yellow]")
            self.console.logger.info("1. Check if SQLite is working properly")
            self.console.logger.info("2. Verify database file permissions")
            self.console.logger.info("3. Check for any missing dependencies")
        
        # General instructions
        self.console.logger.info("\n[bold green]🚀 Next Steps:[/bold green]")
        self.console.logger.info("1. Update your DeepSeek API key for full functionality")
        self.console.logger.info("2. Install Qdrant for vector database features (optional)")
        self.console.logger.info("3. Run: python test_core_features.py for detailed testing")
        self.console.logger.info("4. Check the documentation for advanced features")
    
    async def run_all_tests(self) -> Any:
        """Run all tests"""
        self.console.logger.info(Panel(
            "[bold cyan]Final System Test Suite[/bold cyan]\n"
            "Comprehensive testing of all working components",
            title="[bold cyan]Final System Test[/bold cyan]",
            border_style="cyan"
        ))
        
        # Run tests
        await self.test_simple_embeddings()
        await self.test_sql_database()
        self.test_api_keys()
        
        # Print results
        self.print_summary()
        self.print_fix_instructions()

async def main() -> None:
    """Main test function"""
    console = Console()
    
    console.logger.info(Panel(
        "[bold cyan]Final System Test Suite[/bold cyan]\n"
        "Comprehensive testing of all working components",
        title="[bold cyan]Final System Test[/bold cyan]",
        border_style="cyan"
    ))
    
    # Create and run tester
    tester = FinalSystemTester()
    await tester.run_all_tests()
    
    console.logger.info("\n[bold green]Final system test completed![/bold green]")

if __name__ == "__main__":
    asyncio.run(main()) 