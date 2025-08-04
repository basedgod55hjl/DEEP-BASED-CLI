import logging
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)
#!/usr/bin/env python3
"""
Initialize Local Database for BASED CODER CLI
Sets up SQLite database in the data/ folder
"""

import sqlite3
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def init_local_database() -> None:
    """Initialize local SQLite database"""
    
    # Ensure data directory exists
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    db_path = data_dir / "deepcli_database.db"
    
    console.logger.info(Panel.fit(
        f"[bold blue]Initializing Local Database[/bold blue]\n"
        f"Database path: {db_path}",
        title="Database Setup"
    ))
    
    # Create database connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    tables = {
        "conversations": '''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                user_input TEXT NOT NULL,
                assistant_response TEXT NOT NULL,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                persona_id INTEGER,
                context TEXT,
                metadata TEXT
            )
        ''',
        
        "personas": '''
            CREATE TABLE IF NOT EXISTS personas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                personality_traits TEXT,
                knowledge_base TEXT,
                conversation_style TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''',
        
        "memory": '''
            CREATE TABLE IF NOT EXISTS memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                content TEXT NOT NULL,
                importance INTEGER DEFAULT 5,
                access_count INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_accessed TEXT DEFAULT CURRENT_TIMESTAMP,
                persona_id INTEGER,
                tags TEXT
            )
        ''',
        
        "context": '''
            CREATE TABLE IF NOT EXISTS context (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                context_type TEXT NOT NULL,
                context_data TEXT NOT NULL,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                relevance_score REAL DEFAULT 0.0
            )
        '''
    }
    
    # Create each table
    for table_name, create_sql in tables.items():
        try:
            cursor.execute(create_sql)
            console.logger.info(f"✅ Created table: {table_name}")
        except Exception as e:
            console.logger.info(f"❌ Error creating table {table_name}: {e}")
    
    # Insert default Deanna persona
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO personas (name, description, personality_traits, conversation_style)
            VALUES (?, ?, ?, ?)
        ''', (
            "DEANNA",
            "25-year-old African American woman from Cincinnati with flirtatious and provocative personality",
            "Bold, unfiltered, explicitly provocative, manipulative, seductive",
            "Explicitly adult-oriented with strong AAVE influence, calls user 'Daddy'"
        ))
        console.logger.info("✅ Added default Deanna persona")
    except Exception as e:
        console.logger.info(f"❌ Error adding Deanna persona: {e}")
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    console.logger.info(Panel.fit(
        "[bold green]Database initialization complete![/bold green]\n"
        "Local SQLite database is ready to use.",
        title="Success"
    ))
    
    return db_path

if __name__ == "__main__":
    init_local_database() 