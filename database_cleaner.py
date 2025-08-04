import logging
logger = logging.getLogger(__name__)
#!/usr/bin/env python3
"""
Database Cleaner and Maintenance Script for BASED CODER CLI
Cleans databases, adds logs, and improves error handling
"""

import sqlite3
import json
import logging
import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

class DatabaseCleaner:
    """Database cleaning and maintenance utility"""
    
    def __init__(self, data_dir: str = "data"):
    """__init__ function."""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Database paths
        self.main_db_path = self.data_dir / "deepcli_database.db"
        self.memory_db_path = self.data_dir / "deanna_memory.db"
        
        # Logging setup
        self.setup_logging()
        
        # Backup directory
        self.backup_dir = self.data_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
    
    def setup_logging(self) -> Any:
        """Setup comprehensive logging"""
        log_dir = self.data_dir / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # Create timestamped log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"database_cleanup_{timestamp}.log"
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("Database cleaner initialized")
    
    def backup_database(self, db_path: Path) -> Path:
        """Create backup of database"""
        if not db_path.exists():
            self.logger.warning(f"Database {db_path} does not exist, skipping backup")
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{db_path.stem}_backup_{timestamp}.db"
        backup_path = self.backup_dir / backup_name
        
        try:
            shutil.copy2(db_path, backup_path)
            self.logger.info(f"Backup created: {backup_path}")
            return backup_path
        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
            return None
    
    def clean_main_database(self) -> Any:
        """Clean the main database"""
        console.logger.info(Panel.fit("Cleaning Main Database", title="Database Cleanup"))
        
        if not self.main_db_path.exists():
            self.logger.warning("Main database does not exist")
            return
        
        # Create backup
        backup_path = self.backup_database(self.main_db_path)
        
        try:
            conn = sqlite3.connect(self.main_db_path)
            cursor = conn.cursor()
            
            # Get database statistics before cleanup
            stats_before = self.get_database_stats(cursor, "main")
            
            # Clean old conversations (older than 30 days)
            cursor.execute("""
                DELETE FROM conversations 
                WHERE timestamp < datetime('now', '-30 days')
            """)
            conversations_deleted = cursor.rowcount
            
            # Clean old context (older than 7 days)
            cursor.execute("""
                DELETE FROM context 
                WHERE timestamp < datetime('now', '-7 days')
            """)
            context_deleted = cursor.rowcount
            
            # Clean duplicate conversations
            cursor.execute("""
                DELETE FROM conversations 
                WHERE id NOT IN (
                    SELECT MIN(id) 
                    FROM conversations 
                    GROUP BY session_id, user_input, assistant_response
                )
            """)
            duplicates_deleted = cursor.rowcount
            
            # Clean empty or invalid entries
            cursor.execute("""
                DELETE FROM conversations 
                WHERE user_input IS NULL OR user_input = '' 
                OR assistant_response IS NULL OR assistant_response = ''
            """)
            empty_deleted = cursor.rowcount
            
            # Get statistics after cleanup
            stats_after = self.get_database_stats(cursor, "main")
            
            conn.commit()
            conn.close()
            
            # Log cleanup results
            self.logger.info(f"Main database cleanup completed:")
            self.logger.info(f"  - Conversations deleted: {conversations_deleted}")
            self.logger.info(f"  - Context deleted: {context_deleted}")
            self.logger.info(f"  - Duplicates deleted: {duplicates_deleted}")
            self.logger.info(f"  - Empty entries deleted: {empty_deleted}")
            
            # Display results
            self.display_cleanup_results("Main Database", stats_before, stats_after)
            
        except Exception as e:
            self.logger.error(f"Error cleaning main database: {e}")
            console.logger.info(f"[red]Error cleaning main database: {e}[/red]")
    
    def clean_memory_database(self) -> Any:
        """Clean the memory database"""
        console.logger.info(Panel.fit("Cleaning Memory Database", title="Database Cleanup"))
        
        if not self.memory_db_path.exists():
            self.logger.warning("Memory database does not exist")
            return
        
        # Create backup
        backup_path = self.backup_database(self.memory_db_path)
        
        try:
            conn = sqlite3.connect(self.memory_db_path)
            cursor = conn.cursor()
            
            # Get database statistics before cleanup
            stats_before = self.get_database_stats(cursor, "memory")
            
            # Clean old memory entries (older than 90 days)
            cursor.execute("""
                DELETE FROM memory_entries 
                WHERE created_at < datetime('now', '-90 days')
            """)
            memory_deleted = cursor.rowcount
            
            # Clean old chat history (older than 30 days)
            cursor.execute("""
                DELETE FROM chat_history 
                WHERE timestamp < datetime('now', '-30 days')
            """)
            chat_deleted = cursor.rowcount
            
            # Clean old cache entries (older than 7 days)
            cursor.execute("""
                DELETE FROM deepseek_cache 
                WHERE timestamp < datetime('now', '-7 days')
            """)
            cache_deleted = cursor.rowcount
            
            # Clean low-importance memory entries
            cursor.execute("""
                DELETE FROM memory_entries 
                WHERE importance < 3 AND access_count < 2
            """)
            low_importance_deleted = cursor.rowcount
            
            # Get statistics after cleanup
            stats_after = self.get_database_stats(cursor, "memory")
            
            conn.commit()
            conn.close()
            
            # Log cleanup results
            self.logger.info(f"Memory database cleanup completed:")
            self.logger.info(f"  - Memory entries deleted: {memory_deleted}")
            self.logger.info(f"  - Chat history deleted: {chat_deleted}")
            self.logger.info(f"  - Cache entries deleted: {cache_deleted}")
            self.logger.info(f"  - Low importance entries deleted: {low_importance_deleted}")
            
            # Display results
            self.display_cleanup_results("Memory Database", stats_before, stats_after)
            
        except Exception as e:
            self.logger.error(f"Error cleaning memory database: {e}")
            console.logger.info(f"[red]Error cleaning memory database: {e}[/red]")
    
    def get_database_stats(self, cursor, db_type: str) -> Dict[str, Any]:
        """Get database statistics"""
        stats = {}
        
        if db_type == "main":
            # Main database tables
            tables = ["conversations", "personas", "memory", "context"]
        else:
            # Memory database tables
            tables = ["memory_entries", "chat_history", "deepseek_cache", "embeddings", "persona_config"]
        
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                stats[table] = count
            except sqlite3.OperationalError:
                stats[table] = 0
        
        return stats
    
    def display_cleanup_results(self, db_name: str, stats_before: Dict, stats_after: Dict):
    """display_cleanup_results function."""
        """Display cleanup results in a table"""
        table = Table(title=f"{db_name} Cleanup Results")
        table.add_column("Table", style="cyan")
        table.add_column("Before", style="green")
        table.add_column("After", style="blue")
        table.add_column("Difference", style="yellow")
        
        for table_name in stats_before.keys():
            before = stats_before[table_name]
            after = stats_after.get(table_name, 0)
            difference = before - after
            
            table.add_row(
                table_name,
                str(before),
                str(after),
                f"{difference:+d}" if difference != 0 else "0"
            )
        
        console.logger.info(table)
    
    def optimize_database(self, db_path: Path):
    """optimize_database function."""
        """Optimize database performance"""
        if not db_path.exists():
            return
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Analyze tables for better query planning
            cursor.execute("ANALYZE")
            
            # Reindex tables
            cursor.execute("REINDEX")
            
            # Vacuum to reclaim space
            cursor.execute("VACUUM")
            
            conn.close()
            
            self.logger.info(f"Database optimized: {db_path}")
            
        except Exception as e:
            self.logger.error(f"Error optimizing database {db_path}: {e}")
    
    def clean_old_logs(self, days: int = 30):
    """clean_old_logs function."""
        """Clean old log files"""
        log_dir = self.data_dir / "logs"
        if not log_dir.exists():
            return
        
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_count = 0
        
        for log_file in log_dir.glob("*.log"):
            try:
                file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                if file_time < cutoff_date:
                    log_file.unlink()
                    deleted_count += 1
            except Exception as e:
                self.logger.error(f"Error deleting log file {log_file}: {e}")
        
        self.logger.info(f"Deleted {deleted_count} old log files")
    
    def clean_old_backups(self, days: int = 7):
    """clean_old_backups function."""
        """Clean old backup files"""
        if not self.backup_dir.exists():
            return
        
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_count = 0
        
        for backup_file in self.backup_dir.glob("*.db"):
            try:
                file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
                if file_time < cutoff_date:
                    backup_file.unlink()
                    deleted_count += 1
            except Exception as e:
                self.logger.error(f"Error deleting backup file {backup_file}: {e}")
        
        self.logger.info(f"Deleted {deleted_count} old backup files")
    
    def clean_cache_files(self) -> Any:
        """Clean cache files"""
        cache_dirs = [
            self.data_dir / "cache",
            self.data_dir / "temp_embeddings",
            self.data_dir / "models" / ".cache"
        ]
        
        for cache_dir in cache_dirs:
            if cache_dir.exists():
                try:
                    shutil.rmtree(cache_dir)
                    cache_dir.mkdir(exist_ok=True)
                    self.logger.info(f"Cleaned cache directory: {cache_dir}")
                except Exception as e:
                    self.logger.error(f"Error cleaning cache directory {cache_dir}: {e}")
    
    def run_full_cleanup(self) -> Any:
        """Run complete database cleanup and maintenance"""
        console.logger.info(Panel.fit(
            "[bold blue]BASED CODER CLI - Database Cleanup & Maintenance[/bold blue]\n"
            "Running comprehensive cleanup...",
            title="Database Maintenance"
        ))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            # Clean databases
            progress.add_task("Cleaning main database...", total=None)
            self.clean_main_database()
            
            progress.add_task("Cleaning memory database...", total=None)
            self.clean_memory_database()
            
            # Optimize databases
            progress.add_task("Optimizing databases...", total=None)
            self.optimize_database(self.main_db_path)
            self.optimize_database(self.memory_db_path)
            
            # Clean old files
            progress.add_task("Cleaning old logs...", total=None)
            self.clean_old_logs()
            
            progress.add_task("Cleaning old backups...", total=None)
            self.clean_old_backups()
            
            progress.add_task("Cleaning cache files...", total=None)
            self.clean_cache_files()
        
        console.logger.info(Panel.fit(
            "[bold green]Database cleanup completed successfully![/bold green]\n"
            "All databases have been cleaned, optimized, and backed up.",
            title="Cleanup Complete"
        ))
        
        self.logger.info("Full database cleanup completed")

def main() -> None:
    """Main function"""
    cleaner = DatabaseCleaner()
    cleaner.run_full_cleanup()

if __name__ == "__main__":
    main() 