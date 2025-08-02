#!/usr/bin/env python3
"""
Simple usage examples for DeepSeek API integration

This script demonstrates basic functionality without the complexity
of the full chatbot or web API examples.
"""

import sys
import json
from typing import List, Dict

# Add parent directory to path
sys.path.append('..')
from deepseek_integration import (
    DeepSeekClient, 
    DeepSeekModel, 
    ResponseFormat,
    quick_chat,
    quick_reason
)


def example_1_basic_chat():
    """Example 1: Basic chat completion"""
    print("=== Example 1: Basic Chat ===")
    
    # Using the quick function
    response = quick_chat("What are the three primary colors?")
    print(f"Response: {response}\n")


def example_2_conversation():
    """Example 2: Multi-turn conversation"""
    print("=== Example 2: Conversation ===")
    
    client = DeepSeekClient()
    
    # Build a conversation
    messages = [
        {"role": "system", "content": "You are a helpful science teacher."},
        {"role": "user", "content": "What is photosynthesis?"},
        {"role": "assistant", "content": "Photosynthesis is the process by which plants use sunlight, water, and carbon dioxide to create oxygen and energy in the form of sugar."},
        {"role": "user", "content": "Why is it important?"}
    ]
    
    response = client.chat(messages)
    print(f"Response: {response}\n")


def example_3_streaming():
    """Example 3: Streaming response"""
    print("=== Example 3: Streaming ===")
    
    client = DeepSeekClient()
    
    print("Streaming response: ", end='')
    for chunk in client.chat("Write a haiku about programming", stream=True):
        print(chunk, end='', flush=True)
    print("\n")


def example_4_json_output():
    """Example 4: JSON structured output"""
    print("=== Example 4: JSON Output ===")
    
    client = DeepSeekClient()
    
    prompt = """Create a JSON object for a book with the following fields:
    - title
    - author
    - year
    - genres (array)
    - rating (number between 1-5)"""
    
    response = client.chat(
        prompt,
        response_format=ResponseFormat.JSON,
        system_prompt="You must respond with valid JSON only."
    )
    
    print("JSON Response:")
    print(json.dumps(response, indent=2))
    print()


def example_5_reasoning():
    """Example 5: Using the reasoning model"""
    print("=== Example 5: Reasoning Model ===")
    
    # Simple reasoning
    result = quick_reason(
        "A farmer has 17 sheep. All but 9 die. How many sheep are left?"
    )
    
    print(f"Answer: {result['answer']}")
    if 'reasoning' in result:
        print(f"\nReasoning process:\n{result['reasoning']}\n")


def example_6_code_generation():
    """Example 6: Code generation"""
    print("=== Example 6: Code Generation ===")
    
    client = DeepSeekClient()
    
    code_prompt = """Write a Python function that:
    1. Takes a list of numbers as input
    2. Returns the mean, median, and mode
    3. Handles edge cases gracefully
    4. Includes docstring and type hints"""
    
    response = client.chat(
        code_prompt,
        model=DeepSeekModel.CHAT,
        temperature=0.2,  # Lower temperature for more consistent code
        system_prompt="You are an expert Python programmer. Provide clean, well-documented code."
    )
    
    print("Generated Code:")
    print(response)
    print()


def example_7_function_calling():
    """Example 7: Function calling"""
    print("=== Example 7: Function Calling ===")
    
    client = DeepSeekClient()
    
    # Define some functions
    get_weather = client.create_function_tool(
        name="get_weather",
        description="Get the current weather in a given location",
        parameters={
            "location": {
                "type": "string",
                "description": "The city and state, e.g. San Francisco, CA"
            },
            "unit": {
                "type": "string",
                "enum": ["celsius", "fahrenheit"],
                "description": "The unit for temperature"
            }
        },
        required=["location"]
    )
    
    search_web = client.create_function_tool(
        name="search_web",
        description="Search the web for information",
        parameters={
            "query": {
                "type": "string",
                "description": "The search query"
            },
            "num_results": {
                "type": "integer",
                "description": "Number of results to return",
                "default": 5
            }
        },
        required=["query"]
    )
    
    # Ask a question that might need tools
    response = client.chat(
        "What's the weather like in Tokyo and what tourist attractions should I visit?",
        tools=[get_weather, search_web],
        tool_choice="auto"
    )
    
    print("Function calls:")
    for i, call in enumerate(response, 1):
        print(f"{i}. Function: {call.function.name}")
        print(f"   Arguments: {call.function.arguments}")
    print()


