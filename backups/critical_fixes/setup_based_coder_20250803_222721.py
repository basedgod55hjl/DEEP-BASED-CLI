import logging
logger = logging.getLogger(__name__)
#!/usr/bin/env python3
"""
🚀 BASED CODER Setup Script
Comprehensive setup for the BASED CODER CLI system
Made by @Lucariolucario55 on Telegram
"""

import os
import sys
import subprocess
import json
import shutil
from pathlib import Path
import logging
import asyncio
from typing import Dict, Any, List

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BasedCoderSetup:
    """Comprehensive setup for BASED CODER CLI"""
    
    def __init__(self) -> Any:
        self.project_root = Path(__file__).parent
        self.data_dir = self.project_root / "data"
        self.models_dir = self.data_dir / "models"
        self.config_dir = self.project_root / "config"
        self.logs_dir = self.project_root / "logs"
        
        # Create necessary directories
        self.data_dir.mkdir(exist_ok=True)
        self.models_dir.mkdir(exist_ok=True)
        self.config_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        
        # Setup status
        self.setup_status = {
            "python_deps": False,
            "node_deps": False,
            "models_downloaded": False,
            "config_created": False,
            "database_initialized": False,
            "tools_configured": False
        }
    
    def print_banner(self) -> Any:
        """Print setup banner"""
        banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  ██████╗  █████╗ ███████╗███████╗██████╗      ██████╗ ██████╗ ██████╗ ███████╗██████╗  ║
