import { planAgent } from '../agents/planner.js';
import { BaseTool } from '../common/BaseTool';
import { ToolResponse, ToolStatus } from '../common/ToolResponse';

export class PlannerTool extends BaseTool {
  constructor() {
    super('planner_tool', 'Generates rewrite plans', ['plan']);
  }

  async execute(params: Record<string, unknown>): Promise<ToolResponse> {
    const content = (params.content as string) ?? '';
    const plan = await planAgent.plan(content);
    return { success: true, message: 'Plan generated', status: ToolStatus.SUCCESS, data: { plan } };
  }

  getSchema(): Record<string, unknown> {
    return { type: 'object', properties: { content: { type: 'string' } }, required: ['content'] };
  }
}