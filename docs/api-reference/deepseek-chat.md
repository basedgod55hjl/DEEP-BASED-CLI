# DeepSeek-Chat API Reference

## Overview
The `deepseek-chat` model (DeepSeek-V3-0324) is optimized for conversational AI, content generation, and general-purpose language tasks. It provides fast, efficient responses for everyday AI interactions.

## Model Specifications
- **Model ID**: `deepseek-chat`
- **Version**: DeepSeek-V3-0324
- **Context Length**: 64,000 tokens
- **Max Output**: 8,000 tokens
- **Pricing**: $0.07/1M input tokens, $0.28/1M output tokens

## Basic Usage

### Simple Chat Completion
```javascript
import OpenAI from 'openai';

const client = new OpenAI({
  apiKey: 'sk-90e0dd863b8c4e0d879a02851a0ee194',
  baseURL: 'https://api.deepseek.com'
});

const response = await client.chat.completions.create({
  model: 'deepseek-chat',
  messages: [
    { role: 'system', content: 'You are a helpful assistant.' },
    { role: 'user', content: 'Hello! How are you today?' }
  ],
  max_tokens: 1000,
  temperature: 0.7
});

console.log(response.choices[0].message.content);
```

### Streaming Response
```javascript
const stream = await client.chat.completions.create({
  model: 'deepseek-chat',
  messages: [{ role: 'user', content: 'Tell me a story' }],
  stream: true,
  max_tokens: 2000
});

for await (const chunk of stream) {
  const content = chunk.choices[0]?.delta?.content || '';
  process.stdout.write(content);
}
```

## Parameters

### Required Parameters
- **model**: `'deepseek-chat'`
- **messages**: Array of message objects

### Optional Parameters

#### Core Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_tokens` | integer | 2000 | Maximum tokens to generate |
| `temperature` | float | 1.0 | Creativity control (0.0-2.0) |
| `top_p` | float | 1.0 | Nucleus sampling parameter |
| `stream` | boolean | false | Enable streaming responses |
| `stop` | string/array | null | Stop sequences |

#### Advanced Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `presence_penalty` | float | 0.0 | Penalize new topics (-2.0 to 2.0) |
| `frequency_penalty` | float | 0.0 | Penalize repetition (-2.0 to 2.0) |
| `logit_bias` | object | null | Modify token probabilities |
| `user` | string | null | User identifier for tracking |

## Message Format

### Message Structure
```javascript
{
  role: 'system' | 'user' | 'assistant',
  content: string
}
```

### Role Types
- **system**: Sets the behavior and context for the assistant
- **user**: Human input messages
- **assistant**: AI responses (for multi-turn conversations)

### Example Multi-turn Conversation
```javascript
const messages = [
  { role: 'system', content: 'You are a coding assistant.' },
  { role: 'user', content: 'How do I create a function in Python?' },
  { role: 'assistant', content: 'To create a function in Python, use the `def` keyword...' },
  { role: 'user', content: 'Can you show me an example?' }
];

const response = await client.chat.completions.create({
  model: 'deepseek-chat',
  messages: messages
});
```

## Response Format

### Standard Response
```javascript
{
  id: "chatcmpl-123",
  object: "chat.completion",
  created: 1677652288,
  model: "deepseek-chat",
  choices: [{
    index: 0,
    message: {
      role: "assistant",
      content: "Hello! I'm doing well, thank you for asking..."
    },
    finish_reason: "stop"
  }],
  usage: {
    prompt_tokens: 20,
    completion_tokens: 15,
    total_tokens: 35
  }
}
```

### Streaming Response
```javascript
{
  id: "chatcmpl-123",
  object: "chat.completion.chunk",
  created: 1677652288,
  model: "deepseek-chat",
  choices: [{
    index: 0,
    delta: {
      content: "Hello"
    },
    finish_reason: null
  }]
}
```

## Use Cases

### Content Generation
```javascript
const response = await client.chat.completions.create({
  model: 'deepseek-chat',
  messages: [{
    role: 'user',
    content: 'Write a blog post about the benefits of renewable energy'
  }],
  max_tokens: 3000,
  temperature: 0.8
});
```

