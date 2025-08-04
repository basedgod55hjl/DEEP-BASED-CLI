#!/usr/bin/env python3
"""
Transformers Deanna Memory System Setup
Uses Qwen3-Embedding-0.6B with transformers pipeline
"""

import os
from typing import List, Dict, Any, Optional, Tuple

import sys
import json
import subprocess
from pathlib import Path
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/transformers_setup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TransformersDeannaSetup:
    """Setup for Deanna memory system using transformers"""
    
    def __init__(self) -> Any:
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        # API Keys (hardcoded as requested)
        self.huggingface_token = "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"
        self.deepseek_token = "sk-90e0dd863b8c4e0d879a02851a0ee194"
        
        logger.info("TransformersDeannaSetup initialized")
    
    def setup_directories(self) -> Any:
        """Create all necessary directories"""
        directories = [
            "data/memory",
            "data/embeddings", 
            "data/chats",
            "data/logs",
            "data/cache",
            "data/models",
            "data/exports"
        ]
        
        for dir_path in directories:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {dir_path}")
    
    def install_dependencies(self) -> Any:
        """Install required Python dependencies"""
        requirements = [
            "numpy",
            "scikit-learn", 
            "requests",
            "huggingface_hub",
            "transformers>=4.51.0",
            "torch",
            "torchvision",
            "accelerate"
        ]
        
        logger.info("Installing Python dependencies...")
        
        for package in requirements:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", package], 
                             check=True, capture_output=True)
                logger.info(f"Installed {package}")
            except subprocess.CalledProcessError as e:
                logger.warning(f"Failed to install {package}: {e}")
    
    def initialize_memory_manager(self) -> Any:
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
    
    def initialize_transformers_embedding_system(self) -> Any:
        """Initialize the transformers embedding system"""
        logger.info("Initializing transformers embedding system...")
        
        try:
            from data.transformers_embedding_system import TransformersEmbeddingSystem
            
            # Initialize transformers embedding system
            embedding_system = TransformersEmbeddingSystem()
            
            # Test the system
            if embedding_system.test_embedding():
                logger.info("Transformers embedding system working")
                return embedding_system
            else:
                logger.error("Transformers embedding system test failed")
                return None
                
        except Exception as e:
            logger.error(f"Failed to initialize transformers embedding system: {e}")
            return None
    
    def update_memory_embeddings(self, memory_manager, embedding_system) -> Any:
        """Update embeddings for all memory entries"""
        logger.info("Updating memory embeddings with transformers...")
        
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
    
    def setup_deepseek_integration(self) -> Any:
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
    
    def create_system_config(self) -> Any:
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
                "type": "Transformers",
                "model": "Qwen/Qwen3-Embedding-0.6B",
                "dimension": 1024,
                "local": True,
                "cuda_enabled": True,
                "pipeline": True
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
                "transformers_embeddings": True
            }
        }
        
        config_file = self.data_dir / "system_config.json"
        with open(config_file, 'w') as f:
            json.dump(system_config, f, indent=2)
        
        logger.info(f"System config saved to {config_file}")
    
    def test_system(self) -> Any:
        """Test the complete system"""
        logger.info("Testing complete system...")
        
        try:
            # Test memory manager
            from data.memory_manager import memory_manager
            stats = memory_manager.get_memory_stats()
            logger.info(f"Memory manager test: {stats}")
            
            # Test transformers embedding system
            from data.transformers_embedding_system import TransformersEmbeddingSystem
            embedding_system = TransformersEmbeddingSystem()
            
            if embedding_system.test_embedding():
                logger.info("Transformers embedding system test: PASSED")
            else:
                logger.error("Transformers embedding system test: FAILED")
            
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
            embedding = embedding_system.create_embedding(test_text)
            logger.info(f"Embedding test: {len(embedding)} dimensions")
            
            # Get model info
            model_info = embedding_system.get_model_info()
            logger.info(f"Model info: {model_info}")
            
            logger.info("System test completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"System test failed: {e}")
            return False
    
    def export_system_status(self) -> Any:
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
        except Exception:
            status["memory_stats"] = "Not available"
        
        # Add embedding stats if available
        try:
            from data.transformers_embedding_system import TransformersEmbeddingSystem
            embedding_system = TransformersEmbeddingSystem()
            status["embedding_info"] = embedding_system.get_model_info()
        except Exception:
            status["embedding_info"] = "Not available"
        
        status_file = self.data_dir / "system_status.json"
        with open(status_file, 'w') as f:
            json.dump(status, f, indent=2)
        
        logger.info(f"System status exported to {status_file}")
        return status
    
    def run_transformers_setup(self) -> Any:
        """Run the transformers setup process"""
        logger.info("Starting transformers Deanna system setup...")
        
        try:
            # Step 1: Setup directories
            self.setup_directories()
            
            # Step 2: Install dependencies
            self.install_dependencies()
            
            # Step 3: Initialize memory manager
            memory_manager = self.initialize_memory_manager()
            if not memory_manager:
                logger.error("Memory manager initialization failed")
                return False
            
            # Step 4: Initialize transformers embedding system
            embedding_system = self.initialize_transformers_embedding_system()
            if not embedding_system:
                logger.error("Transformers embedding system initialization failed")
                return False
            
            # Step 5: Update memory embeddings
            self.update_memory_embeddings(memory_manager, embedding_system)
            
            # Step 6: Setup DeepSeek integration
            self.setup_deepseek_integration()
            
            # Step 7: Create system config
            self.create_system_config()
            
            # Step 8: Test system
            if not self.test_system():
                logger.warning("System test failed")
            
            # Step 9: Export status
            status = self.export_system_status()
            
            logger.info("‚úÖ Transformers Deanna system setup finished!")
            logger.info(f"üìä System status: {status}")
            
            return True
            
        except Exception as e:
            logger.error(f"Setup failed: {e}")
            return False

def main() -> None:
    """Main setup function"""
    logging.info("üöÄ Transformers Deanna Memory System Setup")
    logging.info("=" * 50)
    
    setup = TransformersDeannaSetup()
    
    if setup.run_transformers_setup():
        logging.info("\n‚úÖ Setup completed successfully!")
        logging.info("\nüìÅ System components:")
        logging.info("   ‚Ä¢ Memory Manager: data/memory_manager.py")
        logging.info("   ‚Ä¢ Transformers Embeddings: data/transformers_embedding_system.py")
        logging.info("   ‚Ä¢ Database: data/deanna_memory.db")
        logging.info("   ‚Ä¢ Config: data/system_config.json")
        logging.info("   ‚Ä¢ Status: data/system_status.json")
        logging.info("\nüé≠ Deanna persona is ready to use!")
        logging.info("\nüîß Features:")
        logging.info("   ‚Ä¢ Qwen3-Embedding-0.6B with transformers")
        logging.info("   ‚Ä¢ CUDA acceleration (if available)")
        logging.info("   ‚Ä¢ Memory caching and search")
        logging.info("   ‚Ä¢ DeepSeek API integration")
        logging.info("   ‚Ä¢ Chat history storage")
        logging.info("   ‚Ä¢ Persona configuration")
        
    else:
        logging.info("\n‚ùå Setup failed! Check logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    main() 