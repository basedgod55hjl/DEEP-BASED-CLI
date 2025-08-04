/**
 * DeepSeek-Reasoner Brain System
 * Main brain that coordinates reasoning, tool calling, and multi-agent communication
 * Made by @Lucariolucario55 on Telegram
 */

import OpenAI from 'openai';
import { EventEmitter } from 'events';
import { Readable } from 'stream';
import chalk from 'chalk';
import { v4 as uuidv4 } from 'uuid';

export class DeepSeekReasonerBrain extends EventEmitter {
    constructor(config) {
        super();
        
        this.config = {
            deepseekApiKey: process.env.DEEPSEEK_API_KEY || 'sk-90e0dd863b8c4e0d879a02851a0ee194',
            deepseekBaseUrl: 'https://api.deepseek.com',
            defaultPersona: 'DEANNA',
            maxTokens: 4000,
            temperature: 0.7,
            ...config
        };
        
        // Core systems
        this.memory = config.memory;
        this.persona = config.persona;
        this.tools = config.tools;
        this.streaming = config.streaming;
        this.conversation = config.conversation;
        this.thoughts = config.thoughts;
        
        // OpenAI clients for different models
        this.reasonerClient = null;
        this.chatClient = null;
        this.v3Client = null;
        
        // State management
        this.isInitialized = false;
        this.currentPersona = null;
        this.activeConversations = new Map();
        this.thoughtCache = new Map();
        this.reasoningChain = [];
        
        // Initialize OpenAI clients
        this.initializeClients();
    }
    
    initializeClients() {
        // DeepSeek-Reasoner client (main brain)
        this.reasonerClient = new OpenAI({
            apiKey: this.config.deepseekApiKey,
            baseURL: this.config.deepseekBaseUrl,
            dangerouslyAllowBrowser: true
        });
        
        // DeepSeek-Chat client (for dynamic conversation)
        this.chatClient = new OpenAI({
            apiKey: this.config.deepseekApiKey,
            baseURL: this.config.deepseekBaseUrl,
            dangerouslyAllowBrowser: true
        });
        
        // DeepSeek-V3 client (for final output)
        this.v3Client = new OpenAI({
            apiKey: this.config.deepseekApiKey,
            baseURL: this.config.deepseekBaseUrl,
            dangerouslyAllowBrowser: true
        });
    }
    
    async initialize() {
        try {
            console.log(chalk.blue('🧠 Initializing DeepSeek-Reasoner Brain...'));
            
            // Load default persona
            await this.loadPersona(this.config.defaultPersona);
            
            // Initialize conversation context
            await this.conversation.initialize();
            
            // Load cached thoughts
            await this.loadCachedThoughts();
            
            this.isInitialized = true;
            console.log(chalk.green('✅ DeepSeek-Reasoner Brain initialized successfully'));
            
        } catch (error) {
            console.error(chalk.red('❌ Failed to initialize DeepSeek-Reasoner Brain:'), error);
            throw error;
        }
    }
    
    async loadPersona(personaName) {
        try {
            this.currentPersona = await this.persona.getPersona(personaName);
            console.log(chalk.magenta(`👤 Loaded persona: ${personaName}`));
        } catch (error) {
            console.error(chalk.red(`❌ Failed to load persona ${personaName}:`), error);
            throw error;
        }
    }
    
    async loadCachedThoughts() {
        try {
            const cachedThoughts = await this.thoughts.getCachedThoughts();
            cachedThoughts.forEach(thought => {
                this.thoughtCache.set(thought.id, thought);
            });
            console.log(chalk.cyan(`💭 Loaded ${cachedThoughts.length} cached thoughts`));
        } catch (error) {
            console.error(chalk.red('❌ Failed to load cached thoughts:'), error);
        }
    }
    
