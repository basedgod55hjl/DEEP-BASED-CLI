"""
Advanced Reasoning Engine - Enhanced BASED GOD CLI
Fast iterative LLM reasoning loops with multi-step analysis
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

from .base_tool import BaseTool, ToolResponse, ToolStatus

class ReasoningStep(Enum):
    INITIAL_ANALYSIS = "initial_analysis"
    INTENT_CLARIFICATION = "intent_clarification"
    TOOL_SELECTION = "tool_selection"
    PARAMETER_OPTIMIZATION = "parameter_optimization"
    EXECUTION_STRATEGY = "execution_strategy"
    RESULT_VALIDATION = "result_validation"
    LEARNING_INTEGRATION = "learning_integration"

@dataclass
class ReasoningState:
    step: ReasoningStep
    input_data: Dict[str, Any]
    reasoning: str
    confidence: float
    next_actions: List[str]
    llm_consultation: Optional[Dict[str, Any]] = None
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

@dataclass
class ReasoningChain:
    chain_id: str
    user_query: str
    steps: List[ReasoningState]
    final_decision: Optional[Dict[str, Any]] = None
    total_confidence: float = 0.0
    execution_time: float = 0.0

class FastReasoningEngine(BaseTool):
    """
    Fast iterative reasoning engine with LLM consultation loops
    """
    
    def __init__(self, llm_tool=None):
        super().__init__(
            name="Fast Reasoning Engine",
            description="Multi-step reasoning engine with fast LLM consultation loops",
            capabilities=[
                "Multi-step iterative reasoning",
                "Real-time LLM consultation",
                "Fast decision loops",
                "Confidence tracking",
                "Learning integration",
                "Reasoning chain analysis"
            ]
        )
        self.llm_tool = llm_tool
        self.reasoning_chains = []
        self.optimization_patterns = {}
        
    async def execute(self, **kwargs) -> ToolResponse:
        """Execute fast reasoning loop"""
        
        user_query = kwargs.get("user_query", "")
        context = kwargs.get("context", {})
        max_iterations = kwargs.get("max_iterations", 5)
        speed_mode = kwargs.get("speed_mode", True)
        
        if not user_query:
            return ToolResponse(
                success=False,
                message="User query is required for reasoning",
                status=ToolStatus.FAILED
            )
        
        try:
            # Start fast reasoning chain
            reasoning_chain = await self._execute_fast_reasoning_loop(
                user_query, context, max_iterations, speed_mode
            )
            
            # Store reasoning chain
            self.reasoning_chains.append(reasoning_chain)
            
            return ToolResponse(
                success=True,
                message="Fast reasoning completed successfully",
                data={
                    "reasoning_chain": asdict(reasoning_chain),
                    "final_decision": reasoning_chain.final_decision,
                    "confidence": reasoning_chain.total_confidence,
                    "steps_completed": len(reasoning_chain.steps),
                    "execution_time": reasoning_chain.execution_time
                },
                metadata={
                    "chain_id": reasoning_chain.chain_id,
                    "speed_optimized": speed_mode
                }
            )
            
        except Exception as e:
            return ToolResponse(
                success=False,
                message=f"Reasoning failed: {str(e)}",
                status=ToolStatus.FAILED
            )
    
    def get_schema(self) -> Dict[str, Any]:
        """Get reasoning engine schema"""
        return {
            "type": "object",
            "properties": {
                "user_query": {
                    "type": "string",
                    "description": "User query to reason about"
                },
                "context": {
                    "type": "object",
                    "description": "Additional context for reasoning"
                },
                "max_iterations": {
                    "type": "integer",
                    "description": "Maximum reasoning iterations",
                    "default": 5,
                    "minimum": 1,
                    "maximum": 10
                },
                "speed_mode": {
                    "type": "boolean",
                    "description": "Enable speed optimizations",
                    "default": True
                }
            },
            "required": ["user_query"]
        }
    
    async def _execute_fast_reasoning_loop(self, user_query: str, context: Dict, 
                                         max_iterations: int, speed_mode: bool) -> ReasoningChain:
        """Execute the main fast reasoning loop"""
        
        start_time = datetime.now()
        chain_id = self._generate_chain_id()
        
        reasoning_chain = ReasoningChain(
            chain_id=chain_id,
            user_query=user_query,
            steps=[]
        )
        
        current_state = None
        
        # Fast reasoning loop
        for iteration in range(max_iterations):
            
            # Determine next reasoning step
            next_step = self._determine_next_step(current_state, iteration)
            
            if next_step is None:
                break  # Reasoning complete
            
            # Execute reasoning step with LLM consultation
            reasoning_state = await self._execute_reasoning_step(
                next_step, user_query, context, current_state, speed_mode
            )
            
            reasoning_chain.steps.append(reasoning_state)
            current_state = reasoning_state
            
            # Check if we have enough confidence to proceed
            if reasoning_state.confidence > 0.9 and iteration >= 2:
                break  # High confidence, can stop early
        
        # Generate final decision
        reasoning_chain.final_decision = await self._generate_final_decision(reasoning_chain)
        reasoning_chain.total_confidence = self._calculate_total_confidence(reasoning_chain)
        
        end_time = datetime.now()
        reasoning_chain.execution_time = (end_time - start_time).total_seconds()
        
        return reasoning_chain
    
    def _determine_next_step(self, current_state: Optional[ReasoningState], iteration: int) -> Optional[ReasoningStep]:
        """Determine the next reasoning step"""
        
        if iteration == 0:
            return ReasoningStep.INITIAL_ANALYSIS
        
        if current_state is None:
            return ReasoningStep.INITIAL_ANALYSIS
        
        current_step = current_state.step
        
        # Fast reasoning progression
        step_progression = {
            ReasoningStep.INITIAL_ANALYSIS: ReasoningStep.INTENT_CLARIFICATION,
            ReasoningStep.INTENT_CLARIFICATION: ReasoningStep.TOOL_SELECTION,
            ReasoningStep.TOOL_SELECTION: ReasoningStep.PARAMETER_OPTIMIZATION,
            ReasoningStep.PARAMETER_OPTIMIZATION: ReasoningStep.EXECUTION_STRATEGY,
            ReasoningStep.EXECUTION_STRATEGY: None  # Complete
        }
        
        return step_progression.get(current_step)
    
    async def _execute_reasoning_step(self, step: ReasoningStep, user_query: str, 
                                    context: Dict, previous_state: Optional[ReasoningState],
                                    speed_mode: bool) -> ReasoningState:
        """Execute a single reasoning step with LLM consultation"""
        
        # Prepare step-specific prompts and data
        step_data = self._prepare_step_data(step, user_query, context, previous_state)
        
        # Fast LLM consultation
        llm_response = await self._fast_llm_consultation(step, step_data, speed_mode)
        
        # Process LLM response into reasoning state
        reasoning_state = self._process_llm_response(step, step_data, llm_response)
        
        return reasoning_state
    
    def _prepare_step_data(self, step: ReasoningStep, user_query: str, 
                          context: Dict, previous_state: Optional[ReasoningState]) -> Dict[str, Any]:
        """Prepare data for each reasoning step"""
        
        base_data = {
            "user_query": user_query,
            "context": context,
            "previous_reasoning": previous_state.reasoning if previous_state else None,
            "previous_confidence": previous_state.confidence if previous_state else 0.0
        }
        
        if step == ReasoningStep.INITIAL_ANALYSIS:
            base_data.update({
                "focus": "Analyze user intent and identify key requirements",
                "output_format": "intent, complexity, urgency, domain"
            })
        
        elif step == ReasoningStep.INTENT_CLARIFICATION:
            base_data.update({
                "focus": "Clarify specific user intent and resolve ambiguities",
                "output_format": "clarified_intent, assumptions, confidence_factors"
            })
        
        elif step == ReasoningStep.TOOL_SELECTION:
            base_data.update({
                "focus": "Select optimal tools for the task",
                "available_tools": ["web_scraper", "code_generator", "data_analyzer", "file_processor", "memory_tool", "llm_query_tool"],
                "output_format": "primary_tool, secondary_tools, reasoning"
            })
        
        elif step == ReasoningStep.PARAMETER_OPTIMIZATION:
            base_data.update({
                "focus": "Optimize parameters for selected tools",
                "output_format": "optimized_parameters, expected_performance, risk_factors"
            })
        
        elif step == ReasoningStep.EXECUTION_STRATEGY:
            base_data.update({
                "focus": "Plan execution strategy and fallbacks",
                "output_format": "execution_plan, fallback_options, success_criteria"
            })
        
        return base_data
    
    async def _fast_llm_consultation(self, step: ReasoningStep, step_data: Dict, speed_mode: bool) -> Dict[str, Any]:
        """Fast LLM consultation for reasoning step"""
        
        if not self.llm_tool:
            # Fallback to rule-based reasoning
            return self._fallback_reasoning(step, step_data)
        
        # Create optimized prompt for speed
        prompt = self._create_fast_prompt(step, step_data, speed_mode)
        
        try:
            # Fast LLM call with optimized parameters
            llm_params = {
                "query": prompt,
                "task_type": "reasoning",
                "max_tokens": 150 if speed_mode else 300,
                "temperature": 0.3  # Lower temperature for consistent reasoning
            }
            
            result = await self.llm_tool.safe_execute(**llm_params)
            
            if result.success:
                return {
                    "llm_response": result.data.get("response", ""),
                    "provider": result.data.get("provider", "unknown"),
                    "success": True
                }
            else:
                return self._fallback_reasoning(step, step_data)
                
        except Exception as e:
            return self._fallback_reasoning(step, step_data)
    
    def _create_fast_prompt(self, step: ReasoningStep, step_data: Dict, speed_mode: bool) -> str:
        """Create optimized prompt for fast reasoning"""
        
        user_query = step_data["user_query"]
        focus = step_data.get("focus", "")
        output_format = step_data.get("output_format", "")
        
        if speed_mode:
            # Ultra-fast prompt
            prompt = f"""FAST REASONING - {step.value.upper()}

