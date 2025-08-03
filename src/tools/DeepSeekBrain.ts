/**
 * DeepSeek Brain - Core Reasoning Engine
 * 
 * Implements dual-brain architecture using DeepSeek-Chat and DeepSeek-Reasoner
 * with intelligent model selection, caching, and performance optimization.
 */

import OpenAI from 'openai';
import { BaseTool } from '../common/BaseTool';
import { ToolResponse, ToolStatus } from '../common/ToolResponse';
import { globalCache } from '../common/CacheManager';
import {
  DEEPSEEK_CONFIG,
  DEEPSEEK_CHAT_CONFIG,
  DEEPSEEK_REASONER_CONFIG,
  BrainMode,
  TaskComplexity,
  DeepSeekConfigUtils,
  ModelSelectionCriteria,
  DeepSeekModelConfig
} from '../common/DeepSeekConfig';

export interface BrainRequest {
  message: string;
  mode?: BrainMode;
  temperature?: number;
  maxTokens?: number;
  stream?: boolean;
  context?: Array<{ role: string; content: string }>;
  requiresReasoning?: boolean;
  priority?: 'speed' | 'accuracy' | 'cost';
}

export interface BrainResponse {
  content: string;
  reasoning?: string;
  model: string;
  mode: BrainMode;
  complexity: TaskComplexity;
  usage: {
    promptTokens: number;
    completionTokens: number;
    totalTokens: number;
    estimatedCost: number;
  };
  cached: boolean;
  processingTime: number;
  metadata?: {
    selectedModel: DeepSeekModelConfig;
    selectionCriteria: ModelSelectionCriteria;
    fallbackUsed?: boolean;
  };
}

export interface StreamChunk {
  content?: string;
  reasoning?: string;
  done: boolean;
  model: string;
  mode: BrainMode;
}

export class DeepSeekBrain extends BaseTool {
  private client: OpenAI;
  private defaultMode: BrainMode;
  private enableCaching: boolean;
  private maxRetries: number;

  constructor(options: {
    mode?: BrainMode;
    enableCaching?: boolean;
    maxRetries?: number;
  } = {}) {
    super(
      'DeepSeekBrain',
      'Dual-brain AI system using DeepSeek-Chat and DeepSeek-Reasoner',
      [
        'conversation',
        'reasoning',
        'problem_solving',
        'mathematical_analysis',
        'code_analysis',
        'decision_making',
        'auto_model_selection'
      ]
    );

    // Validate configuration
    DeepSeekConfigUtils.validateConfig(DEEPSEEK_CONFIG);

    // Initialize OpenAI client with DeepSeek configuration
    this.client = new OpenAI({
      apiKey: DEEPSEEK_CONFIG.apiKey,
      baseURL: DEEPSEEK_CONFIG.baseURL,
      timeout: DEEPSEEK_CONFIG.timeout
    });

    this.defaultMode = options.mode || BrainMode.AUTO;
    this.enableCaching = options.enableCaching !== false;
    this.maxRetries = options.maxRetries || 3;
  }

  async execute(params: Record<string, unknown>): Promise<ToolResponse> {
    const request = this.parseRequest(params);
    
    try {
      const response = await this.think(request);
      
      return {
        success: true,
        message: 'Brain processing completed',
        status: ToolStatus.SUCCESS,
        data: response
      };
    } catch (error) {
      return {
        success: false,
        message: `Brain processing failed: ${error}`,
        status: ToolStatus.FAILED,
        data: { error: error instanceof Error ? error.message : String(error) }
      };
    }
  }

