import { BaseTool } from './common/BaseTool';
import { ToolResponse, ToolStatus } from './common/ToolResponse';
import { PerformanceMonitor } from './common/PerformanceMonitor.js';

/**
 * Optimized Tool Manager with lazy loading and caching
 */
export class ToolManager {
  private readonly toolCache: Map<string, BaseTool> = new Map();
  private readonly executionHistory: Array<{ name: string; params: Record<string, unknown>; response: ToolResponse }> = [];
  private readonly responseCache: Map<string, ToolResponse> = new Map();
  private readonly toolFactories: Map<string, () => Promise<BaseTool>> = new Map();
  private readonly performanceMonitor: PerformanceMonitor = new PerformanceMonitor();

  constructor() {
    this.initializeToolFactories();
  }

  private initializeToolFactories(): void {
    // Lazy load tool factories to reduce initial bundle size
    this.toolFactories.set('llmquerytool', async () => {
      const { LLMQueryTool } = await import('./tools/LLMQueryTool.js');
      return new LLMQueryTool();
    });

    this.toolFactories.set('vectordatabasetool', async () => {
      const { VectorDatabaseTool } = await import('./tools/VectorDatabaseTool.js');
      return new VectorDatabaseTool();
    });

    this.toolFactories.set('sqldatabasetool', async () => {
      const { SQLDatabaseTool } = await import('./tools/SQLDatabaseTool.js');
      return new SQLDatabaseTool();
    });

    this.toolFactories.set('fastreasoningengine', async () => {
      const { FastReasoningEngine } = await import('./tools/FastReasoningEngine.js');
      const { LLMQueryTool } = await import('./tools/LLMQueryTool.js');
      return new FastReasoningEngine(new LLMQueryTool());
    });

    this.toolFactories.set('ragpipelinetool', async () => {
      const { RAGPipelineTool } = await import('./tools/RAGPipelineTool.js');
      const { VectorDatabaseTool } = await import('./tools/VectorDatabaseTool.js');
      const { LLMQueryTool } = await import('./tools/LLMQueryTool.js');
      return new RAGPipelineTool(new VectorDatabaseTool(), new LLMQueryTool());
    });

    this.toolFactories.set('unifiedagentsystem', async () => {
      const { UnifiedAgentSystem } = await import('./tools/UnifiedAgentSystem.js');
      return new UnifiedAgentSystem();
    });

    // Add other tools as needed
    const otherTools = [
      'plannertool', 'readertool', 'writertool', 'reviewertool', 
      'coderagenttool', 'selfhealertool', 'commandexecutortool',
      'debuggertool', 'datadogintegrationtool', 'visiontool',
      'webscrapertool', 'memoryrankertool', 'swarmtool'
    ];

    for (const toolName of otherTools) {
      this.toolFactories.set(toolName, async () => {
        const toolModule = await import(`./tools/${toolName.charAt(0).toUpperCase() + toolName.slice(1)}.js`);
        const ToolClass = toolModule[toolName.charAt(0).toUpperCase() + toolName.slice(1)];
        return new ToolClass();
      });
    }
  }

  async getTool(name: string): Promise<BaseTool | undefined> {
    const normalizedName = name.toLowerCase();
    
    // Check cache first
    if (this.toolCache.has(normalizedName)) {
      return this.toolCache.get(normalizedName);
    }

    // Lazy load tool
    const factory = this.toolFactories.get(normalizedName);
    if (!factory) {
      return undefined;
    }

    try {
      const loadStart = Date.now();
      const tool = await factory();
      const loadTime = Date.now() - loadStart;
      
      this.toolCache.set(normalizedName, tool);
      this.performanceMonitor.recordToolLoad(normalizedName, loadTime);
      return tool;
    } catch (error) {
      console.error(`Failed to load tool ${normalizedName}:`, error);
      return undefined;
    }
  }

  async listTools(): Promise<string[]> {
    return Array.from(this.toolFactories.keys());
  }

  private generateCacheKey(name: string, params: Record<string, unknown>): string {
    return `${name}:${JSON.stringify(params)}`;
  }

  async executeTool(name: string, params: Record<string, unknown>): Promise<ToolResponse> {
    const tool = await this.getTool(name);
    if (!tool) {
      this.performanceMonitor.recordRequest(0, false, true);
      return {
        success: false,
        message: `Tool ${name} not found`,
        status: ToolStatus.FAILED
      };
    }

    // Check cache for idempotent operations
    const cacheKey = this.generateCacheKey(name, params);
    if (this.responseCache.has(cacheKey)) {
      const cachedResponse = this.responseCache.get(cacheKey)!;
      this.performanceMonitor.recordRequest(cachedResponse.executionTime || 0, true);
      return cachedResponse;
    }

    const t0 = Date.now();
    const response = await tool.execute(params);
    const executionTime = Date.now() - t0;
    response.executionTime = executionTime / 1000;

    // Cache successful responses for read operations
    if (response.success && this.isReadOperation(params)) {
      this.responseCache.set(cacheKey, response);
    }

    this.performanceMonitor.recordRequest(executionTime, false, !response.success);
    this.executionHistory.push({ name, params, response });
    return response;
  }

  private isReadOperation(params: Record<string, unknown>): boolean {
    const operation = params.operation as string;
    return ['search', 'query', 'read'].includes(operation);
  }

  history(limit = 20): Array<{ name: string; params: Record<string, unknown>; response: ToolResponse }> {
    return this.executionHistory.slice(-limit);
  }

  clearCache(): void {
    this.responseCache.clear();
  }

  getCacheStats(): { size: number; hitRate: number } {
    const metrics = this.performanceMonitor.getMetrics();
    return {
      size: this.responseCache.size,
      hitRate: metrics.cacheHitRate
    };
  }

  getPerformanceMetrics(): string {
    return this.performanceMonitor.formatMetrics();
  }

  resetPerformanceMetrics(): void {
    this.performanceMonitor.reset();
  }
}