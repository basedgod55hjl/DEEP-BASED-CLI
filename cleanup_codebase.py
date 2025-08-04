#!/usr/bin/env python3
"""
Codebase Cleanup Script
Removes demo files, test copies, rewrites, and keeps only essential components
"""

import os
import shutil
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def cleanup_codebase():
    """Clean up the codebase by removing unnecessary files"""
    
    # Files to delete (demo, test, rewrite, backup files)
    files_to_delete = [
        # Demo files
        "demo.py",
        "demo_deepseek_coder.py", 
        "demo_full_system.py",
        "examples/rag_demo.py",
        "examples/unified_agent_demo.py",
        
        # Test files
        "test_tools.py",
        "test_suite.py", 
        "test_qwen_model.py",
        "test_final_system.py",
        "test_core_features.py",
        "simple_test.py",
        
        # Claude Coder Agent variations (keep only the latest)
        "claude_coder_agent.py",
        "claude_coder_agent_basic.py",
        "claude_coder_agent_fixed.py", 
        "claude_coder_agent_simple.py",
        "claude_coder_standalone.py",
        "claude_coder_fixed.py",
        
        # Setup variations (keep only main setup.py)
        "setup_api_keys.py",
        "setup_based_coder.py",
        "setup_complete_deanna_system.py",
        "setup_deanna_persona.py",
        "setup_simple_deanna_system.py",
        "setup_transformers_deanna_system.py",
        
        # Download variations (keep only main download_manager.py)
        "download_gguf_models.py",
        "download_qwen_model.py",
        "simple_download.py",
        
        # Enhanced variations (keep only main files)
        "enhanced_based_god_cli.py",
        "enhanced_cli.py",
        "enhanced_logging.py",
        
        # Fix and cleanup scripts (temporary)
        "fix_all_docstring_errors.py",
        "fix_docstring_errors.py",
        "file_encoding_fixer.py",
        "cleanup_redundant_files.py",
        "critical_fixes_phase1.py",
        "fix_deepseek_issues.py",
        "run_all_improvements.py",
        
        # Utility scripts (keep only essential)
        "run_cli.py",
        "init_local_db.py",
        "update_api_key.py",
        "database_cleaner.py",
        "config_manager.py",
        
        # Old system files
        "deanna_chat_system.py",
        "system_status.py",
        "simple_embedding_setup.py",
        
        # AI Swarm system (temporary)
        "ai_swarm_system.py",
        "deepseek_reasoner_runner.py",
        
        # Report and summary files
        "CRITICAL_FIXES_PHASE1_SUMMARY.md",
        "critical_fixes_phase1_report.md",
        "file_encoding_fix_report.md",
        "CODEBASE_REWRITE_SUMMARY.md",
        "REWRITE_COMPLETION_SUMMARY.md",
        "CODEBASE_ANALYSIS_SUMMARY.md",
        "CLAUDE_CODER_AGENT_SUMMARY.md",
        "FINAL_IMPROVEMENTS_SUMMARY.md",
        "AI_SWARM_MISSION_SUMMARY.md",
        "IMPROVEMENT_IMPLEMENTATION_PLAN.md",
        "claude_rewrite_plan.md",
        "claude_rewrite_implementation_guide.md",
        "CLAUDE_CODER_AGENT_README.md",
        "FINAL_SYSTEM_SUMMARY.md",
        "SETUP_SUMMARY.md",
        "README_DEANNA_SYSTEM.md",
        "ENHANCED_FEATURES.md",
        "DEEPSEEK_CODER_FEATURES.md",
        "SYSTEM_STATUS.md",
        "commit_message.txt",
        "requirements_enhanced.txt",
        
        # JSON reports
        "system_status_report.json",
        "config_report.json",
        "based_god_memory.json",
        
        # Docker files (Claude Coder Agent)
        "Dockerfile.claude_coder",
        "docker-compose.claude-coder.yml",
        "nginx.conf",
        "run_claude_coder.bat",
        "run_claude_coder.sh",
        
        # Config backups
        "config_backups/",
        
        # Examples backup
        "examples.backup/",
        
        # Rewrite examples
        "rewrite_examples/",
        
        # Reports directory
        "reports/",
        
        # Scans directory  
        "scans/",
        
        # Backups directory
        "backups/",
    ]
    
    # Directories to delete
    dirs_to_delete = [
        "examples",
        "rewrite_examples", 
        "backups",
        "reports",
        "scans",
        "config_backups",
        "examples.backup",
    ]
    
    deleted_files = []
    deleted_dirs = []
    errors = []
    
    logging.info("🧹 Starting codebase cleanup...")
    
    # Delete files
    for file_path in files_to_delete:
        if os.path.exists(file_path):
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    deleted_files.append(file_path)
                    logging.info(f"✅ Deleted file: {file_path}")
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                    deleted_dirs.append(file_path)
                    logging.info(f"✅ Deleted directory: {file_path}")
            except Exception as e:
                errors.append(f"Error deleting {file_path}: {e}")
                logging.error(f"❌ Error deleting {file_path}: {e}")
    
    # Delete directories
    for dir_path in dirs_to_delete:
        if os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path)
                deleted_dirs.append(dir_path)
                logging.info(f"✅ Deleted directory: {dir_path}")
            except Exception as e:
                errors.append(f"Error deleting {dir_path}: {e}")
                logging.error(f"❌ Error deleting {dir_path}: {e}")
    
    # Clean up __pycache__ directories
    for root, dirs, files in os.walk("."):
        if "__pycache__" in dirs:
            try:
                cache_dir = os.path.join(root, "__pycache__")
                shutil.rmtree(cache_dir)
                deleted_dirs.append(cache_dir)
                logging.info(f"✅ Deleted cache: {cache_dir}")
            except Exception as e:
                errors.append(f"Error deleting cache {cache_dir}: {e}")
    
    # Summary
    print(f"\n🎉 Cleanup completed!")
    print(f"📁 Deleted {len(deleted_files)} files")
    print(f"📂 Deleted {len(deleted_dirs)} directories")
    
    if errors:
        print(f"\n⚠️ {len(errors)} errors occurred:")
        for error in errors:
            print(f"  - {error}")
    
    # Show remaining essential files
    print(f"\n📋 Essential files remaining:")
    essential_files = [
        "main.py",
        "config.py", 
        "requirements.txt",
        "README.md",
        ".env",
        ".gitignore",
        "tools/",
        "config/",
        "data/",
        "src/",
        "logs/",
    ]
    
    for file_path in essential_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} (missing)")

if __name__ == "__main__":
    cleanup_codebase() 