"""
RAG Pipeline Tool - Retrieval-Augmented Generation for DEEP-CLI
Integrates vector database, SQL database, and context-aware retrieval
"""

import os
import json
import asyncio
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from tools.base_tool import BaseTool, ToolResponse, ToolStatus
from tools.vector_database_tool import VectorDatabaseTool
from tools.sql_database_tool import SQLDatabaseTool
from tools.llm_query_tool import LLMQueryTool


@dataclass
class RAGContext:
    """Represents RAG context with multiple sources"""
    query: str
    vector_results: List[Dict[str, Any]]
    sql_results: List[Dict[str, Any]]
    persona_context: Optional[Dict[str, Any]]
    memory_context: List[Dict[str, Any]]
    combined_context: str
    relevance_scores: Dict[str, float]
    timestamp: str


class RAGPipelineTool(BaseTool):
    """
    RAG Pipeline Tool - Comprehensive retrieval-augmented generation
    Combines vector search, SQL queries, and context-aware retrieval
    """
    
    def __init__(self, 
                 vector_db_config: Optional[Dict[str, Any]] = None,
                 sql_db_path: str = "deepcli_database.db"):
        """Initialize RAG Pipeline Tool"""
        super().__init__(
            name="RAG Pipeline",
            description="Retrieval-Augmented Generation with context awareness",
            capabilities=[
                "rag_query",
                "context_retrieval",
                "persona_aware_search",
                "memory_augmentation",
                "hybrid_search",
                "context_ranking"
            ]
        )
        
        self.console = Console()
        
        # Initialize sub-tools
        self.vector_tool = VectorDatabaseTool(
            **(vector_db_config or {})
        )
        self.sql_tool = SQLDatabaseTool(db_path=sql_db_path)
        self.llm_tool = LLMQueryTool()
        
        # Configuration
        self.default_context_limit = 5
        self.default_relevance_threshold = 0.5
    
    async def execute(self, **kwargs) -> ToolResponse:
        """Execute RAG pipeline operations"""
        operation = kwargs.get('operation', 'rag_query')
        
        try:
            if operation == 'rag_query':
                return await self._rag_query(kwargs)
            elif operation == 'store_knowledge':
                return await self._store_knowledge(kwargs)
            elif operation == 'hybrid_search':
                return await self._hybrid_search(kwargs)
            elif operation == 'persona_query':
                return await self._persona_aware_query(kwargs)
            elif operation == 'update_context':
                return await self._update_context(kwargs)
            elif operation == 'analyze_relevance':
                return await self._analyze_relevance(kwargs)
            else:
                return ToolResponse(
                    success=False,
                    message=f"Unknown operation: {operation}",
                    status=ToolStatus.FAILED
                )
                
        except Exception as e:
            return ToolResponse(
                success=False,
                message=f"RAG pipeline error: {str(e)}",
                status=ToolStatus.FAILED
            )
    
    async def _rag_query(self, kwargs: Dict[str, Any]) -> ToolResponse:
        """Execute a complete RAG query"""
        query = kwargs.get('query', '')
        session_id = kwargs.get('session_id', '')
        persona_name = kwargs.get('persona_name', 'Deanna')
        include_memory = kwargs.get('include_memory', True)
        include_history = kwargs.get('include_history', True)
        context_limit = kwargs.get('context_limit', self.default_context_limit)
        
        if not query:
            return ToolResponse(
                success=False,
                message="No query provided",
                status=ToolStatus.FAILED
            )
        
        # 1. Get persona context
        persona_context = await self._get_persona_context(persona_name)
        
        # 2. Retrieve vector contexts
        vector_results = await self._retrieve_vector_context(
            query, context_limit
        )
        
        # 3. Retrieve relevant memories
        memory_context = []
        if include_memory:
            memory_context = await self._retrieve_memory_context(
                query, persona_context.get('id') if persona_context else None
            )
        
        # 4. Retrieve conversation history
        history_context = []
        if include_history and session_id:
            history_context = await self._retrieve_history_context(
                session_id, limit=3
            )
        
        # 5. Build combined context
        rag_context = await self._build_rag_context(
            query=query,
            vector_results=vector_results,
            memory_context=memory_context,
            history_context=history_context,
            persona_context=persona_context
        )
        
        # 6. Generate response with context
        response = await self._generate_rag_response(
            query=query,
            rag_context=rag_context,
            persona_context=persona_context
        )
        
        # 7. Store the interaction
        if session_id:
            await self._store_interaction(
                session_id=session_id,
                query=query,
                response=response,
                context=rag_context,
                persona_id=persona_context.get('id') if persona_context else None
            )
        
        return ToolResponse(
            success=True,
            message="RAG query completed successfully",
            data={
                "query": query,
                "response": response,
                "context": {
                    "vector_count": len(vector_results),
                    "memory_count": len(memory_context),
                    "history_count": len(history_context),
                    "total_context_length": len(rag_context.combined_context)
                },
                "persona": persona_name
            }
        )
    
    async def _store_knowledge(self, kwargs: Dict[str, Any]) -> ToolResponse:
        """Store knowledge in both vector and SQL databases"""
        texts = kwargs.get('texts', [])
        category = kwargs.get('category', 'general')
        metadata = kwargs.get('metadata', [])
        importance = kwargs.get('importance', 5)
        persona_id = kwargs.get('persona_id')
        
        if not texts:
            return ToolResponse(
                success=False,
                message="No texts provided to store",
                status=ToolStatus.FAILED
            )
        
        # Store in vector database
        vector_result = await self.vector_tool.execute(
            operation='store',
            texts=texts,
            metadata=metadata,
            category=category
        )
        
        if not vector_result.success:
            return vector_result
        
        # Store important items in SQL memory
        stored_memories = []
        for i, text in enumerate(texts):
            if len(text) > 50:  # Only store substantial content
                memory_result = await self.sql_tool.execute(
                    operation='store_memory',
                    content=text,
                    category=category,
                    importance=importance,
                    persona_id=persona_id,
                    tags=metadata[i].get('tags', []) if i < len(metadata) else []
                )
                if memory_result.success:
                    stored_memories.append(memory_result.data['memory_id'])
        
        return ToolResponse(
            success=True,
            message=f"Stored {len(texts)} items in knowledge base",
            data={
                "vector_ids": vector_result.data['ids'],
                "memory_ids": stored_memories,
                "category": category
            }
        )
    
    async def _hybrid_search(self, kwargs: Dict[str, Any]) -> ToolResponse:
        """Perform hybrid search across vector and SQL databases"""
        query = kwargs.get('query', '')
        limit = kwargs.get('limit', 10)
        include_vectors = kwargs.get('include_vectors', True)
        include_memories = kwargs.get('include_memories', True)
        include_conversations = kwargs.get('include_conversations', False)
        
        results = {
            "vector_results": [],
            "memory_results": [],
            "conversation_results": []
        }
        
        # Vector search
        if include_vectors:
            vector_result = await self.vector_tool.execute(
                operation='search',
                query=query,
                limit=limit
            )
            if vector_result.success:
                results["vector_results"] = vector_result.data['results']
        
        # Memory search (using SQL LIKE for now)
        if include_memories:
            memory_result = await self.sql_tool.execute(
                operation='execute_query',
                query="""
                    SELECT * FROM memory 
                    WHERE content LIKE ? 
                    ORDER BY importance DESC, access_count DESC 
                    LIMIT ?
                """,
                params=[f'%{query}%', limit]
            )
            if memory_result.success:
                results["memory_results"] = memory_result.data['results']
        
        # Conversation search
        if include_conversations:
            conv_result = await self.sql_tool.execute(
                operation='execute_query',
                query="""
                    SELECT * FROM conversations 
                    WHERE user_input LIKE ? OR assistant_response LIKE ?
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """,
                params=[f'%{query}%', f'%{query}%', limit]
            )
            if conv_result.success:
                results["conversation_results"] = conv_result.data['results']
        
        # Rank and combine results
        ranked_results = await self._rank_hybrid_results(query, results)
        
        return ToolResponse(
            success=True,
            message=f"Hybrid search completed",
            data={
                "query": query,
                "results": ranked_results,
                "counts": {
                    "vectors": len(results["vector_results"]),
                    "memories": len(results["memory_results"]),
                    "conversations": len(results["conversation_results"])
                }
            }
        )
    
    async def _persona_aware_query(self, kwargs: Dict[str, Any]) -> ToolResponse:
        """Execute a query with full persona awareness"""
        query = kwargs.get('query', '')
        persona_name = kwargs.get('persona_name', 'Deanna')
        session_id = kwargs.get('session_id', '')
        
        # Get persona details
        persona_result = await self.sql_tool.execute(
            operation='get_persona',
            name=persona_name
        )
        
        if not persona_result.success:
            return ToolResponse(
                success=False,
                message=f"Persona not found: {persona_name}",
                status=ToolStatus.FAILED
            )
        
        persona = persona_result.data['persona']
        
        # Build persona-aware prompt
        persona_prompt = self._build_persona_prompt(persona, query)
        
        # Execute RAG query with persona context
        rag_result = await self._rag_query({
            'query': persona_prompt,
            'session_id': session_id,
            'persona_name': persona_name,
            'include_memory': True,
            'include_history': True
        })
        
        if not rag_result.success:
            return rag_result
        
        # Format response in persona style
        styled_response = self._apply_persona_style(
            rag_result.data['response'],
            persona
        )
        
        return ToolResponse(
            success=True,
            message="Persona-aware query completed",
            data={
                "query": query,
                "response": styled_response,
                "persona": persona_name,
                "context_used": rag_result.data['context']
            }
        )
    
    async def _update_context(self, kwargs: Dict[str, Any]) -> ToolResponse:
        """Update context based on interaction"""
        session_id = kwargs.get('session_id', '')
        context_type = kwargs.get('context_type', 'interaction')
        context_data = kwargs.get('context_data', {})
        relevance_score = kwargs.get('relevance_score', 0.8)
        
        # Store context
        result = await self.sql_tool.execute(
            operation='store_context',
            session_id=session_id,
            context_type=context_type,
            context_data=context_data,
            relevance_score=relevance_score
        )
        
        # If highly relevant, also store as vector
        if relevance_score > 0.7 and context_data.get('text'):
            await self.vector_tool.execute(
                operation='store',
                texts=[context_data['text']],
                category='context',
                metadata=[{
                    'session_id': session_id,
                    'type': context_type,
                    'relevance': relevance_score
                }]
            )
        
        return result
    
    async def _analyze_relevance(self, kwargs: Dict[str, Any]) -> ToolResponse:
        """Analyze relevance of retrieved contexts"""
        query = kwargs.get('query', '')
        contexts = kwargs.get('contexts', [])
        
        if not contexts:
            return ToolResponse(
                success=False,
                message="No contexts provided for analysis",
                status=ToolStatus.FAILED
            )
        
        # Use LLM to analyze relevance
        analysis_prompt = f"""
        Analyze the relevance of the following contexts to the query.
        Rate each on a scale of 0-1 and explain why.
        
        Query: {query}
        
        Contexts:
        {json.dumps(contexts, indent=2)}
        
        Provide analysis in JSON format.
        """
        
        analysis_result = await self.llm_tool.execute(
            query=analysis_prompt,
            task_type='analysis',
            max_tokens=1000
        )
        
        if not analysis_result.success:
            return analysis_result
        
        return ToolResponse(
            success=True,
            message="Relevance analysis completed",
            data={
                "query": query,
                "analysis": analysis_result.data['response'],
                "context_count": len(contexts)
            }
        )
    
    # Helper methods
    
    async def _get_persona_context(self, persona_name: str) -> Optional[Dict[str, Any]]:
        """Get persona context"""
        result = await self.sql_tool.execute(
            operation='get_persona',
            name=persona_name
        )
        return result.data.get('persona') if result.success else None
    
    async def _retrieve_vector_context(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Retrieve vector contexts"""
        result = await self.vector_tool.execute(
            operation='rag_retrieve',
            query=query,
            context_limit=limit,
            max_tokens=1500
        )
        return result.data.get('contexts', []) if result.success else []
    
    async def _retrieve_memory_context(self, query: str, persona_id: Optional[int]) -> List[Dict[str, Any]]:
        """Retrieve memory contexts"""
        # First get high-importance memories
        result = await self.sql_tool.execute(
            operation='get_memory',
            persona_id=persona_id,
            importance_min=7,
            limit=3
        )
        
        memories = result.data.get('memories', []) if result.success else []
        
        # Also search for query-relevant memories
        search_result = await self.sql_tool.execute(
            operation='execute_query',
            query="""
                SELECT * FROM memory 
                WHERE content LIKE ? AND persona_id = ?
                ORDER BY importance DESC 
                LIMIT 3
            """,
            params=[f'%{query}%', persona_id] if persona_id else [f'%{query}%', -1]
        )
        
        if search_result.success:
            memories.extend(search_result.data.get('results', []))
        
        # Deduplicate
        seen_ids = set()
        unique_memories = []
        for mem in memories:
            if mem['id'] not in seen_ids:
                seen_ids.add(mem['id'])
                unique_memories.append(mem)
        
        return unique_memories[:5]  # Limit to 5 memories
    
    async def _retrieve_history_context(self, session_id: str, limit: int) -> List[Dict[str, Any]]:
        """Retrieve conversation history"""
        result = await self.sql_tool.execute(
            operation='get_conversations',
            session_id=session_id,
            limit=limit
        )
        return result.data.get('conversations', []) if result.success else []
    
    async def _build_rag_context(self, **kwargs) -> RAGContext:
        """Build combined RAG context"""
        query = kwargs.get('query', '')
        vector_results = kwargs.get('vector_results', [])
        memory_context = kwargs.get('memory_context', [])
        history_context = kwargs.get('history_context', [])
        persona_context = kwargs.get('persona_context')
        
        # Build combined context string
        context_parts = []
        
        # Add vector search results
        if vector_results:
            context_parts.append("## Relevant Knowledge:")
            for i, ctx in enumerate(vector_results, 1):
                context_parts.append(f"\n### Context {i} (Score: {ctx.get('score', 0):.3f}):")
                context_parts.append(ctx.get('text', ''))
        
        # Add memories
        if memory_context:
            context_parts.append("\n## Relevant Memories:")
            for mem in memory_context:
                context_parts.append(f"\n- [{mem.get('category', 'general')}] {mem.get('content', '')}")
        
        # Add conversation history
        if history_context:
            context_parts.append("\n## Recent Conversation:")
            for conv in history_context:
                context_parts.append(f"\nUser: {conv.get('user_input', '')}")
                context_parts.append(f"Assistant: {conv.get('assistant_response', '')}")
        
        combined_context = "\n".join(context_parts)
        
        # Calculate relevance scores
        relevance_scores = {
            "vector_average": sum(v.get('score', 0) for v in vector_results) / len(vector_results) if vector_results else 0,
            "memory_importance": sum(m.get('importance', 0) for m in memory_context) / len(memory_context) if memory_context else 0,
            "has_history": len(history_context) > 0
        }
        
        return RAGContext(
            query=query,
            vector_results=vector_results,
            sql_results=memory_context + history_context,
            persona_context=persona_context,
            memory_context=memory_context,
            combined_context=combined_context,
            relevance_scores=relevance_scores,
            timestamp=datetime.now().isoformat()
        )
    
    async def _generate_rag_response(self, query: str, rag_context: RAGContext, 
                                   persona_context: Optional[Dict[str, Any]]) -> str:
        """Generate response using RAG context"""
        # Build system message with persona
        system_message = "You are a helpful AI assistant."
        if persona_context:
            traits = persona_context.get('personality_traits', {})
            if isinstance(traits, str):
                traits = json.loads(traits)
            system_message = f"""You are {persona_context.get('name', 'an AI assistant')}. 
{persona_context.get('description', '')}

Personality: {', '.join(traits.get('traits', []))}
Communication style: {traits.get('communication_style', 'professional')}"""
        
        # Build prompt with context
        prompt = f"""Based on the following context, please answer the user's question.

{rag_context.combined_context}

User Question: {query}

Please provide a comprehensive and helpful response."""
        
        # Generate response
        result = await self.llm_tool.execute(
            query=prompt,
            system_message=system_message,
            task_type='general',
            max_tokens=1500
        )
        
        return result.data.get('response', 'I apologize, but I encountered an error generating a response.') if result.success else "Error generating response"
    
    async def _store_interaction(self, session_id: str, query: str, response: str, 
                               context: RAGContext, persona_id: Optional[int]):
        """Store the interaction in database"""
        # Store conversation
        await self.sql_tool.execute(
            operation='store_conversation',
            session_id=session_id,
            user_input=query,
            assistant_response=response,
            persona_id=persona_id,
            context=context.combined_context[:1000],  # Truncate for storage
            metadata={
                'vector_count': len(context.vector_results),
                'memory_count': len(context.memory_context),
                'relevance_scores': context.relevance_scores
            }
        )
        
        # Store as memory if important
        if len(response) > 100:  # Substantial response
            await self.sql_tool.execute(
                operation='store_memory',
                content=f"Q: {query}\nA: {response}",
                category='conversation',
                importance=6,
                persona_id=persona_id,
                tags=['interaction', session_id]
            )
    
    async def _rank_hybrid_results(self, query: str, results: Dict[str, List]) -> List[Dict[str, Any]]:
        """Rank and combine hybrid search results"""
        ranked = []
        
        # Add vector results with type tag
        for r in results.get('vector_results', []):
            ranked.append({
                'type': 'vector',
                'score': r.get('score', 0),
                'text': r.get('text', ''),
                'metadata': r.get('metadata', {})
            })
        
        # Add memory results
        for r in results.get('memory_results', []):
            ranked.append({
                'type': 'memory',
                'score': r.get('importance', 5) / 10.0,  # Normalize importance
                'text': r.get('content', ''),
                'metadata': {
                    'category': r.get('category'),
                    'access_count': r.get('access_count')
                }
            })
        
        # Add conversation results
        for r in results.get('conversation_results', []):
            ranked.append({
                'type': 'conversation',
                'score': 0.5,  # Default score for conversations
                'text': f"Q: {r.get('user_input', '')}\nA: {r.get('assistant_response', '')}",
                'metadata': {
                    'session_id': r.get('session_id'),
                    'timestamp': r.get('timestamp')
                }
            })
        
        # Sort by score
        ranked.sort(key=lambda x: x['score'], reverse=True)
        
        return ranked
    
    def _build_persona_prompt(self, persona: Dict[str, Any], query: str) -> str:
        """Build persona-aware prompt"""
        knowledge = persona.get('knowledge_base', {})
        if isinstance(knowledge, str):
            knowledge = json.loads(knowledge)
        
        return f"""As {persona.get('name')}, with expertise in {', '.join(knowledge.get('domains', []))}, 
please answer the following question: {query}"""
    
    def _apply_persona_style(self, response: str, persona: Dict[str, Any]) -> str:
        """Apply persona conversation style to response"""
        style = persona.get('conversation_style', {})
        if isinstance(style, str):
            style = json.loads(style)
        
        # Add persona-specific elements
        if not response.startswith(("I", "Let", "Here")):
            response = f"{style.get('acknowledgment', 'I understand.')} {response}"
        
        return response
    
    def get_schema(self) -> Dict[str, Any]:
        """Get tool schema"""
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["rag_query", "store_knowledge", "hybrid_search", 
                            "persona_query", "update_context", "analyze_relevance"],
                    "description": "RAG operation to perform"
                },
                "query": {
                    "type": "string",
                    "description": "Query text"
                },
                "texts": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Texts to store"
                },
                "session_id": {
                    "type": "string",
                    "description": "Session identifier"
                },
                "persona_name": {
                    "type": "string",
                    "description": "Persona name (default: Deanna)"
                },
                "category": {
                    "type": "string",
                    "description": "Category for storage"
                },
                "context_limit": {
                    "type": "integer",
                    "description": "Number of contexts to retrieve"
                },
                "include_memory": {
                    "type": "boolean",
                    "description": "Include memory in RAG"
                },
                "include_history": {
                    "type": "boolean",
                    "description": "Include conversation history"
                },
                "metadata": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Metadata for texts"
                }
            },
            "required": ["operation"]
        }