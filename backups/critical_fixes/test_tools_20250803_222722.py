#!/usr/bin/env python3
"""
Test Tools Script for BASED CODER CLI
Tests all tools to ensure they are properly wired and working
"""

import asyncio
from typing import List, Dict, Any, Optional, Tuple

import logging

import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from tools.base_tool import ToolResponse
from tools.sql_database_tool import SQLDatabaseTool
from tools.simple_embedding_tool import SimpleEmbeddingTool
from tools.llm_query_tool import LLMQueryTool
from tools.fim_completion_tool import FIMCompletionTool
from tools.prefix_completion_tool import PrefixCompletionTool
from tools.rag_pipeline_tool import RAGPipelineTool
from tools.reasoning_engine import FastReasoningEngine
from tools.memory_tool import MemoryTool
from tools.vector_database_tool import VectorDatabaseTool
from tools.deepseek_coder_tool import DeepSeekCoderTool
from tools.tool_manager import ToolManager

console = Console()

class ToolTester:
    """Test all tools in the BASED CODER CLI"""
    
    def __init__(self) -> Any:
        self.results = {}
        self.tools = {}
    
    async def test_all_tools(self) -> Any:
        """Test all available tools"""
        console.print(Panel.fit(
            "[bold blue]Testing BASED CODER CLI Tools[/bold blue]\n"
            "Running comprehensive tool tests...",
            title="Tool Test Suite"
        ))
        
        # Test each tool
        await self.test_sql_database()
        await self.test_embedding_tool()
        await self.test_llm_tool()
        await self.test_fim_completion()
        await self.test_prefix_completion()
        await self.test_rag_pipeline()
        await self.test_reasoning_engine()
        await self.test_memory_tool()
        await self.test_vector_database()
        await self.test_deepseek_coder()
        await self.test_tool_manager()
        
        # Display results
        self.display_results()
    
    async def test_sql_database(self) -> Any:
        """Test SQL Database Tool"""
        try:
            tool = SQLDatabaseTool()
            await tool._initialize_database()
            
            # Test storing a conversation
            result = await tool.execute(
                operation="store_conversation",
                session_id="test_session",
                user_input="Hello",
                assistant_response="Hi there!",
                persona_id=1
            )
            
            self.results["SQL Database"] = {
                "status": "✅ PASS" if result.success else "❌ FAIL",
                "message": result.message
            }
            self.tools["SQL Database"] = tool
            
        except Exception as e:
            self.results["SQL Database"] = {
                "status": "❌ FAIL",
                "message": str(e)
            }
    
    async def test_embedding_tool(self) -> Any:
        """Test Simple Embedding Tool"""
        try:
            tool = SimpleEmbeddingTool()
            
            # Test embedding creation using the correct method
            result = await tool.embed_text("test text")
            
            if result.success:
                embedding = result.data.get('embedding', [])
                self.results["Embedding Tool"] = {
                    "status": "✅ PASS",
                    "message": f"Created embedding with {len(embedding)} dimensions"
                }
            else:
                self.results["Embedding Tool"] = {
                    "status": "❌ FAIL",
                    "message": result.message
                }
            
            self.tools["Embedding Tool"] = tool
            
        except Exception as e:
            self.results["Embedding Tool"] = {
                "status": "❌ FAIL",
                "message": str(e)
            }
    
    async def test_llm_tool(self) -> Any:
        """Test LLM Query Tool"""
        try:
            tool = LLMQueryTool()
            
            # Test with a simple query (will fail if no API key)
            result = await tool.execute(
                operation="chat",
                message="Hello",
                model="deepseek-chat"
            )
            
            if result.success:
                self.results["LLM Query Tool"] = {
                    "status": "✅ PASS",
                    "message": "Successfully connected to DeepSeek API"
                }
            else:
                self.results["LLM Query Tool"] = {
                    "status": "⚠️ WARNING",
                    "message": result.message
                }
            
            self.tools["LLM Query Tool"] = tool
            
        except Exception as e:
            self.results["LLM Query Tool"] = {
                "status": "❌ FAIL",
                "message": str(e)
            }
    
    async def test_fim_completion(self) -> Any:
        """Test FIM Completion Tool"""
        try:
            tool = FIMCompletionTool()
            
            # Test FIM completion
            result = await tool.execute(
                operation="complete",
                prefix="def hello() -> None:",
                suffix="logging.info('world')",
                language="python"
            )
            
            self.results["FIM Completion"] = {
                "status": "✅ PASS" if result.success else "❌ FAIL",
                "message": result.message
            }
            self.tools["FIM Completion"] = tool
            
        except Exception as e:
            self.results["FIM Completion"] = {
                "status": "❌ FAIL",
                "message": str(e)
            }
    
    async def test_prefix_completion(self) -> Any:
        """Test Prefix Completion Tool"""
        try:
            tool = PrefixCompletionTool()
            
            # Test prefix completion
            result = await tool.execute(
                operation="complete",
                prefix="def calculate_sum(",
                language="python"
            )
            
            self.results["Prefix Completion"] = {
                "status": "✅ PASS" if result.success else "❌ FAIL",
                "message": result.message
            }
            self.tools["Prefix Completion"] = tool
            
        except Exception as e:
            self.results["Prefix Completion"] = {
                "status": "❌ FAIL",
                "message": str(e)
            }
    
    async def test_rag_pipeline(self) -> Any:
        """Test RAG Pipeline Tool"""
        try:
            tool = RAGPipelineTool()
            
            # Test RAG query using the correct operation
            result = await tool.execute(
                operation="rag_query",
                query="What is Python?",
                documents=["Python is a programming language."]
            )
            
            self.results["RAG Pipeline"] = {
                "status": "✅ PASS" if result.success else "❌ FAIL",
                "message": result.message
            }
            self.tools["RAG Pipeline"] = tool
            
        except Exception as e:
            self.results["RAG Pipeline"] = {
                "status": "❌ FAIL",
                "message": str(e)
            }
    
    async def test_reasoning_engine(self) -> Any:
        """Test Reasoning Engine"""
        try:
            # Create LLM tool for reasoning engine
            llm_tool = LLMQueryTool()
            tool = FastReasoningEngine(llm_tool=llm_tool)
            
            # Test reasoning with required parameters
            result = await tool.execute(
                user_query="What is 2 + 2?",
                context={"task": "Basic arithmetic"},
                max_iterations=3,
                speed_mode=True
            )
            
            self.results["Reasoning Engine"] = {
                "status": "✅ PASS" if result.success else "❌ FAIL",
                "message": result.message
            }
            self.tools["Reasoning Engine"] = tool
            
        except Exception as e:
            self.results["Reasoning Engine"] = {
                "status": "❌ FAIL",
                "message": str(e)
            }
    
    async def test_memory_tool(self) -> Any:
        """Test Memory Tool"""
        try:
            tool = MemoryTool()
            
            # Test memory storage
            result = await tool.execute(
                operation="store",
                content="Test memory entry",
                category="test",
                importance=5
            )
            
            self.results["Memory Tool"] = {
                "status": "✅ PASS" if result.success else "❌ FAIL",
                "message": result.message
            }
            self.tools["Memory Tool"] = tool
            
        except Exception as e:
            self.results["Memory Tool"] = {
                "status": "❌ FAIL",
                "message": str(e)
            }
    
    async def test_vector_database(self) -> Any:
        """Test Vector Database Tool"""
        try:
            tool = VectorDatabaseTool()
            
            # Test vector database operations with a valid operation
            result = await tool.execute(
                operation="store",
                content="test content",
                metadata={"test": "data"}
            )
            
            if result.success:
                self.results["Vector Database"] = {
                    "status": "✅ PASS",
                    "message": "Vector database is available"
                }
            else:
                self.results["Vector Database"] = {
                    "status": "⚠️ WARNING",
                    "message": result.message
                }
            
            self.tools["Vector Database"] = tool
            
        except Exception as e:
            self.results["Vector Database"] = {
                "status": "❌ FAIL",
                "message": str(e)
            }
    
    async def test_deepseek_coder(self) -> Any:
        """Test DeepSeek Coder Tool"""
        try:
            tool = DeepSeekCoderTool()
            
            # Test code generation using the correct operation
            result = await tool.execute(
                operation="code_generation",
                prompt="Create a simple Python function",
                language="python"
            )
            
            if result.success:
                self.results["DeepSeek Coder"] = {
                    "status": "✅ PASS",
                    "message": "Successfully connected to DeepSeek Coder"
                }
            else:
                self.results["DeepSeek Coder"] = {
                    "status": "⚠️ WARNING",
                    "message": result.message
                }
            
            self.tools["DeepSeek Coder"] = tool
            
        except Exception as e:
            self.results["DeepSeek Coder"] = {
                "status": "❌ FAIL",
                "message": str(e)
            }
    
    async def test_tool_manager(self) -> Any:
        """Test Tool Manager"""
        try:
            tool = ToolManager()
            
            # Test tool listing
            tools = tool.list_tools()
            
            self.results["Tool Manager"] = {
                "status": "✅ PASS",
                "message": f"Registered {len(tools)} tools"
            }
            self.tools["Tool Manager"] = tool
            
        except Exception as e:
            self.results["Tool Manager"] = {
                "status": "❌ FAIL",
                "message": str(e)
            }
    
    def display_results(self) -> Any:
        """Display test results"""
        table = Table(title="Tool Test Results")
        table.add_column("Tool", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Message", style="green")
        
        for tool_name, result in self.results.items():
            status_color = "green" if "PASS" in result["status"] else "red" if "FAIL" in result["status"] else "yellow"
            table.add_row(
                tool_name,
                f"[{status_color}]{result['status']}[/{status_color}]",
                result["message"]
            )
        
        console.logging.info(table)
        
        # Summary
        passed = sum(1 for r in self.results.values() if "PASS" in r["status"])
        failed = sum(1 for r in self.results.values() if "FAIL" in r["status"])
        warnings = sum(1 for r in self.results.values() if "WARNING" in r["status"])
        
        console.print(Panel.fit(
            f"[bold]Test Summary:[/bold]\n"
            f"✅ Passed: {passed}\n"
            f"⚠️ Warnings: {warnings}\n"
            f"❌ Failed: {failed}\n"
            f"Total Tools: {len(self.results)}",
            title="Test Summary"
        ))

async def main() -> None:
    """Main test function"""
    tester = ToolTester()
    await tester.test_all_tools()

if __name__ == "__main__":
    asyncio.run(main()) 