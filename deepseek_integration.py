#!/usr/bin/env python3
"""
Comprehensive DeepSeek API Integration Module

This module provides a complete integration with DeepSeek API, supporting:
- Both deepseek-chat and deepseek-reasoner models
- Streaming and non-streaming responses
- Function calling
- Context caching
- JSON output mode
- Error handling and retries
- Token usage tracking
"""

import os
import json
import time
import asyncio
from typing import Dict, List, Optional, Union, AsyncGenerator, Generator, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
from functools import wraps
import httpx
from openai import OpenAI, AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DeepSeekModel(Enum):
    """Available DeepSeek models"""
    CHAT = "deepseek-chat"
    REASONER = "deepseek-reasoner"


class ResponseFormat(Enum):
    """Response format options"""
    TEXT = "text"
    JSON = "json_object"


@dataclass
class DeepSeekConfig:
    """Configuration for DeepSeek API"""
    api_key: str = field(default_factory=lambda: os.getenv("DEEPSEEK_API_KEY", "sk-9af038dd3bdd46258c4a9d02850c9a6d"))
    base_url: str = field(default_factory=lambda: os.getenv("DEEPSEEK_API_ENDPOINT", "https://api.deepseek.com"))
    beta_url: str = "https://api.deepseek.com/beta"
    default_model: DeepSeekModel = DeepSeekModel.CHAT
    max_retries: int = 3
    retry_delay: float = 1.0
    timeout: float = 60.0
    
    def __post_init__(self):
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY is required")


@dataclass
class TokenUsage:
    """Track token usage and costs"""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cache_hit_tokens: int = 0
    cache_miss_tokens: int = 0
    reasoning_tokens: int = 0
    estimated_cost: float = 0.0


class DeepSeekError(Exception):
    """Base exception for DeepSeek API errors"""
    pass


class RateLimitError(DeepSeekError):
    """Rate limit exceeded error"""
    pass


