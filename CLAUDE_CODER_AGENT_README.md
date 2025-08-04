# 🚀 Claude Coder Agent - Docker Edition

Advanced codebase analysis and scanning system powered by Claude 4 and MCP (Model Context Protocol) tools.

## 🎯 Features

- **🔍 Advanced Codebase Scanning**: Comprehensive analysis of your entire codebase
- **🤖 AI-Powered Analysis**: Uses Claude 4 and DeepSeek AI for intelligent code analysis
- **🔧 MCP Integration**: Leverages Model Context Protocol tools for enhanced scanning
- **📊 Detailed Reports**: Generates comprehensive scan reports with insights
- **🐳 Docker Containerized**: Easy deployment and consistent environment
- **📈 Complexity Scoring**: Advanced code complexity analysis
- **🔍 Issue Detection**: Identifies potential problems and improvement opportunities
- **💡 Smart Suggestions**: AI-generated improvement recommendations

## 🛠️ Prerequisites

- Docker Desktop installed and running
- At least 4GB RAM available for Docker
- Internet connection for API access

## 🚀 Quick Start

### Option 1: Using Docker Compose (Recommended)

```bash
# Run with docker-compose
docker-compose -f docker-compose.claude-coder.yml up --build

# Run with web interface
docker-compose -f docker-compose.claude-coder.yml --profile web up --build
```

### Option 2: Using Shell Scripts

**Linux/Mac:**
```bash
chmod +x run_claude_coder.sh
./run_claude_coder.sh
```

**Windows:**
```cmd
run_claude_coder.bat
```

### Option 3: Manual Docker Commands

```bash
# Build the image
docker build -f Dockerfile.claude_coder -t claude-coder-agent .

# Run the container
docker run --rm \
    -v "$(pwd):/app/codebase:ro" \
    -v "$(pwd)/scans:/app/scans" \
    -v "$(pwd)/logs:/app/logs" \
    -v "$(pwd)/data:/app/data" \
    -e CLAUDE_API_KEY="your-claude-api-key" \
    -e DEEPSEEK_API_KEY="your-deepseek-api-key" \
    claude-coder-agent
```

## 📁 Output Structure

After running the scan, you'll find:

```
project/
├── scans/
│   └── codebase_scan_YYYYMMDD_HHMMSS.json  # Detailed scan report
├── logs/
│   └── claude_coder_agent_YYYYMMDD_HHMMSS.log  # Execution logs
└── data/
    └── ...  # Database and other data files
```

## 📊 Scan Report Format

The scan report includes:

```json
{
  "scan_timestamp": "2024-01-01T12:00:00",
  "codebase_path": "/app/codebase",
  "system_status": {
    "docker_available": true,
    "mcp_available": true,
    "claude_api_working": true,
    "deepseek_api_working": true
  },
  "analysis_results": [
    {
      "file_path": "path/to/file.py",
      "complexity_score": 45.2,
      "issues": ["Contains TODO comments", "Too many print statements"],
      "suggestions": ["Add type hints", "Add docstrings"],
      "dependencies": ["requests", "numpy"],
      "estimated_rewrite_time": 90,
      "mcp_insights": {
        "file_size": 1024,
        "last_modified": "2024-01-01T10:00:00"
      }
    }
  ]
}
```

## 🔧 Configuration

### Environment Variables

- `CLAUDE_API_KEY`: Your Claude API key
- `DEEPSEEK_API_KEY`: Your DeepSeek API key
- `PYTHONPATH`: Python path (set automatically)

### Volume Mounts

- `./:/app/codebase:ro`: Your codebase (read-only)
- `./scans:/app/scans`: Scan output directory
- `./logs:/app/logs`: Log files directory
- `./data:/app/data`: Data and database files

## 🌐 Web Interface

To view scan results via web interface:

```bash
# Start with web interface
docker-compose -f docker-compose.claude-coder.yml --profile web up --build

# Access at: http://localhost:8080/scans/
```

## 🔍 Analysis Features

### Code Complexity Scoring
- Calculates complexity based on control structures
- Considers loops, conditionals, functions, and classes
- Provides normalized scores (0-100)

### Issue Detection
- TODO/FIXME comments
- Excessive print statements
- Bare except clauses
- Wildcard imports
- Long files (>500 lines)

### Smart Suggestions
- Type hints for functions
- Docstring recommendations
- Error handling improvements
- Async/await usage

### MCP Integration
- Filesystem analysis
- Docker container insights
- Enhanced metadata extraction
- Cross-file dependency analysis

## 🐛 Troubleshooting

### Common Issues

1. **Docker not running**
   ```
   ❌ Docker is not running. Please start Docker and try again.
   ```
   **Solution**: Start Docker Desktop

2. **API key errors**
   ```
   ❌ Claude API test failed
   ```
   **Solution**: Check your API keys in environment variables

3. **Permission errors**
   ```
   ❌ Permission denied
   ```
   **Solution**: Ensure Docker has access to your project directory

4. **Memory issues**
   ```
   ❌ Out of memory
   ```
   **Solution**: Increase Docker memory limit to 4GB+

### Logs

Check the logs directory for detailed error information:
```bash
tail -f logs/claude_coder_agent_*.log
```

## 🔄 Advanced Usage

### Custom Scan Path

To scan a specific directory:

```bash
docker run --rm \
    -v "/path/to/your/code:/app/codebase:ro" \
    -v "$(pwd)/scans:/app/scans" \
    claude-coder-agent
```

### Multiple Scans

Run multiple scans with different configurations:

```bash
# First scan
docker run --rm -v "$(pwd):/app/codebase:ro" -v "$(pwd)/scans:/app/scans" claude-coder-agent

# Second scan (different output)
docker run --rm -v "$(pwd):/app/codebase:ro" -v "$(pwd)/scans2:/app/scans" claude-coder-agent
```

### Integration with CI/CD

Add to your CI/CD pipeline:

```yaml
# GitHub Actions example
- name: Run Claude Coder Agent
  run: |
    docker build -f Dockerfile.claude_coder -t claude-coder-agent .
    docker run --rm \
      -v "${{ github.workspace }}:/app/codebase:ro" \
      -v "${{ github.workspace }}/scans:/app/scans" \
      -e CLAUDE_API_KEY="${{ secrets.CLAUDE_API_KEY }}" \
      -e DEEPSEEK_API_KEY="${{ secrets.DEEPSEEK_API_KEY }}" \
      claude-coder-agent
```

## 📈 Performance

- **Scan Speed**: ~1000 files/minute
- **Memory Usage**: ~2GB RAM
- **Disk Space**: ~500MB for container + scan results
- **Network**: Requires internet for API calls

## 🔒 Security

- Codebase is mounted read-only
- API keys are passed via environment variables
- No persistent data collection
- All analysis happens locally in container

## 🤝 Contributing

To contribute to the Claude Coder Agent:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with Docker
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

- Check the logs in `./logs/` directory
- Review the scan reports in `./scans/` directory
- Ensure Docker is running and has sufficient resources
- Verify your API keys are valid and have sufficient credits

---

**Made with ❤️ by @Lucariolucario55 on Telegram** 