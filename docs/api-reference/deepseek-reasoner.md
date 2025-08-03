# DeepSeek-Reasoner API Reference

## Overview
The `deepseek-reasoner` model (DeepSeek-R1-0528) is designed for advanced reasoning, complex problem-solving, and chain-of-thought processing. It provides transparent reasoning through the `reasoning_content` field, allowing you to see the model's thought process.

## Model Specifications
- **Model ID**: `deepseek-reasoner`
- **Version**: DeepSeek-R1-0528
- **Context Length**: 64,000 tokens
- **Max Output**: 8,000 tokens (including reasoning content)
- **Pricing**: $0.55/1M input tokens, $2.19/1M output tokens
- **Special Feature**: Chain-of-Thought reasoning with `reasoning_content`

## Key Features

### Chain-of-Thought Reasoning
The model generates internal reasoning before providing the final answer:

```javascript
import OpenAI from 'openai';

const client = new OpenAI({
  apiKey: 'sk-90e0dd863b8c4e0d879a02851a0ee194',
  baseURL: 'https://api.deepseek.com'
});

const response = await client.chat.completions.create({
  model: 'deepseek-reasoner',
  messages: [{
    role: 'user',
    content: 'If a train travels 120 km in 2 hours, what is its average speed?'
  }]
});

console.log('Reasoning:', response.choices[0].message.reasoning_content);
console.log('Answer:', response.choices[0].message.content);
```

## Basic Usage

### Simple Reasoning Task
```javascript
const response = await client.chat.completions.create({
  model: 'deepseek-reasoner',
  messages: [{
    role: 'user',
    content: 'Solve: 15% of 240 is what number?'
  }],
  max_tokens: 4000
});

// Access both reasoning and final answer
const reasoning = response.choices[0].message.reasoning_content;
const answer = response.choices[0].message.content;

console.log('Thought process:', reasoning);
console.log('Final answer:', answer);
```

### Complex Problem Solving
```javascript
const response = await client.chat.completions.create({
  model: 'deepseek-reasoner',
  messages: [{
    role: 'user',
    content: `A company has 3 departments: Sales (40 employees), Marketing (25 employees), 
              and Engineering (35 employees). If they need to reduce staff by 20% overall, 
              and each department must reduce by the same percentage, how many employees 
              will each department have after the reduction?`
  }],
  max_tokens: 6000
});
```

## Parameters

### Required Parameters
- **model**: `'deepseek-reasoner'`
- **messages**: Array of message objects

### Supported Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_tokens` | integer | 32000 | Maximum tokens (including reasoning) |
| `stream` | boolean | false | Enable streaming responses |
| `stop` | string/array | null | Stop sequences |
| `user` | string | null | User identifier |

### Unsupported Parameters
The following parameters are **not supported** by `deepseek-reasoner`:
- `temperature` (always uses optimal reasoning temperature)
- `top_p`
- `presence_penalty`
- `frequency_penalty`
- `logprobs`
- `top_logprobs`

## Response Format

### Standard Response Structure
```javascript
{
  id: "chatcmpl-reasoning-123",
  object: "chat.completion",
  created: 1677652288,
  model: "deepseek-reasoner",
  choices: [{
    index: 0,
    message: {
      role: "assistant",
      content: "The average speed is 60 km/h.",
      reasoning_content: "To find average speed, I need to use the formula: speed = distance / time. Given: distance = 120 km, time = 2 hours. Therefore: speed = 120 km ÷ 2 hours = 60 km/h."
    },
    finish_reason: "stop"
  }],
  usage: {
    prompt_tokens: 25,
    completion_tokens: 180,
    total_tokens: 205
  }
}
```

### Streaming Response
```javascript
// First chunks contain reasoning_content
{
  id: "chatcmpl-reasoning-123",
  object: "chat.completion.chunk",
  created: 1677652288,
  model: "deepseek-reasoner",
  choices: [{
    index: 0,
    delta: {
      reasoning_content: "To solve this problem, I need to..."
    },
    finish_reason: null
  }]
}

// Later chunks contain the final answer
{
  id: "chatcmpl-reasoning-123",
  object: "chat.completion.chunk",
  created: 1677652288,
  model: "deepseek-reasoner",
  choices: [{
    index: 0,
    delta: {
      content: "The answer is 60 km/h."
    },
    finish_reason: null
  }]
}
```

## Streaming Implementation

### Non-Streaming Example
```javascript
const response = await client.chat.completions.create({
  model: 'deepseek-reasoner',
  messages: [{ role: 'user', content: 'What is 9.11 compared to 9.8?' }]
});

const reasoning = response.choices[0].message.reasoning_content;
const answer = response.choices[0].message.content;

console.log('🧠 Reasoning:', reasoning);
console.log('💡 Answer:', answer);
```

