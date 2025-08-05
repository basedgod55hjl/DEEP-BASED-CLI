#!/usr/bin/env python3
"""
🔧 Sub-Agent Architecture - Anthropic Cookbook Inspired
Made by @Lucariolucario55 on Telegram

Advanced sub-agent architecture with hierarchical task delegation
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json
import uuid
from abc import ABC, abstractmethod
import sympy as sp

logger = logging.getLogger(__name__)


class AgentType(Enum):
    """Agent types for specialization"""

    COORDINATOR = "coordinator"
    CODER = "coder"
    ANALYZER = "analyzer"
    RESEARCHER = "researcher"
    VALIDATOR = "validator"
    OPTIMIZER = "optimizer"
    DEBUGGER = "debugger"
    SPECIALIST = "specialist"
    CALCULUS = "calculus"


class TaskPriority(Enum):
    """Task priority levels"""

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Task:
    """Task definition with metadata"""

    id: str
    type: str
    description: str
    priority: TaskPriority
    agent_type: AgentType
    input_data: Dict[str, Any]
    created_at: datetime
    deadline: Optional[datetime] = None
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskResult:
    """Task execution result"""

    task_id: str
    success: bool
    output: Any
    execution_time: float
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseAgent(ABC):
    """Base agent class with common functionality"""

    def __init__(self, agent_id: str, agent_type: AgentType, capabilities: List[str]):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.capabilities = capabilities
        self.is_busy = False
        self.task_history: List[TaskResult] = []
        self.performance_metrics = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "average_execution_time": 0.0,
            "success_rate": 1.0,
        }

    @abstractmethod
    async def execute_task(self, task: Task) -> TaskResult:
        """Execute a task and return result"""
        pass

    def can_handle_task(self, task: Task) -> bool:
        """Check if agent can handle the task"""
        return task.agent_type == self.agent_type

    def update_metrics(self, result: TaskResult):
        """Update performance metrics"""
        self.task_history.append(result)

        if result.success:
            self.performance_metrics["tasks_completed"] += 1
        else:
            self.performance_metrics["tasks_failed"] += 1

        # Update success rate
        total_tasks = (
            self.performance_metrics["tasks_completed"]
            + self.performance_metrics["tasks_failed"]
        )
        self.performance_metrics["success_rate"] = (
            self.performance_metrics["tasks_completed"] / total_tasks
        )

        # Update average execution time
        total_time = sum(r.execution_time for r in self.task_history)
        self.performance_metrics["average_execution_time"] = total_time / len(
            self.task_history
        )

    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "capabilities": self.capabilities,
            "is_busy": self.is_busy,
            "performance_metrics": self.performance_metrics,
            "recent_tasks": len(self.task_history[-10:]),  # Last 10 tasks
        }


class CoordinatorAgent(BaseAgent):
    """Main coordinator agent that delegates tasks to sub-agents"""

    def __init__(self, agent_id: str, sub_agents: List[BaseAgent]):
        super().__init__(
            agent_id, AgentType.COORDINATOR, ["task_delegation", "workflow_management"]
        )
        self.sub_agents = {agent.agent_id: agent for agent in sub_agents}
        self.task_queue: List[Task] = []
        self.active_tasks: Dict[str, Task] = {}
        self.completed_tasks: Dict[str, TaskResult] = {}

    async def execute_task(self, task: Task) -> TaskResult:
        """Coordinate task execution by delegating to appropriate sub-agents"""
        start_time = datetime.now()

        try:
            # Find suitable sub-agent
            suitable_agents = [
                agent
                for agent in self.sub_agents.values()
                if agent.can_handle_task(task) and not agent.is_busy
            ]

            if not suitable_agents:
                # Find best available agent based on performance
                suitable_agents = [
                    agent
                    for agent in self.sub_agents.values()
                    if agent.can_handle_task(task)
                ]

                if not suitable_agents:
                    raise Exception(
                        f"No suitable agent found for task type: {task.agent_type}"
                    )

                # Sort by success rate and average execution time
                suitable_agents.sort(
                    key=lambda a: (
                        a.performance_metrics["success_rate"],
                        -a.performance_metrics["average_execution_time"],
                    ),
                    reverse=True,
                )

            selected_agent = suitable_agents[0]
            selected_agent.is_busy = True

            try:
                # Execute task
                result = await selected_agent.execute_task(task)

                # Update agent metrics
                selected_agent.update_metrics(result)

                # Store completed task
                self.completed_tasks[task.id] = result

                return result

            finally:
                selected_agent.is_busy = False

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            result = TaskResult(
                task_id=task.id,
                success=False,
                output=None,
                execution_time=execution_time,
                error_message=str(e),
            )

            self.completed_tasks[task.id] = result
            return result

    async def delegate_complex_task(
        self, description: str, subtasks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Delegate a complex task by breaking it into subtasks"""
        task_id = str(uuid.uuid4())
        results = {}

        # Create and execute subtasks
        for i, subtask_data in enumerate(subtasks):
            subtask = Task(
                id=f"{task_id}_subtask_{i}",
                type=subtask_data["type"],
                description=subtask_data["description"],
                priority=TaskPriority(subtask_data.get("priority", 2)),
                agent_type=AgentType(subtask_data["agent_type"]),
                input_data=subtask_data.get("input_data", {}),
                created_at=datetime.now(),
                dependencies=subtask_data.get("dependencies", []),
            )

            result = await self.execute_task(subtask)
            results[subtask.id] = result

        # Aggregate results
        return {
            "task_id": task_id,
            "subtask_results": results,
            "overall_success": all(r.success for r in results.values()),
            "total_execution_time": sum(r.execution_time for r in results.values()),
        }

    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        return {
            "coordinator": self.get_status(),
            "sub_agents": {
                agent_id: agent.get_status()
                for agent_id, agent in self.sub_agents.items()
            },
            "task_queue_length": len(self.task_queue),
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
        }


