/**
 * Reasoning Example with DeepSeek-Reasoner
 * 
 * This example demonstrates advanced reasoning capabilities using the deepseek-reasoner model.
 * Shows chain-of-thought processing, mathematical problem solving, and logical reasoning.
 */

import OpenAI from 'openai';

// Initialize DeepSeek client with hardcoded API key
const client = new OpenAI({
  apiKey: 'sk-90e0dd863b8c4e0d879a02851a0ee194',
  baseURL: 'https://api.deepseek.com'
});

/**
 * Basic reasoning example
 */
async function basicReasoning() {
  console.log('🧠 Basic Reasoning Example\n');

  try {
    const response = await client.chat.completions.create({
      model: 'deepseek-reasoner',
      messages: [{
        role: 'user',
        content: 'If a train travels 120 kilometers in 2 hours, what is its average speed?'
      }],
      max_tokens: 4000
    });

    const reasoning = response.choices[0].message.reasoning_content;
    const answer = response.choices[0].message.content;

    console.log('🤔 Reasoning Process:');
    console.log(reasoning);
    console.log('\n💡 Final Answer:');
    console.log(answer);
    console.log('\n📊 Usage:', response.usage);
    
  } catch (error) {
    console.error('❌ Error:', error.message);
  }
}

/**
 * Mathematical problem solving
 */
async function mathematicalReasoning() {
  console.log('\n🔢 Mathematical Problem Solving\n');

  const problems = [
    {
      name: 'Percentage Calculation',
      problem: 'What is 15% of 240?'
    },
    {
      name: 'Compound Interest',
      problem: 'If I invest $1000 at 5% annual compound interest for 3 years, how much will I have?'
    },
    {
      name: 'Geometry Problem',
      problem: 'A rectangular garden is 12 meters long and 8 meters wide. If I want to put a fence around it and the fence costs $15 per meter, what will be the total cost?'
    },
    {
      name: 'Word Problem',
      problem: 'A company has 3 departments: Sales (40 employees), Marketing (25 employees), and Engineering (35 employees). If they need to reduce staff by 20% overall, and each department must reduce by the same percentage, how many employees will each department have after the reduction?'
    }
  ];

  for (const problem of problems) {
    try {
      console.log(`📋 Problem: ${problem.name}`);
      console.log(`❓ Question: ${problem.problem}\n`);

      const response = await client.chat.completions.create({
        model: 'deepseek-reasoner',
        messages: [{
          role: 'user',
          content: `Solve this step by step: ${problem.problem}`
        }],
        max_tokens: 6000
      });

      const reasoning = response.choices[0].message.reasoning_content;
      const answer = response.choices[0].message.content;

      console.log('🧮 Step-by-step reasoning:');
      console.log(reasoning);
      console.log('\n✅ Solution:');
      console.log(answer);
      console.log('\n' + '═'.repeat(60) + '\n');

      // Small delay between requests
      await new Promise(resolve => setTimeout(resolve, 1500));
      
    } catch (error) {
      console.error(`❌ Error in ${problem.name}:`, error.message);
    }
  }
}

/**
 * Logical reasoning examples
 */
async function logicalReasoning() {
  console.log('\n🎯 Logical Reasoning Examples\n');

  const logicProblems = [
    {
      name: 'Syllogism',
      problem: 'All cats are mammals. All mammals are animals. Fluffy is a cat. Based on these statements, what can we conclude about Fluffy?'
    },
    {
      name: 'Number Comparison',
      problem: '9.11 and 9.8, which is greater? Explain your reasoning.'
    },
    {
      name: 'Logic Puzzle',
      problem: 'There are three boxes: one contains only apples, one contains only oranges, and one contains both apples and oranges. All boxes are labeled incorrectly. You can pick one fruit from one box. How can you correctly label all three boxes?'
    },
    {
      name: 'Deductive Reasoning',
      problem: 'If it rains, then the ground gets wet. The ground is wet. Can we conclude that it rained? Explain why or why not.'
    }
  ];

  for (const problem of logicProblems) {
    try {
      console.log(`🎲 Logic Problem: ${problem.name}`);
      console.log(`🤔 Challenge: ${problem.problem}\n`);

      const response = await client.chat.completions.create({
        model: 'deepseek-reasoner',
        messages: [{
          role: 'user',
          content: problem.problem
        }],
        max_tokens: 5000
      });

      const reasoning = response.choices[0].message.reasoning_content;
      const answer = response.choices[0].message.content;

      console.log('🧠 Logical reasoning:');
      console.log(reasoning);
      console.log('\n🎯 Conclusion:');
      console.log(answer);
      console.log('\n' + '─'.repeat(50) + '\n');

      // Small delay between requests
      await new Promise(resolve => setTimeout(resolve, 1500));
      
    } catch (error) {
      console.error(`❌ Error in ${problem.name}:`, error.message);
    }
  }
}

