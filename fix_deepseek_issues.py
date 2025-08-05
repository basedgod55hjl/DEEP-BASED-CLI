#!/usr/bin/env python3
"""
Fix DeepSeek API Issues
Script to resolve DeepSeek API balance and configuration issues
"""

import os
import sys
import json
from pathlib import Path

def update_api_key():
    """Update the DeepSeek API key with a new one"""
    
    # New API key (you should replace this with a valid one)
    new_api_key = "sk-your-api-key"
    
    print("🔧 Fixing DeepSeek API Issues...")
    print(f"📝 Current API Key: {new_api_key[:10]}...")
    
    # Update .env file
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
        
        # Replace or add DEEPSEEK_API_KEY
        if "DEEPSEEK_API_KEY=" in content:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith("DEEPSEEK_API_KEY="):
                    lines[i] = f"DEEPSEEK_API_KEY={new_api_key}"
                    break
            content = '\n'.join(lines)
        else:
            content += f"\nDEEPSEEK_API_KEY={new_api_key}"
        
        with open(env_file, 'w') as f:
            f.write(content)
        print("✅ Updated .env file")
    else:
        # Create .env file
        with open(env_file, 'w') as f:
            f.write(f"DEEPSEEK_API_KEY={new_api_key}\n")
        print("✅ Created .env file")
    
    # Update config files
    config_files = [
        "config/api_keys.py",
        "config/deepcli_config.py"
    ]
    
    for config_file in config_files:
        if Path(config_file).exists():
            with open(config_file, 'r') as f:
                content = f.read()
            
            # Replace API key in the file
            content = content.replace(
                'DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-your-api-key")',
                f'DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "{new_api_key}")'
            )
            
            with open(config_file, 'w') as f:
                f.write(content)
            print(f"✅ Updated {config_file}")
    
    # Set environment variable for current session
    os.environ["DEEPSEEK_API_KEY"] = new_api_key
    print("✅ Set environment variable for current session")
    
    print("\n🎯 DeepSeek API Key Updated Successfully!")
    print("📋 Next Steps:")
    print("1. Add balance to your DeepSeek account at: https://platform.deepseek.com")
    print("2. Run: python test_tools.py to verify the fixes")
    print("3. Run: python main.py to start the CLI")

def check_api_balance():
    """Check if the API key has sufficient balance"""
    import requests
    
    api_key = os.getenv("DEEPSEEK_API_KEY", "sk-your-api-key")
    
    try:
        # Test API call
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 10
        }
        
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ API key is working and has sufficient balance")
            return True
        elif response.status_code == 402:
            print("❌ API key has insufficient balance")
            print("💡 Please add balance to your DeepSeek account")
            return False
        else:
            print(f"⚠️ API test returned status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API: {str(e)}")
        return False

def main():
    """Main function"""
    print("🚀 DeepSeek API Issue Fixer")
    print("=" * 40)
    
    # Update API key
    update_api_key()
    
    print("\n🔍 Testing API Key...")
    if check_api_balance():
        print("\n🎉 All issues resolved! You can now run the CLI.")
    else:
        print("\n⚠️ API key needs balance. Please add funds to your DeepSeek account.")
        print("🔗 Visit: https://platform.deepseek.com")

if __name__ == "__main__":
    main() 