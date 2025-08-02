import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'fs';
import { homedir } from 'os';
import { join } from 'path';
import { DeepSeekConfig } from '../types/index.js';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

export class ConfigManager {
  private configDir: string;
  private configFile: string;
  private config: DeepSeekConfig;

  constructor() {
    this.configDir = join(homedir(), '.deepseek');
    this.configFile = join(this.configDir, 'config.json');
    this.config = this.loadConfig();
  }

  private loadConfig(): DeepSeekConfig {
    // First check environment variables
    const envConfig: DeepSeekConfig = {
      apiKey: process.env.DEEPSEEK_API_KEY,
      apiEndpoint: process.env.DEEPSEEK_API_ENDPOINT,
      model: process.env.DEEPSEEK_MODEL,
      maxTokens: process.env.DEEPSEEK_MAX_TOKENS ? parseInt(process.env.DEEPSEEK_MAX_TOKENS) : undefined,
      temperature: process.env.DEEPSEEK_TEMPERATURE ? parseFloat(process.env.DEEPSEEK_TEMPERATURE) : undefined,
    };

    // Then check config file
    if (existsSync(this.configFile)) {
      try {
        const fileConfig = JSON.parse(readFileSync(this.configFile, 'utf-8'));
        return { ...fileConfig, ...envConfig };
      } catch (error) {
        console.error('Error reading config file:', error);
      }
    }

    return envConfig;
  }

  saveConfig(config: Partial<DeepSeekConfig>): void {
    if (!existsSync(this.configDir)) {
      mkdirSync(this.configDir, { recursive: true });
    }

    const currentConfig = this.loadConfig();
    const newConfig = { ...currentConfig, ...config };
    
    writeFileSync(this.configFile, JSON.stringify(newConfig, null, 2));
    this.config = newConfig;
  }

  getConfig(): DeepSeekConfig {
    return this.config;
  }

  get(key: keyof DeepSeekConfig): any {
    return this.config[key];
  }

  set(key: keyof DeepSeekConfig, value: any): void {
    this.saveConfig({ [key]: value });
  }

  isConfigured(): boolean {
    return !!this.config.apiKey;
  }
}