║  ██╔══██╗██╔══██╗██╔════╝██╔════╝██╔══██╗    ██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔══██╗ ║
║  ██████╔╝███████║███████╗███████╗██║  ██║    ██║     ██║   ██║██║  ██║█████╗  ██████╔╝ ║
║  ██╔══██╗██╔══██║╚════██║╚════██║██║  ██║    ██║     ██║   ██║██║  ██║██╔══╝  ██╔══██╗ ║
║  ██████╔╝██║  ██║███████║███████║██████╔╝    ╚██████╗╚██████╔╝██████╔╝███████╗██║  ██║ ║
║  ╚═════╝ ╚═╝  ╚═╝╚══════╝╚══════╝╚═════╝      ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝ ║
║                                                                              ║
║                    🚀 BASED CODER Setup Script                               ║
║                                                                              ║
║                    Made by @Lucariolucario55 on Telegram                     ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """
        logger.info(banner)
    
    def check_python_version(self) -> bool:
        """Check if Python version is compatible"""
        try:
            version = sys.version_info
            if version.major >= 3 and version.minor >= 8:
                logger.info(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
                return True
            else:
                logger.error(f"❌ Python 3.8+ required, found {version.major}.{version.minor}.{version.micro}")
                return False
        except Exception as e:
            logger.error(f"❌ Error checking Python version: {e}")
            return False
    
    def check_node_version(self) -> bool:
        """Check if Node.js version is compatible"""
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip()
                logger.info(f"✅ Node.js {version} detected")
                return True
            else:
                logger.error("❌ Node.js not found")
                return False
        except Exception as e:
            logger.error(f"❌ Error checking Node.js version: {e}")
            return False
    
    def install_python_dependencies(self) -> bool:
        """Install Python dependencies"""
        try:
            logger.info("📦 Installing Python dependencies...")
            
            # Install requirements
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', 'requirements_enhanced.txt'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ Python dependencies installed successfully")
                self.setup_status["python_deps"] = True
                return True
            else:
                logger.error(f"❌ Failed to install Python dependencies: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error installing Python dependencies: {e}")
            return False
    
    def install_node_dependencies(self) -> bool:
        """Install Node.js dependencies"""
        try:
            logger.info("📦 Installing Node.js dependencies...")
            
            # Install npm dependencies
            result = subprocess.run(['npm', 'install'], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ Node.js dependencies installed successfully")
                self.setup_status["node_deps"] = True
                return True
            else:
                logger.error(f"❌ Failed to install Node.js dependencies: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error installing Node.js dependencies: {e}")
            return False
    
    def build_typescript(self) -> bool:
        """Build TypeScript code"""
        try:
            logger.info("🔨 Building TypeScript...")
            
            # Build TypeScript
            result = subprocess.run(['npm', 'run', 'build'], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ TypeScript built successfully")
                return True
            else:
                logger.error(f"❌ Failed to build TypeScript: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error building TypeScript: {e}")
            return False
    
    def download_models(self) -> bool:
        """Download required models"""
        try:
            logger.info("📥 Downloading models...")
            
            # Check if models already exist
            qwen_model_path = self.models_dir / "qwen3_embedding"
            if qwen_model_path.exists():
                logger.info("✅ Models already downloaded")
                self.setup_status["models_downloaded"] = True
                return True
            
            # Download Qwen3 model
            from huggingface_hub import snapshot_download
            
            logger.info("📥 Downloading Qwen3 embedding model...")
            snapshot_download(
                repo_id="Qwen/Qwen3-Embedding-0.6B",
                local_dir=str(qwen_model_path),
                token="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"
            )
            
            logger.info("✅ Models downloaded successfully")
            self.setup_status["models_downloaded"] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Error downloading models: {e}")
            return False
    
    def create_configuration(self) -> bool:
        """Create configuration files"""
        try:
            logger.info("⚙️ Creating configuration...")
            
            # Create API keys configuration
            api_keys_config = {
                "deepseek": {
                    "api_key": "sk-90e0dd863b8c4e0d879a02851a0ee194",
                    "base_url": "https://api.deepseek.com/beta",
                    "model": "deepseek-chat"
                },
                "huggingface": {
                    "api_key": "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",
                    "models": {
                        "embedding": "Qwen/Qwen3-Embedding-0.6B",
                        "completion": "Qwen/Qwen3-0.5B"
                    }
                }
            }
            
            config_file = self.config_dir / "api_keys.json"
            with open(config_file, 'w') as f:
                json.dump(api_keys_config, f, indent=2)
            
            # Create main configuration
            main_config = {
                "system": {
                    "name": "BASED CODER CLI",
                    "version": "1.0.0",
                    "author": "@Lucariolucario55 on Telegram",
                    "session_timeout": 3600,
                    "max_conversation_history": 100,
                    "context_cache_size": 50
                },
                "features": {
                    "rainbow_interface": True,
                    "colorful_agents": True,
                    "context_caching": True,
                    "multi_round_conversations": True,
                    "function_calls": True,
                    "reasoning": True,
                    "fim_completion": True,
                    "prefix_completion": True,
                    "rag_pipeline": True,
                    "memory_system": True,
                    "persona_management": True
                },
                "models": {
                    "embedding": {
                        "type": "qwen3",
                        "path": str(self.models_dir / "qwen3_embedding"),
                        "dimension": 1024
                    },
                    "completion": {
                        "type": "deepseek",
                        "model": "deepseek-chat"
                    }
                },
                "database": {
                    "type": "sqlite",
                    "path": str(self.data_dir / "based_coder.db")
                },
                "logging": {
                    "level": "INFO",
                    "file": str(self.logs_dir / "based_coder.log"),
                    "max_size": "10MB",
                    "backup_count": 5
                }
            }
            
            main_config_file = self.config_dir / "based_coder_config.json"
            with open(main_config_file, 'w') as f:
                json.dump(main_config, f, indent=2)
            
            logger.info("✅ Configuration created successfully")
            self.setup_status["config_created"] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating configuration: {e}")
            return False
    
    def initialize_database(self) -> bool:
        """Initialize database"""
        try:
            logger.info("🗄️ Initializing database...")
            
            # Import and initialize database
            sys.path.append(str(self.project_root))
            from tools.sql_database_tool import SQLDatabaseTool
            
            db_tool = SQLDatabaseTool()
            asyncio.run(db_tool.initialize())
            
            logger.info("✅ Database initialized successfully")
            self.setup_status["database_initialized"] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Error initializing database: {e}")
            return False
    
    def configure_tools(self) -> bool:
        """Configure all tools"""
        try:
            logger.info("🔧 Configuring tools...")
            
            # Test tool initialization
            tools_to_test = [
                "simple_embedding_tool",
                "sql_database_tool",
                "llm_query_tool",
                "fim_completion_tool",
                "prefix_completion_tool",
                "rag_pipeline_tool",
                "reasoning_engine",
                "memory_tool",
                "vector_database_tool"
            ]
            
            for tool_name in tools_to_test:
                try:
                    # Import and test tool
                    module = __import__(f"tools.{tool_name}", fromlist=[tool_name])
                    tool_class = getattr(module, tool_name.replace('_', '').title().replace('_', '') + 'Tool')
                    tool = tool_class()
                    asyncio.run(tool.initialize())
                    logger.info(f"✅ {tool_name} configured")
                except Exception as e:
                    logger.warning(f"⚠️ {tool_name} configuration failed: {e}")
            
            logger.info("✅ Tools configured successfully")
            self.setup_status["tools_configured"] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Error configuring tools: {e}")
            return False
    
    def create_startup_scripts(self) -> bool:
        """Create startup scripts"""
        try:
            logger.info("📝 Creating startup scripts...")
            
            # Create Python startup script
            python_script = """#!/usr/bin/env python3
\"\"\"
🚀 BASED CODER CLI - Python Entry Point
\"\"\"

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from based_coder_cli import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
"""
            
            with open(self.project_root / "run_based_coder.py", 'w') as f:
                f.write(python_script)
            
            # Create shell script for Unix/Linux
            shell_script = """#!/bin/bash
