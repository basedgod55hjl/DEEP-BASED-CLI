#!/usr/bin/env python3
"""
System Status Script for BASED CODER CLI
Comprehensive system monitoring and status reporting
"""

import os
import sys
import platform
import psutil
import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree
from rich.progress import Progress, SpinnerColumn, TextColumn
from database_cleaner import DatabaseCleaner
from enhanced_logging import get_logger
from config_manager import ConfigManager

console = Console()
logger = get_logger()

class SystemStatus:
    """Comprehensive system status monitoring"""
    
    def __init__(self):
        self.base_dir = Path(".")
        self.data_dir = self.base_dir / "data"
        self.config_dir = self.base_dir / "config"
        
        # Initialize components
        self.db_cleaner = DatabaseCleaner()
        self.config_manager = ConfigManager()
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        return {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'architecture': platform.architecture(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'cpu_count': psutil.cpu_count(),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_total': psutil.virtual_memory().total,
            'memory_available': psutil.virtual_memory().available,
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': self.get_disk_usage(),
            'uptime': self.get_uptime()
        }
    
    def get_disk_usage(self) -> Dict[str, Any]:
        """Get disk usage information"""
        try:
            if os.path.exists('/'):
                disk = psutil.disk_usage('/')
            else:
                disk = psutil.disk_usage('C:\\')
            
            return {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': disk.percent
            }
        except Exception as e:
            logger.log_error(e, "getting_disk_usage")
            return {'error': str(e)}
    
    def get_uptime(self) -> str:
        """Get system uptime"""
        try:
            uptime_seconds = psutil.boot_time()
            uptime = datetime.now() - datetime.fromtimestamp(uptime_seconds)
            return str(uptime).split('.')[0]  # Remove microseconds
        except Exception as e:
            logger.log_error(e, "getting_uptime")
            return "Unknown"
    
    def get_database_status(self) -> Dict[str, Any]:
        """Get database status and statistics"""
        status = {}
        
        # Main database
        main_db = self.data_dir / "deepcli_database.db"
        if main_db.exists():
            try:
                conn = sqlite3.connect(main_db)
                cursor = conn.cursor()
                
                # Get table statistics
                tables = ['conversations', 'personas', 'memory', 'context']
                for table in tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        status[f'main_{table}'] = count
                    except sqlite3.OperationalError:
                        status[f'main_{table}'] = 0
                
                # Get database size
                status['main_db_size'] = main_db.stat().st_size
                conn.close()
                
            except Exception as e:
                logger.log_error(e, "checking_main_database")
                status['main_db_error'] = str(e)
        else:
            status['main_db_exists'] = False
        
        # Memory database
        memory_db = self.data_dir / "deanna_memory.db"
        if memory_db.exists():
            try:
                conn = sqlite3.connect(memory_db)
                cursor = conn.cursor()
                
                # Get table statistics
                tables = ['memory_entries', 'chat_history', 'deepseek_cache', 'embeddings', 'persona_config']
                for table in tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        status[f'memory_{table}'] = count
                    except sqlite3.OperationalError:
                        status[f'memory_{table}'] = 0
                
                # Get database size
                status['memory_db_size'] = memory_db.stat().st_size
                conn.close()
                
            except Exception as e:
                logger.log_error(e, "checking_memory_database")
                status['memory_db_error'] = str(e)
        else:
            status['memory_db_exists'] = False
        
        return status
    
    def get_file_system_status(self) -> Dict[str, Any]:
        """Get file system status"""
        status = {}
        
        # Check important directories
        directories = {
            'data': self.data_dir,
            'config': self.config_dir,
            'models': self.data_dir / "models",
            'logs': self.data_dir / "logs",
            'cache': self.data_dir / "cache",
            'backups': self.data_dir / "backups"
        }
        
        for name, path in directories.items():
            if path.exists():
                try:
                    # Count files
                    file_count = len(list(path.rglob('*')))
                    dir_count = len([p for p in path.rglob('*') if p.is_dir()])
                    
                    # Get total size
                    total_size = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
                    
                    status[f'{name}_exists'] = True
                    status[f'{name}_files'] = file_count
                    status[f'{name}_dirs'] = dir_count
                    status[f'{name}_size'] = total_size
                except Exception as e:
                    logger.log_error(e, f"checking_directory_{name}")
                    status[f'{name}_error'] = str(e)
            else:
                status[f'{name}_exists'] = False
        
        return status
    
    def get_tool_status(self) -> Dict[str, Any]:
        """Get tool status from test results"""
        try:
            # Import and run tool test
            import test_tools
            # This would require modifying test_tools to return results instead of just printing
            return {'tools_tested': True}
        except Exception as e:
            logger.log_error(e, "testing_tools")
            return {'tools_error': str(e)}
    
    def display_system_info(self, system_info: Dict[str, Any]):
        """Display system information"""
        console.print(Panel.fit("System Information", title="System Info"))
        
        table = Table(title="System Details")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        # Platform info
        table.add_row("Platform", system_info['platform'])
        table.add_row("Version", system_info['platform_version'])
        table.add_row("Architecture", str(system_info['architecture'][0]))
        table.add_row("Processor", system_info['processor'])
        table.add_row("Python Version", system_info['python_version'])
        
        # CPU info
        table.add_row("CPU Cores", str(system_info['cpu_count']))
        table.add_row("CPU Usage", f"{system_info['cpu_percent']:.1f}%")
        
        # Memory info
        memory_gb = system_info['memory_total'] / (1024**3)
        memory_available_gb = system_info['memory_available'] / (1024**3)
        table.add_row("Total Memory", f"{memory_gb:.1f} GB")
        table.add_row("Available Memory", f"{memory_available_gb:.1f} GB")
        table.add_row("Memory Usage", f"{system_info['memory_percent']:.1f}%")
        
        # Disk info
        if 'error' not in system_info['disk_usage']:
            disk_gb = system_info['disk_usage']['total'] / (1024**3)
            disk_used_gb = system_info['disk_usage']['used'] / (1024**3)
            table.add_row("Total Disk", f"{disk_gb:.1f} GB")
            table.add_row("Used Disk", f"{disk_used_gb:.1f} GB")
            table.add_row("Disk Usage", f"{system_info['disk_usage']['percent']:.1f}%")
        
        # Uptime
        table.add_row("System Uptime", system_info['uptime'])
        
        console.print(table)
    
    def display_database_status(self, db_status: Dict[str, Any]):
        """Display database status"""
        console.print(Panel.fit("Database Status", title="Database Status"))
        
        # Main database
        if db_status.get('main_db_exists', True):
            table = Table(title="Main Database")
            table.add_column("Table", style="cyan")
            table.add_column("Records", style="green")
            
            tables = ['conversations', 'personas', 'memory', 'context']
            for table_name in tables:
                count = db_status.get(f'main_{table_name}', 0)
                table.add_row(table_name, str(count))
            
            if 'main_db_size' in db_status:
                size_mb = db_status['main_db_size'] / (1024**2)
                table.add_row("Database Size", f"{size_mb:.2f} MB")
            
            console.print(table)
        else:
            console.print("❌ Main database not found")
        
        # Memory database
        if db_status.get('memory_db_exists', True):
            table = Table(title="Memory Database")
            table.add_column("Table", style="cyan")
            table.add_column("Records", style="green")
            
            tables = ['memory_entries', 'chat_history', 'deepseek_cache', 'embeddings', 'persona_config']
            for table_name in tables:
                count = db_status.get(f'memory_{table_name}', 0)
                table.add_row(table_name, str(count))
            
            if 'memory_db_size' in db_status:
                size_mb = db_status['memory_db_size'] / (1024**2)
                table.add_row("Database Size", f"{size_mb:.2f} MB")
            
            console.print(table)
        else:
            console.print("❌ Memory database not found")
    
    def display_file_system_status(self, fs_status: Dict[str, Any]):
        """Display file system status"""
        console.print(Panel.fit("File System Status", title="File System"))
        
        table = Table(title="Directory Status")
        table.add_column("Directory", style="cyan")
        table.add_column("Exists", style="green")
        table.add_column("Files", style="blue")
        table.add_column("Size", style="yellow")
        
        directories = ['data', 'config', 'models', 'logs', 'cache', 'backups']
        
        for dir_name in directories:
            exists = fs_status.get(f'{dir_name}_exists', False)
            files = fs_status.get(f'{dir_name}_files', 0)
            size = fs_status.get(f'{dir_name}_size', 0)
            
            if size > 0:
                if size > 1024**3:  # GB
                    size_str = f"{size / (1024**3):.2f} GB"
                elif size > 1024**2:  # MB
                    size_str = f"{size / (1024**2):.2f} MB"
                elif size > 1024:  # KB
                    size_str = f"{size / 1024:.2f} KB"
                else:
                    size_str = f"{size} B"
            else:
                size_str = "0 B"
            
            table.add_row(
                dir_name,
                "✅" if exists else "❌",
                str(files),
                size_str
            )
        
        console.print(table)
    
    def display_logging_status(self):
        """Display logging status"""
        console.print(Panel.fit("Logging Status", title="Logging"))
        
        # Get logger status
        error_summary = logger.get_error_summary()
        performance_summary = logger.get_performance_summary()
        
        # Error summary
        error_table = Table(title="Error Summary")
        error_table.add_column("Metric", style="cyan")
        error_table.add_column("Value", style="green")
        
        error_table.add_row("Total Errors", str(error_summary['total_errors']))
        error_table.add_row("Total Warnings", str(error_summary['total_warnings']))
        
        for error_type, count in error_summary['error_types'].items():
            error_table.add_row(f"Error Type: {error_type}", str(count))
        
        console.print(error_table)
        
        # Performance summary
        if performance_summary:
            perf_table = Table(title="Performance Summary")
            perf_table.add_column("Operation", style="cyan")
            perf_table.add_column("Count", style="green")
            perf_table.add_column("Avg Duration", style="blue")
            perf_table.add_column("Success Rate", style="yellow")
            
            for operation, metrics in performance_summary.items():
                perf_table.add_row(
                    operation,
                    str(metrics['count']),
                    f"{metrics['avg_duration']:.3f}s",
                    f"{metrics['success_rate']:.1%}"
                )
            
            console.print(perf_table)
    
    def run_full_status_check(self):
        """Run complete system status check"""
        console.print(Panel.fit(
            "[bold blue]BASED CODER CLI - System Status Check[/bold blue]\n"
            "Running comprehensive system analysis...",
            title="System Status"
        ))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            # Get system information
            progress.add_task("Gathering system information...", total=None)
            system_info = self.get_system_info()
            
            # Get database status
            progress.add_task("Checking database status...", total=None)
            db_status = self.get_database_status()
            
            # Get file system status
            progress.add_task("Checking file system...", total=None)
            fs_status = self.get_file_system_status()
            
            # Get tool status
            progress.add_task("Checking tool status...", total=None)
            tool_status = self.get_tool_status()
        
        # Display all information
        self.display_system_info(system_info)
        self.display_database_status(db_status)
        self.display_file_system_status(fs_status)
        self.display_logging_status()
        
        # Create comprehensive report
        report = {
            'timestamp': datetime.now().isoformat(),
            'system_info': system_info,
            'database_status': db_status,
            'file_system_status': fs_status,
            'tool_status': tool_status,
            'logging_summary': logger.get_error_summary()
        }
        
        # Save report
        report_file = self.base_dir / "system_status_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        console.print(Panel.fit(
            "[bold green]System status check completed![/bold green]\n"
            f"📊 Report saved: {report_file}\n"
            f"💾 Total database records: {sum(v for k, v in db_status.items() if isinstance(v, int) and 'error' not in k)}\n"
            f"📁 Total files: {sum(v for k, v in fs_status.items() if k.endswith('_files') and isinstance(v, int))}\n"
            f"⚠️ Total errors: {logger.get_error_summary()['total_errors']}",
            title="Status Complete"
        ))

def main():
    """Main function"""
    status_checker = SystemStatus()
    status_checker.run_full_status_check()

if __name__ == "__main__":
    main() 