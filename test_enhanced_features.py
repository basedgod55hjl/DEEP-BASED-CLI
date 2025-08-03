#!/usr/bin/env python3
"""
Comprehensive test for enhanced DeepSeek CLI features
Tests all new beta features and improvements
"""

import json
from deepseek_integration import DeepSeekClient

def test_enhanced_features():
    print("🧪 TESTING ENHANCED DEEPSEEK CLI FEATURES")
    print("=" * 60)
    
    client = DeepSeekClient()
    
    # Test 1: Enhanced JSON Output
    print("\n🔬 Test 1: Enhanced JSON Output")
    try:
        result = client.enhanced_json_output(
            "Create a user profile for a software developer",
            json_schema_description="Object with fields: name, age, skills (array), experience_years, city",
            example_json={
                "name": "John Doe",
                "age": 30,
                "skills": ["Python", "JavaScript"],
                "experience_years": 5,
                "city": "San Francisco"
            }
        )
        print(f"✅ Enhanced JSON: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"❌ Enhanced JSON failed: {e}")
    
    # Test 2: Chat Prefix Completion (Beta)
    print("\n🔬 Test 2: Chat Prefix Completion (Beta)")
    try:
        completion = client.chat_prefix_completion(
            "Write a Python function to calculate fibonacci numbers",
            prefix="```python\ndef fibonacci(",
            stop=["```"]
        )
        print(f"✅ Prefix Completion:\n```python\ndef fibonacci({completion}")
    except Exception as e:
        print(f"❌ Prefix completion failed: {e}")
    
    # Test 3: FIM Completion (Beta)
    print("\n🔬 Test 3: Fill-in-the-Middle Completion (Beta)")
    try:
        completion = client.fim_completion(
            prefix="def process_data(data):\n    # Process the input data\n    ",
            suffix="\n    return processed_data",
            max_tokens=100
        )
        print(f"✅ FIM Completion:\n{completion}")
    except Exception as e:
        print(f"❌ FIM completion failed: {e}")
    
    # Test 4: Performance Statistics with Cache Info
    print("\n🔬 Test 4: Enhanced Performance Statistics")
    try:
        stats = client.get_performance_stats()
        print("✅ Performance Statistics:")
        print(f"  Total Tokens: {stats['total_tokens']:,}")
        print(f"  Cache Hit Ratio: {stats['cache_hit_ratio']:.1f}%")
        print(f"  Cache Savings: ${stats['cache_savings']:.4f}")
        print(f"  Estimated Cost: ${stats['estimated_cost']:.4f}")
    except Exception as e:
        print(f"❌ Performance stats failed: {e}")
    
    # Test 5: Parallel Reasoning
    print("\n🔬 Test 5: Parallel Reasoning")
    try:
        import asyncio
        reasoning_prompts = [
            "What is 15 × 17?",
            "Solve: 2x + 5 = 15",
            "What is the square root of 144?"
        ]
        
        results = asyncio.run(client.parallel_reasoning(
            reasoning_prompts,
            reasoning_effort="medium",
            max_concurrent=2
        ))
        
        print("✅ Parallel Reasoning Results:")
        for i, result in enumerate(results):
            print(f"  Problem {i+1}: {result['answer'][:50]}...")
            
    except Exception as e:
        print(f"❌ Parallel reasoning failed: {e}")
    
    # Test 6: Concurrent Batch Processing
    print("\n🔬 Test 6: Concurrent Batch Processing")
    try:
        prompts = [
            "What is AI?",
            "Explain machine learning",
            "Define neural networks",
            "What is deep learning?"
        ]
        
        responses = asyncio.run(client.batch_chat_concurrent(
            prompts,
            max_workers=3,
            temperature=0.5,
            max_tokens=50
        ))
        
        print("✅ Concurrent Batch Processing:")
        for i, response in enumerate(responses):
            print(f"  Response {i+1}: {response[:50]}...")
            
    except Exception as e:
        print(f"❌ Concurrent batch failed: {e}")
    
    print(f"\n🎉 ENHANCED FEATURES TEST COMPLETE!")
    print(f"Total tokens used in this test: {client.total_usage.total_tokens:,}")

if __name__ == "__main__":
    test_enhanced_features()