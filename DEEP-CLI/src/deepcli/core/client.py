"""
Core DeepSeek API client
"""

import asyncio
import json
import logging
from typing import Any, AsyncGenerator, Dict, List, Optional, Union

import httpx
from openai import AsyncOpenAI, OpenAI
from openai.types.chat import ChatCompletionMessageParam

from .config import DeepCLIConfig
from .exceptions import DeepCLIError, RateLimitError
from .models import DeepSeekModel, FunctionCall, Message, ResponseFormat, TokenUsage

logger = logging.getLogger(__name__)


class DeepSeekClient:
    """
    Main client for interacting with DeepSeek API
    
    Supports both sync and async operations, streaming, and function calling.
    """
    
    def __init__(self, config: Optional[DeepCLIConfig] = None):
        self.config = config or DeepCLIConfig()
        
        # Initialize OpenAI clients
        self.client = OpenAI(
            api_key=self.config.api_key,
            base_url=self.config.base_url,
            timeout=self.config.timeout,
            max_retries=self.config.max_retries
        )
        
        self.async_client = AsyncOpenAI(
            api_key=self.config.api_key,
            base_url=self.config.base_url,
            timeout=self.config.timeout,
            max_retries=self.config.max_retries
        )
        
        # Track usage
        self.total_usage = TokenUsage()
    
    def _prepare_messages(
        self, 
        messages: Union[str, List[Message], List[Dict[str, Any]]]
    ) -> List[ChatCompletionMessageParam]:
        """Convert messages to OpenAI format"""
        if isinstance(messages, str):
            return [{"role": "user", "content": messages}]
        
        formatted_messages = []
        for msg in messages:
            if isinstance(msg, Message):
                formatted = {"role": msg.role, "content": msg.content}
                if msg.name:
                    formatted["name"] = msg.name
                if msg.tool_calls:
                    formatted["tool_calls"] = msg.tool_calls
                if msg.tool_call_id:
                    formatted["tool_call_id"] = msg.tool_call_id
                formatted_messages.append(formatted)
            elif isinstance(msg, dict):
                formatted_messages.append(msg)
        
        return formatted_messages
    
    def _extract_usage(self, response: Any) -> TokenUsage:
        """Extract token usage from response"""
        usage = TokenUsage()
        if hasattr(response, 'usage') and response.usage:
            usage.prompt_tokens = response.usage.prompt_tokens or 0
            usage.completion_tokens = response.usage.completion_tokens or 0
            usage.total_tokens = response.usage.total_tokens or 0
            
            # Handle DeepSeek-specific usage fields
            if hasattr(response.usage, 'prompt_cache_hit_tokens'):
                usage.cache_hit_tokens = response.usage.prompt_cache_hit_tokens or 0
            if hasattr(response.usage, 'prompt_cache_miss_tokens'):
                usage.cache_miss_tokens = response.usage.prompt_cache_miss_tokens or 0
            
            # Calculate estimated cost (DeepSeek pricing)
            # Chat: $0.14/1M input, $0.28/1M output (cache hit: $0.014/1M)
            # Reasoner: $0.55/1M input, $2.19/1M output
            if self.config.default_model == DeepSeekModel.CHAT:
                input_cost = (usage.prompt_tokens - usage.cache_hit_tokens) * 0.14 / 1_000_000
                input_cost += usage.cache_hit_tokens * 0.014 / 1_000_000
                output_cost = usage.completion_tokens * 0.28 / 1_000_000
            else:  # Reasoner
                input_cost = usage.prompt_tokens * 0.55 / 1_000_000
                output_cost = usage.completion_tokens * 2.19 / 1_000_000
            
            usage.estimated_cost = input_cost + output_cost
        
        return usage
    
    async def chat(
        self,
        messages: Union[str, List[Message], List[Dict[str, Any]]],
        model: Optional[DeepSeekModel] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        response_format: Optional[ResponseFormat] = None,
        **kwargs: Any
    ) -> Union[str, AsyncGenerator[str, None]]:
        """
        Send a chat completion request
        
        Args:
            messages: Single message string or list of messages
            model: Model to use (defaults to config)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            tools: List of available tools/functions
            tool_choice: Tool selection strategy
            response_format: Response format (text or json)
            **kwargs: Additional parameters
        
        Returns:
            Response text or async generator for streaming
        """
        # Prepare parameters
        params = {
            "model": (model or self.config.default_model).value,
            "messages": self._prepare_messages(messages),
            "temperature": temperature or self.config.temperature,
            "max_tokens": max_tokens or self.config.max_tokens,
            "stream": stream,
            **kwargs
        }
        
        if tools:
            params["tools"] = tools
            if tool_choice:
                params["tool_choice"] = tool_choice
        
        if response_format:
            params["response_format"] = {"type": response_format.value}
        
        try:
            if stream:
                return self._stream_chat(**params)
            else:
                response = await self.async_client.chat.completions.create(**params)
                
                # Track usage
                usage = self._extract_usage(response)
                self.total_usage.add(usage)
                
                # Extract content
                if response.choices and response.choices[0].message:
                    message = response.choices[0].message
                    
                    # Handle function calls
                    if message.tool_calls:
                        function_calls = []
                        for tool_call in message.tool_calls:
                            if tool_call.function:
                                function_calls.append(FunctionCall(
                                    name=tool_call.function.name,
                                    arguments=json.loads(tool_call.function.arguments),
                                    id=tool_call.id
                                ))
                        return {
                            "content": message.content or "",
                            "function_calls": function_calls
                        }
                    
                    return message.content or ""
                
                return ""
                
        except Exception as e:
            if "rate_limit" in str(e).lower():
                raise RateLimitError(f"Rate limit exceeded: {e}")
            raise DeepCLIError(f"API request failed: {e}")
    
    async def _stream_chat(self, **params: Any) -> AsyncGenerator[str, None]:
        """Stream chat completion response"""
        try:
            stream = await self.async_client.chat.completions.create(**params)
            
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        yield delta.content
                    
                    # Handle function call streaming
                    if delta.tool_calls:
                        for tool_call in delta.tool_calls:
                            if tool_call.function:
                                yield json.dumps({
                                    "type": "function_call",
                                    "name": tool_call.function.name,
                                    "arguments": tool_call.function.arguments
                                })
                
                # Extract usage from final chunk
                if chunk.usage:
                    usage = self._extract_usage(chunk)
                    self.total_usage.add(usage)
                    
        except Exception as e:
            if "rate_limit" in str(e).lower():
                raise RateLimitError(f"Rate limit exceeded: {e}")
            raise DeepCLIError(f"Streaming failed: {e}")
    
    def chat_sync(
        self,
        messages: Union[str, List[Message], List[Dict[str, Any]]],
        **kwargs: Any
    ) -> str:
        """Synchronous chat method"""
        params = {
            "model": (kwargs.pop("model", None) or self.config.default_model).value,
            "messages": self._prepare_messages(messages),
            "temperature": kwargs.pop("temperature", self.config.temperature),
            "max_tokens": kwargs.pop("max_tokens", self.config.max_tokens),
            **kwargs
        }
        
        try:
            response = self.client.chat.completions.create(**params)
            
            # Track usage
            usage = self._extract_usage(response)
            self.total_usage.add(usage)
            
            # Extract content
            if response.choices and response.choices[0].message:
                return response.choices[0].message.content or ""
            
            return ""
            
        except Exception as e:
            if "rate_limit" in str(e).lower():
                raise RateLimitError(f"Rate limit exceeded: {e}")
            raise DeepCLIError(f"API request failed: {e}")
    
    async def reasoning_chat(
        self,
        messages: Union[str, List[Message], List[Dict[str, Any]]],
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Use the reasoning model for complex tasks
        
        Returns both reasoning process and final answer
        """
        kwargs["model"] = DeepSeekModel.REASONER
        
        # For reasoning model, we want to capture the full response
        response = await self.chat(messages, stream=False, **kwargs)
        
        # Parse reasoning output (assuming it comes in a structured format)
        if isinstance(response, str):
            # Try to extract reasoning steps if present
            lines = response.split('\n')
            reasoning_steps = []
            final_answer = ""
            
            in_reasoning = False
            for line in lines:
                if line.strip().startswith("Reasoning:"):
                    in_reasoning = True
                    continue
                elif line.strip().startswith("Answer:"):
                    in_reasoning = False
                    final_answer = '\n'.join(lines[lines.index(line)+1:])
                    break
                elif in_reasoning:
                    reasoning_steps.append(line.strip())
            
            return {
                "reasoning": reasoning_steps,
                "answer": final_answer or response,
                "full_response": response
            }
        
        return {"answer": response, "full_response": response}
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics"""
        return {
            "prompt_tokens": self.total_usage.prompt_tokens,
            "completion_tokens": self.total_usage.completion_tokens,
            "total_tokens": self.total_usage.total_tokens,
            "cache_hit_tokens": self.total_usage.cache_hit_tokens,
            "cache_miss_tokens": self.total_usage.cache_miss_tokens,
            "reasoning_tokens": self.total_usage.reasoning_tokens,
            "estimated_cost": f"${self.total_usage.estimated_cost:.4f}",
            "cache_hit_rate": (
                f"{(self.total_usage.cache_hit_tokens / max(self.total_usage.prompt_tokens, 1)) * 100:.1f}%"
                if self.total_usage.prompt_tokens > 0 else "0%"
            )
        }
    
    def reset_usage_stats(self) -> None:
        """Reset usage statistics"""
        self.total_usage = TokenUsage()