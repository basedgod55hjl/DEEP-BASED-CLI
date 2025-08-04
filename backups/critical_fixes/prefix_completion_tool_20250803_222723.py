"""
Prefix Completion Tool - Enhanced BASED GOD CLI
Prefix-based text and code completion using DeepSeek
"""

from typing import
import logging
 Any, Dict, List, Optional
import openai
from .base_tool import BaseTool, ToolResponse, ToolStatus
from config.api_keys import get_deepseek_config

class PrefixCompletionTool(BaseTool):
    """
    Prefix completion tool using DeepSeek
    Continues text or code from a given prefix
    """
    
    def __init__(self) -> Any:
        super().__init__(
            name="Prefix Completion Tool",
            description="Intelligent text and code continuation using DeepSeek's advanced models",
            capabilities=[
                "Natural text continuation",
                "Code completion from prefix",
                "Context-aware generation",
                "Multi-language support",
                "Story and narrative continuation",
                "Technical documentation completion",
                "Email and message drafting",
                "Creative writing assistance"
            ]
        )
        self.client = None
        self._init_client()
    
    def _init_client(self) -> Any:
        """Initialize DeepSeek API client"""
        try:
            # Get DeepSeek configuration
            deepseek_config = get_deepseek_config()
            deepseek_api_key = deepseek_config["api_key"]
            # Use beta API for prefix completion
            deepseek_base_url = "https://api.deepseek.com/beta"
            
            self.client = openai.AsyncOpenAI(
                api_key=deepseek_api_key,
                base_url=deepseek_base_url
            )
            logging.info("✅ Prefix Completion Tool initialized successfully")
        except Exception as e:
            logging.info(f"❌ Prefix Completion Tool initialization failed: {str(e)}")
            self.client = None
    
    async def execute(self, **kwargs) -> ToolResponse:
        """Execute prefix completion"""
        prefix = kwargs.get("prefix", "")
        mode = kwargs.get("mode", "auto")  # auto, text, code
        max_tokens = kwargs.get("max_tokens", 512)
        temperature = kwargs.get("temperature", 0.7)
        model = kwargs.get("model", "deepseek-chat")
        stop_sequences = kwargs.get("stop", [])
        top_p = kwargs.get("top_p", 0.95)
        
        if not prefix:
            return ToolResponse(
                success=False,
                message="Prefix is required for completion",
                status=ToolStatus.FAILED
            )
        
        if not self.client:
            return ToolResponse(
                success=False,
                message="DeepSeek client not initialized",
                status=ToolStatus.FAILED
            )
        
        try:
            # Detect mode if auto
            if mode == "auto":
                mode = self._detect_mode(prefix)
            
            # Adjust parameters based on mode
            if mode == "code":
                temperature = min(temperature, 0.3)
                model = "deepseek-coder"
                if not stop_sequences:
                    stop_sequences = ["\n\n", "```"]
            
            # Prepare system message based on mode
            system_content = self._get_system_message(mode)
            
            # Execute completion
            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "assistant", "content": prefix, "prefix": True}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stop=stop_sequences if stop_sequences else None
            )
            
            completion = response.choices[0].message.content
            
            # Post-process completion
            completion = self._post_process(completion, mode, prefix)
            
            # Analyze the completion
            analysis = self._analyze_completion(prefix, completion, mode)
            
            return ToolResponse(
                success=True,
                message=f"Prefix completion generated successfully ({mode} mode)",
                data={
                    "completion": completion,
                    "full_text": prefix + completion,
                    "mode": mode,
                    "model": model,
                    "analysis": analysis
                },
                metadata={
                    "prefix_length": len(prefix),
                    "completion_length": len(completion),
                    "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else None,
                    "finish_reason": response.choices[0].finish_reason if response.choices else None
                }
            )
            
        except Exception as e:
            return ToolResponse(
                success=False,
                message=f"Prefix completion failed: {str(e)}",
                status=ToolStatus.FAILED
            )
    
    def _detect_mode(self, prefix: str) -> str:
        """Detect whether the prefix is code or text"""
        code_indicators = [
            "def ", "class ", "import ", "from ", "function ", "const ", "let ", "var ",
            "public ", "private ", "static ", "void ", "int ", "string ", "bool ",
            "{", "}", "(", ")", "[", "]", "=>", "->", "::", "<%", "%>",
            "```", "#!/", "#include", "package ", "using ", "namespace "
        ]
        
        # Count code indicators
        code_score = sum(1 for indicator in code_indicators if indicator in prefix)
        
        # Check for common code patterns
        if any(prefix.strip().startswith(p) for p in ["def", "class", "function", "import", "from", "const", "let", "var"]):
            code_score += 3
        
        # Check for indentation (common in code)
        if "\n    " in prefix or "\n\t" in prefix:
            code_score += 2
        
        # Decide based on score
        return "code" if code_score >= 2 else "text"
    
    def _get_system_message(self, mode: str) -> str:
        """Get appropriate system message based on mode"""
        if mode == "code":
            return (
                "You are an expert programmer. Continue the code naturally, "
                "maintaining the same style, indentation, and conventions. "
                "Focus on completing the current thought or function."
            )
        else:
            return (
                "You are a helpful assistant. Continue the text naturally, "
                "maintaining the same tone, style, and context. "
                "Provide a smooth and coherent continuation."
            )
    
    def _post_process(self, completion: str, mode: str, prefix: str) -> str:
        """Post-process the completion based on mode"""
        if mode == "code":
            # Ensure proper indentation continuation
            if prefix.rstrip().endswith(":"):
                last_line = prefix.split('\n')[-1]
                indent = len(last_line) - len(last_line.lstrip())
                if not completion.startswith('\n'):
                    completion = '\n' + ' ' * (indent + 4) + completion.lstrip()
        
        # Remove any duplicate content from the beginning
        if completion.startswith(prefix[-50:]):
            completion = completion[len(prefix[-50:]):]
        
        return completion
    
    def _analyze_completion(self, prefix: str, completion: str, mode: str) -> Dict[str, Any]:
        """Analyze the generated completion"""
        analysis = {
            "mode": mode,
            "coherence": "high",  # Placeholder - could use more sophisticated analysis
            "features": []
        }
        
        if mode == "code":
            # Analyze code features
            if "def " in completion:
                analysis["features"].append("function_definition")
            if "class " in completion:
                analysis["features"].append("class_definition")
            if "return " in completion:
                analysis["features"].append("return_statement")
            if "if " in completion or "else" in completion:
                analysis["features"].append("conditional")
            if "for " in completion or "while " in completion:
                analysis["features"].append("loop")
            if "#" in completion:
                analysis["features"].append("comment")
        else:
            # Analyze text features
            if "." in completion:
                analysis["features"].append("complete_sentences")
            if "?" in completion:
                analysis["features"].append("questions")
            if "!" in completion:
                analysis["features"].append("exclamations")
            if "\n" in completion:
                analysis["features"].append("paragraphs")
        
        # Check completion quality
        if len(completion.strip()) < 10:
            analysis["coherence"] = "low"
        elif len(completion.strip()) < 50:
            analysis["coherence"] = "medium"
        
        return analysis
    
    def get_schema(self) -> Dict[str, Any]:
        """Get parameter schema for prefix completion"""
        return {
            "type": "object",
            "properties": {
                "prefix": {
                    "type": "string",
                    "description": "Text or code to continue from"
                },
                "mode": {
                    "type": "string",
                    "description": "Completion mode",
                    "enum": ["auto", "text", "code"],
                    "default": "auto"
                },
                "model": {
                    "type": "string",
                    "description": "Model to use for completion",
                    "enum": ["deepseek-chat", "deepseek-coder"],
                    "default": "deepseek-chat"
                },
                "max_tokens": {
                    "type": "integer",
                    "description": "Maximum tokens to generate",
                    "default": 512,
                    "minimum": 1,
                    "maximum": 4096
                },
                "temperature": {
                    "type": "number",
                    "description": "Sampling temperature (0.0-2.0)",
                    "default": 0.7,
                    "minimum": 0.0,
                    "maximum": 2.0
                },
                "top_p": {
                    "type": "number",
                    "description": "Nucleus sampling parameter",
                    "default": 0.95,
                    "minimum": 0.0,
                    "maximum": 1.0
                },
                "stop": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Stop sequences for completion",
                    "default": []
                }
            },
            "required": ["prefix"]
        } 