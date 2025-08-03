"""
Enhanced BASED GOD CLI with Modular Tools and LangChain Integration
Inspired by Agent Zero architecture with separate tool files
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

# Import the modular tool system
from tools import ToolManager, ToolResponse

# Rich for enhanced output (optional)
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None

class ActionType(Enum):
    DIRECT_RESPONSE = "direct_response"
    TOOL_EXECUTION = "tool_execution"
    WORKFLOW_EXECUTION = "workflow_execution"
    MULTI_TOOL_PROCESS = "multi_tool_process"
    LEARNING_UPDATE = "learning_update"

class ConfidenceLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

@dataclass
class ReasoningContext:
    user_input: str
    conversation_history: List[Dict]
    available_tools: List[str]
    session_data: Dict[str, Any]
    timestamp: str

@dataclass
class ActionPlan:
    plan_id: str
    primary_action: ActionType
    tools_to_use: List[str]
    parameters: Dict[str, Any]
    estimated_time: int
    confidence: ConfidenceLevel
    reasoning: str
    fallback_plan: Optional[str] = None

class EnhancedBasedGodCLI:
    """
    Enhanced BASED GOD CLI with modular tools and LangChain integration
    """
    
    def __init__(self):
        self.tool_manager = ToolManager()
        self.conversation_history = []
        self.session_data = {}
        self.last_action_plan = None
        self.startup_time = datetime.now()
        
        # Initialize session
        self._initialize_session()
    
    def _initialize_session(self):
        """Initialize CLI session"""
        self.session_data = {
            "session_id": self._generate_session_id(),
            "started_at": self.startup_time.isoformat(),
            "total_interactions": 0,
            "successful_operations": 0,
            "failed_operations": 0
        }
        
        if RICH_AVAILABLE:
            self._display_startup_banner()
        else:
            self._display_simple_banner()
    
    def _display_startup_banner(self):
        """Display rich startup banner"""
        banner_text = """
[bold cyan]🚀 ENHANCED BASED GOD CLI v2.0[/bold cyan]
[bold]Powered by Agent Zero Intelligence & LangChain[/bold]

[dim]✅ Modular Tool Architecture
✅ LangChain LLM Integration  
✅ Agent Zero Reasoning Patterns
✅ Persistent Memory System
✅ Advanced Web Scraping
✅ Code Generation & Analysis[/dim]

