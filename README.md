# BASED GOD CODER CLI 🔥

![BASED GOD CODER CLI Banner](https://img.shields.io/badge/BASED%20GOD-CODER%20CLI-brightgreen?style=for-the-badge&logo=terminal&logoColor=white)

**The ultimate AI-powered command-line interface for developers**

*Made by [@Lucariolucario55](https://t.me/Lucariolucario55) on Telegram*

## 🚀 Features

### 🎨 Beautiful Interface
- **Colorful ASCII Art Banner** - Eye-catching terminal display
- **Rich Terminal Formatting** - Colors, tables, panels, and progress bars
- **Interactive Menu System** - Easy navigation through all features

### 🤖 AI-Powered Capabilities
- **DeepSeek API Integration** - Compatible with DeepSeek-V3 and DeepSeek-R1 models
- **Intelligent Fallback Mode** - Works even when API is unavailable
- **Interactive Chat Mode** - Natural language conversation with AI
- **Code Generation** - Generate code from descriptions in any language

### 🛠️ Developer Tools
- **Docker Integration** - Container management and debugging
- **Code Execution** - Safe execution environment for testing
- **File Analysis** - Analyze and process files
- **Batch Processing** - Handle multiple tasks efficiently

### 📊 Advanced Features
- **Usage Statistics** - Track tokens, costs, and performance
- **Conversation Memory** - Maintains context across sessions
- **Function Calling** - Advanced AI function integration
- **JSON Mode** - Structured output for automation

## 🎯 Quick Start

### Prerequisites
- Python 3.8+
- DeepSeek API key (optional - works in fallback mode)

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/BASED-GOD-CODER-CLI.git
cd BASED-GOD-CODER-CLI

# Install dependencies
pip install -r requirements.txt

# Run the CLI
python based_god_unified_cli.py
```

### Environment Setup (Optional)

Create a `.env` file:
```env
DEEPSEEK_API_KEY=your-api-key-here
DEEPSEEK_API_ENDPOINT=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat
```

## 🎮 Usage

### Interactive Mode
```bash
python based_god_unified_cli.py
```

### Command Line Options
```bash
# Quick chat
python based_god_unified_cli.py --chat "Hello, create a Python function"

# Test API connection
python based_god_unified_cli.py --test-api

# Code generation
python based_god_unified_cli.py --code "web scraper"
```

### Menu Navigation

1. **Chat Mode** - Interactive AI conversation
2. **Reasoning Mode** - Complex problem solving
3. **Code Generation** - Generate code with explanations
4. **File Analysis** - Analyze and process files
5. **Batch Processing** - Process multiple prompts
6. **Function Calling** - Advanced AI capabilities
7. **Beta Features** - Experimental features
8. **JSON Mode** - Structured output
9. **Usage Stats** - Performance metrics
10. **Settings** - Configuration options
11. **Docker Tools** - Container management
12. **MCP Tools** - Protocol integration
13. **Help** - Documentation and examples

## 💻 Code Examples

### Python Code Generation
```
You: "Create a web scraper for extracting product prices"
BASED GOD: *Generates complete Python code with requests and BeautifulSoup*
```

## 🚀 FIM & Prefix Completions (NEW!)

### Fill-in-Middle (FIM) Completion
Perfect for completing code between a prefix and suffix:

```bash
# Using the CLI
"FIM complete: <prefix>def calculate_area(radius):<suffix>return area"

# Using the Python API
from tools import FIMCompletionTool

fim_tool = FIMCompletionTool()
result = await fim_tool.execute(
    prefix="def calculate_area(radius):\n    ",
    suffix="\n    return area",
    language="python"
)
```

### Prefix Completion
Continue text or code naturally from a given starting point:

```bash
# Using the CLI
"Prefix complete: The future of AI will"
"Continue from: class DatabaseConnection:"

# Using the Python API
from tools import PrefixCompletionTool

prefix_tool = PrefixCompletionTool()
result = await prefix_tool.execute(
    prefix="class DatabaseConnection:\n    def __init__(self):",
    mode="code"
)
```

### Advanced FIM Examples

#### Complete a function implementation:
```python
# FIM request
prefix = """
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
"""
suffix = """
    return result
"""

# The model will complete the merge logic
```

#### Complete a class method:
```python
# Prefix completion request
prefix = """
class APIClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()
    
    def make_request(self, endpoint, method='GET', data=None):
"""

# The model will complete the method implementation
```

### Node.js Integration

```javascript
const DeepSeekAgent = require('./nodejs_agents/deepseek-chat');

const agent = new DeepSeekAgent();

// FIM completion
const fimResult = await agent.fimComplete(
    'function factorial(n) {\n    if (n <= 1) return 1;\n    ',
    '\n}'
);

// Prefix completion
const prefixResult = await agent.prefixComplete(
    'The benefits of functional programming include'
);
```

### Docker Management
```bash
# List containers
# Execute commands in containers
# Manage Docker system resources
```

### API Integration
```python
from based_god_cli import BasedGodCLI

cli = BasedGodCLI()
response = await cli.chat_with_api("Generate a REST API")
print(response)
```

## 🔧 Configuration

### API Configuration
The CLI supports multiple DeepSeek models:
- `deepseek-chat` - DeepSeek-V3-0324 (general chat)
- `deepseek-reasoner` - DeepSeek-R1-0528 (advanced reasoning)

### Fallback Mode
When the API is unavailable, the CLI automatically switches to fallback mode:
- Local code generation templates
- Offline help and documentation
- Docker tools (when Docker is installed)
- File system operations

## 🐳 Docker Support

The CLI includes comprehensive Docker integration:
- Container listing and management
- Image operations
- System resource monitoring
- Log viewing and debugging
- Interactive container access

## 📈 Performance

- **Fast Startup** - Optimized loading and initialization
- **Async Operations** - Non-blocking API calls
- **Memory Efficient** - Smart conversation history management
- **Error Handling** - Graceful degradation and recovery

## 🛡️ Security

- **API Key Protection** - Secure handling of credentials
- **Safe Code Execution** - Sandboxed environment for testing
- **Input Validation** - Protection against malicious inputs
- **Error Sanitization** - Clean error messages

## 🤝 Contributing

We welcome contributions! Please feel free to submit:
- Bug reports
- Feature requests
- Pull requests
- Documentation improvements

### Development Setup
```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/BASED-GOD-CODER-CLI.git

# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Run the CLI in development mode
python based_god_unified_cli.py --debug
```

## 📋 Requirements

### Core Dependencies
- `httpx>=0.24.0` - HTTP client for API calls
- `rich>=13.0.0` - Rich terminal formatting
- `asyncio` - Asynchronous operations

### Optional Dependencies
- `python-dotenv` - Environment variable loading
- `docker` - Docker integration (requires Docker installed)

## 🐛 Troubleshooting

### Common Issues

**API Connection Failed**
- Check your API key in `.env` file
- Verify internet connection
- Try fallback mode

**Import Errors**
- Install all required dependencies: `pip install -r requirements.txt`
- Check Python version (3.8+ required)

**Docker Commands Not Working**
- Ensure Docker is installed and running
- Check Docker permissions

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **DeepSeek** - For providing the powerful AI models
- **Rich** - For beautiful terminal formatting
- **httpx** - For reliable HTTP client functionality
- **The Open Source Community** - For inspiration and tools

## 📞 Support

- **Telegram**: [@Lucariolucario55](https://t.me/Lucariolucario55)
- **GitHub Issues**: [Report bugs and request features](https://github.com/YOUR_USERNAME/BASED-GOD-CODER-CLI/issues)

## 🔥 Stay Based!

*"Code with confidence, debug with style, and always stay based!"* - BASED GOD CODER CLI

---

**Made with ❤️ by the BASED GOD CODER community**

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square)
![AI](https://img.shields.io/badge/AI-Powered-orange?style=flat-square)