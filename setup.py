#!/usr/bin/env python3
"""
🚀 BASED CODER CLI - Setup Script
Made by @Lucariolucario55 on Telegram
"""

import os
import sys
import subprocess
from pathlib import Path
import argparse
from dotenv import load_dotenv

# Colors for output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'

def print_banner():
    """Print setup banner"""
    print(f"""{Colors.CYAN}
╔══════════════════════════════════════════════════════════════════════════════╗
║                      🚀 BASED CODER CLI - SETUP                               ║
║                    Made by @Lucariolucario55 on Telegram                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
{Colors.RESET}""")

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    if sys.version_info < (3, 8):
        print(f"{Colors.RED}❌ Python 3.8 or higher is required. You have Python {sys.version}{Colors.RESET}")
        sys.exit(1)
    print(f"{Colors.GREEN}✅ Python {sys.version.split()[0]} detected{Colors.RESET}")

def install_dependencies():
    """Install Python dependencies"""
    print(f"\n{Colors.CYAN}📦 Installing Python dependencies...{Colors.RESET}")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print(f"{Colors.GREEN}✅ Python dependencies installed successfully{Colors.RESET}")
    except subprocess.CalledProcessError:
        print(f"{Colors.RED}❌ Failed to install Python dependencies{Colors.RESET}")
        return False
    return True

def check_node():
    """Check if Node.js is installed"""
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"{Colors.GREEN}✅ Node.js {version} detected{Colors.RESET}")
            return True
    except FileNotFoundError:
        pass
    
    print(f"{Colors.YELLOW}⚠️  Node.js not found. TypeScript components will not be available.{Colors.RESET}")
    return False

def install_node_dependencies():
    """Install Node.js dependencies"""
    if not Path("package.json").exists():
        print(f"{Colors.YELLOW}⚠️  No package.json found. Skipping Node.js dependencies.{Colors.RESET}")
        return True
    
    print(f"\n{Colors.CYAN}📦 Installing Node.js dependencies...{Colors.RESET}")
    try:
        subprocess.run(["npm", "install"], check=True)
        print(f"{Colors.GREEN}✅ Node.js dependencies installed successfully{Colors.RESET}")
        return True
    except subprocess.CalledProcessError:
        print(f"{Colors.RED}❌ Failed to install Node.js dependencies{Colors.RESET}")
        return False
    except FileNotFoundError:
        print(f"{Colors.YELLOW}⚠️  npm not found. Skipping Node.js dependencies.{Colors.RESET}")
        return False

def setup_api_keys():
    """Setup API keys interactively"""
    print(f"\n{Colors.CYAN}🔑 Setting up API keys...{Colors.RESET}")
    
    env_file = Path(".env")
    env_content = []
    
    # Load existing .env if it exists
    existing_env = {}
    if env_file.exists():
        load_dotenv()
        print(f"{Colors.YELLOW}⚠️  Existing .env file found. New values will override existing ones.{Colors.RESET}")
    
    # DeepSeek API Key (Required)
    print(f"\n{Colors.CYAN}1. DeepSeek API Key (Required){Colors.RESET}")
    print("   Get your key from: https://platform.deepseek.com/")
    deepseek_key = input("   Enter your DeepSeek API key (or press Enter to skip): ").strip()
    if deepseek_key:
        env_content.append(f"DEEPSEEK_API_KEY={deepseek_key}")
    elif not os.getenv("DEEPSEEK_API_KEY"):
        print(f"{Colors.YELLOW}   ⚠️  No DeepSeek API key provided. Some features will be limited.{Colors.RESET}")
    
    # HuggingFace Token (Required for embeddings)
    print(f"\n{Colors.CYAN}2. HuggingFace Token (Required for embeddings){Colors.RESET}")
    print("   Get your token from: https://huggingface.co/settings/tokens")
    hf_token = input("   Enter your HuggingFace token (or press Enter to skip): ").strip()
    if hf_token:
        env_content.append(f"HUGGINGFACE_API_KEY={hf_token}")
    elif not os.getenv("HUGGINGFACE_API_KEY"):
        print(f"{Colors.YELLOW}   ⚠️  No HuggingFace token provided. Embedding features will be limited.{Colors.RESET}")
    
    # OpenAI API Key (Optional)
    print(f"\n{Colors.CYAN}3. OpenAI API Key (Optional){Colors.RESET}")
    print("   Get your key from: https://platform.openai.com/api-keys")
    openai_key = input("   Enter your OpenAI API key (or press Enter to skip): ").strip()
    if openai_key:
        env_content.append(f"OPENAI_API_KEY={openai_key}")
    
    # Anthropic API Key (Optional)
    print(f"\n{Colors.CYAN}4. Anthropic API Key (Optional){Colors.RESET}")
    print("   Get your key from: https://console.anthropic.com/")
    anthropic_key = input("   Enter your Anthropic API key (or press Enter to skip): ").strip()
    if anthropic_key:
        env_content.append(f"ANTHROPIC_API_KEY={anthropic_key}")
    
    # Write .env file
    if env_content:
        with open(env_file, "w") as f:
            f.write("\n".join(env_content) + "\n")
        print(f"\n{Colors.GREEN}✅ API keys saved to .env file{Colors.RESET}")
    else:
        print(f"\n{Colors.YELLOW}⚠️  No API keys were configured{Colors.RESET}")

def create_directories():
    """Create necessary directories"""
    directories = [
        "logs",
        "data",
        "data/embeddings",
        "data/models",
        "data/chats",
        "config/backup"
    ]
    
    print(f"\n{Colors.CYAN}📁 Creating directories...{Colors.RESET}")
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    print(f"{Colors.GREEN}✅ Directories created{Colors.RESET}")

def main():
    """Main setup function"""
    parser = argparse.ArgumentParser(description="Setup BASED CODER CLI")
    parser.add_argument("--api-keys", action="store_true", help="Only setup API keys")
    parser.add_argument("--skip-node", action="store_true", help="Skip Node.js setup")
    args = parser.parse_args()
    
    print_banner()
    
    if args.api_keys:
        setup_api_keys()
        return
    
    # Full setup
    print(f"{Colors.CYAN}Starting setup process...{Colors.RESET}\n")
    
    # Check Python version
    check_python_version()
    
    # Create directories
    create_directories()
    
    # Install Python dependencies
    if not install_dependencies():
        print(f"\n{Colors.RED}❌ Setup failed. Please check the error messages above.{Colors.RESET}")
        sys.exit(1)
    
    # Check and install Node.js dependencies
    if not args.skip_node and check_node():
        install_node_dependencies()
    
    # Setup API keys
    setup_api_keys()
    
    print(f"\n{Colors.GREEN}✨ Setup completed successfully!{Colors.RESET}")
    print(f"\n{Colors.CYAN}To start the CLI, run:{Colors.RESET}")
    print(f"  {Colors.YELLOW}python main.py{Colors.RESET}")
    print(f"\n{Colors.CYAN}For help, run:{Colors.RESET}")
    print(f"  {Colors.YELLOW}python main.py --help{Colors.RESET}")
    print(f"\n{Colors.GREEN}Made by @Lucariolucario55 on Telegram{Colors.RESET}")

if __name__ == "__main__":
    main()