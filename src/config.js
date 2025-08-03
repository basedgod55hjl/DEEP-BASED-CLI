#!/usr/bin/env node
/**
 * Configuration management for DeepSeek CLI
 * High-performance, non-blocking configuration with web APIs
 */

import { config } from 'dotenv';
import { readFile, writeFile } from 'fs/promises';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

// Load environment variables
config();

export const DEEPSEEK_CONFIG = {
  // API Configuration
  apiKey: process.env.DEEPSEEK_API_KEY || 'sk-9af038dd3bdd46258c4a9d02850c9a6d',
  baseUrl: process.env.DEEPSEEK_API_ENDPOINT || 'https://api.deepseek.com/v1',
  betaUrl: 'https://api.deepseek.com/beta',
  
  // Models
  models: {
    CHAT: 'deepseek-chat',
    REASONER: 'deepseek-reasoner'
  },
  
  // Default settings
  defaults: {
    model: 'deepseek-chat',
    temperature: 0.7,
    maxTokens: 4096,
    stream: true,
    timeout: 60000,
    maxRetries: 3,
    retryDelay: 1000
  },
  
  // Performance settings
  performance: {
    concurrency: 5,
    batchSize: 10,
    streamChunkSize: 1024,
    cacheSize: 100
  },
  
  // UI Settings
  ui: {
    animations: true,
    colors: true,
    gradients: true,
    spinners: true
  }
};

/**
 * Async configuration loader with caching
 */
class ConfigManager {
  constructor() {
    this.cache = new Map();
    this.configPath = join(__dirname, '../.env');
  }
  
  /**
   * Load configuration asynchronously
   */
  async load() {
    try {
      const data = await readFile(this.configPath, 'utf8');
      const config = this.parseEnv(data);
      this.cache.set('config', config);
      return config;
    } catch (error) {
      // Return defaults if no config file
      return DEEPSEEK_CONFIG;
    }
  }
  
  /**
   * Save configuration asynchronously
   */
  async save(config) {
    const envContent = this.stringifyEnv(config);
    await writeFile(this.configPath, envContent, 'utf8');
    this.cache.set('config', config);
  }
  
  /**
   * Parse environment variables
   */
  parseEnv(content) {
    const config = { ...DEEPSEEK_CONFIG };
    const lines = content.split('\n');
    
    for (const line of lines) {
      const [key, value] = line.split('=');
      if (key && value) {
        switch (key.trim()) {
          case 'DEEPSEEK_API_KEY':
            config.apiKey = value.trim();
            break;
          case 'DEEPSEEK_API_ENDPOINT':
            config.baseUrl = value.trim();
            break;
          case 'DEEPSEEK_MODEL':
            config.defaults.model = value.trim();
            break;
          case 'DEEPSEEK_TEMPERATURE':
            config.defaults.temperature = parseFloat(value.trim());
            break;
          case 'DEEPSEEK_MAX_TOKENS':
            config.defaults.maxTokens = parseInt(value.trim());
            break;
        }
      }
    }
    
    return config;
  }
  
  /**
   * Convert config to environment format
   */
  stringifyEnv(config) {
    return `# DeepSeek CLI Configuration
DEEPSEEK_API_KEY=${config.apiKey}
DEEPSEEK_API_ENDPOINT=${config.baseUrl}
DEEPSEEK_MODEL=${config.defaults.model}
DEEPSEEK_TEMPERATURE=${config.defaults.temperature}
DEEPSEEK_MAX_TOKENS=${config.defaults.maxTokens}
`;
  }
  
  /**
   * Get cached config or load
   */
  async get() {
    if (this.cache.has('config')) {
      return this.cache.get('config');
    }
    return await this.load();
  }
}

export const configManager = new ConfigManager();
export default DEEPSEEK_CONFIG;