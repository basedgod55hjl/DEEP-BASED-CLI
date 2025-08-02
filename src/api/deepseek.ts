import axios, { AxiosInstance } from 'axios';
import { ChatCompletionRequest, ChatCompletionResponse, DeepSeekConfig } from '../types/index.js';

export class DeepSeekAPI {
  private client: AxiosInstance;
  private config: DeepSeekConfig;

  constructor(config: DeepSeekConfig) {
    this.config = {
      apiEndpoint: 'https://api.deepseek.com/v1',
      model: 'deepseek-coder',
      maxTokens: 4096,
      temperature: 0.7,
      timeout: 30000,
      ...config,
    };

    if (!this.config.apiKey) {
      throw new Error('DeepSeek API key is required');
    }

    this.client = axios.create({
      baseURL: this.config.apiEndpoint,
      timeout: this.config.timeout,
      headers: {
        'Authorization': `Bearer ${this.config.apiKey}`,
        'Content-Type': 'application/json',
      },
    });
  }

  async createChatCompletion(request: ChatCompletionRequest): Promise<ChatCompletionResponse> {
    try {
      const response = await this.client.post<ChatCompletionResponse>('/chat/completions', {
        model: request.model || this.config.model,
        messages: request.messages,
        temperature: request.temperature ?? this.config.temperature,
        max_tokens: request.max_tokens ?? this.config.maxTokens,
        stream: request.stream || false,
      });

      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.error?.message || error.message;
        throw new Error(`DeepSeek API error: ${message}`);
      }
      throw error;
    }
  }

  async streamChatCompletion(
    request: ChatCompletionRequest,
    onChunk: (chunk: string) => void
  ): Promise<void> {
    try {
      const response = await this.client.post('/chat/completions', {
        ...request,
        model: request.model || this.config.model,
        stream: true,
      }, {
        responseType: 'stream',
      });

      response.data.on('data', (chunk: Buffer) => {
        const lines = chunk.toString().split('\n').filter(line => line.trim() !== '');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') {
              return;
            }
            
            try {
              const parsed = JSON.parse(data);
              const content = parsed.choices?.[0]?.delta?.content;
              if (content) {
                onChunk(content);
              }
            } catch (e) {
              // Skip invalid JSON chunks
            }
          }
        }
      });

      return new Promise((resolve, reject) => {
        response.data.on('end', resolve);
        response.data.on('error', reject);
      });
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.error?.message || error.message;
        throw new Error(`DeepSeek API error: ${message}`);
      }
      throw error;
    }
  }
}