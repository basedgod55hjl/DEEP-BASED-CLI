#!/usr/bin/env python3
"""
🔑 API Keys Setup Script for BASED CODER CLI
Interactive script to configure API keys and create .env file
Made by @Lucariolucario55 on Telegram
"""

import os
import sys
from pathlib import Path
import colorama
from colorama import Fore, Style
import getpass

# Initialize colorama for Windows compatibility
colorama.init()

def print_banner():
    """Print the setup banner"""
    banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  ██████╗  █████╗ ███████╗███████╗██████╗      ██████╗ ██████╗ ██████╗ ███████╗██████╗  ║
║  ██╔══██╗██╔══██╗██╔════╝██╔════╝██╔══██╗    ██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔══██╗ ║
║  ██████╔╝███████║███████╗███████╗██║  ██║    ██║     ██║   ██║██║  ██║█████╗  ██████╔╝ ║
║  ██╔══██╗██╔══██║╚════██║╚════██║██║  ██║    ██║     ██║   ██║██║  ██║██╔══╝  ██╔══██╗ ║
║  ██████╔╝██║  ██║███████║███████║██████╔╝    ╚██████╗╚██████╔╝██████╔╝███████╗██║  ██║ ║
║  ╚═════╝ ╚═╝  ╚═╝╚══════╝╚══════╝╚═════╝      ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝ ║
║                                                                              ║
║                    🔑 API Keys Configuration Setup                           ║
║                                                                              ║
║                    Made by @Lucariolucario55 on Telegram                     ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
    """
    print(banner)

def validate_deepseek_key(api_key: str) -> bool:
    """Validate DeepSeek API key format"""
    if not api_key:
        return False
    if not api_key.startswith("sk-"):
        return False
    if len(api_key) < 20:
        return False
    return True

def validate_huggingface_token(token: str) -> bool:
    """Validate HuggingFace token format"""
    if not token:
        return False
    if not token.startswith("hf_"):
        return False
    if len(token) < 10:
        return False
    return True

def get_api_key_input(prompt: str, validator_func, is_password: bool = True) -> str:
    """Get API key input with validation"""
    while True:
        try:
            if is_password:
                api_key = getpass.getpass(f"{Fore.YELLOW}{prompt}{Style.RESET_ALL}")
            else:
                api_key = input(f"{Fore.YELLOW}{prompt}{Style.RESET_ALL}")
            
            if not api_key.strip():
                print(f"{Fore.RED}❌ API key cannot be empty. Please try again.{Style.RESET_ALL}")
                continue
            
            if validator_func(api_key.strip()):
                return api_key.strip()
            else:
                print(f"{Fore.RED}❌ Invalid API key format. Please check and try again.{Style.RESET_ALL}")
                
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}⚠️ Setup cancelled by user.{Style.RESET_ALL}")
            sys.exit(0)
        except Exception as e:
            print(f"{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}")

def create_env_file(env_content: str):
    """Create .env file with API keys"""
    try:
        env_path = Path(".env")
        
        # Check if .env already exists
        if env_path.exists():
            backup_path = Path(".env.backup")
            if not backup_path.exists():
                env_path.rename(backup_path)
                print(f"{Fore.CYAN}📁 Backed up existing .env to .env.backup{Style.RESET_ALL}")
            else:
                env_path.unlink()
                print(f"{Fore.CYAN}📁 Replaced existing .env file{Style.RESET_ALL}")
        
        # Write new .env file
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        print(f"{Fore.GREEN}✅ .env file created successfully!{Style.RESET_ALL}")
        return True
        
    except Exception as e:
        print(f"{Fore.RED}❌ Error creating .env file: {str(e)}{Style.RESET_ALL}")
        return False

def update_config_files(deepseek_key: str, huggingface_token: str):
    """Update configuration files with new API keys"""
    try:
        # Update api_keys.py
        api_keys_path = Path("config/api_keys.py")
        if api_keys_path.exists():
            with open(api_keys_path, 'r') as f:
                content = f.read()
            
            # Update DeepSeek API key
            content = content.replace(
                'DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-your-api-key")',
                f'DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "{deepseek_key}")'
            )
            
            # Update HuggingFace API key
            content = content.replace(
                'HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "hf-your-api-token")',
                f'HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "{huggingface_token}")'
            )
            
            with open(api_keys_path, 'w') as f:
                f.write(content)
            
            print(f"{Fore.GREEN}✅ Updated config/api_keys.py{Style.RESET_ALL}")
        
        # Update deepcli_config.py
        config_path = Path("config/deepcli_config.py")
        if config_path.exists():
            with open(config_path, 'r') as f:
                content = f.read()
            
            # Update DeepSeek API key in LLMConfig
            content = content.replace(
                'api_key: str = "sk-your-api-key"',
                f'api_key: str = "{deepseek_key}"'
            )
            
            with open(config_path, 'w') as f:
                f.write(content)
            
            print(f"{Fore.GREEN}✅ Updated config/deepcli_config.py{Style.RESET_ALL}")
        
        return True
        
    except Exception as e:
        print(f"{Fore.RED}❌ Error updating config files: {str(e)}{Style.RESET_ALL}")
        return False

def test_api_keys(deepseek_key: str, huggingface_token: str):
    """Test the API keys to ensure they work"""
    print(f"\n{Fore.CYAN}🧪 Testing API keys...{Style.RESET_ALL}")
    
    # Test DeepSeek API key
    try:
        import requests
        
        headers = {
            "Authorization": f"Bearer {deepseek_key}",
            "Content-Type": "application/json"
        }
        
        # Simple test request
        test_data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 10
        }
        
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"{Fore.GREEN}✅ DeepSeek API key is valid and working{Style.RESET_ALL}")
        elif response.status_code == 401:
            print(f"{Fore.RED}❌ DeepSeek API key is invalid{Style.RESET_ALL}")
        elif response.status_code == 402:
            print(f"{Fore.YELLOW}⚠️ DeepSeek API key is valid but account has insufficient balance{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}⚠️ DeepSeek API key test returned status {response.status_code}{Style.RESET_ALL}")
            
    except Exception as e:
        print(f"{Fore.YELLOW}⚠️ Could not test DeepSeek API key: {str(e)}{Style.RESET_ALL}")
    
    # Test HuggingFace token
    try:
        headers = {
            "Authorization": f"Bearer {huggingface_token}"
        }
        
        response = requests.get(
            "https://huggingface.co/api/whoami",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"{Fore.GREEN}✅ HuggingFace token is valid (User: {user_info.get('name', 'Unknown')}){Style.RESET_ALL}")
        elif response.status_code == 401:
            print(f"{Fore.RED}❌ HuggingFace token is invalid{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}⚠️ HuggingFace token test returned status {response.status_code}{Style.RESET_ALL}")
            
    except Exception as e:
        print(f"{Fore.YELLOW}⚠️ Could not test HuggingFace token: {str(e)}{Style.RESET_ALL}")

def main():
    """Main setup function"""
    print_banner()
    
    print(f"{Fore.CYAN}🔧 Welcome to the BASED CODER CLI API Keys Setup!{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}This script will help you configure your API keys for the BASED CODER CLI.{Style.RESET_ALL}")
    print()
    
    # Get DeepSeek API key
    print(f"{Fore.BLUE}📋 Step 1: DeepSeek API Key{Style.RESET_ALL}")
    print(f"{Fore.WHITE}To get your DeepSeek API key:{Style.RESET_ALL}")
    print(f"  1. Visit https://platform.deepseek.com")
    print(f"  2. Sign up or log in to your account")
    print(f"  3. Go to API Keys section")
    print(f"  4. Create a new API key")
    print(f"  5. Copy the key (starts with 'sk-')")
    print()
    
    deepseek_key = get_api_key_input(
        "🔑 Enter your DeepSeek API key (sk-...): ",
        validate_deepseek_key,
        is_password=True
    )
    
    print(f"{Fore.GREEN}✅ DeepSeek API key received{Style.RESET_ALL}")
    print()
    
    # Get HuggingFace token
    print(f"{Fore.BLUE}📋 Step 2: HuggingFace Token{Style.RESET_ALL}")
    print(f"{Fore.WHITE}To get your HuggingFace token:{Style.RESET_ALL}")
    print(f"  1. Visit https://huggingface.co")
    print(f"  2. Sign up or log in to your account")
    print(f"  3. Go to Settings > Access Tokens")
    print(f"  4. Create a new token")
    print(f"  5. Copy the token (starts with 'hf_')")
    print()
    
    huggingface_token = get_api_key_input(
        "🔑 Enter your HuggingFace token (hf_...): ",
        validate_huggingface_token,
        is_password=True
    )
    
    print(f"{Fore.GREEN}✅ HuggingFace token received{Style.RESET_ALL}")
    print()
    
    # Create .env file
    print(f"{Fore.BLUE}📋 Step 3: Creating .env file{Style.RESET_ALL}")
    
    env_content = f"""# BASED CODER CLI Environment Variables