/**
 * Code analysis and debugging
 */
async function codeAnalysis() {
  console.log('\n💻 Code Analysis and Debugging\n');

  const codeProblems = [
    {
      name: 'Algorithm Analysis',
      code: `def mystery_function(n):
    if n <= 1:
        return n
    return mystery_function(n-1) + mystery_function(n-2)`,
      question: 'What does this Python function do? What is its time complexity? Can it be optimized?'
    },
    {
      name: 'Bug Detection',
      code: `function calculateAverage(numbers) {
    let sum = 0;
    for (let i = 0; i <= numbers.length; i++) {
        sum += numbers[i];
    }
    return sum / numbers.length;
}`,
      question: 'Find and explain the bug in this JavaScript function. How would you fix it?'
    },
    {
      name: 'Performance Analysis',
      code: `SELECT * FROM users 
WHERE age > 18 
AND city = 'New York' 
AND status = 'active'
ORDER BY created_at DESC`,
      question: 'Analyze this SQL query for performance issues and suggest optimizations.'
    }
  ];

  for (const problem of codeProblems) {
    try {
      console.log(`🔍 Analysis: ${problem.name}`);
      console.log(`📝 Code:\n${problem.code}`);
      console.log(`❓ Question: ${problem.question}\n`);

      const response = await client.chat.completions.create({
        model: 'deepseek-reasoner',
        messages: [{
          role: 'user',
          content: `Analyze this code:\n\n${problem.code}\n\n${problem.question}`
        }],
        max_tokens: 6000
      });

      const reasoning = response.choices[0].message.reasoning_content;
      const answer = response.choices[0].message.content;

      console.log('🔬 Detailed analysis:');
      console.log(reasoning);
      console.log('\n📋 Summary and recommendations:');
      console.log(answer);
      console.log('\n' + '═'.repeat(60) + '\n');

      // Small delay between requests
      await new Promise(resolve => setTimeout(resolve, 1500));
      
    } catch (error) {
      console.error(`❌ Error in ${problem.name}:`, error.message);
    }
  }
}

/**
 * Streaming reasoning example
 */
async function streamingReasoning() {
  console.log('\n🌊 Streaming Reasoning Example\n');

  try {
    const problem = `A farmer has 17 sheep. All but 9 die. How many sheep are left?`;
    
    console.log(`🐑 Problem: ${problem}`);
    console.log('\n🧠 Reasoning process (streaming):');

    const stream = await client.chat.completions.create({
      model: 'deepseek-reasoner',
      messages: [{
        role: 'user',
        content: problem
      }],
      stream: true,
      max_tokens: 4000
    });

    let reasoning = '';
    let answer = '';
    let isReasoningPhase = true;

    for await (const chunk of stream) {
      const delta = chunk.choices[0]?.delta;
      
      if (delta?.reasoning_content) {
        reasoning += delta.reasoning_content;
        process.stdout.write(delta.reasoning_content);
      }
      
      if (delta?.content) {
        if (isReasoningPhase) {
          console.log('\n\n💡 Final answer:');
          isReasoningPhase = false;
        }
        answer += delta.content;
        process.stdout.write(delta.content);
      }
    }

    console.log('\n\n📊 Complete reasoning captured:', reasoning.length, 'characters');
    console.log('📝 Final answer captured:', answer.length, 'characters');
    
  } catch (error) {
    console.error('❌ Error:', error.message);
  }
}

