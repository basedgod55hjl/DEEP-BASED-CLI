import logging
logger = logging.getLogger(__name__)
#!/usr/bin/env python3
"""
Setup Deanna Persona from DEANNA_MEMORY.JSON
Loads the existing persona configuration without modification
"""

import json
import sqlite3
from datetime import datetime
import os

def load_deanna_memory():
    """Load the DEANNA_MEMORY.JSON file"""
    json_path = "data/DEANNA_MEMORY.JSON"
    
    if not os.path.exists(json_path):
        logger.info(f"Error: {json_path} not found!")
        return None
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            deanna_data = json.load(f)
        logger.info(f"Successfully loaded {json_path}")
        return deanna_data
    except Exception as e:
        logger.info(f"Error loading {json_path}: {e}")
        return None

def setup_database():
    """Initialize the database with required tables"""
    conn = sqlite3.connect('deepcli_database.db')
    cursor = conn.cursor()
    
    # Create personas table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS personas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            personality_traits TEXT,
            knowledge_base TEXT,
            conversation_style TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # Create memory table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            content TEXT NOT NULL,
            importance INTEGER DEFAULT 5,
            access_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            persona_id INTEGER,
            tags TEXT,
            FOREIGN KEY (persona_id) REFERENCES personas(id)
        )
    ''')
    
    conn.commit()
    return conn, cursor

def insert_deanna_persona(conn, cursor, deanna_data):
    """Insert Deanna persona into the database"""
    
    # Extract persona information from JSON
    persona_info = {
        'name': deanna_data.get('name', 'DEANNA'),
        'description': deanna_data.get('description', ''),
        'personality_traits': json.dumps(deanna_data.get('personality_traits', [])),
        'knowledge_base': json.dumps({
            'personality': deanna_data.get('personality', ''),
            'conversation_style': deanna_data.get('conversation_style', {}),
            'key_phrases': deanna_data.get('key_phrases', []),
            'explicit_words': deanna_data.get('explicit_words', []),
            'greeting_templates': deanna_data.get('greeting_templates', []),
            'farewell_templates': deanna_data.get('farewell_templates', [])
        }),
        'conversation_style': json.dumps(deanna_data.get('conversation_style', {})),
        'is_active': 1
    }
    
    # Insert or replace persona
    cursor.execute('''
        INSERT OR REPLACE INTO personas 
        (name, description, personality_traits, knowledge_base, conversation_style, is_active, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        persona_info['name'],
        persona_info['description'],
        persona_info['personality_traits'],
        persona_info['knowledge_base'],
        persona_info['conversation_style'],
        persona_info['is_active'],
        datetime.now().isoformat(),
        datetime.now().isoformat()
    ))
    
    persona_id = cursor.lastrowid
    logger.info(f"Deanna persona configured with ID: {persona_id}")
    
    return persona_id

def insert_memory_entries(conn, cursor, persona_id, deanna_data):
    """Insert memory entries from the JSON data"""
    
    # Insert system prompt as memory
    if 'system_prompt' in deanna_data:
        cursor.execute('''
            INSERT INTO memory (category, content, importance, persona_id, tags)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            'system_prompt',
            deanna_data['system_prompt'],
            10,  # High importance
            persona_id,
            'core,personality'
        ))
    
    # Insert additional context as memory
    if 'additional_context' in deanna_data:
        for key, value in deanna_data['additional_context'].items():
            cursor.execute('''
                INSERT INTO memory (category, content, importance, persona_id, tags)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                f'context_{key}',
                json.dumps(value),
                8,  # High importance
                persona_id,
                'context,background'
            ))
    
    # Insert behavioral patterns
    if 'behavioral_patterns' in deanna_data:
        cursor.execute('''
            INSERT INTO memory (category, content, importance, persona_id, tags)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            'behavioral_patterns',
            json.dumps(deanna_data['behavioral_patterns']),
            9,  # High importance
            persona_id,
            'behavior,patterns'
        ))
    
    # Insert response preferences
    if 'response_preferences' in deanna_data:
        cursor.execute('''
            INSERT INTO memory (category, content, importance, persona_id, tags)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            'response_preferences',
            json.dumps(deanna_data['response_preferences']),
            9,  # High importance
            persona_id,
            'responses,preferences'
        ))
    
    logger.info("Memory entries inserted successfully")

def main():
    """Main function to set up Deanna persona"""
    logger.info("Setting up Deanna persona from DEANNA_MEMORY.JSON...")
    
    # Load the JSON data
    deanna_data = load_deanna_memory()
    if not deanna_data:
        return
    
    # Setup database
    conn, cursor = setup_database()
    
    try:
        # Insert persona
        persona_id = insert_deanna_persona(conn, cursor, deanna_data)
        
        # Insert memory entries
        insert_memory_entries(conn, cursor, persona_id, deanna_data)
        
        # Commit changes
        conn.commit()
        
        logger.info("✅ Deanna persona successfully configured!")
        logger.info(f"📊 Persona ID: {persona_id}")
        logger.info("🎭 Using original DEANNA_MEMORY.JSON configuration")
        logger.info("💾 All data stored in deepcli_database.db")
        
    except Exception as e:
        logger.info(f"❌ Error setting up persona: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    main() 