  /**
   * Main thinking method - processes requests with intelligent model selection
   */
  async think(request: BrainRequest): Promise<BrainResponse> {
    const startTime = Date.now();
    
    // Create cache key for the request
    const cacheKey = this.createCacheKey(request);
    
    // Check cache if enabled
    if (this.enableCaching) {
      const cached = await globalCache.get<BrainResponse>(cacheKey);
      if (cached) {
        return {
          ...cached,
          cached: true,
          processingTime: Date.now() - startTime
        };
      }
    }

    // Determine processing mode and model
    const mode = request.mode || this.defaultMode;
    const { selectedModel, criteria } = this.selectModel(request, mode);

    let response: BrainResponse;

    try {
      switch (mode) {
        case BrainMode.CHAT:
          response = await this.processChatMode(request, selectedModel, criteria);
          break;
        case BrainMode.REASONING:
          response = await this.processReasoningMode(request, selectedModel, criteria);
          break;
        case BrainMode.AUTO:
          response = await this.processAutoMode(request, selectedModel, criteria);
          break;
        case BrainMode.HYBRID:
          response = await this.processHybridMode(request, criteria);
          break;
        default:
          throw new Error(`Unsupported brain mode: ${mode}`);
      }

      response.processingTime = Date.now() - startTime;
      response.cached = false;

      // Cache the response if enabled
      if (this.enableCaching) {
        await globalCache.set(cacheKey, response, 15 * 60 * 1000); // 15 minutes
      }

      return response;

    } catch (error) {
      // Try fallback approach
      if (selectedModel.modelId === 'deepseek-reasoner') {
        console.warn('Reasoner failed, falling back to chat model');
        return this.processChatMode(request, DEEPSEEK_CHAT_CONFIG, criteria, true);
      } else {
        throw error;
      }
    }
  }

  /**
   * Streaming version of think method
   */
  async *thinkStream(request: BrainRequest): AsyncGenerator<StreamChunk> {
    const { selectedModel, criteria } = this.selectModel(request, request.mode || this.defaultMode);
    
    const messages = this.buildMessages(request);
    const modelParams = this.buildModelParams(request, selectedModel);

    try {
      const stream = await this.client.chat.completions.create({
        ...modelParams,
        stream: true
      }) as any;

      let content = '';
      let reasoning = '';

      for await (const chunk of stream) {
        const delta = chunk.choices[0]?.delta;
        
        if (delta?.reasoning_content) {
          reasoning += delta.reasoning_content;
          yield {
            reasoning: delta.reasoning_content,
            done: false,
            model: selectedModel.modelId,
            mode: request.mode || BrainMode.AUTO
          };
        }
        
        if (delta?.content) {
          content += delta.content;
          yield {
            content: delta.content,
            done: false,
            model: selectedModel.modelId,
            mode: request.mode || BrainMode.AUTO
          };
        }
      }

      yield {
        done: true,
        model: selectedModel.modelId,
        mode: request.mode || BrainMode.AUTO
      };

    } catch (error) {
      throw new Error(`Streaming failed: ${error}`);
    }
  }

  /**
   * Process request using chat mode (deepseek-chat)
   */
  private async processChatMode(
    request: BrainRequest, 
    model: DeepSeekModelConfig, 
    criteria: ModelSelectionCriteria,
    isFallback = false
  ): Promise<BrainResponse> {
    const messages = this.buildMessages(request);
    const params = this.buildModelParams(request, DEEPSEEK_CHAT_CONFIG);

    const response = await this.client.chat.completions.create(params);
    
    const content = response.choices[0].message.content || '';
    const usage = response.usage || { prompt_tokens: 0, completion_tokens: 0, total_tokens: 0 };

    return {
      content,
      model: 'deepseek-chat',
      mode: BrainMode.CHAT,
      complexity: criteria.complexity,
      usage: {
        promptTokens: usage.prompt_tokens,
        completionTokens: usage.completion_tokens,
        totalTokens: usage.total_tokens,
        estimatedCost: DeepSeekConfigUtils.calculateCost(
          DEEPSEEK_CHAT_CONFIG, 
          usage.prompt_tokens, 
          usage.completion_tokens
        )
      },
      cached: false,
      processingTime: 0,
      metadata: {
        selectedModel: DEEPSEEK_CHAT_CONFIG,
        selectionCriteria: criteria,
        fallbackUsed: isFallback
      }
    };
  }

