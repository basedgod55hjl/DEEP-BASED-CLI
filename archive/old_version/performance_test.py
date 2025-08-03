#!/usr/bin/env python3
"""
Performance test for DeepSeek CLI with async improvements
Tests concurrent processing vs sequential processing
"""

import time
import asyncio
from deepseek_integration import DeepSeekClient

def test_performance():
    print("🚀 DEEPSEEK CLI PERFORMANCE TEST")
    print("=" * 60)
    
    client = DeepSeekClient()
    
    # Test prompts
    test_prompts = [
        "What is Python?",
        "Explain machine learning in one sentence",
        "What is the capital of France?",
        "Write a haiku about programming",
        "What is 2+2?",
        "Explain quantum computing briefly",
        "What is JavaScript?",
        "Define artificial intelligence"
    ]
    
    print(f"Testing with {len(test_prompts)} prompts...")
    print()
    
    # Test 1: Sequential Processing (Original)
    print("🔄 Test 1: Sequential Processing")
    start_time = time.time()
    
    sequential_responses = []
    for i, prompt in enumerate(test_prompts, 1):
        print(f"Processing {i}/{len(test_prompts)}...", end='\r')
        response = client.chat(prompt, temperature=0.1, max_tokens=50)
        sequential_responses.append(response)
    
    sequential_time = time.time() - start_time
    print(f"✅ Sequential time: {sequential_time:.2f} seconds")
    print()
    
    # Test 2: Concurrent Processing (New)
    print("🔄 Test 2: Concurrent Processing")
    start_time = time.time()
    
    concurrent_responses = asyncio.run(
        client.batch_chat_concurrent(
            test_prompts,
            temperature=0.1,
            max_tokens=50,
            max_workers=4
        )
    )
    
    concurrent_time = time.time() - start_time
    print(f"✅ Concurrent time: {concurrent_time:.2f} seconds")
    print()
    
    # Results
    improvement = ((sequential_time - concurrent_time) / sequential_time) * 100
    speedup = sequential_time / concurrent_time
    
    print("📊 PERFORMANCE RESULTS")
    print("-" * 40)
    print(f"Sequential time: {sequential_time:.2f}s")
    print(f"Concurrent time: {concurrent_time:.2f}s")
    print(f"Speed improvement: {improvement:.1f}%")
    print(f"Speedup factor: {speedup:.1f}x")
    print()
    
    # Verify responses are similar quality
    print("🔍 QUALITY CHECK")
    print("-" * 40)
    print("First prompt responses:")
    print(f"Sequential: {sequential_responses[0][:100]}...")
    print(f"Concurrent: {concurrent_responses[0][:100]}...")
    print()
    
    # Performance stats
    stats = client.get_performance_stats()
    print("📈 USAGE STATISTICS")
    print("-" * 40)
    print(f"Total tokens: {stats['total_tokens']:,}")
    print(f"Cache hit ratio: {stats['cache_hit_ratio']:.1f}%")
    print(f"Estimated cost: ${stats['estimated_cost']:.4f}")
    
    print("\n🎉 Performance test complete!")

if __name__ == "__main__":
    test_performance()