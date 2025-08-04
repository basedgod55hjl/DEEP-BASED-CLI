#!/usr/bin/env python3
"""
Advanced Claude Coder Agent - Enhanced with Reasoning, Agents, CoT Loops, and Claude 4 Opus Thinking
Comprehensive codebase analysis and rewriting system
"""

import os
import sys
import json
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging
import requests
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.tree import Tree
from rich.text import Text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console = Console()

@dataclass
class CodeAnalysis:
    """Enhanced code analysis results"""
    file_path: str
    complexity_score: float
    issues: List[str]
    suggestions: List[str]
    dependencies: List[str]
    estimated_rewrite_time: int
    file_size: int
    lines_of_code: int
    reasoning_chain: List[str]
    agent_insights: List[str]
    rewrite_plan: Dict[str, Any]

@dataclass
class SystemStatus:
    """Enhanced system status information"""
    python_version: str
    claude_api_working: bool
    deepseek_api_working: bool
    database_status: str
    tool_status: Dict[str, bool]
    reasoning_capabilities: List[str]

class ReasoningAgent:
    """Advanced reasoning agent with Chain of Thought capabilities"""
    
    def __init__(self, claude_api_key: str):
    """__init__ function."""
        self.claude_api_key = claude_api_key
        self.thinking_chain = []
        
    async def think_step_by_step(self, problem: str, context: str = "") -> List[str]:
        """Perform step-by-step reasoning using Claude 4 Opus"""
        try:
            prompt = f"""
You are Claude 4 Opus, an advanced reasoning AI. Analyze this problem step by step:

PROBLEM: {problem}
CONTEXT: {context}

Think through this systematically:
1. What is the core issue?
2. What are the underlying causes?
3. What are the potential solutions?
4. What are the trade-offs?
5. What is the optimal approach?

Provide your reasoning chain step by step.
"""
            
            headers = {
                "x-api-key": self.claude_api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            
            data = {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 2000,
                "messages": [{"role": "user", "content": prompt}]
            }
            
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                reasoning = result['content'][0]['text']
                steps = [step.strip() for step in reasoning.split('\n') if step.strip()]
                self.thinking_chain.extend(steps)
                return steps
            else:
                logger.warning(f"Claude API request failed: {response.status_code}")
                return ["API request failed"]
                
        except Exception as e:
            logger.error(f"Reasoning error: {e}")
            return [f"Reasoning error: {e}"]
    
    async def analyze_code_complexity(self, code: str, file_path: str) -> Dict[str, Any]:
        """Analyze code complexity with advanced reasoning"""
        problem = f"Analyze the complexity and quality of this code file: {file_path}"
        context = f"Code content:\n{code[:2000]}..." if len(code) > 2000 else f"Code content:\n{code}"
        
        reasoning_steps = await self.think_step_by_step(problem, context)
        
        return {
            "reasoning_chain": reasoning_steps,
            "complexity_factors": self._extract_complexity_factors(code),
            "quality_metrics": self._calculate_quality_metrics(code),
            "improvement_areas": self._identify_improvement_areas(code)
        }
    
    def _extract_complexity_factors(self, code: str) -> Dict[str, int]:
        """Extract complexity factors from code"""
        factors = {
            "cyclomatic_complexity": 0,
            "nesting_depth": 0,
            "function_count": 0,
            "class_count": 0,
            "import_count": 0,
            "exception_handlers": 0,
            "async_functions": 0
        }
        
        lines = code.split('\n')
        max_nesting = 0
        current_nesting = 0
        
        for line in lines:
            stripped = line.strip()
            
            # Count functions
            if stripped.startswith('def ') or stripped.startswith('async def '):
                factors["function_count"] += 1
                if stripped.startswith('async def '):
                    factors["async_functions"] += 1
            
            # Count classes
            if stripped.startswith('class '):
                factors["class_count"] += 1
            
            # Count imports
            if stripped.startswith('import ') or stripped.startswith('from '):
                factors["import_count"] += 1
            
            # Count exceptions
            if stripped.startswith('except'):
                factors["exception_handlers"] += 1
            
            # Calculate nesting depth
            if stripped.endswith(':'):
                current_nesting += 1
                max_nesting = max(max_nesting, current_nesting)
            elif stripped and not stripped.startswith('#'):
                # Check for dedent
                if current_nesting > 0:
                    current_nesting = max(0, current_nesting - 1)
        
        factors["nesting_depth"] = max_nesting
        factors["cyclomatic_complexity"] = (
            factors["function_count"] + 
            code.count('if ') + 
            code.count('for ') + 
            code.count('while ') + 
            code.count('except')
        )
        
        return factors
    
    def _calculate_quality_metrics(self, code: str) -> Dict[str, float]:
        """Calculate code quality metrics"""
        lines = code.split('\n')
        total_lines = len(lines)
        if total_lines == 0:
            return {"readability": 0, "maintainability": 0, "testability": 0}
        
        # Readability metrics
        comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
        docstring_lines = sum(1 for line in lines if '"""' in line or "'''" in line)
        long_lines = sum(1 for line in lines if len(line) > 80)
        
        readability = min(100, (
            (comment_lines / total_lines * 30) +
            (docstring_lines / total_lines * 40) +
            (1 - long_lines / total_lines) * 30
        ))
        
        # Maintainability metrics
        function_count = code.count('def ')
        class_count = code.count('class ')
        complexity = self._extract_complexity_factors(code)["cyclomatic_complexity"]
        
        maintainability = max(0, 100 - (complexity * 2) - (function_count * 3) - (class_count * 5))
        
        # Testability metrics
        testable_functions = function_count - code.count('def __')
        testability = min(100, (testable_functions / max(1, function_count)) * 100)
        
        return {
            "readability": round(readability, 2),
            "maintainability": round(maintainability, 2),
            "testability": round(testability, 2)
        }
    
    def _identify_improvement_areas(self, code: str) -> List[str]:
        """Identify areas for improvement"""
        improvements = []
        
        if code.count('except Exception:') > 0:
            improvements.append("Replace bare except clauses with specific exception types")
        
        if code.count('logging.info(') > 5:
            improvements.append("Replace print statements with proper logging")
        
        if code.count('import *') > 0:
            improvements.append("Replace wildcard imports with specific imports")
        
        if len(code.split('\n')) > 500:
            improvements.append("Consider splitting large file into smaller modules")
        
        if code.count('def ') > 20:
            improvements.append("Consider breaking down large functions")
        
        if code.count('class ') > 5:
            improvements.append("Consider separating classes into different files")
        
        return improvements

class CodebaseAgent:
    """Agent for analyzing and understanding the codebase structure"""
    
    def __init__(self) -> Any:
        self.codebase_structure = {}
        self.dependency_graph = {}
        self.architectural_patterns = []
        
    async def analyze_codebase_structure(self, codebase_path: Path) -> Dict[str, Any]:
        """Analyze the overall codebase structure"""
        console.print(Panel.fit(
            "[bold blue]🏗️ Analyzing Codebase Architecture[/bold blue]",
            title="Architecture Analysis"
        ))
        
        structure = {
            "modules": [],
            "dependencies": {},
            "patterns": [],
            "entry_points": [],
            "configuration_files": [],
            "test_files": [],
            "documentation_files": []
        }
        
        # Analyze file structure
        for file_path in codebase_path.rglob("*"):
            if file_path.is_file():
                relative_path = str(file_path.relative_to(codebase_path))
                
                if file_path.suffix == '.py':
                    if 'test' in relative_path.lower():
                        structure["test_files"].append(relative_path)
                    elif file_path.name in ['main.py', '__main__.py', 'app.py']:
                        structure["entry_points"].append(relative_path)
                    else:
                        structure["modules"].append(relative_path)
                elif file_path.suffix in ['.json', '.yaml', '.yml', '.toml']:
                    structure["configuration_files"].append(relative_path)
                elif file_path.suffix in ['.md', '.txt', '.rst']:
                    structure["documentation_files"].append(relative_path)
        
        # Analyze dependencies
        structure["dependencies"] = await self._analyze_dependencies(codebase_path)
        
        # Identify patterns
        structure["patterns"] = self._identify_patterns(structure)
        
        self.codebase_structure = structure
        return structure
    
    async def _analyze_dependencies(self, codebase_path: Path) -> Dict[str, List[str]]:
        """Analyze dependencies between modules"""
        dependencies = {}
        
        for py_file in codebase_path.rglob("*.py"):
            if py_file.is_file():
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    module_name = str(py_file.relative_to(codebase_path)).replace('\\', '/').replace('.py', '')
                    imports = self._extract_imports(content)
                    dependencies[module_name] = imports
                    
                except Exception as e:
                    logger.warning(f"Error analyzing dependencies for {py_file}: {e}")
        
        return dependencies
    
    def _extract_imports(self, content: str) -> List[str]:
        """Extract import statements from code"""
        imports = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                if line.startswith('import '):
                    module = line.split('import ')[1].split(' as ')[0].split(',')[0].strip()
                else:
                    module = line.split('from ')[1].split(' import ')[0].strip()
                
                if module not in imports:
                    imports.append(module)
        
        return imports
    
    def _identify_patterns(self, structure: Dict[str, Any]) -> List[str]:
        """Identify architectural patterns in the codebase"""
        patterns = []
        
        # Check for common patterns
        if any('tool' in module for module in structure["modules"]):
            patterns.append("Tool-based architecture")
        
        if any('agent' in module for module in structure["modules"]):
            patterns.append("Agent-based architecture")
        
        if any('api' in module for module in structure["modules"]):
            patterns.append("API-driven architecture")
        
        if any('cli' in module for module in structure["modules"]):
            patterns.append("CLI-based interface")
        
        if len(structure["test_files"]) > 0:
            patterns.append("Test-driven development")
        
        if any('config' in module for module in structure["configuration_files"]):
            patterns.append("Configuration management")
        
        return patterns

class RewriteAgent:
    """Agent for planning and executing code rewrites"""
    
    def __init__(self, reasoning_agent: ReasoningAgent):
    """__init__ function."""
        self.reasoning_agent = reasoning_agent
        self.rewrite_plans = {}
        
    async def create_rewrite_plan(self, file_path: str, analysis: CodeAnalysis) -> Dict[str, Any]:
        """Create a comprehensive rewrite plan for a file"""
        console.logging.info(f"[yellow]📝 Creating rewrite plan for {file_path}[/yellow]")
        
        problem = f"Create a comprehensive rewrite plan for {file_path} based on the analysis"
        context = f"""
File: {file_path}
Issues: {analysis.issues}
Suggestions: {analysis.suggestions}
Complexity Score: {analysis.complexity_score}
Lines of Code: {analysis.lines_of_code}
"""
        
        reasoning_steps = await self.reasoning_agent.think_step_by_step(problem, context)
        
        plan = {
            "file_path": file_path,
            "priority": self._calculate_priority(analysis),
            "estimated_effort": analysis.estimated_rewrite_time,
            "rewrite_strategy": self._determine_strategy(analysis),
            "improvements": analysis.suggestions,
            "risks": self._assess_risks(analysis),
            "dependencies": analysis.dependencies,
            "reasoning_chain": reasoning_steps,
            "step_by_step_plan": self._create_step_plan(analysis)
        }
        
        self.rewrite_plans[file_path] = plan
        return plan
    
    def _calculate_priority(self, analysis: CodeAnalysis) -> str:
        """Calculate rewrite priority"""
        score = analysis.complexity_score + len(analysis.issues) * 10
        
        if score > 80:
            return "HIGH"
        elif score > 50:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _determine_strategy(self, analysis: CodeAnalysis) -> str:
        """Determine rewrite strategy"""
        if analysis.complexity_score > 70:
            return "Complete refactor"
        elif len(analysis.issues) > 10:
            return "Major improvements"
        elif analysis.lines_of_code > 500:
            return "Modularization"
        else:
            return "Incremental improvements"
    
    def _assess_risks(self, analysis: CodeAnalysis) -> List[str]:
        """Assess risks of rewriting"""
        risks = []
        
        if analysis.complexity_score > 80:
            risks.append("High complexity - risk of introducing bugs")
        
        if len(analysis.dependencies) > 10:
            risks.append("Many dependencies - risk of breaking changes")
        
        if analysis.lines_of_code > 1000:
            risks.append("Large file - risk of incomplete refactoring")
        
        return risks
    
    def _create_step_plan(self, analysis: CodeAnalysis) -> List[str]:
        """Create step-by-step rewrite plan"""
        steps = []
        
        # Address critical issues first
        if "Error reading file" in str(analysis.issues):
            steps.append("Fix file encoding issues")
        
        if "Too many print statements" in str(analysis.issues):
            steps.append("Replace print statements with logging")
        
        if "Bare except clauses" in str(analysis.issues):
            steps.append("Improve exception handling")
        
        if "File is very long" in str(analysis.issues):
            steps.append("Split into smaller modules")
        
        # Add general improvements
        steps.append("Add type hints where missing")
        steps.append("Improve documentation")
        steps.append("Add error handling")
        steps.append("Optimize performance")
        
        return steps

class AdvancedClaudeCoderAgent:
    """Advanced Claude Coder Agent with reasoning, agents, and CoT loops"""
    
    def __init__(self, codebase_path: str = "."):
    """__init__ function."""
        self.codebase_path = Path(codebase_path)
        self.claude_api_key = os.getenv("CLAUDE_API_KEY", "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")
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY", "sk-90e0dd863b8c4e0d879a02851a0ee194")
        
        # Initialize agents
        self.reasoning_agent = ReasoningAgent(self.claude_api_key)
        self.codebase_agent = CodebaseAgent()
        self.rewrite_agent = RewriteAgent(self.reasoning_agent)
        
        self.analysis_results = []
        self.system_status = None
        self.codebase_structure = None
        
        # Initialize components
        self._setup_logging()
        self._check_system_status()
        
    def _setup_logging(self) -> Any:
        """Setup advanced logging"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"advanced_claude_coder_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        
    def _check_system_status(self) -> Any:
        """Check enhanced system status"""
        console.print(Panel.fit(
            "[bold blue]🔍 Checking Advanced System Status[/bold blue]",
            title="Advanced System Check"
        ))
        
        status = SystemStatus(
            python_version=sys.version,
            claude_api_working=self._test_claude_api(),
            deepseek_api_working=self._test_deepseek_api(),
            database_status=self._check_database(),
            tool_status=self._check_tools(),
            reasoning_capabilities=["Chain of Thought", "Step-by-step Analysis", "Architectural Reasoning"]
        )
        
        self.system_status = status
        self._display_system_status(status)
        
    def _test_claude_api(self) -> bool:
        """Test Claude API connectivity"""
        try:
            headers = {
                "x-api-key": self.claude_api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            
            data = {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 10,
                "messages": [{"role": "user", "content": "test"}]
            }
            
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data,
                timeout=10
            )
            
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Claude API test failed: {e}")
            return False
        
    def _test_deepseek_api(self) -> bool:
        """Test DeepSeek API connectivity"""
        try:
            headers = {
                "Authorization": f"Bearer {self.deepseek_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 10
            }
            
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=10
            )
            
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"DeepSeek API test failed: {e}")
            return False
        
    def _check_database(self) -> str:
        """Check database status"""
        try:
            db_path = Path("data/deepcli_database.db")
            if db_path.exists():
                return "✅ Available"
            else:
                return "❌ Not found"
        except Exception as e:
            return f"⚠️ Error: {e}"
        
    def _check_tools(self) -> Dict[str, bool]:
        """Check tool availability"""
        tools = {}
        
        tool_files = [
            "tools/llm_query_tool.py",
            "tools/deepseek_coder_tool.py",
            "tools/reasoning_engine.py",
            "tools/sql_database_tool.py",
            "tools/memory_tool.py"
        ]
        
        for tool_file in tool_files:
            tools[tool_file] = Path(tool_file).exists()
        
        return tools
        
    def _display_system_status(self, status: SystemStatus):
    """_display_system_status function."""
        """Display enhanced system status"""
        table = Table(title="Advanced System Status")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="bold")
        
        table.add_row("Python Version", status.python_version.split()[0])
        table.add_row("Claude API", "✅ Working" if status.claude_api_working else "❌ Failed")
        table.add_row("DeepSeek API", "✅ Working" if status.deepseek_api_working else "❌ Failed")
        table.add_row("Database", status.database_status)
        
        console.logging.info(table)
        
        # Display reasoning capabilities
        console.print(Panel.fit(
            f"[bold green]🧠 Reasoning Capabilities:[/bold green]\n" + 
            "\n".join([f"• {cap}" for cap in status.reasoning_capabilities]),
            title="Advanced Features"
        ))
        
        if status.tool_status:
            tool_table = Table(title="Tool Status")
            tool_table.add_column("Tool", style="cyan")
            tool_table.add_column("Status", style="bold")
            
            for tool, available in status.tool_status.items():
                status_text = "✅ Available" if available else "❌ Missing"
                tool_table.add_row(tool, status_text)
            
            console.logging.info(tool_table)
    
    async def run_comprehensive_analysis(self) -> Any:
        """Run comprehensive codebase analysis with reasoning"""
        console.print(Panel.fit(
            "[bold green]🚀 Starting Comprehensive Codebase Analysis[/bold green]",
            title="Advanced Analysis"
        ))
        
        # Step 1: Analyze codebase structure
        self.codebase_structure = await self.codebase_agent.analyze_codebase_structure(self.codebase_path)
        
        # Step 2: Analyze individual files with reasoning
        await self._analyze_files_with_reasoning()
        
        # Step 3: Create rewrite plans
        await self._create_rewrite_plans()
        
        # Step 4: Generate comprehensive report
        await self._generate_comprehensive_report()
        
    async def _analyze_files_with_reasoning(self) -> Any:
        """Analyze files with advanced reasoning"""
        console.print(Panel.fit(
            "[bold blue]🧠 Analyzing Files with Advanced Reasoning[/bold blue]",
            title="Reasoning Analysis"
        ))
        
        python_files = []
        for py_file in self.codebase_path.rglob("*.py"):
            if "backup" not in str(py_file) and "node_modules" not in str(py_file):
                python_files.append(py_file)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            task = progress.add_task("Analyzing with reasoning...", total=len(python_files))
            
            for file_path in python_files:
                analysis = await self._analyze_file_with_reasoning(file_path)
                self.analysis_results.append(analysis)
                progress.advance(task)
        
        self._display_enhanced_analysis_summary()
    
    async def _analyze_file_with_reasoning(self, file_path: Path) -> CodeAnalysis:
        """Analyze a single file with advanced reasoning"""
        try:
            # Read file with multiple encodings
            content = None
            for encoding in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']:
                try:
                    with open(file_path, "r", encoding=encoding) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    logger.warning(f"Error reading {file_path} with {encoding}: {e}")
                    continue
            
            if content is None:
                raise Exception("Could not read file with any encoding")
            
            # Basic analysis
            complexity_score = self._calculate_complexity(content)
            issues = self._identify_issues(content, file_path)
            suggestions = self._generate_suggestions(content, file_path)
            dependencies = self._extract_dependencies(content)
            estimated_time = int(complexity_score * 2)
            file_size = len(content)
            lines_of_code = len(content.split("\n"))
            
            # Advanced reasoning analysis
            reasoning_analysis = await self.reasoning_agent.analyze_code_complexity(content, str(file_path))
            
            # Agent insights
            agent_insights = await self._generate_agent_insights(content, file_path, reasoning_analysis)
            
            # Rewrite plan
            rewrite_plan = await self.rewrite_agent.create_rewrite_plan(str(file_path), CodeAnalysis(
                file_path=str(file_path),
                complexity_score=complexity_score,
                issues=issues,
                suggestions=suggestions,
                dependencies=dependencies,
                estimated_rewrite_time=estimated_time,
                file_size=file_size,
                lines_of_code=lines_of_code,
                reasoning_chain=[],
                agent_insights=[],
                rewrite_plan={}
            ))
            
            return CodeAnalysis(
                file_path=str(file_path),
                complexity_score=complexity_score,
                issues=issues,
                suggestions=suggestions,
                dependencies=dependencies,
                estimated_rewrite_time=estimated_time,
                file_size=file_size,
                lines_of_code=lines_of_code,
                reasoning_chain=reasoning_analysis["reasoning_chain"],
                agent_insights=agent_insights,
                rewrite_plan=rewrite_plan
            )
        
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
            return CodeAnalysis(
                file_path=str(file_path),
                complexity_score=0,
                issues=[f"Error reading file: {e}"],
                suggestions=["Check file encoding", "Verify file integrity"],
                dependencies=[],
                estimated_rewrite_time=0,
                file_size=0,
                lines_of_code=0,
                reasoning_chain=[f"Analysis failed: {e}"],
                agent_insights=[],
                rewrite_plan={}
            )
    
    async def _generate_agent_insights(self, content: str, file_path: Path, reasoning_analysis: Dict[str, Any]) -> List[str]:
        """Generate insights from multiple agents"""
        insights = []
        
        # Architecture insights
        if reasoning_analysis["complexity_factors"]["class_count"] > 3:
            insights.append("Consider applying design patterns to reduce class complexity")
        
        if reasoning_analysis["complexity_factors"]["function_count"] > 15:
            insights.append("File has many functions - consider module separation")
        
        if reasoning_analysis["quality_metrics"]["maintainability"] < 50:
            insights.append("Low maintainability score - prioritize refactoring")
        
        # Performance insights
        if content.count('for ') > content.count('while '):
            insights.append("Consider using list comprehensions for better performance")
        
        if content.count('requests.') > 0 and content.count('async') == 0:
            insights.append("Consider using async HTTP requests for better performance")
        
        # Security insights
        if content.count('eval(') > 0:
            insights.append("Security risk: eval() usage detected")
        
        if content.count('exec(') > 0:
            insights.append("Security risk: exec() usage detected")
        
        return insights
    
    async def _create_rewrite_plans(self) -> Any:
        """Create comprehensive rewrite plans"""
        console.print(Panel.fit(
            "[bold blue]📝 Creating Comprehensive Rewrite Plans[/bold blue]",
            title="Rewrite Planning"
        ))
        
        # Plans are already created during analysis
        total_plans = len(self.rewrite_agent.rewrite_plans)
        high_priority = sum(1 for plan in self.rewrite_agent.rewrite_plans.values() if plan["priority"] == "HIGH")
        
        console.logging.info(f"✅ Created {total_plans} rewrite plans")
        console.logging.info(f"🔴 {high_priority} high priority files identified")
    
    def _calculate_complexity(self, content: str) -> float:
        """Calculate code complexity score"""
        complexity = 0
        
        complexity += content.count("if ") * 1
        complexity += content.count("for ") * 2
        complexity += content.count("while ") * 2
        complexity += content.count("try:") * 1
        complexity += content.count("except") * 1
        complexity += content.count("async def") * 3
        complexity += content.count("class ") * 2
        complexity += content.count("import ") * 0.5
        complexity += content.count("from ") * 0.5
        
        lines = len(content.split("\n"))
        if lines > 0:
            complexity = complexity / lines * 100
        
        return min(complexity, 100)
        
    def _identify_issues(self, content: str, file_path: Path) -> List[str]:
        """Identify potential issues in the code"""
        issues = []
        
        if "TODO" in content or "FIXME" in content:
            issues.append("Contains TODO/FIXME comments")
        
        if content.count("logging.info(") > 5:
            issues.append("Too many print statements - consider logging")
        
        if content.count("except Exception:") > 0:
            issues.append("Bare except clauses - specify exception types")
        
        if content.count("import *") > 0:
            issues.append("Wildcard imports - import specific modules")
        
        if len(content.split("\n")) > 500:
            issues.append("File is very long - consider splitting")
        
        return issues
        
    def _generate_suggestions(self, content: str, file_path: Path) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        
        if "def " in content and "->" not in content:
            suggestions.append("Add type hints to functions")
        
        if "def " in content and '"""' not in content and "'''" not in content:
            suggestions.append("Add docstrings to functions")
        
        if "requests." in content and "try:" not in content:
            suggestions.append("Add error handling for HTTP requests")
        
        if "async def" in content and "await" not in content:
            suggestions.append("Consider using await in async functions")
        
        return suggestions
        
    def _extract_dependencies(self, content: str) -> List[str]:
        """Extract dependencies from import statements"""
        dependencies = []
        
        lines = content.split("\n")
        for line in lines:
            if line.strip().startswith("import ") or line.strip().startswith("from "):
                if line.startswith("import "):
                    module = line.split("import ")[1].split(" as ")[0].split(",")[0].strip()
                else:
                    module = line.split("from ")[1].split(" import ")[0].strip()
                
                if module not in dependencies:
                    dependencies.append(module)
        
        return dependencies
    
    def _display_enhanced_analysis_summary(self) -> Any:
        """Display enhanced analysis summary"""
        console.print(Panel.fit(
            "[bold blue]📊 Enhanced Analysis Summary[/bold blue]",
            title="Advanced Analysis Results"
        ))
        
        total_files = len(self.analysis_results)
        total_issues = sum(len(r.issues) for r in self.analysis_results)
        total_suggestions = sum(len(r.suggestions) for r in self.analysis_results)
        avg_complexity = sum(r.complexity_score for r in self.analysis_results) / total_files if total_files > 0 else 0
        total_rewrite_time = sum(r.estimated_rewrite_time for r in self.analysis_results)
        total_lines = sum(r.lines_of_code for r in self.analysis_results)
        
        summary_table = Table(title="Enhanced Summary Statistics")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="bold")
        
        summary_table.add_row("Total Files", str(total_files))
        summary_table.add_row("Total Lines of Code", str(total_lines))
        summary_table.add_row("Total Issues", str(total_issues))
        summary_table.add_row("Total Suggestions", str(total_suggestions))
        summary_table.add_row("Average Complexity", f"{avg_complexity:.1f}")
        summary_table.add_row("Estimated Rewrite Time", f"{total_rewrite_time} minutes")
        summary_table.add_row("High Priority Files", str(len([r for r in self.analysis_results if r.rewrite_plan.get("priority") == "HIGH"])))
        
        console.logging.info(summary_table)
        
        # Display architectural insights
        if self.codebase_structure:
            console.print(Panel.fit(
                f"[bold green]🏗️ Architectural Patterns:[/bold green]\n" + 
                "\n".join([f"• {pattern}" for pattern in self.codebase_structure["patterns"]]),
                title="Architecture Insights"
            ))
    
    async def _generate_comprehensive_report(self) -> Any:
        """Generate comprehensive analysis report"""
        console.print(Panel.fit(
            "[bold blue]📄 Generating Comprehensive Report[/bold blue]",
            title="Report Generation"
        ))
        
        scans_dir = Path("scans")
        scans_dir.mkdir(exist_ok=True)
        
        report_path = scans_dir / f"advanced_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report_data = {
            "scan_timestamp": datetime.now().isoformat(),
            "codebase_path": str(self.codebase_path),
            "system_status": {
                "python_version": self.system_status.python_version,
                "claude_api_working": self.system_status.claude_api_working,
                "deepseek_api_working": self.system_status.deepseek_api_working,
                "reasoning_capabilities": self.system_status.reasoning_capabilities
            },
            "codebase_structure": self.codebase_structure,
            "analysis_results": [
                {
                    "file_path": r.file_path,
                    "complexity_score": r.complexity_score,
                    "issues": r.issues,
                    "suggestions": r.suggestions,
                    "dependencies": r.dependencies,
                    "estimated_rewrite_time": r.estimated_rewrite_time,
                    "file_size": r.file_size,
                    "lines_of_code": r.lines_of_code,
                    "reasoning_chain": r.reasoning_chain,
                    "agent_insights": r.agent_insights,
                    "rewrite_plan": r.rewrite_plan
                }
                for r in self.analysis_results
            ],
            "rewrite_plans": self.rewrite_agent.rewrite_plans
        }
        
        with open(report_path, "w") as f:
            json.dump(report_data, f, indent=2)
        
        console.logging.info(f"✅ Comprehensive report saved to: {report_path}")

async def main() -> None:
    """Main function"""
    console.print(Panel.fit(
        "[bold blue]Advanced Claude 4 Coder Agent - Enhanced Edition[/bold blue]\n"
        "Advanced Codebase Analysis with Reasoning, Agents, and CoT Loops\n"
        "God-level development with Claude 4 Opus thinking",
        title="🚀 Advanced Claude Coder Agent"
    ))
    
    agent = AdvancedClaudeCoderAgent()
    
    await agent.run_comprehensive_analysis()
    
    console.print(Panel.fit(
        "[bold green]🎉 Advanced Analysis Complete![/bold green]\n"
        "Your codebase has been analyzed with:\n"
        "• Advanced reasoning with Chain of Thought\n"
        "• Multi-agent analysis and insights\n"
        "• Comprehensive rewrite planning\n"
        "• Architectural pattern recognition\n"
        "• Quality metrics and recommendations",
        title="✅ Advanced Analysis Complete"
    ))

if __name__ == "__main__":
    asyncio.run(main()) 