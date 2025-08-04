#!/usr/bin/env node

/**
 * DeepSeek-Reasoner Brain System
 * Main entry point for the AI agent system
 * Made by @Lucariolucario55 on Telegram
 */

import express from 'express';
import { createServer } from 'http';
import { Server } from 'socket.io';
import cors from 'cors';
import helmet from 'helmet';
import compression from 'compression';
import morgan from 'morgan';
import dotenv from 'dotenv';
import chalk from 'chalk';
import ora from 'ora';
import { exec, execFile } from 'child_process';
import fs from 'fs';
import path from 'path';

// Import core systems
import { DeepSeekReasonerBrain } from './core/DeepSeekReasonerBrain.js';
import { PersonaSystem } from './core/PersonaSystem.js';
import { MemoryStore } from './core/MemoryStore.js';
import { ToolManager } from './core/ToolManager.js';
import { StreamingManager } from './core/StreamingManager.js';
import { ConversationManager } from './core/ConversationManager.js';
import { ThoughtStorage } from './core/ThoughtStorage.js';
import { WebScraperTool } from './tools/WebScraperTool.js';
import { QwenEmbeddingTool } from './tools/QwenEmbeddingTool.js';
import { Logger } from './utils/Logger.js';

// Load environment variables
dotenv.config();

class DeepSeekReasonerServer {
    constructor() {
        this.app = express();
        this.server = createServer(this.app);
        this.io = new Server(this.server, {
            cors: {
                origin: "*",
                methods: ["GET", "POST"]
            }
        });
        
        this.port = process.env.PORT || 3000;
        this.brain = null;
        this.persona = null;
        this.memory = null;
        this.tools = null;
        this.streaming = null;
        this.conversation = null;
        this.thoughts = null;
        this.logger = new Logger();
        
        this.setupMiddleware();
        this.setupRoutes();
        this.setupWebSocket();
        this.initializeSystems();
    }
    
    setupMiddleware() {
        // Security middleware
        this.app.use(helmet());
        this.app.use(cors());
        this.app.use(compression());
        this.app.use(morgan('combined'));
        
        // Body parsing
        this.app.use(express.json({ limit: '50mb' }));
        this.app.use(express.urlencoded({ extended: true, limit: '50mb' }));
        
        // Static files
        this.app.use(express.static('public'));
    }
    
