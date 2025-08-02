#!/usr/bin/env python3
"""
Interactive Chatbot Application using DeepSeek API

This example shows how to build a full-featured chatbot with:
- Conversation history management
- Context-aware responses
- Different conversation modes
- File handling
- Web search simulation
"""

import sys
import json
from datetime import datetime
from typing import List, Dict, Optional
import readline  # For better input handling

# Add parent directory to path to import deepseek_integration
sys.path.append('..')
from deepseek_integration import DeepSeekClient, DeepSeekModel, ResponseFormat


class ChatBot:
    """Interactive chatbot with conversation management"""
    
    def __init__(self):
        self.client = DeepSeekClient()
        self.conversation_history: List[Dict[str, str]] = []
        self.system_prompt = "You are a helpful AI assistant. Be concise but thorough in your responses."
        self.mode = "chat"  # chat, reason, code
        self.context_window = 10  # Keep last N messages for context
        
    def add_message(self, role: str, content: str):
        """Add a message to conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
    def get_context_messages(self) -> List[Dict[str, str]]:
        """Get recent messages for context"""
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Get last N messages
        recent = self.conversation_history[-self.context_window:]
        for msg in recent:
            messages.append({"role": msg["role"], "content": msg["content"]})
            
        return messages
    
    def handle_special_commands(self, user_input: str) -> Optional[str]:
        """Handle special commands"""
        if user_input.startswith("/"):
            command = user_input[1:].lower().split()
            
            if command[0] == "help":
                return self.show_help()
            elif command[0] == "mode":
                if len(command) > 1:
                    return self.set_mode(command[1])
                return f"Current mode: {self.mode}"
            elif command[0] == "clear":
                self.conversation_history.clear()
                return "Conversation history cleared."
            elif command[0] == "save":
                return self.save_conversation()
            elif command[0] == "system":
                if len(command) > 1:
                    self.system_prompt = " ".join(command[1:])
                    return f"System prompt updated."
                return f"Current system prompt: {self.system_prompt}"
            elif command[0] == "stats":
                return self.show_stats()
            elif command[0] == "export":
                return self.export_last_response()
                
        return None
    
    def show_help(self) -> str:
        """Show available commands"""
        return """
Available commands:
/help          - Show this help message
/mode [chat|reason|code] - Switch conversation mode
/clear         - Clear conversation history
/save          - Save conversation to file
/system [prompt] - Set or show system prompt
/stats         - Show usage statistics
/export        - Export last response to file
/quit or /exit - Exit the chatbot

Special features in chat:
- Ask me to analyze code
- Request JSON formatted responses
- Ask for step-by-step reasoning
- Request summaries or translations
        """
    
    def set_mode(self, mode: str) -> str:
        """Set conversation mode"""
        valid_modes = ["chat", "reason", "code"]
        if mode in valid_modes:
            self.mode = mode
            if mode == "code":
                self.system_prompt = "You are an expert programmer. Provide clear, well-commented code with explanations."
            elif mode == "reason":
                self.system_prompt = "You are a logical problem solver. Break down problems step by step."
            else:
                self.system_prompt = "You are a helpful AI assistant. Be concise but thorough in your responses."
            return f"Mode switched to: {mode}"
        return f"Invalid mode. Choose from: {', '.join(valid_modes)}"
    
    def save_conversation(self) -> str:
        """Save conversation history to file"""
        filename = f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(self.conversation_history, f, indent=2)
        return f"Conversation saved to {filename}"
    
    def show_stats(self) -> str:
        """Show usage statistics"""
        stats = self.client.get_usage_summary()
        return f"""
