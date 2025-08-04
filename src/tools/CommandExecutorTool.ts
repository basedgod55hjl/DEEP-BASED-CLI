import { BaseTool } from '../common/BaseTool';
import { ToolResponse, ToolStatus } from '../common/ToolResponse';
import { exec } from 'node:child_process';
import { promisify } from 'node:util';
const execAsync = promisify(exec);

export class CommandExecutorTool extends BaseTool {
  constructor() {
    super('command_executor_tool', 'Runs shell commands in sandbox', ['exec']);
  }

  async execute(params: Record<string, unknown>): Promise<ToolResponse> {
    const cmd = (params.command as string) ?? '';
    if (!cmd.startsWith('echo') && !cmd.startsWith('ls')) {
      return { success: false, message: 'Forbidden command', status: ToolStatus.FAILED };
    }
    const { stdout } = await execAsync(cmd);
    return { success: true, message: 'Command executed', status: ToolStatus.SUCCESS, data: { stdout } };
  }

  getSchema(): Record<string, unknown> {
    return { type: 'object', properties: { command: { type: 'string' } }, required: ['command'] };
  }
}