### Streaming Example
```javascript
const stream = await client.chat.completions.create({
  model: 'deepseek-reasoner',
  messages: [{ role: 'user', content: 'Explain quantum computing' }],
  stream: true
});

let reasoning = '';
let answer = '';

for await (const chunk of stream) {
  const delta = chunk.choices[0]?.delta;
  
  if (delta?.reasoning_content) {
    reasoning += delta.reasoning_content;
    process.stdout.write(`🧠 ${delta.reasoning_content}`);
  }
  
  if (delta?.content) {
    answer += delta.content;
    process.stdout.write(`💡 ${delta.content}`);
  }
}

console.log('\n\nFull reasoning:', reasoning);
console.log('Final answer:', answer);
```

## Multi-turn Conversations

### Important: Exclude reasoning_content from follow-up messages
```javascript
let messages = [
  { role: 'user', content: '9.11 and 9.8, which is greater?' }
];

// First round
let response = await client.chat.completions.create({
  model: 'deepseek-reasoner',
  messages: messages
});

const reasoning1 = response.choices[0].message.reasoning_content;
const answer1 = response.choices[0].message.content;

// Add ONLY the content to conversation history (NOT reasoning_content)
messages.push({ role: 'assistant', content: answer1 });
messages.push({ role: 'user', content: 'How many Rs are in strawberry?' });

// Second round
response = await client.chat.completions.create({
  model: 'deepseek-reasoner',
  messages: messages
});

const reasoning2 = response.choices[0].message.reasoning_content;
const answer2 = response.choices[0].message.content;
```

### Conversation Helper Function
```javascript
class ReasoningConversation {
  constructor() {
    this.messages = [];
    this.client = new OpenAI({
      apiKey: 'sk-90e0dd863b8c4e0d879a02851a0ee194',
      baseURL: 'https://api.deepseek.com'
    });
  }

  async ask(question) {
    this.messages.push({ role: 'user', content: question });

    const response = await this.client.chat.completions.create({
      model: 'deepseek-reasoner',
      messages: this.messages
    });

    const reasoning = response.choices[0].message.reasoning_content;
    const answer = response.choices[0].message.content;

    // Only add the final answer to conversation history
    this.messages.push({ role: 'assistant', content: answer });

    return { reasoning, answer };
  }
}

// Usage
const conversation = new ReasoningConversation();
const result1 = await conversation.ask('What is 25% of 80?');
const result2 = await conversation.ask('Now add 15 to that result');
```

## Use Cases

### Mathematical Problem Solving
```javascript
const mathProblem = `
A rectangular garden is 12 meters long and 8 meters wide. 
If you want to put a fence around it and the fence costs $15 per meter, 
how much will the total cost be?
`;

const response = await client.chat.completions.create({
  model: 'deepseek-reasoner',
  messages: [{ role: 'user', content: mathProblem }]
});
```

### Logical Reasoning
```javascript
const logicPuzzle = `
All cats are mammals. All mammals are animals. Fluffy is a cat.
Based on these statements, what can we conclude about Fluffy?
Explain your reasoning step by step.
`;

const response = await client.chat.completions.create({
  model: 'deepseek-reasoner',
  messages: [{ role: 'user', content: logicPuzzle }]
});
```

### Code Analysis and Debugging
```javascript
const codeAnalysis = `
Analyze this Python function and explain what it does:

def mystery_function(n):
    if n <= 1:
        return n
    return mystery_function(n-1) + mystery_function(n-2)

What is the time complexity and can it be optimized?
`;

const response = await client.chat.completions.create({
  model: 'deepseek-reasoner',
  messages: [{ role: 'user', content: codeAnalysis }]
});
```

### Decision Making
```javascript
const decisionProblem = `
I have $1000 to invest. I can choose between:
1. Stock A: 8% annual return, low risk
2. Stock B: 15% annual return, high risk
3. Bonds: 4% annual return, very low risk

I'm 25 years old and planning for retirement. What should I choose and why?
`;

const response = await client.chat.completions.create({
  model: 'deepseek-reasoner',
  messages: [{ role: 'user', content: decisionProblem }]
});
```

## Advanced Features

### Function Calling Support
```javascript
const response = await client.chat.completions.create({
  model: 'deepseek-reasoner',
  messages: [{
    role: 'user',
    content: 'What\'s the weather like in New York?'
  }],
  functions: [{
    name: 'get_weather',
    description: 'Get weather information for a location',
    parameters: {
      type: 'object',
      properties: {
        location: { type: 'string' }
      }
    }
  }]
});
```

### JSON Output Mode
```javascript
const response = await client.chat.completions.create({
  model: 'deepseek-reasoner',
  messages: [{
    role: 'user',
    content: 'Analyze the pros and cons of remote work. Return as JSON.'
  }],
  response_format: { type: 'json_object' }
});
```

## Best Practices

### When to Use deepseek-reasoner
✅ **Use for:**
- Mathematical calculations
- Step-by-step problem solving
- Logical reasoning tasks
- Complex analysis requiring explanation
- Educational content with explanations
- Debugging and troubleshooting

