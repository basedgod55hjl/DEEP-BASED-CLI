/**
 * Thought Storage System
 * Stores and retrieves reasoning thoughts to save tokens
 * Made by @Lucariolucario55 on Telegram
 */

import fs from 'fs-extra';
import path from 'path';
import { v4 as uuidv4 } from 'uuid';
import chalk from 'chalk';

export class ThoughtStorage {
    constructor() {
        this.thoughtsFile = 'data/thoughts.json';
        this.thoughts = new Map();
        this.isInitialized = false;
    }
    
    async initialize() {
        try {
            console.log(chalk.blue('💭 Initializing Thought Storage...'));
            
            // Ensure directory exists
            await fs.ensureDir(path.dirname(this.thoughtsFile));
            
            // Load existing thoughts
            await this.loadThoughts();
            
            this.isInitialized = true;
            console.log(chalk.green('✅ Thought Storage initialized'));
        } catch (error) {
            console.error(chalk.red('❌ Failed to initialize Thought Storage:'), error);
            throw error;
        }
    }
    
    async loadThoughts() {
        try {
            if (await fs.pathExists(this.thoughtsFile)) {
                const data = await fs.readJson(this.thoughtsFile);
                data.thoughts.forEach(thought => {
                    this.thoughts.set(thought.id, thought);
                });
                console.log(chalk.cyan(`📖 Loaded ${data.thoughts.length} thoughts`));
            }
        } catch (error) {
            console.warn(chalk.yellow('⚠️ Failed to load thoughts:'), error);
        }
    }
    
    async saveThoughts() {
        try {
            const data = {
                thoughts: Array.from(this.thoughts.values()),
                metadata: {
                    total: this.thoughts.size,
                    lastUpdated: new Date().toISOString()
                }
            };
            
            await fs.writeJson(this.thoughtsFile, data, { spaces: 2 });
        } catch (error) {
            console.error(chalk.red('❌ Failed to save thoughts:'), error);
        }
    }
    
    async storeThought(content, conversationId = null) {
        const thought = {
            id: uuidv4(),
            content,
            conversationId,
            timestamp: new Date().toISOString(),
            usageCount: 0
        };
        
        this.thoughts.set(thought.id, thought);
        await this.saveThoughts();
        
        return thought;
    }
    
    async searchRelevantThoughts(query, limit = 5) {
        // Simple search implementation
        const relevantThoughts = [];
        
        for (const thought of this.thoughts.values()) {
            if (thought.content.toLowerCase().includes(query.toLowerCase())) {
                relevantThoughts.push(thought);
            }
        }
        
        // Sort by usage count and recency
        relevantThoughts.sort((a, b) => {
            if (a.usageCount !== b.usageCount) {
                return b.usageCount - a.usageCount;
            }
            return new Date(b.timestamp) - new Date(a.timestamp);
        });
        
        return relevantThoughts.slice(0, limit);
    }
    
    async getCachedThoughts() {
        return Array.from(this.thoughts.values());
    }
    
    async saveReasoningChain(reasoningChain) {
        // Save reasoning chain for future reference
        console.log(chalk.yellow('💾 Saving reasoning chain...'));
    }
    
    getStatus() {
        return {
            initialized: this.isInitialized,
            totalThoughts: this.thoughts.size
        };
    }
} 