    setupRoutes() {
        // Health check
        this.app.get('/health', (req, res) => {
            res.json({
                status: 'healthy',
                timestamp: new Date().toISOString(),
                brain: this.brain ? 'active' : 'inactive',
                persona: this.persona ? 'loaded' : 'not loaded'
            });
        });
        
        // Brain status
        this.app.get('/brain/status', (req, res) => {
            if (!this.brain) {
                return res.status(503).json({ error: 'Brain not initialized' });
            }
            res.json(this.brain.getStatus());
        });
        
        // Chat endpoint
        this.app.post('/chat', async (req, res) => {
            try {
                const { message, persona = 'DEANNA', stream = false } = req.body;
                
                if (!message) {
                    return res.status(400).json({ error: 'Message is required' });
                }
                
                if (stream) {
                    // Set up streaming response
                    res.writeHead(200, {
                        'Content-Type': 'text/plain',
                        'Transfer-Encoding': 'chunked'
                    });
                    
                    const streamResponse = await this.brain.chatWithStreaming(message, persona);
                    streamResponse.on('data', (chunk) => {
                        res.write(chunk);
                    });
                    
                    streamResponse.on('end', () => {
                        res.end();
                    });
                } else {
                    // Regular response
                    const response = await this.brain.chat(message, persona);
                    res.json(response);
                }
            } catch (error) {
                this.logger.error('Chat error:', error);
                res.status(500).json({ error: error.message });
            }
        });
        
        // Tool calling endpoint
        this.app.post('/tools/call', async (req, res) => {
            try {
                const { tool, params } = req.body;
                const result = await this.tools.callTool(tool, params);
                res.json(result);
            } catch (error) {
                this.logger.error('Tool calling error:', error);
                res.status(500).json({ error: error.message });
            }
        });
        
        // Memory operations
        this.app.post('/memory/store', async (req, res) => {
            try {
                const { content, category, tags, importance } = req.body;
                const result = await this.memory.store(content, category, tags, importance);
                res.json(result);
            } catch (error) {
                this.logger.error('Memory store error:', error);
                res.status(500).json({ error: error.message });
            }
        });
        
        this.app.get('/memory/search', async (req, res) => {
            try {
                const { query, category, tags, limit } = req.query;
                const result = await this.memory.search(query, category, tags, limit);
                res.json(result);
            } catch (error) {
                this.logger.error('Memory search error:', error);
                res.status(500).json({ error: error.message });
            }
        });
        
        // Web scraping endpoint
        this.app.post('/scrape', async (req, res) => {
            try {
                const { url, selectors, config } = req.body;
                const result = await this.tools.getTool('web_scraper').scrape(url, selectors, config);
                res.json(result);
            } catch (error) {
                this.logger.error('Scraping error:', error);
                res.status(500).json({ error: error.message });
            }
        });
        
        // Embedding endpoint
        this.app.post('/embed', async (req, res) => {
            try {
                const { text, model = 'qwen' } = req.body;
                const result = await this.tools.getTool('qwen_embedding').embed(text, model);
                res.json(result);
            } catch (error) {
                this.logger.error('Embedding error:', error);
                res.status(500).json({ error: error.message });
            }
        });
        
        // Reasoning endpoint
        this.app.post('/reason', async (req, res) => {
            try {
                const { question, context, persona = 'DEANNA' } = req.body;
                const result = await this.brain.reason(question, context, persona);
                res.json(result);
            } catch (error) {
                this.logger.error('Reasoning error:', error);
                res.status(500).json({ error: error.message });
            }
        });
        
        // FIM completion endpoint
        this.app.post('/fim', async (req, res) => {
            try {
                const { prefix, suffix, model = 'deepseek-chat' } = req.body;
                const result = await this.brain.fimCompletion(prefix, suffix, model);
                res.json(result);
            } catch (error) {
                this.logger.error('FIM completion error:', error);
                res.status(500).json({ error: error.message });
            }
        });
        
        // Prefix completion endpoint
        this.app.post('/prefix', async (req, res) => {
            try {
                const { text, model = 'deepseek-chat' } = req.body;
                const result = await this.brain.prefixCompletion(text, model);
                res.json(result);
            } catch (error) {
                this.logger.error('Prefix completion error:', error);
                res.status(500).json({ error: error.message });
            }
        });

        // CLI command execution endpoint
        this.app.post('/cli/run', (req, res) => {
            const { command } = req.body;
            if (!command) {
                return res.status(400).json({ error: 'Command is required' });
            }

            const runner = path.join(process.cwd(), 'tools', 'cli_runner');
            const execCallback = (error, stdout, stderr) => {
                if (error) {
                    return res.status(500).json({ error: stderr || error.message });
                }
                res.json({ output: stdout });
            };

            if (fs.existsSync(runner)) {
                execFile(runner, [command], execCallback);
            } else {
                exec(command, execCallback);
            }
        });
    }
    
    setupWebSocket() {
        this.io.on('connection', (socket) => {
            this.logger.info(`Client connected: ${socket.id}`);
            
            // Handle chat messages
            socket.on('chat', async (data) => {
                try {
                    const { message, persona = 'DEANNA' } = data;
                    const response = await this.brain.chat(message, persona);
                    socket.emit('chat_response', response);
                } catch (error) {
                    this.logger.error('WebSocket chat error:', error);
                    socket.emit('error', { error: error.message });
                }
            });
            
            // Handle streaming chat
            socket.on('chat_stream', async (data) => {
                try {
                    const { message, persona = 'DEANNA' } = data;
                    const stream = await this.brain.chatWithStreaming(message, persona);
                    
                    stream.on('data', (chunk) => {
                        socket.emit('stream_chunk', { data: chunk.toString() });
                    });
                    
                    stream.on('end', () => {
                        socket.emit('stream_end');
                    });
                } catch (error) {
                    this.logger.error('WebSocket streaming error:', error);
                    socket.emit('error', { error: error.message });
                }
            });
            
            // Handle tool calls
            socket.on('tool_call', async (data) => {
                try {
                    const { tool, params } = data;
                    const result = await this.tools.callTool(tool, params);
                    socket.emit('tool_result', result);
                } catch (error) {
                    this.logger.error('WebSocket tool call error:', error);
                    socket.emit('error', { error: error.message });
                }
            });
            
            socket.on('disconnect', () => {
                this.logger.info(`Client disconnected: ${socket.id}`);
            });
        });
    }
    
