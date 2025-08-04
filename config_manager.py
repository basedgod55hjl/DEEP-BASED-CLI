#!/usr/bin/env python3
"""
Configuration Manager for BASED CODER CLI
Manages all configuration files, models, and settings
"""

import json
import yaml
import os
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree
from enhanced_logging import get_logger

console = Console()
logger = get_logger()

class ConfigManager:
    """Comprehensive configuration manager"""
    
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self.config_dir = self.base_dir / "config"
        self.data_dir = self.base_dir / "data"
        self.models_dir = self.data_dir / "models"
        
        # Ensure directories exist
        self.config_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)
        self.models_dir.mkdir(exist_ok=True)
        
        # Configuration files
        self.config_files = {
            'main': self.config_dir / "deepcli_config.py",
            'api_keys': self.config_dir / "api_keys.py",
            'enhanced': self.config_dir / "enhanced_config.json",
            'models': self.models_dir / "qwen_embedding_system_info.json",
            'qwen_config': self.models_dir / "qwen3_embedding" / "config.json",
            'qwen_sentence_config': self.models_dir / "qwen3_embedding" / "config_sentence_transformers.json",
            'env': self.base_dir / ".env"
        }
    
    def read_all_configs(self) -> Dict[str, Any]:
        """Read all configuration files"""
        configs = {}
        
        console.print(Panel.fit("Reading All Configuration Files", title="Config Manager"))
        
        for name, file_path in self.config_files.items():
            try:
                if file_path.exists():
                    configs[name] = self.read_config_file(file_path)
                    console.print(f"✅ {name}: {file_path}")
                else:
                    configs[name] = None
                    console.print(f"❌ {name}: {file_path} (not found)")
            except Exception as e:
                logger.log_error(e, f"reading_config_{name}")
                configs[name] = None
                console.print(f"⚠️ {name}: {file_path} (error: {e})")
        
        return configs
    
    def read_config_file(self, file_path: Path) -> Any:
        """Read a single configuration file"""
        if not file_path.exists():
            return None
        
        try:
            if file_path.suffix == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            elif file_path.suffix == '.yaml' or file_path.suffix == '.yml':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            elif file_path.suffix == '.py':
                # For Python files, we'll read as text and extract key info
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    return self.extract_python_config(content)
            elif file_path.name == '.env':
                return self.read_env_file(file_path)
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            logger.log_error(e, f"reading_file_{file_path.name}")
            return None
    
    def extract_python_config(self, content: str) -> Dict[str, Any]:
        """Extract configuration from Python file content"""
        config = {}
        
        # Look for common patterns
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                try:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')
                    config[key] = value
                except:
                    continue
        
        return config
    
    def read_env_file(self, file_path: Path) -> Dict[str, str]:
        """Read .env file"""
        env_vars = {}
        
        if not file_path.exists():
            return env_vars
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
        except Exception as e:
            logger.log_error(e, "reading_env_file")
        
        return env_vars
    
    def display_config_summary(self, configs: Dict[str, Any]):
        """Display configuration summary"""
        console.print(Panel.fit("Configuration Summary", title="Config Summary"))
        
        # Create summary table
        table = Table(title="Configuration Files Status")
        table.add_column("Config", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Type", style="green")
        table.add_column("Size", style="blue")
        
        for name, config in configs.items():
            file_path = self.config_files[name]
            
            if config is not None:
                status = "✅ Loaded"
                config_type = type(config).__name__
                
                if isinstance(config, dict):
                    size = f"{len(config)} keys"
                elif isinstance(config, str):
                    size = f"{len(config)} chars"
                else:
                    size = "N/A"
            else:
                status = "❌ Not Found"
                config_type = "N/A"
                size = "N/A"
            
            table.add_row(name, status, config_type, size)
        
        console.print(table)
    
    def display_model_configs(self, configs: Dict[str, Any]):
        """Display model-specific configurations"""
        console.print(Panel.fit("Model Configurations", title="Model Configs"))
        
        # Qwen model config
        if configs.get('qwen_config'):
            qwen_config = configs['qwen_config']
            
            table = Table(title="Qwen Model Configuration")
            table.add_column("Parameter", style="cyan")
            table.add_column("Value", style="green")
            
            key_params = [
                'model_type', 'hidden_size', 'num_attention_heads', 
                'num_hidden_layers', 'vocab_size', 'max_position_embeddings'
            ]
            
            for param in key_params:
                if param in qwen_config:
                    table.add_row(param, str(qwen_config[param]))
            
            console.print(table)
        
        # Model info
        if configs.get('models'):
            model_info = configs['models']
            
            table = Table(title="Model System Info")
            table.add_column("Parameter", style="cyan")
            table.add_column("Value", style="green")
            
            for key, value in model_info.items():
                table.add_row(key, str(value))
            
            console.print(table)
    
    def validate_configs(self, configs: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate configuration files"""
        console.print(Panel.fit("Validating Configurations", title="Config Validation"))
        
        validation_results = {}
        
        # Validate API keys
        if configs.get('env'):
            env_vars = configs['env']
            api_issues = []
            
            if 'DEEPSEEK_API_KEY' not in env_vars:
                api_issues.append("Missing DEEPSEEK_API_KEY")
            elif not env_vars['DEEPSEEK_API_KEY'].startswith('sk-'):
                api_issues.append("Invalid DEEPSEEK_API_KEY format")
            
            if 'HUGGINGFACE_API_KEY' not in env_vars:
                api_issues.append("Missing HUGGINGFACE_API_KEY")
            elif not env_vars['HUGGINGFACE_API_KEY'].startswith('hf_'):
                api_issues.append("Invalid HUGGINGFACE_API_KEY format")
            
            validation_results['api_keys'] = api_issues
        
        # Validate model configs
        if configs.get('qwen_config'):
            model_issues = []
            qwen_config = configs['qwen_config']
            
            required_params = ['model_type', 'hidden_size', 'vocab_size']
            for param in required_params:
                if param not in qwen_config:
                    model_issues.append(f"Missing required parameter: {param}")
            
            validation_results['model_config'] = model_issues
        
        # Display validation results
        for config_type, issues in validation_results.items():
            if issues:
                console.print(f"❌ {config_type}: {len(issues)} issues found")
                for issue in issues:
                    console.print(f"  - {issue}")
            else:
                console.print(f"✅ {config_type}: Valid")
        
        return validation_results
    
    def backup_configs(self) -> Path:
        """Create backup of all configuration files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.base_dir / "config_backups" / f"backup_{timestamp}"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        console.print(Panel.fit(f"Creating Config Backup: {backup_dir}", title="Config Backup"))
        
        backed_up_files = 0
        
        for name, file_path in self.config_files.items():
            if file_path.exists():
                try:
                    backup_path = backup_dir / f"{name}_{file_path.name}"
                    shutil.copy2(file_path, backup_path)
                    backed_up_files += 1
                    console.print(f"✅ Backed up: {file_path.name}")
                except Exception as e:
                    logger.log_error(e, f"backing_up_{name}")
                    console.print(f"❌ Failed to backup: {file_path.name}")
        
        console.print(f"📦 Backup completed: {backed_up_files} files backed up")
        return backup_dir
    
    def clean_configs(self):
        """Clean and optimize configuration files"""
        console.print(Panel.fit("Cleaning Configuration Files", title="Config Cleanup"))
        
        # Clean backup files older than 7 days
        backup_root = self.base_dir / "config_backups"
        if backup_root.exists():
            cutoff_date = datetime.now() - timedelta(days=7)
            deleted_count = 0
            
            for backup_dir in backup_root.iterdir():
                if backup_dir.is_dir():
                    try:
                        dir_time = datetime.fromtimestamp(backup_dir.stat().st_mtime)
                        if dir_time < cutoff_date:
                            shutil.rmtree(backup_dir)
                            deleted_count += 1
                    except Exception as e:
                        logger.log_error(e, f"cleaning_backup_{backup_dir.name}")
            
            console.print(f"🗑️ Deleted {deleted_count} old backup directories")
    
    def create_config_report(self) -> Dict[str, Any]:
        """Create comprehensive configuration report"""
        console.print(Panel.fit("Generating Configuration Report", title="Config Report"))
        
        configs = self.read_all_configs()
        validation_results = self.validate_configs(configs)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'configs_loaded': len([c for c in configs.values() if c is not None]),
            'configs_total': len(configs),
            'validation_issues': sum(len(issues) for issues in validation_results.values()),
            'config_details': {},
            'validation_results': validation_results
        }
        
        # Add details for each config
        for name, config in configs.items():
            if config is not None:
                report['config_details'][name] = {
                    'type': type(config).__name__,
                    'size': len(str(config)) if config else 0,
                    'keys': len(config) if isinstance(config, dict) else 0
                }
        
        # Save report
        report_file = self.base_dir / "config_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        console.print(f"📊 Configuration report saved: {report_file}")
        return report
    
    def run_full_analysis(self):
        """Run complete configuration analysis"""
        console.print(Panel.fit(
            "[bold blue]BASED CODER CLI - Configuration Analysis[/bold blue]\n"
            "Analyzing all configuration files...",
            title="Config Analysis"
        ))
        
        # Read all configs
        configs = self.read_all_configs()
        
        # Display summary
        self.display_config_summary(configs)
        
        # Display model configs
        self.display_model_configs(configs)
        
        # Validate configs
        validation_results = self.validate_configs(configs)
        
        # Create backup
        backup_dir = self.backup_configs()
        
        # Clean old backups
        self.clean_configs()
        
        # Generate report
        report = self.create_config_report()
        
        console.print(Panel.fit(
            "[bold green]Configuration analysis completed![/bold green]\n"
            f"📁 Backup created: {backup_dir}\n"
            f"📊 Report generated: config_report.json\n"
            f"✅ {report['configs_loaded']}/{report['configs_total']} configs loaded\n"
            f"⚠️ {report['validation_issues']} validation issues found",
            title="Analysis Complete"
        ))

def main():
    """Main function"""
    config_manager = ConfigManager()
    config_manager.run_full_analysis()

if __name__ == "__main__":
    main() 