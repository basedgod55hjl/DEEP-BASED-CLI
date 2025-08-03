#!/usr/bin/env python3
"""
Quick test of the real-time chat with background reasoning
"""

import asyncio
from tools.llm_query_tool import LLMQueryTool

async def test_realtime_chat():
    """Test the real-time chat with CoT streaming"""
    
    print("🚀 Testing Real-time DeepSeek Chat with Background Reasoning")
    print("=" * 60)
    
    # Initialize LLM tool
    llm_tool = LLMQueryTool()
    
    # Test 1: Simple greeting (should trigger reasoning flow now)
    print("\n💬 Test 1: Simple greeting with CoT")
    result1 = await llm_tool.execute(
        query="Hello, how are you?",
        task_type="general"
    )
    
    if result1.success:
        print("✅ Real-time chat successful!")
        print(f"Provider: {result1.data.get('provider')}")
        print(f"Streaming: {result1.data.get('streaming')}")
        print(f"CoT Displayed: {result1.data.get('cot_displayed')}")
    else:
        print(f"❌ Test 1 failed: {result1.message}")
    
    print("\n" + "="*60)
    
    # Test 2: Reasoning question
    print("\n🧠 Test 2: Complex reasoning question")
    result2 = await llm_tool.execute(
        query="Explain why machine learning works and what makes it powerful",
        task_type="reasoning"
    )
    
    if result2.success:
        print("✅ Complex reasoning successful!")
        print(f"Provider: {result2.data.get('provider')}")
        print(f"Real-time flow: {result2.metadata.get('realtime_flow')}")
        print(f"Background reasoning: {result2.metadata.get('background_reasoning')}")
    else:
        print(f"❌ Test 2 failed: {result2.message}")
    
    print("\n🎯 Real-time chat testing completed!")

if __name__ == "__main__":
    asyncio.run(test_realtime_chat())