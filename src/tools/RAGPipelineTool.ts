import { BaseTool } from '../common/BaseTool';
import { ToolResponse, ToolStatus } from '../common/ToolResponse';
import { VectorDatabaseTool } from './VectorDatabaseTool';
import { LLMQueryTool } from './LLMQueryTool';

export class RAGPipelineTool extends BaseTool {
  private readonly vector: VectorDatabaseTool;
  private readonly llm: LLMQueryTool;

  constructor(vector = new VectorDatabaseTool(), llm = new LLMQueryTool()) {
    super('rag_pipeline_tool', 'Retrieval-augmented generation (stub)', ['rag_query']);
    this.vector = vector;
    this.llm = llm;
  }

  async execute(params: Record<string, unknown>): Promise<ToolResponse> {
    const query = (params.query as string) ?? '';

    // placeholder: no real search, just echo
    const llmRes = await this.llm.execute({ operation: 'chat_completion', prompt: `Answer as best you can: ${query}` });

    return {
      success: true,
      message: 'RAG response ready',
      status: ToolStatus.SUCCESS,
      data: {
        response: llmRes.data?.response,
        sources: []
      }
    };
  }

  getSchema(): Record<string, unknown> {
    return {
      type: 'object',
      properties: {
        query: { type: 'string' }
      },
      required: ['query']
    };
  }
}