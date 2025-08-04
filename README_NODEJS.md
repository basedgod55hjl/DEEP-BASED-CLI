# DeepSeek-Reasoner Brain System

🚀 **Advanced AI Agent System with DeepSeek-Reasoner as Main Brain**

Made by @Lucariolucario55 on Telegram

## 🌟 Features

### 🧠 **DeepSeek-Reasoner as Main Brain**
- **Chain-of-Thought Reasoning**: Advanced reasoning with step-by-step analysis
- **Tool Calling Integration**: Seamless integration with Qwen tools and web scraping
- **Multi-Model Coordination**: DeepSeek-Reasoner → DeepSeek-Chat → DeepSeek-V3 pipeline
- **Streaming Token Feedback**: Real-time token streaming for enhanced user experience

### 👤 **DEANNA Persona System**
- **Default Persona**: DEANNA (Digital Entity for Advanced Neural Network Architecture)
- **Personality Traits**: Intelligent, creative, empathetic, and professional
- **Conversation Patterns**: Natural, engaging, and context-aware responses
- **Knowledge Base**: Specialized in AI, programming, reasoning, and problem-solving

### 🔧 **Advanced Tool Integration**
- **Qwen Embedding Tool**: High-quality embeddings using Qwen3-Embedding-0.6B
- **Web Scraper Tool**: AI-powered web scraping with multiple methods (Puppeteer, Cheerio, Osmosis)
- **Memory Store**: Persistent JSON-based memory with advanced querying
- **Thought Storage**: Cached reasoning thoughts to save tokens

### 💬 **Multi-Conversation Support**
- **Context Management**: Maintains conversation history and context
- **Persona Switching**: Dynamic persona loading and switching
- **Streaming Responses**: Real-time streaming with reasoning visualization
- **WebSocket Support**: Real-time communication for web applications

### 🎯 **Advanced Features**
- **FIM Completion**: Fill-in-the-middle text completion
- **Prefix Completion**: Context-aware text continuation
- **Semantic Search**: Vector-based similarity search
- **Memory Analytics**: Usage patterns and insights
- **Cache Management**: Intelligent caching for performance

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- npm or yarn
- DeepSeek API key

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/basedgod55hjl/DEEP-BASED-CLI.git
cd DEEP-BASED-CLI
```

2. **Install dependencies**
```bash
npm install
```

3. **Set up environment variables**
```bash
# Create .env file
echo "DEEPSEEK_API_KEY=your_deepseek_api_key_here" > .env
echo "PORT=3000" >> .env
```

4. **Start the server**
```bash
npm start
```

### Development Mode
```bash
npm run dev
```

## 📡 API Endpoints

### Chat Endpoints

#### Regular Chat
```bash
POST /chat
Content-Type: application/json

{
  "message": "Hello, how can you help me?",
  "persona": "DEANNA",
  "stream": false
}
```

#### Streaming Chat
```bash
POST /chat
Content-Type: application/json

{
  "message": "Explain quantum computing",
  "persona": "DEANNA",
  "stream": true
}
```

### Tool Endpoints

#### Web Scraping
```bash
POST /scrape
Content-Type: application/json

{
  "url": "https://example.com",
  "selectors": {
    "title": "h1",
    "content": "article",
    "links": "a"
  },
  "config": {
    "method": "puppeteer",
    "timeout": 30000
  }
}
```

#### Embedding Generation
```bash
POST /embed
Content-Type: application/json

{
  "text": "Generate embedding for this text",
  "model": "qwen"
}
```

### Memory Endpoints

#### Store Memory
```bash
POST /memory/store
Content-Type: application/json

{
  "content": "Important information to remember",
  "category": "conversation",
  "tags": ["important", "user-preference"],
  "importance": 8.5
}
```

#### Search Memory
```bash
GET /memory/search?query=important&category=conversation&limit=10
```

### Reasoning Endpoints

#### Chain-of-Thought Reasoning
```bash
POST /reason
Content-Type: application/json

{
  "question": "How do I implement a neural network?",
  "context": "I'm a beginner in machine learning",
  "persona": "DEANNA"
}
```

#### FIM Completion
```bash
POST /fim
Content-Type: application/json

{
  "prefix": "The quick brown fox",
  "suffix": "over the lazy dog",
  "model": "deepseek-chat"
}
```

#### Prefix Completion
```bash
POST /prefix
Content-Type: application/json

{
  "text": "The future of artificial intelligence",
  "model": "deepseek-chat"
}
```

## 🔌 WebSocket API

### Connection
```javascript
const socket = io('ws://localhost:3000');
```

### Chat Events
```javascript
// Send chat message
socket.emit('chat', {
  message: 'Hello DEANNA!',
  persona: 'DEANNA'
});

// Receive response
socket.on('chat_response', (response) => {
  console.log('Response:', response);
});

// Streaming chat
socket.emit('chat_stream', {
  message: 'Explain quantum computing',
  persona: 'DEANNA'
});

socket.on('stream_chunk', (chunk) => {
  console.log('Stream chunk:', chunk.data);
});

socket.on('stream_end', () => {
  console.log('Stream ended');
});
```

### Tool Events
```javascript
// Call tool
socket.emit('tool_call', {
  tool: 'web_scraper',
  params: {
    url: 'https://example.com',
    selectors: { title: 'h1' }
  }
});

