#!/usr/bin/env python3
"""
Simple Test Script for DEEP-CLI
Tests basic functionality without complex imports
"""

import asyncio
import logging
import hashlib
import numpy as np
from pathlib import Path
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleEmbeddingTest:
    """Simple embedding test using hash-based embeddings"""
    
    def __init__(self):
        self.embedding_dim = 384
        
    def create_embedding(self, text: str) -> np.ndarray:
        """Create a simple hash-based embedding"""
        # Create a simple hash-based embedding
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Convert to numpy array
        embedding = np.frombuffer(hash_bytes, dtype=np.float32)
        
        # Pad or truncate to embedding_dim
        if len(embedding) < self.embedding_dim:
            padding = np.zeros(self.embedding_dim - len(embedding), dtype=np.float32)
            embedding = np.concatenate([embedding, padding])
        else:
            embedding = embedding[:self.embedding_dim]
        
        # Normalize
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
    
    def test_embedding(self):
        """Test the embedding system"""
        try:
            logger.info("Testing simple embedding system...")
            
            test_texts = [
                "Hello world",
                "This is a test",
                "Embedding system working"
            ]
            
            embeddings = []
            for text in test_texts:
                embedding = self.create_embedding(text)
                embeddings.append(embedding)
                logger.info(f"Created embedding for '{text}': {len(embedding)} dimensions")
            
            # Test similarity
            sim = self.compute_similarity(embeddings[0], embeddings[1])
            logger.info(f"Similarity between first two texts: {sim:.4f}")
            
            logger.info("✅ Simple embedding test passed!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Simple embedding test failed: {e}")
            return False

class SimpleDatabaseTest:
    """Simple database test using JSON files"""
    
    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.db_file = self.data_dir / "simple_test_db.json"
    
    def store_persona(self, persona_data: dict):
        """Store persona data in JSON file"""
        try:
            # Load existing data
            if self.db_file.exists():
                with open(self.db_file, 'r') as f:
                    data = json.load(f)
            else:
                data = {"personas": []}
            
            # Add new persona
            data["personas"].append(persona_data)
            
            # Save data
            with open(self.db_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"✅ Stored persona: {persona_data.get('name', 'Unknown')}")
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
    
    def test_database(self):
        """Test the database system"""
        try:
            logger.info("Testing simple database system...")
            
            # Test storing persona
            persona_data = {
                "name": "Deanna",
                "description": "AI Assistant",
                "personality": "Helpful and knowledgeable"
            }
            
            if self.store_persona(persona_data):
                # Test retrieving personas
                personas = self.get_personas()
                logger.info(f"Retrieved {len(personas)} personas")
                
                logger.info("✅ Simple database test passed!")
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"❌ Simple database test failed: {e}")
            return False

async def run_simple_tests():
    """Run simple system tests"""
    logger.info("🚀 Running Simple DEEP-CLI Tests...")
    
    # Test embedding system
    embedding_test = SimpleEmbeddingTest()
    embedding_result = embedding_test.test_embedding()
    
    # Test database system
    database_test = SimpleDatabaseTest()
    database_result = database_test.test_database()
    
    # Print summary
    logger.info("\n" + "="*50)
    logger.info("📊 SIMPLE TEST RESULTS")
    logger.info("="*50)
    
    tests = [
        ("Simple Embedding System", embedding_result),
        ("Simple Database System", database_result)
    ]
    
    passed = 0
    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\nOverall: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        logger.info("🎉 All simple tests passed!")
        logger.info("\n📋 What you can do:")
        logger.info("- Create embeddings for text using hash-based method")
        logger.info("- Store and retrieve personas using JSON database")
        logger.info("- The system is ready for basic functionality")
    else:
        logger.info("⚠️  Some tests failed. Check logs for details.")
    
    return passed == len(tests)

async def interactive_demo():
    """Run interactive demo"""
    logger.info("🤖 Simple DEEP-CLI Interactive Demo")
    logger.info("Type 'quit' to exit, 'help' for commands")
    
    embedding_test = SimpleEmbeddingTest()
    database_test = SimpleDatabaseTest()
    
    while True:
        try:
            user_input = input("\n> ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                logger.info("Goodbye!")
                break
            
            elif user_input.lower() == 'help':
                logger.info("""
Available Commands:
- help: Show this help
- embed <text>: Create embedding for text
- store <name> <description>: Store a persona
- list: List all personas
- quit/exit/q: Exit the program
                """)
            
            elif user_input.lower().startswith('embed '):
                text = user_input[6:]  # Remove 'embed ' prefix
                embedding = embedding_test.create_embedding(text)
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
                    if database_test.store_persona(persona_data):
                        logger.info(f"Stored persona: {name}")
                    else:
                        logger.error("Failed to store persona")
                else:
                    logger.error("Usage: store <name> <description>")
            
            elif user_input.lower() == 'list':
                personas = database_test.get_personas()
                if personas:
                    logger.info("Stored personas:")
                    for persona in personas:
                        logger.info(f"- {persona.get('name', 'Unknown')}: {persona.get('description', 'No description')}")
                else:
                    logger.info("No personas stored yet")
            
            else:
                logger.info("Unknown command. Type 'help' for available commands.")
                
        except KeyboardInterrupt:
            logger.info("\nGoodbye!")
            break
        except Exception as e:
            logger.error(f"Error: {e}")

async def main():
    """Main function"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "test":
            await run_simple_tests()
        elif command == "demo":
            await interactive_demo()
        else:
            logger.info("Usage: python simple_test.py [test|demo]")
    else:
        # Default to tests
        await run_simple_tests()

if __name__ == "__main__":
    import sys
    asyncio.run(main()) 