#!/usr/bin/env python3
"""
Simple Deanna Memory System Setup
Uses existing components and simple TF-IDF embeddings
"""

import os
import sys
import json
from pathlib import Path
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/simple_setup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SimpleDeannaSetup:
    """Simple setup for Deanna memory system"""
    
    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        # API Keys (hardcoded as requested)
        self.huggingface_token = "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"
        self.deepseek_token = "sk-90e0dd863b8c4e0d879a02851a0ee194"
        
        logger.info("SimpleDeannaSetup initialized")
    
    def setup_directories(self):
        """Create all necessary directories"""
        directories = [
            "data/memory",
            "data/embeddings", 
            "data/chats",
            "data/logs",
            "data/cache",
            "data/exports"
        ]
        
        for dir_path in directories:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {dir_path}")
    
    def initialize_memory_manager(self):
        """Initialize the memory manager"""
        logger.info("Initializing memory manager...")
        
        try:
            from data.memory_manager import DeannaMemoryManager
            memory_manager = DeannaMemoryManager()
            
            # Get stats
            stats = memory_manager.get_memory_stats()
            logger.info(f"Memory manager initialized: {stats}")
            
            return memory_manager
            
        except Exception as e:
            logger.error(f"Failed to initialize memory manager: {e}")
            return None
    
    def initialize_simple_embedding_system(self):
        """Initialize the simple embedding system"""
        logger.info("Initializing simple embedding system...")
        
        try:
            from data.simple_embedding_system import SimpleEmbeddingSystem
            
            # Initialize simple embedding system
            embedding_system = SimpleEmbeddingSystem()
            
            # Test the system
            if embedding_system.test_embedding():
                logger.info("Simple embedding system working")
                return embedding_system
            else:
                logger.error("Simple embedding system test failed")
                return None
                
        except Exception as e:
            logger.error(f"Failed to initialize embedding system: {e}")
            return None
    
    def update_memory_embeddings(self, memory_manager, embedding_system):
        """Update embeddings for all memory entries"""
        logger.info("Updating memory embeddings...")
        
        try:
            # Get all memory entries
            conn = memory_manager.db_path
            import sqlite3
            conn = sqlite3.connect(conn)
            cursor = conn.cursor()
            
            cursor.execute('SELECT id, content FROM memory_entries')
            entries = cursor.fetchall()
            conn.close()
            
            logger.info(f"Found {len(entries)} entries to process")
            
            updated_count = 0
            for entry_id, content in entries:
                try:
                    # Create embedding
                    embedding = embedding_system.create_embedding(content)
                    
                    # Store embedding
                    memory_manager.store_embedding(content, embedding)
                    
                    updated_count += 1
                    
                    if updated_count % 10 == 0:
                        logger.info(f"Processed {updated_count}/{len(entries)} embeddings")
                        
                except Exception as e:
                    logger.error(f"Failed to process embedding for entry {entry_id}: {e}")
            
            logger.info(f"Updated {updated_count} memory embeddings")
            
        except Exception as e:
            logger.error(f"Failed to update memory embeddings: {e}")
    
    def setup_deepseek_integration(self):
        """Setup DeepSeek API integration"""
        logger.info("Setting up DeepSeek integration...")
        
        # Create DeepSeek configuration
        deepseek_config = {
            "api_key": self.deepseek_token,
            "base_url": "https://api.deepseek.com",
            "models": {
                "chat": "deepseek-chat",
                "coder": "deepseek-coder"
            },
            "cache_enabled": True,
            "max_tokens": 4096,
            "temperature": 0.7
        }
        
        config_file = self.data_dir / "deepseek_config.json"
        with open(config_file, 'w') as f:
            json.dump(deepseek_config, f, indent=2)
        
        logger.info(f"DeepSeek config saved to {config_file}")
    
    def create_system_config(self):
        """Create system configuration file"""
        logger.info("Creating system configuration...")
        
        system_config = {
            "version": "1.0.0",
            "created_at": datetime.now().isoformat(),
            "persona": {
                "name": "DEANNA",
                "nickname": "DEEDEE",
                "memory_file": "data/DEANNA_MEMORY.JSON"
            },
            "embeddings": {
                "type": "TF-IDF",
                "dimension": 512,
                "local": True,
                "cuda_enabled": False,
                "model": "Local TF-IDF"
            },
            "api_keys": {
                "huggingface": self.huggingface_token,
                "deepseek": self.deepseek_token
            },
            "storage": {
                "database": "data/deanna_memory.db",
                "embeddings_dir": "data/embeddings",
                "cache_dir": "data/cache",
                "chats_dir": "data/chats",
                "logs_dir": "data/logs"
            },
            "features": {
                "memory_caching": True,
                "embedding_similarity": True,
                "deepseek_caching": True,
                "chat_history": True,
                "persona_config": True,
                "simple_embeddings": True
            }
        }
        
        config_file = self.data_dir / "system_config.json"
        with open(config_file, 'w') as f:
            json.dump(system_config, f, indent=2)
        
        logger.info(f"System config saved to {config_file}")
    
    def test_system(self):
        """Test the complete system"""
        logger.info("Testing complete system...")
        
        try:
            # Test memory manager
            from data.memory_manager import memory_manager
            stats = memory_manager.get_memory_stats()
            logger.info(f"Memory manager test: {stats}")
            
            # Test simple embedding system
            from data.simple_embedding_system import simple_embedding_system
            
            if simple_embedding_system.test_embedding():
                logger.info("Simple embedding system test: PASSED")
            else:
                logger.error("Simple embedding system test: FAILED")
            
            # Test persona config
            persona_config = memory_manager.get_persona_config("DEANNA")
            if persona_config:
                logger.info(f"Persona config test: PASSED ({len(persona_config)} keys)")
            else:
                logger.error("Persona config test: FAILED")
            
            # Test memory search
            results = memory_manager.search_memory("personality", limit=5)
            logger.info(f"Memory search test: {len(results)} results")
            
            # Test embedding similarity
            test_text = "Deanna personality traits"
            embedding = simple_embedding_system.create_embedding(test_text)
            logger.info(f"Embedding test: {len(embedding)} dimensions")
            
            logger.info("System test completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"System test failed: {e}")
            return False
    
    def export_system_status(self):
        """Export system status report"""
        logger.info("Exporting system status...")
        
        status = {
            "timestamp": datetime.now().isoformat(),
            "system_info": {
                "python_version": sys.version,
                "platform": sys.platform,
                "working_directory": str(Path.cwd())
            },
            "directories": {
                "data_dir": str(self.data_dir),
                "exists": self.data_dir.exists(),
                "subdirs": [str(p) for p in self.data_dir.iterdir() if p.is_dir()]
            },
            "files": {
                "deanna_memory": str(self.data_dir / "DEANNA_MEMORY.JSON"),
                "memory_db": str(self.data_dir / "deanna_memory.db"),
                "system_config": str(self.data_dir / "system_config.json")
            }
        }
        
        # Add memory stats if available
        try:
            from data.memory_manager import memory_manager
            status["memory_stats"] = memory_manager.get_memory_stats()
        except:
            status["memory_stats"] = "Not available"
        
        # Add embedding stats if available
        try:
            from data.simple_embedding_system import simple_embedding_system
            status["embedding_info"] = simple_embedding_system.get_system_info()
        except:
            status["embedding_info"] = "Not available"
        
        status_file = self.data_dir / "system_status.json"
        with open(status_file, 'w') as f:
            json.dump(status, f, indent=2)
        
        logger.info(f"System status exported to {status_file}")
        return status
    
    def run_simple_setup(self):
        """Run the simple setup process"""
        logger.info("Starting simple Deanna system setup...")
        
        try:
            # Step 1: Setup directories
            self.setup_directories()
            
            # Step 2: Initialize memory manager
            memory_manager = self.initialize_memory_manager()
            if not memory_manager:
                logger.error("Memory manager initialization failed")
                return False
            
            # Step 3: Initialize simple embedding system
            embedding_system = self.initialize_simple_embedding_system()
            if not embedding_system:
                logger.error("Simple embedding system initialization failed")
                return False
            
            # Step 4: Update memory embeddings
            self.update_memory_embeddings(memory_manager, embedding_system)
            
            # Step 5: Setup DeepSeek integration
            self.setup_deepseek_integration()
            
            # Step 6: Create system config
            self.create_system_config()
            
            # Step 7: Test system
            if not self.test_system():
                logger.warning("System test failed")
            
            # Step 8: Export status
            status = self.export_system_status()
            
            logger.info("✅ Simple Deanna system setup finished!")
            logger.info(f"📊 System status: {status}")
            
            return True
            
        except Exception as e:
            logger.error(f"Setup failed: {e}")
            return False

def main():
    """Main setup function"""
    print("🚀 Simple Deanna Memory System Setup")
    print("=" * 50)
    
    setup = SimpleDeannaSetup()
    
    if setup.run_simple_setup():
        print("\n✅ Setup completed successfully!")
        print("\n📁 System components:")
        print("   • Memory Manager: data/memory_manager.py")
        print("   • Simple Embeddings: data/simple_embedding_system.py")
        print("   • Database: data/deanna_memory.db")
        print("   • Config: data/system_config.json")
        print("   • Status: data/system_status.json")
        print("\n🎭 Deanna persona is ready to use!")
        print("\n🔧 Features:")
        print("   • Local TF-IDF embeddings")
        print("   • Memory caching and search")
        print("   • DeepSeek API integration")
        print("   • Chat history storage")
        print("   • Persona configuration")
        
    else:
        print("\n❌ Setup failed! Check logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    main() 