// Receive tool result
socket.on('tool_result', (result) => {
  console.log('Tool result:', result);
});
```

## 🏗️ Architecture

### Core Components

```
DeepSeek-Reasoner Brain System
├── DeepSeekReasonerBrain (Main Brain)
│   ├── Reasoning Engine (Chain-of-Thought)
│   ├── Tool Coordinator
│   ├── Persona Manager
│   └── Response Generator
├── PersonaSystem (DEANNA & Others)
│   ├── Personality Traits
│   ├── Conversation Patterns
│   └── Knowledge Base
├── MemoryStore (JSON Memory)
│   ├── Persistent Storage
│   ├── Advanced Querying
│   └── Analytics
├── ToolManager (Tool Integration)
│   ├── QwenEmbeddingTool
│   ├── WebScraperTool
│   └── Extensible Tool System
├── StreamingManager (Real-time)
│   ├── Token Streaming
│   ├── WebSocket Support
│   └── Event Management
├── ConversationManager (Multi-conversation)
│   ├── Context Management
│   ├── History Tracking
│   └── Persona Switching
└── ThoughtStorage (Token Optimization)
    ├── Cached Thoughts
    ├── Reasoning Chains
    └── Reuse Optimization
```

### Data Flow

1. **User Input** → **DeepSeek-Reasoner Brain**
2. **Reasoning Process** → **Chain-of-Thought Analysis**
3. **Tool Calls** → **Qwen Tools & Web Scraping**
4. **Memory Integration** → **JSON Memory Store**
5. **Persona Processing** → **DEANNA Personality**
6. **Final Response** → **DeepSeek-V3 Generation**
7. **Streaming Output** → **Real-time Token Feed**

## 🛠️ Configuration

### Environment Variables
```bash
# Required
DEEPSEEK_API_KEY=your_api_key_here

# Optional
PORT=3000
NODE_ENV=development
LOG_LEVEL=info
CACHE_SIZE=10000
MAX_MEMORY_ENTRIES=10000
```

### Persona Configuration
Personas are stored in `data/personas/` as JSON files. The default DEANNA persona includes:

- **Personality Traits**: Intelligent, creative, empathetic
- **Communication Style**: Professional, warm, engaging
- **Expertise**: AI, programming, reasoning, problem-solving
- **Values**: Accuracy, creativity, user empowerment
- **Behavioral Patterns**: Systematic, collaborative, educational

### Tool Configuration
Tools can be configured in their respective classes:

- **Qwen Embedding**: Model path, dimension, normalization
- **Web Scraper**: Timeout, retries, user agent, cache settings
- **Memory Store**: Max entries, backup interval, auto-cleanup

## 📊 Monitoring & Analytics

### Health Check
```bash
GET /health
```

### Brain Status
```bash
GET /brain/status
```

### Memory Analytics
```bash
GET /memory/analytics
```

### Tool Status
```bash
GET /tools/status
```

## 🔧 Development

### Project Structure
```
src/
├── index.js                 # Main entry point
├── core/                    # Core systems
│   ├── DeepSeekReasonerBrain.js
│   ├── PersonaSystem.js
│   ├── MemoryStore.js
│   ├── ToolManager.js
│   ├── StreamingManager.js
│   ├── ConversationManager.js
│   └── ThoughtStorage.js
├── tools/                   # Tool implementations
│   ├── QwenEmbeddingTool.js
│   └── WebScraperTool.js
└── utils/                   # Utilities
    └── Logger.js
```

### Adding New Tools
1. Create tool class in `src/tools/`
2. Implement required methods
3. Register in `ToolManager.js`
4. Add API endpoints in `index.js`

### Adding New Personas
1. Create persona JSON in `data/personas/`
2. Define personality traits and patterns
3. Load via `PersonaSystem.js`

## 🚀 Deployment

### Production Setup
```bash
# Build for production
npm run build

# Start production server
NODE_ENV=production npm start
```

### Docker Deployment
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
```

### Environment Variables for Production
```bash
DEEPSEEK_API_KEY=your_production_key
NODE_ENV=production
PORT=3000
LOG_LEVEL=warn
```

## 🔒 Security

- **API Key Protection**: Environment variable storage
- **Input Validation**: Comprehensive request validation
- **Rate Limiting**: Built-in rate limiting for API endpoints
- **CORS Configuration**: Configurable cross-origin settings
- **Helmet Security**: Security headers and middleware

## 📈 Performance

- **Caching**: Intelligent caching for embeddings and scraped data
- **Streaming**: Real-time token streaming for better UX
- **Memory Management**: Efficient memory usage with cleanup
- **Concurrent Processing**: Parallel tool execution
- **Database Optimization**: Indexed memory queries

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Implement changes
4. Add tests
5. Submit pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- **Documentation**: Check this README and inline code comments
- **Issues**: Report bugs via GitHub Issues
- **Discussions**: Use GitHub Discussions for questions
- **Telegram**: Contact @Lucariolucario55

## 🎯 Roadmap

- [ ] Enhanced AI model integration
- [ ] Advanced reasoning capabilities
- [ ] Multi-modal support (images, audio)
- [ ] Distributed deployment
- [ ] Advanced analytics dashboard
- [ ] Plugin system for custom tools
- [ ] Mobile app integration
- [ ] Enterprise features

---

**Made with ❤️ by @Lucariolucario55**

*Advanced AI Agent System powered by DeepSeek-Reasoner* 