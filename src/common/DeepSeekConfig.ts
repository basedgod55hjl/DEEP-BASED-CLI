/**
 * DeepSeek API Configuration
 * 
 * Central configuration for DeepSeek API integration with hardcoded credentials
 * and model specifications as requested.
 */

export interface DeepSeekModelConfig {
  modelId: string;
  version: string;
  contextLength: number;
  maxOutput: number;
  inputCostPer1M: number;
  outputCostPer1M: number;
  features: string[];
  useCases: string[];
}

export interface DeepSeekAPIConfig {
  apiKey: string;
  baseURL: string;
  timeout: number;
  retries: number;
  rateLimitRetryDelay: number;
}

/**
 * Hardcoded DeepSeek API configuration as requested
 */
export const DEEPSEEK_CONFIG: DeepSeekAPIConfig = {
  apiKey: 'sk-90e0dd863b8c4e0d879a02851a0ee194',
  baseURL: 'https://api.deepseek.com',
  timeout: 60000, // 60 seconds
  retries: 3,
  rateLimitRetryDelay: 2000 // 2 seconds
};

/**
 * DeepSeek Chat Model Configuration (DeepSeek-V3)
 */
export const DEEPSEEK_CHAT_CONFIG: DeepSeekModelConfig = {
  modelId: 'deepseek-chat',
  version: 'DeepSeek-V3-0324',
  contextLength: 64000,
  maxOutput: 8000,
  inputCostPer1M: 0.07,
  outputCostPer1M: 0.28,
  features: [
    'conversational_ai',
    'content_generation',
    'code_assistance',
    'translation',
    'summarization',
    'creative_writing'
  ],
  useCases: [
    'general_conversation',
    'customer_support',
    'content_creation',
    'code_help',
    'quick_responses',
    'brainstorming'
  ]
};

/**
 * DeepSeek Reasoner Model Configuration (DeepSeek-R1)
 */
export const DEEPSEEK_REASONER_CONFIG: DeepSeekModelConfig = {
  modelId: 'deepseek-reasoner',
  version: 'DeepSeek-R1-0528',
  contextLength: 64000,
  maxOutput: 8000,
  inputCostPer1M: 0.55,
  outputCostPer1M: 2.19,
  features: [
    'chain_of_thought',
    'mathematical_reasoning',
    'logical_analysis',
    'step_by_step_solving',
    'complex_problem_solving',
    'reasoning_content_field'
  ],
  useCases: [
    'mathematical_problems',
    'logical_puzzles',
    'code_analysis',
    'decision_making',
    'educational_explanations',
    'debugging',
    'research_analysis'
  ]
};

/**
 * Task complexity levels for model selection
 */
export enum TaskComplexity {
  SIMPLE = 'simple',
  MODERATE = 'moderate',
  COMPLEX = 'complex',
  REASONING = 'reasoning'
}

/**
 * Model selection criteria
 */
export interface ModelSelectionCriteria {
  complexity: TaskComplexity;
  requiresReasoning: boolean;
  requiresStepByStep: boolean;
  isMathematical: boolean;
  isConversational: boolean;
  needsExplanation: boolean;
  speedPriority: boolean;
  costPriority: boolean;
}

/**
 * Brain operation modes
 */
export enum BrainMode {
  CHAT = 'chat',           // Use deepseek-chat for conversations
  REASONING = 'reasoning', // Use deepseek-reasoner for complex thinking
  AUTO = 'auto',          // Automatically select based on task
  HYBRID = 'hybrid'       // Use both models in sequence
}

/**
 * Default brain configuration
 */
export const DEFAULT_BRAIN_CONFIG = {
  mode: BrainMode.AUTO,
  chatModel: DEEPSEEK_CHAT_CONFIG,
  reasoningModel: DEEPSEEK_REASONER_CONFIG,
  apiConfig: DEEPSEEK_CONFIG,
  enableCaching: true,
  cacheTimeout: 15 * 60 * 1000, // 15 minutes
  enableStreaming: true,
  maxRetries: 3,
  temperatureRange: {
    min: 0.0,
    max: 2.0,
    default: 0.7
  }
};

/**
 * Keywords that indicate complex reasoning tasks
 */
export const REASONING_KEYWORDS = [
  'solve', 'calculate', 'analyze', 'explain', 'reason', 'logic',
  'step by step', 'mathematical', 'problem', 'algorithm', 'debug',
  'compare', 'evaluate', 'decision', 'strategy', 'plan', 'optimize',
  'derive', 'prove', 'determine', 'conclude', 'infer', 'deduce'
];

/**
 * Keywords that indicate simple conversational tasks
 */
export const CHAT_KEYWORDS = [
  'hello', 'hi', 'tell me', 'what is', 'how are', 'thanks',
  'write', 'create', 'generate', 'translate', 'summarize',
  'story', 'poem', 'email', 'letter', 'blog', 'article'
];

/**
 * Mathematical operation patterns
 */
