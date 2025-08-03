# 🚀 SuperAgentScraper - Advanced AI-Powered Web Scraper

**Production-ready, multi-modal web scraper with DeepSeek AI integration for intelligent data extraction and analysis.**

## 🌟 Features

### Core Capabilities
- **🤖 AI-Powered Intelligence**: DeepSeek Reasoner, Chat, FIM, and Prefix Completion
- **🖼️ Multi-Modal Processing**: Images (OCR), PDFs, Videos, Audio, Documents
- **🧠 Vector Memory**: Qdrant-powered semantic search and RAG
- **🕷️ Stealth Scraping**: Anti-detection, fingerprint rotation, proxy support
- **⚡ Concurrent Processing**: Multi-threaded scraping with agent pools
- **🔍 Smart Analysis**: Cross-media intelligence with pattern recognition
- **📊 Rich Reporting**: HTML, JSON, Markdown export formats

### Advanced Features
- **Dynamic Tool Loading**: Drop custom handlers in `./tools/`
- **Watchdog Systems**: Block detection, rate limiting, anomaly monitoring
- **Session Management**: Persistent memory across scraping sessions
- **Browser Automation**: Selenium with stealth mode for JS-heavy sites
- **Media Extraction**: Automatic download and processing of all media types
- **Conversation History**: Multi-turn analysis with context retention

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Chrome/Chromium browser
- Tesseract OCR (`apt-get install tesseract-ocr` or `brew install tesseract`)
- FFmpeg (for video processing)

### Setup
```bash
# Clone the repository
git clone <your-repo>
cd DEEP-CLI

# Install dependencies
pip install -r requirements_enhanced.txt

# Install system dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y tesseract-ocr chromium-driver ffmpeg

# Install system dependencies (macOS)
brew install tesseract chromium-driver ffmpeg
```

## 🔧 Configuration

The scraper uses a hardcoded DeepSeek API key by default. To use your own:

```python
# In your code
scraper = SuperAgentScraper(api_key="your-api-key-here")

# Or via CLI
python tools/super_agent_scraper.py scrape --api_key "your-key" --urls https://example.com
```

## 📖 Usage

### CLI Commands

#### 1. Scrape Websites
```bash
# Basic scraping
python tools/super_agent_scraper.py scrape --urls https://example.com

# Multiple URLs with analysis
python tools/super_agent_scraper.py scrape \
    --urls https://example.com https://sample.org \
    --analysis_query "Extract all technical specifications and pricing"

# With custom workers
python tools/super_agent_scraper.py scrape \
    --urls https://target.com \
    --workers 10 \
    --format html \
    --output report
```

#### 2. Query Memory
```bash
# Search vector memory
python tools/super_agent_scraper.py memory --query "security protocols"

# Find related content
python tools/super_agent_scraper.py memory --query "user authentication methods"
```

#### 3. Analyze Data
```bash
# Analyze previously scraped data
python tools/super_agent_scraper.py analyze \
    --data_file scraped_data.json \
    --query "What are the main security vulnerabilities?"
```

#### 4. Export Results
```bash
# Export in different formats
python tools/super_agent_scraper.py export \
    --data_file results.json \
    --format html \
    --output security_report

# Markdown export
python tools/super_agent_scraper.py export \
    --data_file results.json \
    --format markdown \
    --output analysis
```

#### 5. FIM Completion
```bash
# Fill-in-the-middle completion
python tools/super_agent_scraper.py fim \
    --prefix "def scrape_website(url):" \
    --suffix "return scraped_data"
```

### Python API

```python
from tools.super_agent_scraper import SuperAgentScraper

# Initialize scraper
scraper = SuperAgentScraper(
    storage_path="my_scraped_data",
    max_workers=5
)

# Single URL scraping
result = scraper.adaptive_scrape("https://example.com")

# Multi-URL campaign with analysis
results = scraper.streaming_scrape(
    urls=["https://site1.com", "https://site2.com"],
    analysis_query="Extract product information and prices"
)

# Query memory
memories = scraper.query_memory("previous findings about security")

# RAG-enhanced analysis
analysis = scraper.rag_enhanced_analysis(
    query="Compare security features",
    scraped_data=results['results']['https://site1.com']
)

# Export results
scraper.export_results(results, format="html", output_path="report")

# Clean up
scraper.close()
```