[bold yellow]Available Tools:[/bold yellow]
"""
        
        tools = self.tool_manager.list_tools()
        for tool in tools:
            banner_text += f"[green]• {tool['name']}[/green]: {tool['description'][:60]}...\n"
        
        banner_text += f"\n[bold]Session ID:[/bold] [cyan]{self.session_data['session_id']}[/cyan]"
        
        console.print(Panel(banner_text, title="[bold white]ENHANCED BASED GOD CLI[/bold white]", border_style="cyan"))
    
    def _display_simple_banner(self):
        """Display simple text banner"""
        print("=" * 80)
        print("🚀 ENHANCED BASED GOD CLI v2.0")
        print("Powered by Agent Zero Intelligence & LangChain")
        print("=" * 80)
        print("✅ Modular Tool Architecture")
        print("✅ LangChain LLM Integration") 
        print("✅ Agent Zero Reasoning Patterns")
        print("✅ Persistent Memory System")
        print("✅ Advanced Web Scraping")
        print("✅ Code Generation & Analysis")
        print("=" * 80)
        
        tools = self.tool_manager.list_tools()
        print(f"Available Tools ({len(tools)}):")
        for tool in tools:
            print(f"  • {tool['name']}: {tool['description'][:60]}...")
        
        print(f"\nSession ID: {self.session_data['session_id']}")
        print("=" * 80)
    
    async def chat(self, user_input: str) -> str:
        """Main chat interface with enhanced reasoning"""
        
        # Store user input in conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        
        # Enhance with RAG - retrieve relevant context from memory
        relevant_context = await self._retrieve_rag_context(user_input)
        
        # Create reasoning context with RAG enhancement
        context = ReasoningContext(
            user_input=user_input,
            conversation_history=self.conversation_history[-10:],  # Last 10 messages
            available_tools=list(self.tool_manager.tools.keys()),
            session_data={**self.session_data, "rag_context": relevant_context},
            timestamp=datetime.now().isoformat()
        )
        
        # Analyze and plan
        action_plan = await self._create_action_plan(context)
        self.last_action_plan = action_plan
        
        # Display reasoning if rich available
        if RICH_AVAILABLE:
            self._display_reasoning_process(action_plan)
        
        # Execute plan
        response = await self._execute_action_plan(action_plan, context)
        
        # Update conversation history
        self.conversation_history.append({
            "timestamp": context.timestamp,
            "user_input": user_input,
            "response": response,
            "action_plan": action_plan,
            "success": "error" not in response.lower()
        })
        
        # Update session stats
        self.session_data["total_interactions"] += 1
        if "error" not in response.lower():
            self.session_data["successful_operations"] += 1
        else:
            self.session_data["failed_operations"] += 1
        
        # Store in memory
        await self._store_interaction_memory(user_input, response, action_plan)
        
        return response
    
    def chat_sync(self, user_input: str) -> str:
        """Synchronous wrapper for chat"""
        return asyncio.run(self.chat(user_input))
    
    async def _create_action_plan(self, context: ReasoningContext) -> ActionPlan:
        """Create action plan using fast iterative reasoning with LLM consultation loops"""
        
        # Use the fast reasoning engine for intelligent planning
        reasoning_result = await self.tool_manager.execute_tool(
            "fast_reasoning_engine",
            user_query=context.user_input,
            context={
                "conversation_history": context.conversation_history,
                "available_tools": context.available_tools,
                "session_data": context.session_data
            },
            max_iterations=4,  # Fast iterations
            speed_mode=True    # Enable speed optimizations
        )
        
        if reasoning_result.success:
            # Extract decision from reasoning engine
            final_decision = reasoning_result.data.get("final_decision", {})
            
            # Convert reasoning engine output to ActionPlan
            return ActionPlan(
                plan_id=self._generate_plan_id(),
                primary_action=self._map_decision_to_action_type(final_decision.get("decision_type", "tool_execution")),
                tools_to_use=final_decision.get("selected_tools", ["llm_query_tool"]),
                parameters=final_decision.get("parameters", {"query": context.user_input}),
                estimated_time=int(reasoning_result.data.get("execution_time", 8) * 1.5),  # Add buffer
                confidence=self._map_confidence_to_level(final_decision.get("confidence_score", 0.7)),
                reasoning=final_decision.get("reasoning_summary", "Fast iterative reasoning analysis completed"),
                fallback_plan="llm_query_tool"
            )
        
        else:
            # Fallback to simple keyword-based planning if reasoning engine fails
            return await self._create_fallback_action_plan(context)
    
    def _map_decision_to_action_type(self, decision_type: str) -> ActionType:
        """Map reasoning engine decision type to ActionType"""
        mapping = {
            "tool_execution": ActionType.TOOL_EXECUTION,
            "multi_tool_process": ActionType.MULTI_TOOL_PROCESS,
            "workflow_execution": ActionType.WORKFLOW_EXECUTION,
            "direct_response": ActionType.DIRECT_RESPONSE,
            "deepseek_conversation_flow": ActionType.TOOL_EXECUTION  # Use tool execution for DeepSeek flow
        }
        return mapping.get(decision_type, ActionType.TOOL_EXECUTION)
    
    def _map_confidence_to_level(self, confidence_score: float) -> ConfidenceLevel:
        """Map numerical confidence to ConfidenceLevel enum"""
        if confidence_score >= 0.9:
            return ConfidenceLevel.VERY_HIGH
        elif confidence_score >= 0.75:
            return ConfidenceLevel.HIGH
        elif confidence_score >= 0.6:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW
    
    async def _create_fallback_action_plan(self, context: ReasoningContext) -> ActionPlan:
        """Fallback action plan creation using keyword analysis"""
        
        user_input = context.user_input.lower()
        
        # Quick keyword-based analysis for fallback
        if any(keyword in user_input for keyword in ["scrape", "web", "crawl"]):
            return ActionPlan(
                plan_id=self._generate_plan_id(),
                primary_action=ActionType.TOOL_EXECUTION,
                tools_to_use=["web_scraper"],
                parameters=self._extract_scraping_parameters(context.user_input),
                estimated_time=15,
                confidence=ConfidenceLevel.MEDIUM,
                reasoning="Fallback: Web scraping detected via keywords"
            )
        
        elif any(keyword in user_input for keyword in ["code", "function", "script"]):
            return ActionPlan(
                plan_id=self._generate_plan_id(),
                primary_action=ActionType.TOOL_EXECUTION,
                tools_to_use=["code_generator"],
                parameters=self._extract_code_parameters(context.user_input),
                estimated_time=10,
                confidence=ConfidenceLevel.MEDIUM,
                reasoning="Fallback: Code generation detected via keywords"
            )
        
        elif any(keyword in user_input for keyword in ["analyze", "data", "csv"]):
            return ActionPlan(
                plan_id=self._generate_plan_id(),
                primary_action=ActionType.TOOL_EXECUTION,
                tools_to_use=["data_analyzer"],
                parameters=self._extract_analysis_parameters(context.user_input),
                estimated_time=8,
                confidence=ConfidenceLevel.MEDIUM,
                reasoning="Fallback: Data analysis detected via keywords"
            )
        
        # Default fallback
        return ActionPlan(
            plan_id=self._generate_plan_id(),
            primary_action=ActionType.TOOL_EXECUTION,
            tools_to_use=["llm_query_tool"],
            parameters={"query": context.user_input, "task_type": "general"},
            estimated_time=8,
            confidence=ConfidenceLevel.LOW,
            reasoning="Fallback: Default LLM query"
        )
    
    async def _execute_action_plan(self, plan: ActionPlan, context: ReasoningContext) -> str:
        """Execute the action plan"""
        
        try:
            if plan.primary_action == ActionType.TOOL_EXECUTION:
                return await self._execute_single_tool(plan, context)
            
            elif plan.primary_action == ActionType.MULTI_TOOL_PROCESS:
                return await self._execute_multi_tool_process(plan, context)
            
            elif plan.primary_action == ActionType.WORKFLOW_EXECUTION:
                return await self._execute_workflow(plan, context)
            
            else:
                return "I understand your request, but I need more specific instructions to help you. Could you please provide more details?"
        
        except Exception as e:
            return f"❌ An error occurred while processing your request: {str(e)}\n\nPlease try rephrasing your request or use the 'help' command."
    
    async def _execute_single_tool(self, plan: ActionPlan, context: ReasoningContext) -> str:
        """Execute a single tool"""
        
        if not plan.tools_to_use:
            return "❌ No tools specified in action plan"
        
        tool_name = plan.tools_to_use[0]
        
        # Show progress if rich available
        if RICH_AVAILABLE:
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
                task = progress.add_task(f"Executing {tool_name}...", total=None)
                result = await self.tool_manager.execute_tool(tool_name, **plan.parameters)
        else:
            print(f"🔧 Executing {tool_name}...")
            result = await self.tool_manager.execute_tool(tool_name, **plan.parameters)
        
        return self._format_tool_response(result, tool_name)
    
    async def _execute_multi_tool_process(self, plan: ActionPlan, context: ReasoningContext) -> str:
        """Execute multiple tools in sequence"""
        
        responses = []
        
        for tool_name in plan.tools_to_use:
            if RICH_AVAILABLE:
                console.print(f"[cyan]🔧 Executing {tool_name}...[/cyan]")
            else:
                print(f"🔧 Executing {tool_name}...")
            
            # Customize parameters for each tool
            tool_params = self._customize_parameters_for_tool(tool_name, plan.parameters, context)
            
            result = await self.tool_manager.execute_tool(tool_name, **tool_params)
            formatted_response = self._format_tool_response(result, tool_name)
            responses.append(f"**{tool_name.title()}:**\n{formatted_response}")
        
        return "\n\n".join(responses)
    
    async def _execute_workflow(self, plan: ActionPlan, context: ReasoningContext) -> str:
        """Execute a predefined workflow"""
        
        # This would contain predefined workflows
        return "Workflow execution not yet implemented"
    
    def _format_tool_response(self, result: ToolResponse, tool_name: str) -> str:
        """Format tool response for display"""
        
        if not result.success:
            return f"❌ {tool_name} failed: {result.message}"
        
        response = f"✅ {result.message}\n"
        
        if result.data:
            # Tool-specific formatting
            if tool_name == "web_scraper":
                response += self._format_scraper_response(result.data)
            elif tool_name == "code_generator":
                response += self._format_code_response(result.data)
            elif tool_name == "data_analyzer":
                response += self._format_analysis_response(result.data)
            elif tool_name == "file_processor":
                response += self._format_file_response(result.data)
            elif tool_name == "memory_tool":
                response += self._format_memory_response(result.data)
            elif tool_name == "llm_query_tool":
                response += self._format_llm_response(result.data)
            else:
                response += f"Result: {result.data}"
        
        if result.metadata:
            response += f"\n\n⏱️ Execution time: {result.metadata.get('processing_time', result.execution_time):.2f}s"
        
        return response
    
    def _format_scraper_response(self, data: Dict[str, Any]) -> str:
        """Format web scraper response"""
        return f"""
