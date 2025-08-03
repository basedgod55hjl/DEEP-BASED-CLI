import { reviewAgent } from '../agents/reviewer.js';
import { BaseTool } from '../common/BaseTool';
import { ToolResponse, ToolStatus } from '../common/ToolResponse';

export class ReviewerTool extends BaseTool {
  constructor() {
    super('reviewer_tool', 'Reviews rewritten code', ['review']);
  }

  async execute(params: Record<string, unknown>): Promise<ToolResponse> {
    const original = (params.original as string) ?? '';
    const rewritten = (params.rewritten as string) ?? '';
    const ok = await reviewAgent.review(original, rewritten);
    return { success: ok, message: ok ? 'Review passed' : 'Review failed', status: ok ? ToolStatus.SUCCESS : ToolStatus.FAILED };
  }

  getSchema(): Record<string, unknown> {
    return {
      type: 'object',
      properties: { original: { type: 'string' }, rewritten: { type: 'string' } },
      required: ['original', 'rewritten']
    };
  }
}