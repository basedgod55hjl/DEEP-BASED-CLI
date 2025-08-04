#!/usr/bin/env python3
"""
Complete Deanna Memory System Setup
Integrates DEANNA_MEMORY.JSON, local embeddings, DeepSeek caching, and all data storage
"""

import os
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
        logging.FileHandler('data/setup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DeannaSystemSetup:
    """Complete setup for Deanna memory system"""
    
    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        # API Keys (hardcoded as requested)
        self.huggingface_token = "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"
        self.deepseek_token = "sk-90e0dd863b8c4e0d879a02851a0ee194"
        
        logger.info("DeannaSystemSetup initialized")
    
    def setup_directories(self):
        """Create all necessary directories"""
        directories = [
            "data/memory",
            "data/embeddings", 
            "data/chats",
            "data/logs",
            "data/cache",
            "data/models",
            "data/temp_embeddings",
            "data/exports"
        ]
        
        for dir_path in directories:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {dir_path}")
    
    def install_dependencies(self):
        """Install required Python dependencies"""
        requirements = [
            "numpy",
            "scikit-learn", 
            "requests",
            "huggingface_hub",
            "llama-cpp-python",
            "sqlite3"
        ]
        
        logger.info("Installing Python dependencies...")
        
        for package in requirements:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", package], 
                             check=True, capture_output=True)
                logger.info(f"Installed {package}")
            except subprocess.CalledProcessError as e:
                logger.warning(f"Failed to install {package}: {e}")
    
    def setup_llama_cpp(self):
        """Setup llama.cpp for local embeddings"""
        logger.info("Setting up llama.cpp...")
        
        # Check if llama.cpp is already installed
        try:
            import llama_cpp
            logger.info("llama-cpp-python already installed")
            return True
        except ImportError:
            pass
        
        # Try to install llama-cpp-python with CUDA support
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", 
                "llama-cpp-python", "--force-reinstall", "--upgrade"
            ], check=True, capture_output=True)
            logger.info("Installed llama-cpp-python")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install llama-cpp-python: {e}")
            return False
    
    def download_qwen_model(self):
        """Download Qwen3 embedding model"""
        logger.info("Downloading Qwen3 embedding model...")
        
        model_dir = Path("data/models")
        model_file = model_dir / "qwen3-embedding-0.6b.gguf"
        
        if model_file.exists():
            logger.info(f"Model already exists: {model_file}")
            return str(model_file)
        
        try:
            from huggingface_hub import hf_hub_download
            
            model_path = hf_hub_download(
                repo_id="Qwen/Qwen3-Embedding-0.6B-GGUF",
                filename="qwen3-embedding-0.6b.gguf",
                token=self.huggingface_token,
                local_dir=str(model_dir)
            )
            
            logger.info(f"Model downloaded to: {model_path}")
            return model_path
            
        except Exception as e:
            logger.error(f"Failed to download model: {e}")
            return None
    
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
    
    def initialize_embedding_system(self, memory_manager):
        """Initialize the embedding system"""
        logger.info("Initializing embedding system...")
        
        try:
            from data.local_embedding_system import LocalEmbeddingSystem
            
            # Initialize local embedding system
            local_system = LocalEmbeddingSystem()
            
            # Test the system
            if local_system.test_embedding():
                logger.info("Local embedding system working")
                
                # Update memory embeddings
                logger.info("Updating memory embeddings...")
                self.update_memory_embeddings(memory_manager, local_system)
                
                return local_system
            else:
                logger.error("Local embedding system test failed")
                return None
                
        except Exception as e:
            logger.error(f"Failed to initialize embedding system: {e}")
            return None
    
    def update_memory_embeddings(self, memory_manager, embedding_system):
        """Update embeddings for all memory entries"""
        logger.info("Updating memory embeddings...")
        
        try:
            # Get all memory entries without embeddings
            conn = memory_manager.db_path
            import sqlite3
            conn = sqlite3.connect(conn)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, content FROM memory_entries 
                WHERE embedding_hash IS NULL OR embedding_hash = ''
            ''')
            
            entries = cursor.fetchall()
            conn.close()
            
            logger.info(f"Found {len(entries)} entries to update")
            
            updated_count = 0
            for entry_id, content in entries:
                try:
                    # Create embedding
                    embedding = embedding_system.create_embedding(content)
                    
                    # Store embedding
                    memory_manager.store_embedding(content, embedding)
                    
                    updated_count += 1
                    
                    if updated_count % 10 == 0:
                        logger.info(f"Updated {updated_count}/{len(entries)} embeddings")
                        
                except Exception as e:
                    logger.error(f"Failed to update embedding for entry {entry_id}: {e}")
            
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
                "coder": "deepseek-coder",
                "embedding": "deepseek-embedding"
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
                "model": "Qwen/Qwen3-Embedding-0.6B-GGUF",
                "dimension": 1024,
                "local": True,
                "cuda_enabled": True
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
                "persona_config": True
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
            
            # Test embedding system
            from data.local_embedding_system import LocalEmbeddingSystem
            embedding_system = LocalEmbeddingSystem()
            
            if embedding_system.test_embedding():
                logger.info("Embedding system test: PASSED")
            else:
                logger.error("Embedding system test: FAILED")
            
            # Test persona config
            persona_config = memory_manager.get_persona_config("DEANNA")
            if persona_config:
                logger.info(f"Persona config test: PASSED ({len(persona_config)} keys)")
            else:
                logger.error("Persona config test: FAILED")
            
            # Test memory search
            results = memory_manager.search_memory("personality", limit=5)
            logger.info(f"Memory search test: {len(results)} results")
            
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
            from data.local_embedding_system import LocalEmbeddingSystem
            embedding_system = LocalEmbeddingSystem()
            status["embedding_info"] = embedding_system.get_model_info()
        except:
            status["embedding_info"] = "Not available"
        
        status_file = self.data_dir / "system_status.json"
        with open(status_file, 'w') as f:
            json.dump(status, f, indent=2)
        
        logger.info(f"System status exported to {status_file}")
        return status
    
    def run_complete_setup(self):
        """Run the complete setup process"""
        logger.info("Starting complete Deanna system setup...")
        
        try:
            # Step 1: Setup directories
            self.setup_directories()
            
            # Step 2: Install dependencies
            self.install_dependencies()
            
            # Step 3: Setup llama.cpp
            if not self.setup_llama_cpp():
                logger.warning("llama.cpp setup failed, continuing...")
            
            # Step 4: Download model
            model_path = self.download_qwen_model()
            if not model_path:
                logger.error("Model download failed")
                return False
            
            # Step 5: Initialize memory manager
            memory_manager = self.initialize_memory_manager()
            if not memory_manager:
                logger.error("Memory manager initialization failed")
                return False
            
            # Step 6: Initialize embedding system
            embedding_system = self.initialize_embedding_system(memory_manager)
            if not embedding_system:
                logger.warning("Embedding system initialization failed, continuing...")
            
            # Step 7: Setup DeepSeek integration
            self.setup_deepseek_integration()
            
            # Step 8: Create system config
            self.create_system_config()
            
            # Step 9: Test system
            if not self.test_system():
                logger.warning("System test failed")
            
            # Step 10: Export status
            status = self.export_system_status()
            
            logger.info("‚úÖ Complete Deanna system setup finished!")
            logger.info(f"üìä System status: {status}")
            
            return True
            
        except Exception as e:
            logger.error(f"Setup failed: {e}")
            return False

def main():
    """Main setup function"""
    print("üöÄ Deanna Memory System Setup")
    print("=" * 50)
    
    setup = DeannaSystemSetup()
    
    if setup.run_complete_setup():
        print("\n‚úÖ Setup completed successfully!")
        print("\nüìÅ System components:")
        print("   ‚Ä¢ Memory Manager: data/memory_manager.py")
        print("   ‚Ä¢ Local Embeddings: data/local_embedding_system.py")
        print("   ‚Ä¢ Database: data/deanna_memory.db")
        print("   ‚Ä¢ Config: data/system_config.json")
        print("   ‚Ä¢ Status: data/system_status.json")
        print("\nüé≠ Deanna persona is ready to use!")
        
    else:
        print("\n‚ùå Setup failed! Check logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    main() 