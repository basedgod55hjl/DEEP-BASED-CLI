#!/usr/bin/env python3
"""
DeepSeek Reasoner Tool - Comprehensive Codebase Analysis and Integration
Advanced reasoning system for codebase analysis, wiring, and GitHub integration
"""

import os
import json
import asyncio
import aiohttp
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from datetime import datetime
import hashlib
import shutil
from collections import defaultdict

from .base_tool import BaseTool, ToolResponse

logger = logging.getLogger(__name__)

@dataclass
class FileAnalysis:
    """File analysis results"""
    file_path: str
    file_type: str
    size: int
    lines: int
    dependencies: List[str]
    imports: List[str]
    exports: List[str]
    complexity: float
    issues: List[str]
    suggestions: List[str]
    git_history: Optional[List[Dict[str, Any]]] = None

@dataclass
class CodebaseAnalysis:
    """Complete codebase analysis"""
    total_files: int
    total_lines: int
    file_types: Dict[str, int]
    dependencies: Dict[str, List[str]]
    redundant_files: List[str]
    missing_dependencies: List[str]
    architecture_issues: List[str]
    improvement_suggestions: List[str]
    file_analysis: Dict[str, FileAnalysis]

@dataclass
class GitHubIntegration:
    """GitHub integration data"""
    repo_url: str
    api_endpoint: str
    file_tree: Dict[str, Any]
    commit_history: List[Dict[str, Any]]
    contributors: List[str]
    last_updated: str

