#!/usr/bin/env python3
"""
Update API Key Script
Simple script to update the DeepSeek API key
"""

import os
import sys
from config.api_keys import update_deepseek_api_key, print_api_status

def main():
    """Main function to update API key"""
    print("🔑 DeepSeek API Key Update Tool")
    print("=" * 40)
    
    # Show current status
    print_api_status()
    print()
    
    # Get new API key
    print("To get a DeepSeek API key:")
    print("1. Visit: https://platform.deepseek.com")
    print("2. Sign up or log in")
    print("3. Go to API Keys section")
    print("4. Create a new API key")
    print()
    
    new_key = input("Enter your DeepSeek API key (or press Enter to skip): ").strip()
    
    if new_key:
        if new_key.startswith("sk-") and len(new_key) > 20:
            # Update the key
            update_deepseek_api_key(new_key)
            
            # Update environment variable for current session
            os.environ["DEEPSEEK_API_KEY"] = new_key
            
            print("✅ API key updated successfully!")
            print("Note: This update is for the current session only.")
            print("For permanent update, set the DEEPSEEK_API_KEY environment variable.")
            
        else:
            print("❌ Invalid API key format. DeepSeek API keys should start with 'sk-' and be longer than 20 characters.")
    else:
        print("⏭️ Skipping API key update.")
    
    print()
    print("Current API status:")
    print_api_status()

if __name__ == "__main__":
    main() 