export const MATH_PATTERNS = [
  /\d+\s*[+\-*/]\s*\d+/,           // Basic arithmetic
  /\d+%/,                          // Percentages
  /\$\d+/,                         // Currency
  /\d+\s*(km|m|cm|ft|in|miles)/,   // Measurements
  /\d+\s*hours?/,                  // Time
  /area|volume|perimeter|radius/i,  // Geometry
  /interest|compound|annual/i,      // Finance
  /equation|formula|calculate/i     // Math terms
];

/**
 * Utility functions for configuration
 */
export class DeepSeekConfigUtils {
  /**
   * Determine task complexity based on input
   */
  static analyzeTaskComplexity(input: string): TaskComplexity {
    const lowerInput = input.toLowerCase();
    
    // Check for mathematical patterns
    const hasMath = MATH_PATTERNS.some(pattern => pattern.test(input));
    if (hasMath) return TaskComplexity.REASONING;
    
    // Check for reasoning keywords
    const hasReasoningKeywords = REASONING_KEYWORDS.some(keyword => 
      lowerInput.includes(keyword));
    if (hasReasoningKeywords) return TaskComplexity.COMPLEX;
    
    // Check for simple conversational patterns
    const hasChatKeywords = CHAT_KEYWORDS.some(keyword => 
      lowerInput.includes(keyword));
    if (hasChatKeywords) return TaskComplexity.SIMPLE;
    
    // Default based on length and complexity
    if (input.length > 200) return TaskComplexity.MODERATE;
    if (input.split(' ').length > 20) return TaskComplexity.MODERATE;
    
    return TaskComplexity.SIMPLE;
  }

  /**
   * Select appropriate model based on criteria
   */
  static selectModel(criteria: ModelSelectionCriteria): DeepSeekModelConfig {
    // Prioritize reasoning model for complex tasks
    if (criteria.requiresReasoning || 
        criteria.requiresStepByStep || 
        criteria.isMathematical ||
        criteria.complexity === TaskComplexity.REASONING) {
      return DEEPSEEK_REASONER_CONFIG;
    }
    
    // Use chat model for conversational tasks or when speed/cost is priority
    if (criteria.isConversational || 
        criteria.speedPriority || 
        criteria.costPriority ||
        criteria.complexity === TaskComplexity.SIMPLE) {
      return DEEPSEEK_CHAT_CONFIG;
    }
    
    // Default to chat for moderate complexity
    return DEEPSEEK_CHAT_CONFIG;
  }

  /**
   * Create model selection criteria from input
   */
  static createSelectionCriteria(input: string, options: Partial<ModelSelectionCriteria> = {}): ModelSelectionCriteria {
    const complexity = this.analyzeTaskComplexity(input);
    const lowerInput = input.toLowerCase();
    
    return {
      complexity,
      requiresReasoning: REASONING_KEYWORDS.some(keyword => lowerInput.includes(keyword)),
      requiresStepByStep: lowerInput.includes('step') || lowerInput.includes('explain'),
      isMathematical: MATH_PATTERNS.some(pattern => pattern.test(input)),
      isConversational: CHAT_KEYWORDS.some(keyword => lowerInput.includes(keyword)),
      needsExplanation: lowerInput.includes('explain') || lowerInput.includes('why'),
      speedPriority: false,
      costPriority: false,
      ...options
    };
  }

  /**
   * Calculate estimated cost for a request
   */
  static calculateCost(
    model: DeepSeekModelConfig, 
    inputTokens: number, 
    outputTokens: number
  ): number {
    const inputCost = (inputTokens / 1000000) * model.inputCostPer1M;
    const outputCost = (outputTokens / 1000000) * model.outputCostPer1M;
    return inputCost + outputCost;
  }

  /**
   * Estimate token count from text
   */
  static estimateTokens(text: string): number {
    // Rough approximation: 1 token ≈ 4 characters for English
    // This can be refined with actual tokenization if needed
    return Math.ceil(text.length / 4);
  }

  /**
   * Validate API configuration
   */
  static validateConfig(config: DeepSeekAPIConfig): boolean {
    if (!config.apiKey || !config.apiKey.startsWith('sk-')) {
      throw new Error('Invalid API key format');
    }
    
    if (!config.baseURL || !config.baseURL.startsWith('https://')) {
      throw new Error('Invalid base URL');
    }
    
    return true;
  }

  /**
   * Get model by ID
   */
  static getModelConfig(modelId: string): DeepSeekModelConfig {
    switch (modelId) {
      case 'deepseek-chat':
        return DEEPSEEK_CHAT_CONFIG;
      case 'deepseek-reasoner':
        return DEEPSEEK_REASONER_CONFIG;
      default:
        throw new Error(`Unknown model ID: ${modelId}`);
    }
  }

  /**
   * Check if model supports feature
   */
  static modelSupportsFeature(modelId: string, feature: string): boolean {
    const config = this.getModelConfig(modelId);
    return config.features.includes(feature);
  }
}

// All exports are already declared above with 'export const' or 'export class'
// No need for additional export statement