# Generated by setup_api_keys.py
# Made by @Lucariolucario55 on Telegram

# DeepSeek API Configuration
DEEPSEEK_API_KEY={deepseek_key}
DEEPSEEK_BASE_URL=https://api.deepseek.com

# HuggingFace API Configuration
HUGGINGFACE_API_KEY={huggingface_token}

# Qdrant Configuration (Optional)
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_API_KEY=

# Environment
ENVIRONMENT=development
"""
    
    if create_env_file(env_content):
        print(f"{Fore.GREEN}✅ Environment file created successfully!{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}❌ Failed to create environment file{Style.RESET_ALL}")
        return False
    
    # Update configuration files
    print(f"\n{Fore.BLUE}📋 Step 4: Updating configuration files{Style.RESET_ALL}")
    if update_config_files(deepseek_key, huggingface_token):
        print(f"{Fore.GREEN}✅ Configuration files updated successfully!{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}⚠️ Some configuration files could not be updated{Style.RESET_ALL}")
    
    # Test API keys
    test_api_keys(deepseek_key, huggingface_token)
    
    # Final summary
    print(f"\n{Fore.CYAN}🎉 Setup Complete!{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✅ API keys have been configured successfully{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✅ .env file created with your API keys{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✅ Configuration files updated{Style.RESET_ALL}")
    print()
    
    print(f"{Fore.YELLOW}🚀 You can now run the BASED CODER CLI:{Style.RESET_ALL}")
    print(f"   python based_coder_cli.py")
    print()
    
    print(f"{Fore.CYAN}📝 Important Notes:{Style.RESET_ALL}")
    print(f"  • Your API keys are stored in the .env file")
    print(f"  • The .env file is ignored by git for security")
    print(f"  • Keep your API keys secure and don't share them")
    print(f"  • You can update keys anytime by running this script again")
    print()
    
    print(f"{Fore.MAGENTA}💡 Need help? Contact @Lucariolucario55 on Telegram{Style.RESET_ALL}")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print(f"\n{Fore.GREEN}🎯 Setup completed successfully!{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}❌ Setup failed. Please check the errors above.{Style.RESET_ALL}")
            sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}👋 Setup cancelled by user.{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}❌ Unexpected error: {str(e)}{Style.RESET_ALL}")
        sys.exit(1) 