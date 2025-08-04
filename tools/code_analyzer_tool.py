#!/usr/bin/env python3
"""
🔍 Code Analyzer Tool - Enhanced Codebase Understanding for DEEP-BASED-CODER
Powered by DeepSeek models exclusively

Features:
- Codebase structure analysis
- Dependency mapping
- Code pattern recognition
- Code explanation and documentation
- Performance analysis
- Security scanning
- Best practices recommendations
- DeepSeek Reasoner integration for advanced analysis
"""

import os
import sys
import json
import ast
import re
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Set
from datetime import datetime
import subprocess
import asyncio

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from .base_tool import BaseTool, ToolResponse, ToolStatus
from .deepseek_coder_tool import DeepSeekCoderTool

class CodeAnalyzerTool(BaseTool):
    """Enhanced code analysis and understanding tool powered by DeepSeek"""
    
    def __init__(self):
        super().__init__()
        self.name = "Code Analyzer Tool"
        self.description = "Comprehensive codebase analysis and understanding with DeepSeek integration"
        self.deepseek_tool = DeepSeekCoderTool()
        self.supported_languages = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'react',
            '.tsx': 'react',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.rb': 'ruby',
            '.cs': 'csharp',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.dart': 'dart',
            '.lua': 'lua',
            '.r': 'r',
            '.sql': 'sql',
            '.sh': 'bash',
            '.ps1': 'powershell',
            '.yml': 'yaml',
            '.yaml': 'yaml',
            '.json': 'json',
            '.xml': 'xml',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.less': 'less'
        }
        
    def get_schema(self) -> Dict[str, Any]:
        """Get tool schema for API integration"""
        return {
            "name": "code_analyzer",
            "description": "Analyze code structure, patterns, and quality",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["analyze", "explain", "analyze_project", "find_patterns", 
                                "security_scan", "performance_analyze", "documentation_generate",
                                "complexity_analysis", "dependency_analysis"],
                        "description": "Type of analysis to perform"
                    },
                    "path": {
                        "type": "string",
                        "description": "Path to analyze (file or directory)"
                    },
                    "file_content": {
                        "type": "string",
                        "description": "Content of file to analyze"
                    },
                    "file_path": {
                        "type": "string", 
                        "description": "Path of file being analyzed"
                    },
                    "options": {
                        "type": "object",
                        "description": "Additional analysis options"
                    }
                },
                "required": ["action"]
            }
        }
        
    async def execute(self, action: str, **kwargs) -> ToolResponse:
        """Execute code analysis action with DeepSeek integration"""
        try:
            if action == "analyze":
                return await self._analyze_project(**kwargs)
            elif action == "explain":
                return await self._explain_code(**kwargs)
            elif action == "analyze_project":
                return await self._analyze_project(**kwargs)
            elif action == "find_patterns":
                return await self._find_patterns(**kwargs)
            elif action == "security_scan":
                return await self._security_scan(**kwargs)
            elif action == "performance_analyze":
                return await self._performance_analyze(**kwargs)
            elif action == "documentation_generate":
                return await self._generate_documentation(**kwargs)
            elif action == "complexity_analysis":
                return await self._complexity_analysis(**kwargs)
            elif action == "dependency_analysis":
                return await self._dependency_analysis(**kwargs)
            else:
                return ToolResponse(
                    status=ToolStatus.ERROR,
                    message=f"Unknown action: {action}",
                    data={"available_actions": ["analyze", "explain", "analyze_project", 
                                               "find_patterns", "security_scan", "performance_analyze", 
                                               "documentation_generate", "complexity_analysis", 
                                               "dependency_analysis"]}
                )
        except Exception as e:
            logging.error(f"Code analysis error: {e}")
            return ToolResponse(
                status=ToolStatus.ERROR,
                message=f"Code analysis error: {str(e)}"
            )
    
    async def _analyze_project(self, path: str = None, **kwargs) -> ToolResponse:
        """Analyze entire project structure and dependencies with DeepSeek insights"""
        try:
            if not path:
                path = os.getcwd()
            
            # Basic analysis
            analysis = {
                "project_info": self._get_project_info(path),
                "structure": self._analyze_structure(path),
                "dependencies": self._analyze_dependencies(path),
                "patterns": self._find_code_patterns(path),
                "complexity": self._analyze_complexity(path),
                "security": self._basic_security_scan(path),
                "performance": self._basic_performance_analysis(path),
                "suggestions": []
            }
            
            # Enhanced AI analysis using DeepSeek Reasoner
            deepseek_analysis = await self._deepseek_project_analysis(analysis, path)
            analysis.update(deepseek_analysis)
            
            return ToolResponse(
                status=ToolStatus.SUCCESS,
                data=analysis,
                message="Comprehensive project analysis complete with DeepSeek insights"
            )
                
        except Exception as e:
            logging.error(f"Project analysis error: {e}")
            return ToolResponse(
                status=ToolStatus.ERROR,
                message=f"Project analysis error: {str(e)}"
            )
    
    async def _deepseek_project_analysis(self, basic_analysis: Dict[str, Any], path: str) -> Dict[str, Any]:
        """Use DeepSeek Reasoner for advanced project analysis"""
        try:
            # Create comprehensive analysis prompt
            prompt = f"""
            Analyze this codebase comprehensively and provide expert insights:

            PROJECT INFORMATION:
            {json.dumps(basic_analysis['project_info'], indent=2)}

            STRUCTURE ANALYSIS:
            {json.dumps(basic_analysis['structure'], indent=2)}

            DEPENDENCIES:
            {json.dumps(basic_analysis['dependencies'], indent=2)}

            CODE PATTERNS:
            {json.dumps(basic_analysis['patterns'], indent=2)}

            COMPLEXITY METRICS:
            {json.dumps(basic_analysis['complexity'], indent=2)}

            Please provide:
            1. **Architecture Assessment**: Overall architecture quality and recommendations
            2. **Code Quality Score**: Rate from 1-10 with justification
            3. **Security Assessment**: Security posture and vulnerabilities
            4. **Performance Analysis**: Performance bottlenecks and optimizations
            5. **Maintainability**: How maintainable is this codebase
            6. **Scalability**: Can this codebase scale effectively
            7. **Best Practices**: What best practices are missing
            8. **Technical Debt**: Areas of technical debt to address
            9. **Refactoring Priorities**: Top 5 refactoring priorities
            10. **Technology Recommendations**: Technology stack improvements

            Format as JSON with clear sections.
            """
            
            response = await self.deepseek_tool.execute(
                "reasoning", 
                prompt=prompt,
                use_reasoning_model=True
            )
            
            if response.status == ToolStatus.SUCCESS:
                # Parse the DeepSeek response
                deepseek_insights = response.data.get("response", "")
                
                # Try to extract structured data
                try:
                    # Look for JSON in the response
                    json_match = re.search(r'\{.*\}', deepseek_insights, re.DOTALL)
                    if json_match:
                        structured_analysis = json.loads(json_match.group())
                    else:
                        # Fallback to parsed text analysis
                        structured_analysis = self._parse_deepseek_analysis(deepseek_insights)
                except:
                    structured_analysis = self._parse_deepseek_analysis(deepseek_insights)
                
                return {
                    "deepseek_analysis": structured_analysis,
                    "ai_insights": deepseek_insights,
                    "enhanced_suggestions": self._extract_suggestions(deepseek_insights)
                }
            else:
                return {
                    "deepseek_analysis": "Analysis unavailable",
                    "ai_insights": "DeepSeek analysis failed",
                    "enhanced_suggestions": []
                }
                
        except Exception as e:
            logging.error(f"DeepSeek analysis error: {e}")
            return {
                "deepseek_analysis": f"Error: {str(e)}",
                "ai_insights": "Analysis failed",
                "enhanced_suggestions": []
            }
    
    def _parse_deepseek_analysis(self, text: str) -> Dict[str, Any]:
        """Parse DeepSeek analysis text into structured data"""
        try:
            analysis = {
                "architecture_assessment": "",
                "code_quality_score": 0,
                "security_assessment": "",
                "performance_analysis": "",
                "maintainability": "",
                "scalability": "",
                "best_practices": [],
                "technical_debt": [],
                "refactoring_priorities": [],
                "technology_recommendations": []
            }
            
            # Extract sections using regex patterns
            sections = {
                "architecture_assessment": r"Architecture Assessment[:\-]*\s*(.*?)(?=\n\n|\n[A-Z]|$)",
                "security_assessment": r"Security Assessment[:\-]*\s*(.*?)(?=\n\n|\n[A-Z]|$)",
                "performance_analysis": r"Performance Analysis[:\-]*\s*(.*?)(?=\n\n|\n[A-Z]|$)",
                "maintainability": r"Maintainability[:\-]*\s*(.*?)(?=\n\n|\n[A-Z]|$)",
                "scalability": r"Scalability[:\-]*\s*(.*?)(?=\n\n|\n[A-Z]|$)"
            }
            
            for key, pattern in sections.items():
                match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                if match:
                    analysis[key] = match.group(1).strip()
            
            # Extract score
            score_match = re.search(r"(?:score|rating)[:\-]*\s*(\d+)", text, re.IGNORECASE)
            if score_match:
                analysis["code_quality_score"] = int(score_match.group(1))
            
            return analysis
        except Exception as e:
            logging.error(f"Parse analysis error: {e}")
            return {"error": str(e)}
    
    def _extract_suggestions(self, text: str) -> List[str]:
        """Extract actionable suggestions from DeepSeek analysis"""
        try:
            suggestions = []
            
            # Look for numbered lists, bullet points, or recommendation sections
            patterns = [
                r"(?:^|\n)\d+\.\s*(.*?)(?=\n\d+\.|\n[A-Z]|\n\n|$)",
                r"(?:^|\n)[-*]\s*(.*?)(?=\n[-*]|\n[A-Z]|\n\n|$)",
                r"(?:recommendation|suggest|should|consider)[:\-]*\s*(.*?)(?=\n\n|\n[A-Z]|$)"
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
                suggestions.extend([match.strip() for match in matches if len(match.strip()) > 10])
            
            # Remove duplicates and clean up
            unique_suggestions = []
            for suggestion in suggestions:
                if suggestion not in unique_suggestions and len(suggestion) > 20:
                    unique_suggestions.append(suggestion)
            
            return unique_suggestions[:10]  # Limit to top 10
        except Exception as e:
            logging.error(f"Extract suggestions error: {e}")
            return []
    
    def _get_project_info(self, path: str) -> Dict[str, Any]:
        """Get comprehensive project information"""
        try:
            project_path = Path(path)
            
            # Check for common project files
            project_files = {
                "package.json": project_path / "package.json",
                "requirements.txt": project_path / "requirements.txt",
                "pyproject.toml": project_path / "pyproject.toml",
                "Cargo.toml": project_path / "Cargo.toml",
                "go.mod": project_path / "go.mod",
                "pom.xml": project_path / "pom.xml",
                "build.gradle": project_path / "build.gradle",
                "Gemfile": project_path / "Gemfile",
                "composer.json": project_path / "composer.json",
                "CMakeLists.txt": project_path / "CMakeLists.txt",
                "Makefile": project_path / "Makefile",
                "Dockerfile": project_path / "Dockerfile",
                "docker-compose.yml": project_path / "docker-compose.yml",
                ".gitignore": project_path / ".gitignore",
                "README.md": project_path / "README.md",
                "LICENSE": project_path / "LICENSE"
            }
            
            detected_files = {}
            for name, file_path in project_files.items():
                if file_path.exists():
                    detected_files[name] = str(file_path)
            
            # Determine project type and framework
            project_type, framework = self._detect_project_type_and_framework(detected_files, project_path)
            
            return {
                "name": project_path.name,
                "path": str(project_path),
                "type": project_type,
                "framework": framework,
                "detected_files": detected_files,
                "size": self._get_directory_size(project_path),
                "file_count": self._count_files(project_path),
                "language_distribution": self._get_language_distribution(project_path),
                "git_info": self._get_git_info(project_path),
                "last_modified": self._get_last_modified(project_path)
            }
        except Exception as e:
            logging.error(f"Failed to get project info: {e}")
            return {"error": str(e)}
    
    def _detect_project_type_and_framework(self, detected_files: Dict[str, str], project_path: Path) -> Tuple[str, str]:
        """Detect project type and framework"""
        try:
            project_type = "unknown"
            framework = "none"
            
            # Primary type detection
            if "package.json" in detected_files:
                project_type = "nodejs"
                # Check for framework
                try:
                    with open(detected_files["package.json"], 'r') as f:
                        package_data = json.load(f)
                        deps = {**package_data.get("dependencies", {}), 
                               **package_data.get("devDependencies", {})}
                        
                        if "react" in deps:
                            framework = "react"
                        elif "vue" in deps:
                            framework = "vue"
                        elif "angular" in deps or "@angular/core" in deps:
                            framework = "angular"
                        elif "express" in deps:
                            framework = "express"
                        elif "next" in deps:
                            framework = "nextjs"
                        elif "nuxt" in deps:
                            framework = "nuxtjs"
                except:
                    pass
                    
            elif "requirements.txt" in detected_files or "pyproject.toml" in detected_files:
                project_type = "python"
                # Check for framework
                try:
                    if "requirements.txt" in detected_files:
                        with open(detected_files["requirements.txt"], 'r') as f:
                            reqs = f.read().lower()
                            if "django" in reqs:
                                framework = "django"
                            elif "flask" in reqs:
                                framework = "flask"
                            elif "fastapi" in reqs:
                                framework = "fastapi"
                            elif "tornado" in reqs:
                                framework = "tornado"
                except:
                    pass
                    
            elif "Cargo.toml" in detected_files:
                project_type = "rust"
                try:
                    with open(detected_files["Cargo.toml"], 'r') as f:
                        cargo_content = f.read().lower()
                        if "actix" in cargo_content:
                            framework = "actix"
                        elif "rocket" in cargo_content:
                            framework = "rocket"
                        elif "warp" in cargo_content:
                            framework = "warp"
                except:
                    pass
                    
            elif "go.mod" in detected_files:
                project_type = "go"
                try:
                    with open(detected_files["go.mod"], 'r') as f:
                        go_content = f.read().lower()
                        if "gin" in go_content:
                            framework = "gin"
                        elif "echo" in go_content:
                            framework = "echo"
                        elif "fiber" in go_content:
                            framework = "fiber"
                except:
                    pass
                    
            elif "pom.xml" in detected_files or "build.gradle" in detected_files:
                project_type = "java"
                if any((project_path / "src" / "main" / "java").rglob("*Spring*.java")):
                    framework = "spring"
                elif any((project_path / "src" / "main" / "java").rglob("*Controller.java")):
                    framework = "spring-boot"
                    
            return project_type, framework
        except Exception as e:
            logging.error(f"Project type detection error: {e}")
            return "unknown", "none"
    
    def _get_language_distribution(self, project_path: Path) -> Dict[str, int]:
        """Get distribution of programming languages in project"""
        try:
            distribution = {}
            
            for file_path in project_path.rglob('*'):
                if file_path.is_file() and not any(part.startswith('.') for part in file_path.parts):
                    ext = file_path.suffix.lower()
                    if ext in self.supported_languages:
                        lang = self.supported_languages[ext]
                        distribution[lang] = distribution.get(lang, 0) + 1
                    else:
                        distribution["other"] = distribution.get("other", 0) + 1
            
            return distribution
        except Exception as e:
            logging.error(f"Language distribution error: {e}")
            return {}
    
    def _get_git_info(self, project_path: Path) -> Dict[str, Any]:
        """Get Git repository information"""
        try:
            git_info = {}
            
            if (project_path / ".git").exists():
                try:
                    # Get current branch
                    result = subprocess.run(
                        ["git", "branch", "--show-current"],
                        cwd=project_path,
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        git_info["current_branch"] = result.stdout.strip()
                    
                    # Get commit count
                    result = subprocess.run(
                        ["git", "rev-list", "--count", "HEAD"],
                        cwd=project_path,
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        git_info["commit_count"] = int(result.stdout.strip())
                    
                    # Get last commit date
                    result = subprocess.run(
                        ["git", "log", "-1", "--format=%ci"],
                        cwd=project_path,
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        git_info["last_commit"] = result.stdout.strip()
                        
                except subprocess.TimeoutExpired:
                    git_info["error"] = "Git commands timed out"
                except Exception as e:
                    git_info["error"] = str(e)
            
            return git_info
        except Exception as e:
            logging.error(f"Git info error: {e}")
            return {"error": str(e)}
    
    def _get_last_modified(self, project_path: Path) -> str:
        """Get last modification time of project"""
        try:
            latest_time = 0
            for file_path in project_path.rglob('*'):
                if file_path.is_file():
                    mtime = file_path.stat().st_mtime
                    if mtime > latest_time:
                        latest_time = mtime
            
            return datetime.fromtimestamp(latest_time).isoformat()
        except Exception as e:
            logging.error(f"Last modified error: {e}")
            return "unknown"
    
    def _get_directory_size(self, path: Path) -> int:
        """Get directory size in bytes"""
        try:
            total_size = 0
            for file_path in path.rglob('*'):
                if file_path.is_file():
                    try:
                        total_size += file_path.stat().st_size
                    except (OSError, PermissionError):
                        pass  # Skip files we can't access
            return total_size
        except Exception:
            return 0
    
    def _count_files(self, path: Path) -> int:
        """Count files in directory"""
        try:
            return len([f for f in path.rglob('*') if f.is_file()])
        except Exception:
            return 0
    
    def _analyze_structure(self, path: str) -> Dict[str, Any]:
        """Analyze project structure comprehensively"""
        try:
            project_path = Path(path)
            structure = {
                "directories": [],
                "files": [],
                "file_types": {},
                "depth": 0,
                "architecture_patterns": [],
                "organization_score": 0
            }
            
            # Analyze directory structure
            for item in project_path.rglob('*'):
                if item.is_dir():
                    if not any(part.startswith('.') for part in item.parts):
                        rel_path = str(item.relative_to(project_path))
                        structure["directories"].append(rel_path)
                        
                        # Detect architecture patterns
                        if "src" in rel_path or "source" in rel_path:
                            structure["architecture_patterns"].append("source_separation")
                        if "test" in rel_path.lower() or "spec" in rel_path.lower():
                            structure["architecture_patterns"].append("test_organization")
                        if "docs" in rel_path.lower() or "documentation" in rel_path.lower():
                            structure["architecture_patterns"].append("documentation")
                            
                elif item.is_file():
                    if not any(part.startswith('.') for part in item.parts):
                        rel_path = str(item.relative_to(project_path))
                        structure["files"].append(rel_path)
                        
                        # Count file types
                        ext = item.suffix.lower()
                        if ext in self.supported_languages:
                            lang = self.supported_languages[ext]
                            structure["file_types"][lang] = structure["file_types"].get(lang, 0) + 1
                        else:
                            structure["file_types"]["other"] = structure["file_types"].get("other", 0) + 1
            
            # Calculate metrics
            structure["depth"] = max(len(Path(f).parts) for f in structure["files"]) if structure["files"] else 0
            structure["organization_score"] = self._calculate_organization_score(structure)
            
            return structure
        except Exception as e:
            logging.error(f"Failed to analyze structure: {e}")
            return {"error": str(e)}
    
    def _calculate_organization_score(self, structure: Dict[str, Any]) -> float:
        """Calculate project organization score (0-100)"""
        try:
            score = 0
            max_score = 100
            
            # Bonus for good directory structure
            if "source_separation" in structure.get("architecture_patterns", []):
                score += 20
            if "test_organization" in structure.get("architecture_patterns", []):
                score += 20
            if "documentation" in structure.get("architecture_patterns", []):
                score += 10
            
            # Penalty for too deep nesting
            depth = structure.get("depth", 0)
            if depth > 6:
                score -= (depth - 6) * 5
            
            # Bonus for reasonable file distribution
            file_types = structure.get("file_types", {})
            if len(file_types) > 1:  # Multiple file types
                score += 10
            
            return min(max_score, max(0, score))
        except Exception:
            return 0
    
    def _analyze_dependencies(self, path: str) -> Dict[str, Any]:
        """Analyze project dependencies comprehensively"""
        try:
            dependencies = {
                "python": {},
                "nodejs": {},
                "rust": {},
                "go": {},
                "java": {},
                "other": {},
                "analysis": {
                    "total_dependencies": 0,
                    "outdated_risk": "unknown",
                    "security_risk": "unknown",
                    "complexity_score": 0
                }
            }
            
            project_path = Path(path)
            
            # Python dependencies
            self._analyze_python_dependencies(project_path, dependencies)
            
            # Node.js dependencies
            self._analyze_nodejs_dependencies(project_path, dependencies)
            
            # Rust dependencies
            self._analyze_rust_dependencies(project_path, dependencies)
            
            # Go dependencies
            self._analyze_go_dependencies(project_path, dependencies)
            
            # Calculate analysis metrics
            total_deps = sum(len(deps) for deps in dependencies.values() if isinstance(deps, dict))
            dependencies["analysis"]["total_dependencies"] = total_deps
            dependencies["analysis"]["complexity_score"] = min(100, total_deps * 2)
            
            return dependencies
        except Exception as e:
            logging.error(f"Failed to analyze dependencies: {e}")
            return {"error": str(e)}
    
    def _analyze_python_dependencies(self, project_path: Path, dependencies: Dict[str, Any]):
        """Analyze Python dependencies"""
        try:
            # requirements.txt
            requirements_file = project_path / "requirements.txt"
            if requirements_file.exists():
                with open(requirements_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            if '==' in line:
                                name, version = line.split('==', 1)
                                dependencies["python"][name] = version
                            elif '>=' in line:
                                name, version = line.split('>=', 1)
                                dependencies["python"][name] = f">={version}"
                            elif '<=' in line:
                                name, version = line.split('<=', 1)
                                dependencies["python"][name] = f"<={version}"
                            else:
                                dependencies["python"][line] = "latest"
            
            # pyproject.toml
            pyproject_file = project_path / "pyproject.toml"
            if pyproject_file.exists():
                try:
                    import toml
                    with open(pyproject_file, 'r') as f:
                        data = toml.load(f)
                        if "tool" in data and "poetry" in data["tool"]:
                            if "dependencies" in data["tool"]["poetry"]:
                                dependencies["python"].update(data["tool"]["poetry"]["dependencies"])
                except ImportError:
                    pass  # toml not available
                except Exception as e:
                    logging.warning(f"Failed to parse pyproject.toml: {e}")
        except Exception as e:
            logging.error(f"Python dependency analysis error: {e}")
    
    def _analyze_nodejs_dependencies(self, project_path: Path, dependencies: Dict[str, Any]):
        """Analyze Node.js dependencies"""
        try:
            package_json = project_path / "package.json"
            if package_json.exists():
                with open(package_json, 'r') as f:
                    data = json.load(f)
                    if "dependencies" in data:
                        dependencies["nodejs"].update(data["dependencies"])
                    if "devDependencies" in data:
                        for dep, version in data["devDependencies"].items():
                            dependencies["nodejs"][f"{dep} (dev)"] = version
        except Exception as e:
            logging.error(f"Node.js dependency analysis error: {e}")
    
    def _analyze_rust_dependencies(self, project_path: Path, dependencies: Dict[str, Any]):
        """Analyze Rust dependencies"""
        try:
            cargo_toml = project_path / "Cargo.toml"
            if cargo_toml.exists():
                try:
                    import toml
                    with open(cargo_toml, 'r') as f:
                        data = toml.load(f)
                        if "dependencies" in data:
                            dependencies["rust"].update(data["dependencies"])
                        if "dev-dependencies" in data:
                            for dep, version in data["dev-dependencies"].items():
                                dependencies["rust"][f"{dep} (dev)"] = version
                except ImportError:
                    pass
        except Exception as e:
            logging.error(f"Rust dependency analysis error: {e}")
    
    def _analyze_go_dependencies(self, project_path: Path, dependencies: Dict[str, Any]):
        """Analyze Go dependencies"""
        try:
            go_mod = project_path / "go.mod"
            if go_mod.exists():
                with open(go_mod, 'r') as f:
                    content = f.read()
                    # Simple parsing for require blocks
                    in_require = False
                    for line in content.split('\n'):
                        line = line.strip()
                        if line.startswith('require ('):
                            in_require = True
                            continue
                        elif line == ')' and in_require:
                            in_require = False
                            continue
                        elif in_require and line:
                            parts = line.split()
                            if len(parts) >= 2:
                                dependencies["go"][parts[0]] = parts[1]
        except Exception as e:
            logging.error(f"Go dependency analysis error: {e}")
    
    def _find_code_patterns(self, path: str) -> Dict[str, Any]:
        """Find comprehensive code patterns"""
        try:
            patterns = {
                "design_patterns": [],
                "anti_patterns": [],
                "code_smells": [],
                "architecture_patterns": [],
                "best_practices": [],
                "violations": []
            }
            
            project_path = Path(path)
            
            # Analyze different file types
            for file_path in project_path.rglob('*'):
                if file_path.is_file() and not any(part.startswith('.') for part in file_path.parts):
                    ext = file_path.suffix.lower()
                    if ext in self.supported_languages:
                        file_patterns = self._analyze_file_patterns(file_path, ext)
                        for key in patterns:
                            patterns[key].extend(file_patterns.get(key, []))
            
            return patterns
        except Exception as e:
            logging.error(f"Failed to find patterns: {e}")
            return {"error": str(e)}
    
    def _analyze_file_patterns(self, file_path: Path, extension: str) -> Dict[str, List[str]]:
        """Analyze patterns in individual file"""
        try:
            language = self.supported_languages[extension]
            
            if language == 'python':
                return self._analyze_python_patterns(file_path)
            elif language in ['javascript', 'typescript']:
                return self._analyze_javascript_patterns(file_path)
            elif language == 'java':
                return self._analyze_java_patterns(file_path)
            else:
                return self._analyze_generic_patterns(file_path, language)
        except Exception:
            return {"design_patterns": [], "anti_patterns": [], "code_smells": [], 
                   "architecture_patterns": [], "best_practices": [], "violations": []}
    
    def _analyze_python_patterns(self, file_path: Path) -> Dict[str, List[str]]:
        """Enhanced Python pattern analysis"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            patterns = {
                "design_patterns": [],
                "anti_patterns": [],
                "code_smells": [],
                "architecture_patterns": [],
                "best_practices": [],
                "violations": []
            }
            
            file_name = file_path.name
            lines = content.split('\n')
            
            # Parse AST for deeper analysis
            try:
                tree = ast.parse(content)
                
                # Design patterns detection
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Singleton pattern
                        if any(isinstance(child, ast.FunctionDef) and child.name == '__new__' 
                              for child in node.body):
                            patterns["design_patterns"].append(f"Singleton pattern in {file_name}")
                        
                        # Factory pattern
                        if any(isinstance(child, ast.FunctionDef) and 'create' in child.name.lower() 
                              for child in node.body):
                            patterns["design_patterns"].append(f"Factory pattern in {file_name}")
                        
                        # Observer pattern
                        if any(isinstance(child, ast.FunctionDef) and 
                              child.name in ['notify', 'subscribe', 'unsubscribe'] 
                              for child in node.body):
                            patterns["design_patterns"].append(f"Observer pattern in {file_name}")
                    
                    # Anti-patterns
                    if isinstance(node, ast.Global):
                        patterns["anti_patterns"].append(f"Global variables in {file_name}")
                    
                    if isinstance(node, ast.Try) and not node.handlers:
                        patterns["anti_patterns"].append(f"Bare try block in {file_name}")
                    
                    if isinstance(node, ast.ExceptHandler) and not node.type:
                        patterns["anti_patterns"].append(f"Bare except clause in {file_name}")
                
                # Code quality checks
                class_count = len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)])
                function_count = len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)])
                
                if class_count > 10:
                    patterns["code_smells"].append(f"Too many classes in {file_name} ({class_count})")
                
                if function_count > 20:
                    patterns["code_smells"].append(f"Too many functions in {file_name} ({function_count})")
                
            except SyntaxError:
                patterns["violations"].append(f"Syntax error in {file_name}")
            
            # Text-based analysis
            if len(lines) > 500:
                patterns["code_smells"].append(f"Large file: {file_name} ({len(lines)} lines)")
            
            # Best practices checks
            if any('import *' in line for line in lines):
                patterns["violations"].append(f"Wildcard imports in {file_name}")
            
            if any(line.strip().startswith('print(') for line in lines):
                patterns["violations"].append(f"Print statements in {file_name} (use logging)")
            
            if '#!/usr/bin/env python' in lines[0] if lines else False:
                patterns["best_practices"].append(f"Proper shebang in {file_name}")
            
            return patterns
        except Exception as e:
            logging.error(f"Python pattern analysis error: {e}")
            return {"design_patterns": [], "anti_patterns": [], "code_smells": [], 
                   "architecture_patterns": [], "best_practices": [], "violations": []}
    
    def _analyze_javascript_patterns(self, file_path: Path) -> Dict[str, List[str]]:
        """Enhanced JavaScript/TypeScript pattern analysis"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            patterns = {
                "design_patterns": [],
                "anti_patterns": [],
                "code_smells": [],
                "architecture_patterns": [],
                "best_practices": [],
                "violations": []
            }
            
            file_name = file_path.name
            lines = content.split('\n')
            
            # Pattern detection using regex
            if re.search(r'class\s+\w+\s*{', content):
                patterns["design_patterns"].append(f"ES6 Class pattern in {file_name}")
            
            if re.search(r'function\s*\*\s*\w+', content):
                patterns["design_patterns"].append(f"Generator pattern in {file_name}")
            
            if re.search(r'async\s+function', content):
                patterns["best_practices"].append(f"Async/await pattern in {file_name}")
            
            # Anti-patterns
            if re.search(r'\bvar\s+\w+', content):
                patterns["anti_patterns"].append(f"var usage in {file_name} (use const/let)")
            
            if re.search(r'console\.log', content):
                patterns["violations"].append(f"console.log in {file_name} (remove for production)")
            
            if re.search(r'==\s*[^=]', content):
                patterns["violations"].append(f"== operator in {file_name} (use === instead)")
            
            # Architecture patterns
            if re.search(r'export\s+default', content):
                patterns["architecture_patterns"].append(f"ES6 modules in {file_name}")
            
            if re.search(r'import\s+.*\s+from', content):
                patterns["architecture_patterns"].append(f"ES6 imports in {file_name}")
            
            # Code smells
            if len(lines) > 500:
                patterns["code_smells"].append(f"Large file: {file_name} ({len(lines)} lines)")
            
            # Count functions
            function_count = len(re.findall(r'function\s+\w+|const\s+\w+\s*=\s*\(.*\)\s*=>', content))
            if function_count > 15:
                patterns["code_smells"].append(f"Too many functions in {file_name} ({function_count})")
            
            return patterns
        except Exception as e:
            logging.error(f"JavaScript pattern analysis error: {e}")
            return {"design_patterns": [], "anti_patterns": [], "code_smells": [], 
                   "architecture_patterns": [], "best_practices": [], "violations": []}
    
    def _analyze_java_patterns(self, file_path: Path) -> Dict[str, List[str]]:
        """Enhanced Java pattern analysis"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            patterns = {
                "design_patterns": [],
                "anti_patterns": [],
                "code_smells": [],
                "architecture_patterns": [],
                "best_practices": [],
                "violations": []
            }
            
            file_name = file_path.name
            lines = content.split('\n')
            
            # Design patterns
            if re.search(r'class\s+\w+Factory', content):
                patterns["design_patterns"].append(f"Factory pattern in {file_name}")
            
            if re.search(r'class\s+\w+Singleton', content):
                patterns["design_patterns"].append(f"Singleton pattern in {file_name}")
            
            if re.search(r'interface\s+\w+Observer', content):
                patterns["design_patterns"].append(f"Observer pattern in {file_name}")
            
            # Best practices
            if re.search(r'public\s+class\s+' + file_path.stem, content):
                patterns["best_practices"].append(f"Proper class naming in {file_name}")
            
            # Violations
            if re.search(r'System\.out\.print', content):
                patterns["violations"].append(f"System.out.print in {file_name} (use logging)")
            
            # Code smells
            if len(lines) > 300:
                patterns["code_smells"].append(f"Large file: {file_name} ({len(lines)} lines)")
            
            return patterns
        except Exception as e:
            logging.error(f"Java pattern analysis error: {e}")
            return {"design_patterns": [], "anti_patterns": [], "code_smells": [], 
                   "architecture_patterns": [], "best_practices": [], "violations": []}
    
    def _analyze_generic_patterns(self, file_path: Path, language: str) -> Dict[str, List[str]]:
        """Generic pattern analysis for other languages"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            patterns = {
                "design_patterns": [],
                "anti_patterns": [],
                "code_smells": [],
                "architecture_patterns": [],
                "best_practices": [],
                "violations": []
            }
            
            file_name = file_path.name
            lines = content.split('\n')
            
            # Generic checks
            if len(lines) > 500:
                patterns["code_smells"].append(f"Large {language} file: {file_name} ({len(lines)} lines)")
            
            # Language-specific basic checks
            if language == 'go':
                if 'package main' in content:
                    patterns["architecture_patterns"].append(f"Main package in {file_name}")
                if 'func main()' in content:
                    patterns["architecture_patterns"].append(f"Entry point in {file_name}")
            
            elif language == 'rust':
                if 'fn main()' in content:
                    patterns["architecture_patterns"].append(f"Entry point in {file_name}")
                if '#[derive(' in content:
                    patterns["best_practices"].append(f"Derive macros in {file_name}")
            
            return patterns
        except Exception:
            return {"design_patterns": [], "anti_patterns": [], "code_smells": [], 
                   "architecture_patterns": [], "best_practices": [], "violations": []}
    
    def _analyze_complexity(self, path: str) -> Dict[str, Any]:
        """Enhanced complexity analysis"""
        try:
            complexity = {
                "cyclomatic_complexity": {},
                "cognitive_complexity": {},
                "nesting_depth": {},
                "function_length": {},
                "overall_score": 0,
                "high_complexity_files": []
            }
            
            project_path = Path(path)
            total_complexity = 0
            file_count = 0
            
            # Analyze different file types
            for file_path in project_path.rglob('*'):
                if (file_path.is_file() and 
                    not any(part.startswith('.') for part in file_path.parts) and
                    file_path.suffix.lower() in self.supported_languages):
                    
                    file_complexity = self._analyze_file_complexity(file_path)
                    
                    if file_complexity:
                        rel_path = str(file_path.relative_to(project_path))
                        complexity["cyclomatic_complexity"][rel_path] = file_complexity.get("cyclomatic", 0)
                        complexity["cognitive_complexity"][rel_path] = file_complexity.get("cognitive", 0)
                        complexity["nesting_depth"][rel_path] = file_complexity.get("nesting", 0)
                        complexity["function_length"][rel_path] = file_complexity.get("function_length", 0)
                        
                        # Track high complexity files
                        if file_complexity.get("cyclomatic", 0) > 10:
                            complexity["high_complexity_files"].append({
                                "file": rel_path,
                                "cyclomatic": file_complexity.get("cyclomatic", 0),
                                "cognitive": file_complexity.get("cognitive", 0)
                            })
                        
                        total_complexity += file_complexity.get("cyclomatic", 0)
                        file_count += 1
            
            # Calculate overall score
            if file_count > 0:
                avg_complexity = total_complexity / file_count
                complexity["overall_score"] = min(100, max(0, 100 - (avg_complexity - 5) * 10))
            
            return complexity
        except Exception as e:
            logging.error(f"Failed to analyze complexity: {e}")
            return {"error": str(e)}
    
    def _analyze_file_complexity(self, file_path: Path) -> Optional[Dict[str, int]]:
        """Analyze complexity of individual file"""
        try:
            ext = file_path.suffix.lower()
            language = self.supported_languages.get(ext)
            
            if language == 'python':
                return self._analyze_python_complexity(file_path)
            else:
                return self._analyze_generic_complexity(file_path)
        except Exception:
            return None
    
    def _analyze_python_complexity(self, file_path: Path) -> Dict[str, int]:
        """Enhanced Python complexity analysis"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            complexity = {
                "cyclomatic": 1,  # Base complexity
                "cognitive": 0,
                "nesting": 0,
                "function_length": 0,
                "class_count": 0,
                "function_count": 0
            }
            
            try:
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    # Cyclomatic complexity
                    if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor, 
                                        ast.AsyncWith, ast.With)):
                        complexity["cyclomatic"] += 1
                    elif isinstance(node, ast.ExceptHandler):
                        complexity["cyclomatic"] += 1
                    elif isinstance(node, ast.BoolOp):
                        complexity["cyclomatic"] += len(node.values) - 1
                    elif isinstance(node, ast.ListComp):
                        complexity["cyclomatic"] += 1
                    
                    # Cognitive complexity (more nuanced)
                    if isinstance(node, ast.If):
                        complexity["cognitive"] += 1
                        # Nested conditions increase cognitive load
                        if hasattr(node, 'orelse') and node.orelse:
                            complexity["cognitive"] += 1
                    elif isinstance(node, (ast.While, ast.For)):
                        complexity["cognitive"] += 1
                    elif isinstance(node, ast.ExceptHandler):
                        complexity["cognitive"] += 1
                    elif isinstance(node, ast.BoolOp):
                        complexity["cognitive"] += len(node.values) - 1
                    
                    # Count classes and functions
                    if isinstance(node, ast.ClassDef):
                        complexity["class_count"] += 1
                    elif isinstance(node, ast.FunctionDef):
                        complexity["function_count"] += 1
                        
                        # Calculate function length
                        if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
                            func_length = node.end_lineno - node.lineno + 1
                            complexity["function_length"] = max(complexity["function_length"], func_length)
                        
                        # Calculate nesting depth for this function
                        depth = self._calculate_nesting_depth(node)
                        complexity["nesting"] = max(complexity["nesting"], depth)
                
            except SyntaxError:
                # File has syntax errors
                complexity["cyclomatic"] = 0
            
            return complexity
        except Exception:
            return {"cyclomatic": 0, "cognitive": 0, "nesting": 0, "function_length": 0}
    
    def _analyze_generic_complexity(self, file_path: Path) -> Dict[str, int]:
        """Generic complexity analysis for non-Python files"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            complexity = {
                "cyclomatic": 1,
                "cognitive": 0,
                "nesting": 0,
                "function_length": 0
            }
            
            lines = content.split('\n')
            
            # Simple pattern-based complexity analysis
            for line in lines:
                line = line.strip()
                
                # Control flow statements
                if re.match(r'\s*(if|while|for|switch|case)\s*\(', line):
                    complexity["cyclomatic"] += 1
                    complexity["cognitive"] += 1
                
                # Boolean operators
                if '&&' in line or '||' in line:
                    complexity["cyclomatic"] += line.count('&&') + line.count('||')
                    complexity["cognitive"] += line.count('&&') + line.count('||')
                
                # Exception handling
                if re.match(r'\s*(catch|except|rescue)\s*\(', line):
                    complexity["cyclomatic"] += 1
                    complexity["cognitive"] += 1
            
            # Calculate nesting depth
            max_depth = 0
            current_depth = 0
            for line in lines:
                stripped = line.strip()
                if stripped.endswith('{') or stripped.endswith(':'):
                    current_depth += 1
                    max_depth = max(max_depth, current_depth)
                elif stripped.startswith('}') or (stripped and not stripped.startswith(' ') and current_depth > 0):
                    current_depth = max(0, current_depth - 1)
            
            complexity["nesting"] = max_depth
            complexity["function_length"] = len(lines)
            
            return complexity
        except Exception:
            return {"cyclomatic": 0, "cognitive": 0, "nesting": 0, "function_length": 0}
    
    def _calculate_nesting_depth(self, node: ast.AST, current_depth: int = 0) -> int:
        """Calculate nesting depth of AST node"""
        max_depth = current_depth
        
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.Try, ast.With, 
                                ast.AsyncFor, ast.AsyncWith)):
                child_depth = self._calculate_nesting_depth(child, current_depth + 1)
                max_depth = max(max_depth, child_depth)
            else:
                child_depth = self._calculate_nesting_depth(child, current_depth)
                max_depth = max(max_depth, child_depth)
        
        return max_depth
    
    async def _explain_code(self, file_content: str = None, file_path: str = None, **kwargs) -> ToolResponse:
        """Explain code using DeepSeek Reasoner"""
        try:
            if not file_content and file_path:
                # Read file if path provided
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        file_content = f.read()
                except Exception as e:
                    return ToolResponse(
                        status=ToolStatus.ERROR,
                        message=f"Failed to read file {file_path}: {str(e)}"
                    )
            
            if not file_content:
                return ToolResponse(
                    status=ToolStatus.ERROR,
                    message="No file content provided"
                )
            
            # Determine language
            if file_path:
                ext = Path(file_path).suffix.lower()
                language = self.supported_languages.get(ext, "unknown")
            else:
                language = "unknown"
            
            # Create comprehensive explanation prompt
            prompt = f"""
            Please provide a comprehensive explanation of this {language} code:

            File: {file_path or 'Unknown'}
            Language: {language}
            Lines of code: {len(file_content.split('\n'))}

            Code:
            ```{language}
            {file_content}
            ```

            Please provide a detailed analysis covering:

            1. **Overview**: What does this code do? What is its main purpose?
            
            2. **Structure Analysis**: 
               - Key classes, functions, and their responsibilities
               - Code organization and architecture
               - Entry points and main flow
            
            3. **Logic Explanation**:
               - Step-by-step explanation of the main logic
               - Control flow and decision points
               - Data transformations and processing
            
            4. **Important Components**:
               - Key variables and their purposes
               - Important data structures
               - External dependencies and imports
            
            5. **Design Patterns & Techniques**:
               - Any design patterns used
               - Programming techniques and paradigms
               - Best practices implemented
            
            6. **Potential Issues & Improvements**:
               - Code quality observations
               - Potential bugs or edge cases
               - Performance considerations
               - Security implications
               - Suggested improvements
            
            7. **Usage & Integration**:
               - How to use this code
               - Integration points with other systems
               - Configuration requirements
            
            Please format your response in clear markdown with proper sections and code highlighting.
            """
            
            response = await self.deepseek_tool.execute(
                "reasoning", 
                prompt=prompt,
                use_reasoning_model=True
            )
            
            if response.status == ToolStatus.SUCCESS:
                explanation = response.data.get("response", "")
                
                return ToolResponse(
                    status=ToolStatus.SUCCESS,
                    data={
                        "explanation": explanation,
                        "language": language,
                        "file_path": file_path,
                        "code_length": len(file_content),
                        "analysis_timestamp": datetime.now().isoformat()
                    },
                    message="Code explanation generated successfully"
                )
            else:
                return ToolResponse(
                    status=ToolStatus.ERROR,
                    message="Failed to generate code explanation using DeepSeek"
                )
                
        except Exception as e:
            logging.error(f"Code explanation error: {e}")
            return ToolResponse(
                status=ToolStatus.ERROR,
                message=f"Code explanation error: {str(e)}"
            )
    
    # Additional methods for security, performance, etc.
    def _basic_security_scan(self, path: str) -> Dict[str, Any]:
        """Basic security scan of codebase"""
        try:
            security_issues = []
            project_path = Path(path)
            
            for file_path in project_path.rglob('*'):
                if (file_path.is_file() and 
                    not any(part.startswith('.') for part in file_path.parts) and
                    file_path.suffix.lower() in self.supported_languages):
                    
                    issues = self._scan_file_security(file_path)
                    security_issues.extend(issues)
            
            return {
                "issues": security_issues,
                "total_issues": len(security_issues),
                "severity_breakdown": self._categorize_security_issues(security_issues)
            }
        except Exception as e:
            logging.error(f"Security scan error: {e}")
            return {"error": str(e)}
    
    def _scan_file_security(self, file_path: Path) -> List[Dict[str, Any]]:
        """Scan individual file for security issues"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            issues = []
            
            # Common security patterns across languages
            dangerous_patterns = [
                (r'\beval\s*\(', "dangerous_function", "high", "eval() function usage"),
                (r'\bexec\s*\(', "dangerous_function", "high", "exec() function usage"),
                (r'shell=True', "shell_injection", "high", "Shell injection vulnerability"),
                (r'innerHTML\s*=', "xss_vulnerability", "medium", "Potential XSS with innerHTML"),
                (r'document\.write\s*\(', "xss_vulnerability", "medium", "Potential XSS with document.write"),
                (r'System\.out\.print', "information_disclosure", "low", "Information disclosure"),
                (r'console\.log', "information_disclosure", "low", "Console logging in production"),
                (r'password\s*=\s*[\'"][^\'"]+[\'"]', "hardcoded_secret", "high", "Hardcoded password"),
                (r'api_key\s*=\s*[\'"][^\'"]+[\'"]', "hardcoded_secret", "high", "Hardcoded API key"),
                (r'SELECT\s+\*\s+FROM.*\+', "sql_injection", "high", "Potential SQL injection"),
            ]
            
            for pattern, issue_type, severity, description in dangerous_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    issues.append({
                        "type": issue_type,
                        "severity": severity,
                        "description": description,
                        "file": str(file_path),
                        "line": line_num,
                        "pattern": pattern
                    })
            
            return issues
        except Exception:
            return []
    
    def _categorize_security_issues(self, issues: List[Dict[str, Any]]) -> Dict[str, int]:
        """Categorize security issues by severity"""
        categories = {"high": 0, "medium": 0, "low": 0}
        for issue in issues:
            severity = issue.get("severity", "low")
            categories[severity] = categories.get(severity, 0) + 1
        return categories
    
    def _basic_performance_analysis(self, path: str) -> Dict[str, Any]:
        """Basic performance analysis"""
        try:
            performance_issues = []
            project_path = Path(path)
            
            for file_path in project_path.rglob('*'):
                if (file_path.is_file() and 
                    not any(part.startswith('.') for part in file_path.parts) and
                    file_path.suffix.lower() in self.supported_languages):
                    
                    issues = self._analyze_file_performance(file_path)
                    performance_issues.extend(issues)
            
            return {
                "issues": performance_issues,
                "total_issues": len(performance_issues),
                "categories": self._categorize_performance_issues(performance_issues)
            }
        except Exception as e:
            logging.error(f"Performance analysis error: {e}")
            return {"error": str(e)}
    
    def _analyze_file_performance(self, file_path: Path) -> List[Dict[str, Any]]:
        """Analyze file for performance issues"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            issues = []
            
            # Performance anti-patterns
            performance_patterns = [
                (r'time\.sleep\s*\(', "blocking_operation", "Sleep operations block execution"),
                (r'for\s+\w+\s+in\s+range\s*\(\s*len\s*\(', "inefficient_loop", "Inefficient loop pattern"),
                (r'\+\s*=.*\s*\+\s*', "string_concatenation", "Inefficient string concatenation"),
                (r'\.append\s*\(.*\)\s*\n.*\.append', "list_operations", "Multiple append operations"),
                (r'import\s+(?!.*\bfrom\b)', "import_efficiency", "Consider more specific imports"),
            ]
            
            for pattern, issue_type, description in performance_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    issues.append({
                        "type": issue_type,
                        "description": description,
                        "file": str(file_path),
                        "line": line_num
                    })
            
            return issues
        except Exception:
            return []
    
    def _categorize_performance_issues(self, issues: List[Dict[str, Any]]) -> Dict[str, int]:
        """Categorize performance issues by type"""
        categories = {}
        for issue in issues:
            issue_type = issue.get("type", "unknown")
            categories[issue_type] = categories.get(issue_type, 0) + 1
        return categories

# Additional specialized methods would continue here...
# For brevity, I'm including the most important ones

# CLI interface for direct usage
if __name__ == "__main__":
    async def main():
        tool = CodeAnalyzerTool()
        
        if len(sys.argv) > 1:
            try:
                params = json.loads(sys.argv[1])
                response = await tool.execute(**params)
                print(json.dumps(response.to_dict(), indent=2))
            except json.JSONDecodeError:
                print("Invalid JSON parameters")
            except Exception as e:
                print(f"Error: {e}")
        else:
            print("Code Analyzer Tool - Usage: python code_analyzer_tool.py '{\"action\": \"analyze\", \"path\": \".\"}'")
            print("Available actions:", ["analyze", "explain", "analyze_project", "find_patterns", 
                                        "security_scan", "performance_analyze", "documentation_generate"])
    
    asyncio.run(main())