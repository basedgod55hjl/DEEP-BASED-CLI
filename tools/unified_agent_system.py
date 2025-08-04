"""
Unified LLM Agent System - Enhanced BASED GOD CLI
Treats memory, persona, tool-use, contact caching, and conversation as one brain
"""

import asyncio
import json
import logging
import sqlite3
import aiosqlite
from typing import Dict, Any, Optional, List, Union, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import uuid
from pathlib import Path

from .base_tool import BaseTool, ToolResponse
from .llm_query_tool import LLMQueryTool
from .vector_database_tool import VectorDatabaseTool
from .sql_database_tool import SQLDatabaseTool

class AgentState(Enum):
    """Agent operational states"""
    IDLE = "idle"
    THINKING = "thinking"
    EXECUTING = "executing"
    LEARNING = "learning"
    ADAPTING = "adapting"
    ERROR = "error"

class InteractionType(Enum):
    """Types of interactions"""
    CONVERSATION = "conversation"
    TOOL_USE = "tool_use"
    MEMORY_RETRIEVAL = "memory_retrieval"
    LEARNING = "learning"
    REASONING = "reasoning"
    PLANNING = "planning"

@dataclass
class EnhancedContact:
    """Enhanced contact information with relationship mapping"""
    id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    organization: Optional[str] = None
    relationship_strength: float = 0.5
    interaction_count: int = 0
    last_interaction: Optional[datetime] = None
    preferences: Dict[str, Any] = None
    tags: List[str] = None
    notes: str = ""
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self) -> Any:
        if self.preferences is None:
            self.preferences = {}
        if self.tags is None:
            self.tags = []
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

@dataclass
class EnhancedMemory:
    """Enhanced memory with semantic understanding and emotional valence"""
    id: str
    content: str
    memory_type: str
    importance: float
    emotional_valence: float
    context: str = ""
    associations: List[str] = None
    confidence: float = 1.0
    source: str = "user"
    created_at: datetime = None
    last_accessed: datetime = None
    access_count: int = 0
    
    def __post_init__(self) -> Any:
        if self.associations is None:
            self.associations = []
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_accessed is None:
            self.last_accessed = datetime.now()

@dataclass
class EnhancedConversation:
    """Enhanced conversation with context and analysis"""
    id: str
    user_message: str
    agent_response: str
    conversation_type: str  # "chat", "task", "learning", "reasoning"
    context: Dict[str, Any]
    tools_used: List[str]
    reasoning_chain: List[str]
    sentiment: float = 0.0
    satisfaction_score: float = 0.0
    created_at: datetime = None
    
    def __post_init__(self) -> Any:
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class EnhancedTool:
    """Enhanced tool with usage analytics"""
    id: str
    name: str
    description: str
    capabilities: List[str]
    usage_count: int = 0
    success_rate: float = 1.0
    average_execution_time: float = 0.0
    last_used: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime = None
    
    def __post_init__(self) -> Any:
        if self.created_at is None:
            self.created_at = datetime.now()

