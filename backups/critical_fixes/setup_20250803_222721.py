#!/usr/bin/env python3
"""
üöÄ BASED CODER CLI - Unified Setup System
Made by @Lucariolucario55 on Telegram

Consolidated setup system for the entire BASED CODER CLI
"""

import os
import sys
import subprocess
import json
import shutil
import logging
import asyncio
import getpass
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import colorama
from colorama import Fore, Style
import requests

# Import our configuration and download manager
from config import get_config, update_api_keys, validate_deepseek_key, validate_huggingface_token
from download_manager import DownloadManager

# Initialize colorama
colorama.init()

logger = logging.getLogger(__name__)

class BasedCoderSetup:
    """Unified setup system for BASED CODER CLI"""
    
    def __init__(self) -> Any:
        self.config = get_config()
        self.project_root = Path(__file__).parent
        self.data_dir = self.project_root / "data"
        self.config_dir = self.project_root / "config"
        self.logs_dir = self.project_root / "logs"
        
        # Create necessary directories
        self.data_dir.mkdir(exist_ok=True)
        self.config_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        
        # Setup status
        self.setup_status = {
            "python_deps": False,
            "node_deps": False,
            "models_downloaded": False,
            "config_created": False,
            "database_initialized": False,
            "tools_configured": False,
            "api_keys_setup": False
        }
        
        # Download manager
        self.download_manager = DownloadManager()
    
    def print_banner(self) -> Any:
        """Print setup banner"""
        banner = f"""
{Fore.CYAN}‚ïî‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïó
‚ïë                                                                              ‚ïë
‚ïë  ‚ñà‚ñà‚ñà‚ñà‚ñà‚ñà‚ïó  ‚ñà‚ñà‚ñà‚ñà‚ñà‚ïó ‚ñà‚ñà‚ñà‚ñà‚ñà‚ñà‚ñà‚ïó‚ñà‚ñà‚ñà‚ñà‚ñà‚ñà‚ñà‚ïó‚ñà‚ñà‚ñà‚ñà‚ñà‚ñà‚ïó      ‚ñà‚ñà‚ñà‚ñà‚ñà‚ñà‚ïó ‚ñà‚ñà‚ñà‚ñà‚ñà‚ñà‚ïó ‚ñà‚ñà‚ñà‚ñà‚ñà‚ñà‚ïó ‚ñà‚ñà‚ñà‚ñà‚ñà‚ñà‚ñà‚ïó‚ñà‚ñà‚ñà‚ñà‚ñà‚ñà‚ïó  ‚ïë
‚ïë  ‚ñà‚ñà‚ïî‚ïê‚ïê‚ñà‚ñà‚ïó‚ñà‚ñà‚ïî‚ïê‚ïê‚ñà‚ñà‚ïó‚ñà‚ñà‚ïî‚ïê‚ïê‚ïê‚ïê‚ïù‚ñà‚ñà‚ïî‚ïê‚ïê‚ïê‚ïê‚ïù‚ñà‚ñà‚ïî‚ïê‚ïê‚ñà‚ñà‚ïó    ‚ñà‚ñà‚ïî‚ïê‚ïê‚ïê‚ïê‚ïù‚ñà‚ñà‚ïî‚ïê‚ïê‚ïê‚ñà‚ñà‚ïó‚ñà‚ñà‚ïî‚ïê‚ïê‚ñà‚ñà‚ïó‚ñà‚ñà‚ïî‚ïê‚ïê‚ïê‚ïê‚ïù‚ñà‚ñà‚ïî‚ïê‚ïê‚ñà‚ñà‚ïó ‚ïë
‚ïë  ‚ñà‚ñà‚ñà‚ñà‚ñà‚ñà‚ïî‚ïù‚ñà‚ñà‚ñà‚ñà‚ñà‚ñà‚ñà‚ïë‚ñà‚ñà‚ñà‚ñà‚ñà‚ñà‚ñà‚ïó‚ñà‚ñà‚ñà‚ñà‚ñà‚ñà‚ñà‚ïó‚ñà‚ñà‚ïë  ‚ñà‚ñà‚ïë    ‚ñà‚ñà‚ïë     ‚ñà‚ñà‚ïë   ‚ñà‚ñà‚ïë‚ñà‚ñà‚ïë  ‚ñà‚ñà‚ïë‚ñà‚ñà‚ñà‚ñà‚ñà‚ïó  ‚ñà‚ñà‚ñà‚ñà‚ñà‚ñà‚ïî‚ïù ‚ïë
‚ïë  ‚ñà‚ñà‚ïî‚ïê‚ïê‚ñà‚ñà‚ïó‚ñà‚ñà‚ïî‚ïê‚ïê‚ñà‚ñà‚ïë‚ïö‚ïê‚ïê‚ïê‚ïê‚ñà‚ñà‚ïë‚ïö‚ïê‚ïê‚ïê‚ïê‚ñà‚ñà‚ïë‚ñà‚ñà‚ïë  ‚ñà‚ñà‚ïë    ‚ñà‚ñà‚ïë     ‚ñà‚ñà‚ïë   ‚ñà‚ñà‚ïë‚ñà‚ñà‚ïë  ‚ñà‚ñà‚ïë‚ñà‚ñà‚ïî‚ïê‚ïê‚ïù  ‚ñà‚ñà‚ïî‚ïê‚ïê‚ñà‚ñà‚ïó ‚ïë
‚ïë  ‚ñà‚ñà‚ñà‚ñà‚ñà‚ñà‚ïî‚ïù‚ñà‚ñà‚ïë  ‚ñà‚ñà‚ïë‚ñà‚ñà‚ñà‚ñà‚ñà‚ñà‚ñà‚ïë‚ñà‚ñà‚ñà‚ñà‚ñà‚ñà‚ñà‚ïë‚ñà‚ñà‚ñà‚ñà‚ñà‚ñà‚ïî‚ïù    ‚ïö‚ñà‚ñà‚ñà‚ñà‚ñà‚ñà‚ïó‚ïö‚ñà‚ñà‚ñà‚ñà‚ñà‚ñà‚ïî‚ïù‚ñà‚ñà‚ñà‚ñà‚ñà‚ñà‚ïî‚ïù‚ñà‚ñà‚ñà‚ñà‚ñà‚ñà‚ñà‚ïó‚ñà‚ñà‚ïë  ‚ñà‚ñà‚ïë ‚ïë
‚ïë  ‚ïö‚ïê‚ïê‚ïê‚ïê‚ïê‚ïù ‚ïö‚ïê‚ïù  ‚ïö‚ïê‚ïù‚ïö‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïù‚ïö‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïù‚ïö‚ïê‚ïê‚ïê‚ïê‚ïê‚ïù      ‚ïö‚ïê‚ïê‚ïê‚ïê‚ïê‚ïù ‚ïö‚ïê‚ïê‚ïê‚ïê‚ïê‚ïù ‚ïö‚ïê‚ïê‚ïê‚ïê‚ïê‚ïù ‚ïö‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïù‚ïö‚ïê‚ïù  ‚ïö‚ïê‚ïù ‚ïë
‚ïë                                                                              ‚ïë
‚ïë                    üöÄ BASED CODER CLI - UNIFIED SETUP                        ‚ïë
‚ïë                                                                              ‚ïë
‚ïë                    Made by @Lucariolucario55 on Telegram                     ‚ïë
‚ïë                                                                              ‚ïë
‚ïö‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïù{Style.RESET_ALL}
        """
        logging.info(banner)
    
    def check_python_version(self) -> bool:
        """Check if Python version is compatible"""
        try:
            version = sys.version_info
            if version.major >= 3 and version.minor >= 8:
                logging.info(f"{Fore.GREEN}‚úÖ Python {version.major}.{version.minor}.{version.micro} detected{Style.RESET_ALL}")
                return True
            else:
                logging.info(f"{Fore.RED}‚ùå Python 3.8+ required, found {version.major}.{version.minor}.{version.micro}{Style.RESET_ALL}")
                return False
        except Exception as e:
            logging.info(f"{Fore.RED}‚ùå Error checking Python version: {e}{Style.RESET_ALL}")
            return False
    
    def check_node_version(self) -> bool:
        """Check if Node.js version is compatible"""
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip()
                logging.info(f"{Fore.GREEN}‚úÖ Node.js {version} detected{Style.RESET_ALL}")
                return True
            else:
                logging.info(f"{Fore.RED}‚ùå Node.js not found{Style.RESET_ALL}")
                return False
        except Exception as e:
            logging.info(f"{Fore.RED}‚ùå Error checking Node.js version: {e}{Style.RESET_ALL}")
            return False
    
    def setup_api_keys_interactive(self) -> bool:
        """Interactive API keys setup"""
        logging.info(f"\n{Fore.YELLOW}üîë API Keys Setup{Style.RESET_ALL}")
        logging.info("=" * 50)
        
        # DeepSeek API Key
        logging.info(f"\n{Fore.CYAN}DeepSeek API Key Setup:{Style.RESET_ALL}")
        logging.info("To get a DeepSeek API key:")
        logging.info("1. Visit: https://platform.deepseek.com")
        logging.info("2. Sign up or log in")
        logging.info("3. Go to API Keys section")
        logging.info("4. Create a new API key")
        logging.info()
        
        deepseek_key = getpass.getpass(f"{Fore.YELLOW}Enter your DeepSeek API key (or press Enter to skip): {Style.RESET_ALL}").strip()
        
        # HuggingFace Token
        logging.info(f"\n{Fore.CYAN}HuggingFace Token Setup:{Style.RESET_ALL}")
        logging.info("To get a HuggingFace token:")
        logging.info("1. Visit: https://huggingface.co/settings/tokens")
        logging.info("2. Sign up or log in")
        logging.info("3. Create a new token")
        logging.info()
        
        huggingface_token = getpass.getpass(f"{Fore.YELLOW}Enter your HuggingFace token (or press Enter to skip): {Style.RESET_ALL}").strip()
        
        # Validate and update
        valid_keys = True
        
        if deepseek_key:
            if validate_deepseek_key(deepseek_key):
                update_api_keys(deepseek_key=deepseek_key)
                logging.info(f"{Fore.GREEN}‚úÖ DeepSeek API key updated successfully!{Style.RESET_ALL}")
            else:
                logging.info(f"{Fore.RED}‚ùå Invalid DeepSeek API key format{Style.RESET_ALL}")
                valid_keys = False
        
        if huggingface_token:
            if validate_huggingface_token(huggingface_token):
                update_api_keys(huggingface_token=huggingface_token)
                logging.info(f"{Fore.GREEN}‚úÖ HuggingFace token updated successfully!{Style.RESET_ALL}")
            else:
                logging.info(f"{Fore.RED}‚ùå Invalid HuggingFace token format{Style.RESET_ALL}")
                valid_keys = False
        
        # Create .env file
        env_content = ""
        if deepseek_key:
            env_content += f"DEEPSEEK_API_KEY={deepseek_key}\n"
        if huggingface_token:
            env_content += f"HUGGINGFACE_API_KEY={huggingface_token}\n"
        
        if env_content:
            env_file = self.project_root / ".env"
            with open(env_file, 'w') as f:
                f.write(env_content)
            logging.info(f"{Fore.GREEN}‚úÖ .env file created{Style.RESET_ALL}")
        
        self.setup_status["api_keys_setup"] = valid_keys
        return valid_keys
    
    async def install_dependencies(self) -> bool:
        """Install all dependencies"""
        logging.info(f"\n{Fore.YELLOW}üì¶ Installing Dependencies{Style.RESET_ALL}")
        logging.info("=" * 50)
        
        # Install Python dependencies
        logging.info(f"\n{Fore.CYAN}Installing Python dependencies...{Style.RESET_ALL}")
        success = await self.download_manager.install_python_dependencies()
        if success:
            self.setup_status["python_deps"] = True
        
        # Install Node.js dependencies
        logging.info(f"\n{Fore.CYAN}Installing Node.js dependencies...{Style.RESET_ALL}")
        success = await self.download_manager.install_node_dependencies()
        if success:
            self.setup_status["node_deps"] = True
        
        # Build TypeScript
        logging.info(f"\n{Fore.CYAN}Building TypeScript...{Style.RESET_ALL}")
        await self.download_manager.build_typescript()
        
        return self.setup_status["python_deps"] and self.setup_status["node_deps"]
    
    async def download_models(self) -> bool:
        """Download required models"""
        logging.info(f"\n{Fore.YELLOW}üì• Downloading Models{Style.RESET_ALL}")
        logging.info("=" * 50)
        
        # Validate credentials first
        if not self.download_manager.validate_credentials():
            logging.info(f"{Fore.RED}‚ùå API credentials not valid. Please run setup again.{Style.RESET_ALL}")
            return False
        
        # Download Qwen model
        logging.info(f"\n{Fore.CYAN}Downloading Qwen3 embedding model...{Style.RESET_ALL}")
        success = await self.download_manager.download_qwen_model()
        
        # Download GGUF models
        logging.info(f"\n{Fore.CYAN}Downloading GGUF models...{Style.RESET_ALL}")
        success = await self.download_manager.download_gguf_models()
        
        if success:
            self.setup_status["models_downloaded"] = True
        
        return success
    
    def initialize_database(self) -> bool:
        """Initialize database and tables"""
        logging.info(f"\n{Fore.YELLOW}üóÑÔ∏è Initializing Database{Style.RESET_ALL}")
        logging.info("=" * 50)
        
        try:
            import sqlite3
            
            # Create database directory
            db_dir = Path(self.config.database.sqlite_path).parent
            db_dir.mkdir(parents=True, exist_ok=True)
            
            # Initialize database
            conn = sqlite3.connect(self.config.database.sqlite_path)
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS personas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    personality_traits TEXT,
                    knowledge_base TEXT,
                    conversation_style TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    embedding BLOB,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    user_message TEXT NOT NULL,
                    assistant_message TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logging.info(f"{Fore.GREEN}‚úÖ Database initialized successfully{Style.RESET_ALL}")
            self.setup_status["database_initialized"] = True
            return True
            
        except Exception as e:
            logging.info(f"{Fore.RED}‚ùå Failed to initialize database: {e}{Style.RESET_ALL}")
            return False
    
    def configure_tools(self) -> bool:
        """Configure tools and systems"""
        logging.info(f"\n{Fore.YELLOW}üõ†Ô∏è Configuring Tools{Style.RESET_ALL}")
        logging.info("=" * 50)
        
        try:
            # Create tools configuration
            tools_config = {
                "embedding_system": {
                    "type": "qwen3",
                    "model_path": str(self.data_dir / "models" / "qwen3_embedding"),
                    "enabled": True
                },
                "vector_database": {
                    "type": "qdrant",
                    "host": self.config.database.vector_db_host,
                    "port": self.config.database.vector_db_port,
                    "enabled": self.config.features.enable_vector_database
                },
                "rag_pipeline": {
                    "enabled": self.config.features.enable_rag_pipeline,
                    "max_context_length": self.config.rag.max_context_length,
                    "similarity_threshold": self.config.rag.similarity_threshold
                },
                "memory_system": {
                    "enabled": self.config.features.enable_emotional_intelligence,
                    "max_entries": self.config.memory.max_memory_entries,
                    "retention_days": self.config.memory.memory_retention_days
                }
            }
            
            # Save tools configuration
            tools_config_file = self.config_dir / "tools_config.json"
            with open(tools_config_file, 'w') as f:
                json.dump(tools_config, f, indent=2)
            
            logging.info(f"{Fore.GREEN}‚úÖ Tools configured successfully{Style.RESET_ALL}")
            self.setup_status["tools_configured"] = True
            return True
            
        except Exception as e:
            logging.info(f"{Fore.RED}‚ùå Failed to configure tools: {e}{Style.RESET_ALL}")
            return False
    
    def create_startup_scripts(self) -> bool:
        """Create startup scripts"""
        logging.info(f"\n{Fore.YELLOW}üöÄ Creating Startup Scripts{Style.RESET_ALL}")
        logging.info("=" * 50)
        
        try:
            # Create main.py if it doesn't exist
            main_py = self.project_root / "main.py"
            if not main_py.exists():
                main_content = '''#!/usr/bin/env python3
"""
üöÄ BASED CODER CLI - Main Entry Point
Made by @Lucariolucario55 on Telegram
"""

import asyncio
from main import main

if __name__ == "__main__":
    asyncio.run(main())
'''
                with open(main_py, 'w') as f:
                    f.write(main_content)
                
                # Make executable
                os.chmod(main_py, 0o755)
                logging.info(f"{Fore.GREEN}‚úÖ Created main.py{Style.RESET_ALL}")
            
            # Create batch file for Windows
            if os.name == 'nt':
                batch_file = self.project_root / "run.bat"
                batch_content = '''@echo off
echo Starting BASED CODER CLI...
python main.py
pause
'''
                with open(batch_file, 'w') as f:
                    f.write(batch_content)
                logging.info(f"{Fore.GREEN}‚úÖ Created run.bat{Style.RESET_ALL}")
            
            # Create shell script for Unix
            else:
                shell_file = self.project_root / "run.sh"
                shell_content = '''#!/bin/bash
echo "Starting BASED CODER CLI..."
python3 main.py
'''
                with open(shell_file, 'w') as f:
                    f.write(shell_content)
                
                # Make executable
                os.chmod(shell_file, 0o755)
                logging.info(f"{Fore.GREEN}‚úÖ Created run.sh{Style.RESET_ALL}")
            
            return True
            
        except Exception as e:
            logging.info(f"{Fore.RED}‚ùå Failed to create startup scripts: {e}{Style.RESET_ALL}")
            return False
    
    async def run_tests(self) -> bool:
        """Run system tests"""
        logging.info(f"\n{Fore.YELLOW}üß™ Running System Tests{Style.RESET_ALL}")
        logging.info("=" * 50)
        
        try:
            # Import test suite
            from test_suite import run_all_tests
            
            # Run tests
            test_results = await run_all_tests()
            
            # Print results
            success_count = sum(1 for result in test_results.values() if result)
            total_count = len(test_results)
            
            logging.info(f"\n{Fore.CYAN}Test Results:{Style.RESET_ALL}")
            for test_name, success in test_results.items():
                status_icon = "‚úÖ" if success else "‚ùå"
                logging.info(f"  {status_icon} {test_name}")
            
            logging.info(f"\n{Fore.GREEN}‚úÖ {success_count}/{total_count} tests passed{Style.RESET_ALL}")
            
            return success_count == total_count
            
        except Exception as e:
            logging.info(f"{Fore.RED}‚ùå Failed to run tests: {e}{Style.RESET_ALL}")
            return False
    
    def print_setup_summary(self) -> Any:
        """Print setup summary"""
        logging.info(f"\n{Fore.CYAN}üìä SETUP SUMMARY{Style.RESET_ALL}")
        logging.info("=" * 60)
        
        for component, status in self.setup_status.items():
            status_icon = "‚úÖ" if status else "‚ùå"
            component_name = component.replace("_", " ").title()
            logging.info(f"{status_icon} {component_name}")
        
        logging.info("=" * 60)
        
        # Overall status
        success_count = sum(self.setup_status.values())
        total_count = len(self.setup_status)
        
        if success_count == total_count:
            logging.info(f"{Fore.GREEN}üéâ Setup completed successfully!{Style.RESET_ALL}")
            logging.info(f"\n{Fore.YELLOW}Next steps:{Style.RESET_ALL}")
            logging.info("1. Run: python main.py")
            logging.info("2. Or use: ./run.sh (Unix) or run.bat (Windows)")
        else:
            logging.info(f"{Fore.YELLOW}‚ö†Ô∏è {success_count}/{total_count} components setup successfully{Style.RESET_ALL}")
            logging.info(f"\n{Fore.RED}Some components failed. Please check the errors above.{Style.RESET_ALL}")
    
    async def run_complete_setup(self) -> bool:
        """Run complete setup process"""
        self.print_banner()
        
        logging.info(f"{Fore.CYAN}üöÄ Starting BASED CODER CLI Setup...{Style.RESET_ALL}")
        
        # Check system requirements
        logging.info(f"\n{Fore.YELLOW}üîç Checking System Requirements{Style.RESET_ALL}")
        logging.info("=" * 50)
        
        if not self.check_python_version():
            return False
        
        if not self.check_node_version():
            logging.info(f"{Fore.YELLOW}‚ö†Ô∏è Node.js not found. Some features may not work.{Style.RESET_ALL}")
        
        # Setup API keys
        self.setup_api_keys_interactive()
        
        # Install dependencies
        await self.install_dependencies()
        
        # Download models
        await self.download_models()
        
        # Initialize database
        self.initialize_database()
        
        # Configure tools
        self.configure_tools()
        
        # Create startup scripts
        self.create_startup_scripts()
        
        # Run tests
        await self.run_tests()
        
        # Print summary
        self.print_setup_summary()
        
        return True

# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

async def setup_complete() -> None:
    """Run complete setup"""
    setup = BasedCoderSetup()
    return await setup.run_complete_setup()

async def setup_api_keys() -> None:
    """Setup only API keys"""
    setup = BasedCoderSetup()
    return setup.setup_api_keys_interactive()

async def setup_dependencies() -> None:
    """Setup only dependencies"""
    setup = BasedCoderSetup()
    return await setup.install_dependencies()

async def setup_models() -> None:
    """Setup only models"""
    setup = BasedCoderSetup()
    return await setup.download_models()

def setup_database() -> None:
    """Setup only database"""
    setup = BasedCoderSetup()
    return setup.initialize_database()

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

async def main() -> None:
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="BASED CODER CLI Setup")
    parser.add_argument("--complete", action="store_true", help="Run complete setup")
    parser.add_argument("--api-keys", action="store_true", help="Setup only API keys")
    parser.add_argument("--deps", action="store_true", help="Setup only dependencies")
    parser.add_argument("--models", action="store_true", help="Setup only models")
    parser.add_argument("--database", action="store_true", help="Setup only database")
    
    args = parser.parse_args()
    
    if args.complete:
        await setup_complete()
    elif args.api_keys:
        await setup_api_keys()
    elif args.deps:
        await setup_dependencies()
    elif args.models:
        await setup_models()
    elif args.database:
        setup_database()
    else:
        # Default: complete setup
        await setup_complete()

if __name__ == "__main__":
    asyncio.run(main()) 