## 🎯 Use Cases

### 1. Security Research
```bash
python tools/super_agent_scraper.py scrape \
    --urls https://nvd.nist.gov https://cve.mitre.org \
    --analysis_query "Extract latest critical vulnerabilities"
```

### 2. Market Intelligence
```bash
python tools/super_agent_scraper.py scrape \
    --urls https://competitor1.com https://competitor2.com \
    --analysis_query "Compare pricing strategies and product features"
```

### 3. Content Aggregation
```bash
python tools/super_agent_scraper.py scrape \
    --urls https://news1.com https://news2.com https://news3.com \
    --analysis_query "Summarize main stories about AI developments"
```

### 4. Documentation Extraction
```bash
python tools/super_agent_scraper.py scrape \
    --urls https://docs.example.com \
    --analysis_query "Extract all API endpoints and their parameters"
```

## 🔌 Custom Tool Handlers

Create custom media processors by adding Python files to `./tools/`:

```python
# ./tools/custom_handler.py
TYPE = "custom"  # Handler type

def process(filepath):
    """Process custom file type"""
    # Your processing logic
    return {
        "processed": True,
        "data": "extracted data"
    }
```

## 📊 Output Examples

### JSON Output
```json
{
  "results": {
    "https://example.com": {
      "url": "https://example.com",
      "title": "Example Site",
      "media": [
        {
          "type": "image",
          "ocr_text": "Extracted text from image",
          "ai_description": "A diagram showing..."
        },
        {
          "type": "pdf",
          "text": "PDF content...",
          "ai_analysis": {
            "reasoning": "The document discusses...",
            "answer": "Key points are..."
          }
        }
      ],
      "analysis": "Comprehensive analysis of all content..."
    }
  },
  "summary": {
    "total_urls": 1,
    "successful": 1,
    "failed": 0,
    "media_processed": 2
  }
}
```

### HTML Report
- Beautiful, styled reports with statistics
- Media previews and extracted content
- AI analysis sections
- Interactive navigation

## 🛡️ Anti-Detection Features

1. **User Agent Rotation**: Random browser fingerprints
2. **Viewport Randomization**: Different screen sizes
3. **JavaScript Injection**: Bypass `navigator.webdriver` detection
4. **Request Delays**: Human-like browsing patterns
5. **Proxy Support**: Route through different IPs
6. **Session Management**: Intelligent cookie handling

## 🧪 Advanced Features

### Multi-Modal Intelligence
- Cross-reference text, images, and documents
- Extract data from videos and audio
- OCR for text in images
- PDF table extraction
- Code analysis

### Memory System
- Vector embeddings for semantic search
- Pattern recognition across sessions
- Conversation history retention
- Similar content discovery

### AI Capabilities
- **DeepSeek Reasoner**: Complex analysis with chain-of-thought
- **FIM Completion**: Fill-in-the-middle for code/content
- **Prefix Completion**: Controlled output generation
- **Multi-turn Conversations**: Context-aware analysis

## 📈 Performance

- Concurrent scraping with configurable workers
- Automatic retry on failures
- Rate limiting protection
- Memory-efficient media processing
- Progress tracking with rich console output

## 🔍 Troubleshooting

### Common Issues

1. **ChromeDriver not found**
   ```bash
   # Install ChromeDriver
   wget https://chromedriver.storage.googleapis.com/LATEST_RELEASE
   # Or use package manager
   ```

2. **Tesseract not found**
   ```bash
   # Verify installation
   tesseract --version
   ```

3. **Memory errors with large media**
   - Reduce `max_workers`
   - Process files in batches
   - Increase system swap

## 🚦 Best Practices

1. **Respect robots.txt**: Check site policies
2. **Rate Limiting**: Don't overwhelm servers
3. **Legal Compliance**: Ensure you have permission
4. **Error Handling**: Monitor failed scrapes
5. **Resource Management**: Close scraper properly

## 📝 License

This tool is for educational and research purposes. Users are responsible for compliance with applicable laws and website terms of service.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new features
4. Submit pull request

## 🆘 Support

- GitHub Issues: Report bugs
- Discussions: Feature requests
- Wiki: Extended documentation

---

**⚡ Built with DeepSeek AI integration for next-level web intelligence gathering.**