    async chat(message, persona = null) {
        if (!this.isInitialized) {
            throw new Error('Brain not initialized');
        }
        
        const conversationId = uuidv4();
        const personaToUse = persona || this.config.defaultPersona;
        
        try {
            // Load persona if different from current
            if (personaToUse !== this.currentPersona?.name) {
                await this.loadPersona(personaToUse);
            }
            
            // Start reasoning process
            const reasoningResult = await this.reason(message, null, personaToUse);
            
            // Generate final response using V3
            const finalResponse = await this.generateFinalResponse(message, reasoningResult, personaToUse);
            
            // Store in memory
            await this.memory.store(message, 'conversation', [personaToUse, 'chat'], 1.0);
            await this.memory.store(finalResponse, 'conversation', [personaToUse, 'response'], 1.0);
            
            // Store thoughts for reuse
            await this.storeThoughts(reasoningResult.thoughts, conversationId);
            
            return {
                conversationId,
                message,
                response: finalResponse,
                reasoning: reasoningResult,
                persona: personaToUse,
                timestamp: new Date().toISOString()
            };
            
        } catch (error) {
            console.error(chalk.red('❌ Chat error:'), error);
            throw error;
        }
    }
    
    async chatWithStreaming(message, persona = null) {
        if (!this.isInitialized) {
            throw new Error('Brain not initialized');
        }
        
        const personaToUse = persona || this.config.defaultPersona;
        
        // Create readable stream
        const stream = new Readable({
            read() {}
        });
        
        try {
            // Start reasoning in background
            const reasoningPromise = this.reason(message, null, personaToUse);
            
            // Stream reasoning process
            stream.push(chalk.blue('🧠 Reasoning...\n'));
            
            // Get reasoning result
            const reasoningResult = await reasoningPromise;
            
            // Stream reasoning thoughts
            for (const thought of reasoningResult.thoughts) {
                stream.push(chalk.cyan(`💭 ${thought}\n`));
                await new Promise(resolve => setTimeout(resolve, 100)); // Small delay for readability
            }
            
            // Stream tool calls if any
            if (reasoningResult.toolCalls && reasoningResult.toolCalls.length > 0) {
                stream.push(chalk.yellow('🔧 Using tools...\n'));
                for (const toolCall of reasoningResult.toolCalls) {
                    stream.push(chalk.yellow(`🔧 ${toolCall.tool}: ${toolCall.result}\n`));
                }
            }
            
            // Generate and stream final response
            stream.push(chalk.green('💬 Response:\n'));
            
            const finalResponse = await this.generateFinalResponseWithStreaming(
                message, 
                reasoningResult, 
                personaToUse,
                stream
            );
            
            stream.push(null); // End stream
            
            return stream;
            
        } catch (error) {
            stream.push(chalk.red(`❌ Error: ${error.message}\n`));
            stream.push(null);
            return stream;
        }
    }
    
    async reason(question, context = null, persona = null) {
        const personaToUse = persona || this.config.defaultPersona;
        const reasoningId = uuidv4();
        
        try {
            // Get relevant memories and thoughts
            const memories = await this.memory.search(question, null, [], 5);
            const relevantThoughts = await this.getRelevantThoughts(question);
            
            // Build reasoning context
            const reasoningContext = {
                question,
                context: context || '',
                persona: personaToUse,
                memories: memories.results || [],
                relevantThoughts,
                availableTools: this.tools.getAvailableTools()
            };
            
            // Generate reasoning prompt
            const reasoningPrompt = this.buildReasoningPrompt(reasoningContext);
            
            // Use DeepSeek-Reasoner for chain-of-thought reasoning
            const reasoningResponse = await this.reasonerClient.chat.completions.create({
                model: 'deepseek-reasoner',
                messages: [
                    {
                        role: 'system',
                        content: `You are ${personaToUse}, an advanced AI reasoning system. Think step by step about the question and determine what tools or actions are needed.`
                    },
                    {
                        role: 'user',
                        content: reasoningPrompt
                    }
                ],
                max_tokens: 2000,
                temperature: 0.3
            });
            
            // Extract reasoning content and final answer
            const reasoningContent = reasoningResponse.choices[0].message.reasoning_content;
            const finalAnswer = reasoningResponse.choices[0].message.content;
            
            // Parse reasoning for tool calls
            const toolCalls = await this.parseToolCalls(reasoningContent);
            
            // Execute tool calls if any
            const toolResults = [];
            for (const toolCall of toolCalls) {
                try {
                    const result = await this.tools.callTool(toolCall.tool, toolCall.params);
                    toolResults.push({
                        tool: toolCall.tool,
                        params: toolCall.params,
                        result: result
                    });
                } catch (error) {
                    toolResults.push({
                        tool: toolCall.tool,
                        params: toolCall.params,
                        error: error.message
                    });
                }
            }
            
            // Extract thoughts from reasoning
            const thoughts = this.extractThoughts(reasoningContent);
            
            const reasoningResult = {
                reasoningId,
                question,
                reasoning: reasoningContent,
                finalAnswer,
                toolCalls: toolResults,
                thoughts,
                context: reasoningContext,
                timestamp: new Date().toISOString()
            };
            
            // Store reasoning chain
            this.reasoningChain.push(reasoningResult);
            
            return reasoningResult;
            
        } catch (error) {
            console.error(chalk.red('❌ Reasoning error:'), error);
            throw error;
        }
    }
    