🌐 **Scraped URL:** {data.get('url', 'N/A')}
📊 **Items Found:** {data.get('items_found', 0)}
🎯 **Strategy:** {data.get('scraping_strategy', 'N/A')}

**Sample Data:**
{str(data.get('extracted_data', [])[:3])[:200]}...
"""
    
    def _format_code_response(self, data: Dict[str, Any]) -> str:
        """Format code generator response"""
        code = data.get('code', '')
        return f"""
💻 **Language:** {data.get('language', 'N/A')}
📏 **Lines:** {data.get('estimated_lines', 0)}
✅ **Validation:** {'Passed' if data.get('validation', {}).get('valid', False) else 'Failed'}

**Generated Code:**
```{data.get('language', '')}
{code[:500]}...
```
"""
    
    def _format_analysis_response(self, data: Dict[str, Any]) -> str:
        """Format data analysis response"""
        results = data.get('results', {})
        return f"""
📊 **Data Format:** {data.get('format', 'N/A')}
📈 **Records:** {data.get('data_summary', {}).get('record_count', 0)}

**Analysis Results:**
{str(results)[:300]}...
"""
    
    def _format_file_response(self, data: Dict[str, Any]) -> str:
        """Format file processor response"""
        return f"""
📁 **File:** {data.get('file_path', 'N/A')}
📏 **Size:** {data.get('size_bytes', 0)} bytes
📄 **Lines:** {data.get('line_count', 0)}
"""
    
    def _format_memory_response(self, data: Dict[str, Any]) -> str:
        """Format memory tool response"""
        entries = data.get('entries', [])
        return f"""
