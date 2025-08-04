/**
 * Conversation Manager
 * Handles multi-conversation support and context management
 * Made by @Lucariolucario55 on Telegram
 */

import { v4 as uuidv4 } from 'uuid';
import chalk from 'chalk';

export class ConversationManager {
    constructor() {
        this.conversations = new Map();
        this.isInitialized = false;
    }
    
    async initialize() {
        try {
            console.log(chalk.blue('💬 Initializing Conversation Manager...'));
            this.isInitialized = true;
            console.log(chalk.green('✅ Conversation Manager initialized'));
        } catch (error) {
            console.error(chalk.red('❌ Failed to initialize Conversation Manager:'), error);
            throw error;
        }
    }
    
    createConversation(persona = 'DEANNA') {
        const conversationId = uuidv4();
        const conversation = {
            id: conversationId,
            persona,
            messages: [],
            created: new Date().toISOString(),
            lastActivity: new Date().toISOString()
        };
        
        this.conversations.set(conversationId, conversation);
        return conversationId;
    }
    
    addMessage(conversationId, message, isUser = true) {
        const conversation = this.conversations.get(conversationId);
        if (!conversation) {
            throw new Error(`Conversation ${conversationId} not found`);
        }
        
        const messageObj = {
            id: uuidv4(),
            content: message,
            isUser,
            timestamp: new Date().toISOString()
        };
        
        conversation.messages.push(messageObj);
        conversation.lastActivity = new Date().toISOString();
        
        return messageObj;
    }
    
    getConversation(conversationId) {
        return this.conversations.get(conversationId);
    }
    
    async saveState() {
        // Save conversation state to persistent storage
        console.log(chalk.yellow('💾 Saving conversation state...'));
    }
    
    getStatus() {
        return {
            initialized: this.isInitialized,
            activeConversations: this.conversations.size
        };
    }
} 