# DeepSeek CLI

A beautiful, feature-rich command-line interface for DeepSeek's AI models, combining the power of both `deepseek-chat` and `deepseek-reasoner` models with an intuitive terminal experience.

![DeepSeek CLI Demo](https://img.shields.io/badge/DeepSeek-CLI-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

### 🎨 Beautiful Interface
- **Rich Terminal UI**: Colorful menus, tables, and panels using the `rich` library
- **Interactive Prompts**: User-friendly input with validation and auto-completion
- **Progress Indicators**: Visual feedback for long-running operations
- **Syntax Highlighting**: Beautiful code display with line numbers

### 🤖 Dual Model Support
- **DeepSeek-Chat**: For general conversations, creative tasks, and code generation
- **DeepSeek-Reasoner**: For complex problem-solving with step-by-step reasoning

### 🚀 Core Features
1. **Chat Mode**: Interactive conversations with context awareness
2. **Reasoning Mode**: Complex problem solving with detailed reasoning steps
3. **Code Generation**: Generate code in multiple languages with best practices
4. **File Analysis**: Analyze, summarize, and improve files
5. **Batch Processing**: Process multiple prompts concurrently
6. **Function Calling**: Demonstrate AI tool usage capabilities
7. **Usage Statistics**: Track token usage and costs
8. **Settings Management**: Customize model, temperature, and more

### 🔄 Advanced Features
- **Streaming Responses**: Real-time output for better user experience
- **Context Caching**: Automatic caching for up to 74% cost savings
- **Export Options**: Save conversations and results in multiple formats
- **Command-line Arguments**: Quick access to features without menu navigation
- **Error Handling**: Graceful handling with retry logic for rate limits

## 📋 Prerequisites

- Python 3.8 or higher
- DeepSeek API key ([Get one here](https://platform.deepseek.com/api_keys))

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository (or download the files)
git clone <repository-url>
cd deepseek-cli

# Run the setup script
chmod +x setup_deepseek_cli.sh
./setup_deepseek_cli.sh
```

The setup script will:
- Check Python version
- Create a virtual environment
- Install dependencies
- Create a `.env` file for your API key
- Set up convenient run scripts

### 2. Add Your API Key

Edit the `.env` file and add your DeepSeek API key:

```env
DEEPSEEK_API_KEY=your-actual-api-key-here
```

### 3. Run the CLI

```bash
# Interactive mode
./run_deepseek_cli.sh

# Or use the system-wide command (if you set it up)
deepseek
```

## 🎯 Usage Examples

### Interactive Mode

Simply run the CLI to access the beautiful menu interface:

```bash
./run_deepseek_cli.sh
```

You'll see a menu like this:

```
╔══════════════════════════════════════╗
║       DeepSeek CLI                   ║
║  AI-powered command-line assistant   ║
╚══════════════════════════════════════╝

┌─────────────────── Main Menu ───────────────────┐
│ Option │ Feature          │ Description         │
├────────┼──────────────────┼─────────────────────┤
│ 1      │ Chat Mode        │ Interactive chat    │
│ 2      │ Reasoning Mode   │ Problem solving     │
│ 3      │ Code Generation  │ Generate code       │
│ 4      │ File Analysis    │ Analyze files       │
│ 5      │ Batch Processing │ Multiple prompts    │
│ 6      │ Function Calling │ Tool demonstrations │
│ 7      │ Usage Stats      │ Token usage         │
│ 8      │ Settings         │ Configure CLI       │
│ 9      │ Help             │ Show help           │
│ 0      │ Exit             │ Exit application    │
└──────────────────────────────────────────────────┘
```

### Command-Line Mode

Quick access to features without entering interactive mode:

```bash
# Quick chat
./run_deepseek_cli.sh --chat "What is the meaning of life?"

# Reasoning mode
./run_deepseek_cli.sh --reason "If a train travels 120 km in 2 hours, what is its speed?"

# Code generation
./run_deepseek_cli.sh --code "binary search algorithm"

# With specific model
./run_deepseek_cli.sh --model reasoner --reason "Solve x^2 + 5x + 6 = 0"

# Adjust temperature
./run_deepseek_cli.sh --chat "Write a poem" --temperature 1.2

# Disable streaming
./run_deepseek_cli.sh --chat "Explain quantum computing" --no-stream
```

## 🛠️ Feature Details

### Chat Mode
- Maintains conversation history
- Context-aware responses
- Commands: `clear` (clear history), `exit` (return to menu)
- Streaming responses for natural conversation flow

### Reasoning Mode
- Three effort levels: low, medium, high
- Shows step-by-step reasoning process
- Ideal for math problems, logic puzzles, and complex analysis

### Code Generation
- Support for 20+ programming languages
- Includes comments, error handling, and best practices
- Syntax highlighting in terminal
- Option to save generated code to file

### File Analysis
- Summarize documents
- Analyze code files
- Suggest improvements
- Explain functionality
- Custom analysis requests

### Batch Processing
- Process multiple prompts concurrently
- Progress tracking
- Export results to JSON
- Configurable concurrency

### Function Calling Demo
- Demonstrates AI's ability to use tools
- Sample functions: weather, web search, calculations
- Shows how AI determines which function to call

### Settings
- Switch between models
- Adjust temperature (0.0-2.0)
- Set max tokens
- Toggle streaming
- Configure history saving
- Set export format

## 📊 Usage Statistics

The CLI tracks:
- Token usage (prompt, completion, total)
- Cache hits and misses
- Reasoning tokens (for reasoner model)
- Cost estimates
- Cache savings
- Efficiency metrics

## 🎨 Customization

### Environment Variables

Create a `.env` file with:

```env
# Required
DEEPSEEK_API_KEY=your-api-key

# Optional
DEEPSEEK_API_ENDPOINT=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_MAX_TOKENS=4096
DEEPSEEK_TEMPERATURE=0.7
```

### Settings in CLI

Access Settings (option 8) to configure:
- Default model
- Temperature
- Max tokens
- Streaming behavior
- Export formats

## 🐛 Troubleshooting

### API Key Issues
- Ensure your API key is correctly set in `.env`
- Check that the file has no extra spaces or quotes
- Verify your API key at [platform.deepseek.com](https://platform.deepseek.com)

### Installation Issues
- Ensure Python 3.8+ is installed: `python3 --version`
- Try manual installation:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  python deepseek_cli.py
  ```

### Rich Library Fallback
- If colors don't display properly, the CLI will automatically fall back to plain text
- To force plain text mode, uninstall rich: `pip uninstall rich`

### Rate Limits
- The CLI automatically retries with exponential backoff
- Reduce `max_concurrent` in batch processing if hitting limits

## 📁 Project Structure

```
deepseek-cli/
├── deepseek_integration.py    # Core DeepSeek API wrapper
├── deepseek_cli.py           # Main CLI application
├── requirements.txt          # Python dependencies
├── setup_deepseek_cli.sh     # Setup script
├── run_deepseek_cli.sh       # Run script (created by setup)
├── .env                      # API configuration (create this)
└── examples/                 # Example applications
    ├── chatbot_app.py
    ├── web_api.py
    └── simple_usage.py
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built on top of the DeepSeek API
- Uses the fantastic `rich` library for the beautiful terminal UI
- Inspired by modern CLI applications like Gemini CLI

## 📞 Support

- For API issues: Visit [DeepSeek Platform](https://platform.deepseek.com)
- For CLI issues: Open an issue in this repository
- For feature requests: Feel free to suggest improvements!

---

**Enjoy using DeepSeek CLI! 🚀**