/**
 * Multi-turn reasoning conversation
 */
async function multiTurnReasoning() {
  console.log('\n🔄 Multi-turn Reasoning Conversation\n');

  let messages = [];
  
  const conversation = [
    'What is 25% of 80?',
    'Now add 15 to that result.',
    'If I divide the current result by 5, what do I get?',
    'Is this final number greater than 7?'
  ];

  try {
    for (let i = 0; i < conversation.length; i++) {
      const question = conversation[i];
      
      // Add user question
      messages.push({ role: 'user', content: question });
      
      console.log(`👤 Question ${i + 1}: ${question}`);

      const response = await client.chat.completions.create({
        model: 'deepseek-reasoner',
        messages: messages,
        max_tokens: 4000
      });

      const reasoning = response.choices[0].message.reasoning_content;
      const answer = response.choices[0].message.content;

      console.log('🧠 Reasoning:');
      console.log(reasoning);
      console.log('\n🤖 Answer:');
      console.log(answer);

      // IMPORTANT: Only add the final answer to conversation history
      // Do NOT include reasoning_content in the next request
      messages.push({ role: 'assistant', content: answer });

      console.log('\n' + '─'.repeat(40) + '\n');

      // Small delay between requests
      await new Promise(resolve => setTimeout(resolve, 1500));
    }
    
  } catch (error) {
    console.error('❌ Error:', error.message);
  }
}

/**
 * Decision making and analysis
 */
async function decisionMaking() {
  console.log('\n🤝 Decision Making and Analysis\n');

  const decisions = [
    {
      name: 'Investment Decision',
      scenario: `I have $1000 to invest. I can choose between:
1. Stock A: 8% annual return, low risk
2. Stock B: 15% annual return, high risk  
3. Bonds: 4% annual return, very low risk

I'm 25 years old and planning for retirement. What should I choose and why?`
    },
    {
      name: 'Career Choice',
      scenario: `I have two job offers:
Job A: $80,000 salary, great work-life balance, limited growth potential
Job B: $65,000 salary, demanding hours, high growth potential and learning opportunities

I'm 28 years old, single, and value both money and personal development. Which should I choose?`
    },
    {
      name: 'Business Strategy',
      scenario: `My small business has been profitable for 2 years. I can either:
1. Expand to a second location (requires $50K loan)
2. Invest in online marketing and e-commerce ($20K)
3. Save money and maintain current operations

Current monthly profit is $8K. What factors should I consider and what would you recommend?`
    }
  ];

  for (const decision of decisions) {
    try {
      console.log(`🎯 Decision: ${decision.name}`);
      console.log(`📊 Scenario:\n${decision.scenario}\n`);

      const response = await client.chat.completions.create({
        model: 'deepseek-reasoner',
        messages: [{
          role: 'user',
          content: `Analyze this decision scenario and provide a reasoned recommendation:\n\n${decision.scenario}`
        }],
        max_tokens: 8000
      });

      const reasoning = response.choices[0].message.reasoning_content;
      const answer = response.choices[0].message.content;

      console.log('🔍 Analysis process:');
      console.log(reasoning);
      console.log('\n💼 Recommendation:');
      console.log(answer);
      console.log('\n' + '═'.repeat(60) + '\n');

      // Small delay between requests
      await new Promise(resolve => setTimeout(resolve, 2000));
      
    } catch (error) {
      console.error(`❌ Error in ${decision.name}:`, error.message);
    }
  }
}

/**
 * Reasoning conversation helper class
 */
class ReasoningConversation {
  constructor() {
    this.messages = [];
    this.history = [];
  }