🧠 **Memory Operation Completed**
📚 **Entries:** {len(entries)}
🔍 **Results:** {data.get('total_found', len(entries))}
"""
    
    def _format_llm_response(self, data: Dict[str, Any]) -> str:
        """Format LLM response"""
        response_text = data.get('response', '')
        return f"""
🤖 **Provider:** {data.get('provider', 'N/A')}
💭 **Response:**

{response_text}
"""
    
    def _display_reasoning_process(self, plan: ActionPlan):
        """Display the reasoning process"""
        if RICH_AVAILABLE:
            reasoning_panel = Panel(
                f"[bold yellow]🧠 Reasoning:[/bold yellow] {plan.reasoning}\n" +
                f"[bold cyan]🎯 Action:[/bold cyan] {plan.primary_action.value}\n" +
                f"[bold green]🔧 Tools:[/bold green] {', '.join(plan.tools_to_use)}\n" +
                f"[bold blue]⏱️ Estimated Time:[/bold blue] {plan.estimated_time}s\n" +
                f"[bold magenta]🎯 Confidence:[/bold magenta] {plan.confidence.value}",
                title="[bold white]Action Plan[/bold white]",
                border_style="yellow"
            )
            console.print(reasoning_panel)
        else:
            print(f"\n🧠 Reasoning: {plan.reasoning}")
            print(f"🎯 Action: {plan.primary_action.value}")
            print(f"🔧 Tools: {', '.join(plan.tools_to_use)}")
            print(f"⏱️ Estimated Time: {plan.estimated_time}s")
            print(f"🎯 Confidence: {plan.confidence.value}\n")
    
    # Parameter extraction methods
    def _extract_scraping_parameters(self, user_input: str) -> Dict[str, Any]:
        """Extract web scraping parameters"""
        import re
        
        # Try to find URL in input
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, user_input)
        
        params = {}
        if urls:
            params["url"] = urls[0]
        
        # Extract extraction type
        if "news" in user_input:
            params["extraction_type"] = "news"
        elif "product" in user_input or "shop" in user_input:
            params["extraction_type"] = "ecommerce"
        elif "link" in user_input:
            params["extraction_type"] = "links"
        else:
            params["extraction_type"] = "auto"
        
        return params
    
    def _extract_code_parameters(self, user_input: str) -> Dict[str, Any]:
        """Extract code generation parameters"""
        params = {"description": user_input}
        
        # Detect language
        if "python" in user_input.lower():
            params["language"] = "python"
        elif "javascript" in user_input.lower() or "js" in user_input.lower():
            params["language"] = "javascript"
        elif "html" in user_input.lower():
            params["language"] = "html"
        elif "css" in user_input.lower():
            params["language"] = "css"
        
        # Detect code type
        if "function" in user_input.lower():
            params["code_type"] = "function"
        elif "class" in user_input.lower():
            params["code_type"] = "class"
        elif "script" in user_input.lower():
            params["code_type"] = "script"
        
        return params
    
    def _extract_analysis_parameters(self, user_input: str) -> Dict[str, Any]:
        """Extract data analysis parameters"""
        return {"data": user_input}  # Simplified - would need more sophisticated extraction
    
    def _extract_file_parameters(self, user_input: str) -> Dict[str, Any]:
        """Extract file processing parameters"""
        params = {}
        
        # Try to extract file path
        import re
        path_pattern = r'["\']([^"\']+)["\']'
        paths = re.findall(path_pattern, user_input)
        
        if paths:
            params["file_path"] = paths[0]
        
        # Detect operation
        if "read" in user_input:
            params["operation"] = "read"
        elif "write" in user_input:
            params["operation"] = "write"
        elif "analyze" in user_input:
            params["operation"] = "analyze"
        
        return params
    
    def _extract_memory_parameters(self, user_input: str) -> Dict[str, Any]:
        """Extract memory operation parameters"""
        params = {}
        
        if "search" in user_input:
            params["operation"] = "search"
            # Extract search query
            words = user_input.split()
            search_idx = words.index("search") if "search" in words else -1
            if search_idx >= 0 and search_idx < len(words) - 1:
                params["query"] = " ".join(words[search_idx + 1:])
        elif "remember" in user_input or "store" in user_input:
            params["operation"] = "store"
            params["content"] = user_input
        else:
            params["operation"] = "stats"
        
        return params
    
    def _extract_llm_parameters(self, user_input: str) -> Dict[str, Any]:
        """Extract LLM query parameters"""
        params = {"query": user_input}
        
        # Detect task type
        if "code" in user_input.lower():
            params["task_type"] = "coding"
        elif "create" in user_input.lower() or "write" in user_input.lower():
            params["task_type"] = "creative"
        elif "analyze" in user_input.lower():
            params["task_type"] = "analysis"
        elif "explain" in user_input.lower() or "reason" in user_input.lower():
            params["task_type"] = "reasoning"
        else:
            params["task_type"] = "general"
        
        return params
    
    def _customize_parameters_for_tool(self, tool_name: str, base_params: Dict[str, Any], context: ReasoningContext) -> Dict[str, Any]:
        """Customize parameters for specific tools in multi-tool processes"""
        
        if tool_name == "code_generator":
            return {
                "description": base_params.get("description", ""),
                "language": "python",
                "include_docs": True
            }
        elif tool_name == "file_processor":
            return {
                "operation": "write",
                "file_path": "generated_code.py",
                "content": "# Generated code will be placed here"
            }
        elif tool_name == "llm_query_tool":
            return {
                "query": base_params.get("query", context.user_input),
                "task_type": "general",
                "context": context.conversation_history,
                "session_data": context.session_data
            }
        
        return base_params
    
    async def _retrieve_rag_context(self, user_input: str) -> Dict[str, Any]:
        """Retrieve relevant context from memory for RAG enhancement"""
        try:
            # Search memory for relevant conversations
            search_result = await self.tool_manager.execute_tool(
                "memory_tool",
                operation="search",
                query=user_input,
                limit=5
            )
            
            rag_context = {
                "relevant_conversations": [],
                "relevant_patterns": [],
                "context_summary": ""
            }
            
            if search_result.success and search_result.data:
                entries = search_result.data.get("entries", [])
                
                # Extract relevant conversations
                for entry in entries[:3]:  # Top 3 most relevant
                    rag_context["relevant_conversations"].append({
                        "content": entry.get("content", "")[:200] + "...",
                        "timestamp": entry.get("timestamp", ""),
                        "category": entry.get("category", ""),
                        "relevance": entry.get("relevance", 0)
                    })
                
                # Create context summary
                if rag_context["relevant_conversations"]:
                    rag_context["context_summary"] = f"Found {len(rag_context['relevant_conversations'])} relevant past conversations related to your query."
                else:
                    rag_context["context_summary"] = "No directly relevant past conversations found."
            
            return rag_context
            
        except Exception as e:
            # Return empty context on error
            return {
                "relevant_conversations": [],
                "relevant_patterns": [],
                "context_summary": f"RAG context retrieval failed: {str(e)}"
            }
    
    async def _store_interaction_memory(self, user_input: str, response: str, plan: ActionPlan):
        """Store interaction in memory"""
        try:
            await self.tool_manager.execute_tool(
                "memory_tool",
                operation="store",
                content=f"User: {user_input}\nAssistant: {response[:200]}...",
                category="conversation",
                metadata={
                    "plan_id": plan.plan_id,
                    "tools_used": plan.tools_to_use,
                    "confidence": plan.confidence.value
                }
            )
        except:
            pass  # Silent fail for memory storage
    
    # Utility methods
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def _generate_plan_id(self) -> str:
        """Generate unique plan ID"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    # CLI Commands
    def show_tools(self):
        """Show available tools"""
        tools = self.tool_manager.list_tools()
        
        if RICH_AVAILABLE:
            from rich.table import Table as RichTable
            table = RichTable(title="Available Tools")
            table.add_column("Name", style="cyan")
            table.add_column("Description", style="white")
            table.add_column("Usage", style="green")
            
            for tool in tools:
                table.add_row(
                    tool["name"],
                    tool["description"][:50] + "...",
                    str(tool["statistics"]["usage_count"])
                )
            
            console.print(table)
        else:
            print("\n🔧 Available Tools:")
            print("=" * 60)
            for tool in tools:
                print(f"• {tool['name']}: {tool['description']}")
                print(f"  Usage: {tool['statistics']['usage_count']} times")
                print()
    
    def show_memory_stats(self):
        """Show memory statistics"""
        try:
            # Try to get current event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, create task
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._show_memory_stats_async())
                    future.result()
            else:
                # If no loop running, use asyncio.run
                asyncio.run(self._show_memory_stats_async())
        except RuntimeError:
            # Fallback to asyncio.run
            asyncio.run(self._show_memory_stats_async())
    
    async def _show_memory_stats_async(self):
        """Async version of show memory stats"""
        result = await self.tool_manager.execute_tool("memory_tool", operation="stats")
        
        if result.success and result.data:
            stats = result.data
            
            if RICH_AVAILABLE:
                memory_panel = Panel(
                    f"[bold cyan]Total Entries:[/bold cyan] {stats.get('total_entries', 0)}\n" +
                    f"[bold green]Categories:[/bold green] {len(stats.get('entries_by_category', {}))}\n" +
                    f"[bold yellow]Total Accesses:[/bold yellow] {stats.get('total_accesses', 0)}\n" +
                    f"[bold blue]Most Accessed:[/bold blue] {stats.get('most_accessed_entry', 'None')}",
                    title="[bold white]Memory Statistics[/bold white]",
                    border_style="blue"
                )
                console.print(memory_panel)
            else:
                print("\n🧠 Memory Statistics:")
                print("=" * 40)
                print(f"Total Entries: {stats.get('total_entries', 0)}")
                print(f"Categories: {len(stats.get('entries_by_category', {}))}")
                print(f"Total Accesses: {stats.get('total_accesses', 0)}")
                print(f"Most Accessed: {stats.get('most_accessed_entry', 'None')}")
        else:
            print("❌ Could not retrieve memory statistics")
    
    def show_system_stats(self):
        """Show system statistics"""
        stats = self.tool_manager.get_system_statistics()
        
        if RICH_AVAILABLE:
            system_panel = Panel(
                f"[bold cyan]Total Tools:[/bold cyan] {stats['total_tools']}\n" +
                f"[bold green]Total Executions:[/bold green] {stats['total_executions']}\n" +
                f"[bold yellow]Success Rate:[/bold yellow] {stats['success_rate']:.1f}%\n" +
                f"[bold blue]Session Interactions:[/bold blue] {self.session_data['total_interactions']}",
                title="[bold white]System Statistics[/bold white]",
                border_style="green"
            )
            console.print(system_panel)
        else:
            print("\n📊 System Statistics:")
            print("=" * 40)
            print(f"Total Tools: {stats['total_tools']}")
            print(f"Total Executions: {stats['total_executions']}")
            print(f"Success Rate: {stats['success_rate']:.1f}%")
            print(f"Session Interactions: {self.session_data['total_interactions']}")
    
    def show_last_plan(self):
        """Show details of the last action plan"""
        if not self.last_action_plan:
            print("❌ No action plan available")
            return
        
        plan = self.last_action_plan
        
        if RICH_AVAILABLE:
            plan_panel = Panel(
                f"[bold cyan]Plan ID:[/bold cyan] {plan.plan_id}\n" +
                f"[bold green]Action:[/bold green] {plan.primary_action.value}\n" +
                f"[bold yellow]Tools:[/bold yellow] {', '.join(plan.tools_to_use)}\n" +
                f"[bold blue]Confidence:[/bold blue] {plan.confidence.value}\n" +
                f"[bold magenta]Reasoning:[/bold magenta] {plan.reasoning}",
                title="[bold white]Last Action Plan[/bold white]",
                border_style="magenta"
            )
            console.print(plan_panel)
        else:
            print("\n📋 Last Action Plan:")
            print("=" * 40)
            print(f"Plan ID: {plan.plan_id}")
            print(f"Action: {plan.primary_action.value}")
            print(f"Tools: {', '.join(plan.tools_to_use)}")
            print(f"Confidence: {plan.confidence.value}")
            print(f"Reasoning: {plan.reasoning}")
    
    def show_reasoning_analytics(self):
        """Show reasoning engine analytics"""
        asyncio.run(self._show_reasoning_analytics_async())
    
    async def _show_reasoning_analytics_async(self):
        """Async version of show reasoning analytics"""
        
        reasoning_tool = self.tool_manager.get_tool("fast_reasoning_engine")
        if not reasoning_tool:
            print("❌ Reasoning engine not available")
            return
        
        try:
            analytics = reasoning_tool.get_reasoning_analytics()
            
            if RICH_AVAILABLE:
                from rich.table import Table
                
                # Main analytics panel
                analytics_panel = Panel(
                    f"[bold cyan]Total Chains:[/bold cyan] {analytics.get('total_reasoning_chains', 0)}\n" +
                    f"[bold green]Avg Confidence:[/bold green] {analytics.get('average_confidence', 0):.2f}\n" +
                    f"[bold yellow]Avg Steps:[/bold yellow] {analytics.get('average_steps_per_chain', 0):.1f}\n" +
                    f"[bold blue]Avg Time:[/bold blue] {analytics.get('average_execution_time', 0):.2f}s",
                    title="[bold white]Reasoning Analytics[/bold white]",
                    border_style="cyan"
                )
                console.print(analytics_panel)
                
                # Recent chains table
                recent_chains = analytics.get('recent_chains', [])
                if recent_chains:
                    chains_table = Table(title="Recent Reasoning Chains")
                    chains_table.add_column("ID", style="cyan")
                    chains_table.add_column("Query", style="white")
                    chains_table.add_column("Confidence", style="green")
                    chains_table.add_column("Steps", style="blue")
                    
                    for chain in recent_chains:
                        chains_table.add_row(
                            chain.get('id', 'N/A'),
                            chain.get('query', 'N/A')[:30] + "...",
                            f"{chain.get('confidence', 0):.2f}",
                            str(chain.get('steps', 0))
                        )
                    
                    console.print(chains_table)
                
            else:
                print("\n🧠 Reasoning Analytics:")
                print("=" * 40)
                print(f"Total Chains: {analytics.get('total_reasoning_chains', 0)}")
                print(f"Average Confidence: {analytics.get('average_confidence', 0):.2f}")
                print(f"Average Steps: {analytics.get('average_steps_per_chain', 0):.1f}")
                print(f"Average Time: {analytics.get('average_execution_time', 0):.2f}s")
                
                # Recent chains
                recent_chains = analytics.get('recent_chains', [])
                if recent_chains:
                    print(f"\nRecent Chains ({len(recent_chains)}):")
                    for chain in recent_chains:
                        print(f"• {chain.get('id', 'N/A')}: {chain.get('query', 'N/A')[:40]}... "
                              f"(conf: {chain.get('confidence', 0):.2f}, steps: {chain.get('steps', 0)})")
        
        except Exception as e:
            if RICH_AVAILABLE:
                console.print(f"[bold red]❌ Error retrieving reasoning analytics: {str(e)}[/bold red]")
            else:
                print(f"❌ Error retrieving reasoning analytics: {str(e)}")