def example_8_batch_processing():
    """Example 8: Batch processing multiple prompts"""
    print("=== Example 8: Batch Processing ===")
    
    client = DeepSeekClient()
    
    # List of different tasks
    tasks = [
        "Translate 'Good morning' to Japanese",
        "What is the square root of 144?",
        "Write a one-line Python function to reverse a string",
        "What's the chemical formula for water?",
        "Generate a random fun fact about space"
    ]
    
    print("Processing batch requests...")
    responses = client.batch_chat(tasks, temperature=0.5, max_concurrent=3)
    
    for task, response in zip(tasks, responses):
        print(f"\nTask: {task}")
        print(f"Response: {response}")
    print()


def example_9_usage_tracking():
    """Example 9: Track API usage and costs"""
    print("=== Example 9: Usage Tracking ===")
    
    client = DeepSeekClient()
    
    # Reset usage to start fresh
    client.reset_usage()
    
    # Make several requests
    client.chat("Hello, how are you?")
    client.chat("Tell me a joke")
    client.chat("What is 2+2?", model=DeepSeekModel.REASONER)
    
    # Check usage
    usage = client.get_usage_summary()
    
    print("Usage Summary:")
    print(f"- Total tokens: {usage['usage']['total_tokens']:,}")
    print(f"- Prompt tokens: {usage['usage']['prompt_tokens']:,}")
    print(f"- Completion tokens: {usage['usage']['completion_tokens']:,}")
    print(f"- Cache hit rate: {usage['efficiency']['cache_hit_rate']}%")
    print(f"- Estimated cost: ${usage['costs']['total_cost']:.4f}")
    print(f"- Cache savings: ${usage['costs']['cache_savings']:.4f}")
    print()


def example_10_error_handling():
    """Example 10: Error handling"""
    print("=== Example 10: Error Handling ===")
    
    from deepseek_integration import DeepSeekError, DeepSeekConfig
    
    # Example with invalid API key
    try:
        bad_config = DeepSeekConfig(api_key="invalid-key")
        bad_client = DeepSeekClient(bad_config)
        bad_client.chat("This will fail")
    except DeepSeekError as e:
        print(f"Expected error: {e}")
    
    # Example with very long prompt (would exceed token limit)
    client = DeepSeekClient()
    try:
        very_long_prompt = "Tell me about " + "everything " * 50000
        client.chat(very_long_prompt)
    except Exception as e:
        print(f"Token limit error: {type(e).__name__}")
    
    print("\nError handling examples completed.\n")


def main():
    """Run all examples"""
    print("DeepSeek API Integration - Simple Usage Examples\n")
    
    examples = [
        example_1_basic_chat,
        example_2_conversation,
        example_3_streaming,
        example_4_json_output,
        example_5_reasoning,
        example_6_code_generation,
        example_7_function_calling,
        example_8_batch_processing,
        example_9_usage_tracking,
        example_10_error_handling
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"Error in {example.__name__}: {e}\n")
        
        # Small pause between examples
        input("Press Enter to continue to next example...")
        print()
    
    print("All examples completed!")


if __name__ == "__main__":
    # Check if API key is set
    import os
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("Error: DEEPSEEK_API_KEY environment variable not set!")
        print("Please set it up according to the README instructions.")
        sys.exit(1)
    
    main()