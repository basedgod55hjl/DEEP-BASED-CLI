import { BaseTool } from './common/BaseTool';
import { ToolResponse, ToolStatus } from './common/ToolResponse';
import * as ToolExports from './tools/index.js';

/**
 * Dynamic Tool Manager (TypeScript)
 * Automatically discovers all exports in src/tools and instantiates them.
 */
export class ToolManager {
  private readonly tools: Record<string, BaseTool> = {};
  private readonly executionHistory: Array<{ name: string; params: Record<string, unknown>; response: ToolResponse }> = [];

  constructor() {
    this.autoRegisterTools();
  }

  private autoRegisterTools(): void {
    for (const [exportName, exported] of Object.entries(ToolExports)) {
      // Only attempt to instantiate classes that extend BaseTool
      if (typeof exported === 'function') {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const MaybeClass = exported as any;
        const instance: unknown = new MaybeClass();
        if (instance instanceof BaseTool) {
          const key = MaybeClass.name.toLowerCase();
          this.tools[key] = instance;
          // eslint-disable-next-line no-console
          console.log(`🔧 Registered tool: ${MaybeClass.name}`);
        }
      }
    }
  }

  listTools(): string[] {
    return Object.keys(this.tools);
  }

  getTool(name: string): BaseTool | undefined {
    return this.tools[name.toLowerCase()];
  }

  async executeTool(name: string, params: Record<string, unknown>): Promise<ToolResponse> {
    const tool = this.getTool(name);
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