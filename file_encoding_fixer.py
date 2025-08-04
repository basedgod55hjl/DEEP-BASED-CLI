#!/usr/bin/env python3
"""
File Encoding Fixer - Fixes file reading issues in DEEP-CLI codebase
"""

import os
import sys
import chardet
import logging
from pathlib import Path
from typing import List, Dict, Tuple
import shutil
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileEncodingFixer:
    """Tool to fix file encoding issues causing reading errors"""
    
    def __init__(self, codebase_path: str = "."):
        self.codebase_path = Path(codebase_path)
        self.fixed_files = []
        self.failed_files = []
        self.backup_dir = Path("backups/file_encoding_fixes")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
    def detect_encoding(self, file_path: Path) -> str:
        """Detect file encoding using chardet"""
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                if not raw_data:
                    return 'utf-8'
                
                result = chardet.detect(raw_data)
                encoding = result['encoding'] if result['encoding'] else 'utf-8'
                confidence = result['confidence'] if result['confidence'] else 0
                
                logger.info(f"Detected encoding for {file_path}: {encoding} (confidence: {confidence:.2f})")
                return encoding
        except Exception as e:
            logger.warning(f"Error detecting encoding for {file_path}: {e}")
            return 'utf-8'
    
    def read_file_safely(self, file_path: Path) -> Tuple[str, str, bool]:
        """Safely read file with multiple encoding attempts"""
        encodings_to_try = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
        
        # First try detected encoding
        detected_encoding = self.detect_encoding(file_path)
        if detected_encoding not in encodings_to_try:
            encodings_to_try.insert(0, detected_encoding)
        
        for encoding in encodings_to_try:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                    logger.info(f"Successfully read {file_path} with {encoding} encoding")
                    return content, encoding, True
            except UnicodeDecodeError as e:
                logger.debug(f"Failed to read {file_path} with {encoding}: {e}")
                continue
            except Exception as e:
                logger.warning(f"Error reading {file_path} with {encoding}: {e}")
                continue
        
        logger.error(f"Failed to read {file_path} with any encoding")
        return "", "unknown", False
    
    def create_backup(self, file_path: Path) -> Path:
        """Create backup of original file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        backup_path = self.backup_dir / backup_name
        
        try:
            shutil.copy2(file_path, backup_path)
            logger.info(f"Created backup: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Failed to create backup for {file_path}: {e}")
            return None
    
    def fix_file_encoding(self, file_path: Path) -> bool:
        """Fix encoding issues in a single file"""
        try:
            logger.info(f"Processing file: {file_path}")
            
            # Create backup
            backup_path = self.create_backup(file_path)
            if not backup_path:
                self.failed_files.append((str(file_path), "Backup creation failed"))
                return False
            
            # Read file with detected encoding
            content, original_encoding, success = self.read_file_safely(file_path)
            
            if not success:
                self.failed_files.append((str(file_path), "File reading failed"))
                return False
            
            # Write back with UTF-8 encoding
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                logger.info(f"Successfully fixed encoding for {file_path} (was: {original_encoding})")
                self.fixed_files.append((str(file_path), original_encoding))
                return True
                
            except Exception as e:
                logger.error(f"Failed to write {file_path}: {e}")
                # Restore from backup
                try:
                    shutil.copy2(backup_path, file_path)
                    logger.info(f"Restored {file_path} from backup")
                except Exception as restore_error:
                    logger.error(f"Failed to restore {file_path}: {restore_error}")
                
                self.failed_files.append((str(file_path), f"Write failed: {e}"))
                return False
                
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            self.failed_files.append((str(file_path), str(e)))
            return False
    
    def find_problematic_files(self) -> List[Path]:
        """Find files that might have encoding issues"""
        problematic_files = []
        
        # Files that were reported with reading errors
        known_problematic = [
            "based_coder_cli.py",
            "claude_coder_agent.py",
            "claude_coder_agent_basic.py",
            "claude_coder_agent_fixed.py",
            "claude_coder_agent_simple.py",
            "demo.py",
            "download_manager.py",
            "download_qwen_model.py",
            "fix_deepseek_issues.py",
            "main.py",
            "setup.py",
            "setup_api_keys.py",
            "setup_complete_deanna_system.py",
            "setup_simple_deanna_system.py",
            "setup_transformers_deanna_system.py",
            "simple_test.py",
            "system_status.py",
            "test_qwen_model.py",
            "test_suite.py",
            "data/embedding_system.py",
            "data/local_embedding_system.py",
            "data/transformers_embedding_system.py",
            "examples/rag_demo.py",
            "tools/code_generator_tool.py",
            "tools/file_processor_tool.py",
            "tools/memory_tool.py",
            "tools/reasoning_engine.py",
            "tools/tool_manager.py",
            "tools/web_scraper_tool.py",
            "src/tools/advanced/code_architecture_tool.py"
        ]
        
        for file_name in known_problematic:
            file_path = self.codebase_path / file_name
            if file_path.exists():
                problematic_files.append(file_path)
        
        # Also scan for any Python files that might have issues
        for py_file in self.codebase_path.rglob("*.py"):
            if py_file not in problematic_files:
                # Test if file can be read
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        f.read()
                except UnicodeDecodeError:
                    problematic_files.append(py_file)
                except Exception:
                    # Other errors might indicate encoding issues
                    problematic_files.append(py_file)
        
        return problematic_files
    
    def fix_all_files(self) -> Dict[str, any]:
        """Fix encoding issues in all problematic files"""
        logger.info("Starting file encoding fix process...")
        
        problematic_files = self.find_problematic_files()
        logger.info(f"Found {len(problematic_files)} potentially problematic files")
        
        for file_path in problematic_files:
            self.fix_file_encoding(file_path)
        
        return {
            "total_files": len(problematic_files),
            "fixed_files": self.fixed_files,
            "failed_files": self.failed_files,
            "success_rate": len(self.fixed_files) / len(problematic_files) if problematic_files else 0
        }
    
    def generate_report(self, results: Dict[str, any]) -> str:
        """Generate a report of the fixing process"""
        report = f"""
