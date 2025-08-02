# DeepSeek API Integration

A comprehensive Python integration for DeepSeek's language models, providing easy access to both `deepseek-chat` and `deepseek-reasoner` models with full feature support.

## Features

- 🤖 **Dual Model Support**: Access both DeepSeek-Chat and DeepSeek-Reasoner models
- 🔄 **Streaming Responses**: Real-time streaming for better user experience
- 🧩 **Function Calling**: Built-in support for tool/function definitions
- 📊 **JSON Output Mode**: Structured data generation with guaranteed valid JSON
- 💰 **Usage Tracking**: Monitor token usage and estimate costs
- 🔁 **Automatic Retries**: Handle rate limits with exponential backoff
- ⚡ **Async Support**: Both synchronous and asynchronous APIs
- 🎯 **Batch Processing**: Process multiple prompts concurrently
- 💾 **Context Caching**: Automatic caching for reduced costs (up to 74% savings)
- 🌐 **Web API**: Ready-to-use FastAPI service with WebSocket support

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd deepseek-integration
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your environment variables:
```bash
cp .env.example .env
# Edit .env and add your DeepSeek API key
```

## Quick Start

### Basic Usage

```python
from deepseek_integration import DeepSeekClient

# Initialize client
client = DeepSeekClient()

# Simple chat
response = client.chat("What is the capital of France?")
print(response)

# Using the reasoning model
result = client.reason("If a train travels 120 km in 2 hours, what is its average speed?")
print(f"Answer: {result['answer']}")
print(f"Reasoning: {result['reasoning']}")
```

### Streaming Responses

```python
# Stream responses for better UX
for chunk in client.chat("Tell me a story", stream=True):
    print(chunk, end='', flush=True)
```

### JSON Output Mode

```python
from deepseek_integration import ResponseFormat

# Generate structured data
response = client.chat(
    "Create a user profile with name, age, and hobbies",
    response_format=ResponseFormat.JSON,
    system_prompt="Always respond with valid JSON"
)
print(json.dumps(response, indent=2))
```

### Function Calling

```python
# Define a function tool
weather_tool = client.create_function_tool(
    name="get_weather",
    description="Get the current weather in a location",
    parameters={
        "location": {"type": "string", "description": "City name"},
        "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
    },
    required=["location"]
)

# Use function calling
response = client.chat(
    "What's the weather in Paris?",
    tools=[weather_tool],
    tool_choice="auto"
)
```

### Batch Processing

```python
# Process multiple prompts concurrently
prompts = [
    "Translate 'hello' to Spanish",
    "What is 2+2?",
    "Name the planets in our solar system"
]

responses = client.batch_chat(prompts, max_concurrent=3)
for prompt, response in zip(prompts, responses):
    print(f"Q: {prompt}\nA: {response}\n")
```

## Examples

### 1. Interactive Chatbot

Run the interactive chatbot with conversation history and multiple modes:

```bash
python examples/chatbot_app.py
```

Features:
- Chat, reasoning, and code generation modes
- Conversation history management
- Usage statistics tracking
- Export conversations

Commands:
- `/help` - Show available commands
- `/mode [chat|reason|code]` - Switch conversation mode
- `/stats` - Show usage statistics
- `/save` - Save conversation to file
- `/quit` - Exit the chatbot

### 2. Web API Service

Start the FastAPI web service:

```bash
python examples/web_api.py
```

The API will be available at `http://localhost:8000` with the following endpoints:

- `POST /api/v1/chat` - Chat completion
- `POST /api/v1/reason` - Reasoning endpoint
- `POST /api/v1/functions/call` - Function calling
- `POST /api/v1/batch` - Batch processing
- `GET /api/v1/usage` - Usage statistics
- `WS /ws/chat` - WebSocket for real-time chat

#### Example API Calls

**Chat Completion:**
```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hello!"}
    ],
    "temperature": 0.7
  }'
```

**Streaming Response:**
```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Tell me a joke"}
    ],
    "stream": true
  }'
```

**Reasoning:**
```bash
curl -X POST "http://localhost:8000/api/v1/reason" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What is the sum of all numbers from 1 to 100?",
    "reasoning_effort": "high"
  }'
```

## Advanced Usage

