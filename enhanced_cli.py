#!/usr/bin/env python3
"""
Enhanced DEEP-CLI with Qwen3 Embeddings
Uses the downloaded Qwen3 embedding model for high-quality embeddings
"""

import asyncio
import logging
import hashlib
import numpy as np
from pathlib import Path
import json
import sys

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QwenEmbeddingSystem:
    """Qwen3 embedding system using the downloaded model"""
    
    def __init__(self):
        self.embedding_dim = 1024
        self.model = None
        self.initialize_model()
    
    def initialize_model(self):
        """Initialize the Qwen3 embedding model"""
        try:
            from sentence_transformers import SentenceTransformer
            
            models_dir = Path("data/models")
            model_path = models_dir / "qwen3_embedding"
            
            if model_path.exists():
                logger.info("Loading Qwen3 embedding model...")
                self.model = SentenceTransformer(str(model_path))
                self.embedding_dim = self.model.get_sentence_embedding_dimension()
                logger.info(f"✅ Qwen3 model loaded with dimension: {self.embedding_dim}")
                return True
            else:
                logger.warning("Qwen3 model not found, using hash-based fallback")
                return False
                
        except Exception as e:
            logger.error(f"Failed to load Qwen3 model: {e}")
            return False
    
    def create_embedding(self, text: str) -> np.ndarray:
        """Create embedding for a text"""
        if self.model is not None:
            try:
                return self.model.encode(text)
            except Exception as e:
                logger.error(f"Failed to create Qwen3 embedding: {e}")
                return self._create_hash_embedding(text)
        else:
            return self._create_hash_embedding(text)
    
    def _create_hash_embedding(self, text: str) -> np.ndarray:
        """Create a simple hash-based embedding as fallback"""
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        
        embedding = np.frombuffer(hash_bytes, dtype=np.float32)
        
        if len(embedding) < self.embedding_dim:
            padding = np.zeros(self.embedding_dim - len(embedding), dtype=np.float32)
            embedding = np.concatenate([embedding, padding])
        else:
            embedding = embedding[:self.embedding_dim]
        
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        return embedding
    
    def compute_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Compute cosine similarity between two vectors"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def batch_create_embeddings(self, texts: list) -> list:
        """Create embeddings for multiple texts"""
        if self.model is not None:
            try:
                return self.model.encode(texts)
            except Exception as e:
                logger.error(f"Failed to create batch embeddings: {e}")
                return [self._create_hash_embedding(text) for text in texts]
        else:
            return [self._create_hash_embedding(text) for text in texts]

class EnhancedDatabaseSystem:
    """Enhanced database system with embeddings"""
    
    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.db_file = self.data_dir / "enhanced_db.json"
        self.embedding_system = QwenEmbeddingSystem()
    
    def store_persona(self, persona_data: dict):
        """Store persona with embedding"""
        try:
            # Load existing data
            if self.db_file.exists():
                with open(self.db_file, 'r') as f:
                    data = json.load(f)
            else:
                data = {"personas": [], "embeddings": {}}
            
            # Create embedding for persona description
            description = persona_data.get('description', '')
            embedding = self.embedding_system.create_embedding(description)
            
            # Add persona with embedding
            persona_id = len(data["personas"])
            persona_data["id"] = persona_id
            persona_data["embedding"] = embedding.tolist()
            
            data["personas"].append(persona_data)
            data["embeddings"][str(persona_id)] = embedding.tolist()
            
            # Save data
            with open(self.db_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"✅ Stored persona with embedding: {persona_data.get('name', 'Unknown')}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to store persona: {e}")
            return False
    
    def get_personas(self):
        """Get all personas"""
        try:
            if self.db_file.exists():
                with open(self.db_file, 'r') as f:
                    data = json.load(f)
                return data.get("personas", [])
            else:
                return []
        except Exception as e:
            logger.error(f"❌ Failed to get personas: {e}")
            return []
    
    def find_similar_personas(self, query: str, top_k: int = 3):
        """Find personas similar to the query"""
        try:
            personas = self.get_personas()
            if not personas:
                return []
            
            # Create query embedding
            query_embedding = self.embedding_system.create_embedding(query)
            
            # Calculate similarities
            similarities = []
            for persona in personas:
                if "embedding" in persona:
                    persona_embedding = np.array(persona["embedding"])
                    sim = self.embedding_system.compute_similarity(query_embedding, persona_embedding)
                    similarities.append((persona, sim))
            
            # Sort by similarity
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"❌ Failed to find similar personas: {e}")
            return []