class CoderAgent(BaseAgent):
    """Specialized agent for code generation and modification"""

    def __init__(self, agent_id: str, llm_client):
        super().__init__(
            agent_id, AgentType.CODER, ["code_generation", "code_review", "refactoring"]
        )
        self.llm_client = llm_client

    async def execute_task(self, task: Task) -> TaskResult:
        start_time = datetime.now()

        try:
            if task.type == "code_generation":
                output = await self._generate_code(task.input_data)
            elif task.type == "code_review":
                output = await self._review_code(task.input_data)
            elif task.type == "refactoring":
                output = await self._refactor_code(task.input_data)
            else:
                raise ValueError(f"Unknown task type: {task.type}")

            execution_time = (datetime.now() - start_time).total_seconds()
            result = TaskResult(
                task_id=task.id,
                success=True,
                output=output,
                execution_time=execution_time,
            )

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            result = TaskResult(
                task_id=task.id,
                success=False,
                output=None,
                execution_time=execution_time,
                error_message=str(e),
            )

        self.update_metrics(result)
        return result

    async def _generate_code(self, input_data: Dict[str, Any]) -> str:
        """Generate code based on requirements"""
        prompt = f"""
Generate code for the following requirements:
{input_data.get('requirements', '')}

Language: {input_data.get('language', 'python')}
Style: {input_data.get('style', 'clean and readable')}
"""

        response = await self.llm_client.generate_response(prompt)
        return response

    async def _review_code(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Review code for issues and improvements"""
        code = input_data.get("code", "")
        prompt = f"""
Review the following code for issues, improvements, and best practices:

```{input_data.get('language', 'python')}
{code}
```

Provide a detailed analysis including:
1. Potential bugs
2. Performance issues
3. Security concerns
4. Code style improvements
5. Best practices recommendations
"""

        response = await self.llm_client.generate_response(prompt)
        return {"review": response}

    async def _refactor_code(self, input_data: Dict[str, Any]) -> str:
        """Refactor code for better structure and performance"""
        code = input_data.get("code", "")
        prompt = f"""
Refactor the following code to improve:
- Readability
- Performance
- Maintainability
- Code structure

Original code:
```{input_data.get('language', 'python')}
{code}
```

Provide the refactored version with explanations of the improvements.
"""

        response = await self.llm_client.generate_response(prompt)
        return response


class AnalyzerAgent(BaseAgent):
    """Specialized agent for code and data analysis"""

    def __init__(self, agent_id: str, llm_client):
        super().__init__(
            agent_id,
            AgentType.ANALYZER,
            ["code_analysis", "performance_analysis", "security_analysis"],
        )
        self.llm_client = llm_client

    async def execute_task(self, task: Task) -> TaskResult:
        start_time = datetime.now()

        try:
            if task.type == "code_analysis":
                output = await self._analyze_code(task.input_data)
            elif task.type == "performance_analysis":
                output = await self._analyze_performance(task.input_data)
            elif task.type == "security_analysis":
                output = await self._analyze_security(task.input_data)
            else:
                raise ValueError(f"Unknown task type: {task.type}")

            execution_time = (datetime.now() - start_time).total_seconds()
            result = TaskResult(
                task_id=task.id,
                success=True,
                output=output,
                execution_time=execution_time,
            )

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            result = TaskResult(
                task_id=task.id,
                success=False,
                output=None,
                execution_time=execution_time,
                error_message=str(e),
            )

        self.update_metrics(result)
        return result

    async def _analyze_code(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code for complexity, maintainability, etc."""
        code = input_data.get("code", "")
        prompt = f"""
Analyze the following code for:
1. Cyclomatic complexity
2. Maintainability index
3. Code smells
4. Potential improvements

Code:
```{input_data.get('language', 'python')}
{code}
```

Provide a structured analysis with metrics and recommendations.
"""

        response = await self.llm_client.generate_response(prompt)
        return {"analysis": response}

    async def _analyze_performance(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code for performance issues"""
        code = input_data.get("code", "")
        prompt = f"""
Analyze the following code for performance issues:

```{input_data.get('language', 'python')}
{code}
```

Identify:
1. Time complexity issues
2. Memory usage problems
3. Inefficient algorithms
4. Optimization opportunities
"""

        response = await self.llm_client.generate_response(prompt)
        return {"performance_analysis": response}

    async def _analyze_security(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code for security vulnerabilities"""
        code = input_data.get("code", "")
        prompt = f"""
Analyze the following code for security vulnerabilities:

```{input_data.get('language', 'python')}
{code}
```

Identify:
1. SQL injection vulnerabilities
2. XSS vulnerabilities
3. Input validation issues
4. Authentication/authorization problems
5. Data exposure risks
"""

        response = await self.llm_client.generate_response(prompt)
        return {"security_analysis": response}


class ResearcherAgent(BaseAgent):
    """Specialized agent for research and information gathering"""

    def __init__(self, agent_id: str, llm_client, search_tool):
        super().__init__(
            agent_id,
            AgentType.RESEARCHER,
            ["web_search", "documentation_search", "research_synthesis"],
        )
        self.llm_client = llm_client
        self.search_tool = search_tool

    async def execute_task(self, task: Task) -> TaskResult:
        start_time = datetime.now()

        try:
            if task.type == "web_search":
                output = await self._search_web(task.input_data)
            elif task.type == "documentation_search":
                output = await self._search_documentation(task.input_data)
            elif task.type == "research_synthesis":
                output = await self._synthesize_research(task.input_data)
            else:
                raise ValueError(f"Unknown task type: {task.type}")

            execution_time = (datetime.now() - start_time).total_seconds()
            result = TaskResult(
                task_id=task.id,
                success=True,
                output=output,
                execution_time=execution_time,
            )

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            result = TaskResult(
                task_id=task.id,
                success=False,
                output=None,
                execution_time=execution_time,
                error_message=str(e),
            )

        self.update_metrics(result)
        return result

    async def _search_web(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Search the web for information"""
        query = input_data.get("query", "")
        results = await self.search_tool.search(query)
        return {"search_results": results}

    async def _search_documentation(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Search documentation for specific information"""
        query = input_data.get("query", "")
        prompt = f"""
Search for documentation about: {query}

Provide:
1. Relevant documentation links
2. Key concepts and explanations
3. Code examples
4. Best practices
"""

        response = await self.llm_client.generate_response(prompt)
        return {"documentation_search": response}

    async def _synthesize_research(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize research findings"""
        findings = input_data.get("findings", [])
        prompt = f"""
Synthesize the following research findings:

{findings}

Provide:
1. Key insights
2. Patterns and trends
3. Recommendations
4. Action items
"""

        response = await self.llm_client.generate_response(prompt)
        return {"synthesis": response}


class CalculusAgent(BaseAgent):
    """Specialized agent for calculus operations"""

    def __init__(self, agent_id: str):
        super().__init__(
            agent_id, AgentType.CALCULUS, ["derivative", "integral", "limit"]
        )

    async def execute_task(self, task: Task) -> TaskResult:
        start_time = datetime.now()
        try:
            if task.type == "derivative":
                output = self._calculate_derivative(task.input_data)
            elif task.type == "integral":
                output = self._calculate_integral(task.input_data)
            elif task.type == "limit":
                output = self._calculate_limit(task.input_data)
            else:
                raise ValueError(f"Unknown task type: {task.type}")

            execution_time = (datetime.now() - start_time).total_seconds()
            result = TaskResult(
                task_id=task.id,
                success=True,
                output=output,
                execution_time=execution_time,
            )
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            result = TaskResult(
                task_id=task.id,
                success=False,
                output=None,
                execution_time=execution_time,
                error_message=str(e),
            )

        self.update_metrics(result)
        return result

    def _calculate_derivative(self, input_data: Dict[str, Any]) -> str:
        expr = sp.sympify(input_data.get("expression", ""))
        var = sp.symbols(input_data.get("variable", "x"))
        return str(sp.diff(expr, var))

    def _calculate_integral(self, input_data: Dict[str, Any]) -> str:
        expr = sp.sympify(input_data.get("expression", ""))
        var = sp.symbols(input_data.get("variable", "x"))
        return str(sp.integrate(expr, var))

    def _calculate_limit(self, input_data: Dict[str, Any]) -> str:
        expr = sp.sympify(input_data.get("expression", ""))
        var = sp.symbols(input_data.get("variable", "x"))
        point = input_data.get("point", 0)
        direction = input_data.get("direction", "+")
        result = sp.limit(expr, var, point, dir=direction)
        return str(result)


# Agent Factory
class AgentFactory:
    """Factory for creating specialized agents"""

    @staticmethod
    def create_agent(agent_type: AgentType, agent_id: str, **kwargs) -> BaseAgent:
        """Create an agent of the specified type"""
        if agent_type == AgentType.CODER:
            return CoderAgent(agent_id, kwargs.get("llm_client"))
        elif agent_type == AgentType.ANALYZER:
            return AnalyzerAgent(agent_id, kwargs.get("llm_client"))
        elif agent_type == AgentType.RESEARCHER:
            return ResearcherAgent(
                agent_id, kwargs.get("llm_client"), kwargs.get("search_tool")
            )
        elif agent_type == AgentType.CALCULUS:
            return CalculusAgent(agent_id)
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")


# Enhanced Sub-Agent System
class SubAgentSystem:
    """Main system for managing sub-agents"""

    def __init__(self, llm_client, search_tool=None):
        self.llm_client = llm_client
        self.search_tool = search_tool

        # Create sub-agents
        self.agents = {
            "coder": AgentFactory.create_agent(
                AgentType.CODER, "coder_001", llm_client=llm_client
            ),
            "analyzer": AgentFactory.create_agent(
                AgentType.ANALYZER, "analyzer_001", llm_client=llm_client
            ),
            "researcher": AgentFactory.create_agent(
                AgentType.RESEARCHER,
                "researcher_001",
                llm_client=llm_client,
                search_tool=search_tool,
            ),
            "calculus": AgentFactory.create_agent(AgentType.CALCULUS, "calculus_001"),
        }

        # Create coordinator
        self.coordinator = CoordinatorAgent(
            "coordinator_001", list(self.agents.values())
        )

    async def execute_complex_task(
        self, description: str, subtasks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute a complex task using sub-agents"""
        return await self.coordinator.delegate_complex_task(description, subtasks)

    async def generate_code_with_analysis(
        self, requirements: str, language: str = "python"
    ) -> Dict[str, Any]:
        """Generate code with comprehensive analysis"""
        description = f"Generate {language} code with analysis"
        subtasks = [
            {
                "type": "code_generation",
                "description": f"Generate {language} code for: {requirements}",
                "agent_type": "coder",
                "priority": 3,
                "input_data": {"requirements": requirements, "language": language},
            },
            {
                "type": "code_analysis",
                "description": "Analyze the generated code",
                "agent_type": "analyzer",
                "priority": 2,
                "input_data": {
                    "code": "{{code_generation.output}}",
                    "language": language,
                },
                "dependencies": ["code_generation"],
            },
            {
                "type": "security_analysis",
                "description": "Perform security analysis",
                "agent_type": "analyzer",
                "priority": 2,
                "input_data": {
                    "code": "{{code_generation.output}}",
                    "language": language,
                },
                "dependencies": ["code_generation"],
            },
        ]

        return await self.execute_complex_task(description, subtasks)

    async def solve_calculus(
        self, task_type: str, expression: str, variable: str = "x", **kwargs
    ) -> Dict[str, Any]:
        """Solve a calculus problem using the calculus agent"""
        subtask = {
            "type": task_type,
            "description": f"{task_type} for {expression}",
            "agent_type": "calculus",
            "priority": 2,
            "input_data": {"expression": expression, "variable": variable, **kwargs},
        }
        return await self.execute_complex_task("calculus_task", [subtask])

    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        return self.coordinator.get_system_status()


# Example usage
async def test_sub_agent_system():
    """Test the sub-agent system"""

    # Mock LLM client
    class MockLLMClient:
        async def generate_response(self, prompt: str) -> str:
            await asyncio.sleep(0.1)  # Simulate API call
            return f"Response to: {prompt[:50]}..."

    # Mock search tool
    class MockSearchTool:
        async def search(self, query: str) -> Dict[str, Any]:
            await asyncio.sleep(0.1)  # Simulate search
            return {
                "results": [
                    {"title": f"Result for {query}", "snippet": "Sample result"}
                ]
            }

    # Create system
    llm_client = MockLLMClient()
    search_tool = MockSearchTool()
    system = SubAgentSystem(llm_client, search_tool)

    # Test complex task
    result = await system.generate_code_with_analysis(
        "Create a web scraper that extracts article titles", "python"
    )

    print(f"Task result: {result}")

    # Get system status
    status = system.get_system_status()
    print(f"System status: {status}")


if __name__ == "__main__":
    asyncio.run(test_sub_agent_system())
