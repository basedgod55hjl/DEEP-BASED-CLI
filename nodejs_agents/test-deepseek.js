/**
 * Test script for DeepSeek Node.js Agent
 * Tests all functionality with the new API key
 */

const DeepSeekAgent = require('./deepseek-chat.js');

async function testDeepSeekAgent() {
  console.log('🚀 Testing DeepSeek Node.js Agent...\n');
  
  const agent = new DeepSeekAgent();
  
  try {
    // Test 1: Chat Completion
    console.log('=== Test 1: Chat Completion ===');
    const chatResponse = await agent.chat([
      { role: 'system', content: 'You are a helpful assistant.' },
      { role: 'user', content: 'What is 2 + 2?' }
    ]);
    console.log('✅ Chat Response:', chatResponse.choices[0].message.content);
    
    // Test 2: FIM Completion
    console.log('\n=== Test 2: FIM Completion ===');
    const fimResponse = await agent.fimComplete(
      'def hello_world():\n    print("Hello, ',
      '!")\n\nhello_world()'
    );
    console.log('✅ FIM Response:', fimResponse.choices[0].text);
    
    // Test 3: Prefix Completion
    console.log('\n=== Test 3: Prefix Completion ===');
    const prefixResponse = await agent.prefixComplete(
      'The quick brown fox'
    );
    console.log('✅ Prefix Response:', prefixResponse.choices[0].message.content);
    
    // Test 4: Stream Chat
    console.log('\n=== Test 4: Stream Chat ===');
    console.log('Streaming: ');
    for await (const chunk of agent.streamChat([
      { role: 'user', content: 'Say hello in one word' }
    ])) {
      process.stdout.write(chunk);
    }
    console.log('\n✅ Stream completed');
    
    console.log('\n🎉 All tests passed! Node.js agent is working correctly.');
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
  }
}

// Run tests
testDeepSeekAgent(); 