import { readerAgent } from '../agents/reader.js';
import { BaseTool } from '../common/BaseTool';
import { ToolResponse, ToolStatus } from '../common/ToolResponse';

export class ReaderTool extends BaseTool {
  constructor() {
    super('reader_tool', 'Loads file contents', ['read']);
  }

  async execute(params: Record<string, unknown>): Promise<ToolResponse> {
    const path = (params.path as string) ?? '';
    const content = await readerAgent.loadFile(path);
    return { success: true, message: 'File loaded', status: ToolStatus.SUCCESS, data: { content } };
  }

  getSchema(): Record<string, unknown> {
    return { type: 'object', properties: { path: { type: 'string' } }, required: ['path'] };
  }
}