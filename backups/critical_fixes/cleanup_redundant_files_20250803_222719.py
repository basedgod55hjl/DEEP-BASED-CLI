import logging
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)
#!/usr/bin/env python3
"""
🧹 BASED CODER CLI - Redundant Files Cleanup Script
Made by @Lucariolucario55 on Telegram

This script removes all redundant files that have been consolidated into the unified system.
"""

import os
import shutil
from pathlib import Path
import colorama
from colorama import Fore, Style

# Initialize colorama
colorama.init()

def print_banner() -> None:
    """Print cleanup banner"""
    banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  🧹 BASED CODER CLI - REDUNDANT FILES CLEANUP                               ║
║                                                                              ║
║  This script will remove all redundant files that have been consolidated    ║
║  into the new unified system.                                               ║
║                                                                              ║
║  Made by @Lucariolucario55 on Telegram                                      ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
    """
    logger.info(banner)

def get_redundant_files() -> None:
    """Get list of redundant files to remove"""
    redundant_files = [
        # CLI Entry Points (consolidated into main.py)
        "based_coder_cli.py",
        "enhanced_cli.py", 
        "run_cli.py",
        "enhanced_based_god_cli.py",
        
        # Setup Scripts (consolidated into setup.py)
        "setup_based_coder.py",
        "setup_api_keys.py",
        "setup_complete_deanna_system.py",
        "setup_simple_deanna_system.py",
        "setup_deanna_persona.py",
        "setup_transformers_deanna_system.py",
        
        # Download Scripts (consolidated into download_manager.py)
        "download_qwen_model.py",
        "simple_download.py",
        "download_gguf_models.py",
        
        # Test Scripts (consolidated into test_suite.py)
        "test_final_system.py",
        "test_core_features.py",
        "test_qwen_model.py",
        "simple_test.py",
        
        # Demo Scripts (consolidated into demo.py)
        "demo_deepseek_coder.py",
        "demo_full_system.py",
        
        # Configuration Files (consolidated into config.py)
        "config/deepcli_config.py",
        "config/api_keys.py",
        "config/enhanced_config.json",
        
        # Documentation Files (consolidated into README.md)
        "README_BASED_CODER.md",
        "README_DEANNA_SYSTEM.md",
        "DEEPSEEK_CODER_FEATURES.md",
        "FINAL_SYSTEM_SUMMARY.md",
        "ENHANCED_FEATURES.md",
        "SETUP_SUMMARY.md",
        "SYSTEM_STATUS.md",
        
        # Other redundant files
        "update_api_key.py",
        "deanna_chat_system.py",
        "commit_message.txt",
        "requirements_enhanced.txt",
        
        # Examples (consolidated into demo.py)
        "examples/unified_agent_demo.py",
        "examples/rag_demo.py",
    ]
    
    return redundant_files

def get_redundant_directories() -> None:
    """Get list of redundant directories to remove"""
    redundant_dirs = [
        # Empty or redundant directories
        "examples",  # Content moved to demo.py
    ]
    
    return redundant_dirs

def backup_file(file_path) -> Any:
    """Create backup of file before deletion"""
    try:
        if file_path.exists():
            backup_path = file_path.with_suffix(file_path.suffix + '.backup')
            shutil.copy2(file_path, backup_path)
            return backup_path
    except Exception as e:
        logger.info(f"{Fore.RED}❌ Failed to backup {file_path}: {e}{Style.RESET_ALL}")
    return None

def remove_file(file_path) -> Any:
    """Remove a file with backup"""
    try:
        if file_path.exists():
            # Create backup
            backup_path = backup_file(file_path)
            if backup_path:
                logger.info(f"{Fore.YELLOW}📁 Backed up: {file_path} -> {backup_path}{Style.RESET_ALL}")
            
            # Remove file
            file_path.unlink()
            logger.info(f"{Fore.GREEN}✅ Removed: {file_path}{Style.RESET_ALL}")
            return True
        else:
            logger.info(f"{Fore.YELLOW}⚠️ File not found: {file_path}{Style.RESET_ALL}")
            return False
    except Exception as e:
        logger.info(f"{Fore.RED}❌ Failed to remove {file_path}: {e}{Style.RESET_ALL}")
        return False

def remove_directory(dir_path) -> Any:
    """Remove a directory with backup"""
    try:
        if dir_path.exists():
            # Create backup
            backup_path = dir_path.with_suffix('.backup')
            shutil.copytree(dir_path, backup_path)
            logger.info(f"{Fore.YELLOW}📁 Backed up: {dir_path} -> {backup_path}{Style.RESET_ALL}")
            
            # Remove directory
            shutil.rmtree(dir_path)
            logger.info(f"{Fore.GREEN}✅ Removed: {dir_path}{Style.RESET_ALL}")
            return True
        else:
            logger.info(f"{Fore.YELLOW}⚠️ Directory not found: {dir_path}{Style.RESET_ALL}")
            return False
    except Exception as e:
        logger.info(f"{Fore.RED}❌ Failed to remove {dir_path}: {e}{Style.RESET_ALL}")
        return False

def cleanup_redundant_files() -> None:
    """Clean up all redundant files"""
    logger.info(f"{Fore.CYAN}🧹 Starting cleanup process...{Style.RESET_ALL}")
    logger.info()
    
    project_root = Path(__file__).parent
    redundant_files = get_redundant_files()
    redundant_dirs = get_redundant_directories()
    
    # Statistics
    total_files = len(redundant_files)
    total_dirs = len(redundant_dirs)
    removed_files = 0
    removed_dirs = 0
    
    logger.info(f"{Fore.YELLOW}📋 Files to remove: {total_files}{Style.RESET_ALL}")
    logger.info(f"{Fore.YELLOW}📁 Directories to remove: {total_dirs}{Style.RESET_ALL}")
    logger.info()
    
    # Remove files
    logger.info(f"{Fore.CYAN}🗑️ Removing redundant files...{Style.RESET_ALL}")
    logger.info("-" * 60)
    
    for file_name in redundant_files:
        file_path = project_root / file_name
        if remove_file(file_path):
            removed_files += 1
        logger.info()
    
    # Remove directories
    logger.info(f"{Fore.CYAN}🗑️ Removing redundant directories...{Style.RESET_ALL}")
    logger.info("-" * 60)
    
    for dir_name in redundant_dirs:
        dir_path = project_root / dir_name
        if remove_directory(dir_path):
            removed_dirs += 1
        logger.info()
    
    # Print summary
    logger.info(f"{Fore.CYAN}📊 CLEANUP SUMMARY{Style.RESET_ALL}")
    logger.info("=" * 60)
    logger.info(f"{Fore.GREEN}✅ Files removed: {removed_files}/{total_files}{Style.RESET_ALL}")
    logger.info(f"{Fore.GREEN}✅ Directories removed: {removed_dirs}/{total_dirs}{Style.RESET_ALL}")
    logger.info()
    
    if removed_files == total_files and removed_dirs == total_dirs:
        logger.info(f"{Fore.GREEN}🎉 All redundant files cleaned up successfully!{Style.RESET_ALL}")
    else:
        logger.info(f"{Fore.YELLOW}⚠️ Some files could not be removed. Check the output above.{Style.RESET_ALL}")
    
    logger.info()
    logger.info(f"{Fore.CYAN}💡 Next steps:{Style.RESET_ALL}")
    logger.info("1. Test the unified system: python main.py")
    logger.info("2. Run tests: python test_suite.py --all")
    logger.info("3. Run demos: python demo.py --complete")
    logger.info("4. Check that everything works correctly")

def main() -> None:
    """Main cleanup function"""
    print_banner()
    
    # Confirm cleanup
    logger.info(f"{Fore.YELLOW}⚠️ WARNING: This will remove redundant files from the BASED CODER CLI.{Style.RESET_ALL}")
    logger.info(f"{Fore.YELLOW}⚠️ Backups will be created before deletion.{Style.RESET_ALL}")
    logger.info()
    
    confirm = input(f"{Fore.CYAN}Do you want to proceed with cleanup? (y/N): {Style.RESET_ALL}").strip().lower()
    
    if confirm in ['y', 'yes']:
        cleanup_redundant_files()
    else:
        logger.info(f"{Fore.YELLOW}❌ Cleanup cancelled.{Style.RESET_ALL}")

if __name__ == "__main__":
    main() 