class DeepSeekClient:
    """
    Main client for interacting with DeepSeek API
    
    Example:
        client = DeepSeekClient()
        response = client.chat("Hello, how are you?")
        print(response)
    """
    
    def __init__(self, config: Optional[DeepSeekConfig] = None):
        self.config = config or DeepSeekConfig()
        
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
        
    def _retry_on_error(self, func: Callable):
        """Decorator for retry logic"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(self.config.max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if "429" in str(e):
                        wait_time = self.config.retry_delay * (2 ** attempt)
                        logger.warning(f"Rate limit hit, waiting {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        raise
            raise RateLimitError(f"Max retries exceeded: {last_error}")
        return wrapper
    
    def _update_usage(self, usage_data: Dict[str, Any]):
        """Update token usage tracking"""
        if usage_data:
            self.total_usage.prompt_tokens += usage_data.get("prompt_tokens", 0)
            self.total_usage.completion_tokens += usage_data.get("completion_tokens", 0)
            self.total_usage.total_tokens += usage_data.get("total_tokens", 0)
            self.total_usage.cache_hit_tokens += usage_data.get("prompt_cache_hit_tokens", 0)
            self.total_usage.cache_miss_tokens += usage_data.get("prompt_cache_miss_tokens", 0)
            
            if "completion_tokens_details" in usage_data:
                self.total_usage.reasoning_tokens += usage_data["completion_tokens_details"].get("reasoning_tokens", 0)
    
    def chat(
        self,
        messages: Union[str, List[ChatCompletionMessageParam]],
        model: Optional[DeepSeekModel] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        response_format: Optional[ResponseFormat] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Union[str, Dict[str, Any], Generator]:
        """
        Send a chat completion request
        
        Args:
            messages: Single message string or list of message dicts
            model: Model to use (defaults to config default)
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response
            stream: Whether to stream the response
            response_format: Response format (text or json)
            tools: List of function definitions
            tool_choice: How to handle function calls
            system_prompt: System message to prepend
            **kwargs: Additional parameters
            
        Returns:
            Response string, dict (if JSON mode), or generator (if streaming)
        """
        # Prepare messages
        if isinstance(messages, str):
            message_list = []
            if system_prompt:
                message_list.append({"role": "system", "content": system_prompt})
            message_list.append({"role": "user", "content": messages})
        else:
            message_list = messages.copy()
            if system_prompt and not any(m.get("role") == "system" for m in message_list):
                message_list.insert(0, {"role": "system", "content": system_prompt})
        
        # Prepare parameters
        params = {
            "model": (model or self.config.default_model).value,
            "messages": message_list,
            "temperature": temperature,
            "stream": stream,
            **kwargs
        }
        
        if max_tokens:
            params["max_tokens"] = max_tokens
            
        if response_format:
            params["response_format"] = {"type": response_format.value}
            
        if tools:
            params["tools"] = tools
            if tool_choice:
                params["tool_choice"] = tool_choice
        
        # Make request
        if stream:
            return self._stream_chat(**params)
        else:
            response = self._retry_on_error(lambda: self.client.chat.completions.create(**params))()
            self._update_usage(response.usage.model_dump() if response.usage else {})
            
            # Return appropriate format
            if tools and response.choices[0].message.tool_calls:
                return response.choices[0].message.tool_calls
            elif response_format == ResponseFormat.JSON:
                return json.loads(response.choices[0].message.content)
            else:
                return response.choices[0].message.content
    
    def _stream_chat(self, **params) -> Generator:
        """Handle streaming chat responses"""
        stream = self._retry_on_error(lambda: self.client.chat.completions.create(**params))()
        
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
            
            # Update usage from final chunk
            if hasattr(chunk, 'usage') and chunk.usage:
                self._update_usage(chunk.usage.model_dump())
    
    async def achat(
        self,
        messages: Union[str, List[ChatCompletionMessageParam]],
        model: Optional[DeepSeekModel] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        response_format: Optional[ResponseFormat] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Union[str, Dict[str, Any], AsyncGenerator]:
        """Async version of chat method"""
        # Prepare messages (same as sync version)
        if isinstance(messages, str):
            message_list = []
            if system_prompt:
                message_list.append({"role": "system", "content": system_prompt})
            message_list.append({"role": "user", "content": messages})
        else:
            message_list = messages.copy()
            if system_prompt and not any(m.get("role") == "system" for m in message_list):
                message_list.insert(0, {"role": "system", "content": system_prompt})
        
        # Prepare parameters
        params = {
            "model": (model or self.config.default_model).value,
            "messages": message_list,
            "temperature": temperature,
            "stream": stream,
            **kwargs
        }
        
        if max_tokens:
            params["max_tokens"] = max_tokens
            
        if response_format:
            params["response_format"] = {"type": response_format.value}
            
        if tools:
            params["tools"] = tools
            if tool_choice:
                params["tool_choice"] = tool_choice
        
        # Make request
        if stream:
            return self._astream_chat(**params)
        else:
            response = await self.async_client.chat.completions.create(**params)
            self._update_usage(response.usage.model_dump() if response.usage else {})
            
            # Return appropriate format
            if tools and response.choices[0].message.tool_calls:
                return response.choices[0].message.tool_calls
            elif response_format == ResponseFormat.JSON:
                return json.loads(response.choices[0].message.content)
            else:
                return response.choices[0].message.content
    
    async def _astream_chat(self, **params) -> AsyncGenerator:
        """Handle async streaming chat responses"""
        stream = await self.async_client.chat.completions.create(**params)
        
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
            
            # Update usage from final chunk
            if hasattr(chunk, 'usage') and chunk.usage:
                self._update_usage(chunk.usage.model_dump())
    
    def reason(
        self,
        prompt: str,
        reasoning_effort: str = "medium",
        show_reasoning: bool = True,
        **kwargs
    ) -> Dict[str, str]:
        """
        Use the reasoning model for complex problem-solving
        
        Args:
            prompt: The problem or question to solve
            reasoning_effort: Level of reasoning (low, medium, high, none)
            show_reasoning: Whether to include reasoning steps in response
            **kwargs: Additional chat parameters
            
        Returns:
            Dictionary with 'answer' and optionally 'reasoning' keys
        """
        response = self.client.chat.completions.create(
            model=DeepSeekModel.REASONER.value,
            messages=[{"role": "user", "content": prompt}],
            reasoning_effort=reasoning_effort,
            **kwargs
        )
        
        self._update_usage(response.usage.model_dump() if response.usage else {})
        
        result = {"answer": response.choices[0].message.content}
        
        if show_reasoning and hasattr(response.choices[0].message, 'reasoning_content'):
            result["reasoning"] = response.choices[0].message.reasoning_content
            
        return result
    
    def create_function_tool(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        required: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Helper to create a function tool definition
        
        Args:
            name: Function name
            description: Function description
            parameters: Parameter schema (JSON Schema format)
            required: List of required parameter names
            
        Returns:
            Tool definition dict
        """
        return {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": parameters,
                    "required": required or []
                }
            }
        }
    
    def batch_chat(
        self,
        prompts: List[str],
        model: Optional[DeepSeekModel] = None,
        max_concurrent: int = 5,
        **kwargs
    ) -> List[str]:
        """
        Process multiple prompts concurrently
        
        Args:
            prompts: List of prompts to process
            model: Model to use
            max_concurrent: Maximum concurrent requests
            **kwargs: Additional chat parameters
            
        Returns:
            List of responses in same order as prompts
        """
        async def process_batch():
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def process_one(prompt: str) -> str:
                async with semaphore:
                    return await self.achat(prompt, model=model, **kwargs)
            
            tasks = [process_one(prompt) for prompt in prompts]
            return await asyncio.gather(*tasks)
        
        return asyncio.run(process_batch())
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """Get summary of token usage and estimated costs"""
        # Rough cost estimates (adjust based on actual pricing)
        prompt_cost_per_1m = 0.07  # $0.07 per 1M tokens
        completion_cost_per_1m = 0.28  # $0.28 per 1M tokens
        
        prompt_cost = (self.total_usage.prompt_tokens / 1_000_000) * prompt_cost_per_1m
        completion_cost = (self.total_usage.completion_tokens / 1_000_000) * completion_cost_per_1m
        
        cache_savings = (self.total_usage.cache_hit_tokens / 1_000_000) * prompt_cost_per_1m * 0.74
        
        return {
            "usage": {
                "prompt_tokens": self.total_usage.prompt_tokens,
                "completion_tokens": self.total_usage.completion_tokens,
                "total_tokens": self.total_usage.total_tokens,
                "cache_hit_tokens": self.total_usage.cache_hit_tokens,
                "cache_miss_tokens": self.total_usage.cache_miss_tokens,
                "reasoning_tokens": self.total_usage.reasoning_tokens
            },
            "costs": {
                "prompt_cost": round(prompt_cost, 4),
                "completion_cost": round(completion_cost, 4),
                "total_cost": round(prompt_cost + completion_cost, 4),
                "cache_savings": round(cache_savings, 4)
            },
            "efficiency": {
                "cache_hit_rate": round(
                    self.total_usage.cache_hit_tokens / max(self.total_usage.prompt_tokens, 1) * 100, 2
                )
            }
        }
    
    def reset_usage(self):
        """Reset usage tracking"""
        self.total_usage = TokenUsage()


