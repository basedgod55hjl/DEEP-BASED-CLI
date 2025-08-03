/**
 * Basic Chat Example with DeepSeek-Chat
 * 
 * This example demonstrates simple conversational AI using the deepseek-chat model.
 * Perfect for general conversations, content generation, and quick responses.
 */

import OpenAI from 'openai';

// Initialize DeepSeek client with hardcoded API key
const client = new OpenAI({
  apiKey: 'sk-90e0dd863b8c4e0d879a02851a0ee194',
  baseURL: 'https://api.deepseek.com'
});

/**
 * Simple chat completion
 */
async function basicChat() {
  console.log('🤖 Basic Chat Example\n');

  try {
    const response = await client.chat.completions.create({
      model: 'deepseek-chat',
      messages: [
        { role: 'system', content: 'You are a helpful and friendly assistant.' },
        { role: 'user', content: 'Hello! Can you tell me about artificial intelligence?' }
      ],
      max_tokens: 1500,
      temperature: 0.7
    });

    console.log('💬 Response:', response.choices[0].message.content);
    console.log('\n📊 Usage:', response.usage);
    
  } catch (error) {
    console.error('❌ Error:', error.message);
  }
}

/**
 * Multi-turn conversation
 */
async function multiTurnChat() {
  console.log('\n🔄 Multi-turn Conversation Example\n');

  const messages = [
    { role: 'system', content: 'You are a coding assistant.' }
  ];

  const questions = [
    'What is JavaScript?',
    'How do I create a function in JavaScript?',
    'Can you show me an example of an arrow function?',
    'What are the benefits of arrow functions?'
  ];

  try {
    for (const question of questions) {
      // Add user question
      messages.push({ role: 'user', content: question });

      console.log(`👤 User: ${question}`);

      const response = await client.chat.completions.create({
        model: 'deepseek-chat',
        messages: messages,
        max_tokens: 1000,
        temperature: 0.5
      });

      const answer = response.choices[0].message.content;
      console.log(`🤖 Assistant: ${answer}\n`);

      // Add assistant response to conversation history
      messages.push({ role: 'assistant', content: answer });

      // Small delay between requests
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  } catch (error) {
    console.error('❌ Error:', error.message);
  }
}

/**
 * Streaming chat response
 */
async function streamingChat() {
  console.log('\n🌊 Streaming Response Example\n');

  try {
    console.log('👤 User: Tell me a creative story about a robot learning to paint');
    console.log('🤖 Assistant: ');

    const stream = await client.chat.completions.create({
      model: 'deepseek-chat',
      messages: [{
        role: 'user',
        content: 'Tell me a creative story about a robot learning to paint. Make it engaging and about 200 words.'
      }],
      stream: true,
      max_tokens: 2000,
      temperature: 0.8
    });

    let fullResponse = '';
    for await (const chunk of stream) {
      const content = chunk.choices[0]?.delta?.content || '';
      if (content) {
        process.stdout.write(content);
        fullResponse += content;
      }
    }

    console.log('\n\n📝 Full response length:', fullResponse.length, 'characters');
    
  } catch (error) {
    console.error('❌ Error:', error.message);
  }
}

/**
 * Content generation examples
 */
async function contentGeneration() {
  console.log('\n✍️ Content Generation Examples\n');

  const tasks = [
    {
      name: 'Blog Post Outline',
      prompt: 'Create an outline for a blog post about the benefits of remote work',
      temperature: 0.6
    },
    {
      name: 'Product Description',
      prompt: 'Write a compelling product description for a smart home security camera',
      temperature: 0.7
    },
    {
      name: 'Email Template',
      prompt: 'Write a professional email template for following up with a potential client',
      temperature: 0.5
    }
  ];

  for (const task of tasks) {
    try {
      console.log(`📋 Task: ${task.name}`);
      console.log(`💭 Prompt: ${task.prompt}\n`);

      const response = await client.chat.completions.create({
        model: 'deepseek-chat',
        messages: [
          { role: 'system', content: 'You are a professional content writer.' },
          { role: 'user', content: task.prompt }
        ],
        max_tokens: 1500,
        temperature: task.temperature
      });

      console.log('📝 Generated Content:');
      console.log(response.choices[0].message.content);
      console.log('\n' + '─'.repeat(50) + '\n');

      // Small delay between requests
      await new Promise(resolve => setTimeout(resolve, 1000));
      
    } catch (error) {
      console.error(`❌ Error in ${task.name}:`, error.message);
    }
  }
}

/**
 * Different temperature examples
 */
async function temperatureExamples() {
  console.log('\n🌡️ Temperature Comparison Examples\n');

  const prompt = 'Write a short poem about the ocean';
  const temperatures = [0.1, 0.5, 1.0, 1.5];

  for (const temperature of temperatures) {
    try {
      console.log(`🌡️ Temperature: ${temperature}`);

      const response = await client.chat.completions.create({
        model: 'deepseek-chat',
        messages: [
          { role: 'system', content: 'You are a creative poet.' },
          { role: 'user', content: prompt }
        ],
        max_tokens: 500,
        temperature: temperature
      });

      console.log('🎭 Generated Poem:');
      console.log(response.choices[0].message.content);
      console.log('\n' + '─'.repeat(30) + '\n');

      // Small delay between requests
      await new Promise(resolve => setTimeout(resolve, 1000));
      
    } catch (error) {
      console.error(`❌ Error at temperature ${temperature}:`, error.message);
    }
  }
}

/**
 * Error handling example
 */
async function errorHandlingExample() {
  console.log('\n🛡️ Error Handling Example\n');

  // Example with invalid parameters
  try {
    const response = await client.chat.completions.create({
      model: 'deepseek-chat',
      messages: [
        { role: 'user', content: 'Test message' }
      ],
      max_tokens: 100000, // This will likely cause an error
      temperature: 3.0 // This might cause an error
    });

    console.log('Response:', response.choices[0].message.content);
    
  } catch (error) {
    console.log('✅ Caught expected error:');
    console.log('Status:', error.status);
    console.log('Message:', error.message);
    console.log('Type:', error.type);
  }

  // Example with proper error handling and retry
  let retries = 3;
  while (retries > 0) {
    try {
      console.log(`\n🔄 Attempting request (${4 - retries}/3)...`);
      
      const response = await client.chat.completions.create({
        model: 'deepseek-chat',
        messages: [
          { role: 'user', content: 'What is the capital of France?' }
        ],
        max_tokens: 100,
        temperature: 0.3
      });

      console.log('✅ Success:', response.choices[0].message.content);
      break;
      
    } catch (error) {
      retries--;
      console.log(`❌ Attempt failed: ${error.message}`);
      
      if (retries > 0) {
        console.log(`⏳ Waiting before retry... (${retries} attempts left)`);
        await new Promise(resolve => setTimeout(resolve, 2000));
      } else {
        console.log('💥 All retries exhausted');
      }
    }
  }
}

/**
 * Main execution function
 */
async function main() {
  console.log('🚀 DeepSeek Chat Examples Starting...\n');

  try {
    await basicChat();
    await multiTurnChat();
    await streamingChat();
    await contentGeneration();
    await temperatureExamples();
    await errorHandlingExample();
    
    console.log('\n✅ All examples completed successfully!');
    
  } catch (error) {
    console.error('💥 Fatal error:', error.message);
  }
}

/**
 * Utility function to estimate token count
 */
function estimateTokens(text) {
  // Rough approximation: 1 token ≈ 4 characters
  return Math.ceil(text.length / 4);
}

/**
 * Utility function to format response with metadata
 */
function formatResponse(response) {
  return {
    content: response.choices[0].message.content,
    model: response.model,
    usage: response.usage,
    estimatedCost: calculateCost(response.usage, 'deepseek-chat')
  };
}

/**
 * Utility function to calculate approximate cost
 */
function calculateCost(usage, model) {
  const prices = {
    'deepseek-chat': {
      input: 0.07 / 1000000,  // $0.07 per 1M tokens
      output: 0.28 / 1000000  // $0.28 per 1M tokens
    }
  };

  const price = prices[model];
  if (!price) return 'Unknown';

  const inputCost = usage.prompt_tokens * price.input;
  const outputCost = usage.completion_tokens * price.output;
  const totalCost = inputCost + outputCost;

  return `$${totalCost.toFixed(6)}`;
}

// Run the examples
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(console.error);
}

export {
  basicChat,
  multiTurnChat,
  streamingChat,
  contentGeneration,
  temperatureExamples,
  errorHandlingExample,
  estimateTokens,
  formatResponse,
  calculateCost
};