### Custom Configuration

```python
from deepseek_integration import DeepSeekClient, DeepSeekConfig, DeepSeekModel

config = DeepSeekConfig(
    api_key="your-api-key",
    base_url="https://api.deepseek.com",
    default_model=DeepSeekModel.REASONER,
    max_retries=5,
    timeout=120.0
)

client = DeepSeekClient(config)
```

### Async Operations

```python
import asyncio

async def async_example():
    client = DeepSeekClient()
    
    # Async chat
    response = await client.achat("Hello, async world!")
    print(response)
    
    # Async streaming
    async for chunk in await client.achat("Tell me a story", stream=True):
        print(chunk, end='', flush=True)

asyncio.run(async_example())
```

### Error Handling

```python
from deepseek_integration import DeepSeekError, RateLimitError

try:
    response = client.chat("Hello")
except RateLimitError as e:
    print(f"Rate limit exceeded: {e}")
    # Wait and retry
except DeepSeekError as e:
    print(f"API error: {e}")
```

### Token Usage Monitoring

```python
# Get usage summary
usage = client.get_usage_summary()
print(f"Total tokens used: {usage['usage']['total_tokens']:,}")
print(f"Estimated cost: ${usage['costs']['total_cost']:.4f}")
print(f"Cache hit rate: {usage['efficiency']['cache_hit_rate']}%")

# Reset usage tracking
client.reset_usage()
```

## Model Comparison

| Feature | deepseek-chat | deepseek-reasoner |
|---------|--------------|-------------------|
| General conversation | ✅ Excellent | ✅ Good |
| Code generation | ✅ Excellent | ✅ Good |
| Mathematical reasoning | ✅ Good | ✅ Excellent |
| Step-by-step problem solving | ✅ Good | ✅ Excellent |
| Context length | 163,840 tokens | 163,840 tokens |
| Response speed | Fast | Slower (due to reasoning) |

## Cost Optimization

1. **Use Context Caching**: Repeated prompts are automatically cached, reducing costs by up to 74%
2. **Optimize Prompts**: Shorter, more specific prompts use fewer tokens
3. **Set Max Tokens**: Limit response length when appropriate
4. **Batch Processing**: Process multiple requests concurrently for efficiency
5. **Monitor Usage**: Regularly check usage statistics to identify optimization opportunities

## API Reference

### DeepSeekClient

The main client class for interacting with DeepSeek API.

#### Methods

- `chat(messages, model=None, temperature=0.7, max_tokens=None, stream=False, response_format=None, tools=None, tool_choice=None, system_prompt=None, **kwargs)`
- `achat(...)` - Async version of chat
- `reason(prompt, reasoning_effort="medium", show_reasoning=True, **kwargs)`
- `create_function_tool(name, description, parameters, required=None)`
- `batch_chat(prompts, model=None, max_concurrent=5, **kwargs)`
- `get_usage_summary()` - Get token usage and cost statistics
- `reset_usage()` - Reset usage tracking

### Configuration Options

- `api_key`: Your DeepSeek API key
- `base_url`: API endpoint (default: https://api.deepseek.com)
- `default_model`: Default model to use
- `max_retries`: Maximum retry attempts
- `retry_delay`: Initial retry delay in seconds
- `timeout`: Request timeout in seconds

## Requirements

- Python 3.8+
- OpenAI Python SDK
- FastAPI (for web service)
- python-dotenv
- httpx
- pydantic

## Environment Variables

Create a `.env` file with:

```env
DEEPSEEK_API_KEY=your-api-key-here
DEEPSEEK_API_ENDPOINT=https://api.deepseek.com/v1  # Optional
DEEPSEEK_MODEL=deepseek-chat  # Optional
DEEPSEEK_MAX_TOKENS=4096  # Optional
DEEPSEEK_TEMPERATURE=0.7  # Optional
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

<<<<<<< Current (Your changes)
Please see our [security disclosure process](SECURITY.md). All [security advisories](https://github.com/google-gemini/gemini-cli/security/advisories) are managed on Github.
=======
- Built on top of the DeepSeek API
- Uses OpenAI's SDK for compatibility
- Inspired by modern AI integration patterns
>>>>>>> Incoming (Background Agent changes)
