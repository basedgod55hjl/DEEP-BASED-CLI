# DeepCLI - Powerful AI-Powered CLI for DeepSeek Models

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

DeepCLI is a comprehensive command-line interface for interacting with DeepSeek AI models. It features an intuitive interactive mode, powerful slash commands, persistent memory, and extensible architecture.

## 🚀 Features

- **🤖 Dual Model Support**: Access both DeepSeek Chat and Reasoner models
- **💬 Interactive Mode**: Beautiful terminal UI with command completion
- **⚡ Slash Commands**: Quick access to specialized AI personas and tasks
- **🧠 Persistent Memory**: SQLite-based memory system for context retention
- **📊 Usage Tracking**: Real-time token usage and cost estimation
- **🔧 Extensible**: Plugin system for custom commands and tools
- **🎨 Rich UI**: Colorful output with tables, panels, and progress indicators
- **🔒 Secure**: API key management and configuration safety

## 📦 Installation

### From PyPI (Recommended)

```bash
pip install deepseek-cli
```

### From Source

```bash
git clone https://github.com/yourusername/deep-cli.git
cd deep-cli
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/yourusername/deep-cli.git
cd deep-cli
pip install -e ".[dev]"
```

## 🔧 Configuration

Set your DeepSeek API key:

```bash
export DEEPSEEK_API_KEY="your-api-key-here"
```

Or create a `.env` file:

```env
DEEPSEEK_API_KEY=your-api-key-here
```

## 🎯 Quick Start

### Interactive Mode

Simply run `deepcli` to enter interactive mode:

```bash
deepcli
```

### Command Line Mode

Send a single message:

```bash
deepcli chat "Explain quantum computing"
```

Use the reasoning model:

```bash
deepcli reason "Solve this math problem: ∫x²dx" --show-reasoning
```

### Memory Operations

Store and recall information:

```bash
# Store information
deepcli memory store "project_name" "DeepCLI Development"

# Recall information
deepcli memory recall "project_name"

# Search memories
deepcli memory search "project"

# View statistics
deepcli memory stats
```

## 💫 Slash Commands

DeepCLI supports powerful slash commands in interactive mode:

### Implementation Command

```
/deep:implement user authentication system
/impl frontend navbar component --persona frontend
```

### Analysis Command

```
/deep:analyze security
/deep:analyze performance
```

### Other Commands

- `/deep:design` - System design and architecture
- `/deep:test` - Generate tests
- `/deep:document` - Create documentation
- `/deep:review` - Code review
- `/deep:debug` - Debug issues
- `/deep:refactor` - Refactor code

## 🎭 AI Personas

DeepCLI includes specialized AI personas for different tasks:

- **🏗️ Architect**: System design and architecture
- **🎨 Frontend**: UI/UX and frontend development
- **⚙️ Backend**: APIs and backend systems
- **🔒 Security**: Security analysis and best practices
- **🔍 Analyst**: Code analysis and debugging
- **📝 Scribe**: Documentation and writing
- **🚀 DevOps**: Infrastructure and deployment

## 🧠 Memory System

DeepCLI includes a powerful SQLite-based memory system:

- **Persistent Storage**: Memories persist across sessions
- **Namespaces**: Organize memories by context
- **Search**: Full-text search across memories
- **Export/Import**: Backup and restore memories

## 📊 Usage Examples

### Complex Task with Reasoning

```bash
deepcli reason "Design a distributed cache system" --show-reasoning
```

### Batch Processing

```python
# Create a script using DeepCLI as a library
from deepcli import DeepSeekClient, DeepSeekModel

async def main():
    client = DeepSeekClient()
    
    # Process multiple prompts
    prompts = ["Task 1", "Task 2", "Task 3"]
    for prompt in prompts:
        response = await client.chat(prompt)
        print(response)
```

### Stream Responses

```bash
deepcli chat "Write a story about AI" --stream
```

## 🛠️ Advanced Configuration

Create a configuration file at `~/.deepcli/config.toml`:

```toml
# API Configuration
api_key = "your-api-key"
default_model = "chat"
temperature = 0.7
max_tokens = 4096

# Memory Configuration
memory_enabled = true
memory_db_path = "~/.deepcli/memory.db"

# UI Configuration
use_rich = true
color_theme = "monokai"

# GitHub Integration
github_token = "your-github-token"
github_repo = "username/repo"
```

## 🔌 Extending DeepCLI

### Creating Custom Commands

```python
from deepcli.commands.base import Command

class MyCommand(Command):
    @property
    def name(self):
        return "my:command"
    
    @property
    def description(self):
        return "My custom command"
    
    async def execute(self, context):
        # Your command logic here
        return "Command executed!"
```

### Adding MCP Servers

Configure MCP servers in `~/.deepcli/mcp_servers.json`:

```json
{
  "web-search": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-websearch"],
    "env": {
      "GOOGLE_API_KEY": "${GOOGLE_API_KEY}"
    }
  }
}
```

## 🐛 Troubleshooting

### API Key Issues

If you get API key errors:

1. Ensure your API key is set correctly
2. Check if the key has proper permissions
3. Verify you have credits available

### Memory Database Issues

If memory operations fail:

1. Check write permissions for `~/.deepcli/`
2. Ensure SQLite is installed
3. Try deleting and recreating the database

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/deep-cli.git
cd deep-cli

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check .
black --check .
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- DeepSeek for providing powerful AI models
- The open-source community for inspiration and tools
- Contributors who help improve DeepCLI

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/deep-cli/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/deep-cli/discussions)
- **Email**: support@deepcli.com

---

Made with ❤️ by the DeepCLI Team