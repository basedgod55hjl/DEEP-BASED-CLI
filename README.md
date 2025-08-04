# 🚀 BASED CODER CLI

> A powerful AI-powered coding assistant with full system access and multi-modal capabilities
> Made by @Lucariolucario55 on Telegram

## ✨ Features

- **🤖 AI-Powered Assistance**: Chat with advanced AI models (DeepSeek, GPT, Claude)
- **💻 Full System Access**: Execute commands and manage your development environment
- **🔧 Code Generation & Analysis**: Generate, debug, and optimize code with AI
- **📚 RAG Pipeline**: Advanced retrieval-augmented generation for context-aware responses
- **🧠 Reasoning Engine**: Step-by-step problem solving with chain-of-thought reasoning
- **💾 Memory System**: Persistent memory for context retention across sessions
- **🌈 Beautiful CLI**: Rainbow interface with rich formatting
- **🔄 Multi-Language Support**: Python and TypeScript implementations

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Node.js 18 or higher (for TypeScript components)
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/based-coder-cli.git
cd based-coder-cli
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install Node.js dependencies (optional, for TypeScript tools):
```bash
npm install
```

4. Set up your API keys:
```bash
python main.py --setup
```

Or create a `.env` file:
```env
DEEPSEEK_API_KEY=your_deepseek_api_key
HUGGINGFACE_API_KEY=your_huggingface_token
OPENAI_API_KEY=your_openai_key  # Optional
ANTHROPIC_API_KEY=your_anthropic_key  # Optional
```

### Running the CLI

Start the interactive mode:
```bash
python main.py
```

Or use command-line arguments:
```bash
python main.py --interactive
```

## 📖 Commands

### System Commands
- `/help` - Show available commands
- `/status` - Display system status
- `/clear` - Clear conversation history
- `/history` - Show conversation history
- `/setup` - Configure API keys

### AI Commands
- `/chat <message>` - Chat with AI assistant
- `/code <prompt>` - Generate code from description
- `/debug <code>` - Debug and fix code issues
- `/analyze <code>` - Analyze code structure and quality
- `/reason <question>` - Use reasoning engine for problem-solving

### Memory Commands
- `/remember <content>` - Store information in memory
- `/recall <query>` - Retrieve information from memory

### Advanced Features
- `/fim <prefix> <suffix>` - Fill-in-Middle completion
- `/prefix <text>` - Prefix-based code completion
- `/rag <query>` - Query using RAG pipeline
- `/web <query>` - Search the web
- `/scrape <url>` - Extract content from websites

## 🏗️ Architecture

```
based-coder-cli/
├── main.py              # Main entry point
├── config.py            # Configuration management
├── requirements.txt     # Python dependencies
├── package.json         # Node.js dependencies
├── tsconfig.json        # TypeScript configuration
├── tools/               # Python tools and agents
│   ├── __init__.py
│   ├── base_tool.py
│   ├── llm_query_tool.py
│   ├── memory_tool.py
│   ├── rag_pipeline_tool.py
│   └── ...
├── src/                 # TypeScript implementation
│   ├── ToolManager.ts
│   ├── cli/
│   ├── tools/
│   └── common/
├── data/                # Data storage
│   ├── unified_agent.db
│   ├── embeddings/
│   └── models/
└── config/              # Configuration files
    ├── api_keys.py
    └── enhanced_config.json
```

## 🔧 Configuration

The CLI can be configured through:

1. **Environment Variables** (`.env` file)
2. **Configuration Files** (`config/enhanced_config.json`)
3. **Command-line Arguments**

### Configuration Options

```json
{
  "llm": {
    "default_model": "deepseek-chat",
    "temperature": 0.7,
    "max_tokens": 4000
  },
  "embedding": {
    "model": "qwen3-embedding",
    "dimension": 1024
  },
  "rag": {
    "chunk_size": 1000,
    "overlap": 200,
    "top_k": 5
  }
}
```

## 🛠️ Development

### Building TypeScript Components

```bash
npm run build
```

### Running Tests

```bash
# Python tests
pytest

# TypeScript tests
npm test
```

### Linting

```bash
# Python
pylint tools/
black tools/

# TypeScript
npm run lint
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Made by @Lucariolucario55 on Telegram
- Built with DeepSeek, OpenAI, and Anthropic APIs
- Inspired by modern AI coding assistants

## 📞 Support

For support, questions, or feature requests:
- Telegram: @Lucariolucario55
- GitHub Issues: [Create an issue](https://github.com/yourusername/based-coder-cli/issues)

---

**Note**: This is an AI-powered tool. Always review generated code and commands before execution. Use responsibly and ensure you understand the implications of granting system access to AI tools.
