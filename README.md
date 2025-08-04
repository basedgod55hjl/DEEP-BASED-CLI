# 🚀 Enhanced BASED GOD CLI

Enhanced AI-powered development tool with Anthropic Cookbook integration.

## Features

- **Enhanced Tool Integration**: Advanced tool registry with validation and caching
- **JSON Mode Support**: Structured JSON output with schema validation
- **Prompt Caching System**: Multi-strategy caching with compression
- **Sub-Agent Architecture**: Hierarchical task delegation system
- **Advanced RAG Pipeline**: Hybrid search with persona awareness
- **Unified Agent System**: Comprehensive AI assistant capabilities

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the enhanced CLI
python enhanced_based_god_cli.py

# Check system status
python enhanced_based_god_cli.py --status

# Interactive mode
python enhanced_based_god_cli.py --interactive
```

## Architecture

- `enhanced_based_god_cli.py` - Main entry point
- `tools/` - Core tool implementations
- `config/` - Configuration management
- `data/` - Database and storage files

## Enhanced Features

### Tool Integration
- Schema validation for all tools
- Rate limiting and performance monitoring
- Error handling and recovery mechanisms

### JSON Mode Support
- Structured JSON output with validation
- Multiple predefined schemas
- Real-time validation and error recovery

### Prompt Caching
- Multiple eviction strategies (LRU, LFU, TTL, Hybrid)
- Data compression and persistent storage
- Performance monitoring and statistics

### Sub-Agent Architecture
- Hierarchical task delegation
- Specialized agents (Coder, Analyzer, Researcher, etc.)
- Task prioritization and performance tracking

## Configuration

All configuration is managed through `config/enhanced_config.json` with support for:
- Environment-specific configurations
- Feature flags
- Performance tuning
- Security settings

## Development

See `.cursor/rules/` for comprehensive development guidelines and debugging information.

## C++ Website Mapper Example

An example C++ utility is included in `tools/website_mapper.cpp`. It fetches a
webpage and prints all hyperlinks and button labels it finds.

### Build

```bash
g++ tools/website_mapper.cpp -o tools/website_mapper -lcurl
```

### Run

```bash
tools/website_mapper https://example.com
```

### Web UI

A simple web interface is available to run the mapper from your browser.

```bash
# build the C++ mapper if you haven't already
g++ tools/website_mapper.cpp -o tools/website_mapper -lcurl

# start the web server
node tools/website_mapper_server.js
```

Then open [http://localhost:3001](http://localhost:3001) and enter a URL to
see the discovered links and button labels.

## Made by @Lucariolucario55 on Telegram