# 🚀 BASED CODER CLI - Shell Entry Point

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate virtual environment if it exists
if [ -d "$DIR/venv" ]; then
    source "$DIR/venv/bin/activate"
fi

# Run the Python CLI
python "$DIR/based_coder_cli.py" "$@"
"""
            
            with open(self.project_root / "run_based_coder.sh", 'w') as f:
                f.write(shell_script)
            
            # Make shell script executable
            os.chmod(self.project_root / "run_based_coder.sh", 0o755)
            
            # Create batch script for Windows
            batch_script = """@echo off
REM 🚀 BASED CODER CLI - Windows Entry Point

REM Get the directory of this script
set DIR=%~dp0

REM Activate virtual environment if it exists
if exist "%DIR%venv\\Scripts\\activate.bat" (
    call "%DIR%venv\\Scripts\\activate.bat"
)

REM Run the Python CLI
python "%DIR%based_coder_cli.py" %*
"""
            
            with open(self.project_root / "run_based_coder.bat", 'w') as f:
                f.write(batch_script)
            
            logger.info("✅ Startup scripts created successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating startup scripts: {e}")
            return False
    
    def run_tests(self) -> bool:
        """Run system tests"""
        try:
            logger.info("🧪 Running system tests...")
            
            # Test Python CLI
            result = subprocess.run([
                sys.executable, 'based_coder_cli.py', '--status'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ Python CLI test passed")
            else:
                logger.warning(f"⚠️ Python CLI test failed: {result.stderr}")
            
            # Test Node.js CLI
            result = subprocess.run([
                'node', 'dist/cli/BasedCoderCLI.js', 'status'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ Node.js CLI test passed")
            else:
                logger.warning(f"⚠️ Node.js CLI test failed: {result.stderr}")
            
            logger.info("✅ System tests completed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error running tests: {e}")
            return False
    
    def print_setup_summary(self) -> Any:
        """Print setup summary"""
        logger.info("\n" + "="*80)
        logger.info("🚀 BASED CODER Setup Summary")
        logger.info("="*80)
        
        for step, status in self.setup_status.items():
            icon = "✅" if status else "❌"
            step_name = step.replace('_', ' ').title()
            logger.info(f"{icon} {step_name}")
        
        logger.info("\n" + "="*80)
        logger.info("🎯 Quick Start Commands:")
        logger.info("="*80)
        logger.info("Python CLI:  python based_coder_cli.py")
        logger.info("Node.js CLI: node dist/cli/BasedCoderCLI.js")
        logger.info("Shell:       ./run_based_coder.sh")
        logger.info("Windows:     run_based_coder.bat")
        logger.info("\n" + "="*80)
    
    async def run_complete_setup(self) -> Any:
        """Run complete setup process"""
        self.print_banner()
        
        logger.info("🚀 Starting BASED CODER setup...")
        
        # Check system requirements
        if not self.check_python_version():
            logger.error("❌ Python version check failed")
            return False
        
        if not self.check_node_version():
            logger.error("❌ Node.js version check failed")
            return False
        
        # Install dependencies
        if not self.install_python_dependencies():
            logger.error("❌ Python dependencies installation failed")
            return False
        
        if not self.install_node_dependencies():
            logger.error("❌ Node.js dependencies installation failed")
            return False
        
        # Build TypeScript
        if not self.build_typescript():
            logger.error("❌ TypeScript build failed")
            return False
        
        # Download models
        if not self.download_models():
            logger.error("❌ Model download failed")
            return False
        
        # Create configuration
        if not self.create_configuration():
            logger.error("❌ Configuration creation failed")
            return False
        
        # Initialize database
        if not self.initialize_database():
            logger.error("❌ Database initialization failed")
            return False
        
        # Configure tools
        if not self.configure_tools():
            logger.error("❌ Tool configuration failed")
            return False
        
        # Create startup scripts
        if not self.create_startup_scripts():
            logger.error("❌ Startup script creation failed")
            return False
        
        # Run tests
        if not self.run_tests():
            logger.warning("⚠️ Some tests failed, but setup completed")
        
        # Print summary
        self.print_setup_summary()
        
        logger.info("🎉 BASED CODER setup completed successfully!")
        return True

async def main() -> None:
    """Main setup function"""
    setup = BasedCoderSetup()
    success = await setup.run_complete_setup()
    
    if success:
        logger.info("\n🎉 Setup completed successfully! You can now use BASED CODER CLI.")
        logger.info("💡 Try: python based_coder_cli.py")
    else:
        logger.info("\n❌ Setup failed. Please check the logs and try again.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 