Usage Statistics:
- Total tokens: {stats['usage']['total_tokens']:,}
- Prompt tokens: {stats['usage']['prompt_tokens']:,}
- Completion tokens: {stats['usage']['completion_tokens']:,}
- Cache hit rate: {stats['efficiency']['cache_hit_rate']}%
- Estimated cost: ${stats['costs']['total_cost']:.4f}
- Cache savings: ${stats['costs']['cache_savings']:.4f}
        """
    
    def export_last_response(self) -> str:
        """Export last assistant response to file"""
        for msg in reversed(self.conversation_history):
            if msg["role"] == "assistant":
                filename = f"response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                with open(filename, 'w') as f:
                    f.write(msg["content"])
                return f"Last response exported to {filename}"
        return "No assistant response found to export."
    
    def detect_special_request(self, user_input: str) -> Dict[str, any]:
        """Detect special types of requests"""
        lower_input = user_input.lower()
        
        # Check for JSON request
        if "json" in lower_input and ("format" in lower_input or "response" in lower_input):
            return {"type": "json", "format": ResponseFormat.JSON}
            
        # Check for code request
        if any(word in lower_input for word in ["write code", "implement", "function", "class", "program"]):
            return {"type": "code", "language": "python"}
            
        # Check for reasoning request
        if any(word in lower_input for word in ["explain", "why", "how does", "reason", "step by step"]):
            return {"type": "reasoning"}
            
        return {"type": "normal"}
    
    def process_input(self, user_input: str) -> str:
        """Process user input and generate response"""
        # Add user message to history
        self.add_message("user", user_input)
        
        # Detect special request type
        request_type = self.detect_special_request(user_input)
        
        try:
            if self.mode == "reason" or request_type["type"] == "reasoning":
                # Use reasoning model
                result = self.client.reason(
                    user_input,
                    reasoning_effort="high" if "complex" in user_input.lower() else "medium"
                )
                response = result["answer"]
                if "reasoning" in result and result["reasoning"]:
                    response = f"Reasoning:\n{result['reasoning']}\n\nAnswer:\n{response}"
                    
            elif request_type["type"] == "json":
                # Generate JSON response
                messages = self.get_context_messages()
                response = self.client.chat(
                    messages,
                    response_format=ResponseFormat.JSON,
                    temperature=0.3
                )
                response = json.dumps(response, indent=2)
                
            elif request_type["type"] == "code" or self.mode == "code":
                # Generate code with lower temperature
                messages = self.get_context_messages()
                response = self.client.chat(
                    messages,
                    model=DeepSeekModel.CHAT,
                    temperature=0.2,
                    system_prompt="You are an expert programmer. Always include comments and explanations."
                )
                
            else:
                # Normal chat
                messages = self.get_context_messages()
                response = self.client.chat(
                    messages,
                    model=DeepSeekModel.CHAT,
                    temperature=0.7
                )
            
            # Add assistant response to history
            self.add_message("assistant", response)
            return response
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.add_message("assistant", error_msg)
            return error_msg
    
    def run(self):
        """Main chat loop"""
        print("🤖 DeepSeek Chatbot Started!")
        print("Type /help for available commands or /quit to exit.\n")
        
        while True:
            try:
                # Get user input
                user_input = input(f"[{self.mode}]> ").strip()
                
                # Check for exit
                if user_input.lower() in ["/quit", "/exit", "quit", "exit"]:
                    print("\n👋 Goodbye! Thanks for chatting!")
                    print(self.show_stats())
                    break
                
                # Skip empty input
                if not user_input:
                    continue
                
                # Handle special commands
                command_response = self.handle_special_commands(user_input)
                if command_response:
                    print(f"\n{command_response}\n")
                    continue
                
                # Process regular input
                print("\n💭 Thinking...", end='', flush=True)
                response = self.process_input(user_input)
                print("\r" + " " * 20 + "\r", end='')  # Clear "Thinking..."
                
                # Display response
                print(f"\n🤖: {response}\n")
                
            except KeyboardInterrupt:
                print("\n\nUse /quit to exit properly.")
                continue
            except Exception as e:
                print(f"\n❌ Error: {str(e)}\n")


def main():
    """Run the chatbot"""
    chatbot = ChatBot()
    
    # Optional: Load previous conversation
    # chatbot.load_conversation("previous_chat.json")
    
    chatbot.run()


if __name__ == "__main__":
    main()