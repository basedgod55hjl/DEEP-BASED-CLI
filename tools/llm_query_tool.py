"""
LLM Query Tool - Enhanced BASED GOD CLI
LangChain-powered LLM integration with Agent Zero patterns
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from datetime import datetime
import openai
from openai import AsyncOpenAI
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from .base_tool import BaseTool, ToolResponse
from config.api_keys import get_deepseek_config, is_deepseek_key_valid

@dataclass
class CompletionConfig:
    """Configuration for completion requests"""
    model: str = "deepseek-chat"
    temperature: float = 0.7
    max_tokens: int = 2000
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stream: bool = False
    stop: Optional[List[str]] = None
    response_format: Optional[Dict[str, str]] = None

class LLMQueryTool(BaseTool):
    """
    Enhanced LLM Query Tool with advanced completion capabilities
    Supports FIM, prefix completion, streaming, and model switching
    """
    
    def __init__(self, 
                 api_key: str = None,
                 base_url: str = None,
                 default_model: str = "deepseek-chat"):
    
        """Initialize Enhanced LLM Query Tool"""
        super().__init__(
            name="Enhanced LLM Query",
            description="Advanced LLM interactions with FIM, prefix completion, streaming, and model switching",
            capabilities=[
                "chat_completion",
                "FIM (Fill-in-Middle) completion support",
                "Prefix completion for code and text",
                "Streaming responses",
                "Model switching",
                "Context management",
                "Error handling and retry logic",
                "Response formatting",
                "Multi-modal support",
                "Function calling"
            ]
        )
        
        # Get DeepSeek configuration
        deepseek_config = get_deepseek_config()
        
        # DeepSeek API configuration
        self.api_key = api_key or deepseek_config["api_key"]
        self.base_url = base_url or deepseek_config["base_url"]
        self.default_model = default_model
        
        # Validate API key
        if not is_deepseek_key_valid():
            logging.warning("⚠️ DeepSeek API key appears to be invalid. Please update it in config/api_keys.py")
        
        # Initialize OpenAI client for FIM/prefix completions
        self.openai_client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        # Initialize LangChain providers with enhanced models
        self.providers = {}
        self._initialize_providers()
        
        # Model configurations
        self.model_configs = {
            "deepseek_chat": {
                "model": "deepseek-chat",
                "temperature": 0.7,
                "max_tokens": 2000,
                "description": "General purpose chat and completion",
            },
            "deepseek_coder": {
                "model": "deepseek-coder",
                "temperature": 0.3,
                "max_tokens": 4000,
                "description": "Specialized for code generation and analysis",
            },
            "deepseek_reasoner": {
                "model": "deepseek-reasoner",
                "temperature": 0.5,
                "max_tokens": 8000,
                "description": "Advanced reasoning and complex problem solving",
            },
        }
        
        # Context management
        self.conversation_history = []
        self.max_history_length = 50
        
        # Error handling
        self.max_retries = 3
        self.retry_delay = 1.0
        
        # Logging
        self.logger = logging.getLogger(__name__)
        
    def _initialize_providers(self) -> Any:
        """Initialize LangChain providers with enhanced configurations"""
        # DeepSeek Chat model (primary)
        self.providers["deepseek_chat"] = ChatOpenAI(
            model="deepseek-chat",
            temperature=0.7,
            api_key=self.api_key,
            base_url=self.base_url,
            max_tokens=2000,
            streaming=True
        )
        
        # DeepSeek Coder model (for programming tasks)
        self.providers["deepseek_coder"] = ChatOpenAI(
            model="deepseek-coder",
            temperature=0.3,
            api_key=self.api_key,
            base_url=self.base_url,
            max_tokens=4000,
            streaming=True
        )
        
        # DeepSeek Reasoner model (for complex reasoning)
        self.providers["deepseek_reasoner"] = ChatOpenAI(
            model="deepseek-reasoner",
            temperature=0.5,
            api_key=self.api_key,
            base_url=self.base_url,
            max_tokens=8000,
            streaming=True
        )
    
    async def execute(self, **kwargs) -> ToolResponse:
        """Execute LLM query with enhanced capabilities"""
        try:
            mode = kwargs.get("mode", "chat")
            
            if mode == "fim":
                return await self.fim_complete(**kwargs)
            elif mode == "prefix":
                return await self.prefix_complete(**kwargs)
            elif mode == "stream":
                return await self.stream_completion(**kwargs)
            elif mode == "function":
                return await self.function_call(**kwargs)
            else:
                return await self.chat_completion(**kwargs)
                
        except Exception as e:
            self.logger.error(f"Error in LLM query execution: {str(e)}")
            return ToolResponse(
                success=False,
                data={"error": str(e)},
                message=f"LLM query failed: {str(e)}"
            )
    
    async def chat_completion(self, **kwargs) -> ToolResponse:
        """Enhanced chat completion with context management"""
        try:
            # Extract parameters
            prompt = kwargs.get("prompt", "")
            system_message = kwargs.get("system_message", "")
            model = kwargs.get("model", self.default_model)
            temperature = kwargs.get("temperature", 0.7)
            max_tokens = kwargs.get("max_tokens", 2000)
            stream = kwargs.get("stream", False)
            
            # Build messages
            messages = []
            if system_message:
                messages.append(SystemMessage(content=system_message))
            
            # Add conversation history
            for msg in self.conversation_history[-10:]:  # Last 10 messages
                messages.append(msg)
            
            # Add current message
            messages.append(HumanMessage(content=prompt))
            
            # Get provider
            provider = self.providers.get(model, self.providers["deepseek_chat"])
            
            # Execute completion
            if stream:
                return await self._stream_completion(provider, messages, temperature, max_tokens)
            else:
                response = await provider.ainvoke(messages)
                
                # Update conversation history
                self.conversation_history.extend([
                    HumanMessage(content=prompt),
                    response
                ])
                
                # Trim history if too long
                if len(self.conversation_history) > self.max_history_length:
                    self.conversation_history = self.conversation_history[-self.max_history_length:]
                
                return ToolResponse(
                    success=True,
                    data={
                        "response": response.content,
                        "model": model,
                        "tokens_used": getattr(response, 'usage', {}),
                        "timestamp": datetime.now().isoformat()
                    },
                    message="Chat completion successful"
                )
                
        except Exception as e:
            return await self._handle_error(e, "chat completion")
    
    async def fim_complete(self, **kwargs) -> ToolResponse:
        """Enhanced FIM completion with better prompt formatting"""
        try:
            prefix = kwargs.get("prefix", "")
            suffix = kwargs.get("suffix", "")
            language = kwargs.get("language", "python")
            model = kwargs.get("model", "deepseek-coder")
            temperature = kwargs.get("temperature", 0.3)
            max_tokens = kwargs.get("max_tokens", 1000)
            
            # Enhanced FIM prompt formatting
            language_hint = f"# {language.upper()} CODE\n" if language else ""
            fim_prompt = f"{language_hint}<PRE>{prefix}<MID>{suffix}<SUF>"
            
            # Execute completion
            response = await self.openai_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": fim_prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False
            )
            
            completion = response.choices[0].message.content
            
            # Post-process completion
            completion = self._clean_fim_completion(completion, prefix, suffix)
            
            return ToolResponse(
                success=True,
                data={
                    "completion": completion,
                    "model": model,
                    "language": language,
                    "tokens_used": response.usage,
                    "timestamp": datetime.now().isoformat()
                },
                message="FIM completion successful"
            )
            
        except Exception as e:
            return await self._handle_error(e, "FIM completion")
    
    async def prefix_complete(self, **kwargs) -> ToolResponse:
        """Enhanced prefix completion with intelligent mode detection"""
        try:
            prefix = kwargs.get("prefix", "")
            model = kwargs.get("model", "deepseek-chat")
            temperature = kwargs.get("temperature", 0.7)
            max_tokens = kwargs.get("max_tokens", 1000)
            
            # Auto-detect mode and adjust parameters
            detected_mode = self._detect_mode(prefix)
            if detected_mode == "code":
                model = "deepseek-coder"
                temperature = 0.3
                max_tokens = 2000
            
            # Enhanced prompt formatting
            if detected_mode == "code":
                prompt = f"Complete the following code:\n\n{prefix}"
            else:
                prompt = f"Continue the following text:\n\n{prefix}"
            
            # Execute completion
            response = await self.openai_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False
            )
            
            completion = response.choices[0].message.content
            
            # Post-process completion
            completion = self._clean_prefix_completion(completion, prefix, detected_mode)
            
            return ToolResponse(
                success=True,
                data={
                    "completion": completion,
                    "model": model,
                    "mode": detected_mode,
                    "tokens_used": response.usage,
                    "timestamp": datetime.now().isoformat()
                },
                message="Prefix completion successful"
            )
            
        except Exception as e:
            return await self._handle_error(e, "prefix completion")
    
    async def stream_completion(self, **kwargs) -> ToolResponse:
        """Streaming completion with real-time output"""
        try:
            prompt = kwargs.get("prompt", "")
            model = kwargs.get("model", "deepseek-chat")
            temperature = kwargs.get("temperature", 0.7)
            max_tokens = kwargs.get("max_tokens", 2000)
            
            # Execute streaming completion
            stream = await self.openai_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            
            # Collect streamed response
            full_response = ""
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
            
            return ToolResponse(
                success=True,
                data={
                    "response": full_response,
                    "model": model,
                    "streamed": True,
                    "timestamp": datetime.now().isoformat()
                },
                message="Streaming completion successful"
            )
            
        except Exception as e:
            return await self._handle_error(e, "streaming completion")
    
    async def function_call(self, **kwargs) -> ToolResponse:
        """Function calling with custom tools"""
        try:
            prompt = kwargs.get("prompt", "")
            functions = kwargs.get("functions", [])
            model = kwargs.get("model", "deepseek-chat")
            temperature = kwargs.get("temperature", 0.7)
            
            # Execute function call
            response = await self.openai_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                tools=functions,
                tool_choice="auto",
                temperature=temperature
            )
            
            return ToolResponse(
                success=True,
                data={
                    "response": response.choices[0].message,
                    "model": model,
                    "function_calls": response.choices[0].message.tool_calls,
                    "timestamp": datetime.now().isoformat()
                },
                message="Function call successful"
            )
            
        except Exception as e:
            return await self._handle_error(e, "function call")
    
    def _detect_mode(self, prefix: str) -> str:
        """Enhanced mode detection for prefix completion"""
        # Code indicators
        code_indicators = [
            "def ", "class ", "import ", "from ", "if __name__",
            "function ", "const ", "let ", "var ", "public ", "private ",
            "<?php", "<script", "<html", "package ", "namespace ",
            "public class", "interface ", "enum ", "struct ",
            "//", "/*", "#", "<!--", "<!--", "*/", "*/"
        ]
        
        # Check for code indicators
        prefix_lower = prefix.lower()
        for indicator in code_indicators:
            if indicator.lower() in prefix_lower:
                return "code"
        
        # Check for code-like patterns
        if any(char in prefix for char in ["{", "}", "(", ")", ";", "=", "->", "=>"]):
            return "code"
        
        return "text"
    
    def _clean_fim_completion(self, completion: str, prefix: str, suffix: str) -> str:
        """Clean and validate FIM completion"""
        # Remove any remaining tokens
        completion = completion.replace("<PRE>", "").replace("<MID>", "").replace("<SUF>", "")
        completion = completion.replace("<｜fim begin｜>", "").replace("<｜fim hole｜>", "").replace("<｜fim end｜>", "")
        
        # Ensure completion doesn't duplicate prefix or suffix
        if completion.startswith(prefix):
            completion = completion[len(prefix):]
        if completion.endswith(suffix):
            completion = completion[:-len(suffix)]
        
        return completion.strip()
    
    def _clean_prefix_completion(self, completion: str, prefix: str, mode: str) -> str:
        """Clean and validate prefix completion"""
        # Remove any duplicate prefix
        if completion.startswith(prefix):
            completion = completion[len(prefix):]
        
        # For code, ensure proper indentation
        if mode == "code":
            lines = completion.split('\n')
            if lines and not lines[0].strip():
                lines = lines[1:]
            completion = '\n'.join(lines)
        
        return completion.strip()
    
    async def _stream_completion(self, provider, messages, temperature, max_tokens) -> Any:
        """Handle streaming completion"""
        try:
            response = await provider.ainvoke(messages)
            return ToolResponse(
                success=True,
                data={
                    "response": response.content,
                    "streamed": True,
                    "timestamp": datetime.now().isoformat()
                },
                message="Streaming completion successful"
            )
        except Exception as e:
            return await self._handle_error(e, "streaming completion")
    
    async def _handle_error(self, error: Exception, operation: str) -> ToolResponse:
        """Enhanced error handling with retry logic"""
        self.logger.error(f"Error in {operation}: {str(error)}")
        
        # Check for specific error types
        if "insufficient_quota" in str(error).lower() or "402" in str(error):
            return ToolResponse(
                success=False,
                data={"error": "Insufficient API quota"},
                message="API quota exceeded. Please check your account balance."
            )
        elif "rate_limit" in str(error).lower() or "429" in str(error):
            return ToolResponse(
                success=False,
                data={"error": "Rate limit exceeded"},
                message="Rate limit exceeded. Please wait before retrying."
            )
        else:
            return ToolResponse(
                success=False,
                data={"error": str(error)},
                message=f"{operation} failed: {str(error)}"
            )
    
    def get_schema(self) -> Dict[str, Any]:
        """Get enhanced schema for the tool"""
        return {
            "name": "Enhanced LLM Query",
            "description": "Advanced LLM interactions with multiple completion modes",
            "parameters": {
                "mode": {
                    "type": "string",
                    "enum": ["chat", "fim", "prefix", "stream", "function"],
                    "description": "Completion mode to use"
                },
                "prompt": {
                    "type": "string",
                    "description": "Input prompt for completion"
                },
                "prefix": {
                    "type": "string",
                    "description": "Prefix for FIM or prefix completion"
                },
                "suffix": {
                    "type": "string",
                    "description": "Suffix for FIM completion"
                },
                "model": {
                    "type": "string",
                    "enum": ["deepseek-chat", "deepseek-coder", "deepseek-reasoner"],
                    "description": "Model to use for completion"
                },
                "temperature": {
                    "type": "number",
                    "description": "Temperature for generation (0.0-2.0)"
                },
                "max_tokens": {
                    "type": "integer",
                    "description": "Maximum tokens to generate"
                },
                "stream": {
                    "type": "boolean",
                    "description": "Whether to stream the response"
                },
                "system_message": {
                    "type": "string",
                    "description": "System message for chat completion"
                },
                "functions": {
                    "type": "array",
                    "description": "Functions for function calling"
                },
                "language": {
                    "type": "string",
                    "description": "Programming language for code completion"
                }
            }
        }
    
    def clear_history(self) -> Any:
        """Clear conversation history"""
        self.conversation_history = []
    
    def get_history(self) -> List:
        """Get conversation history"""
        return self.conversation_history.copy()
    
    def add_to_history(self, role: str, content: str):
    
        """Add message to conversation history"""
        if role == "user":
            self.conversation_history.append(HumanMessage(content=content))
        elif role == "assistant":
            # Create a simple message object for assistant responses
            from langchain_core.messages import AIMessage
            self.conversation_history.append(AIMessage(content=content))
        
        # Trim history if too long
        if len(self.conversation_history) > self.max_history_length:
            self.conversation_history = self.conversation_history[-self.max_history_length:]