# Convenience functions for quick usage
def quick_chat(prompt: str, **kwargs) -> str:
    """Quick chat without creating a client instance"""
    client = DeepSeekClient()
    return client.chat(prompt, **kwargs)


def quick_reason(prompt: str, **kwargs) -> Dict[str, str]:
    """Quick reasoning without creating a client instance"""
    client = DeepSeekClient()
    return client.reason(prompt, **kwargs)


# Example usage and tests
if __name__ == "__main__":
    # Example 1: Basic chat
    client = DeepSeekClient()
    
    print("=== Example 1: Basic Chat ===")
    response = client.chat("What is the capital of France?")
    print(f"Response: {response}\n")
    
    # Example 2: Streaming chat
    print("=== Example 2: Streaming Chat ===")
    for chunk in client.chat("Tell me a short story", stream=True):
        print(chunk, end='', flush=True)
    print("\n")
    
    # Example 3: Reasoning model
    print("=== Example 3: Reasoning Model ===")
    math_problem = "If a train travels 120 km in 2 hours, what is its average speed?"
    result = client.reason(math_problem)
    print(f"Answer: {result['answer']}")
    if 'reasoning' in result:
        print(f"Reasoning: {result['reasoning']}\n")
    
    # Example 4: JSON output
    print("=== Example 4: JSON Output ===")
    json_prompt = "Generate a JSON object with name, age, and city fields for a fictional person"
    json_response = client.chat(
        json_prompt,
        response_format=ResponseFormat.JSON,
        system_prompt="You must respond with valid JSON only"
    )
    print(f"JSON Response: {json.dumps(json_response, indent=2)}\n")
    
    # Example 5: Function calling
    print("=== Example 5: Function Calling ===")
    weather_tool = client.create_function_tool(
        name="get_weather",
        description="Get the current weather in a location",
        parameters={
            "location": {"type": "string", "description": "City name"},
            "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
        },
        required=["location"]
    )
    
    response = client.chat(
        "What's the weather in Paris?",
        tools=[weather_tool],
        tool_choice="auto"
    )
    print(f"Function calls: {response}\n")
    
    # Example 6: Batch processing
    print("=== Example 6: Batch Processing ===")
    questions = [
        "What is 2+2?",
        "What is the capital of Japan?",
        "Translate 'hello' to Spanish"
    ]
    answers = client.batch_chat(questions, temperature=0)
    for q, a in zip(questions, answers):
        print(f"Q: {q}")
        print(f"A: {a}\n")
    
    # Show usage summary
    print("=== Usage Summary ===")
    print(json.dumps(client.get_usage_summary(), indent=2))