# File Encoding Fix Report

## Summary
- **Total Files Processed**: {results['total_files']}
- **Successfully Fixed**: {len(results['fixed_files'])}
- **Failed**: {len(results['failed_files'])}
- **Success Rate**: {results['success_rate']:.1%}

## Fixed Files
"""
        
        for file_path, original_encoding in results['fixed_files']:
            report += f"- `{file_path}` (was: {original_encoding})\n"
        
        if results['failed_files']:
            report += "\n## Failed Files\n"
            for file_path, error in results['failed_files']:
                report += f"- `{file_path}`: {error}\n"
        
        report += f"\n## Backups Created\n"
        report += f"All original files backed up to: `{self.backup_dir}`\n"
        
        return report

def main():
    """Main function"""
    print("🔧 File Encoding Fixer")
    print("=" * 50)
    
    fixer = FileEncodingFixer()
    results = fixer.fix_all_files()
    
    print(f"\n📊 Results:")
    print(f"Total files processed: {results['total_files']}")
    print(f"Successfully fixed: {len(results['fixed_files'])}")
    print(f"Failed: {len(results['failed_files'])}")
    print(f"Success rate: {results['success_rate']:.1%}")
    
    if results['fixed_files']:
        print(f"\n✅ Fixed Files:")
        for file_path, encoding in results['fixed_files']:
            print(f"  - {file_path} (was: {encoding})")
    
    if results['failed_files']:
        print(f"\n❌ Failed Files:")
        for file_path, error in results['failed_files']:
            print(f"  - {file_path}: {error}")
    
    # Generate and save report
    report = fixer.generate_report(results)
    report_path = Path("file_encoding_fix_report.md")
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"\n📄 Report saved to: {report_path}")
    print(f"💾 Backups saved to: {fixer.backup_dir}")
    
    return results

if __name__ == "__main__":
    main() 