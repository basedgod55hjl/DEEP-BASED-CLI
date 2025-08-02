export interface DeepSeekConfig {
  apiKey?: string;
  apiEndpoint?: string;
  model?: string;
  maxTokens?: number;
  temperature?: number;
  timeout?: number;
}

export interface ChatMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

export interface ChatCompletionRequest {
  model: string;
  messages: ChatMessage[];
  temperature?: number;
  max_tokens?: number;
  stream?: boolean;
}

export interface ChatCompletionResponse {
  id: string;
  object: string;
  created: number;
  model: string;
  choices: Array<{
    index: number;
    message: ChatMessage;
    finish_reason: string;
  }>;
  usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

export interface CodebaseAnalysisOptions {
  path: string;
  includePatterns?: string[];
  excludePatterns?: string[];
  maxFileSize?: number;
  maxFiles?: number;
}

export interface FileInfo {
  path: string;
  content: string;
  size: number;
  extension: string;
}