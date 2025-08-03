import { BaseTool } from '../common/BaseTool';
import { ToolResponse, ToolStatus } from '../common/ToolResponse';
import { GGUFEmbedder } from '../embeddings/GGUFEmbedder.js';

export class SimpleEmbeddingTool extends BaseTool {
  constructor() {
    super('simple_embedding_tool', 'Local embedding placeholder', ['embed_texts']);
  }

  async execute(params: Record<string, unknown>): Promise<ToolResponse> {
    const text = (params.text as string) ?? '';
    const embedder = await GGUFEmbedder.get();
    const embedding = await embedder.embed(text);
    return {
      success: true,
      message: 'Embedding generated',
      status: ToolStatus.SUCCESS,
      data: { embedding }
    };
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