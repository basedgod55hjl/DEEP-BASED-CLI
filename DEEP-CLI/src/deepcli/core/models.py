"""
Core data models and enums for DeepCLI
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class DeepSeekModel(str, Enum):
    """Available DeepSeek models"""
    CHAT = "deepseek-chat"
    REASONER = "deepseek-reasoner"


class ResponseFormat(str, Enum):
    """Response format options"""
    TEXT = "text"
    JSON = "json_object"


class CommandType(str, Enum):
    """Available command types"""
    IMPLEMENT = "implement"
    ANALYZE = "analyze"
    DESIGN = "design"
    TEST = "test"
    DOCUMENT = "document"
    REVIEW = "review"
    DEBUG = "debug"
    REFACTOR = "refactor"


class PersonaType(str, Enum):
    """AI persona types"""
    ARCHITECT = "architect"
    FRONTEND = "frontend"
    BACKEND = "backend"
    SECURITY = "security"
    ANALYST = "analyst"
    SCRIBE = "scribe"
    DEVOPS = "devops"
    TESTER = "tester"


@dataclass
class TokenUsage:
    """Track token usage and costs"""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cache_hit_tokens: int = 0
    cache_miss_tokens: int = 0
    reasoning_tokens: int = 0
    estimated_cost: float = 0.0

    def add(self, other: "TokenUsage") -> None:
        """Add another TokenUsage to this one"""
        self.prompt_tokens += other.prompt_tokens
        self.completion_tokens += other.completion_tokens
        self.total_tokens += other.total_tokens
        self.cache_hit_tokens += other.cache_hit_tokens
        self.cache_miss_tokens += other.cache_miss_tokens
        self.reasoning_tokens += other.reasoning_tokens
        self.estimated_cost += other.estimated_cost


@dataclass
class Message:
    """Chat message"""
    role: str
    content: str
    name: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class FunctionCall:
    """Function call representation"""
    name: str
    arguments: Dict[str, Any]
    id: Optional[str] = None


@dataclass
class TaskProfile:
    """Predefined task profile with optimal settings"""
    name: str
    temperature: float
    model: DeepSeekModel
    description: str
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None


# Predefined task profiles
TASK_PROFILES = {
    "coding": TaskProfile(
        name="coding",
        temperature=0.0,
        model=DeepSeekModel.CHAT,
        description="Code generation and debugging",
        max_tokens=4096
    ),
    "math": TaskProfile(
        name="math",
        temperature=0.0,
        model=DeepSeekModel.REASONER,
        description="Mathematical problem solving",
        max_tokens=8192
    ),
    "conversation": TaskProfile(
        name="conversation",
        temperature=1.3,
        model=DeepSeekModel.CHAT,
        description="General conversation",
        max_tokens=2048
    ),
    "creative": TaskProfile(
        name="creative",
        temperature=1.5,
        model=DeepSeekModel.CHAT,
        description="Creative writing and brainstorming",
        max_tokens=4096
    ),
    "analysis": TaskProfile(
        name="analysis",
        temperature=0.7,
        model=DeepSeekModel.REASONER,
        description="Data analysis and reasoning",
        max_tokens=8192
    ),
    "translation": TaskProfile(
        name="translation",
        temperature=1.3,
        model=DeepSeekModel.CHAT,
        description="Language translation",
        max_tokens=2048
    ),
}


class Persona(BaseModel):
    """AI Persona configuration"""
    type: PersonaType
    name: str
    expertise: List[str]
    prompt_prefix: str
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    style: Optional[str] = None


# Predefined personas
PERSONAS = {
    PersonaType.ARCHITECT: Persona(
        type=PersonaType.ARCHITECT,
        name="System Architect",
        expertise=["system design", "architecture patterns", "scalability"],
        prompt_prefix="As an experienced system architect with expertise in distributed systems and design patterns, ",
        temperature=0.7,
        style="technical and precise"
    ),
    PersonaType.SECURITY: Persona(
        type=PersonaType.SECURITY,
        name="Security Expert",
        expertise=["security", "vulnerabilities", "best practices"],
        prompt_prefix="As a cybersecurity expert specializing in application security and secure coding practices, ",
        temperature=0.3,
        style="cautious and thorough"
    ),
    PersonaType.FRONTEND: Persona(
        type=PersonaType.FRONTEND,
        name="Frontend Developer",
        expertise=["UI/UX", "React", "TypeScript", "accessibility"],
        prompt_prefix="As a senior frontend developer with expertise in modern web technologies and user experience, ",
        temperature=0.8,
        style="user-focused and creative"
    ),
    PersonaType.BACKEND: Persona(
        type=PersonaType.BACKEND,
        name="Backend Engineer",
        expertise=["APIs", "databases", "microservices", "performance"],
        prompt_prefix="As a backend engineer specializing in scalable APIs and data systems, ",
        temperature=0.5,
        style="efficient and systematic"
    ),
    PersonaType.ANALYST: Persona(
        type=PersonaType.ANALYST,
        name="Code Analyst",
        expertise=["debugging", "performance analysis", "code review"],
        prompt_prefix="As a code analyst with deep expertise in debugging and optimization, ",
        temperature=0.4,
        style="analytical and detail-oriented"
    ),
    PersonaType.DEVOPS: Persona(
        type=PersonaType.DEVOPS,
        name="DevOps Engineer",
        expertise=["CI/CD", "infrastructure", "automation", "monitoring"],
        prompt_prefix="As a DevOps engineer with expertise in automation and cloud infrastructure, ",
        temperature=0.6,
        style="practical and automation-focused"
    ),
}


@dataclass
class CommandContext:
    """Context for command execution"""
    command_type: CommandType
    args: List[str]
    cwd: str
    project_type: Optional[str] = None
    files: List[str] = field(default_factory=list)
    persona: Optional[Persona] = None
    memory_namespace: str = "default"
    session_id: Optional[str] = None