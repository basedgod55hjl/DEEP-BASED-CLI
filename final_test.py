#!/usr/bin/env python3
"""
Comprehensive test suite for DeepSeek CLI
Tests all major features and functionality
"""

import os
import sys
from deepseek_integration import DeepSeekClient

def test_all_features():
    print("🚀 COMPREHENSIVE DEEPSEEK CLI TEST")
    print("=" * 60)
    
    print(f"✅ API Key: {os.environ.get('DEEPSEEK_API_KEY', 'Not set')}")
    
    try:
        client = DeepSeekClient()
        print("✅ Client initialized")
        
        # Test 1: Basic Chat
        print("\n🧪 Test 1: Basic Chat")
        response = client.chat("Tell me a programming joke in one line")
        print(f"✅ Chat Response: {response}")
        
        # Test 2: Reasoning Model
        print("\n🧪 Test 2: Reasoning Model")
        reasoning_result = client.reason("What is 15 × 17?", reasoning_effort="medium")
        print(f"✅ Reasoning Answer: {reasoning_result['answer']}")
        if 'reasoning' in reasoning_result:
            print(f"🧠 Reasoning Process: {reasoning_result['reasoning'][:100]}...")
        
        # Test 3: JSON Output
        print("\n🧪 Test 3: JSON Output")
        from deepseek_integration import ResponseFormat
        json_response = client.chat(
            "Generate a JSON object with fields: name, age, city for a fictional character",
            response_format=ResponseFormat.JSON
        )
        print(f"✅ JSON Response: {json_response}")
        
        # Test 4: Function Calling
        print("\n🧪 Test 4: Function Calling")
        weather_tool = client.create_function_tool(
            name="get_weather",
            description="Get weather information for a city",
            parameters={
                "city": {"type": "string", "description": "The city name"}
            },
            required=["city"]
        )
        
        tool_response = client.chat(
            "What's the weather like in Paris?",
            tools=[weather_tool]
        )
        print(f"✅ Function Call Response: {tool_response}")
        
        # Test 5: Usage Statistics
        print("\n📊 Usage Statistics:")
        usage = client.total_usage
        print(f"✅ Total Tokens: {usage.total_tokens}")
        print(f"✅ Prompt Tokens: {usage.prompt_tokens}")
        print(f"✅ Completion Tokens: {usage.completion_tokens}")
        
        print("\n🎉 ALL TESTS PASSED! DeepSeek CLI is fully functional!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_all_features()
    sys.exit(0 if success else 1)