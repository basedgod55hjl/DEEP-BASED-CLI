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

export class LLMQueryTool extends BaseTool {
  private openai: OpenAI;
  private readonly providerPreferences: Record<string, string[]>;

  constructor(apiKey?: string, baseURL?: string) {
    super('llm_query_tool', 'DeepSeek LLM query wrapper', [
      'chat_completion',
      'function_call',
      'prefix_completion',
      'fim_completion'
    ]);

    this.openai = new OpenAI({
      apiKey: apiKey || process.env.DEEPSEEK_API_KEY || 'sk-your-api-key',
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
          return await this.chatCompletion(params as ChatCompletionParams);
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

  async chatCompletion({ messages, prompt, model, temperature = 0.7, maxTokens = 2000 }: ChatCompletionParams): Promise<ToolResponse> {
    const chatMessages = messages ?? [
      { role: 'user' as const, content: prompt ?? '' }
    ];

    const chosenModel = model || 'deepseek-chat';

    const start = Date.now();
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