Query: {user_query}
Focus: {focus}
Output: {output_format}

Quick analysis (2-3 lines):"""
        else:
            # Standard prompt
            prompt = f"""REASONING STEP: {step.value.upper()}

User Query: {user_query}
Context: {step_data.get('context', {})}
Focus: {focus}
Previous: {step_data.get('previous_reasoning', 'None')}

Required Output Format: {output_format}

Analysis:"""
        
        return prompt
    
    def _fallback_reasoning(self, step: ReasoningStep, step_data: Dict) -> Dict[str, Any]:
        """Fallback reasoning when LLM is unavailable"""
        
        user_query = step_data["user_query"].lower()
        
        fallback_responses = {
            ReasoningStep.INITIAL_ANALYSIS: {
                "intent": self._analyze_intent_keywords(user_query),
                "complexity": "medium",
                "urgency": "normal",
                "domain": self._identify_domain(user_query)
            },
            ReasoningStep.TOOL_SELECTION: {
                "primary_tool": self._select_tool_by_keywords(user_query),
                "reasoning": "Selected based on keyword analysis"
            }
        }
        
        return {
            "llm_response": fallback_responses.get(step, {"reasoning": "Fallback analysis"}),
            "provider": "fallback",
            "success": True
        }
    
    def _process_llm_response(self, step: ReasoningStep, step_data: Dict, llm_response: Dict) -> ReasoningState:
        """Process LLM response into structured reasoning state"""
        
        response_text = llm_response.get("llm_response", "")
        
        # Extract confidence from response quality
        confidence = self._calculate_step_confidence(step, response_text, llm_response["success"])
        
        # Determine next actions based on step
        next_actions = self._determine_next_actions(step, response_text)
        
        return ReasoningState(
            step=step,
            input_data=step_data,
            reasoning=response_text,
            confidence=confidence,
            next_actions=next_actions,
            llm_consultation=llm_response
        )
    
    def _calculate_step_confidence(self, step: ReasoningStep, response: str, llm_success: bool) -> float:
        """Calculate confidence for reasoning step"""
        
        base_confidence = 0.8 if llm_success else 0.5
        
        # Adjust based on response quality
        response_quality_factors = [
            len(response) > 20,  # Sufficient detail
            "because" in response.lower() or "reason" in response.lower(),  # Reasoning present
            "confident" in response.lower() or "certain" in response.lower(),  # Explicit confidence
            step.value in response.lower()  # Relevant to step
        ]
        
        quality_boost = sum(response_quality_factors) * 0.05
        final_confidence = min(0.95, base_confidence + quality_boost)
        
        return final_confidence
    
    def _determine_next_actions(self, step: ReasoningStep, response: str) -> List[str]:
        """Determine next actions based on reasoning step"""
        
        actions_map = {
            ReasoningStep.INITIAL_ANALYSIS: ["clarify_intent", "identify_requirements"],
            ReasoningStep.INTENT_CLARIFICATION: ["select_tools", "gather_context"],
            ReasoningStep.TOOL_SELECTION: ["optimize_parameters", "prepare_execution"],
            ReasoningStep.PARAMETER_OPTIMIZATION: ["plan_execution", "setup_fallbacks"],
            ReasoningStep.EXECUTION_STRATEGY: ["execute_plan", "monitor_results"]
        }
        
        return actions_map.get(step, ["continue_reasoning"])
    
    async def _generate_final_decision(self, reasoning_chain: ReasoningChain) -> Dict[str, Any]:
        """Generate final decision from reasoning chain with DeepSeek chat → reasoner → chat flow"""
        
        if not reasoning_chain.steps:
            # Default to DeepSeek chat for any conversation
            return {
                "decision_type": "tool_execution",
                "selected_tools": ["llm_query_tool"],
                "parameters": {"query": reasoning_chain.user_query, "task_type": "general"},
                "confidence_score": 0.5
            }
        
        # Aggregate reasoning from all steps
        tool_selections = []
        parameters = {}
        execution_plans = []
        
        for step_state in reasoning_chain.steps:
            if step_state.step == ReasoningStep.TOOL_SELECTION:
                if isinstance(step_state.llm_consultation.get("llm_response"), dict):
                    tool = step_state.llm_consultation["llm_response"].get("primary_tool")
                    if tool:
                        tool_selections.append(tool)
            elif step_state.step == ReasoningStep.PARAMETER_OPTIMIZATION:
                # Extract parameters from reasoning
                params = self._extract_parameters_from_reasoning(step_state.reasoning)
                parameters.update(params)
            elif step_state.step == ReasoningStep.EXECUTION_STRATEGY:
                execution_plans.append(step_state.reasoning)
        
        # Ensure we always have at least one tool selected
        if not tool_selections:
            # Default to DeepSeek chat for all conversations
            tool_selections = ["llm_query_tool"]
            
        # Ensure parameters include the original query
        if "query" not in parameters:
            parameters["query"] = reasoning_chain.user_query
            
        # Set task type for proper DeepSeek model selection
        if "task_type" not in parameters:
            parameters["task_type"] = self._determine_task_type(reasoning_chain.user_query)
        
        # Generate final decision with DeepSeek flow
        final_decision = {
            "decision_type": "deepseek_conversation_flow",
            "selected_tools": tool_selections,
            "parameters": parameters,
            "execution_strategy": execution_plans[-1] if execution_plans else "deepseek_chat_to_reasoner",
            "reasoning_summary": self._summarize_reasoning_chain(reasoning_chain),
            "confidence_score": max(reasoning_chain.total_confidence, 0.5)  # Minimum confidence for DeepSeek
        }
        
        return final_decision
    
    def _determine_task_type(self, query: str) -> str:
        """Determine task type for proper DeepSeek model selection"""
        query_lower = query.lower()
        
        # Coding related
        if any(word in query_lower for word in ["code", "function", "python", "javascript", "program", "debug", "syntax"]):
            return "coding"
        
        # Analysis related
        elif any(word in query_lower for word in ["analyze", "data", "statistics", "chart", "report"]):
            return "analysis"
        
        # Creative related
        elif any(word in query_lower for word in ["write", "story", "creative", "poem", "imagine"]):
            return "creative"
        
        # Reasoning related
        elif any(word in query_lower for word in ["explain", "why", "how", "reason", "logic", "think"]):
            return "reasoning"
        
        # Default to general conversation
        else:
            return "general"
    
    def _calculate_total_confidence(self, reasoning_chain: ReasoningChain) -> float:
        """Calculate total confidence for reasoning chain"""
        
        if not reasoning_chain.steps:
            return 0.0
        
        # Weighted average of step confidences
        total_weight = 0
        weighted_confidence = 0
        
        step_weights = {
            ReasoningStep.INITIAL_ANALYSIS: 1.0,
            ReasoningStep.INTENT_CLARIFICATION: 1.2,
            ReasoningStep.TOOL_SELECTION: 1.5,
            ReasoningStep.PARAMETER_OPTIMIZATION: 1.3,
            ReasoningStep.EXECUTION_STRATEGY: 1.1
        }
        
        for step_state in reasoning_chain.steps:
            weight = step_weights.get(step_state.step, 1.0)
            weighted_confidence += step_state.confidence * weight
            total_weight += weight
        
        return weighted_confidence / total_weight if total_weight > 0 else 0.0
    
    # Helper methods for fallback reasoning
    def _analyze_intent_keywords(self, query: str) -> str:
        """Analyze intent from keywords"""
        intent_keywords = {
            "create": ["create", "generate", "build", "make"],
            "analyze": ["analyze", "examine", "study", "review"],
            "scrape": ["scrape", "extract", "crawl", "fetch"],
            "process": ["process", "handle", "manage", "work"],
            "search": ["search", "find", "look", "query"]
        }
        
        for intent, keywords in intent_keywords.items():
            if any(keyword in query for keyword in keywords):
                return intent
        
        return "general"
    
    def _identify_domain(self, query: str) -> str:
        """Identify domain from query"""
        domain_keywords = {
            "web": ["web", "html", "url", "website", "scrape"],
            "code": ["code", "function", "script", "program"],
            "data": ["data", "csv", "json", "analyze"],
            "file": ["file", "read", "write", "save"]
        }
        
        for domain, keywords in domain_keywords.items():
            if any(keyword in query for keyword in keywords):
                return domain
        
        return "general"
    
    def _select_tool_by_keywords(self, query: str) -> str:
        """Select tool based on keywords"""
        tool_keywords = {
            "web_scraper": ["scrape", "web", "html", "crawl"],
            "code_generator": ["code", "generate", "function", "script"],
            "data_analyzer": ["analyze", "data", "csv", "json"],
            "file_processor": ["file", "read", "write", "save"],
            "llm_query_tool": ["ask", "question", "explain", "help"]
        }
        
        for tool, keywords in tool_keywords.items():
            if any(keyword in query for keyword in keywords):
                return tool
        
        return "llm_query_tool"  # Default
    
    def _extract_parameters_from_reasoning(self, reasoning: str) -> Dict[str, Any]:
        """Extract parameters from reasoning text"""
        parameters = {}
        
        # Simple parameter extraction
        if "url" in reasoning.lower():
            import re
            urls = re.findall(r'https?://[^\s]+', reasoning)
            if urls:
                parameters["url"] = urls[0]
        
        if "language" in reasoning.lower():
            languages = ["python", "javascript", "html", "css"]
            for lang in languages:
                if lang in reasoning.lower():
                    parameters["language"] = lang
                    break
        
        return parameters
    
    def _summarize_reasoning_chain(self, reasoning_chain: ReasoningChain) -> str:
        """Summarize the entire reasoning chain"""
        
        summary_parts = []
        
        for step_state in reasoning_chain.steps:
            step_summary = f"{step_state.step.value}: {step_state.reasoning[:100]}..."
            summary_parts.append(step_summary)
        
        return " → ".join(summary_parts)
    
    def _generate_chain_id(self) -> str:
        """Generate unique chain ID"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def get_reasoning_analytics(self) -> Dict[str, Any]:
        """Get analytics on reasoning patterns"""
        
        if not self.reasoning_chains:
            return {"message": "No reasoning chains available"}
        
        total_chains = len(self.reasoning_chains)
        avg_confidence = sum(chain.total_confidence for chain in self.reasoning_chains) / total_chains
        avg_steps = sum(len(chain.steps) for chain in self.reasoning_chains) / total_chains
        avg_execution_time = sum(chain.execution_time for chain in self.reasoning_chains) / total_chains
        
        # Step analysis
        step_counts = {}
        for chain in self.reasoning_chains:
            for step_state in chain.steps:
                step_name = step_state.step.value
                step_counts[step_name] = step_counts.get(step_name, 0) + 1
        
        return {
            "total_reasoning_chains": total_chains,
            "average_confidence": avg_confidence,
            "average_steps_per_chain": avg_steps,
            "average_execution_time": avg_execution_time,
            "step_usage": step_counts,
            "recent_chains": [
                {
                    "id": chain.chain_id,
                    "query": chain.user_query[:50] + "...",
                    "confidence": chain.total_confidence,
                    "steps": len(chain.steps)
                }
                for chain in self.reasoning_chains[-5:]  # Last 5 chains
            ]
        }