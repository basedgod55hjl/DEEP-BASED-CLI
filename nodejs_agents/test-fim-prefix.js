/**
 * Test script for DeepSeek Node.js agent
 * Tests FIM and prefix completion features
 */

const DeepSeekAgent = require('./deepseek-chat');

async function testFIMCompletion() {
    console.log('\n🔧 Testing FIM Completion...');
    
    const agent = new DeepSeekAgent();
    
    try {
        // Test 1: Simple function completion
        console.log('\n📝 Test 1: Complete function body');
        const result1 = await agent.fimComplete(
            'function add(a, b) {\n    ',
            '\n}'
        );
        console.log('✅ FIM Result:', result1.choices[0].text);
        
        // Test 2: Class method completion
        console.log('\n📝 Test 2: Complete class method');
        const result2 = await agent.fimComplete(
            'class Calculator {\n    constructor() {\n        this.result = 0;\n    }\n    \n    multiply(a, b) {\n        ',
            '\n        return this.result;\n    }\n}'
        );
        console.log('✅ FIM Result:', result2.choices[0].text);
        
    } catch (error) {
        console.error('❌ FIM test failed:', error.message);
    }
}

async function testPrefixCompletion() {
    console.log('\n\n🔧 Testing Prefix Completion...');
    
    const agent = new DeepSeekAgent();
    
    try {
        // Test 1: Text completion
        console.log('\n📝 Test 1: Complete text');
        const result1 = await agent.prefixComplete(
            'The advantages of using Node.js for backend development include'
        );
        console.log('✅ Prefix Result:', result1.choices[0].message.content);
        
        // Test 2: Code completion
        console.log('\n📝 Test 2: Complete code');
        const result2 = await agent.prefixComplete(
            'async function fetchData(url) {\n    try {\n        const response = await fetch(url);',
            { 
                systemPrompt: 'Complete the JavaScript async function',
                model: 'deepseek-coder'
            }
        );
        console.log('✅ Prefix Result:', result2.choices[0].message.content);
        
    } catch (error) {
        console.error('❌ Prefix test failed:', error.message);
    }
}

async function testStreamCompletion() {
    console.log('\n\n🔧 Testing Stream Completion...');
    
    const agent = new DeepSeekAgent();
    
    try {
        console.log('\n📝 Streaming response:');
        process.stdout.write('Stream: ');
        
        for await (const chunk of agent.streamChat([
            { role: 'user', content: 'Write a haiku about coding' }
        ])) {
            process.stdout.write(chunk);
        }
        console.log('\n✅ Stream completed');
        
    } catch (error) {
        console.error('❌ Stream test failed:', error.message);
    }
}

async function runAllTests() {
    console.log('🚀 DeepSeek Node.js Agent Test Suite');
    console.log('=' . repeat(50));
    
    try {
        await testFIMCompletion();
        await testPrefixCompletion();
        await testStreamCompletion();
        
        console.log('\n' + '=' . repeat(50));
        console.log('✅ All tests completed!');
    } catch (error) {
        console.error('\n❌ Test suite failed:', error);
    }
}

// Run tests
runAllTests();