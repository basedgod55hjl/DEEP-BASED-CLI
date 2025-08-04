import logging
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)
#!/usr/bin/env python3
"""
Update API Key Script
Simple script to update the DeepSeek API key
"""

import os
import sys
from config.api_keys import update_deepseek_api_key, print_api_status

def main() -> None:
    """Main function to update API key"""
    logger.info("🔑 DeepSeek API Key Update Tool")
    logger.info("=" * 40)
    
    # Show current status
    print_api_status()
    logger.info()
    
    # Get new API key
    logger.info("To get a DeepSeek API key:")
    logger.info("1. Visit: https://platform.deepseek.com")
    logger.info("2. Sign up or log in")
    logger.info("3. Go to API Keys section")
    logger.info("4. Create a new API key")
    logger.info()
    
    new_key = input("Enter your DeepSeek API key (or press Enter to skip): ").strip()
    
    if new_key:
        if new_key.startswith("sk-") and len(new_key) > 20:
            # Update the key
            update_deepseek_api_key(new_key)
            
            # Update environment variable for current session
            os.environ["DEEPSEEK_API_KEY"] = new_key
            
            logger.info("✅ API key updated successfully!")
            logger.info("Note: This update is for the current session only.")
            logger.info("For permanent update, set the DEEPSEEK_API_KEY environment variable.")
            
        else:
            logger.info("❌ Invalid API key format. DeepSeek API keys should start with 'sk-' and be longer than 20 characters.")
    else:
        logger.info("⏭️ Skipping API key update.")
    
    logger.info()
    logger.info("Current API status:")
    print_api_status()

if __name__ == "__main__":
    main() 