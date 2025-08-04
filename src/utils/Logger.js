/**
 * Logger Utility
 * Centralized logging for the DeepSeek-Reasoner Brain System
 * Made by @Lucariolucario55 on Telegram
 */

import chalk from 'chalk';
import fs from 'fs-extra';
import path from 'path';

export class Logger {
    constructor() {
        this.logDir = 'logs';
        this.logFile = path.join(this.logDir, `deepseek-reasoner-${new Date().toISOString().split('T')[0]}.log`);
        
        this.initialize();
    }
    
    async initialize() {
        try {
            await fs.ensureDir(this.logDir);
        } catch (error) {
            console.error('Failed to initialize logger:', error);
        }
    }
    
    async log(level, message, data = null) {
        const timestamp = new Date().toISOString();
        const logEntry = {
            timestamp,
            level,
            message,
            data
        };
        
        // Console output
        this.logToConsole(level, message, data);
        
        // File output
        await this.logToFile(logEntry);
    }
    
    logToConsole(level, message, data) {
        const timestamp = new Date().toISOString();
        
        switch (level.toLowerCase()) {
            case 'info':
                console.log(chalk.blue(`[${timestamp}] INFO: ${message}`));
                break;
            case 'warn':
                console.log(chalk.yellow(`[${timestamp}] WARN: ${message}`));
                break;
            case 'error':
                console.log(chalk.red(`[${timestamp}] ERROR: ${message}`));
                break;
            case 'debug':
                console.log(chalk.gray(`[${timestamp}] DEBUG: ${message}`));
                break;
            default:
                console.log(`[${timestamp}] ${level.toUpperCase()}: ${message}`);
        }
        
        if (data) {
            console.log(chalk.gray(JSON.stringify(data, null, 2)));
        }
    }
    
    async logToFile(logEntry) {
        try {
            const logLine = JSON.stringify(logEntry) + '\n';
            await fs.appendFile(this.logFile, logLine);
        } catch (error) {
            console.error('Failed to write to log file:', error);
        }
    }
    
    info(message, data = null) {
        return this.log('info', message, data);
    }
    
    warn(message, data = null) {
        return this.log('warn', message, data);
    }
    
    error(message, data = null) {
        return this.log('error', message, data);
    }
    
    debug(message, data = null) {
        return this.log('debug', message, data);
    }
} 