#!/usr/bin/env python3
"""
Test DeepSeek API Key
"""

import os
import httpx
import asyncio
import json

async def test_deepseek_api():
    """Test if the DeepSeek API key is working"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise EnvironmentError("DEEPSEEK_API_KEY environment variable not set")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, please respond with 'API is working!' if you receive this."},
        ],
        "max_tokens": 50,
        "temperature": 0.7,
    }

    print("Testing DeepSeek API key...")
    print(f"API Key: {api_key[:6]}...")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30.0,
            )

            print(f"Status Code: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                print("✅ API Key is working!")
                print("Response:", result.get("choices", [{}])[0].get("message", {}).get("content", ""))
                return True
            else:
                print("❌ API Error:")
                print(response.text)
                return False

    except Exception as e:
        print(f"❌ Connection Error: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(test_deepseek_api())

