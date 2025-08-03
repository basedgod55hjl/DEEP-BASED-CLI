import { BaseTool } from '../common/BaseTool';
import { ToolResponse, ToolStatus } from '../common/ToolResponse';
import { exec } from 'node:child_process';
import { promisify } from 'node:util';
const execAsync = promisify(exec);

export class SelfHealerTool extends BaseTool {
  constructor() {
    super('self_healer_tool', 'Runs test suite and suggests fixes', ['heal']);
  }

  async execute(): Promise<ToolResponse> {
    try {
      const { stdout } = await execAsync('npm test --silent');
      const success = !stdout.includes('FAIL');
      return {
        success,
        message: success ? 'All tests passing' : 'Tests failing',
        status: success ? ToolStatus.SUCCESS : ToolStatus.FAILED,
        data: { output: stdout }
      };
    } catch (err: any) {
      return { success: false, message: err.message, status: ToolStatus.FAILED };
    }
  }

  getSchema(): Record<string, unknown> {
    return { type: 'object', properties: {} };
  }
}