    async generateFinalResponse(message, reasoningResult, persona) {
        try {
            // Build final response prompt
            const finalPrompt = this.buildFinalResponsePrompt(message, reasoningResult, persona);
            
            // Use DeepSeek-V3 for final response
            const response = await this.v3Client.chat.completions.create({
                model: 'deepseek-chat',
                messages: [
                    {
                        role: 'system',
                        content: `You are ${persona}. Provide a clear, helpful, and engaging response based on the reasoning provided.`
                    },
                    {
                        role: 'user',
                        content: finalPrompt
                    }
                ],
                max_tokens: this.config.maxTokens,
                temperature: this.config.temperature
            });
            
            return response.choices[0].message.content;
            
        } catch (error) {
            console.error(chalk.red('❌ Final response generation error:'), error);
            throw error;
        }
    }
    
    async generateFinalResponseWithStreaming(message, reasoningResult, persona, stream) {
        try {
            const finalPrompt = this.buildFinalResponsePrompt(message, reasoningResult, persona);
            
            const response = await this.v3Client.chat.completions.create({
                model: 'deepseek-chat',
                messages: [
                    {
                        role: 'system',
                        content: `You are ${persona}. Provide a clear, helpful, and engaging response based on the reasoning provided.`
                    },
                    {
                        role: 'user',
                        content: finalPrompt
                    }
                ],
                max_tokens: this.config.maxTokens,
                temperature: this.config.temperature,
                stream: true
            });
            
            for await (const chunk of response) {
                const content = chunk.choices[0]?.delta?.content;
                if (content) {
                    stream.push(content);
                }
            }
            
        } catch (error) {
            console.error(chalk.red('❌ Streaming response error:'), error);
            throw error;
        }
    }
    
    async fimCompletion(prefix, suffix, model = 'deepseek-chat') {
        try {
            const client = model === 'deepseek-reasoner' ? this.reasonerClient : this.chatClient;
            
            const response = await client.chat.completions.create({
                model: model,
                messages: [
                    {
                        role: 'user',
                        content: `Complete the following text:\nPrefix: ${prefix}\nSuffix: ${suffix}`
                    }
                ],
                max_tokens: this.config.maxTokens,
                temperature: 0.3
            });
            
            return response.choices[0].message.content;
            
        } catch (error) {
            console.error(chalk.red('❌ FIM completion error:'), error);
            throw error;
        }
    }
    
    async prefixCompletion(text, model = 'deepseek-chat') {
        try {
            const client = model === 'deepseek-reasoner' ? this.reasonerClient : this.chatClient;
            
            const response = await client.chat.completions.create({
                model: model,
                messages: [
                    {
                        role: 'user',
                        content: `Complete the following text: ${text}`
                    }
                ],
                max_tokens: this.config.maxTokens,
                temperature: 0.7
            });
            
            return response.choices[0].message.content;
            
        } catch (error) {
            console.error(chalk.red('❌ Prefix completion error:'), error);
            throw error;
        }
    }
    