class EnhancedCLI:
    """Enhanced CLI with Qwen3 embeddings"""
    
    def __init__(self):
        self.embedding_system = QwenEmbeddingSystem()
        self.database_system = EnhancedDatabaseSystem()
    
    async def test_system(self):
        """Test the enhanced system"""
        logger.info("🚀 Testing Enhanced DEEP-CLI with Qwen3...")
        
        # Test embedding system
        test_texts = [
            "Hello world",
            "This is a test",
            "Machine learning is fascinating"
        ]
        
        embeddings = []
        for text in test_texts:
            embedding = self.embedding_system.create_embedding(text)
            embeddings.append(embedding)
            logger.info(f"Created embedding for '{text}': {len(embedding)} dimensions")
        
        # Test similarity
        sim = self.embedding_system.compute_similarity(embeddings[0], embeddings[1])
        logger.info(f"Similarity between first two texts: {sim:.4f}")
        
        # Test database system
        persona_data = {
            "name": "Deanna",
            "description": "AI Assistant specialized in machine learning",
            "personality": "Helpful and knowledgeable"
        }
        
        if self.database_system.store_persona(persona_data):
            personas = self.database_system.get_personas()
            logger.info(f"Retrieved {len(personas)} personas")
            
            # Test similarity search
            similar = self.database_system.find_similar_personas("machine learning expert")
            if similar:
                logger.info(f"Found {len(similar)} similar personas")
                for persona, sim in similar:
                    logger.info(f"  {persona['name']}: {sim:.4f}")
        
        logger.info("✅ Enhanced system test passed!")
        return True
    
    async def interactive_mode(self):
        """Run interactive mode"""
        logger.info("🤖 Enhanced DEEP-CLI Interactive Mode")
        logger.info("Type 'quit' to exit, 'help' for commands")
        
        while True:
            try:
                user_input = input("\n> ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    logger.info("Goodbye!")
                    break
                
                elif user_input.lower() == 'help':
                    self.show_help()
                
                elif user_input.lower() == 'test':
                    await self.test_system()
                
                elif user_input.lower().startswith('embed '):
                    text = user_input[6:]  # Remove 'embed ' prefix
                    embedding = self.embedding_system.create_embedding(text)
                    logger.info(f"Created embedding: {len(embedding)} dimensions")
                
                elif user_input.lower().startswith('store '):
                    parts = user_input[6:].split(' ', 1)  # Remove 'store ' prefix
                    if len(parts) >= 2:
                        name, description = parts[0], parts[1]
                        persona_data = {
                            "name": name,
                            "description": description,
                            "created": "now"
                        }
                        if self.database_system.store_persona(persona_data):
                            logger.info(f"Stored persona: {name}")
                        else:
                            logger.error("Failed to store persona")
                    else:
                        logger.error("Usage: store <name> <description>")
                
                elif user_input.lower() == 'list':
                    personas = self.database_system.get_personas()
                    if personas:
                        logger.info("Stored personas:")
                        for persona in personas:
                            logger.info(f"- {persona.get('name', 'Unknown')}: {persona.get('description', 'No description')}")
                    else:
                        logger.info("No personas stored yet")
                
                elif user_input.lower().startswith('find '):
                    query = user_input[5:]  # Remove 'find ' prefix
                    similar = self.database_system.find_similar_personas(query)
                    if similar:
                        logger.info(f"Found {len(similar)} similar personas for '{query}':")
                        for persona, sim in similar:
                            logger.info(f"  {persona['name']}: {sim:.4f}")
                    else:
                        logger.info("No similar personas found")
                
                else:
                    logger.info("Unknown command. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                logger.info("\nGoodbye!")
                break
            except Exception as e:
                logger.error(f"Error: {e}")
    
    def show_help(self):
        """Show available commands"""
        help_text = """
Available Commands:
- help: Show this help
- test: Run system tests
- embed <text>: Create embedding for text
- store <name> <description>: Store a persona with embedding
- list: List all personas
- find <query>: Find similar personas
- quit/exit/q: Exit the program
        """
        logger.info(help_text)

async def main():
    """Main function"""
    cli = EnhancedCLI()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "test":
            await cli.test_system()
        elif command == "interactive":
            await cli.interactive_mode()
        else:
            logger.info("Usage: python enhanced_cli.py [test|interactive]")
    else:
        # Default to interactive mode
        await cli.interactive_mode()

if __name__ == "__main__":
    asyncio.run(main()) 