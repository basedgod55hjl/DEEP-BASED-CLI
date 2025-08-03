import { BaseTool } from '../common/BaseTool';
import { ToolResponse, ToolStatus } from '../common/ToolResponse';

export class SimpleEmbeddingTool extends BaseTool {
  constructor() {
    super('simple_embedding_tool', 'Local embedding placeholder', ['embed_texts']);
  }

  async execute(params: Record<string, unknown>): Promise<ToolResponse> {
    const text = (params.text as string) ?? '';
    const embedding = this.fakeEmbed(text);
    return {
      success: true,
      message: 'Embedding generated (fake)',
      status: ToolStatus.SUCCESS,
      data: { embedding }
    };
  }

  private fakeEmbed(text: string): number[] {
    // very naive hash to numbers
    return Array.from(text).map((c) => (c.charCodeAt(0) % 53) / 53);
  }

  getSchema(): Record<string, unknown> {
    return {
      type: 'object',
      properties: {
        text: { type: 'string' }
      },
      required: ['text']
    };
  }
}