❌ **Don't use for:**
- Simple conversations (use `deepseek-chat`)
- Quick factual queries
- Creative writing without reasoning
- Real-time chat where speed is critical

### Optimizing Reasoning Quality

#### Clear Problem Definition
```javascript
// Good: Specific and structured
const goodPrompt = `
Problem: Calculate compound interest
Principal: $1000
Rate: 5% annually
Time: 3 years
Show all steps in your calculation.
`;

// Avoid: Vague requests
const vaguePrompt = "Help me with some math";
```

#### Request Step-by-Step Explanations
```javascript
const prompt = `
Solve this problem step by step:
A car travels 300 km in 4 hours. 
If it maintains the same speed, how far will it travel in 6 hours?

Please show:
1. What information is given
2. What formula to use
3. The calculation steps
4. The final answer
`;
```

### Performance Considerations

#### Token Usage Optimization
```javascript
// Monitor token usage - reasoning can be verbose
const response = await client.chat.completions.create({
  model: 'deepseek-reasoner',
  messages: messages,
  max_tokens: 4000 // Adjust based on problem complexity
});

console.log(`Reasoning tokens: ${response.usage.completion_tokens}`);
```

#### Caching Strategies
```javascript
// Cache reasoning for similar problems
const reasoningCache = new Map();

async function getCachedReasoning(problem) {
  const key = hashProblem(problem);
  
  if (reasoningCache.has(key)) {
    return reasoningCache.get(key);
  }
  
  const response = await client.chat.completions.create({
    model: 'deepseek-reasoner',
    messages: [{ role: 'user', content: problem }]
  });
  
  const result = {
    reasoning: response.choices[0].message.reasoning_content,
    answer: response.choices[0].message.content
  };
  
  reasoningCache.set(key, result);
  return result;
}
```

## Error Handling

### Common Errors
```javascript
try {
  const response = await client.chat.completions.create({
    model: 'deepseek-reasoner',
    messages: messages
  });
  
  return {
    reasoning: response.choices[0].message.reasoning_content,
    answer: response.choices[0].message.content
  };
} catch (error) {
  if (error.status === 400) {
    // Check if reasoning_content was included in messages
    console.error('Invalid request - check message format');
  } else if (error.status === 413) {
    console.error('Request too large - reduce max_tokens or input length');
  } else if (error.status === 429) {
    console.error('Rate limit exceeded - implement backoff');
  }
  throw error;
}
```

### Validation Helper
```javascript
function validateReasonerMessages(messages) {
  for (const message of messages) {
    if (message.reasoning_content) {
      throw new Error(
        'reasoning_content field found in input messages. ' +
        'This field should only be in responses, not requests.'
      );
    }
  }
  return true;
}
```

## Integration Examples

### Educational Platform
```javascript
class MathTutor {
  constructor() {
    this.client = new OpenAI({
      apiKey: 'sk-90e0dd863b8c4e0d879a02851a0ee194',
      baseURL: 'https://api.deepseek.com'
    });
  }

  async solveProblem(problem, studentLevel = 'high-school') {
    const prompt = `
    As a math tutor for ${studentLevel} students, solve this problem:
    ${problem}
    
    Explain each step clearly and check your work.
    `;

    const response = await this.client.chat.completions.create({
      model: 'deepseek-reasoner',
      messages: [{ role: 'user', content: prompt }]
    });

    return {
      reasoning: response.choices[0].message.reasoning_content,
      solution: response.choices[0].message.content,
      usage: response.usage
    };
  }
}
```

### Code Review Assistant
```javascript
class CodeReviewer {
  async analyzeCode(code, language = 'javascript') {
    const prompt = `
    Review this ${language} code for:
    1. Correctness
    2. Performance issues
    3. Best practices
    4. Security concerns
    
    Code:
    ${code}
    
    Provide detailed reasoning for each issue found.
    `;

    const response = await client.chat.completions.create({
      model: 'deepseek-reasoner',
      messages: [{ role: 'user', content: prompt }]
    });

    return {
      analysis: response.choices[0].message.reasoning_content,
      recommendations: response.choices[0].message.content
    };
  }
}
```

## Troubleshooting

### Common Issues

1. **Missing reasoning_content**: Ensure you're using `deepseek-reasoner` model
2. **400 Error**: Check that `reasoning_content` is not in input messages
3. **Slow responses**: Reasoning takes time - consider streaming for UX
4. **High token usage**: Reasoning is verbose - monitor and optimize prompts

### Debug Helper
```javascript
function debugReasonerResponse(response) {
  console.log('Model:', response.model);
  console.log('Reasoning length:', response.choices[0].message.reasoning_content?.length || 0);
  console.log('Answer length:', response.choices[0].message.content?.length || 0);
  console.log('Total tokens:', response.usage.total_tokens);
  console.log('Finish reason:', response.choices[0].finish_reason);
}
```

---

*For simpler conversational tasks, consider using the [deepseek-chat](deepseek-chat.md) model for better speed and cost efficiency.*