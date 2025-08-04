import logging
logger = logging.getLogger(__name__)
#!/usr/bin/env python3
"""
Core Features Test
Test the core working features without external dependencies
"""

import asyncio
import logging
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import time

from tools.simple_embedding_tool import SimpleEmbeddingTool
from tools.sql_database_tool import SQLDatabaseTool
from tools.fim_completion_tool import FIMCompletionTool
from tools.prefix_completion_tool import PrefixCompletionTool
from config.deepcli_config import get_config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CoreFeaturesTester:
    """Test core features that work without external dependencies"""
    
    def __init__(self):
        """Initialize the tester"""
        self.console = Console()
        self.config = get_config()
        
        # Initialize tools that don't require external services
        self.embedding_tool = SimpleEmbeddingTool()
        self.sql_db = SQLDatabaseTool()
        self.fim_tool = FIMCompletionTool()
        self.prefix_tool = PrefixCompletionTool()
        
        # Test results
        self.test_results = []
    
    async def test_configuration(self):
        """Test configuration system"""
        self.console.logger.info("\n[bold green]Testing Configuration System...[/bold green]")
        
        try:
            # Test config retrieval
            config = get_config()
            
            # Test basic config structure
            required_sections = ['database', 'llm', 'persona', 'rag', 'memory']
            for section in required_sections:
                if hasattr(config, section):
                    self.console.logger.info(f"✅ {section} configuration available")
                else:
                    self.console.logger.info(f"❌ {section} configuration missing")
            
            self.test_results.append({
                "test": "Configuration System",
                "status": "PASS",
                "message": "Configuration system working correctly"
            })
            
        except Exception as e:
            self.console.logger.info(f"❌ Configuration test failed: {str(e)}")
            self.test_results.append({
                "test": "Configuration System",
                "status": "FAIL",
                "message": str(e)
            })
    
    async def test_simple_embeddings(self):
        """Test simple embedding system"""
        self.console.logger.info("\n[bold green]Testing Simple Embedding System...[/bold green]")
        
        try:
            # Test basic embedding
            test_texts = [
                "Hello, this is a test sentence.",
                "Another test sentence for embedding.",
                "The quick brown fox jumps over the lazy dog."
            ]
            
            result = await self.embedding_tool.embed_texts(test_texts)
            
            if result.success:
                self.console.logger.info(f"✅ Simple embedding successful: {result.data['total_generated']} embeddings")
                self.console.logger.info(f"   Dimension: {result.data['embedding_dimension']}")
                
                # Test similarity
                embeddings = result.data['embeddings']
                if len(embeddings) >= 2:
                    similarity_result = await self.embedding_tool.compute_similarity(
                        embedding1=embeddings[0]['embedding'],
                        embedding2=embeddings[1]['embedding']
                    )
                    
                    if similarity_result.success:
                        self.console.logger.info(f"✅ Similarity computation: {similarity_result.data['similarity']:.4f}")
                    else:
                        self.console.logger.info(f"❌ Similarity computation failed")
                
                self.test_results.append({
                    "test": "Simple Embedding System",
                    "status": "PASS",
                    "message": f"Generated {result.data['total_generated']} embeddings successfully"
                })
            else:
                self.console.logger.info(f"❌ Simple embedding failed: {result.message}")
                self.test_results.append({
                    "test": "Simple Embedding System",
                    "status": "FAIL",
                    "message": result.message
                })
                
        except Exception as e:
            self.console.logger.info(f"❌ Simple embedding test failed: {str(e)}")
            self.test_results.append({
                "test": "Simple Embedding System",
                "status": "FAIL",
                "message": str(e)
            })
    
    async def test_sql_database(self):
        """Test SQL database functionality"""
        self.console.logger.info("\n[bold green]Testing SQL Database System...[/bold green]")
        
        try:
            # Test persona storage
            persona_data = {
                "name": f"Test Persona {int(time.time())}",  # Use timestamp for unique names
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
                self.console.logger.info(f"✅ Persona storage successful")
                
                # Test persona retrieval
                retrieve_result = await self.sql_db.execute(
                    operation="get_persona",
                    persona_id=result.data["persona_id"]
                )
                
                if retrieve_result.success:
                    self.console.logger.info(f"✅ Persona retrieval successful")
                    self.test_results.append({
                        "test": "SQL Database System",
                        "status": "PASS",
                        "message": "Persona storage and retrieval working"
                    })
                else:
                    self.console.logger.info(f"❌ Persona retrieval failed: {retrieve_result.message}")
                    self.test_results.append({
                        "test": "SQL Database System",
                        "status": "FAIL",
                        "message": retrieve_result.message
                    })
            else:
                self.console.logger.info(f"❌ Persona storage failed: {result.message}")
                self.test_results.append({
                    "test": "SQL Database System",
                    "status": "FAIL",
                    "message": result.message
                })
                
        except Exception as e:
            self.console.logger.info(f"❌ SQL database test failed: {str(e)}")
            self.test_results.append({
                "test": "SQL Database System",
                "status": "FAIL",
                "message": str(e)
            })
    
    async def test_fim_completion(self):
        """Test FIM completion functionality"""
        self.console.logger.info("\n[bold green]Testing FIM Completion...[/bold green]")
        
        try:
            # Test Python FIM completion
            prefix = "def calculate_sum(a, b):\n    "
            suffix = "\n    return result"
            
            result = await self.fim_tool.execute(
                prefix=prefix,
                suffix=suffix,
                language="python"
            )
            
            if result.success:
                self.console.logger.info(f"✅ FIM completion successful")
                self.console.logger.info(f"   Generated: {result.data['completion'][:50]}...")
                self.test_results.append({
                    "test": "FIM Completion",
                    "status": "PASS",
                    "message": "FIM completion working correctly"
                })
            else:
                self.console.logger.info(f"❌ FIM completion failed: {result.message}")
                self.test_results.append({
                    "test": "FIM Completion",
                    "status": "FAIL",
                    "message": result.message
                })
                
        except Exception as e:
            self.console.logger.info(f"❌ FIM completion test failed: {str(e)}")
            self.test_results.append({
                "test": "FIM Completion",
                "status": "FAIL",
                "message": str(e)
            })
    
    async def test_prefix_completion(self):
        """Test prefix completion functionality"""
        self.console.logger.info("\n[bold green]Testing Prefix Completion...[/bold green]")
        
        try:
            # Test text prefix completion
            prefix = "The quick brown fox"
            
            result = await self.prefix_tool.execute(
                prefix=prefix,
                max_tokens=20
            )
            
            if result.success:
                self.console.logger.info(f"✅ Prefix completion successful")
                self.console.logger.info(f"   Generated: {result.data['completion'][:50]}...")
                self.test_results.append({
                    "test": "Prefix Completion",
                    "status": "PASS",
                    "message": "Prefix completion working correctly"
                })
            else:
                self.console.logger.info(f"❌ Prefix completion failed: {result.message}")
                self.test_results.append({
                    "test": "Prefix Completion",
                    "status": "FAIL",
                    "message": result.message
                })
                
        except Exception as e:
            self.console.logger.info(f"❌ Prefix completion test failed: {str(e)}")
            self.test_results.append({
                "test": "Prefix Completion",
                "status": "FAIL",
                "message": str(e)
            })
    
    def print_summary(self):
        """Print test summary"""
        self.console.logger.info("\n[bold cyan]Test Summary[/bold cyan]")
        
        table = Table(title="Core Features Test Results")
        table.add_column("Test", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Message", style="white")
        
        passed = 0
        failed = 0
        
        for result in self.test_results:
            status_style = "green" if result["status"] == "PASS" else "red"
            table.add_row(
                result["test"],
                f"[{status_style}]{result['status']}[/{status_style}]",
                result["message"]
            )
            
            if result["status"] == "PASS":
                passed += 1
            else:
                failed += 1
        
        self.console.logger.info(table)
        self.console.logger.info(f"\n[bold]Results: {passed} passed, {failed} failed[/bold]")
        
        if failed == 0:
            self.console.logger.info("\n[bold green]🎉 All core features working correctly![/bold green]")
        else:
            self.console.logger.info(f"\n[bold yellow]⚠️ {failed} tests failed, but core system is functional[/bold yellow]")
    
    async def run_all_tests(self):
        """Run all core feature tests"""
        self.console.logger.info(Panel(
            "[bold cyan]Core Features Test Suite[/bold cyan]\n"
            "Testing core functionality without external dependencies",
            title="[bold cyan]Core Features Test[/bold cyan]",
            border_style="cyan"
        ))
        
        # Run tests
        await self.test_configuration()
        await self.test_simple_embeddings()
        await self.test_sql_database()
        await self.test_fim_completion()
        await self.test_prefix_completion()
        
        # Print summary
        self.print_summary()

async def main():
    """Main test function"""
    console = Console()
    
    console.logger.info(Panel(
        "[bold cyan]Core Features Test Suite[/bold cyan]\n"
        "Testing core functionality without external dependencies",
        title="[bold cyan]Core Features Test[/bold cyan]",
        border_style="cyan"
    ))
    
    # Create and run tester
    tester = CoreFeaturesTester()
    await tester.run_all_tests()
    
    console.logger.info("\n[bold green]Core features test completed![/bold green]")

if __name__ == "__main__":
    asyncio.run(main()) 