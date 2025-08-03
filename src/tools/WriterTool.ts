import { writeAgent } from '../agents/writer.js';
import { BaseTool } from '../common/BaseTool';
import { ToolResponse, ToolStatus } from '../common/ToolResponse';

export class WriterTool extends BaseTool {
  constructor() {
    super('writer_tool', 'Rewrites files', ['rewrite']);
  }

  async execute(params: Record<string, unknown>): Promise<ToolResponse> {
    const path = (params.path as string) ?? '';
    const plan = (params.plan as string) ?? '';
    await writeAgent.rewrite(path, plan);
    return { success: true, message: 'File rewritten', status: ToolStatus.SUCCESS };
  }

  getSchema(): Record<string, unknown> {
    return {
      type: 'object',
      properties: { path: { type: 'string' }, plan: { type: 'string' } },
      required: ['path', 'plan']
    };
  }
}