  /**
   * Process request using reasoning mode (deepseek-reasoner)
   */
  private async processReasoningMode(
    request: BrainRequest, 
    model: DeepSeekModelConfig, 
    criteria: ModelSelectionCriteria
  ): Promise<BrainResponse> {
    const messages = this.buildMessages(request);
    const params = this.buildModelParams(request, DEEPSEEK_REASONER_CONFIG);

    const response = await this.client.chat.completions.create(params);
    
    const content = response.choices[0].message.content || '';
    const reasoning = (response.choices[0].message as any).reasoning_content || '';
    const usage = response.usage || { prompt_tokens: 0, completion_tokens: 0, total_tokens: 0 };

    return {
      content,
      reasoning,
      model: 'deepseek-reasoner',
      mode: BrainMode.REASONING,
      complexity: criteria.complexity,
      usage: {
        promptTokens: usage.prompt_tokens,
        completionTokens: usage.completion_tokens,
        totalTokens: usage.total_tokens,
        estimatedCost: DeepSeekConfigUtils.calculateCost(
          DEEPSEEK_REASONER_CONFIG, 
          usage.prompt_tokens, 
          usage.completion_tokens
        )
      },
      cached: false,
      processingTime: 0,
      metadata: {
        selectedModel: DEEPSEEK_REASONER_CONFIG,
        selectionCriteria: criteria
      }
    };
  }

  /**
   * Process request using auto mode (intelligent model selection)
   */
  private async processAutoMode(
    request: BrainRequest, 
    model: DeepSeekModelConfig, 
    criteria: ModelSelectionCriteria
  ): Promise<BrainResponse> {
    if (model.modelId === 'deepseek-reasoner') {
      return this.processReasoningMode(request, model, criteria);
    } else {
      return this.processChatMode(request, model, criteria);
    }
  }

  /**
   * Process request using hybrid mode (both models in sequence)
   */
  private async processHybridMode(
    request: BrainRequest, 
    criteria: ModelSelectionCriteria
  ): Promise<BrainResponse> {
    // First, get reasoning from the reasoner model
    const reasoningResponse = await this.processReasoningMode(request, DEEPSEEK_REASONER_CONFIG, criteria);
    
    // Then, use the chat model to refine the response
    const refinedRequest: BrainRequest = {
      ...request,
      message: `Based on this reasoning: ${reasoningResponse.reasoning}\n\nProvide a clear, concise answer to: ${request.message}`
    };
    
    const chatResponse = await this.processChatMode(refinedRequest, DEEPSEEK_CHAT_CONFIG, criteria);
    
    // Combine both responses
    return {
      content: chatResponse.content,
      reasoning: reasoningResponse.reasoning,
      model: 'hybrid',
      mode: BrainMode.HYBRID,
      complexity: criteria.complexity,
      usage: {
        promptTokens: reasoningResponse.usage.promptTokens + chatResponse.usage.promptTokens,
        completionTokens: reasoningResponse.usage.completionTokens + chatResponse.usage.completionTokens,
        totalTokens: reasoningResponse.usage.totalTokens + chatResponse.usage.totalTokens,
        estimatedCost: reasoningResponse.usage.estimatedCost + chatResponse.usage.estimatedCost
      },
      cached: false,
      processingTime: 0,
      metadata: {
        selectedModel: DEEPSEEK_REASONER_CONFIG,
        selectionCriteria: criteria
      }
    };
  }

  /**
   * Select appropriate model based on request and mode
   */
  private selectModel(request: BrainRequest, mode: BrainMode): {
    selectedModel: DeepSeekModelConfig;
    criteria: ModelSelectionCriteria;
  } {
    const criteria = DeepSeekConfigUtils.createSelectionCriteria(request.message, {
      requiresReasoning: request.requiresReasoning,
      speedPriority: request.priority === 'speed',
      costPriority: request.priority === 'cost'
    });

    let selectedModel: DeepSeekModelConfig;

    switch (mode) {
      case BrainMode.CHAT:
        selectedModel = DEEPSEEK_CHAT_CONFIG;
        break;
      case BrainMode.REASONING:
        selectedModel = DEEPSEEK_REASONER_CONFIG;
        break;
      case BrainMode.AUTO:
        selectedModel = DeepSeekConfigUtils.selectModel(criteria);
        break;
      case BrainMode.HYBRID:
        selectedModel = DEEPSEEK_REASONER_CONFIG; // Start with reasoning
        break;
      default:
        selectedModel = DEEPSEEK_CHAT_CONFIG;
    }

    return { selectedModel, criteria };
  }

