/**
 * DeepSeek API Connection Test Script
 * 
 * Tests connectivity and basic functionality of both DeepSeek models:
 * - deepseek-chat (conversational AI)
 * - deepseek-reasoner (reasoning and chain-of-thought)
 */

import OpenAI from 'openai';

// DeepSeek API Configuration (hardcoded as requested)
const DEEPSEEK_CONFIG = {
  apiKey: 'sk-90e0dd863b8c4e0d879a02851a0ee194',
  baseURL: 'https://api.deepseek.com'
};

// Initialize client
const client = new OpenAI(DEEPSEEK_CONFIG);

/**
 * Test DeepSeek-Chat model
 */
async function testChatModel() {
  console.log('🤖 Testing DeepSeek-Chat Model...\n');

  try {
    const response = await client.chat.completions.create({
      model: 'deepseek-chat',
      messages: [
        { role: 'system', content: 'You are a helpful assistant.' },
        { role: 'user', content: 'Hello! Please respond with a brief greeting and confirm you are working.' }
      ],
      max_tokens: 100,
      temperature: 0.7
    });

    console.log('✅ DeepSeek-Chat Response:');
    console.log(response.choices[0].message.content);
    console.log('\n📊 Usage Stats:');
    console.log(`- Prompt tokens: ${response.usage.prompt_tokens}`);
    console.log(`- Completion tokens: ${response.usage.completion_tokens}`);
    console.log(`- Total tokens: ${response.usage.total_tokens}`);
    
    const cost = calculateCost('deepseek-chat', response.usage.prompt_tokens, response.usage.completion_tokens);
    console.log(`- Estimated cost: $${cost.toFixed(6)}`);
    
    return true;
  } catch (error) {
    console.error('❌ DeepSeek-Chat Error:', error.message);
    return false;
  }
}

/**
 * Test DeepSeek-Reasoner model
 */
async function testReasonerModel() {
  console.log('\n🧠 Testing DeepSeek-Reasoner Model...\n');

  try {
    const response = await client.chat.completions.create({
      model: 'deepseek-reasoner',
      messages: [{
        role: 'user',
        content: 'What is 15% of 200? Please show your reasoning.'
      }],
      max_tokens: 2000
    });

    console.log('✅ DeepSeek-Reasoner Response:');
    
    if (response.choices[0].message.reasoning_content) {
      console.log('🤔 Reasoning Process:');
      console.log(response.choices[0].message.reasoning_content);
      console.log('\n💡 Final Answer:');
    }
    
    console.log(response.choices[0].message.content);
    console.log('\n📊 Usage Stats:');
    console.log(`- Prompt tokens: ${response.usage.prompt_tokens}`);
    console.log(`- Completion tokens: ${response.usage.completion_tokens}`);
    console.log(`- Total tokens: ${response.usage.total_tokens}`);
    
    const cost = calculateCost('deepseek-reasoner', response.usage.prompt_tokens, response.usage.completion_tokens);
    console.log(`- Estimated cost: $${cost.toFixed(6)}`);
    
    return true;
  } catch (error) {
    console.error('❌ DeepSeek-Reasoner Error:', error.message);
    return false;
  }
}

/**
 * Test streaming functionality
 */
async function testStreaming() {
  console.log('\n🌊 Testing Streaming Functionality...\n');

  try {
    console.log('💬 Streaming response from DeepSeek-Chat:');
    
    const stream = await client.chat.completions.create({
      model: 'deepseek-chat',
      messages: [{
        role: 'user',
        content: 'Count from 1 to 5 and explain what streaming is.'
      }],
      stream: true,
      max_tokens: 300
    });

    let fullResponse = '';
    for await (const chunk of stream) {
      const content = chunk.choices[0]?.delta?.content || '';
      if (content) {
        process.stdout.write(content);
        fullResponse += content;
      }
    }

    console.log('\n\n✅ Streaming test completed');
    console.log(`📝 Total response length: ${fullResponse.length} characters`);
    
    return true;
  } catch (error) {
    console.error('❌ Streaming Error:', error.message);
    return false;
  }
}

/**
 * Test error handling
 */
async function testErrorHandling() {
  console.log('\n🛡️ Testing Error Handling...\n');

  // Test with invalid model
  try {
    await client.chat.completions.create({
      model: 'invalid-model',
      messages: [{ role: 'user', content: 'Test' }]
    });
    console.log('❌ Expected error but got success');
    return false;
  } catch (error) {
    console.log('✅ Invalid model error handled correctly:', error.status);
  }

  // Test with excessive tokens
  try {
    await client.chat.completions.create({
      model: 'deepseek-chat',
      messages: [{ role: 'user', content: 'Test' }],
      max_tokens: 100000 // This should fail
    });
    console.log('❌ Expected token limit error but got success');
    return false;
  } catch (error) {
    console.log('✅ Token limit error handled correctly:', error.status);
  }

  return true;
}

/**
 * Test both models with the same task for comparison
 */
