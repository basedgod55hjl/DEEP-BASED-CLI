/**
 * Streaming Manager
 * Handles token streaming and real-time communication
 * Made by @Lucariolucario55 on Telegram
 */

import { EventEmitter } from 'events';
import chalk from 'chalk';

export class StreamingManager extends EventEmitter {
    constructor() {
        super();
        this.isInitialized = false;
        this.activeStreams = new Map();
    }
    
    async initialize() {
        try {
            console.log(chalk.blue('📡 Initializing Streaming Manager...'));
            this.isInitialized = true;
            console.log(chalk.green('✅ Streaming Manager initialized'));
        } catch (error) {
            console.error(chalk.red('❌ Failed to initialize Streaming Manager:'), error);
            throw error;
        }
    }
    
    createStream(streamId) {
        const stream = new EventEmitter();
        this.activeStreams.set(streamId, stream);
        return stream;
    }
    
    removeStream(streamId) {
        this.activeStreams.delete(streamId);
    }
    
    getStatus() {
        return {
            initialized: this.isInitialized,
            activeStreams: this.activeStreams.size
        };
    }
} 