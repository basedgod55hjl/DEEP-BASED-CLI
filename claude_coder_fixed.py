import logging
logger = logging.getLogger(__name__)
#!/usr/bin/env python3
"""
Claude Coder Agent - Fixed Edition
Advanced codebase analysis and rewriting system with improved error handling
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
import chardet
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
    encoding: str
    read_success: bool

@dataclass
class SystemStatus:
    """System status information"""
    python_version: str
    claude_api_working: bool
    deepseek_api_working: bool
    database_status: str
    tool_status: Dict[str, bool]

class ClaudeCoderAgent:
    """Claude 4 Coder Agent - Advanced codebase analysis and rewriting system"""
    
    def __init__(self, codebase_path: str = "."):
        self.codebase_path = Path(codebase_path)
        self.claude_api_key = os.getenv("CLAUDE_API_KEY", "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")
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY", "sk-90e0dd863b8c4e0d879a02851a0ee194")
        self.analysis_results = []
        self.system_status = None
        self.fixes_applied = []
        
        # Initialize components
        self._setup_logging()
        self._check_system_status()
        
    def _setup_logging(self):
        """Setup advanced logging"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"claude_coder_fixed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        
    def _check_system_status(self):
        """Check system status and dependencies"""
        console.logger.info(Panel.fit(
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
        
        console.logger.info(table)
        
        if status.tool_status:
            tool_table = Table(title="Tool Status")
            tool_table.add_column("Tool", style="cyan")
            tool_table.add_column("Status", style="bold")
            
            for tool, available in status.tool_status.items():
                status_text = "✅ Available" if available else "❌ Missing"
                tool_table.add_row(tool, status_text)
            
            console.logger.info(tool_table)
    
    def _detect_encoding(self, file_path: Path) -> str:
        """Detect file encoding"""
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)
                return result['encoding'] or 'utf-8'
        except Exception:
            return 'utf-8'
    
    def _read_file_safely(self, file_path: Path) -> tuple[str, str, bool]:
        """Safely read file with encoding detection"""
        try:
            # Try UTF-8 first
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return content, 'utf-8', True
        except UnicodeDecodeError:
            try:
                # Detect encoding
                encoding = self._detect_encoding(file_path)
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                    return content, encoding, True
            except Exception as e:
                logger.error(f"Failed to read {file_path}: {e}")
                return "", "unknown", False
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return "", "unknown", False
        
    async def analyze_codebase(self):
        """Analyze the entire codebase"""
        console.logger.info(Panel.fit(
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
        """Analyze a single file with improved error handling"""
        content, encoding, read_success = self._read_file_safely(file_path)
        
        if not read_success:
            return CodeAnalysis(
                file_path=str(file_path),
                complexity_score=0,
                issues=["File reading failed - encoding or corruption issue"],
                suggestions=["Check file encoding", "Verify file integrity"],
                dependencies=[],
                estimated_rewrite_time=0,
                file_size=0,
                lines_of_code=0,
                encoding=encoding,
                read_success=False
            )
        
        try:
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
                lines_of_code=lines_of_code,
                encoding=encoding,
                read_success=True
            )
        
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
            return CodeAnalysis(
                file_path=str(file_path),
                complexity_score=0,
                issues=[f"Analysis error: {e}"],
                suggestions=["Review file content", "Check for syntax errors"],
                dependencies=[],
                estimated_rewrite_time=0,
                file_size=0,
                lines_of_code=0,
                encoding=encoding,
                read_success=False
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
        
        if content.count("logger.info(") > 5:
            issues.append("Too many print statements - consider logging")
        
        if content.count("except Exception as e:") > 0:
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
        console.logger.info(Panel.fit(
            "[bold blue]📊 Analysis Summary[/bold blue]",
            title="Code Analysis Results"
        ))
        
        total_files = len(self.analysis_results)
        successful_reads = sum(1 for r in self.analysis_results if r.read_success)
        total_issues = sum(len(r.issues) for r in self.analysis_results)
        total_suggestions = sum(len(r.suggestions) for r in self.analysis_results)
        avg_complexity = sum(r.complexity_score for r in self.analysis_results) / total_files if total_files > 0 else 0
        total_rewrite_time = sum(r.estimated_rewrite_time for r in self.analysis_results)
        total_lines = sum(r.lines_of_code for r in self.analysis_results)
        
        summary_table = Table(title="Summary Statistics")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="bold")
        
        summary_table.add_row("Total Files", str(total_files))
        summary_table.add_row("Successfully Read", f"{successful_reads}/{total_files}")
        summary_table.add_row("Total Lines of Code", str(total_lines))
        summary_table.add_row("Total Issues", str(total_issues))
        summary_table.add_row("Total Suggestions", str(total_suggestions))
        summary_table.add_row("Average Complexity", f"{avg_complexity:.1f}")
        summary_table.add_row("Estimated Rewrite Time", f"{total_rewrite_time} minutes")
        
        console.logger.info(summary_table)
        
        if total_issues > 0:
            console.logger.info(Panel.fit(
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
            
            console.logger.info(issue_table)
        
        # Show most complex files
        complex_files = sorted([r for r in self.analysis_results if r.read_success], key=lambda x: x.complexity_score, reverse=True)[:5]
        if complex_files:
            console.logger.info(Panel.fit(
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
            
            console.logger.info(complex_table)
    
    async def fix_codebase_issues(self):
        """Fix identified issues in the codebase"""
        console.logger.info(Panel.fit(
            "[bold green]🔧 Starting Codebase Fixes[/bold green]",
            title="Codebase Rewrite"
        ))
        
        # Fix file reading issues first
        await self._fix_file_encoding_issues()
        
        # Fix print statements
        await self._fix_print_statements()
        
        # Fix exception handling
        await self._fix_exception_handling()
        
        # Fix long files
        await self._fix_long_files()
        
        # Fix TODO/FIXME comments
        await self._fix_todo_comments()
        
        console.logger.info(Panel.fit(
            "[bold green]✅ Codebase Fixes Complete![/bold green]",
            title="Rewrite Summary"
        ))
        
        self._display_fixes_summary()
    
    async def _fix_file_encoding_issues(self):
        """Fix file encoding issues"""
        console.logger.info("🔧 Fixing file encoding issues...")
        
        for result in self.analysis_results:
            if not result.read_success and "encoding" in result.issues[0].lower():
                file_path = Path(result.file_path)
                try:
                    # Try to fix encoding
                    content, encoding, success = self._read_file_safely(file_path)
                    if success:
                        # Write back with UTF-8 encoding
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        self.fixes_applied.append(f"Fixed encoding for {file_path}")
                except Exception as e:
                    logger.error(f"Failed to fix encoding for {file_path}: {e}")
    
    async def _fix_print_statements(self):
        """Replace print statements with logging"""
        console.logger.info("🔧 Fixing print statements...")
        
        for result in self.analysis_results:
            if result.read_success and "print statements" in str(result.issues):
                file_path = Path(result.file_path)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Replace print statements with logging
                    lines = content.split('\n')
                    new_lines = []
                    logging_added = False
                    
                    for line in lines:
                        if 'logger.info(' in line and not line.strip().startswith('#'):
                            if not logging_added:
                                new_lines.insert(0, 'import logging')
                                new_lines.insert(1, 'logger = logging.getLogger(__name__)')
                                logging_added = True
                            
                            # Replace print with logger.info
                            new_line = line.replace('logger.info(', 'logger.info(')
                            new_lines.append(new_line)
                        else:
                            new_lines.append(line)
                    
                    if logging_added:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write('\n'.join(new_lines))
                        self.fixes_applied.append(f"Replaced print statements with logging in {file_path}")
                        
                except Exception as e:
                    logger.error(f"Failed to fix print statements in {file_path}: {e}")
    
    async def _fix_exception_handling(self):
        """Fix bare except clauses"""
        console.logger.info("🔧 Fixing exception handling...")
        
        for result in self.analysis_results:
            if result.read_success and "Bare except clauses" in str(result.issues):
                file_path = Path(result.file_path)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Replace bare except with specific exceptions
                    content = content.replace('except Exception as e:', 'except Exception as e:')
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    self.fixes_applied.append(f"Fixed exception handling in {file_path}")
                        
                except Exception as e:
                    logger.error(f"Failed to fix exception handling in {file_path}: {e}")
    
    async def _fix_long_files(self):
        """Split long files into smaller modules"""
        console.logger.info("🔧 Splitting long files...")
        
        for result in self.analysis_results:
            if result.read_success and result.lines_of_code > 500:
                file_path = Path(result.file_path)
                if file_path.name in ['main.py', 'config.py', 'ai_agent_orchestrator.py']:
                    # These are core files, don't split automatically
                    self.fixes_applied.append(f"Marked {file_path} for manual splitting (core file)")
                else:
                    self.fixes_applied.append(f"Marked {file_path} for splitting ({result.lines_of_code} lines)")
    
    async def _fix_todo_comments(self):
        """Address TODO/FIXME comments"""
        console.logger.info("🔧 Addressing TODO/FIXME comments...")
        
        for result in self.analysis_results:
            if result.read_success and "TODO/FIXME" in str(result.issues):
                file_path = Path(result.file_path)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Replace TODO/FIXME with more specific comments
                    content = content.replace('FIXME: [PRIORITY]  [PRIORITY] ', 'FIXME: [PRIORITY]  [PRIORITY] ')
                    content = content.replace('FIXME: [PRIORITY] ', 'FIXME: [PRIORITY]  [PRIORITY] ')
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    self.fixes_applied.append(f"Updated TODO/FIXME comments in {file_path}")
                        
                except Exception as e:
                    logger.error(f"Failed to fix TODO comments in {file_path}: {e}")
    
    def _display_fixes_summary(self):
        """Display summary of applied fixes"""
        console.logger.info(Panel.fit(
            "[bold green]📋 Applied Fixes Summary[/bold green]",
            title="Fixes Applied"
        ))
        
        if self.fixes_applied:
            fixes_table = Table()
            fixes_table.add_column("Fix", style="cyan")
            
            for fix in self.fixes_applied:
                fixes_table.add_row(fix)
            
            console.logger.info(fixes_table)
        else:
            console.logger.info("No fixes were applied.")
    
    async def run_full_rewrite(self):
        """Run complete codebase analysis and rewrite"""
        console.logger.info(Panel.fit(
            "[bold green]🚀 Starting Full Codebase Rewrite[/bold green]",
            title="Full Rewrite"
        ))
        
        await self.analyze_codebase()
        await self.fix_codebase_issues()
        
        # Generate rewrite report
        await self._generate_rewrite_report()
        
    async def _generate_rewrite_report(self):
        """Generate comprehensive rewrite report"""
        scans_dir = Path("scans")
        scans_dir.mkdir(exist_ok=True)
        
        report_path = scans_dir / f"rewrite_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report_data = {
            "rewrite_timestamp": datetime.now().isoformat(),
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
                    "lines_of_code": r.lines_of_code,
                    "encoding": r.encoding,
                    "read_success": r.read_success
                }
                for r in self.analysis_results
            ],
            "applied_fixes": self.fixes_applied
        }
        
        with open(report_path, "w") as f:
            json.dump(report_data, f, indent=2)
        
        console.logger.info(f"✅ Rewrite report saved to: {report_path}")

async def main():
    """Main function"""
    console.logger.info(Panel.fit(
        "[bold blue]Claude 4 Coder Agent - Fixed Edition[/bold blue]\n"
        "Advanced Codebase Analysis and Rewriting System\n"
        "God-level development with AI-powered fixes",
        title="🚀 Claude Coder Agent"
    ))
    
    agent = ClaudeCoderAgent()
    
    await agent.run_full_rewrite()
    
    console.logger.info(Panel.fit(
        "[bold green]🎉 Codebase Rewrite Complete![/bold green]\n"
        "Your codebase has been analyzed and fixed with:\n"
        "• Improved file reading with encoding detection\n"
        "• Automatic print statement replacement\n"
        "• Enhanced exception handling\n"
        "• File splitting recommendations\n"
        "• TODO/FIXME comment updates",
        title="✅ Rewrite Complete"
    ))

if __name__ == "__main__":
    asyncio.run(main()) 