#!/usr/bin/env python3
"""
Fix DeepSeek API Issues
Script to resolve DeepSeek API balance and configuration issues
"""

import os
from typing import List, Dict, Any, Optional, Tuple

import logging

import sys
import json
from pathlib import Path

def update_api_key() -> None:
    """Update the DeepSeek API key with a new one"""
    
    # New API key (you should replace this with a valid one)
    new_api_key = "sk-90e0dd863b8c4e0d879a02851a0ee194"
    
    logging.info("üîß Fixing DeepSeek API Issues...")
    logging.info(f"üìù Current API Key: {new_api_key[:10]}...")
    
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
        logging.info("‚úÖ Updated .env file")
    else:
        # Create .env file
        with open(env_file, 'w') as f:
            f.write(f"DEEPSEEK_API_KEY={new_api_key}\n")
        logging.info("‚úÖ Created .env file")
    
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
                'DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-90e0dd863b8c4e0d879a02851a0ee194")',
                f'DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "{new_api_key}")'
            )
            
            with open(config_file, 'w') as f:
                f.write(content)
            logging.info(f"‚úÖ Updated {config_file}")
    
    # Set environment variable for current session
    os.environ["DEEPSEEK_API_KEY"] = new_api_key
    logging.info("‚úÖ Set environment variable for current session")
    
    logging.info("\nüéØ DeepSeek API Key Updated Successfully!")
    logging.info("üìã Next Steps:")
    logging.info("1. Add balance to your DeepSeek account at: https://platform.deepseek.com")
    logging.info("2. Run: python test_tools.py to verify the fixes")
    logging.info("3. Run: python main.py to start the CLI")

def check_api_balance() -> None:
    """Check if the API key has sufficient balance"""
    import requests
    
    api_key = os.getenv("DEEPSEEK_API_KEY", "sk-90e0dd863b8c4e0d879a02851a0ee194")
    
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
            logging.info("‚úÖ API key is working and has sufficient balance")
            return True
        elif response.status_code == 402:
            logging.info("‚ùå API key has insufficient balance")
            logging.info("üí° Please add balance to your DeepSeek account")
            return False
        else:
            logging.info(f"‚ö†Ô∏è API test returned status code: {response.status_code}")
            return False
            
    except Exception as e:
        logging.info(f"‚ùå Error testing API: {str(e)}")
        return False

def main() -> None:
    """Main function"""
    logging.info("üöÄ DeepSeek API Issue Fixer")
    logging.info("=" * 40)
    
    # Update API key
    update_api_key()
    
    logging.info("\nüîç Testing API Key...")
    if check_api_balance():
        logging.info("\nüéâ All issues resolved! You can now run the CLI.")
    else:
        logging.info("\n‚ö†Ô∏è API key needs balance. Please add funds to your DeepSeek account.")
        logging.info("üîó Visit: https://platform.deepseek.com")

if __name__ == "__main__":
    main() 