class DeepSeekReasonerTool(BaseTool):
    """DeepSeek Reasoner Tool for comprehensive codebase analysis"""
    
    def __init__(self):
        super().__init__()
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        self.github_api_url = "https://api.github.com"
        self.analysis_cache = {}
        self.redundant_files_cache = set()
        
    async def execute(self, operation: str, **kwargs) -> ToolResponse:
        """Execute DeepSeek Reasoner operations"""
        try:
            if operation == "analyze_codebase":
                return await self._analyze_entire_codebase()
            elif operation == "wire_components":
                return await self._wire_components_together()
            elif operation == "remove_redundancy":
                return await self._remove_redundant_files()
            elif operation == "github_integration":
                repo_url = kwargs.get('repo_url')
                if not repo_url:
                    return ToolResponse(False, "repo_url parameter required")
                return await self._github_integration(repo_url)
            elif operation == "deep_reasoning":
                query = kwargs.get('query')
                if not query:
                    return ToolResponse(False, "query parameter required")
                return await self._deep_reasoning(query)
            elif operation == "optimize_architecture":
                return await self._optimize_architecture()
            elif operation == "generate_integration_plan":
                return await self._generate_integration_plan()
            else:
                return ToolResponse(False, f"Unknown operation: {operation}")
                
        except Exception as e:
            logger.error(f"DeepSeek Reasoner operation failed: {e}")
            return ToolResponse(False, str(e))
    
    async def _make_deepseek_request(self, prompt: str, model: str = "deepseek-chat") -> str:
        """Make request to DeepSeek API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.deepseek_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 4000,
                "temperature": 0.1
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url,
                    headers=headers,
                    json=payload,
                    timeout=60
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["choices"][0]["message"]["content"]
                    else:
                        logger.warning(f"DeepSeek API request failed: {response.status}")
                        return f"API request failed: {response.status}"
                        
        except Exception as e:
            logger.error(f"DeepSeek API request error: {e}")
            return f"API request error: {str(e)}"
    
    async def _analyze_entire_codebase(self) -> ToolResponse:
        """Analyze the entire codebase comprehensively"""
        try:
            logger.info("🔍 Starting comprehensive codebase analysis...")
            
            # Get all files
            all_files = []
            for root, dirs, files in os.walk("."):
                # Skip certain directories
                dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', '.pytest_cache']]
                
                for file in files:
                    if not file.endswith(('.pyc', '.pyo', '.log', '.tmp', '.backup')):
                        file_path = os.path.join(root, file)
                        all_files.append(file_path)
            
            # Analyze each file
            file_analysis = {}
            total_lines = 0
            file_types = defaultdict(int)
            dependencies = defaultdict(list)
            
            for file_path in all_files:
                try:
                    analysis = await self._analyze_single_file(file_path)
                    file_analysis[file_path] = analysis
                    total_lines += analysis.lines
                    file_types[analysis.file_type] += 1
                    
                    for dep in analysis.dependencies:
                        dependencies[file_path].append(dep)
                        
                except Exception as e:
                    logger.warning(f"Failed to analyze {file_path}: {e}")
            
            # Find redundant files
            redundant_files = await self._find_redundant_files(file_analysis)
            
            # Find missing dependencies
            missing_deps = await self._find_missing_dependencies(dependencies, file_analysis)
            
            # Architecture analysis
            arch_issues = await self._analyze_architecture(file_analysis)
            
            # Generate improvement suggestions
            suggestions = await self._generate_improvement_suggestions(file_analysis, redundant_files, missing_deps)
            
            analysis_result = CodebaseAnalysis(
                total_files=len(all_files),
                total_lines=total_lines,
                file_types=dict(file_types),
                dependencies=dict(dependencies),
                redundant_files=redundant_files,
                missing_dependencies=missing_deps,
                architecture_issues=arch_issues,
                improvement_suggestions=suggestions,
                file_analysis=file_analysis
            )
            
            # Cache the analysis
            self.analysis_cache = {
                'analysis': analysis_result,
                'timestamp': datetime.now().isoformat()
            }
            
            return ToolResponse(True, "Codebase analysis completed", {
                'total_files': analysis_result.total_files,
                'total_lines': analysis_result.total_lines,
                'file_types': analysis_result.file_types,
                'redundant_files_count': len(analysis_result.redundant_files),
                'missing_dependencies_count': len(analysis_result.missing_dependencies),
                'architecture_issues_count': len(analysis_result.architecture_issues),
                'suggestions_count': len(analysis_result.improvement_suggestions)
            })
            
        except Exception as e:
            logger.error(f"Codebase analysis failed: {e}")
            return ToolResponse(False, str(e))
    
    async def _analyze_single_file(self, file_path: str) -> FileAnalysis:
        """Analyze a single file"""
        try:
            file_type = Path(file_path).suffix
            size = os.path.getsize(file_path)
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = len(content.split('\n'))
            
            # Analyze dependencies and imports
            dependencies = []
            imports = []
            exports = []
            
            if file_type == '.py':
                dependencies, imports, exports = await self._analyze_python_file(content)
            elif file_type == '.ts' or file_type == '.js':
                dependencies, imports, exports = await self._analyze_typescript_file(content)
            
            # Calculate complexity
            complexity = await self._calculate_complexity(content, file_type)
            
            # Find issues
            issues = await self._find_file_issues(content, file_type)
            
            # Generate suggestions
            suggestions = await self._generate_file_suggestions(content, file_type, issues)
            
            return FileAnalysis(
                file_path=file_path,
                file_type=file_type,
                size=size,
                lines=lines,
                dependencies=dependencies,
                imports=imports,
                exports=exports,
                complexity=complexity,
                issues=issues,
                suggestions=suggestions
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze file {file_path}: {e}")
            return FileAnalysis(
                file_path=file_path,
                file_type="unknown",
                size=0,
                lines=0,
                dependencies=[],
                imports=[],
                exports=[],
                complexity=0.0,
                issues=[f"Analysis failed: {str(e)}"],
                suggestions=[]
            )
    
    async def _analyze_python_file(self, content: str) -> tuple:
        """Analyze Python file for dependencies"""
        dependencies = []
        imports = []
        exports = []
        
        try:
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                
                # Find imports
                if line.startswith('import ') or line.startswith('from '):
                    imports.append(line)
                    
                    # Extract module names
                    if line.startswith('import '):
                        parts = line.split('import ')[1].split(' as ')[0].split(',')
                        for part in parts:
                            module = part.strip().split('.')[0]
                            if module not in dependencies:
                                dependencies.append(module)
                    elif line.startswith('from '):
                        module = line.split('from ')[1].split(' import ')[0].split('.')[0]
                        if module not in dependencies:
                            dependencies.append(module)
                
                # Find function/class definitions (potential exports)
                if line.startswith('def ') or line.startswith('class '):
                    name = line.split('(')[0].split(':')[0].split(' ')[1]
                    exports.append(name)
                    
        except Exception as e:
            logger.warning(f"Python file analysis error: {e}")
        
        return dependencies, imports, exports
    
    async def _analyze_typescript_file(self, content: str) -> tuple:
        """Analyze TypeScript file for dependencies"""
        dependencies = []
        imports = []
        exports = []
        
        try:
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                
                # Find imports
                if line.startswith('import '):
                    imports.append(line)
                    
                    # Extract module names
                    if 'from ' in line:
                        module = line.split('from ')[1].split(';')[0].strip("'\"")
                        if module.startswith('.'):
                            # Local import
                            pass
                        else:
                            # External dependency
                            dep = module.split('/')[0]
                            if dep not in dependencies:
                                dependencies.append(dep)
                
                # Find exports
                if line.startswith('export '):
                    exports.append(line)
                    
        except Exception as e:
            logger.warning(f"TypeScript file analysis error: {e}")
        
        return dependencies, imports, exports
    
    async def _calculate_complexity(self, content: str, file_type: str) -> float:
        """Calculate code complexity"""
        try:
            lines = content.split('\n')
            complexity = 0.0
            
            for line in lines:
                line = line.strip()
                
                # Basic complexity metrics
                if any(keyword in line for keyword in ['if ', 'for ', 'while ', 'try:', 'except:', 'catch']):
                    complexity += 1
                
                if any(keyword in line for keyword in ['&&', '||', 'and ', 'or ']):
                    complexity += 0.5
                
                if line.count('(') > 2:  # Complex function calls
                    complexity += 0.3
            
            # Normalize by lines
            if lines:
                complexity = complexity / len(lines)
            
            return min(complexity, 10.0)  # Cap at 10
            
        except Exception as e:
            logger.warning(f"Complexity calculation error: {e}")
            return 0.0
    
    async def _find_file_issues(self, content: str, file_type: str) -> List[str]:
        """Find issues in a file"""
        issues = []
        
        try:
            lines = content.split('\n')
            
            # Check for common issues
            if len(lines) > 500:
                issues.append("File is very long (>500 lines)")
            
            if content.count('TODO') > 5:
                issues.append("Many TODO comments found")
            
            if content.count('FIXME') > 0:
                issues.append("FIXME comments found")
            
            if content.count('print(') > 10:
                issues.append("Many print statements (consider logging)")
            
            if content.count('except:') > 0:
                issues.append("Bare except clauses found")
            
            # Language-specific issues
            if file_type == '.py':
                if content.count('import *') > 0:
                    issues.append("Wildcard imports found")
                
                if content.count('global ') > 5:
                    issues.append("Many global variables")
                    
        except Exception as e:
            logger.warning(f"Issue detection error: {e}")
        
        return issues
    
    async def _generate_file_suggestions(self, content: str, file_type: str, issues: List[str]) -> List[str]:
        """Generate improvement suggestions for a file"""
        suggestions = []
        
        try:
            if "File is very long" in str(issues):
                suggestions.append("Consider splitting into smaller modules")
            
            if "Many print statements" in str(issues):
                suggestions.append("Replace print statements with proper logging")
            
            if "Bare except clauses" in str(issues):
                suggestions.append("Use specific exception types instead of bare except")
            
            if "Wildcard imports" in str(issues):
                suggestions.append("Import specific functions/classes instead of using *")
            
            if "Many global variables" in str(issues):
                suggestions.append("Consider using classes or modules to organize state")
            
            # Add general suggestions
            if len(content) > 1000:
                suggestions.append("Consider adding type hints for better code clarity")
            
            if content.count('def ') > 10:
                suggestions.append("Consider breaking down large functions")
                
        except Exception as e:
            logger.warning(f"Suggestion generation error: {e}")
        
        return suggestions
    
    async def _find_redundant_files(self, file_analysis: Dict[str, FileAnalysis]) -> List[str]:
        """Find redundant files in the codebase"""
        redundant_files = []
        
        try:
            # Group files by content hash
            content_hashes = {}
            for file_path, analysis in file_analysis.items():
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        content_hash = hashlib.md5(content.encode()).hexdigest()
                        
                        if content_hash in content_hashes:
                            redundant_files.append(file_path)
                        else:
                            content_hashes[content_hash] = file_path
                            
                except Exception as e:
                    logger.warning(f"Failed to hash {file_path}: {e}")
            
            # Find backup files
            for file_path in file_analysis.keys():
                if file_path.endswith('.backup') or '.backup.' in file_path:
                    redundant_files.append(file_path)
            
            # Find duplicate functionality
            duplicate_patterns = await self._find_duplicate_patterns(file_analysis)
            redundant_files.extend(duplicate_patterns)
            
        except Exception as e:
            logger.error(f"Redundant file detection failed: {e}")
        
        return list(set(redundant_files))
    
    async def _find_duplicate_patterns(self, file_analysis: Dict[str, FileAnalysis]) -> List[str]:
        """Find files with duplicate functionality patterns"""
        duplicate_files = []
        
        try:
            # Group files by similar functionality
            function_patterns = defaultdict(list)
            
            for file_path, analysis in file_analysis.items():
                if analysis.file_type == '.py':
                    # Look for common function patterns
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            
                            # Check for common patterns
                            if 'def main(' in content and 'if __name__ == "__main__"' in content:
                                function_patterns['main_script'].append(file_path)
                            
                            if 'class ' in content and 'def __init__' in content:
                                function_patterns['class_with_init'].append(file_path)
                            
                            if 'async def ' in content:
                                function_patterns['async_functions'].append(file_path)
                                
                    except Exception as e:
                        logger.warning(f"Failed to analyze patterns in {file_path}: {e}")
            
            # Find potential duplicates
            for pattern, files in function_patterns.items():
                if len(files) > 2:  # More than 2 files with same pattern
                    # Keep the most recent/modified file, mark others as redundant
                    files.sort(key=lambda f: os.path.getmtime(f), reverse=True)
                    duplicate_files.extend(files[1:])  # All except the most recent
                    
        except Exception as e:
            logger.error(f"Duplicate pattern detection failed: {e}")
        
        return duplicate_files
    
    async def _find_missing_dependencies(self, dependencies: Dict[str, List[str]], file_analysis: Dict[str, FileAnalysis]) -> List[str]:
        """Find missing dependencies"""
        missing_deps = []
        
        try:
            # Get all required dependencies
            all_required = set()
            for deps in dependencies.values():
                all_required.update(deps)
            
            # Check which dependencies are missing
            for dep in all_required:
                if not await self._dependency_exists(dep):
                    missing_deps.append(dep)
                    
        except Exception as e:
            logger.error(f"Missing dependency detection failed: {e}")
        
        return missing_deps
    
    async def _dependency_exists(self, dependency: str) -> bool:
        """Check if a dependency exists"""
        try:
            # Check if it's a built-in module
            import importlib
            try:
                importlib.import_module(dependency)
                return True
            except ImportError:
                pass
            
            # Check if it's a local file
            if os.path.exists(f"{dependency}.py"):
                return True
            
            # Check if it's in the current directory
            if os.path.exists(dependency):
                return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Dependency check failed for {dependency}: {e}")
            return False
    
    async def _analyze_architecture(self, file_analysis: Dict[str, FileAnalysis]) -> List[str]:
        """Analyze codebase architecture"""
        issues = []
        
        try:
            # Check for architectural issues
            main_files = [f for f in file_analysis.keys() if 'main' in f.lower()]
            if len(main_files) > 3:
                issues.append("Multiple main files detected - consider consolidation")
            
            # Check for circular dependencies
            circular_deps = await self._detect_circular_dependencies(file_analysis)
            if circular_deps:
                issues.append(f"Circular dependencies detected: {circular_deps}")
            
            # Check for proper separation of concerns
            if not any('config' in f.lower() for f in file_analysis.keys()):
                issues.append("No configuration management detected")
            
            if not any('test' in f.lower() for f in file_analysis.keys()):
                issues.append("No test files detected")
                
        except Exception as e:
            logger.error(f"Architecture analysis failed: {e}")
        
        return issues
    
    async def _detect_circular_dependencies(self, file_analysis: Dict[str, FileAnalysis]) -> List[str]:
        """Detect circular dependencies"""
        circular_deps = []
        
        try:
            # Build dependency graph
            graph = {}
            for file_path, analysis in file_analysis.items():
                graph[file_path] = analysis.dependencies
            
            # Simple circular dependency detection
            for file_path, deps in graph.items():
                for dep in deps:
                    if dep in graph and file_path in graph[dep]:
                        circular_deps.append(f"{file_path} <-> {dep}")
                        
        except Exception as e:
            logger.error(f"Circular dependency detection failed: {e}")
        
        return circular_deps
    
    async def _generate_improvement_suggestions(self, file_analysis: Dict[str, FileAnalysis], redundant_files: List[str], missing_deps: List[str]) -> List[str]:
        """Generate overall improvement suggestions"""
        suggestions = []
        
        try:
            if redundant_files:
                suggestions.append(f"Remove {len(redundant_files)} redundant files to clean up codebase")
            
            if missing_deps:
                suggestions.append(f"Install {len(missing_deps)} missing dependencies")
            
            # Count issues by type
            total_issues = sum(len(analysis.issues) for analysis in file_analysis.values())
            if total_issues > 50:
                suggestions.append("High number of issues detected - prioritize code quality improvements")
            
            # Suggest testing
            test_files = [f for f in file_analysis.keys() if 'test' in f.lower()]
            if len(test_files) < len(file_analysis) * 0.1:  # Less than 10% test coverage
                suggestions.append("Add comprehensive test coverage")
            
            # Suggest documentation
            doc_files = [f for f in file_analysis.keys() if f.endswith('.md') or 'readme' in f.lower()]
            if len(doc_files) < 3:
                suggestions.append("Improve documentation coverage")
                
        except Exception as e:
            logger.error(f"Improvement suggestion generation failed: {e}")
        
        return suggestions
    
    async def _wire_components_together(self) -> ToolResponse:
        """Wire all components together"""
        try:
            logger.info("🔗 Wiring components together...")
            
            if not self.analysis_cache:
                # Run analysis first
                analysis_result = await self._analyze_entire_codebase()
                if not analysis_result.success:
                    return analysis_result
            
            analysis = self.analysis_cache['analysis']
            
            # Create integration plan
            integration_plan = await self._create_integration_plan(analysis)
            
            # Execute integration
            integration_results = await self._execute_integration(integration_plan)
            
            return ToolResponse(True, "Component wiring completed", {
                'integration_plan': integration_plan,
                'results': integration_results,
                'files_modified': len(integration_results.get('modified_files', [])),
                'new_files_created': len(integration_results.get('new_files', []))
            })
            
        except Exception as e:
            logger.error(f"Component wiring failed: {e}")
            return ToolResponse(False, str(e))
    
    async def _create_integration_plan(self, analysis: CodebaseAnalysis) -> Dict[str, Any]:
        """Create integration plan"""
        plan = {
            'main_entry_points': [],
            'module_consolidation': [],
            'dependency_management': [],
            'configuration_unification': [],
            'testing_framework': [],
            'documentation_updates': []
        }
        
        try:
            # Identify main entry points
            for file_path, file_analysis in analysis.file_analysis.items():
                if 'main' in file_path.lower() or file_path.endswith('.py') and 'if __name__ == "__main__"' in file_analysis.content:
                    plan['main_entry_points'].append(file_path)
            
            # Plan module consolidation
            for file_path in analysis.redundant_files:
                plan['module_consolidation'].append({
                    'action': 'remove',
                    'file': file_path,
                    'reason': 'Redundant file'
                })
            
            # Plan dependency management
            for dep in analysis.missing_dependencies:
                plan['dependency_management'].append({
                    'action': 'install',
                    'dependency': dep,
                    'type': 'external'
                })
            
            return plan
            
        except Exception as e:
            logger.error(f"Integration plan creation failed: {e}")
            return plan
    
    async def _execute_integration(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute integration plan"""
        results = {
            'modified_files': [],
            'new_files': [],
            'removed_files': [],
            'errors': []
        }
        
        try:
            # Execute module consolidation
            for item in plan['module_consolidation']:
                if item['action'] == 'remove':
                    try:
                        os.remove(item['file'])
                        results['removed_files'].append(item['file'])
                    except Exception as e:
                        results['errors'].append(f"Failed to remove {item['file']}: {e}")
            
            # Create unified configuration
            config_content = await self._create_unified_config()
            config_file = "config/unified_config.py"
            os.makedirs("config", exist_ok=True)
            
            with open(config_file, 'w') as f:
                f.write(config_content)
            results['new_files'].append(config_file)
            
            # Create main orchestrator
            orchestrator_content = await self._create_main_orchestrator()
            orchestrator_file = "main_orchestrator.py"
            
            with open(orchestrator_file, 'w') as f:
                f.write(orchestrator_content)
            results['new_files'].append(orchestrator_file)
            
        except Exception as e:
            logger.error(f"Integration execution failed: {e}")
            results['errors'].append(str(e))
        
        return results
    
    async def _create_unified_config(self) -> str:
        """Create unified configuration file"""
        return '''#!/usr/bin/env python3
"""
Unified Configuration for DEEP-CLI
Centralized configuration management
"""

import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class UnifiedConfig:
    """Unified configuration manager"""
    
    def __init__(self):
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from environment and files"""
        return {
            'api_keys': {
                'deepseek': os.getenv('DEEPSEEK_API_KEY'),
                'github': os.getenv('GITHUB_TOKEN'),
                'anthropic': os.getenv('ANTHROPIC_API_KEY')
            },
            'paths': {
                'data_dir': 'data',
                'logs_dir': 'logs',
                'config_dir': 'config'
            },
            'features': {
                'git_integration': True,
                'github_learning': True,
                'deep_reasoning': True,
                'auto_optimization': True
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value

# Global config instance
config = UnifiedConfig()
'''
    
    async def _create_main_orchestrator(self) -> str:
        """Create main orchestrator file"""
        return '''#!/usr/bin/env python3
"""
Main Orchestrator for DEEP-CLI
Coordinates all components and tools
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, Any

from config.unified_config import config
from tools.tool_manager import ToolManager
from tools.deepseek_reasoner_tool import DeepSeekReasonerTool

class MainOrchestrator:
    """Main orchestrator for the system"""
    
    def __init__(self):
        self.tool_manager = ToolManager()
        self.reasoner = DeepSeekReasonerTool()
        self.logger = logging.getLogger(__name__)
    
    async def initialize_system(self):
        """Initialize the entire system"""
        self.logger.info("🚀 Initializing DEEP-CLI system...")
        
        # Initialize tools
        await self.tool_manager.health_check()
        
        # Run codebase analysis
        analysis_result = await self.reasoner.execute("analyze_codebase")
        if analysis_result.success:
            self.logger.info("✅ Codebase analysis completed")
        
        # Wire components
        wiring_result = await self.reasoner.execute("wire_components")
        if wiring_result.success:
            self.logger.info("✅ Component wiring completed")
        
        self.logger.info("🎉 System initialization completed!")
    
    async def run(self):
        """Main run method"""
        await self.initialize_system()
        
        # Start interactive mode or other operations
        # This can be extended based on requirements

if __name__ == "__main__":
    orchestrator = MainOrchestrator()
    asyncio.run(orchestrator.run())
'''
    
    async def _remove_redundant_files(self) -> ToolResponse:
        """Remove redundant files"""
        try:
            logger.info("🗑️ Removing redundant files...")
            
            if not self.analysis_cache:
                # Run analysis first
                analysis_result = await self._analyze_entire_codebase()
                if not analysis_result.success:
                    return analysis_result
            
            analysis = self.analysis_cache['analysis']
            removed_files = []
            errors = []
            
            for file_path in analysis.redundant_files:
                try:
                    # Create backup before removal
                    backup_path = f"{file_path}.removed_backup"
                    shutil.move(file_path, backup_path)
                    removed_files.append(file_path)
                    self.redundant_files_cache.add(file_path)
                    
                except Exception as e:
                    errors.append(f"Failed to remove {file_path}: {e}")
            
            return ToolResponse(True, f"Removed {len(removed_files)} redundant files", {
                'removed_files': removed_files,
                'errors': errors,
                'backups_created': len(removed_files)
            })
            
        except Exception as e:
            logger.error(f"Redundant file removal failed: {e}")
            return ToolResponse(False, str(e))
    
    async def _github_integration(self, repo_url: str) -> ToolResponse:
        """Integrate with GitHub for repository learning"""
        try:
            logger.info(f"🔗 Integrating with GitHub: {repo_url}")
            
            # Extract repo info from URL
            repo_parts = repo_url.replace('https://github.com/', '').split('/')
            if len(repo_parts) != 2:
                return ToolResponse(False, "Invalid GitHub repository URL")
            
            owner, repo = repo_parts
            
            # GitHub API endpoints
            headers = {}
            if self.github_token:
                headers['Authorization'] = f'token {self.github_token}'
            
            async with aiohttp.ClientSession() as session:
                # Get repository information
                repo_url_api = f"{self.github_api_url}/repos/{owner}/{repo}"
                async with session.get(repo_url_api, headers=headers) as response:
                    if response.status == 200:
                        repo_data = await response.json()
                    else:
                        return ToolResponse(False, f"Failed to fetch repo data: {response.status}")
                
                # Get file tree
                tree_url = f"{self.github_api_url}/repos/{owner}/{repo}/git/trees/main?recursive=1"
                async with session.get(tree_url, headers=headers) as response:
                    if response.status == 200:
                        tree_data = await response.json()
                        file_tree = tree_data.get('tree', [])
                    else:
                        file_tree = []
                
                # Get recent commits
                commits_url = f"{self.github_api_url}/repos/{owner}/{repo}/commits"
                async with session.get(commits_url, headers=headers) as response:
                    if response.status == 200:
                        commits_data = await response.json()
                        recent_commits = commits_data[:10]  # Last 10 commits
                    else:
                        recent_commits = []
            
            # Create GitHub integration data
            github_data = GitHubIntegration(
                repo_url=repo_url,
                api_endpoint=f"{self.github_api_url}/repos/{owner}/{repo}",
                file_tree=file_tree,
                commit_history=recent_commits,
                contributors=repo_data.get('contributors_url', ''),
                last_updated=repo_data.get('updated_at', '')
            )
            
            # Save GitHub data
            os.makedirs("data", exist_ok=True)
            github_file = f"data/github_integration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(github_file, 'w') as f:
                json.dump({
                    'repo_url': github_data.repo_url,
                    'file_count': len(github_data.file_tree),
                    'commit_count': len(github_data.commit_history),
                    'last_updated': github_data.last_updated,
                    'file_tree': github_data.file_tree[:100],  # Limit for storage
                    'recent_commits': github_data.commit_history
                }, f, indent=2)
            
            return ToolResponse(True, "GitHub integration completed", {
                'repo_url': repo_url,
                'file_count': len(file_tree),
                'commit_count': len(recent_commits),
                'github_data_file': github_file
            })
            
        except Exception as e:
            logger.error(f"GitHub integration failed: {e}")
            return ToolResponse(False, str(e))
    
    async def _deep_reasoning(self, query: str) -> ToolResponse:
        """Perform deep reasoning on the codebase"""
        try:
            logger.info("🧠 Performing deep reasoning...")
            
            if not self.analysis_cache:
                # Run analysis first
                analysis_result = await self._analyze_entire_codebase()
                if not analysis_result.success:
                    return analysis_result
            
            analysis = self.analysis_cache['analysis']
            
            # Create comprehensive prompt for DeepSeek
            prompt = f"""
            Perform deep reasoning analysis on this codebase:
            
            Codebase Overview:
            - Total files: {analysis.total_files}
            - Total lines: {analysis.total_lines}
            - File types: {analysis.file_types}
            - Redundant files: {len(analysis.redundant_files)}
            - Missing dependencies: {len(analysis.missing_dependencies)}
            - Architecture issues: {len(analysis.architecture_issues)}
            
            Query: {query}
            
            Please provide:
            1. Deep analysis of the codebase structure
            2. Identification of architectural patterns
            3. Recommendations for improvement
            4. Potential optimizations
            5. Security considerations
            6. Performance analysis
            
            Focus on actionable insights and specific recommendations.
            """
            
            # Get DeepSeek reasoning
            reasoning_result = await self._make_deepseek_request(prompt, "deepseek-reasoner")
            
            return ToolResponse(True, "Deep reasoning completed", {
                'query': query,
                'reasoning': reasoning_result,
                'analysis_summary': {
                    'total_files': analysis.total_files,
                    'total_lines': analysis.total_lines,
                    'issues_count': len(analysis.architecture_issues)
                }
            })
            
        except Exception as e:
            logger.error(f"Deep reasoning failed: {e}")
            return ToolResponse(False, str(e))
    
    async def _optimize_architecture(self) -> ToolResponse:
        """Optimize the codebase architecture"""
        try:
            logger.info("⚡ Optimizing architecture...")
            
            if not self.analysis_cache:
                # Run analysis first
                analysis_result = await self._analyze_entire_codebase()
                if not analysis_result.success:
                    return analysis_result
            
            analysis = self.analysis_cache['analysis']
            
            # Create optimization plan
            optimization_plan = await self._create_optimization_plan(analysis)
            
            # Execute optimizations
            optimization_results = await self._execute_optimizations(optimization_plan)
            
            return ToolResponse(True, "Architecture optimization completed", {
                'optimization_plan': optimization_plan,
                'results': optimization_results,
                'files_optimized': len(optimization_results.get('optimized_files', [])),
                'performance_improvements': optimization_results.get('performance_improvements', [])
            })
            
        except Exception as e:
            logger.error(f"Architecture optimization failed: {e}")
            return ToolResponse(False, str(e))
    
    async def _create_optimization_plan(self, analysis: CodebaseAnalysis) -> Dict[str, Any]:
        """Create optimization plan"""
        plan = {
            'performance_optimizations': [],
            'memory_optimizations': [],
            'code_quality_improvements': [],
            'architectural_refactoring': []
        }
        
        try:
            # Performance optimizations
            for file_path, file_analysis in analysis.file_analysis.items():
                if file_analysis.complexity > 5.0:
                    plan['performance_optimizations'].append({
                        'file': file_path,
                        'action': 'refactor_high_complexity',
                        'current_complexity': file_analysis.complexity
                    })
                
                if file_analysis.lines > 300:
                    plan['performance_optimizations'].append({
                        'file': file_path,
                        'action': 'split_large_file',
                        'current_lines': file_analysis.lines
                    })
            
            # Code quality improvements
            for file_path, file_analysis in analysis.file_analysis.items():
                if file_analysis.issues:
                    plan['code_quality_improvements'].append({
                        'file': file_path,
                        'issues': file_analysis.issues,
                        'suggestions': file_analysis.suggestions
                    })
            
            return plan
            
        except Exception as e:
            logger.error(f"Optimization plan creation failed: {e}")
            return plan
    
    async def _execute_optimizations(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute optimization plan"""
        results = {
            'optimized_files': [],
            'performance_improvements': [],
            'errors': []
        }
        
        try:
            # Execute performance optimizations
            for opt in plan['performance_optimizations']:
                try:
                    if opt['action'] == 'refactor_high_complexity':
                        # Create refactored version
                        refactored_content = await self._refactor_high_complexity(opt['file'])
                        if refactored_content:
                            backup_path = f"{opt['file']}.complexity_backup"
                            shutil.copy2(opt['file'], backup_path)
                            
                            with open(opt['file'], 'w') as f:
                                f.write(refactored_content)
                            
                            results['optimized_files'].append(opt['file'])
                            results['performance_improvements'].append(f"Reduced complexity in {opt['file']}")
                    
                except Exception as e:
                    results['errors'].append(f"Failed to optimize {opt['file']}: {e}")
            
        except Exception as e:
            logger.error(f"Optimization execution failed: {e}")
            results['errors'].append(str(e))
        
        return results
    
    async def _refactor_high_complexity(self, file_path: str) -> Optional[str]:
        """Refactor high complexity file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Create refactoring prompt
            prompt = f"""
            Refactor this high-complexity Python file to reduce complexity:
            
            {content}
            
            Please:
            1. Break down large functions into smaller ones
            2. Extract complex logic into separate functions
            3. Use helper functions for repeated patterns
            4. Improve readability and maintainability
            5. Keep the same functionality
            
            Return only the refactored code.
            """
            
            refactored_content = await self._make_deepseek_request(prompt, "deepseek-coder")
            return refactored_content
            
        except Exception as e:
            logger.error(f"Refactoring failed for {file_path}: {e}")
            return None
    
    async def _generate_integration_plan(self) -> ToolResponse:
        """Generate comprehensive integration plan"""
        try:
            logger.info("📋 Generating integration plan...")
            
            if not self.analysis_cache:
                # Run analysis first
                analysis_result = await self._analyze_entire_codebase()
                if not analysis_result.success:
                    return analysis_result
            
            analysis = self.analysis_cache['analysis']
            
            # Create comprehensive integration plan
            plan = {
                'phase_1': {
                    'name': 'Codebase Cleanup',
                    'tasks': [
                        f"Remove {len(analysis.redundant_files)} redundant files",
                        f"Fix {len(analysis.missing_dependencies)} missing dependencies",
                        "Consolidate configuration files"
                    ]
                },
                'phase_2': {
                    'name': 'Component Integration',
                    'tasks': [
                        "Wire all tools together",
                        "Create unified entry points",
                        "Implement proper error handling"
                    ]
                },
                'phase_3': {
                    'name': 'GitHub Integration',
                    'tasks': [
                        "Set up GitHub API integration",
                        "Implement repository learning",
                        "Create automated analysis pipeline"
                    ]
                },
                'phase_4': {
                    'name': 'Optimization',
                    'tasks': [
                        "Performance optimization",
                        "Memory usage optimization",
                        "Code quality improvements"
                    ]
                }
            }
            
            # Save integration plan
            os.makedirs("data", exist_ok=True)
            plan_file = f"data/integration_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(plan_file, 'w') as f:
                json.dump(plan, f, indent=2)
            
            return ToolResponse(True, "Integration plan generated", {
                'plan': plan,
                'plan_file': plan_file,
                'total_phases': len(plan),
                'total_tasks': sum(len(phase['tasks']) for phase in plan.values())
            })
            
        except Exception as e:
            logger.error(f"Failed to generate integration plan: {e}")
            return ToolResponse(False, f"Integration plan generation failed: {str(e)}") 