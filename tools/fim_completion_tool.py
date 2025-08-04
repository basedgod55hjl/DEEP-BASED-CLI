"""
FIM Completion Tool - Enhanced BASED GOD CLI
Fill-in-Middle completion for code using DeepSeek
"""

from typing import Any, Dict, Optional
import openai
from .base_tool import BaseTool, ToolResponse, ToolStatus
from config.api_keys import get_deepseek_config

class FIMCompletionTool(BaseTool):
    """
    Fill-in-Middle completion tool using DeepSeek
    Completes code between prefix and suffix
    """
    
    def __init__(self):
        super().__init__(
            name="FIM Completion Tool",
            description="Fill-in-Middle code completion using DeepSeek's advanced models",
            capabilities=[
                "Complete code between prefix and suffix",
                "Smart context-aware code generation",
                "Support for multiple programming languages",
                "Intelligent indentation and formatting",
                "Function and class completion",
                "Code pattern recognition"
            ]
        )
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """Initialize DeepSeek API client"""
        try:
            # Get DeepSeek configuration
            deepseek_config = get_deepseek_config()
            deepseek_api_key = deepseek_config["api_key"]
            # Use beta API for FIM completion
            deepseek_base_url = "https://api.deepseek.com/beta"
            
            self.client = openai.AsyncOpenAI(
                api_key=deepseek_api_key,
                base_url=deepseek_base_url
            )
            print("✅ FIM Completion Tool initialized successfully")
        except Exception as e:
            print(f"❌ FIM Completion Tool initialization failed: {str(e)}")
            self.client = None
    
    async def execute(self, **kwargs) -> ToolResponse:
        """Execute FIM completion"""
        prefix = kwargs.get("prefix", "")
        suffix = kwargs.get("suffix", "")
        language = kwargs.get("language", "python")
        max_tokens = kwargs.get("max_tokens", 1024)
        temperature = kwargs.get("temperature", 0.3)
        model = kwargs.get("model", "deepseek-coder")
        
        if not prefix:
            return ToolResponse(
                success=False,
                message="Prefix is required for FIM completion",
                status=ToolStatus.FAILED
            )
        
        if not self.client:
            return ToolResponse(
                success=False,
                message="DeepSeek client not initialized",
                status=ToolStatus.FAILED
            )
        
        try:
            # Prepare FIM prompt with language hint
            language_hint = f"# Language: {language}\n" if language else ""
            fim_prompt = f"{language_hint}<PRE>{prefix}<MID>{suffix}<SUF>"
            
            # Execute completion
            response = await self.client.completions.create(
                model=model,
                prompt=fim_prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=["<PRE>", "<MID>", "<SUF>"]
            )
            
            completion = response.choices[0].text
            
            # Clean up the completion
            completion = completion.strip()
            
            # Analyze the completion
            analysis = self._analyze_completion(prefix, completion, suffix, language)
            
            return ToolResponse(
                success=True,
                message="FIM completion generated successfully",
                data={
                    "completion": completion,
                    "full_code": prefix + completion + suffix,
                    "language": language,
                    "model": model,
                    "analysis": analysis
                },
                metadata={
                    "prefix_length": len(prefix),
                    "suffix_length": len(suffix),
                    "completion_length": len(completion),
                    "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else None
                }
            )
            
        except Exception as e:
            return ToolResponse(
                success=False,
                message=f"FIM completion failed: {str(e)}",
                status=ToolStatus.FAILED
            )
    
    def _analyze_completion(self, prefix: str, completion: str, suffix: str, language: str) -> Dict[str, Any]:
        """Analyze the generated completion"""
        analysis = {
            "type": "unknown",
            "features": []
        }
        
        # Detect completion type
        if "def " in completion:
            analysis["type"] = "function"
            analysis["features"].append("function_definition")
        elif "class " in completion:
            analysis["type"] = "class"
            analysis["features"].append("class_definition")
        elif "import " in completion or "from " in completion:
            analysis["type"] = "import"
            analysis["features"].append("import_statement")
        elif "if " in completion or "for " in completion or "while " in completion:
            analysis["type"] = "control_flow"
            analysis["features"].append("control_structure")
        else:
            analysis["type"] = "code_block"
        
        # Check for common patterns
        if "return " in completion:
            analysis["features"].append("return_statement")
        if "try:" in completion:
            analysis["features"].append("exception_handling")
        if "#" in completion and language == "python":
            analysis["features"].append("comments")
        if '"""' in completion or "'''" in completion:
            analysis["features"].append("docstring")
        
        # Check if completion bridges prefix and suffix well
        if prefix.rstrip().endswith(":") and completion.startswith("    "):
            analysis["features"].append("proper_indentation")
        
        return analysis
    
    def get_schema(self) -> Dict[str, Any]:
        """Get parameter schema for FIM completion"""
        return {
            "type": "object",
            "properties": {
                "prefix": {
                    "type": "string",
                    "description": "Code before the completion point"
                },
                "suffix": {
                    "type": "string",
                    "description": "Code after the completion point",
                    "default": ""
                },
                "language": {
                    "type": "string",
                    "description": "Programming language",
                    "enum": ["python", "javascript", "typescript", "java", "cpp", "c", "csharp", "go", "rust", "php", "ruby", "swift"],
                    "default": "python"
                },
                "model": {
                    "type": "string",
                    "description": "Model to use for completion",
                    "enum": ["deepseek-coder", "deepseek-chat"],
                    "default": "deepseek-coder"
                },
                "max_tokens": {
                    "type": "integer",
                    "description": "Maximum tokens to generate",
                    "default": 1024,
                    "minimum": 1,
                    "maximum": 4096
                },
                "temperature": {
                    "type": "number",
                    "description": "Sampling temperature (0.0-1.0)",
                    "default": 0.3,
                    "minimum": 0.0,
                    "maximum": 1.0
                }
            },
            "required": ["prefix"]
        } 