  /**
   * Build messages array for API request
   */
  private buildMessages(request: BrainRequest): Array<{ role: string; content: string }> {
    const messages: Array<{ role: string; content: string }> = [];
    
    // Add context if provided
    if (request.context && request.context.length > 0) {
      messages.push(...request.context);
    }
    
    // Add the main message
    messages.push({ role: 'user', content: request.message });
    
    return messages;
  }

  /**
   * Build model parameters for API request
   */
  private buildModelParams(request: BrainRequest, model: DeepSeekModelConfig): any {
    const messages = this.buildMessages(request);
    
    const params: any = {
      model: model.modelId,
      messages,
      max_tokens: Math.min(request.maxTokens || 4000, model.maxOutput),
      stream: request.stream || false
    };

    // Add temperature only for chat model (reasoner doesn't support it)
    if (model.modelId === 'deepseek-chat') {
      params.temperature = request.temperature || 0.7;
    }

    return params;
  }

  /**
   * Parse request parameters
   */
  private parseRequest(params: Record<string, unknown>): BrainRequest {
    return {
      message: params.message as string || '',
      mode: params.mode as BrainMode,
      temperature: params.temperature as number,
      maxTokens: params.maxTokens as number,
      stream: params.stream as boolean,
      context: params.context as Array<{ role: string; content: string }>,
      requiresReasoning: params.requiresReasoning as boolean,
      priority: params.priority as 'speed' | 'accuracy' | 'cost'
    };
  }

  /**
   * Create cache key for request
   */
  private createCacheKey(request: BrainRequest): string {
    const keyData = {
      message: request.message,
      mode: request.mode,
      temperature: request.temperature,
      context: request.context
    };
    return `deepseek-brain:${JSON.stringify(keyData)}`;
  }

  /**
   * Get schema for the tool
   */
  getSchema(): Record<string, unknown> {
    return {
      type: 'object',
      properties: {
        message: {
          type: 'string',
          description: 'The message or question to process'
        },
        mode: {
          type: 'string',
          enum: ['chat', 'reasoning', 'auto', 'hybrid'],
          description: 'Processing mode'
        },
        temperature: {
          type: 'number',
          minimum: 0,
          maximum: 2,
          description: 'Creativity level (chat mode only)'
        },
        maxTokens: {
          type: 'number',
          description: 'Maximum tokens to generate'
        },
        stream: {
          type: 'boolean',
          description: 'Enable streaming response'
        },
        context: {
          type: 'array',
          description: 'Conversation context',
          items: {
            type: 'object',
            properties: {
              role: { type: 'string' },
              content: { type: 'string' }
            }
          }
        },
        requiresReasoning: {
          type: 'boolean',
          description: 'Force reasoning mode'
        },
        priority: {
          type: 'string',
          enum: ['speed', 'accuracy', 'cost'],
          description: 'Processing priority'
        }
      },
      required: ['message']
    };
  }

  /**
   * Utility methods for external use
   */
  
  /**
   * Analyze task complexity
   */
  analyzeComplexity(message: string): TaskComplexity {
    return DeepSeekConfigUtils.analyzeTaskComplexity(message);
  }

  /**
   * Get model recommendation
   */
  recommendModel(message: string): DeepSeekModelConfig {
    const criteria = DeepSeekConfigUtils.createSelectionCriteria(message);
    return DeepSeekConfigUtils.selectModel(criteria);
  }

  /**
   * Estimate cost for a request
   */
  estimateCost(message: string, maxTokens = 2000): number {
    const model = this.recommendModel(message);
    const inputTokens = DeepSeekConfigUtils.estimateTokens(message);
    const outputTokens = Math.min(maxTokens, model.maxOutput);
    return DeepSeekConfigUtils.calculateCost(model, inputTokens, outputTokens);
  }

  /**
   * Get brain statistics
   */
  getStats() {
    return {
      defaultMode: this.defaultMode,
      enableCaching: this.enableCaching,
      maxRetries: this.maxRetries,
      chatModel: DEEPSEEK_CHAT_CONFIG,
      reasoningModel: DEEPSEEK_REASONER_CONFIG,
      cacheStats: globalCache.getStats()
    };
  }
}