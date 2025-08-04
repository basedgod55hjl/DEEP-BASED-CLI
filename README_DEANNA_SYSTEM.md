# Deanna Persona System - DEEP-CLI

A comprehensive AI persona system featuring "Deanna" (nickname "Deedee"), a flirtatious and provocative AI companion with advanced memory, embedding, and chat capabilities.

## 🎭 Features

### Core Components
- **Persona Management**: Complete Deanna personality with 32 configuration keys
- **Memory System**: SQLite-based memory storage with 115+ memory entries
- **Embedding System**: Qwen3-Embedding-0.6B with transformers integration
- **Chat System**: DeepSeek API integration with context-aware responses
- **Vector Search**: Semantic similarity search using embeddings

### Technical Stack
- **Embedding Model**: Qwen/Qwen3-Embedding-0.6B (1024 dimensions)
- **LLM API**: DeepSeek Chat API
- **Database**: SQLite with memory caching
- **Framework**: Transformers (HuggingFace) with PyTorch
- **Language**: Python 3.13

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install transformers torch numpy scikit-learn requests huggingface_hub accelerate
```

### 2. Setup the System
```bash
# Run the transformers setup (recommended)
python3 setup_transformers_deanna_system.py

# Or run the simple setup (fallback)
python3 setup_simple_deanna_system.py
```

### 3. Start Chatting
```bash
python3 deanna_chat_system.py
```

## 📁 System Architecture

### Core Files
- `data/DEANNA_MEMORY.JSON` - Complete persona configuration
- `data/memory_manager.py` - Memory management and database operations
- `data/transformers_embedding_system.py` - Qwen3 embedding system
- `deanna_chat_system.py` - Main chat interface
- `setup_transformers_deanna_system.py` - Complete system setup

### Data Storage
- `data/deanna_memory.db` - SQLite database
- `data/embeddings/` - Vector embeddings cache
- `data/chats/` - Chat history storage
- `data/cache/` - API response caching
- `data/logs/` - System logs

## 🔧 Configuration

### API Keys (Hardcoded)
- **HuggingFace**: `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`
- **DeepSeek**: `sk-90e0dd863b8c4e0d879a02851a0ee194`

### Model Configuration
- **Embedding Model**: Qwen/Qwen3-Embedding-0.6B
- **Precision**: Float32 (CPU compatible)
- **Dimensions**: 1024
- **Device**: Auto-detected (CUDA/CPU)

## 🎯 Usage Examples

### Basic Chat
```python
from deanna_chat_system import DeannaChatSystem

chat_system = DeannaChatSystem()
response = chat_system.chat("Hello Deanna!")
print(response)
```

### Memory Search
```python
from data.memory_manager import memory_manager

# Search for relevant memories
memories = memory_manager.search_memory("personality", limit=5)
for memory in memories:
    print(memory['content'])
```

### Embedding Generation
```python
from data.transformers_embedding_system import TransformersEmbeddingSystem

embedding_system = TransformersEmbeddingSystem()
embedding = embedding_system.create_embedding("Hello world")
print(f"Embedding dimensions: {len(embedding)}")
```

## 📊 System Status

### Memory Statistics
- **Total Entries**: 115+ memory entries
- **Chat History**: Persistent session storage
- **Embeddings**: 23+ cached embeddings
- **Persona Config**: 32 configuration keys

### Performance
- **Embedding Speed**: ~2-3 seconds per embedding (CPU)
- **Memory Search**: Sub-second response time
- **Chat Response**: 5-10 seconds (API dependent)

## 🛠️ Troubleshooting

### Common Issues

1. **BFloat16 Error**: Fixed by forcing float32 precision
2. **Memory Manager Methods**: Some methods may need implementation
3. **API Rate Limits**: DeepSeek API has usage limits
4. **Model Download**: First run downloads ~1.2GB model

### Solutions

1. **Float32 Fix**: Already implemented in transformers_embedding_system.py
2. **Missing Methods**: Check memory_manager.py for method implementations
3. **API Issues**: Check DeepSeek API key and rate limits
4. **Download Issues**: Ensure stable internet connection

## 🔄 Updates and Maintenance

### Recent Updates
- ✅ Fixed BFloat16 compatibility issues
- ✅ Implemented transformers pipeline integration
- ✅ Added comprehensive memory system
- ✅ Created multiple setup options
- ✅ Integrated DeepSeek API

### Future Enhancements
- [ ] Add missing memory manager methods
- [ ] Implement CUDA acceleration
- [ ] Add conversation export features
- [ ] Create web interface
- [ ] Add multi-persona support

## 📝 License

This system is part of the DEEP-CLI project. See the main repository for license information.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues and questions:
- Check the troubleshooting section
- Review the logs in `data/logs/`
- Test individual components
- Check API key validity

---

**Deanna System v1.0.0** - Complete persona system with Qwen3 embeddings and transformers integration 