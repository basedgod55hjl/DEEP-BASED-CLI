import logging
logger = logging.getLogger(__name__)
#!/usr/bin/env python3
"""
Deanna Chat System
Complete integration of Deanna persona with memory, embeddings, and DeepSeek API
"""

import json
import uuid
import logging
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import sqlite3

# Import our components
from data.memory_manager import memory_manager
from data.transformers_embedding_system import initialize_transformers_embedding_system

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/deanna_chat.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DeannaChatSystem:
    """Complete chat system for Deanna persona"""
    
    def __init__(self) -> Any:
        self.persona_name = "DEANNA"
        self.nickname = "DEEDEE"
        
        # API Keys (hardcoded as requested)
        self.deepseek_token = "sk-90e0dd863b8c4e0d879a02851a0ee194"
        self.deepseek_base_url = "https://api.deepseek.com/v1"
        
        # Initialize components
        self.memory_manager = memory_manager
        self.embedding_system = initialize_transformers_embedding_system()
        
        # Chat history
        self.chat_history = []
        self.session_id = str(uuid.uuid4())
        
        logger.info(f"DeannaChatSystem initialized for {self.persona_name}")
    
    def get_persona_context(self) -> str:
        """Get Deanna's persona context from memory"""
        try:
            persona_config = self.memory_manager.get_persona_config(self.persona_name)
            if persona_config:
                # Extract system prompt and core personality
                system_prompt = persona_config.get("system_prompt", "")
                core_traits = persona_config.get("core_traits", "")
                
                context = f"{system_prompt}\n\n{core_traits}"
                return context
            else:
                logger.warning("Persona config not found")
                return ""
                
        except Exception as e:
            logger.error(f"Error getting persona context: {e}")
            return ""
    
    def get_relevant_memories(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get relevant memories based on query similarity"""
        try:
            # Create embedding for query
            query_embedding = self.embedding_system.create_embedding(query)
            
            # Search memory with embedding similarity
            memories = self.memory_manager.search_memory_with_embedding(
                query_embedding, 
                limit=limit
            )
            
            return memories
            
        except Exception as e:
            logger.error(f"Error getting relevant memories: {e}")
            return []
    
    def format_chat_context(self, user_message: str) -> str:
        """Format the complete context for DeepSeek API"""
        try:
            # Get persona context
            persona_context = self.get_persona_context()
            
            # Get relevant memories
            relevant_memories = self.get_relevant_memories(user_message, limit=3)
            
            # Format memories
            memory_context = ""
            if relevant_memories:
                memory_context = "\n\nRelevant memories:\n"
                for i, memory in enumerate(relevant_memories, 1):
                    memory_context += f"{i}. {memory.get('content', '')[:200]}...\n"
            
            # Get recent chat history (last 5 exchanges)
            recent_history = self.chat_history[-10:] if self.chat_history else []
            chat_context = ""
            if recent_history:
                chat_context = "\n\nRecent conversation:\n"
                for exchange in recent_history:
                    chat_context += f"User: {exchange.get('user', '')}\n"
                    chat_context += f"Deanna: {exchange.get('assistant', '')}\n"
            
            # Combine all context
            full_context = f"{persona_context}{memory_context}{chat_context}\n\nUser: {user_message}\nDeanna:"
            
            return full_context
            
        except Exception as e:
            logger.error(f"Error formatting chat context: {e}")
            return f"User: {user_message}\nDeanna:"
    
    def call_deepseek_api(self, context: str) -> str:
        """Call DeepSeek API for response generation"""
        try:
            url = f"{self.deepseek_base_url}/chat/completions"
            
            headers = {
                "Authorization": f"Bearer {self.deepseek_token}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "user",
                        "content": context
                    }
                ],
                "max_tokens": 2048,
                "temperature": 0.8,
                "top_p": 0.9
            }
            
            logger.info("Calling DeepSeek API...")
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                assistant_message = result['choices'][0]['message']['content']
                logger.info("DeepSeek API call successful")
                return assistant_message
            else:
                logger.error(f"DeepSeek API error: {response.status_code} - {response.text}")
                return "I'm sorry, I'm having trouble connecting right now. Can you try again?"
                
        except Exception as e:
            logger.error(f"Error calling DeepSeek API: {e}")
            return "I'm experiencing some technical difficulties. Please try again later."
    
    def store_chat_exchange(self, user_message: str, assistant_message: str):
    """store_chat_exchange function."""
        """Store chat exchange in history and database"""
        try:
            # Add to chat history
            exchange = {
                'timestamp': datetime.now().isoformat(),
                'session_id': self.session_id,
                'user': user_message,
                'assistant': assistant_message
            }
            
            self.chat_history.append(exchange)
            
            # Store in database
            self.memory_manager.store_chat_exchange(
                session_id=self.session_id,
                user_message=user_message,
                assistant_message=assistant_message
            )
            
            # Create embeddings for both messages
            user_embedding = self.embedding_system.create_embedding(user_message)
            assistant_embedding = self.embedding_system.create_embedding(assistant_message)
            
            # Store embeddings
            self.memory_manager.store_embedding(user_message, user_embedding)
            self.memory_manager.store_embedding(assistant_message, assistant_embedding)
            
            logger.info("Chat exchange stored successfully")
            
        except Exception as e:
            logger.error(f"Error storing chat exchange: {e}")
    
    def chat(self, user_message: str) -> str:
        """Main chat function"""
        try:
            logger.info(f"Processing user message: {user_message[:50]}...")
            
            # Format context
            context = self.format_chat_context(user_message)
            
            # Get response from DeepSeek
            assistant_message = self.call_deepseek_api(context)
            
            # Store the exchange
            self.store_chat_exchange(user_message, assistant_message)
            
            return assistant_message
            
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return "I'm sorry, something went wrong. Can you try again?"
    
    def get_chat_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get chat history"""
        try:
            return self.chat_history[-limit:] if self.chat_history else []
        except Exception as e:
            logger.error(f"Error getting chat history: {e}")
            return []
    
    def clear_chat_history(self) -> Any:
        """Clear current chat history"""
        try:
            self.chat_history = []
            self.session_id = str(uuid.uuid4())
            logger.info("Chat history cleared")
        except Exception as e:
            logger.error(f"Error clearing chat history: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status information"""
        try:
            status = {
                'persona_name': self.persona_name,
                'nickname': self.nickname,
                'session_id': self.session_id,
                'chat_history_length': len(self.chat_history),
                'memory_stats': self.memory_manager.get_memory_stats(),
                'embedding_info': self.embedding_system.get_model_info(),
                'deepseek_configured': bool(self.deepseek_token)
            }
            return status
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {}

def main() -> None:
    """Main chat interface"""
    logger.info("🎭 Deanna Chat System")
    logger.info("=" * 50)
    logger.info("Type 'quit' to exit, 'status' for system info, 'clear' to clear history")
    logger.info()
    
    # Initialize chat system
    chat_system = DeannaChatSystem()
    
    # Get system status
    status = chat_system.get_system_status()
    logger.info(f"System initialized: {status.get('persona_name', 'Unknown')} ({status.get('nickname', 'Unknown')})")
    logger.info(f"Memory entries: {status.get('memory_stats', {}).get('total_entries', 0)}")
    logger.info(f"Embedding model: {status.get('embedding_info', {}).get('model_name', 'Unknown')}")
    logger.info()
    
    # Chat loop
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() == 'quit':
                logger.info("Goodbye! 👋")
                break
            elif user_input.lower() == 'status':
                status = chat_system.get_system_status()
                logger.info(f"\nSystem Status:")
                logger.info(f"   Session ID: {status.get('session_id', 'Unknown')}")
                logger.info(f"   Chat History: {status.get('chat_history_length', 0)} exchanges")
                logger.info(f"   Memory Entries: {status.get('memory_stats', {}).get('total_entries', 0)}")
                logger.info(f"   Embedding Model: {status.get('embedding_info', {}).get('model_name', 'Unknown')}")
                logger.info(f"   Device: {status.get('embedding_info', {}).get('device', 'Unknown')}")
                logger.info()
                continue
            elif user_input.lower() == 'clear':
                chat_system.clear_chat_history()
                logger.info("Chat history cleared! 🗑️")
                logger.info()
                continue
            elif not user_input:
                continue
            
            # Get response
            response = chat_system.chat(user_input)
            logger.info(f"Deanna: {response}")
            logger.info()
            
        except KeyboardInterrupt:
            logger.info("\nGoodbye! 👋")
            break
        except Exception as e:
            logger.info(f"Error: {e}")
            logger.info("Please try again.")

if __name__ == "__main__":
    main() 