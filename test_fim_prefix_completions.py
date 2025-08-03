"""
Test script for FIM and Prefix Completion features
Tests both Python tools and CLI integration
"""

import asyncio
import sys
from tools import FIMCompletionTool, PrefixCompletionTool, LLMQueryTool
from enhanced_based_god_cli import EnhancedBasedGodCLI


async def test_fim_completion_tool():
    """Test FIM Completion Tool"""
    print("\n🔧 Testing FIM Completion Tool...")
    
    fim_tool = FIMCompletionTool()
    
    # Test 1: Complete a simple function
    print("\n📝 Test 1: Complete simple function")
    result = await fim_tool.execute(
        prefix="def add(a, b):\n    ",
        suffix="\n    return result",
        language="python"
    )
    
    if result.success:
        print(f"✅ Success: {result.message}")
        print(f"Completion: {result.data['completion']}")
        print(f"Full code:\n{result.data['full_code']}")
    else:
        print(f"❌ Failed: {result.message}")
    
    # Test 2: Complete a class method
    print("\n\n📝 Test 2: Complete class method")
    result = await fim_tool.execute(
        prefix="""class Calculator:
    def __init__(self):
        self.history = []
    
    def multiply(self, a, b):
        """,
        suffix="""
        self.history.append(result)
        return result""",
        language="python"
    )
    
    if result.success:
        print(f"✅ Success: {result.message}")
        print(f"Completion: {result.data['completion']}")
        print(f"Analysis: {result.data['analysis']}")
    else:
        print(f"❌ Failed: {result.message}")


async def test_prefix_completion_tool():
    """Test Prefix Completion Tool"""
    print("\n\n🔧 Testing Prefix Completion Tool...")
    
    prefix_tool = PrefixCompletionTool()
    
    # Test 1: Complete text
    print("\n📝 Test 1: Complete text")
    result = await prefix_tool.execute(
        prefix="The benefits of using TypeScript include",
        mode="text"
    )
    
    if result.success:
        print(f"✅ Success: {result.message}")
        print(f"Completion: {result.data['completion']}")
        print(f"Full text: {result.data['full_text']}")
    else:
        print(f"❌ Failed: {result.message}")
    
    # Test 2: Complete code
    print("\n\n📝 Test 2: Complete code")
    result = await prefix_tool.execute(
        prefix="""async function fetchUserData(userId) {
    try {
        const response = await fetch(`/api/users/${userId}`);""",
        mode="code"
    )
    
    if result.success:
        print(f"✅ Success: {result.message}")
        print(f"Completion: {result.data['completion']}")
        print(f"Analysis: {result.data['analysis']}")
    else:
        print(f"❌ Failed: {result.message}")


async def test_llm_query_tool_fim():
    """Test LLM Query Tool with FIM mode"""
    print("\n\n🔧 Testing LLM Query Tool - FIM Mode...")
    
    llm_tool = LLMQueryTool()
    
    # Test FIM mode
    print("\n📝 Test: FIM mode in LLM Query Tool")
    result = await llm_tool.execute(
        mode="fim",
        prefix="def factorial(n):\n    if n <= 1:\n        return 1\n    ",
        suffix="\n    return result",
        model="deepseek-coder"
    )
    
    if result.success:
        print(f"✅ Success: {result.message}")
        print(f"Completion: {result.data['completion']}")
        print(f"Full code:\n{result.data['full_code']}")
    else:
        print(f"❌ Failed: {result.message}")


async def test_llm_query_tool_prefix():
    """Test LLM Query Tool with prefix mode"""
    print("\n\n🔧 Testing LLM Query Tool - Prefix Mode...")
    
    llm_tool = LLMQueryTool()
    
    # Test prefix mode
    print("\n📝 Test: Prefix mode in LLM Query Tool")
    result = await llm_tool.execute(
        mode="prefix",
        prefix="The future of artificial intelligence will",
        max_tokens=150
    )
    
    if result.success:
        print(f"✅ Success: {result.message}")
        print(f"Completion: {result.data['completion']}")
        print(f"Full text: {result.data['full_text']}")
    else:
        print(f"❌ Failed: {result.message}")


async def test_cli_integration():
    """Test CLI integration with FIM and prefix completions"""
    print("\n\n🔧 Testing CLI Integration...")
    
    cli = EnhancedBasedGodCLI()
    
    # Test 1: CLI FIM command
    print("\n📝 Test 1: CLI FIM command")
    response = await cli.chat("FIM complete: <prefix>def calculate_area(radius):<suffix>return area")
    print(f"Response: {response}")
    
    # Test 2: CLI prefix command
    print("\n\n📝 Test 2: CLI prefix command")
    response = await cli.chat("Prefix complete: Once upon a time in a digital world")
    print(f"Response: {response}")
    
    # Test 3: CLI with code blocks
    print("\n\n📝 Test 3: CLI with code blocks")
    response = await cli.chat("""Fill in middle: ```python
def merge_lists(list1, list2):
    merged = []
```
```python
    return merged
```""")
    print(f"Response: {response}")


async def run_all_tests():
    """Run all tests"""
    print("🚀 Starting FIM and Prefix Completion Tests...")
    print("=" * 60)
    
    try:
        # Test individual tools
        await test_fim_completion_tool()
        await test_prefix_completion_tool()
        
        # Test LLM Query Tool integration
        await test_llm_query_tool_fim()
        await test_llm_query_tool_prefix()
        
        # Test CLI integration
        await test_cli_integration()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


def main():
    """Main test runner"""
    print("🔥 FIM & Prefix Completion Test Suite")
    print("Testing Enhanced BASED GOD CLI Features")
    
    # Run tests
    asyncio.run(run_all_tests())


if __name__ == "__main__":
    main()