class UnifiedAgentSystem(BaseTool):
    """
    Enhanced Unified LLM Agent System
    Advanced AI agent with unified memory, persona, tools, and learning capabilities
    """
    
    def __init__(self, 
                 db_path: str = "data/unified_agent.db",
                 vector_db_config: Optional[Dict[str, Any]] = None,
                 enable_learning: bool = True,
                 enable_reasoning: bool = True,
                 enable_planning: bool = True):
    """__init__ function."""
        """Initialize Enhanced Unified Agent System"""
        super().__init__(
            name="Enhanced Unified Agent System",
            description="Advanced AI agent with unified memory, persona, tools, learning, and reasoning",
            capabilities=[
                "unified_memory_management",
                "advanced_persona_adaptation",
                "intelligent_tool_selection",
                "contact_caching_and_enrichment",
                "conversational_intelligence",
                "context_aware_responses",
                "real_time_learning",
                "relationship_mapping",
                "multi_modal_interaction",
                "advanced_reasoning",
                "autonomous_planning",
                "emotional_intelligence",
                "predictive_analytics",
                "adaptive_behavior"
            ]
        )
        
        # Core components
        self.db_path = db_path
        self.vector_db_config = vector_db_config or {}
        self.enable_learning = enable_learning
        self.enable_reasoning = enable_reasoning
        self.enable_planning = enable_planning
        
        # Logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize sub-systems
        self.llm_tool = LLMQueryTool()
        
        # Initialize vector database only if config is provided
        if vector_db_config:
            try:
                self.vector_db = VectorDatabaseTool(**vector_db_config)
            except Exception as e:
                self.logger.warning(f"Vector database initialization failed: {str(e)}")
                self.vector_db = None
        else:
            self.vector_db = None
            
        self.sql_db = SQLDatabaseTool(db_path)
        
        # Agent state and configuration
        self.current_state = AgentState.IDLE
        self.current_persona = "default"
        self.conversation_context = {}
        self.active_tools = {}
        self.learning_buffer = []
        
        # Enhanced data structures
        self.contacts: Dict[str, EnhancedContact] = {}
        self.memories: Dict[str, EnhancedMemory] = {}
        self.conversations: Dict[str, EnhancedConversation] = {}
        self.tools: Dict[str, EnhancedTool] = {}
        
        # Analytics and metrics
        self.interaction_history = []
        self.performance_metrics = {
            "total_interactions": 0,
            "successful_tool_uses": 0,
            "learning_events": 0,
            "reasoning_sessions": 0,
            "average_response_time": 0.0
        }
        
        # Initialize database and load data
        asyncio.create_task(self._initialize_system())
        
    async def _initialize_system(self) -> Any:
        """Initialize the unified agent system"""
        try:
            # Initialize database
            await self._init_database()
            
            # Load existing data
            await self._load_existing_data()
            
            # Initialize default persona
            await self._initialize_default_persona()
            
            # Start background tasks
            if self.enable_learning:
                asyncio.create_task(self._background_learning_loop())
            
            self.logger.info("Enhanced Unified Agent System initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Unified Agent System: {str(e)}")
            raise
    
    async def _init_database(self) -> Any:
        """Initialize enhanced database schema"""
        async with aiosqlite.connect(self.db_path) as db:
            # Enhanced contacts table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS enhanced_contacts (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT,
                    phone TEXT,
                    role TEXT,
                    organization TEXT,
                    relationship_strength REAL DEFAULT 0.5,
                    interaction_count INTEGER DEFAULT 0,
                    last_interaction TEXT,
                    preferences TEXT,
                    tags TEXT,
                    notes TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)
            
            # Enhanced memories table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS enhanced_memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    importance REAL DEFAULT 0.5,
                    context TEXT,
                    associations TEXT,
                    emotional_valence REAL DEFAULT 0.0,
                    confidence REAL DEFAULT 1.0,
                    source TEXT DEFAULT 'user',
                    created_at TEXT,
                    last_accessed TEXT,
                    access_count INTEGER DEFAULT 0
                )
            """)
            
            # Enhanced conversations table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS enhanced_conversations (
                    id TEXT PRIMARY KEY,
                    user_message TEXT NOT NULL,
                    agent_response TEXT NOT NULL,
                    conversation_type TEXT DEFAULT 'chat',
                    context TEXT,
                    tools_used TEXT,
                    reasoning_chain TEXT,
                    sentiment REAL DEFAULT 0.0,
                    satisfaction_score REAL DEFAULT 0.0,
                    created_at TEXT
                )
            """)
            
            # Enhanced tools table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS enhanced_tools (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    capabilities TEXT,
                    usage_count INTEGER DEFAULT 0,
                    success_rate REAL DEFAULT 1.0,
                    average_execution_time REAL DEFAULT 0.0,
                    last_used TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TEXT
                )
            """)
            
            # Interaction history table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS interaction_history (
                    id TEXT PRIMARY KEY,
                    interaction_type TEXT NOT NULL,
                    content TEXT,
                    context TEXT,
                    timestamp TEXT,
                    duration REAL,
                    success BOOLEAN,
                    metadata TEXT
                )
            """)
            
            # Performance metrics table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id TEXT PRIMARY KEY,
                    metric_name TEXT NOT NULL,
                    metric_value REAL,
                    timestamp TEXT,
                    context TEXT
                )
            """)
            
            await db.commit()
    
    async def _load_existing_data(self) -> Any:
        """Load existing data from database"""
        try:
            # Load contacts
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("SELECT * FROM enhanced_contacts") as cursor:
                    async for row in cursor:
                        contact_data = dict(zip([col[0] for col in cursor.description], row))
                        contact = EnhancedContact(**contact_data)
                        self.contacts[contact.id] = contact
                
                # Load memories
                async with db.execute("SELECT * FROM enhanced_memories") as cursor:
                    async for row in cursor:
                        memory_data = dict(zip([col[0] for col in cursor.description], row))
                        memory = EnhancedMemory(**memory_data)
                        self.memories[memory.id] = memory
                
                # Load tools
                async with db.execute("SELECT * FROM enhanced_tools") as cursor:
                    async for row in cursor:
                        tool_data = dict(zip([col[0] for col in cursor.description], row))
                        tool = EnhancedTool(**tool_data)
                        self.tools[tool.id] = tool
                        
        except Exception as e:
            self.logger.error(f"Error loading existing data: {str(e)}")
    
    async def _initialize_default_persona(self) -> Any:
        """Initialize default persona with enhanced capabilities"""
        default_persona = {
            "name": "Enhanced AI Assistant",
            "personality": "helpful, intelligent, and adaptive",
            "expertise": ["general assistance", "problem solving", "learning"],
            "communication_style": "clear, friendly, and professional",
            "learning_preferences": "continuous improvement and adaptation",
            "emotional_intelligence": "high",
            "reasoning_capabilities": "advanced"
        }
        
        # Store persona in memory
        persona_memory = EnhancedMemory(
            id=str(uuid.uuid4()),
            content=json.dumps(default_persona),
            memory_type="persona",
            importance=1.0,
            emotional_valence=0.8, # Assuming a default emotional valence for persona
            context={"type": "system_configuration"},
            associations=[],
            source="system"
        )
        
        self.memories[persona_memory.id] = persona_memory
        await self._save_memory(persona_memory)
    
    async def execute(self, **kwargs) -> ToolResponse:
        """Execute unified agent operation with enhanced capabilities"""
        try:
            operation = kwargs.get("operation", "conversation")
            
            if operation == "conversation":
                return await self._handle_conversation(**kwargs)
            elif operation == "tool_use":
                return await self._handle_tool_use(**kwargs)
            elif operation == "memory_retrieval":
                return await self._handle_memory_retrieval(**kwargs)
            elif operation == "learning":
                return await self._handle_learning(**kwargs)
            elif operation == "reasoning":
                return await self._handle_reasoning(**kwargs)
            elif operation == "planning":
                return await self._handle_planning(**kwargs)
            elif operation == "contact_management":
                return await self._handle_contact_management(**kwargs)
            else:
                return await self._handle_conversation(**kwargs)
                
        except Exception as e:
            self.logger.error(f"Error in unified agent execution: {str(e)}")
            return ToolResponse(
                success=False,
                data={"error": str(e)},
                message=f"Unified agent operation failed: {str(e)}"
            )
    
    async def _handle_conversation(self, **kwargs) -> ToolResponse:
        """Handle conversation with enhanced context awareness"""
        try:
            user_message = kwargs.get("message", "")
            context = kwargs.get("context", {})
            
            # Update agent state
            self.current_state = AgentState.THINKING
            
            # Retrieve relevant context
            relevant_memories = await self._retrieve_relevant_memories(user_message)
            relevant_contacts = await self._retrieve_relevant_contacts(user_message)
            conversation_history = await self._get_recent_conversations(5)
            
            # Build enhanced context
            enhanced_context = {
                "user_message": user_message,
                "relevant_memories": relevant_memories,
                "relevant_contacts": relevant_contacts,
                "conversation_history": conversation_history,
                "current_persona": self.current_persona,
                "agent_state": self.current_state.value,
                "performance_metrics": self.performance_metrics
            }
            
            # Generate response with reasoning
            if self.enable_reasoning:
                response = await self._generate_reasoned_response(user_message, enhanced_context)
            else:
                response = await self._generate_simple_response(user_message, enhanced_context)
            
            # Update agent state
            self.current_state = AgentState.EXECUTING
            
            # Create conversation record
            conversation = EnhancedConversation(
                id=str(uuid.uuid4()),
                user_message=user_message,
                agent_response=response,
                conversation_type="chat",
                context=enhanced_context,
                tools_used=[],
                reasoning_chain=enhanced_context.get("reasoning_chain", []),
                sentiment=enhanced_context.get("sentiment", 0.0)
            )
            
            # Store conversation
            self.conversations[conversation.id] = conversation
            await self._save_conversation(conversation)
            
            # Update metrics
            self.performance_metrics["total_interactions"] += 1
            
            # Learning opportunity
            if self.enable_learning:
                await self._learn_from_interaction(conversation)
            
            # Update agent state
            self.current_state = AgentState.IDLE
            
            return ToolResponse(
                success=True,
                data={
                    "response": response,
                    "conversation_id": conversation.id,
                    "context_used": enhanced_context,
                    "reasoning_applied": self.enable_reasoning,
                    "learning_enabled": self.enable_learning
                },
                message="Enhanced conversation completed successfully"
            )
            
        except Exception as e:
            self.current_state = AgentState.ERROR
            return await self._handle_error(e, "conversation")
    
    async def _handle_tool_use(self, **kwargs) -> ToolResponse:
        """Handle intelligent tool selection and execution"""
        try:
            task_description = kwargs.get("task", "")
            available_tools = kwargs.get("available_tools", [])
            
            # Select appropriate tools
            selected_tools = await self._select_tools_for_task(task_description, available_tools)
            
            # Execute tools with orchestration
            results = []
            for tool in selected_tools:
                try:
                    result = await self._execute_tool(tool, task_description)
                    results.append(result)
                    
                    # Update tool metrics
                    if tool.id in self.tools:
                        self.tools[tool.id].usage_count += 1
                        self.tools[tool.id].last_used = datetime.now()
                        await self._update_tool_metrics(tool.id, success=True)
                        
                except Exception as e:
                    self.logger.error(f"Tool execution failed: {str(e)}")
                    if tool.id in self.tools:
                        await self._update_tool_metrics(tool.id, success=False)
            
            return ToolResponse(
                success=True,
                data={
                    "tools_used": [tool.name for tool in selected_tools],
                    "results": results,
                    "orchestration": "intelligent"
                },
                message="Tool orchestration completed successfully"
            )
            
        except Exception as e:
            return await self._handle_error(e, "tool use")
    
    async def _handle_memory_retrieval(self, **kwargs) -> ToolResponse:
        """Handle enhanced memory retrieval with semantic search"""
        try:
            query = kwargs.get("query", "")
            memory_type = kwargs.get("memory_type", "all")
            limit = kwargs.get("limit", 10)
            
            # Retrieve memories using vector search if available
            if self.vector_db:
                vector_results = await self.vector_db.search_embeddings(
                    query=query,
                    limit=limit,
                    collection_name="memories"
                )
                
                # Combine with traditional search
                traditional_results = await self._search_memories_traditional(query, limit)
                
                # Merge and rank results
                combined_results = await self._merge_memory_results(
                    vector_results, traditional_results, query
                )
            else:
                combined_results = await self._search_memories_traditional(query, limit)
            
            # Filter by memory type if specified
            if memory_type != "all":
                combined_results = [m for m in combined_results if m.memory_type == memory_type]
            
            return ToolResponse(
                success=True,
                data={
                    "memories": [asdict(memory) for memory in combined_results],
                    "query": query,
                    "search_method": "hybrid" if self.vector_db else "traditional"
                },
                message="Memory retrieval completed successfully"
            )
            
        except Exception as e:
            return await self._handle_error(e, "memory retrieval")
    
    async def _handle_learning(self, **kwargs) -> ToolResponse:
        """Handle real-time learning from interactions"""
        try:
            if not self.enable_learning:
                return ToolResponse(
                    success=False,
                    data={"error": "Learning is disabled"},
                    message="Learning is not enabled"
                )
            
            learning_data = kwargs.get("data", {})
            learning_type = kwargs.get("type", "interaction")
            
            # Process learning data
            if learning_type == "interaction":
                await self._learn_from_interaction_data(learning_data)
            elif learning_type == "feedback":
                await self._learn_from_feedback(learning_data)
            elif learning_type == "pattern":
                await self._learn_from_patterns(learning_data)
            
            # Update learning metrics
            self.performance_metrics["learning_events"] += 1
            
            return ToolResponse(
                success=True,
                data={
                    "learning_type": learning_type,
                    "learning_events": self.performance_metrics["learning_events"]
                },
                message="Learning completed successfully"
            )
            
        except Exception as e:
            return await self._handle_error(e, "learning")
    
    async def _handle_reasoning(self, **kwargs) -> ToolResponse:
        """Handle advanced reasoning with chain-of-thought"""
        try:
            if not self.enable_reasoning:
                return ToolResponse(
                    success=False,
                    data={"error": "Reasoning is disabled"},
                    message="Reasoning is not enabled"
                )
            
            problem = kwargs.get("problem", "")
            reasoning_type = kwargs.get("type", "chain_of_thought")
            
            # Perform reasoning based on type
            if reasoning_type == "chain_of_thought":
                result = await self._chain_of_thought_reasoning(problem)
            elif reasoning_type == "analogical":
                result = await self._analogical_reasoning(problem)
            elif reasoning_type == "deductive":
                result = await self._deductive_reasoning(problem)
            else:
                result = await self._chain_of_thought_reasoning(problem)
            
            # Update reasoning metrics
            self.performance_metrics["reasoning_sessions"] += 1
            
            return ToolResponse(
                success=True,
                data={
                    "reasoning_result": result,
                    "reasoning_type": reasoning_type,
                    "reasoning_sessions": self.performance_metrics["reasoning_sessions"]
                },
                message="Advanced reasoning completed successfully"
            )
            
        except Exception as e:
            return await self._handle_error(e, "reasoning")
    
    async def _handle_planning(self, **kwargs) -> ToolResponse:
        """Handle autonomous planning and goal management"""
        try:
            if not self.enable_planning:
                return ToolResponse(
                    success=False,
                    data={"error": "Planning is disabled"},
                    message="Planning is not enabled"
                )
            
            goal = kwargs.get("goal", "")
            constraints = kwargs.get("constraints", [])
            
            # Generate plan
            plan = await self._generate_plan(goal, constraints)
            
            # Execute plan if requested
            if kwargs.get("execute", False):
                execution_result = await self._execute_plan(plan)
                return ToolResponse(
                    success=True,
                    data={
                        "plan": plan,
                        "execution_result": execution_result,
                        "executed": True
                    },
                    message="Plan generated and executed successfully"
                )
            else:
                return ToolResponse(
                    success=True,
                    data={
                        "plan": plan,
                        "executed": False
                    },
                    message="Plan generated successfully"
                )
                
        except Exception as e:
            return await self._handle_error(e, "planning")
    
    async def _handle_contact_management(self, **kwargs) -> ToolResponse:
        """Handle enhanced contact management"""
        try:
            action = kwargs.get("action", "retrieve")
            
            if action == "add":
                contact_data = kwargs.get("contact_data", {})
                contact = await self._add_contact(contact_data)
                return ToolResponse(
                    success=True,
                    data={"contact": asdict(contact)},
                    message="Contact added successfully"
                )
            elif action == "update":
                contact_id = kwargs.get("contact_id", "")
                updates = kwargs.get("updates", {})
                contact = await self._update_contact(contact_id, updates)
                return ToolResponse(
                    success=True,
                    data={"contact": asdict(contact)},
                    message="Contact updated successfully"
                )
            elif action == "retrieve":
                contact_id = kwargs.get("contact_id", "")
                if contact_id:
                    contact = self.contacts.get(contact_id)
                    if contact:
                        return ToolResponse(
                            success=True,
                            data={"contact": asdict(contact)},
                            message="Contact retrieved successfully"
                        )
                    else:
                        return ToolResponse(
                            success=False,
                            data={"error": "Contact not found"},
                            message="Contact not found"
                        )
                else:
                    # Return all contacts
                    return ToolResponse(
                        success=True,
                        data={"contacts": [asdict(c) for c in self.contacts.values()]},
                        message="All contacts retrieved successfully"
                    )
            else:
                return ToolResponse(
                    success=False,
                    data={"error": "Invalid action"},
                    message="Invalid contact management action"
                )
                
        except Exception as e:
            return await self._handle_error(e, "contact management")
    
    # Enhanced helper methods
    async def _generate_reasoned_response(self, user_message: str, context: Dict[str, Any]) -> str:
        """Generate response with chain-of-thought reasoning"""
        reasoning_prompt = f"""
        You are an advanced AI assistant with reasoning capabilities.
        
        User Message: {user_message}
        
        Context:
        - Relevant Memories: {context.get('relevant_memories', [])}
        - Conversation History: {context.get('conversation_history', [])}
        - Current Persona: {context.get('current_persona', 'default')}
        
        Please provide a response using the following reasoning process:
        
        1. ANALYZE: Understand the user's intent and context
        2. REASON: Apply logical thinking and relevant knowledge
        3. SYNTHESIZE: Combine information from memories and context
        4. RESPOND: Provide a helpful, contextual response
        
        Response:
        """
        
        response = await self.llm_tool.chat_completion(
            prompt=reasoning_prompt,
            model="deepseek-reasoner",
            temperature=0.7
        )
        
        return response.data.get("response", "I'm sorry, I couldn't generate a response.")
    
    async def _generate_simple_response(self, user_message: str, context: Dict[str, Any]) -> str:
        """Generate simple response without advanced reasoning"""
        simple_prompt = f"""
        User: {user_message}
        
        Context: {context.get('relevant_memories', [])}
        
        Assistant:
        """
        
        response = await self.llm_tool.chat_completion(
            prompt=simple_prompt,
            model="deepseek-chat",
            temperature=0.7
        )
        
        return response.data.get("response", "I'm sorry, I couldn't generate a response.")
    
    async def _retrieve_relevant_memories(self, query: str, limit: int = 5) -> List[EnhancedMemory]:
        """Retrieve relevant memories using semantic search"""
        if self.vector_db:
            # Use vector search
            results = await self.vector_db.search_embeddings(
                query=query,
                limit=limit,
                collection_name="memories"
            )
            return results
        else:
            # Use traditional search
            return await self._search_memories_traditional(query, limit)
    
    async def _search_memories_traditional(self, query: str, limit: int) -> List[EnhancedMemory]:
        """Search memories using traditional text matching"""
        query_lower = query.lower()
        relevant_memories = []
        
        for memory in self.memories.values():
            if query_lower in memory.content.lower():
                relevant_memories.append(memory)
        
        # Sort by importance and recency
        relevant_memories.sort(
            key=lambda m: (m.importance, m.last_accessed),
            reverse=True
        )
        
        return relevant_memories[:limit]
    
    async def _merge_memory_results(self, vector_results: List, traditional_results: List, query: str) -> List[EnhancedMemory]:
        """Merge and rank memory search results"""
        # Simple merge - in production, use more sophisticated ranking
        all_results = list(set(vector_results + traditional_results))
        
        # Re-rank based on relevance to query
        for memory in all_results:
            relevance_score = self._calculate_relevance(memory.content, query)
            memory.importance = (memory.importance + relevance_score) / 2
        
        all_results.sort(key=lambda m: m.importance, reverse=True)
        return all_results
    
    def _calculate_relevance(self, content: str, query: str) -> float:
        """Calculate relevance score between content and query"""
        content_words = set(content.lower().split())
        query_words = set(query.lower().split())
        
        if not query_words:
            return 0.0
        
        intersection = content_words.intersection(query_words)
        return len(intersection) / len(query_words)
    
    async def _retrieve_relevant_contacts(self, query: str) -> List[EnhancedContact]:
        """Retrieve relevant contacts based on query"""
        query_lower = query.lower()
        relevant_contacts = []
        
        for contact in self.contacts.values():
            if (query_lower in contact.name.lower() or
                (contact.role and query_lower in contact.role.lower()) or
                (contact.organization and query_lower in contact.organization.lower())):
                relevant_contacts.append(contact)
        
        return relevant_contacts
    
    async def _get_recent_conversations(self, limit: int) -> List[EnhancedConversation]:
        """Get recent conversations"""
        conversations = list(self.conversations.values())
        conversations.sort(key=lambda c: c.created_at, reverse=True)
        return conversations[:limit]
    
    async def _learn_from_interaction(self, conversation: EnhancedConversation):
    """_learn_from_interaction function."""
        """Learn from conversation interaction"""
        # Extract learning insights
        insights = await self._extract_insights_from_conversation(conversation)
        
        # Create learning memory
        learning_memory = EnhancedMemory(
            id=str(uuid.uuid4()),
            content=json.dumps(insights),
            memory_type="learning",
            importance=0.7,
            emotional_valence=0.7, # Assuming a default emotional valence for learning
            context={"source": "conversation", "conversation_id": conversation.id},
            associations=[conversation.id],
            source="system"
        )
        
        self.memories[learning_memory.id] = learning_memory
        await self._save_memory(learning_memory)
    
    async def _extract_insights_from_conversation(self, conversation: EnhancedConversation) -> Dict[str, Any]:
        """Extract learning insights from conversation"""
        insights = {
            "user_preferences": {},
            "communication_patterns": {},
            "topic_interest": {},
            "satisfaction_indicators": {}
        }
        
        # Analyze user message for preferences
        user_message = conversation.user_message.lower()
        
        # Extract topic interests
        topics = ["coding", "data", "analysis", "creative", "technical", "personal"]
        for topic in topics:
            if topic in user_message:
                insights["topic_interest"][topic] = insights["topic_interest"].get(topic, 0) + 1
        
        # Analyze sentiment
        insights["satisfaction_indicators"]["sentiment"] = conversation.sentiment
        
        return insights
    
    async def _background_learning_loop(self) -> Any:
        """Background learning loop for continuous improvement"""
        while True:
            try:
                # Analyze recent interactions
                recent_conversations = await self._get_recent_conversations(20)
                
                # Identify patterns
                patterns = await self._identify_patterns(recent_conversations)
                
                # Update learning
                if patterns:
                    await self._update_learning_from_patterns(patterns)
                
                # Sleep for a while
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error in background learning loop: {str(e)}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def _identify_patterns(self, conversations: List[EnhancedConversation]) -> Dict[str, Any]:
        """Identify patterns in conversations"""
        patterns = {
            "common_topics": {},
            "user_behaviors": {},
            "response_effectiveness": {}
        }
        
        for conversation in conversations:
            # Analyze topics
            words = conversation.user_message.lower().split()
            for word in words:
                if len(word) > 3:  # Skip short words
                    patterns["common_topics"][word] = patterns["common_topics"].get(word, 0) + 1
        
        return patterns
    
    async def _update_learning_from_patterns(self, patterns: Dict[str, Any]):
    """_update_learning_from_patterns function."""
        """Update learning based on identified patterns"""
        # Create pattern memory
        pattern_memory = EnhancedMemory(
            id=str(uuid.uuid4()),
            content=json.dumps(patterns),
            memory_type="pattern",
            importance=0.6,
            emotional_valence=0.6, # Assuming a default emotional valence for patterns
            context={"type": "background_learning"},
            associations=[],
            source="system"
        )
        
        self.memories[pattern_memory.id] = pattern_memory
        await self._save_memory(pattern_memory)
    
    # Database operations
    async def _save_memory(self, memory: EnhancedMemory):
    """_save_memory function."""
        """Save memory to database"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO enhanced_memories 
                (id, content, memory_type, importance, emotional_valence, context, associations, 
                 created_at, last_accessed, access_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                memory.id, memory.content, memory.memory_type, memory.importance,
                memory.emotional_valence, json.dumps(memory.context), json.dumps(memory.associations),
                memory.created_at.isoformat(), memory.last_accessed.isoformat(),
                memory.access_count
            ))
            await db.commit()
    
    async def _save_conversation(self, conversation: EnhancedConversation):
    """_save_conversation function."""
        """Save conversation to database"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO enhanced_conversations 
                (id, user_message, agent_response, conversation_type, context, 
                 tools_used, reasoning_chain, sentiment, satisfaction_score, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                conversation.id, conversation.user_message, conversation.agent_response,
                conversation.conversation_type, json.dumps(conversation.context),
                json.dumps(conversation.tools_used), json.dumps(conversation.reasoning_chain),
                conversation.sentiment, conversation.satisfaction_score,
                conversation.created_at.isoformat()
            ))
            await db.commit()
    
    async def _update_tool_metrics(self, tool_id: str, success: bool):
    """_update_tool_metrics function."""
        """Update tool usage metrics"""
        if tool_id in self.tools:
            tool = self.tools[tool_id]
            tool.usage_count += 1
            tool.last_used = datetime.now()
            
            # Update success rate
            if success:
                tool.success_rate = (tool.success_rate * (tool.usage_count - 1) + 1) / tool.usage_count
            else:
                tool.success_rate = (tool.success_rate * (tool.usage_count - 1)) / tool.usage_count
            
            # Save to database
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    UPDATE enhanced_tools 
                    SET usage_count = ?, success_rate = ?, last_used = ?
                    WHERE id = ?
                """, (tool.usage_count, tool.success_rate, tool.last_used.isoformat(), tool_id))
                await db.commit()
    
    async def _handle_error(self, error: Exception, operation: str) -> ToolResponse:
        """Handle errors in unified agent operations"""
        self.logger.error(f"Error in {operation}: {str(error)}")
        self.current_state = AgentState.ERROR
        
        return ToolResponse(
            success=False,
            data={"error": str(error), "operation": operation},
            message=f"Unified agent {operation} failed: {str(error)}"
        )
    
    def get_schema(self) -> Dict[str, Any]:
        """Get enhanced schema for the unified agent system"""
        return {
            "name": "Enhanced Unified Agent System",
            "description": "Advanced AI agent with unified memory, persona, tools, and learning",
            "parameters": {
                "operation": {
                    "type": "string",
                    "enum": ["conversation", "tool_use", "memory_retrieval", "learning", "reasoning", "planning", "contact_management"],
                    "description": "Type of operation to perform"
                },
                "message": {
                    "type": "string",
                    "description": "User message for conversation"
                },
                "task": {
                    "type": "string",
                    "description": "Task description for tool use"
                },
                "query": {
                    "type": "string",
                    "description": "Query for memory retrieval"
                },
                "goal": {
                    "type": "string",
                    "description": "Goal for planning"
                },
                "action": {
                    "type": "string",
                    "enum": ["add", "update", "retrieve"],
                    "description": "Action for contact management"
                },
                "context": {
                    "type": "object",
                    "description": "Additional context for operations"
                }
            }
        }
    
    # Public API methods
    async def add_contact(self, name: str, **kwargs) -> EnhancedContact:
        """Add a new contact"""
        contact = EnhancedContact(
            id=str(uuid.uuid4()),
            name=name,
            **kwargs
        )
        
        self.contacts[contact.id] = contact
        await self._save_contact(contact)
        return contact
    
    async def get_contact(self, contact_id: str) -> Optional[EnhancedContact]:
        """Get contact by ID"""
        return self.contacts.get(contact_id)
    
    async def add_memory(self, content: str, memory_type: str, **kwargs) -> EnhancedMemory:
        """Add a new memory"""
        memory = EnhancedMemory(
            id=str(uuid.uuid4()),
            content=content,
            memory_type=memory_type,
            **kwargs
        )
        
        self.memories[memory.id] = memory
        await self._save_memory(memory)
        return memory
    
    async def get_memory(self, memory_id: str) -> Optional[EnhancedMemory]:
        """Get memory by ID"""
        return self.memories.get(memory_id)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        return self.performance_metrics.copy()
    
    def get_agent_state(self) -> AgentState:
        """Get current agent state"""
        return self.current_state
    
    async def set_persona(self, persona_name: str):
    """set_persona function."""
        """Set the current persona"""
        self.current_persona = persona_name
        # Load persona-specific memories and preferences
        await self._load_persona_data(persona_name)
    
    async def _load_persona_data(self, persona_name: str):
    """_load_persona_data function."""
        """Load persona-specific data"""
        # Implementation for loading persona-specific memories, preferences, etc.
        pass
    
    async def _save_contact(self, contact: EnhancedContact):
    """_save_contact function."""
        """Save contact to database"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO enhanced_contacts 
                (id, name, email, phone, role, organization, relationship_strength,
                 interaction_count, last_interaction, preferences, tags, notes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                contact.id, contact.name, contact.email, contact.phone,
                contact.role, contact.organization, contact.relationship_strength,
                contact.interaction_count, contact.last_interaction.isoformat() if contact.last_interaction else None,
                json.dumps(contact.preferences), json.dumps(contact.tags), contact.notes,
                contact.created_at.isoformat(), contact.updated_at.isoformat()
            ))
            await db.commit() 