import { BaseTool } from '../common/BaseTool';
import { ToolResponse, ToolStatus } from '../common/ToolResponse';

export class DebuggerTool extends BaseTool {
  constructor() {
    super('debugger_tool', 'Provides debugging instructions', ['debug']);
  }

  async execute(params: Record<string, unknown>): Promise<ToolResponse> {
    const script = params.script ?? 'app.js';
    const message = `Run: node --inspect-brk ${script} and open chrome://inspect`;
    return { success: true, message, status: ToolStatus.SUCCESS };
  }

  getSchema(): Record<string, unknown> {
    return { type: 'object', properties: { script: { type: 'string' } } };
  }
}