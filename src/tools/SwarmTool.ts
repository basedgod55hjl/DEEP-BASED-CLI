import { BaseTool } from '../common/BaseTool';
import { ToolResponse, ToolStatus } from '../common/ToolResponse';
import { ToolManager } from '../ToolManager.js';

export class SwarmTool extends BaseTool {
  private readonly tm = new ToolManager();
  constructor() { super('swarm_tool', 'Orchestrates multiple agent tools to accomplish a coding task', ['execute_task']); }

  async execute(params: Record<string, unknown>): Promise<ToolResponse> {
    const task = params.task as string;
    if (!task) return { success: false, message: 'task required', status: ToolStatus.FAILED };

    // 1. Plan
    const planRes = await this.tm.executeTool('plannertool', { content: task });
    const plan = (planRes.data as any)?.plan ?? '';

    // 2. Code generation
    const codeRes = await this.tm.executeTool('coderagenttool', {
      language: 'typescript',
      description: task,
      style: 'clean'
    });
    const code = (codeRes.data as any)?.code ?? '';

    // 3. Review
    const reviewRes = await this.tm.executeTool('reviewertool', {
      original: '',
      rewritten: code
    });

    return {
      success: true,
      message: 'Swarm task executed',
      status: ToolStatus.SUCCESS,
      data: {
        plan,
        code,
        reviewPassed: reviewRes.success
      }
    };
  }

  getSchema(): Record<string, unknown> {
    return { type: 'object', properties: { task: { type: 'string' } }, required: ['task'] };
  }
}