  async ask(question) {
    this.messages.push({ role: 'user', content: question });

    try {
      const response = await client.chat.completions.create({
        model: 'deepseek-reasoner',
        messages: this.messages,
        max_tokens: 6000
      });

      const reasoning = response.choices[0].message.reasoning_content;
      const answer = response.choices[0].message.content;

      // Store the full interaction
      this.history.push({
        question,
        reasoning,
        answer,
        usage: response.usage
      });

      // Only add the final answer to conversation context
      this.messages.push({ role: 'assistant', content: answer });

      return { reasoning, answer, usage: response.usage };
      
    } catch (error) {
      console.error('❌ Error in conversation:', error.message);
      throw error;
    }
  }

  getHistory() {
    return this.history;
  }

  getTotalTokens() {
    return this.history.reduce((total, item) => total + item.usage.total_tokens, 0);
  }

  clear() {
    this.messages = [];
    this.history = [];
  }
}

/**
 * Conversation helper example
 */
async function conversationHelper() {
  console.log('\n💬 Reasoning Conversation Helper Example\n');

  const conversation = new ReasoningConversation();

  const questions = [
    'I need to calculate the area of a circle with radius 5 meters.',
    'Now I want to know how much paint I need if 1 liter covers 10 square meters.',
    'If the paint costs $25 per liter, what will be the total cost?'
  ];

  try {
    for (let i = 0; i < questions.length; i++) {
      console.log(`🗣️ Question ${i + 1}: ${questions[i]}`);
      
      const result = await conversation.ask(questions[i]);
      
      console.log('🧠 Reasoning:');
      console.log(result.reasoning);
      console.log('\n💡 Answer:');
      console.log(result.answer);
      console.log(`\n📊 Tokens used: ${result.usage.total_tokens}`);
      console.log('\n' + '─'.repeat(50) + '\n');

      // Small delay between questions
      await new Promise(resolve => setTimeout(resolve, 1000));
    }

    console.log(`📈 Total conversation tokens: ${conversation.getTotalTokens()}`);
    console.log(`💰 Estimated cost: ${calculateReasoningCost(conversation.getTotalTokens())}`);
    
  } catch (error) {
    console.error('❌ Error:', error.message);
  }
}

/**
 * Main execution function
 */
async function main() {
  console.log('🚀 DeepSeek Reasoning Examples Starting...\n');

  try {
    await basicReasoning();
    await mathematicalReasoning();
    await logicalReasoning();
    await codeAnalysis();
    await streamingReasoning();
    await multiTurnReasoning();
    await decisionMaking();
    await conversationHelper();
    
    console.log('\n✅ All reasoning examples completed successfully!');
    
  } catch (error) {
    console.error('💥 Fatal error:', error.message);
  }
}

/**
 * Utility function to calculate reasoning cost
 */
function calculateReasoningCost(totalTokens) {
  // Approximate cost calculation for deepseek-reasoner
  // Assuming average split between input and output tokens
  const inputTokens = Math.floor(totalTokens * 0.3);
  const outputTokens = Math.floor(totalTokens * 0.7);
  
  const inputCost = inputTokens * (0.55 / 1000000);
  const outputCost = outputTokens * (2.19 / 1000000);
  const totalCost = inputCost + outputCost;
  
  return `$${totalCost.toFixed(6)}`;
}

/**
 * Utility function to analyze reasoning quality
 */
function analyzeReasoning(reasoning, answer) {
  return {
    reasoningLength: reasoning.length,
    answerLength: answer.length,
    reasoningToAnswerRatio: reasoning.length / answer.length,
    hasStepByStep: reasoning.includes('step') || reasoning.includes('Step'),
    hasCalculations: /\d+\s*[+\-*/]\s*\d+/.test(reasoning),
    hasConclusion: reasoning.toLowerCase().includes('therefore') || 
                   reasoning.toLowerCase().includes('conclusion')
  };
}

/**
 * Utility function to validate reasoner messages
 */
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

// Run the examples
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(console.error);
}

export {
  basicReasoning,
  mathematicalReasoning,
  logicalReasoning,
  codeAnalysis,
  streamingReasoning,
  multiTurnReasoning,
  decisionMaking,
  conversationHelper,
  ReasoningConversation,
  calculateReasoningCost,
  analyzeReasoning,
  validateReasonerMessages
};