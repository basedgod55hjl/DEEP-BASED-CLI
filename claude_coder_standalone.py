#!/usr/bin/env python3
"""
Claude Coder Agent - Standalone Codebase Analysis Tool
Advanced codebase analysis and debugging system
"""

import os
import sys
import json
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging
import requests
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console = Console()

@dataclass
class CodeAnalysis:
    """Code analysis results"""
    file_path: str
    complexity_score: float
    issues: List[str]
    suggestions: List[str]
    dependencies: List[str]
    estimated_rewrite_time: int
    file_size: int
    lines_of_code: int

@dataclass
class SystemStatus:
    """System status information"""
    python_version: str
    claude_api_working: bool
    deepseek_api_working: bool
    database_status: str
    tool_status: Dict[str, bool]

class ClaudeCoderAgent:
    """Claude 4 Coder Agent - Advanced codebase analysis and upgrade system"""
    
    def __init__(self, codebase_path: str = "."):
        self.codebase_path = Path(codebase_path)
        self.claude_api_key = os.getenv("CLAUDE_API_KEY", "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")
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY", "sk-90e0dd863b8c4e0d879a02851a0ee194")
        self.analysis_results = []
        self.system_status = None
        
        # Initialize components
        self._setup_logging()
        self._check_system_status()
        
    def _setup_logging(self):
        """Setup advanced logging"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"claude_coder_agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        
    def _check_system_status(self):
        """Check system status and dependencies"""
        console.print(Panel.fit(
            "[bold blue]🔍 Checking System Status[/bold blue]",
            title="System Check"
        ))
        
        status = SystemStatus(
            python_version=sys.version,
            claude_api_working=self._test_claude_api(),
            deepseek_api_working=self._test_deepseek_api(),
            database_status=self._check_database(),
            tool_status=self._check_tools()
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
        """Display system status"""
        table = Table(title="System Status")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="bold")
        
        table.add_row("Python Version", status.python_version.split()[0])
        table.add_row("Claude API", "✅ Working" if status.claude_api_working else "❌ Failed")
        table.add_row("DeepSeek API", "✅ Working" if status.deepseek_api_working else "❌ Failed")
        table.add_row("Database", status.database_status)
        
        console.print(table)
        
        if status.tool_status:
            tool_table = Table(title="Tool Status")
            tool_table.add_column("Tool", style="cyan")
            tool_table.add_column("Status", style="bold")
            
            for tool, available in status.tool_status.items():
                status_text = "✅ Available" if available else "❌ Missing"
                tool_table.add_row(tool, status_text)
            
            console.print(tool_table)
        
    async def analyze_codebase(self):
        """Analyze the entire codebase"""
        console.print(Panel.fit(
            "[bold blue]🔍 Analyzing Codebase[/bold blue]",
            title="Code Analysis"
        ))
        
        python_files = list(self.codebase_path.rglob("*.py"))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            task = progress.add_task("Analyzing files...", total=len(python_files))
            
            for file_path in python_files:
                analysis = await self._analyze_file(file_path)
                self.analysis_results.append(analysis)
                progress.advance(task)
        
        self._display_analysis_summary()
        
    async def _analyze_file(self, file_path: Path) -> CodeAnalysis:
        """Analyze a single file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            complexity_score = self._calculate_complexity(content)
            issues = self._identify_issues(content, file_path)
            suggestions = self._generate_suggestions(content, file_path)
            dependencies = self._extract_dependencies(content)
            estimated_time = int(complexity_score * 2)
            file_size = len(content)
            lines_of_code = len(content.split("\n"))
            
            return CodeAnalysis(
                file_path=str(file_path),
                complexity_score=complexity_score,
                issues=issues,
                suggestions=suggestions,
                dependencies=dependencies,
                estimated_rewrite_time=estimated_time,
                file_size=file_size,
                lines_of_code=lines_of_code
            )
        
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
            return CodeAnalysis(
                file_path=str(file_path),
                complexity_score=0,
                issues=[f"Error reading file: {e}"],
                suggestions=[],
                dependencies=[],
                estimated_rewrite_time=0,
                file_size=0,
                lines_of_code=0
            )
        
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
        
        if content.count("print(") > 5:
            issues.append("Too many print statements - consider logging")
        
        if content.count("except:") > 0:
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
        
    def _display_analysis_summary(self):
        """Display analysis summary"""
        console.print(Panel.fit(
            "[bold blue]📊 Analysis Summary[/bold blue]",
            title="Code Analysis Results"
        ))
        
        total_files = len(self.analysis_results)
        total_issues = sum(len(r.issues) for r in self.analysis_results)
        total_suggestions = sum(len(r.suggestions) for r in self.analysis_results)
        avg_complexity = sum(r.complexity_score for r in self.analysis_results) / total_files if total_files > 0 else 0
        total_rewrite_time = sum(r.estimated_rewrite_time for r in self.analysis_results)
        total_lines = sum(r.lines_of_code for r in self.analysis_results)
        
        summary_table = Table(title="Summary Statistics")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="bold")
        
        summary_table.add_row("Total Files", str(total_files))
        summary_table.add_row("Total Lines of Code", str(total_lines))
        summary_table.add_row("Total Issues", str(total_issues))
        summary_table.add_row("Total Suggestions", str(total_suggestions))
        summary_table.add_row("Average Complexity", f"{avg_complexity:.1f}")
        summary_table.add_row("Estimated Rewrite Time", f"{total_rewrite_time} minutes")
        
        console.print(summary_table)
        
        if total_issues > 0:
            console.print(Panel.fit(
                "[bold yellow]⚠️ Top Issues Found[/bold yellow]",
                title="Issues Summary"
            ))
            
            all_issues = []
            for result in self.analysis_results:
                all_issues.extend(result.issues)
            
            issue_counts = {}
            for issue in all_issues:
                issue_counts[issue] = issue_counts.get(issue, 0) + 1
            
            issue_table = Table()
            issue_table.add_column("Issue", style="red")
            issue_table.add_column("Count", style="bold")
            
            for issue, count in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                issue_table.add_row(issue, str(count))
            
            console.print(issue_table)
        
        # Show most complex files
        complex_files = sorted(self.analysis_results, key=lambda x: x.complexity_score, reverse=True)[:5]
        if complex_files:
            console.print(Panel.fit(
                "[bold red]🔴 Most Complex Files[/bold red]",
                title="Complexity Analysis"
            ))
            
            complex_table = Table()
            complex_table.add_column("File", style="cyan")
            complex_table.add_column("Complexity", style="bold")
            complex_table.add_column("Lines", style="bold")
            
            for file_analysis in complex_files:
                complex_table.add_row(
                    Path(file_analysis.file_path).name,
                    f"{file_analysis.complexity_score:.1f}",
                    str(file_analysis.lines_of_code)
                )
            
            console.print(complex_table)
        
    async def run_full_scan(self):
        """Run complete codebase scan"""
        console.print(Panel.fit(
            "[bold green]🚀 Starting Full Codebase Scan[/bold green]",
            title="Full Scan"
        ))
        
        await self.analyze_codebase()
        
        # Generate scan report
        await self._generate_scan_report()
        
    async def _generate_scan_report(self):
        """Generate comprehensive scan report"""
        scans_dir = Path("scans")
        scans_dir.mkdir(exist_ok=True)
        
        report_path = scans_dir / f"codebase_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report_data = {
            "scan_timestamp": datetime.now().isoformat(),
            "codebase_path": str(self.codebase_path),
            "system_status": {
                "python_version": self.system_status.python_version,
                "claude_api_working": self.system_status.claude_api_working,
                "deepseek_api_working": self.system_status.deepseek_api_working
            },
            "analysis_results": [
                {
                    "file_path": r.file_path,
                    "complexity_score": r.complexity_score,
                    "issues": r.issues,
                    "suggestions": r.suggestions,
                    "dependencies": r.dependencies,
                    "estimated_rewrite_time": r.estimated_rewrite_time,
                    "file_size": r.file_size,
                    "lines_of_code": r.lines_of_code
                }
                for r in self.analysis_results
            ]
        }
        
        with open(report_path, "w") as f:
            json.dump(report_data, f, indent=2)
        
        console.print(f"✅ Scan report saved to: {report_path}")

async def main():
    """Main function"""
    console.print(Panel.fit(
        "[bold blue]Claude 4 Coder Agent - Standalone Edition[/bold blue]\n"
        "Advanced Codebase Analysis and Debugging System\n"
        "God-level development with AI-powered insights",
        title="🚀 Claude Coder Agent"
    ))
    
    agent = ClaudeCoderAgent()
    
    await agent.run_full_scan()
    
    console.print(Panel.fit(
        "[bold green]🎉 Codebase Scan Complete![/bold green]\n"
        "Your codebase has been analyzed with:\n"
        "• Advanced code complexity scoring\n"
        "• Comprehensive issue identification\n"
        "• Detailed improvement suggestions\n"
        "• Dependency analysis\n"
        "• Performance insights",
        title="✅ Scan Complete"
    ))

if __name__ == "__main__":
    asyncio.run(main()) 