### Code Assistance
```javascript
const response = await client.chat.completions.create({
  model: 'deepseek-chat',
  messages: [{
    role: 'system',
    content: 'You are an expert programmer.'
  }, {
    role: 'user',
    content: 'Debug this JavaScript function: function add(a, b) { return a + b }'
  }],
  temperature: 0.2
});
```

### Language Translation
```javascript
const response = await client.chat.completions.create({
  model: 'deepseek-chat',
  messages: [{
    role: 'user',
    content: 'Translate "Hello, how are you?" to French, Spanish, and German'
  }]
});
```

## Best Practices

### Temperature Guidelines
- **0.0-0.3**: Factual, deterministic responses
- **0.4-0.7**: Balanced creativity and accuracy
- **0.8-1.2**: Creative writing, brainstorming
- **1.3-2.0**: Maximum creativity (experimental)

### Token Management
```javascript
// Estimate tokens (rough approximation)
function estimateTokens(text) {
  return Math.ceil(text.length / 4); // 1 token ≈ 4 characters
}

// Monitor usage
const response = await client.chat.completions.create({
  model: 'deepseek-chat',
  messages: messages,
  max_tokens: 1000
});

console.log(`Used ${response.usage.total_tokens} tokens`);
```

### Error Handling
```javascript
try {
  const response = await client.chat.completions.create({
    model: 'deepseek-chat',
    messages: messages
  });
  return response.choices[0].message.content;
} catch (error) {
  if (error.status === 401) {
    console.error('Authentication failed');
  } else if (error.status === 429) {
    console.error('Rate limit exceeded');
  } else if (error.status === 400) {
    console.error('Invalid request:', error.message);
  }
  throw error;
}
```

## Limitations

### Context Window
- Maximum 64K tokens total (input + output)
- Longer conversations may need truncation
- Consider conversation summarization for long chats

### Rate Limits
- Requests per minute: Varies by plan
- Tokens per minute: Varies by plan
- Monitor usage to avoid throttling

### Unsupported Features
- Image processing (use vision models instead)
- Function calling (limited support)
- Fine-tuning (contact DeepSeek for custom models)

## Performance Tips

### Optimize Prompts
```javascript
// Good: Specific and clear
const goodPrompt = "Write a 200-word summary of renewable energy benefits";

// Avoid: Vague and open-ended
const vaguePrompt = "Tell me about energy";
```

### Batch Similar Requests
```javascript
// Process multiple similar requests efficiently
const prompts = [
  "Summarize this article: ...",
  "Summarize this article: ...",
  "Summarize this article: ..."
];

const responses = await Promise.all(
  prompts.map(prompt => 
    client.chat.completions.create({
      model: 'deepseek-chat',
      messages: [{ role: 'user', content: prompt }]
    })
  )
);
```

### Cache Common Responses
```javascript
const cache = new Map();

async function getCachedResponse(prompt) {
  if (cache.has(prompt)) {
    return cache.get(prompt);
  }
  
  const response = await client.chat.completions.create({
    model: 'deepseek-chat',
    messages: [{ role: 'user', content: prompt }]
  });
  
  cache.set(prompt, response.choices[0].message.content);
  return response.choices[0].message.content;
}
```

## Integration Examples

### Express.js API
```javascript
app.post('/chat', async (req, res) => {
  try {
    const response = await client.chat.completions.create({
      model: 'deepseek-chat',
      messages: req.body.messages,
      max_tokens: 1000
    });
    
    res.json({
      message: response.choices[0].message.content,
      usage: response.usage
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});
```

### WebSocket Streaming
```javascript
ws.on('message', async (data) => {
  const { message } = JSON.parse(data);
  
  const stream = await client.chat.completions.create({
    model: 'deepseek-chat',
    messages: [{ role: 'user', content: message }],
    stream: true
  });
  
  for await (const chunk of stream) {
    const content = chunk.choices[0]?.delta?.content || '';
    if (content) {
      ws.send(JSON.stringify({ content }));
    }
  }
});
```

---

*For more advanced reasoning tasks, consider using the [deepseek-reasoner](deepseek-reasoner.md) model.*