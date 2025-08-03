#!/usr/bin/env python3
"""
Test DeepSeek integration with hardcoded API key
"""

import asyncio
from tools.llm_query_tool import LLMQueryTool

async def test_deepseek_hardcoded():
    """Test DeepSeek API with hardcoded key"""
    
    print("🧪 Testing DeepSeek API with hardcoded key...")
    
    # Initialize LLM tool
    llm_tool = LLMQueryTool()
    
    # Test provider status
    print("\n📊 Provider Status:")
    status = llm_tool.get_provider_status()
    print(f"Available providers: {status['available_providers']}")
    print(f"Total providers: {status['total_providers']}")
    
    # Test simple query
    print("\n💬 Testing simple query...")
    result = await llm_tool.execute(
        query="Hello! Can you tell me what 2 + 2 equals?",
        task_type="general"
    )
    
    if result.success:
        print("✅ DeepSeek API test successful!")
        print(f"Response: {result.data.get('response', 'No response')[:200]}...")
    else:
        print(f"❌ DeepSeek API test failed: {result.message}")
        if result.data and result.data.get('fallback_used'):
            print("🔄 Fallback response was used")
    
    # Test coding query
    print("\n💻 Testing coding query...")
    coding_result = await llm_tool.execute(
        query="Write a simple Python function to calculate fibonacci numbers",
        task_type="coding"
    )
    
    if coding_result.success:
        print("✅ DeepSeek coding test successful!")
        print(f"Response: {coding_result.data.get('response', 'No response')[:200]}...")
    else:
        print(f"❌ DeepSeek coding test failed: {coding_result.message}")
    
    print("\n🎯 Test completed!")

if __name__ == "__main__":
    asyncio.run(test_deepseek_hardcoded())