async function testModelComparison() {
  console.log('\n⚖️ Model Comparison Test...\n');

  const testPrompt = 'Explain the difference between machine learning and artificial intelligence in 2-3 sentences.';

  console.log('📝 Test prompt:', testPrompt);
  console.log('\n--- DeepSeek-Chat Response ---');

  try {
    const chatResponse = await client.chat.completions.create({
      model: 'deepseek-chat',
      messages: [{ role: 'user', content: testPrompt }],
      max_tokens: 500,
      temperature: 0.5
    });

    console.log(chatResponse.choices[0].message.content);
    console.log(`💰 Cost: $${calculateCost('deepseek-chat', chatResponse.usage.prompt_tokens, chatResponse.usage.completion_tokens).toFixed(6)}`);
    console.log(`⏱️ Tokens: ${chatResponse.usage.total_tokens}`);

  } catch (error) {
    console.error('❌ Chat model failed:', error.message);
  }

  console.log('\n--- DeepSeek-Reasoner Response ---');

  try {
    const reasonerResponse = await client.chat.completions.create({
      model: 'deepseek-reasoner',
      messages: [{ role: 'user', content: testPrompt }],
      max_tokens: 1000
    });

    if (reasonerResponse.choices[0].message.reasoning_content) {
      console.log('🧠 Reasoning:', reasonerResponse.choices[0].message.reasoning_content.substring(0, 200) + '...');
    }
    console.log('💡 Answer:', reasonerResponse.choices[0].message.content);
    console.log(`💰 Cost: $${calculateCost('deepseek-reasoner', reasonerResponse.usage.prompt_tokens, reasonerResponse.usage.completion_tokens).toFixed(6)}`);
    console.log(`⏱️ Tokens: ${reasonerResponse.usage.total_tokens}`);

  } catch (error) {
    console.error('❌ Reasoner model failed:', error.message);
  }

  return true;
}

/**
 * Calculate estimated cost based on model and token usage
 */
function calculateCost(model, inputTokens, outputTokens) {
  const pricing = {
    'deepseek-chat': {
      input: 0.07 / 1000000,
      output: 0.28 / 1000000
    },
    'deepseek-reasoner': {
      input: 0.55 / 1000000,
      output: 2.19 / 1000000
    }
  };

  const modelPricing = pricing[model];
  if (!modelPricing) return 0;

  return (inputTokens * modelPricing.input) + (outputTokens * modelPricing.output);
}

/**
 * Run all tests
 */
async function runAllTests() {
  console.log('🚀 DeepSeek API Connection Tests Starting...\n');
  console.log('🔑 API Key:', DEEPSEEK_CONFIG.apiKey.substring(0, 10) + '...');
  console.log('🌐 Base URL:', DEEPSEEK_CONFIG.baseURL);
  console.log('\n' + '='.repeat(60) + '\n');

  const results = {
    chat: false,
    reasoner: false,
    streaming: false,
    errorHandling: false,
    comparison: false
  };

  try {
    results.chat = await testChatModel();
    await new Promise(resolve => setTimeout(resolve, 1000)); // Rate limiting delay

    results.reasoner = await testReasonerModel();
    await new Promise(resolve => setTimeout(resolve, 1000));

    results.streaming = await testStreaming();
    await new Promise(resolve => setTimeout(resolve, 1000));

    results.errorHandling = await testErrorHandling();
    await new Promise(resolve => setTimeout(resolve, 1000));

    results.comparison = await testModelComparison();

  } catch (error) {
    console.error('💥 Fatal error during tests:', error.message);
  }

  // Summary
  console.log('\n' + '='.repeat(60));
  console.log('📋 Test Results Summary:');
  console.log('='.repeat(60));
  
  const tests = [
    ['DeepSeek-Chat Model', results.chat],
    ['DeepSeek-Reasoner Model', results.reasoner],
    ['Streaming Functionality', results.streaming],
    ['Error Handling', results.errorHandling],
    ['Model Comparison', results.comparison]
  ];

  let passedTests = 0;
  tests.forEach(([name, passed]) => {
    console.log(`${passed ? '✅' : '❌'} ${name}`);
    if (passed) passedTests++;
  });

  console.log('\n📊 Overall Results:');
  console.log(`✅ Passed: ${passedTests}/${tests.length}`);
  console.log(`❌ Failed: ${tests.length - passedTests}/${tests.length}`);
  
  if (passedTests === tests.length) {
    console.log('\n🎉 All tests passed! DeepSeek API is working correctly.');
  } else {
    console.log('\n⚠️ Some tests failed. Check the error messages above.');
  }

  console.log('\n💡 Next Steps:');
  console.log('- Use deepseek-chat for conversations and content generation');
  console.log('- Use deepseek-reasoner for complex reasoning and mathematical problems');
  console.log('- Implement caching to reduce API costs');
  console.log('- Monitor token usage for cost optimization');
}

/**
 * Quick connectivity test
 */
async function quickTest() {
  console.log('⚡ Quick Connectivity Test...\n');

  try {
    const response = await client.chat.completions.create({
      model: 'deepseek-chat',
      messages: [{ role: 'user', content: 'Hi' }],
      max_tokens: 10
    });

    console.log('✅ Connection successful!');
    console.log('🤖 Response:', response.choices[0].message.content);
    return true;
  } catch (error) {
    console.error('❌ Connection failed:', error.message);
    return false;
  }
}

// Main execution
if (import.meta.url === `file://${process.argv[1]}`) {
  const testType = process.argv[2] || 'full';
  
  if (testType === 'quick') {
    quickTest().catch(console.error);
  } else {
    runAllTests().catch(console.error);
  }
}

export {
  testChatModel,
  testReasonerModel,
  testStreaming,
  testErrorHandling,
  testModelComparison,
  calculateCost,
  quickTest,
  runAllTests
};