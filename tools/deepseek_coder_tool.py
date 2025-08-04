#!/usr/bin/env python3
"""
🚀 DeepSeek Coder Tool - Advanced Code Generation & Analysis
Made by @Lucariolucario55 on Telegram

Features:
- Code generation and completion
- Debugging and error fixing
- Self-healing code
- FIM (Fill-in-Middle) code completion
- Web search integration
- Web scraping with headless browsers
- Code analysis and optimization
- Logic and loop analysis
- Idea and code storage
- Learning from code examples
"""

import asyncio
import json
import logging
import subprocess
import tempfile
import os
import sys
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass
from datetime import datetime
import aiohttp
import requests
from bs4 import BeautifulSoup
import openai
from openai import AsyncOpenAI
from .base_tool import BaseTool, ToolResponse
from config.api_keys import get_deepseek_config

@dataclass
class CodeAnalysis:
    """Code analysis result"""
    language: str
    complexity: float
    issues: List[str]
    suggestions: List[str]
    security_concerns: List[str]
    performance_tips: List[str]

@dataclass
class WebSearchResult:
    """Web search result"""
    title: str
    url: str
    snippet: str
    relevance_score: float
    source: str

class DeepSeekCoderTool(BaseTool):
    """
    Advanced DeepSeek Coder Tool with comprehensive code capabilities
    """
    
    def __init__(self) -> Any:
        """Initialize DeepSeek Coder Tool"""
        super().__init__(
            name="DeepSeek Coder",
            description="Advanced code generation, debugging, and analysis with web search integration",
            capabilities=[
                "code_generation",
                "code_debugging",
                "self_healing",
                "fim_completion",
                "web_search",
                "web_scraping",
                "code_analysis",
                "logic_analysis",
                "idea_storage",
                "code_learning"
            ]
        )
        
        # Get DeepSeek configuration
        self.config = get_deepseek_config()
        self.api_key = self.config["api_key"]
        self.base_url = self.config["base_url"]
        
        # Initialize OpenAI client
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        # Code storage and learning
        self.code_examples = {}
        self.ideas_database = {}
        self.debugging_patterns = {}
        
        # Web search configuration
        self.search_engines = {
            "duckduckgo": "https://api.duckduckgo.com/",
            "google": "https://www.google.com/search",
            "bing": "https://www.bing.com/search"
        }
        
        # Supported programming languages
        self.supported_languages = [
            "python", "javascript", "typescript", "java", "cpp", "csharp",
            "go", "rust", "php", "ruby", "swift", "kotlin", "scala",
            "html", "css", "sql", "bash", "powershell", "yaml", "json"
        ]
        
        # Initialize session
        self.session = None
        self.is_initialized = False
    
    async def initialize(self) -> Any:
        """Initialize the tool"""
        try:
            # Create aiohttp session for web requests
            self.session = aiohttp.ClientSession()
            
            # Load existing code examples and ideas
            await self._load_code_examples()
            await self._load_ideas_database()
            
            self.is_initialized = True
            logging.info("✅ DeepSeek Coder Tool initialized successfully")
            
        except Exception as e:
            logging.error(f"❌ Failed to initialize DeepSeek Coder Tool: {str(e)}")
            raise
    
    async def execute(self, **kwargs) -> ToolResponse:
        """Execute DeepSeek Coder operations"""
        operation = kwargs.get("operation", "code_generation")
        
        try:
            if operation == "code_generation":
                return await self.generate_code(**kwargs)
            elif operation == "code_debugging":
                return await self.debug_code(**kwargs)
            elif operation == "self_healing":
                return await self.self_heal_code(**kwargs)
            elif operation == "fim_completion":
                return await self.fim_complete(**kwargs)
            elif operation == "web_search":
                return await self.web_search(**kwargs)
            elif operation == "web_scraping":
                return await self.web_scrape(**kwargs)
            elif operation == "code_analysis":
                return await self.analyze_code(**kwargs)
            elif operation == "logic_analysis":
                return await self.analyze_logic(**kwargs)
            elif operation == "store_idea":
                return await self.store_idea(**kwargs)
            elif operation == "store_code":
                return await self.store_code_example(**kwargs)
            elif operation == "learn_from_code":
                return await self.learn_from_code(**kwargs)
            elif operation == "run_code":
                return await self.run_code(**kwargs)
            else:
                return ToolResponse(
                    success=False,
                    message=f"Unknown operation: {operation}",
                    data={}
                )
                
        except Exception as e:
            return await self._handle_error(e, operation)
    
    async def generate_code(self, **kwargs) -> ToolResponse:
        """Generate code based on requirements"""
        prompt = kwargs.get("prompt", "")
        language = kwargs.get("language", "python")
        context = kwargs.get("context", "")
        requirements = kwargs.get("requirements", [])
        
        # Build comprehensive prompt
        full_prompt = f"""
You are an expert {language} programmer. Generate high-quality, production-ready code.

Requirements:
{prompt}

Additional Requirements:
{chr(10).join(f"- {req}" for req in requirements)}

Context:
{context}

Generate complete, working code with:
1. Proper error handling
2. Documentation and comments
3. Best practices
4. Performance optimization
5. Security considerations

Code:
"""
        
        try:
            response = await self.client.chat.completions.create(
                model="deepseek-coder",
                messages=[
                    {"role": "system", "content": "You are an expert programmer. Generate only code with minimal explanation."},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            code = response.choices[0].message.content
            
            # Store the generated code
            await self.store_code_example(
                code=code,
                language=language,
                description=prompt,
                tags=["generated", language]
            )
            
            return ToolResponse(
                success=True,
                message="Code generated successfully",
                data={
                    "code": code,
                    "language": language,
                    "analysis": await self.analyze_code_internal(code, language)
                }
            )
            
        except Exception as e:
            return await self._handle_error(e, "code_generation")
    
    async def debug_code(self, **kwargs) -> ToolResponse:
        """Debug and fix code issues"""
        code = kwargs.get("code", "")
        language = kwargs.get("language", "python")
        error_message = kwargs.get("error_message", "")
        context = kwargs.get("context", "")
        
        # Build debugging prompt
        debug_prompt = f"""
You are an expert {language} debugger. Fix the following code:

Code with issues:
```{language}
{code}
```

Error message:
{error_message}

Context:
{context}

Please:
1. Identify the issues
2. Explain what's wrong
3. Provide the corrected code
4. Add error handling if needed
5. Optimize the code

Fixed code:
"""
        
        try:
            response = await self.client.chat.completions.create(
                model="deepseek-coder",
                messages=[
                    {"role": "system", "content": "You are an expert debugger. Provide detailed analysis and fixed code."},
                    {"role": "user", "content": debug_prompt}
                ],
                temperature=0.2,
                max_tokens=4000
            )
            
            fixed_code = response.choices[0].message.content
            
            # Store debugging pattern
            await self._store_debugging_pattern(
                original_code=code,
                fixed_code=fixed_code,
                error_message=error_message,
                language=language
            )
            
            return ToolResponse(
                success=True,
                message="Code debugged successfully",
                data={
                    "original_code": code,
                    "fixed_code": fixed_code,
                    "issues_found": await self._extract_issues(response.choices[0].message.content),
                    "language": language
                }
            )
            
        except Exception as e:
            return await self._handle_error(e, "code_debugging")
    
    async def self_heal_code(self, **kwargs) -> ToolResponse:
        """Self-healing code with automatic fixes"""
        code = kwargs.get("code", "")
        language = kwargs.get("language", "python")
        
        # First, analyze the code for potential issues
        analysis = await self.analyze_code_internal(code, language)
        
        if not analysis.issues:
            return ToolResponse(
                success=True,
                message="No issues found in code",
                data={"code": code, "analysis": analysis}
            )
        
        # Build self-healing prompt
        heal_prompt = f"""
You are an expert {language} programmer with self-healing capabilities. 
Automatically fix the following code issues:

Code:
```{language}
{code}
```

Issues detected:
{chr(10).join(f"- {issue}" for issue in analysis.issues)}

Suggestions:
{chr(10).join(f"- {suggestion}" for suggestion in analysis.suggestions)}

Please provide the self-healed code with:
1. All issues fixed
2. Improved performance
3. Better error handling
4. Enhanced security
5. Cleaner code structure

Self-healed code:
"""
        
        try:
            response = await self.client.chat.completions.create(
                model="deepseek-coder",
                messages=[
                    {"role": "system", "content": "You are a self-healing code system. Provide only the fixed code."},
                    {"role": "user", "content": heal_prompt}
                ],
                temperature=0.1,
                max_tokens=4000
            )
            
            healed_code = response.choices[0].message.content
            
            return ToolResponse(
                success=True,
                message="Code self-healed successfully",
                data={
                    "original_code": code,
                    "healed_code": healed_code,
                    "issues_fixed": analysis.issues,
                    "improvements": analysis.suggestions,
                    "language": language
                }
            )
            
        except Exception as e:
            return await self._handle_error(e, "self_healing")
    
    async def fim_complete(self, **kwargs) -> ToolResponse:
        """Fill-in-Middle code completion"""
        prefix = kwargs.get("prefix", "")
        suffix = kwargs.get("suffix", "")
        language = kwargs.get("language", "python")
        
        fim_prompt = f"""
Complete the code between the prefix and suffix:

Prefix:
```{language}
{prefix}
```

Suffix:
```{language}
{suffix}
```

Generate the missing code that fits perfectly between prefix and suffix.
Consider:
1. Variable scope and context
2. Function signatures
3. Logic flow
4. Error handling
5. Best practices

Missing code:
"""
        
        try:
            response = await self.client.chat.completions.create(
                model="deepseek-coder",
                messages=[
                    {"role": "system", "content": "You are an expert at FIM completion. Generate only the missing code."},
                    {"role": "user", "content": fim_prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            completion = response.choices[0].message.content
            
            return ToolResponse(
                success=True,
                message="FIM completion successful",
                data={
                    "prefix": prefix,
                    "completion": completion,
                    "suffix": suffix,
                    "full_code": prefix + completion + suffix,
                    "language": language
                }
            )
            
        except Exception as e:
            return await self._handle_error(e, "fim_completion")
    
    async def web_search(self, **kwargs) -> ToolResponse:
        """Web search using DuckDuckGo and other engines"""
        query = kwargs.get("query", "")
        engine = kwargs.get("engine", "duckduckgo")
        max_results = kwargs.get("max_results", 10)
        
        try:
            if engine == "duckduckgo":
                results = await self._duckduckgo_search(query, max_results)
            elif engine == "google":
                results = await self._google_search(query, max_results)
            else:
                results = await self._duckduckgo_search(query, max_results)
            
            return ToolResponse(
                success=True,
                message=f"Web search completed with {len(results)} results",
                data={
                    "query": query,
                    "engine": engine,
                    "results": results,
                    "total_results": len(results)
                }
            )
            
        except Exception as e:
            return await self._handle_error(e, "web_search")
    
    async def web_scrape(self, **kwargs) -> ToolResponse:
        """Web scraping with headless browser simulation"""
        url = kwargs.get("url", "")
        selectors = kwargs.get("selectors", {})
        extract_text = kwargs.get("extract_text", True)
        extract_links = kwargs.get("extract_links", True)
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    scraped_data = {}
                    
                    # Extract text content
                    if extract_text:
                        scraped_data["text"] = soup.get_text(separator='\n', strip=True)
                    
                    # Extract links
                    if extract_links:
                        links = []
                        for link in soup.find_all('a', href=True):
                            links.append({
                                "text": link.get_text(strip=True),
                                "url": link['href'],
                                "title": link.get('title', '')
                            })
                        scraped_data["links"] = links
                    
                    # Extract based on selectors
                    for name, selector in selectors.items():
                        elements = soup.select(selector)
                        scraped_data[name] = [elem.get_text(strip=True) for elem in elements]
                    
                    return ToolResponse(
                        success=True,
                        message="Web scraping completed successfully",
                        data={
                            "url": url,
                            "scraped_data": scraped_data,
                            "timestamp": datetime.now().isoformat()
                        }
                    )
                else:
                    return ToolResponse(
                        success=False,
                        message=f"Failed to fetch URL: {response.status}",
                        data={"url": url, "status": response.status}
                    )
                    
        except Exception as e:
            return await self._handle_error(e, "web_scraping")
    
    async def analyze_code(self, **kwargs) -> ToolResponse:
        """Analyze code for issues, complexity, and improvements"""
        code = kwargs.get("code", "")
        language = kwargs.get("language", "python")
        
        analysis = await self.analyze_code_internal(code, language)
        
        return ToolResponse(
            success=True,
            message="Code analysis completed",
            data={
                "analysis": analysis,
                "code": code,
                "language": language
            }
        )
    
    async def analyze_logic(self, **kwargs) -> ToolResponse:
        """Analyze code logic, loops, and algorithms"""
        code = kwargs.get("code", "")
        language = kwargs.get("language", "python")
        
        logic_prompt = f"""
Analyze the logic, loops, and algorithms in this {language} code:

```{language}
{code}
```

Provide detailed analysis of:
1. Algorithm complexity (Big O notation)
2. Loop efficiency and potential optimizations
3. Logic flow and control structures
4. Edge cases and error conditions
5. Performance bottlenecks
6. Alternative approaches
7. Best practices compliance

Analysis:
"""
        
        try:
            response = await self.client.chat.completions.create(
                model="deepseek-coder",
                messages=[
                    {"role": "system", "content": "You are an expert in algorithm analysis and code logic."},
                    {"role": "user", "content": logic_prompt}
                ],
                temperature=0.3,
                max_tokens=3000
            )
            
            analysis = response.choices[0].message.content
            
            return ToolResponse(
                success=True,
                message="Logic analysis completed",
                data={
                    "analysis": analysis,
                    "code": code,
                    "language": language
                }
            )
            
        except Exception as e:
            return await self._handle_error(e, "logic_analysis")
    
    async def store_idea(self, **kwargs) -> ToolResponse:
        """Store programming ideas and concepts"""
        idea = kwargs.get("idea", "")
        category = kwargs.get("category", "general")
        tags = kwargs.get("tags", [])
        priority = kwargs.get("priority", "medium")
        
        idea_id = f"idea_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.ideas_database[idea_id] = {
            "idea": idea,
            "category": category,
            "tags": tags,
            "priority": priority,
            "timestamp": datetime.now().isoformat(),
            "status": "new"
        }
        
        # Save to file
        await self._save_ideas_database()
        
        return ToolResponse(
            success=True,
            message="Idea stored successfully",
            data={
                "idea_id": idea_id,
                "idea": idea,
                "category": category,
                "tags": tags,
                "priority": priority
            }
        )
    
    async def store_code_example(self, **kwargs) -> ToolResponse:
        """Store code examples for learning"""
        code = kwargs.get("code", "")
        language = kwargs.get("language", "python")
        description = kwargs.get("description", "")
        tags = kwargs.get("tags", [])
        
        example_id = f"example_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.code_examples[example_id] = {
            "code": code,
            "language": language,
            "description": description,
            "tags": tags,
            "timestamp": datetime.now().isoformat(),
            "analysis": await self.analyze_code_internal(code, language)
        }
        
        # Save to file
        await self._save_code_examples()
        
        return ToolResponse(
            success=True,
            message="Code example stored successfully",
            data={
                "example_id": example_id,
                "code": code,
                "language": language,
                "description": description,
                "tags": tags
            }
        )
    
    async def learn_from_code(self, **kwargs) -> ToolResponse:
        """Learn patterns and best practices from code"""
        code = kwargs.get("code", "")
        language = kwargs.get("language", "python")
        
        learning_prompt = f"""
Analyze this {language} code and extract learning insights:

```{language}
{code}
```

Extract:
1. Design patterns used
2. Best practices demonstrated
3. Common anti-patterns to avoid
4. Performance optimizations
5. Security considerations
6. Code organization techniques
7. Testing strategies
8. Documentation practices

Learning insights:
"""
        
        try:
            response = await self.client.chat.completions.create(
                model="deepseek-coder",
                messages=[
                    {"role": "system", "content": "You are an expert code reviewer and teacher."},
                    {"role": "user", "content": learning_prompt}
                ],
                temperature=0.3,
                max_tokens=3000
            )
            
            insights = response.choices[0].message.content
            
            # Store the learning insights
            await self.store_idea(
                idea=insights,
                category="learning",
                tags=["code_analysis", language, "best_practices"],
                priority="high"
            )
            
            return ToolResponse(
                success=True,
                message="Learning analysis completed",
                data={
                    "insights": insights,
                    "code": code,
                    "language": language
                }
            )
            
        except Exception as e:
            return await self._handle_error(e, "learn_from_code")
    
    async def run_code(self, **kwargs) -> ToolResponse:
        """Execute code and return results"""
        code = kwargs.get("code", "")
        language = kwargs.get("language", "python")
        input_data = kwargs.get("input_data", "")
        timeout = kwargs.get("timeout", 30)
        
        try:
            if language == "python":
                return await self._run_python_code(code, input_data, timeout)
            elif language == "javascript":
                return await self._run_javascript_code(code, input_data, timeout)
            elif language == "bash":
                return await self._run_bash_code(code, input_data, timeout)
            else:
                return ToolResponse(
                    success=False,
                    message=f"Language {language} not supported for execution",
                    data={"language": language}
                )
                
        except Exception as e:
            return await self._handle_error(e, "run_code")
    
    # Helper methods
    async def analyze_code_internal(self, code: str, language: str) -> CodeAnalysis:
        """Internal code analysis"""
        issues = []
        suggestions = []
        security_concerns = []
        performance_tips = []
        
        # Basic analysis based on language
        if language == "python":
            if "eval(" in code:
                security_concerns.append("Use of eval() is dangerous")
            if "exec(" in code:
                security_concerns.append("Use of exec() is dangerous")
            if "import os" in code and "os.system(" in code:
                security_concerns.append("os.system() can be dangerous")
        
        # Complexity analysis
        complexity = len(code.split('\n')) / 10  # Simple line-based complexity
        
        return CodeAnalysis(
            language=language,
            complexity=complexity,
            issues=issues,
            suggestions=suggestions,
            security_concerns=security_concerns,
            performance_tips=performance_tips
        )
    
    async def _duckduckgo_search(self, query: str, max_results: int) -> List[WebSearchResult]:
        """Search using DuckDuckGo"""
        try:
            # Use DuckDuckGo Instant Answer API
            url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1&skip_disambig=1"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    results = []
                    
                    # Add instant answer if available
                    if data.get("Abstract"):
                        results.append(WebSearchResult(
                            title=data.get("Heading", "DuckDuckGo Result"),
                            url=data.get("AbstractURL", ""),
                            snippet=data.get("Abstract", ""),
                            relevance_score=0.9,
                            source="duckduckgo"
                        ))
                    
                    # Add related topics
                    for topic in data.get("RelatedTopics", [])[:max_results-1]:
                        if isinstance(topic, dict) and topic.get("Text"):
                            results.append(WebSearchResult(
                                title=topic.get("Text", "").split(" - ")[0],
                                url=topic.get("FirstURL", ""),
                                snippet=topic.get("Text", ""),
                                relevance_score=0.7,
                                source="duckduckgo"
                            ))
                    
                    return results[:max_results]
                else:
                    return []
                    
        except Exception as e:
            logging.error(f"DuckDuckGo search failed: {str(e)}")
            return []
    
    async def _google_search(self, query: str, max_results: int) -> List[WebSearchResult]:
        """Search using Google (simplified)"""
        # Note: This is a simplified version. Real Google search requires API key
        try:
            url = f"https://www.google.com/search?q={query}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    results = []
                    for result in soup.select('.g')[:max_results]:
                        title_elem = result.select_one('h3')
                        link_elem = result.select_one('a')
                        snippet_elem = result.select_one('.VwiC3b')
                        
                        if title_elem and link_elem:
                            results.append(WebSearchResult(
                                title=title_elem.get_text(),
                                url=link_elem.get('href', ''),
                                snippet=snippet_elem.get_text() if snippet_elem else '',
                                relevance_score=0.8,
                                source="google"
                            ))
                    
                    return results
                else:
                    return []
                    
        except Exception as e:
            logging.error(f"Google search failed: {str(e)}")
            return []
    
    async def _run_python_code(self, code: str, input_data: str, timeout: int) -> ToolResponse:
        """Run Python code"""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Run the code
            result = subprocess.run(
                [sys.executable, temp_file],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            # Clean up
            os.unlink(temp_file)
            
            return ToolResponse(
                success=result.returncode == 0,
                message="Code execution completed",
                data={
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode,
                    "execution_time": "measured"
                }
            )
            
        except subprocess.TimeoutExpired:
            return ToolResponse(
                success=False,
                message="Code execution timed out",
                data={"timeout": timeout}
            )
        except Exception as e:
            return ToolResponse(
                success=False,
                message=f"Code execution failed: {str(e)}",
                data={"error": str(e)}
            )
    
    async def _run_javascript_code(self, code: str, input_data: str, timeout: int) -> ToolResponse:
        """Run JavaScript code using Node.js"""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Run the code
            result = subprocess.run(
                ["node", temp_file],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            # Clean up
            os.unlink(temp_file)
            
            return ToolResponse(
                success=result.returncode == 0,
                message="Code execution completed",
                data={
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode
                }
            )
            
        except subprocess.TimeoutExpired:
            return ToolResponse(
                success=False,
                message="Code execution timed out",
                data={"timeout": timeout}
            )
        except Exception as e:
            return ToolResponse(
                success=False,
                message=f"Code execution failed: {str(e)}",
                data={"error": str(e)}
            )
    
    async def _run_bash_code(self, code: str, input_data: str, timeout: int) -> ToolResponse:
        """Run Bash code"""
        try:
            result = subprocess.run(
                ["bash", "-c", code],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return ToolResponse(
                success=result.returncode == 0,
                message="Code execution completed",
                data={
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode
                }
            )
            
        except subprocess.TimeoutExpired:
            return ToolResponse(
                success=False,
                message="Code execution timed out",
                data={"timeout": timeout}
            )
        except Exception as e:
            return ToolResponse(
                success=False,
                message=f"Code execution failed: {str(e)}",
                data={"error": str(e)}
            )
    
    async def _store_debugging_pattern(self, original_code: str, fixed_code: str, error_message: str, language: str):
    """_store_debugging_pattern function."""
        """Store debugging patterns for learning"""
        pattern_id = f"debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.debugging_patterns[pattern_id] = {
            "original_code": original_code,
            "fixed_code": fixed_code,
            "error_message": error_message,
            "language": language,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save to file
        await self._save_debugging_patterns()
    
    async def _extract_issues(self, response_text: str) -> List[str]:
        """Extract issues from response text"""
        issues = []
        lines = response_text.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['error', 'issue', 'problem', 'bug', 'fix']):
                issues.append(line.strip())
        
        return issues
    
    async def _load_code_examples(self) -> Any:
        """Load code examples from file"""
        try:
            examples_file = Path("data/code_examples.json")
            if examples_file.exists():
                with open(examples_file, 'r') as f:
                    self.code_examples = json.load(f)
        except Exception as e:
            logging.warning(f"Could not load code examples: {str(e)}")
    
    async def _save_code_examples(self) -> Any:
        """Save code examples to file"""
        try:
            examples_file = Path("data/code_examples.json")
            examples_file.parent.mkdir(parents=True, exist_ok=True)
            with open(examples_file, 'w') as f:
                json.dump(self.code_examples, f, indent=2)
        except Exception as e:
            logging.error(f"Could not save code examples: {str(e)}")
    
    async def _load_ideas_database(self) -> Any:
        """Load ideas database from file"""
        try:
            ideas_file = Path("data/ideas_database.json")
            if ideas_file.exists():
                with open(ideas_file, 'r') as f:
                    self.ideas_database = json.load(f)
        except Exception as e:
            logging.warning(f"Could not load ideas database: {str(e)}")
    
    async def _save_ideas_database(self) -> Any:
        """Save ideas database to file"""
        try:
            ideas_file = Path("data/ideas_database.json")
            ideas_file.parent.mkdir(parents=True, exist_ok=True)
            with open(ideas_file, 'w') as f:
                json.dump(self.ideas_database, f, indent=2)
        except Exception as e:
            logging.error(f"Could not save ideas database: {str(e)}")
    
    async def _save_debugging_patterns(self) -> Any:
        """Save debugging patterns to file"""
        try:
            patterns_file = Path("data/debugging_patterns.json")
            patterns_file.parent.mkdir(parents=True, exist_ok=True)
            with open(patterns_file, 'w') as f:
                json.dump(self.debugging_patterns, f, indent=2)
        except Exception as e:
            logging.error(f"Could not save debugging patterns: {str(e)}")
    
    async def _handle_error(self, error: Exception, operation: str) -> ToolResponse:
        """Handle errors in tool operations"""
        logging.error(f"Error in {operation}: {str(error)}")
        return ToolResponse(
            success=False,
            message=f"Operation '{operation}' failed: {str(error)}",
            data={"error": str(error), "operation": operation}
        )
    
    def get_schema(self) -> Dict[str, Any]:
        """Get tool schema"""
        return {
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "supported_languages": self.supported_languages,
            "search_engines": list(self.search_engines.keys()),
            "operations": [
                "code_generation",
                "code_debugging",
                "self_healing",
                "fim_completion",
                "web_search",
                "web_scraping",
                "code_analysis",
                "logic_analysis",
                "store_idea",
                "store_code",
                "learn_from_code",
                "run_code"
            ]
        } 