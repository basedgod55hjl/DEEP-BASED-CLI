# DeepSeek CLI

[![npm version](https://img.shields.io/npm/v/@deepseek/cli.svg)](https://www.npmjs.com/package/@deepseek/cli)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful command-line interface for interacting with DeepSeek AI models, featuring codebase analysis, interactive chat, and code generation capabilities.

## Features

- 🤖 **Interactive Chat** - Engage in conversations with DeepSeek models
- 📂 **Codebase Analysis** - Analyze and ask questions about your codebase
- ⚡ **Quick Queries** - Get instant answers without entering chat mode
- 🎨 **Markdown Support** - Beautiful terminal output with syntax highlighting
- 🔧 **Configurable** - Customize model settings and API endpoints
- 🚀 **Stream Support** - Real-time streaming responses

## Installation

### With npm

```bash
npm install -g @deepseek/cli
```

### From source

```bash
git clone https://github.com/deepseek-ai/deepseek-cli.git
cd deepseek-cli
npm install
npm run build
npm link
```

## Quick Start

1. **Configure your API key:**

```bash
deepseek config
```

Or set it via environment variable:

```bash
export DEEPSEEK_API_KEY="your-api-key-here"
```

2. **Start chatting:**

```bash
deepseek chat
```

3. **Quick query:**

```bash
deepseek "What is the capital of France?"
```

## Usage

### Interactive Chat

Start an interactive chat session:

```bash
deepseek chat

# With a custom system prompt
deepseek chat --system "You are a helpful coding assistant"

# Use a specific model
deepseek chat --model deepseek-coder
```

### Codebase Analysis

Analyze your codebase and ask questions:

```bash
# Analyze current directory
deepseek analyze "What does this project do?"

# Analyze specific directory
deepseek analyze "Find all API endpoints" --path /path/to/project

# Generate codebase summary
deepseek analyze --summary
```

### Quick Queries

Get quick answers without entering chat mode:

```bash
# Simple query
deepseek "Explain async/await in JavaScript"

# Query with codebase context
deepseek "How does the authentication work?" --codebase
```

### Configuration

Configure DeepSeek CLI settings:

```bash
# Interactive configuration
deepseek config

# Set specific values
deepseek config --key apiKey --value "your-api-key"
deepseek config --key model --value "deepseek-coder"

# View current configuration
deepseek config --list
```

## Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `apiKey` | Your DeepSeek API key | - |
| `apiEndpoint` | API endpoint URL | `https://api.deepseek.com/v1` |
| `model` | Default model to use | `deepseek-coder` |
| `maxTokens` | Maximum tokens in response | `4096` |
| `temperature` | Response randomness (0-2) | `0.7` |

## Environment Variables

You can also configure the CLI using environment variables:

- `DEEPSEEK_API_KEY` - Your API key
- `DEEPSEEK_API_ENDPOINT` - Custom API endpoint
- `DEEPSEEK_MODEL` - Default model
- `DEEPSEEK_MAX_TOKENS` - Maximum tokens
- `DEEPSEEK_TEMPERATURE` - Temperature setting

## Examples

### Explore a new codebase

```bash
cd /path/to/project
deepseek analyze "Give me an overview of this project's architecture"
deepseek analyze "What are the main components and how do they interact?"
```

### Generate code

```bash
deepseek "Write a Python function to calculate fibonacci numbers"
deepseek "Create a React component for a todo list" --model deepseek-coder
```

### Debug issues

```bash
deepseek analyze "Why might this function be causing memory leaks?" --path src/utils/
deepseek "How can I optimize this SQL query for better performance?"
```

### Learn and explore

```bash
deepseek "Explain the difference between TCP and UDP"
deepseek "What are the best practices for REST API design?"
```

## Advanced Usage

### Custom System Prompts

You can set custom system prompts for specialized behavior:

```bash
deepseek chat --system "You are an expert in React and TypeScript. Provide detailed explanations with code examples."
```

### Model Selection

DeepSeek CLI supports multiple models:

- `deepseek-coder` - Optimized for code generation and analysis
- `deepseek-chat` - General purpose conversational model

```bash
deepseek --model deepseek-chat "Explain quantum computing"
```

## Troubleshooting

### API Key Issues

If you encounter authentication errors:

1. Ensure your API key is correctly set:
   ```bash
   deepseek config --list
   ```

2. Try setting it via environment variable:
   ```bash
   export DEEPSEEK_API_KEY="your-api-key"
   ```

### Connection Issues

If you experience connection problems:

1. Check your internet connection
2. Verify the API endpoint:
   ```bash
   deepseek config --key apiEndpoint --value "https://api.deepseek.com/v1"
   ```

### Rate Limiting

If you hit rate limits, try:
- Reducing request frequency
- Using a paid plan for higher limits
- Implementing exponential backoff in scripts

## Contributing

Contributions are welcome! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

MIT © DeepSeek Team

## Support

- 📧 Email: support@deepseek.ai
- 🐛 Issues: [GitHub Issues](https://github.com/deepseek-ai/deepseek-cli/issues)
- 💬 Discord: [Join our community](https://discord.gg/deepseek)
