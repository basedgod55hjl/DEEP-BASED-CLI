# DeepSeek API Implementation Documentation

## Overview
This documentation provides comprehensive guides, scripts, and implementation details for integrating DeepSeek API models into the deep-cli-ts project. The implementation focuses on two primary models:

- **deepseek-chat** (DeepSeek-V3): For conversational AI and general-purpose tasks
- **deepseek-reasoner** (DeepSeek-R1): For advanced reasoning, chain-of-thought processing, and complex problem-solving

## API Configuration

### Base Configuration
- **Base URL**: `https://api.deepseek.com`
- **API Key**: `sk-90e0dd863b8c4e0d879a02851a0ee194` (hardcoded as requested)
- **Compatible with**: OpenAI SDK format

### Model Specifications

#### DeepSeek-Chat (deepseek-chat)
- **Model**: DeepSeek-V3-0324
- **Context Length**: 64K tokens
- **Max Output**: 8K tokens
- **Input Cost**: $0.07 per 1M tokens
- **Output Cost**: $0.28 per 1M tokens
- **Use Cases**: Conversations, content generation, general AI tasks

#### DeepSeek-Reasoner (deepseek-reasoner)
- **Model**: DeepSeek-R1-0528
- **Context Length**: 64K tokens
- **Max Output**: 8K tokens (including reasoning)
- **Input Cost**: $0.55 per 1M tokens
- **Output Cost**: $2.19 per 1M tokens
- **Special Features**: Chain-of-Thought reasoning, `reasoning_content` field
- **Use Cases**: Complex problem-solving, mathematical reasoning, logical inference

## Documentation Structure

```
docs/
├── README.md                           # This file
├── api-reference/
│   ├── deepseek-chat.md               # Chat model reference
│   ├── deepseek-reasoner.md           # Reasoner model reference
│   ├── authentication.md              # Auth and security
│   └── error-handling.md              # Error codes and handling
├── guides/
│   ├── getting-started.md             # Quick start guide
│   ├── reasoning-chains.md            # Chain-of-thought usage
│   ├── multi-turn-conversations.md   # Conversation management
│   └── performance-optimization.md   # Performance tips
├── examples/
│   ├── basic-chat.js                  # Simple chat example
│   ├── reasoning-example.js           # Reasoning chain example
│   ├── multi-turn-chat.js            # Multi-turn conversation
│   └── advanced-reasoning.js         # Complex reasoning tasks
├── scripts/
│   ├── test-connection.js             # Connection testing
│   ├── benchmark-models.js           # Performance benchmarking
│   └── batch-processing.js           # Batch request handling
└── implementation/
    ├── deepseek-brain.ts              # Core reasoning engine
    ├── conversation-manager.ts        # Chat management
    ├── reasoning-chain.ts             # Chain-of-thought processor
    └── model-selector.ts              # Intelligent model selection
```

## Quick Start

### 1. Installation
```bash
npm install openai
```

### 2. Basic Usage
```javascript
import OpenAI from 'openai';

const client = new OpenAI({
  apiKey: 'sk-90e0dd863b8c4e0d879a02851a0ee194',
  baseURL: 'https://api.deepseek.com'
});

// Chat model for conversations
const chatResponse = await client.chat.completions.create({
  model: 'deepseek-chat',
  messages: [{ role: 'user', content: 'Hello!' }]
});

// Reasoner model for complex thinking
const reasoningResponse = await client.chat.completions.create({
  model: 'deepseek-reasoner',
  messages: [{ role: 'user', content: 'Solve: What is 15% of 240?' }]
});
```

### 3. Brain Logic Implementation
The project implements a dual-brain architecture:

- **Chat Brain** (`deepseek-chat`): Handles conversations, quick responses, and general tasks
- **Reasoning Brain** (`deepseek-reasoner`): Handles complex logic, mathematical problems, and step-by-step reasoning

## Key Features

### Chain-of-Thought Reasoning
The `deepseek-reasoner` model provides transparent reasoning through the `reasoning_content` field:

```javascript
const response = await client.chat.completions.create({
  model: 'deepseek-reasoner',
  messages: [{ role: 'user', content: 'How do I solve this math problem?' }]
});

console.log('Reasoning:', response.choices[0].message.reasoning_content);
console.log('Answer:', response.choices[0].message.content);
```

### Intelligent Model Selection
The system automatically selects the appropriate model based on task complexity:

- Simple queries → `deepseek-chat`
- Complex reasoning → `deepseek-reasoner`
- Mathematical problems → `deepseek-reasoner`
- Conversational tasks → `deepseek-chat`

### Performance Optimizations
- Caching for repeated queries
- Context length management
- Streaming responses for real-time interaction
- Token usage optimization

## Implementation Files

All implementation files are located in the `src/` directory and integrated with the existing tool system:

- `src/tools/DeepSeekBrain.ts` - Core reasoning engine
- `src/tools/ConversationManager.ts` - Multi-turn chat handling
- `src/tools/ReasoningChain.ts` - Chain-of-thought processing
- `src/common/DeepSeekConfig.ts` - Configuration management

## Next Steps

1. Review the [Getting Started Guide](guides/getting-started.md)
2. Explore [API Reference](api-reference/) for detailed documentation
3. Try the [Examples](examples/) to understand implementation patterns
4. Use [Scripts](scripts/) for testing and benchmarking

## Support and Resources

- [DeepSeek API Documentation](https://api-docs.deepseek.com/)
- [DeepSeek Platform](https://platform.deepseek.com/)
- [GitHub Repository](https://github.com/deepseek-ai)
- [Community Discord](https://discord.gg/deepseek)

---

*This documentation is maintained as part of the deep-cli-ts project and reflects the latest DeepSeek API capabilities.*