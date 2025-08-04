#!/usr/bin/env python3
"""
Enhanced Logging and Error Handling System for BASED CODER CLI
Provides comprehensive logging, error tracking, and system monitoring
"""

import logging
import logging.handlers
import sys
import os
import json
import traceback
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable
from functools import wraps
import threading
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()

class EnhancedLogger:
    """Enhanced logging system with error tracking and monitoring"""
    
    def __init__(self, name: str = "BASED_CODER_CLI", log_dir: str = "data/logs"):
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Setup handlers
        self.setup_handlers()
        
        # Error tracking
        self.error_count = 0
        self.warning_count = 0
        self.error_history = []
        
        # Performance tracking
        self.performance_metrics = {}
        
        # Thread safety
        self.lock = threading.Lock()
    
    def setup_handlers(self):
        """Setup various logging handlers"""
        
        # Create timestamped log file
        timestamp = datetime.now().strftime("%Y%m%d")
        log_file = self.log_dir / f"{self.name}_{timestamp}.log"
        
        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Error file handler
        error_file = self.log_dir / f"{self.name}_errors_{timestamp}.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_file,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3
        )
        error_handler.setLevel(logging.ERROR)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Apply formatters
        file_handler.setFormatter(detailed_formatter)
        error_handler.setFormatter(detailed_formatter)
        console_handler.setFormatter(simple_formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)
        self.logger.addHandler(console_handler)
    
    def log_error(self, error: Exception, context: str = "", extra_data: Dict = None):
        """Log error with context and tracking"""
        with self.lock:
            self.error_count += 1
            
            error_info = {
                'timestamp': datetime.now().isoformat(),
                'error_type': type(error).__name__,
                'error_message': str(error),
                'context': context,
                'traceback': traceback.format_exc(),
                'extra_data': extra_data or {}
            }
            
            self.error_history.append(error_info)
            
            # Keep only last 100 errors
            if len(self.error_history) > 100:
                self.error_history = self.error_history[-100:]
            
            # Log the error
            self.logger.error(
                f"Error in {context}: {error}",
                extra={'error_info': error_info}
            )
            
            # Save error to file
            self.save_error_report(error_info)
    
    def log_warning(self, message: str, context: str = "", extra_data: Dict = None):
        """Log warning with tracking"""
        with self.lock:
            self.warning_count += 1
            
            warning_info = {
                'timestamp': datetime.now().isoformat(),
                'message': message,
                'context': context,
                'extra_data': extra_data or {}
            }
            
            self.logger.warning(f"Warning in {context}: {message}")
    
    def log_performance(self, operation: str, duration: float, success: bool = True):
        """Log performance metrics"""
        with self.lock:
            if operation not in self.performance_metrics:
                self.performance_metrics[operation] = {
                    'count': 0,
                    'total_duration': 0,
                    'success_count': 0,
                    'failure_count': 0,
                    'min_duration': float('inf'),
                    'max_duration': 0
                }
            
            metrics = self.performance_metrics[operation]
            metrics['count'] += 1
            metrics['total_duration'] += duration
            metrics['min_duration'] = min(metrics['min_duration'], duration)
            metrics['max_duration'] = max(metrics['max_duration'], duration)
            
            if success:
                metrics['success_count'] += 1
            else:
                metrics['failure_count'] += 1
    
    def save_error_report(self, error_info: Dict):
        """Save error report to file"""
        error_report_file = self.log_dir / "error_reports.json"
        
        try:
            if error_report_file.exists():
                with open(error_report_file, 'r') as f:
                    reports = json.load(f)
            else:
                reports = []
            
            reports.append(error_info)
            
            # Keep only last 50 reports
            if len(reports) > 50:
                reports = reports[-50:]
            
            with open(error_report_file, 'w') as f:
                json.dump(reports, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save error report: {e}")
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get error summary statistics"""
        with self.lock:
            error_types = {}
            for error in self.error_history:
                error_type = error['error_type']
                error_types[error_type] = error_types.get(error_type, 0) + 1
            
            return {
                'total_errors': self.error_count,
                'total_warnings': self.warning_count,
                'error_types': error_types,
                'recent_errors': self.error_history[-10:] if self.error_history else []
            }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        with self.lock:
            summary = {}
            for operation, metrics in self.performance_metrics.items():
                if metrics['count'] > 0:
                    summary[operation] = {
                        'count': metrics['count'],
                        'avg_duration': metrics['total_duration'] / metrics['count'],
                        'min_duration': metrics['min_duration'],
                        'max_duration': metrics['max_duration'],
                        'success_rate': metrics['success_count'] / metrics['count'],
                        'failure_rate': metrics['failure_count'] / metrics['count']
                    }
            return summary
    
    def display_log_summary(self):
        """Display logging summary in rich format"""
        error_summary = self.get_error_summary()
        performance_summary = self.get_performance_summary()
        
        # Error summary table
        error_table = Table(title="Error Summary")
        error_table.add_column("Metric", style="cyan")
        error_table.add_column("Value", style="green")
        
        error_table.add_row("Total Errors", str(error_summary['total_errors']))
        error_table.add_row("Total Warnings", str(error_summary['total_warnings']))
        
        for error_type, count in error_summary['error_types'].items():
            error_table.add_row(f"Error Type: {error_type}", str(count))
        
        console.print(error_table)
        
        # Performance summary table
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
    
    def cleanup_old_logs(self, days: int = 30):
        """Clean up old log files"""
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_count = 0
        
        for log_file in self.log_dir.glob("*.log"):
            try:
                file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                if file_time < cutoff_date:
                    log_file.unlink()
                    deleted_count += 1
            except Exception as e:
                self.logger.error(f"Error deleting log file {log_file}: {e}")
        
        self.logger.info(f"Deleted {deleted_count} old log files")

def error_handler(logger: EnhancedLogger, context: str = ""):
    """Decorator for error handling and logging"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            try:
                result = func(*args, **kwargs)
                duration = (datetime.now() - start_time).total_seconds()
                logger.log_performance(f"{context}.{func.__name__}", duration, True)
                return result
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                logger.log_performance(f"{context}.{func.__name__}", duration, False)
                logger.log_error(e, f"{context}.{func.__name__}", {
                    'args': str(args),
                    'kwargs': str(kwargs)
                })
                raise
        return wrapper
    return decorator

def performance_monitor(logger: EnhancedLogger, operation: str):
    """Decorator for performance monitoring"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            try:
                result = func(*args, **kwargs)
                duration = (datetime.now() - start_time).total_seconds()
                logger.log_performance(operation, duration, True)
                return result
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                logger.log_performance(operation, duration, False)
                raise
        return wrapper
    return decorator

# Global logger instance
enhanced_logger = EnhancedLogger()

def get_logger() -> EnhancedLogger:
    """Get the global enhanced logger instance"""
    return enhanced_logger

def main():
    """Test the enhanced logging system"""
    logger = get_logger()
    
    console.print(Panel.fit(
        "[bold blue]Enhanced Logging System Test[/bold blue]\n"
        "Testing various logging features...",
        title="Logging Test"
    ))
    
    # Test different log levels
    logger.logger.info("This is an info message")
    logger.logger.warning("This is a warning message")
    
    # Test error logging
    try:
        raise ValueError("Test error for logging")
    except Exception as e:
        logger.log_error(e, "test_function")
    
    # Test performance logging
    logger.log_performance("test_operation", 1.5, True)
    logger.log_performance("test_operation", 0.8, False)
    
    # Display summary
    logger.display_log_summary()
    
    console.print(Panel.fit(
        "[bold green]Logging test completed![/bold green]\n"
        "Check the logs directory for detailed logs.",
        title="Test Complete"
    ))

if __name__ == "__main__":
    main() 