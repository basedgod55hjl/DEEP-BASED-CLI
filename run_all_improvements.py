#!/usr/bin/env python3
"""
Run All Improvements Script for BASED CODER CLI
Executes all improvement scripts in the correct sequence
"""

import subprocess
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()

def run_script(script_name: str, description: str) -> bool:
    """Run a Python script and return success status"""
    console.print(f"🔄 Running {description}...")
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            console.print(f"✅ {description} completed successfully")
            return True
        else:
            console.print(f"❌ {description} failed with return code {result.returncode}")
            if result.stderr:
                console.print(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        console.print(f"⏰ {description} timed out after 5 minutes")
        return False
    except Exception as e:
        console.print(f"❌ {description} failed with exception: {e}")
        return False

def main():
    """Run all improvement scripts"""
    console.print(Panel.fit(
        "[bold blue]BASED CODER CLI - Complete System Improvement[/bold blue]\n"
        "Running all improvement scripts in sequence...",
        title="System Improvement"
    ))
    
    # Define the scripts to run in order
    scripts = [
        ("database_cleaner.py", "Database Cleanup and Optimization"),
        ("enhanced_logging.py", "Enhanced Logging System Test"),
        ("config_manager.py", "Configuration Management and Analysis"),
        ("system_status.py", "Comprehensive System Status Check")
    ]
    
    results = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        for script_name, description in scripts:
            task = progress.add_task(f"Running {description}...", total=None)
            
            success = run_script(script_name, description)
            results.append((description, success))
            
            progress.update(task, completed=True)
    
    # Display results summary
    console.print(Panel.fit("Improvement Results Summary", title="Results"))
    
    table = Table(title="Script Execution Results")
    table.add_column("Script", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Description", style="green")
    
    for description, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        table.add_row(description, status, "Completed successfully" if success else "Failed to complete")
    
    console.print(table)
    
    # Calculate success rate
    successful = sum(1 for _, success in results if success)
    total = len(results)
    success_rate = (successful / total) * 100
    
    console.print(Panel.fit(
        f"[bold]Final Results:[/bold]\n"
        f"✅ Successful: {successful}/{total}\n"
        f"📊 Success Rate: {success_rate:.1f}%\n"
        f"🎯 System Status: {'FULLY IMPROVED' if success_rate == 100 else 'PARTIALLY IMPROVED'}",
        title="Improvement Complete"
    ))
    
    if success_rate == 100:
        console.print(Panel.fit(
            "[bold green]🎉 All improvements completed successfully![/bold green]\n"
            "Your BASED CODER CLI system is now fully optimized with:\n"
            "• Clean and optimized databases\n"
            "• Enhanced logging and error handling\n"
            "• Comprehensive configuration management\n"
            "• Full system status monitoring\n\n"
            "Check the generated reports for detailed information.",
            title="Success!"
        ))
    else:
        console.print(Panel.fit(
            "[bold yellow]⚠️ Some improvements failed[/bold yellow]\n"
            "Please check the error messages above and run failed scripts individually.\n"
            "The system may still be partially improved.",
            title="Partial Success"
        ))

if __name__ == "__main__":
    main() 