    async initializeSystems() {
        const spinner = ora('Initializing DeepSeek-Reasoner Brain System...').start();
        
        try {
            // Initialize core systems
            this.logger.info('Initializing core systems...');
            
            // Initialize memory store
            this.memory = new MemoryStore();
            await this.memory.initialize();
            spinner.text = 'Memory store initialized';
            
            // Initialize persona system
            this.persona = new PersonaSystem();
            await this.persona.loadPersona('DEANNA');
            spinner.text = 'Persona system initialized';
            
            // Initialize tool manager
            this.tools = new ToolManager();
            await this.tools.initialize();
            spinner.text = 'Tool manager initialized';
            
            // Initialize streaming manager
            this.streaming = new StreamingManager();
            await this.streaming.initialize();
            spinner.text = 'Streaming manager initialized';
            
            // Initialize conversation manager
            this.conversation = new ConversationManager();
            await this.conversation.initialize();
            spinner.text = 'Conversation manager initialized';
            
            // Initialize thought storage
            this.thoughts = new ThoughtStorage();
            await this.thoughts.initialize();
            spinner.text = 'Thought storage initialized';
            
            // Initialize the main brain
            this.brain = new DeepSeekReasonerBrain({
                memory: this.memory,
                persona: this.persona,
                tools: this.tools,
                streaming: this.streaming,
                conversation: this.conversation,
                thoughts: this.thoughts
            });
            
            await this.brain.initialize();
            spinner.text = 'DeepSeek-Reasoner brain initialized';
            
            spinner.succeed(chalk.green('DeepSeek-Reasoner Brain System initialized successfully!'));
            
            this.logger.info('All systems initialized and ready');
            
        } catch (error) {
            spinner.fail(chalk.red('Failed to initialize systems'));
            this.logger.error('Initialization error:', error);
            process.exit(1);
        }
    }
    
    start() {
        this.server.listen(this.port, () => {
            this.logger.info(chalk.cyan(`🚀 DeepSeek-Reasoner Brain Server running on port ${this.port}`));
            this.logger.info(chalk.yellow(`📡 WebSocket server available at ws://localhost:${this.port}`));
            this.logger.info(chalk.green(`🧠 Brain system: ${this.brain ? 'ACTIVE' : 'INACTIVE'}`));
            this.logger.info(chalk.magenta(`👤 Default persona: DEANNA`));
            this.logger.info(chalk.blue(`🔧 Available tools: ${this.tools ? this.tools.getToolCount() : 0}`));
            
            console.log(chalk.bold.cyan(`
╔══════════════════════════════════════════════════════════════╗
║                    DeepSeek-Reasoner Brain                   ║
║                     Made by @Lucariolucario55                ║
╠══════════════════════════════════════════════════════════════╣
║  🌐 HTTP Server:    http://localhost:${this.port}                    ║
║  📡 WebSocket:      ws://localhost:${this.port}                      ║
║  🧠 Brain Status:   ${this.brain ? 'ACTIVE' : 'INACTIVE'}                    ║
║  👤 Default Persona: DEANNA                                  ║
║  🔧 Tools Available: ${this.tools ? this.tools.getToolCount() : 0}                        ║
╚══════════════════════════════════════════════════════════════╝
            `));
        });
    }
}

// Start the server
const server = new DeepSeekReasonerServer();
server.start();

// Graceful shutdown
process.on('SIGINT', async () => {
    console.log(chalk.yellow('\n🛑 Shutting down DeepSeek-Reasoner Brain System...'));
    
    if (server.brain) {
        await server.brain.shutdown();
    }
    
    process.exit(0);
});

process.on('SIGTERM', async () => {
    console.log(chalk.yellow('\n🛑 Shutting down DeepSeek-Reasoner Brain System...'));
    
    if (server.brain) {
        await server.brain.shutdown();
    }
    
    process.exit(0);
});

export default server; 