    buildReasoningPrompt(context) {
        return `
Question: ${context.question}
Context: ${context.context}
Persona: ${context.persona}

Available Tools: ${context.availableTools.map(t => t.name).join(', ')}

Relevant Memories:
${context.memories.map(m => `- ${m.content}`).join('\n')}

Relevant Thoughts:
${context.relevantThoughts.map(t => `- ${t.content}`).join('\n')}

Please think step by step:
1. Analyze the question and context
2. Determine what information or tools are needed
3. If tools are needed, specify which tools and parameters
4. Provide your reasoning process
5. Give your final answer

Think carefully and be thorough in your reasoning.
        `;
    }
    
    buildFinalResponsePrompt(message, reasoningResult, persona) {
        return `
Original Message: ${message}
Persona: ${persona}

Reasoning Process:
${reasoningResult.reasoning}

Tool Results:
${reasoningResult.toolCalls.map(t => `- ${t.tool}: ${t.result || t.error}`).join('\n')}

Final Answer from Reasoning:
${reasoningResult.finalAnswer}

Please provide a natural, conversational response as ${persona} based on the reasoning above. Make it engaging and helpful.
        `;
    }
    
    async parseToolCalls(reasoningContent) {
        const toolCalls = [];
        
        // Simple parsing - look for tool call patterns
        const toolPattern = /tool:\s*(\w+)\s*params:\s*({[^}]+})/gi;
        let match;
        
        while ((match = toolPattern.exec(reasoningContent)) !== null) {
            try {
                const toolName = match[1];
                const params = JSON.parse(match[2]);
                toolCalls.push({ tool: toolName, params });
            } catch (error) {
                console.warn(chalk.yellow(`⚠️ Failed to parse tool call: ${match[0]}`));
            }
        }
        
        return toolCalls;
    }
    
    extractThoughts(reasoningContent) {
        const thoughts = [];
        
        // Extract thoughts from reasoning content
        const thoughtPattern = /thought:\s*(.+?)(?=\n|$)/gi;
        let match;
        
        while ((match = thoughtPattern.exec(reasoningContent)) !== null) {
            thoughts.push(match[1].trim());
        }
        
        return thoughts;
    }
    
    async getRelevantThoughts(question) {
        try {
            const relevantThoughts = await this.thoughts.searchRelevantThoughts(question, 5);
            return relevantThoughts;
        } catch (error) {
            console.warn(chalk.yellow('⚠️ Failed to get relevant thoughts:'), error);
            return [];
        }
    }
    
    async storeThoughts(thoughts, conversationId) {
        try {
            for (const thought of thoughts) {
                await this.thoughts.storeThought(thought, conversationId);
            }
        } catch (error) {
            console.warn(chalk.yellow('⚠️ Failed to store thoughts:'), error);
        }
    }
    
    getStatus() {
        return {
            initialized: this.isInitialized,
            currentPersona: this.currentPersona?.name,
            activeConversations: this.activeConversations.size,
            cachedThoughts: this.thoughtCache.size,
            reasoningChainLength: this.reasoningChain.length,
            toolsAvailable: this.tools ? this.tools.getToolCount() : 0
        };
    }
    
    async shutdown() {
        try {
            console.log(chalk.yellow('🛑 Shutting down DeepSeek-Reasoner Brain...'));
            
            // Save current state
            await this.saveState();
            
            // Clear active conversations
            this.activeConversations.clear();
            
            // Clear thought cache
            this.thoughtCache.clear();
            
            this.isInitialized = false;
            console.log(chalk.green('✅ DeepSeek-Reasoner Brain shutdown complete'));
            
        } catch (error) {
            console.error(chalk.red('❌ Error during shutdown:'), error);
        }
    }
    
    async saveState() {
        try {
            // Save reasoning chain
            await this.thoughts.saveReasoningChain(this.reasoningChain);
            
            // Save conversation state
            await this.conversation.saveState();
            
        } catch (error) {
            console.error(chalk.red('❌ Error saving state:'), error);
        }
    }
} 