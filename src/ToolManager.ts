import { BaseTool } from './common/BaseTool';
import { ToolResponse, ToolStatus } from './common/ToolResponse';
import { toolFactories } from './tools/index.js';

/**
 * Dynamic Tool Manager (TypeScript)
 * Automatically discovers all exports in src/tools and instantiates them.
 */
export class ToolManager {
  private readonly tools: Record<string, BaseTool> = {};
  private readonly executionHistory: Array<{ name: string; params: Record<string, unknown>; response: ToolResponse }> = [];

  constructor() {
    // No eager registration – tools load on demand.
  }

  private async loadTool(name: string): Promise<BaseTool | undefined> {
    const key = name.toLowerCase();
    if (this.tools[key]) {
      return this.tools[key];
    }
    const factory = toolFactories[key];
    if (!factory) {
      return undefined;
    }
    try {
      const instance = await factory();
      this.tools[key] = instance;
      // eslint-disable-next-line no-console
      console.log(`🔧 Loaded tool: ${instance.constructor.name}`);
      return instance;
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error(`Failed to load tool ${name}:`, err);
      return undefined;
    }
  }

  listTools(): string[] {
    return Object.keys(toolFactories);
  }

  getTool(name: string): BaseTool | undefined {
    return this.tools[name.toLowerCase()];
  }

  async executeTool(name: string, params: Record<string, unknown>): Promise<ToolResponse> {
    const tool = await this.loadTool(name);
    if (!tool) {
      return {
        success: false,
        message: `Tool ${name} not found`,
        status: ToolStatus.FAILED
      };
    }

    const t0 = Date.now();
    const response = await tool.execute(params);
    response.executionTime = (Date.now() - t0) / 1000;

    this.executionHistory.push({ name, params, response });
    return response;
  }

  history(limit = 20): Array<{ name: string; params: Record<string, unknown>; response: ToolResponse }> {
    return this.executionHistory.slice(-limit);
  }
}