def main():
    """Main CLI loop"""
    
    cli = EnhancedBasedGodCLI()
    
    print("\n💬 Enhanced BASED GOD CLI is ready!")
    print("Type 'help' for commands, 'exit' to quit")
    print("=" * 60)
    
    while True:
        try:
            user_input = input("\n🔥 BASED GOD > ").strip()
            
            if not user_input:
                continue
            
            # Handle special commands
            if user_input.lower() == 'exit':
                if RICH_AVAILABLE:
                    console.print("[bold red]👋 Goodbye! Stay Based! 🔥[/bold red]")
                else:
                    print("👋 Goodbye! Stay Based! 🔥")
                break
            
            elif user_input.lower() == 'help':
                if RICH_AVAILABLE:
                    help_text = """
[bold cyan]Available Commands:[/bold cyan]

[yellow]• help[/yellow] - Show this help
[yellow]• tools[/yellow] - Show available tools
[yellow]• memory[/yellow] - Show memory statistics  
[yellow]• stats[/yellow] - Show system statistics
[yellow]• plan[/yellow] - Show last action plan
[yellow]• reasoning[/yellow] - Show reasoning analytics
[yellow]• exit[/yellow] - Exit the CLI

[bold cyan]Example Queries:[/bold cyan]

[green]• "Scrape https://example.com for news articles"[/green]
[green]• "Generate a Python function to calculate fibonacci"[/green]
[green]• "Analyze this CSV data: name,age\nJohn,25\nJane,30"[/green]
[green]• "Ask AI: What is machine learning?"[/green]
[green]• "Remember that I prefer Python for web development"[/green]
"""
                    console.print(Panel(help_text, title="[bold white]Help[/bold white]", border_style="blue"))
                else:
                    print("\n📖 Available Commands:")
                    print("• help - Show this help")
                    print("• tools - Show available tools")
                    print("• memory - Show memory statistics")
                    print("• stats - Show system statistics") 
                    print("• plan - Show last action plan")
                    print("• reasoning - Show reasoning analytics")
                    print("• exit - Exit the CLI")
                    print("\n📝 Example Queries:")
                    print('• "Scrape https://example.com for news articles"')
                    print('• "Generate a Python function to calculate fibonacci"')
                    print('• "Analyze this CSV data: name,age\\nJohn,25\\nJane,30"')
                    print('• "Ask AI: What is machine learning?"')
                    print('• "Remember that I prefer Python for web development"')
                continue
            
            elif user_input.lower() == 'tools':
                cli.show_tools()
                continue
            
            elif user_input.lower() == 'memory':
                cli.show_memory_stats()
                continue
            
            elif user_input.lower() == 'stats':
                cli.show_system_stats()
                continue
            
            elif user_input.lower() == 'plan':
                cli.show_last_plan()
                continue
            
            elif user_input.lower() == 'reasoning':
                cli.show_reasoning_analytics()
                continue
            
            # Process normal chat input
            response = cli.chat_sync(user_input)
            
            if RICH_AVAILABLE:
                console.print(f"\n[bold green]🤖 Assistant:[/bold green]\n{response}")
            else:
                print(f"\n🤖 Assistant:\n{response}")
        
        except KeyboardInterrupt:
            if RICH_AVAILABLE:
                console.print("\n[bold red]👋 Goodbye! Stay Based! 🔥[/bold red]")
            else:
                print("\n👋 Goodbye! Stay Based! 🔥")
            break
        except Exception as e:
            if RICH_AVAILABLE:
                console.print(f"[bold red]❌ Error: {str(e)}[/bold red]")
            else:
                print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()