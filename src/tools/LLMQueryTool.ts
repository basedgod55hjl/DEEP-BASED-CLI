import OpenAI from 'openai';
import { BaseTool } from '../common/BaseTool';
import { ToolResponse, ToolStatus } from '../common/ToolResponse';

export interface ChatCompletionParams {
  messages?: { role: 'user' | 'system' | 'assistant'; content: string }[];
  prompt?: string;
  model?: string;
  temperature?: number;
  maxTokens?: number;
}

interface PendingRequest {
  resolve: (value: ToolResponse) => void;
  reject: (reason: any) => void;
  params: ChatCompletionParams;
  timestamp: number;
}

export class LLMQueryTool extends BaseTool {
  private openai: OpenAI;
  private readonly providerPreferences: Record<string, string[]>;
  private readonly requestQueue: PendingRequest[] = [];
  private readonly maxBatchSize = 5;
  private readonly batchTimeout = 100; // ms
  private batchTimer: NodeJS.Timeout | null = null;
  private readonly connectionPool: Map<string, OpenAI> = new Map();

  constructor(apiKey?: string, baseURL?: string) {
    super('llm_query_tool', 'DeepSeek LLM query wrapper', [
      'chat_completion',
      'function_call',
      'prefix_completion',
      'fim_completion'
    ]);

    this.openai = new OpenAI({
      apiKey: apiKey || process.env.DEEPSEEK_API_KEY || 'sk-90e0dd863b8c4e0d879a02851a0ee194',
      baseURL: baseURL || process.env.DEEPSEEK_BASE_URL || 'https://api.deepseek.com'
    });

    this.providerPreferences = {
      coding: ['deepseek-coder', 'deepseek-chat'],
      creative: ['deepseek-chat', 'deepseek-coder'],
      reasoning: ['deepseek-chat', 'deepseek-coder'],
      analysis: ['deepseek-chat', 'deepseek-coder'],
      factual: ['deepseek-chat', 'deepseek-coder'],
      general: ['deepseek-chat', 'deepseek-coder']
    };
  }

  async execute(params: Record<string, unknown>): Promise<ToolResponse> {
    const operation = (params.operation as string) || 'chat_completion';

    try {
      switch (operation) {
        case 'chat_completion':
          return await this.batchedChatCompletion(params as ChatCompletionParams);
        default:
          return {
            success: false,
            message: `Unsupported operation: ${operation}`,
            status: ToolStatus.FAILED
          };
      }
    } catch (err: any) {
      return {
        success: false,
        message: `LLM error: ${err.message}`,
        status: ToolStatus.FAILED,
        data: { error: err }
      };
    }
  }

  private async batchedChatCompletion(params: ChatCompletionParams): Promise<ToolResponse> {
    return new Promise((resolve, reject) => {
      const request: PendingRequest = {
        resolve,
        reject,
        params,
        timestamp: Date.now()
      };

      this.requestQueue.push(request);

      // Process batch if it's full or schedule processing
      if (this.requestQueue.length >= this.maxBatchSize) {
        this.processBatch();
      } else if (!this.batchTimer) {
        this.batchTimer = setTimeout(() => this.processBatch(), this.batchTimeout);
      }
    });
  }

  private async processBatch(): Promise<void> {
    if (this.batchTimer) {
      clearTimeout(this.batchTimer);
      this.batchTimer = null;
    }

    if (this.requestQueue.length === 0) return;

    const batch = this.requestQueue.splice(0, this.maxBatchSize);
    
    try {
      // Process requests in parallel for better performance
      const promises = batch.map(async (request) => {
        try {
          const response = await this.singleChatCompletion(request.params);
          request.resolve(response);
        } catch (error) {
          request.reject(error);
        }
      });

      await Promise.all(promises);
    } catch (error) {
      // Reject all pending requests if batch processing fails
      batch.forEach(request => request.reject(error));
    }
  }

  private async singleChatCompletion({ messages, prompt, model, temperature = 0.7, maxTokens = 2000 }: ChatCompletionParams): Promise<ToolResponse> {
    const chatMessages = messages ?? [
      { role: 'user' as const, content: prompt ?? '' }
    ];

    const chosenModel = model || 'deepseek-chat';

    const start = Date.now();
    
    try {
      const response = await this.openai.chat.completions.create({
        model: chosenModel,
        messages: chatMessages,
        temperature,
        max_tokens: maxTokens
      });

      const content = response.choices[0]?.message?.content ?? '';
      return {
        success: true,
        message: 'Chat completion success',
        status: ToolStatus.SUCCESS,
        executionTime: (Date.now() - start) / 1000,
        data: {
          response: content,
          raw: response
        }
      };
    } catch (error: any) {
      // Implement exponential backoff for rate limits
      if (error.status === 429) {
        await this.handleRateLimit();
        return this.singleChatCompletion({ messages, prompt, model, temperature, maxTokens });
      }
      throw error;
    }
  }

  private async handleRateLimit(): Promise<void> {
    const delay = Math.random() * 1000 + 1000; // 1-2 seconds
    await new Promise(resolve => setTimeout(resolve, delay));
  }

  private getConnection(model: string): OpenAI {
    // Use connection pooling for different models
    if (!this.connectionPool.has(model)) {
      this.connectionPool.set(model, new OpenAI({
        apiKey: process.env.DEEPSEEK_API_KEY || 'sk-90e0dd863b8c4e0d879a02851a0ee194',
        baseURL: process.env.DEEPSEEK_BASE_URL || 'https://api.deepseek.com'
      }));
    }
    return this.connectionPool.get(model)!;
  }

  getSchema(): Record<string, unknown> {
    return {
      type: 'object',
      properties: {
        operation: {
          type: 'string',
          enum: ['chat_completion'],
          description: 'Type of LLM operation'
        },
        messages: {
          type: 'array',
          description: 'Chat messages',
          items: {
            type: 'object',
            properties: {
              role: { type: 'string' },
              content: { type: 'string' }
            }
          }
        },
        prompt: { type: 'string', description: 'Single prompt string' },
        model: { type: 'string', description: 'Model name (deepseek-chat etc.)' },
        temperature: { type: 'number' },
        maxTokens: { type: 'number' }
      },
      required: ['operation']
    };
  }
}