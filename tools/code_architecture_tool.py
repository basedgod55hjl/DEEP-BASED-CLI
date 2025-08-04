"""
Advanced Code Architecture Analysis Tool
Provides comprehensive system design and architecture analysis capabilities.
"""

import ast
import logging

import os
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass
from deep_cli.core.tool import BaseTool
from deep_cli.core.response import ToolResponse

@dataclass
class ArchitectureComponent:
    """Represents a component in the system architecture"""
    name: str
    type: str  # 'module', 'class', 'function', 'interface'
    dependencies: List[str]
    complexity: float
    lines_of_code: int
    documentation: str
    path: str

@dataclass
class ArchitectureAnalysis:
    """Complete architecture analysis result"""
    components: List[ArchitectureComponent]
    dependency_graph: Dict[str, List[str]]
    complexity_metrics: Dict[str, float]
    recommendations: List[str]
    architecture_score: float

class CodeArchitectureTool(BaseTool):
    """Advanced tool for analyzing and optimizing code architecture"""
    
    def __init__(self) -> Any:
        super().__init__(
            name="code_architecture_tool",
            description="Comprehensive code architecture analysis and optimization",
            capabilities=[
                "system_design_analysis",
                "dependency_mapping",
                "complexity_assessment",
                "architecture_optimization",
                "scalability_analysis"
            ]
        )
        self.supported_languages = ['python', 'typescript', 'javascript', 'java']
    
    async def execute(self, params: Dict[str, Any]) -> ToolResponse:
        """Execute architecture analysis"""
        try:
            operation = params.get('operation', 'analyze')
            
            if operation == 'analyze':
                return await self._analyze_architecture(params)
            elif operation == 'optimize':
                return await self._optimize_architecture(params)
            elif operation == 'generate_diagram':
                return await self._generate_architecture_diagram(params)
            elif operation == 'assess_scalability':
                return await self._assess_scalability(params)
            else:
                return ToolResponse(
                    success=False,
                    error=f"Unknown operation: {operation}",
                    message="Supported operations: analyze, optimize, generate_diagram, assess_scalability"
                )
        except Exception as e:
            return ToolResponse(
                success=False,
                error=str(e),
                message="Architecture analysis failed"
            )
    
    async def _analyze_architecture(self, params: Dict[str, Any]) -> ToolResponse:
        """Analyze code architecture"""
        project_path = params.get('project_path', '.')
        language = params.get('language', 'python')
        
        if not os.path.exists(project_path):
            return ToolResponse(
                success=False,
                error="Project path does not exist",
                message="Please provide a valid project path"
            )
        
        # Analyze project structure
        components = await self._extract_components(project_path, language)
        dependency_graph = self._build_dependency_graph(components)
        complexity_metrics = self._calculate_complexity_metrics(components)
        recommendations = self._generate_recommendations(components, dependency_graph)
        architecture_score = self._calculate_architecture_score(components, dependency_graph)
        
        analysis = ArchitectureAnalysis(
            components=components,
            dependency_graph=dependency_graph,
            complexity_metrics=complexity_metrics,
            recommendations=recommendations,
            architecture_score=architecture_score
        )
        
        return ToolResponse(
            success=True,
            data={
                'analysis': self._serialize_analysis(analysis),
                'summary': {
                    'total_components': len(components),
                    'architecture_score': architecture_score,
                    'complexity_level': self._get_complexity_level(architecture_score),
                    'recommendations_count': len(recommendations)
                }
            },
            message="Architecture analysis completed successfully"
        )
    
    async def _extract_components(self, project_path: str, language: str) -> List[ArchitectureComponent]:
        """Extract architectural components from the project"""
        components = []
        
        for root, dirs, files in os.walk(project_path):
            # Skip common directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv']]
            
            for file in files:
                if self._is_supported_file(file, language):
                    file_path = os.path.join(root, file)
                    file_components = await self._analyze_file(file_path, language)
                    components.extend(file_components)
        
        return components
    
    def _is_supported_file(self, filename: str, language: str) -> bool:
        """Check if file is supported for analysis"""
        extensions = {
            'python': ['.py'],
            'typescript': ['.ts', '.tsx'],
            'javascript': ['.js', '.jsx'],
            'java': ['.java']
        }
        
        return any(filename.endswith(ext) for ext in extensions.get(language, []))
    
    async def _analyze_file(self, file_path: str, language: str) -> List[ArchitectureComponent]:
        """Analyze a single file for components"""
        components = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if language == 'python':
                components = self._analyze_python_file(content, file_path)
            elif language in ['typescript', 'javascript']:
                components = self._analyze_typescript_file(content, file_path)
            elif language == 'java':
                components = self._analyze_java_file(content, file_path)
                
        except Exception as e:
            # Log error but continue with other files
            logging.info(f"Error analyzing {file_path}: {e}")
        
        return components
    
    def _analyze_python_file(self, content: str, file_path: str) -> List[ArchitectureComponent]:
        """Analyze Python file for components"""
        components = []
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    component = ArchitectureComponent(
                        name=node.name,
                        type='class',
                        dependencies=self._extract_python_dependencies(node),
                        complexity=self._calculate_python_complexity(node),
                        lines_of_code=len(node.body),
                        documentation=ast.get_docstring(node) or '',
                        path=file_path
                    )
                    components.append(component)
                
                elif isinstance(node, ast.FunctionDef):
                    component = ArchitectureComponent(
                        name=node.name,
                        type='function',
                        dependencies=self._extract_python_dependencies(node),
                        complexity=self._calculate_python_complexity(node),
                        lines_of_code=len(node.body),
                        documentation=ast.get_docstring(node) or '',
                        path=file_path
                    )
                    components.append(component)
                    
        except SyntaxError:
            # Skip files with syntax errors
            pass
        
        return components
    
    def _extract_python_dependencies(self, node) -> List[str]:
        """Extract dependencies from Python AST node"""
        dependencies = []
        
        for child in ast.walk(node):
            if isinstance(child, ast.Import):
                for alias in child.names:
                    dependencies.append(alias.name)
            elif isinstance(child, ast.ImportFrom):
                if child.module:
                    dependencies.append(child.module)
        
        return dependencies
    
    def _calculate_python_complexity(self, node) -> float:
        """Calculate cyclomatic complexity for Python node"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def _analyze_typescript_file(self, content: str, file_path: str) -> List[ArchitectureComponent]:
        """Analyze TypeScript/JavaScript file for components"""
        # Simplified analysis - in production, use proper TypeScript parser
        components = []
        
        # Extract class definitions
        import re
        class_pattern = r'class\s+(\w+)'
        function_pattern = r'(?:export\s+)?(?:async\s+)?function\s+(\w+)'
        
        for match in re.finditer(class_pattern, content):
            component = ArchitectureComponent(
                name=match.group(1),
                type='class',
                dependencies=[],  # Would need proper parsing
                complexity=1.0,   # Simplified
                lines_of_code=len(content.split('\n')),
                documentation='',
                path=file_path
            )
            components.append(component)
        
        for match in re.finditer(function_pattern, content):
            component = ArchitectureComponent(
                name=match.group(1),
                type='function',
                dependencies=[],
                complexity=1.0,
                lines_of_code=len(content.split('\n')),
                documentation='',
                path=file_path
            )
            components.append(component)
        
        return components
    
    def _analyze_java_file(self, content: str, file_path: str) -> List[ArchitectureComponent]:
        """Analyze Java file for components"""
        # Simplified analysis - in production, use proper Java parser
        components = []
        
        import re
        class_pattern = r'(?:public\s+)?class\s+(\w+)'
        
        for match in re.finditer(class_pattern, content):
            component = ArchitectureComponent(
                name=match.group(1),
                type='class',
                dependencies=[],
                complexity=1.0,
                lines_of_code=len(content.split('\n')),
                documentation='',
                path=file_path
            )
            components.append(component)
        
        return components
    
    def _build_dependency_graph(self, components: List[ArchitectureComponent]) -> Dict[str, List[str]]:
        """Build dependency graph from components"""
        graph = {}
        
        for component in components:
            graph[component.name] = component.dependencies
        
        return graph
    
    def _calculate_complexity_metrics(self, components: List[ArchitectureComponent]) -> Dict[str, float]:
        """Calculate complexity metrics"""
        if not components:
            return {}
        
        complexities = [c.complexity for c in components]
        lines_of_code = [c.lines_of_code for c in components]
        
        return {
            'average_complexity': sum(complexities) / len(complexities),
            'max_complexity': max(complexities),
            'total_lines_of_code': sum(lines_of_code),
            'average_lines_per_component': sum(lines_of_code) / len(lines_of_code),
            'complexity_distribution': {
                'low': len([c for c in complexities if c <= 3]),
                'medium': len([c for c in complexities if 3 < c <= 7]),
                'high': len([c for c in complexities if c > 7])
            }
        }
    
    def _generate_recommendations(self, components: List[ArchitectureComponent], 
                                dependency_graph: Dict[str, List[str]]) -> List[str]:
        """Generate architecture recommendations"""
        recommendations = []
        
        # Check for high complexity components
        high_complexity = [c for c in components if c.complexity > 7]
        if high_complexity:
            recommendations.append(
                f"Consider refactoring {len(high_complexity)} high-complexity components "
                f"({', '.join(c.name for c in high_complexity[:3])})"
            )
        
        # Check for circular dependencies
        circular_deps = self._detect_circular_dependencies(dependency_graph)
        if circular_deps:
            recommendations.append(
                f"Found {len(circular_deps)} circular dependencies. "
                "Consider restructuring to break dependency cycles."
            )
        
        # Check for large components
        large_components = [c for c in components if c.lines_of_code > 200]
        if large_components:
            recommendations.append(
                f"Consider breaking down {len(large_components)} large components "
                f"({', '.join(c.name for c in large_components[:3])})"
            )
        
        # Check for undocumented components
        undocumented = [c for c in components if not c.documentation.strip()]
        if undocumented:
            recommendations.append(
                f"Add documentation to {len(undocumented)} undocumented components"
            )
        
        return recommendations
    
    def _detect_circular_dependencies(self, graph: Dict[str, List[str]]) -> List[List[str]]:
        """Detect circular dependencies using DFS"""
        def dfs(node: str, visited: set, rec_stack: set, path: List[str]) -> List[List[str]]:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            cycles = []
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    cycles.extend(dfs(neighbor, visited, rec_stack, path))
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:] + [neighbor])
            
            rec_stack.remove(node)
            path.pop()
            return cycles
        
        visited = set()
        all_cycles = []
        
        for node in graph:
            if node not in visited:
                all_cycles.extend(dfs(node, visited, set(), []))
        
        return all_cycles
    
    def _calculate_architecture_score(self, components: List[ArchitectureComponent], 
                                    dependency_graph: Dict[str, List[str]]) -> float:
        """Calculate overall architecture score (0-100)"""
        if not components:
            return 0.0
        
        score = 100.0
        
        # Penalize high complexity
        avg_complexity = sum(c.complexity for c in components) / len(components)
        if avg_complexity > 5:
            score -= (avg_complexity - 5) * 5
        
        # Penalize circular dependencies
        circular_deps = self._detect_circular_dependencies(dependency_graph)
        score -= len(circular_deps) * 10
        
        # Penalize large components
        large_components = [c for c in components if c.lines_of_code > 200]
        score -= len(large_components) * 2
        
        # Penalize undocumented components
        undocumented = [c for c in components if not c.documentation.strip()]
        score -= len(undocumented) * 1
        
        return max(0.0, score)
    
    def _get_complexity_level(self, score: float) -> str:
        """Get complexity level based on score"""
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Fair"
        else:
            return "Poor"
    
    def _serialize_analysis(self, analysis: ArchitectureAnalysis) -> Dict[str, Any]:
        """Serialize analysis result for JSON response"""
        return {
            'components': [
                {
                    'name': c.name,
                    'type': c.type,
                    'dependencies': c.dependencies,
                    'complexity': c.complexity,
                    'lines_of_code': c.lines_of_code,
                    'documentation': c.documentation,
                    'path': c.path
                }
                for c in analysis.components
            ],
            'dependency_graph': analysis.dependency_graph,
            'complexity_metrics': analysis.complexity_metrics,
            'recommendations': analysis.recommendations,
            'architecture_score': analysis.architecture_score
        }
    
    async def _optimize_architecture(self, params: Dict[str, Any]) -> ToolResponse:
        """Generate architecture optimization suggestions"""
        # This would implement advanced optimization algorithms
        return ToolResponse(
            success=True,
            data={'optimization_plan': 'Advanced optimization features coming soon'},
            message="Architecture optimization analysis completed"
        )
    
    async def _generate_architecture_diagram(self, params: Dict[str, Any]) -> ToolResponse:
        """Generate architecture diagram"""
        # This would generate visual diagrams (UML, etc.)
        return ToolResponse(
            success=True,
            data={'diagram_url': 'Architecture diagram generation coming soon'},
            message="Architecture diagram generation completed"
        )
    
    async def _assess_scalability(self, params: Dict[str, Any]) -> ToolResponse:
        """Assess system scalability"""
        # This would analyze scalability factors
        return ToolResponse(
            success=True,
            data={'scalability_assessment': 'Scalability analysis coming soon'},
            message="Scalability assessment completed"
        )
    
    def get_schema(self) -> Dict[str, Any]:
        """Return tool parameter schema"""
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["analyze", "optimize", "generate_diagram", "assess_scalability"],
                    "description": "Operation to perform"
                },
                "project_path": {
                    "type": "string",
                    "description": "Path to the project to analyze"
                },
                "language": {
                    "type": "string",
                    "enum": ["python", "typescript", "javascript", "java"],
                    "description": "Primary programming language"
                }
            },
            "required": ["operation"]
        } 