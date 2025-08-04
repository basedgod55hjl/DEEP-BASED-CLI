/**
 * Tool Manager
 * Manages and coordinates all tools including Qwen embedding and web scraper
 * Made by @Lucariolucario55 on Telegram
 */

import { QwenEmbeddingTool } from '../tools/QwenEmbeddingTool.js';
import { WebScraperTool } from '../tools/WebScraperTool.js';
import chalk from 'chalk';

export class ToolManager {
    constructor() {
        this.tools = new Map();
        this.isInitialized = false;
    }
    
    async initialize() {
        try {
            console.log(chalk.blue('🔧 Initializing Tool Manager...'));
            
            // Initialize Qwen embedding tool
            const qwenTool = new QwenEmbeddingTool();
            this.tools.set('qwen_embedding', qwenTool);
            
            // Initialize web scraper tool
            const webScraperTool = new WebScraperTool();
            this.tools.set('web_scraper', webScraperTool);
            
            this.isInitialized = true;
            console.log(chalk.green('✅ Tool Manager initialized'));
            
        } catch (error) {
            console.error(chalk.red('❌ Failed to initialize Tool Manager:'), error);
            throw error;
        }
    }
    
    async callTool(toolName, params) {
        try {
            const tool = this.tools.get(toolName);
            
            if (!tool) {
                throw new Error(`Tool '${toolName}' not found`);
            }
            
            // Call the appropriate method based on tool type
            switch (toolName) {
                case 'qwen_embedding':
                    return await tool.embed_text(params.text);
                case 'web_scraper':
                    return await tool.scrape(params.url, params.selectors, params.config);
                default:
                    throw new Error(`Unknown tool: ${toolName}`);
            }
            
        } catch (error) {
            console.error(chalk.red(`❌ Tool call error for ${toolName}:`), error);
            throw error;
        }
    }
    
    getTool(toolName) {
        return this.tools.get(toolName);
    }
    
    getAvailableTools() {
        return Array.from(this.tools.keys()).map(name => ({
            name,
            description: this.tools.get(name).description
        }));
    }
    
    getToolCount() {
        return this.tools.size;
    }
    
    getStatus() {
        return {
            initialized: this.isInitialized,
            toolCount: this.tools.size,
            tools: Array.from(this.tools.keys())
        };
    }
} 