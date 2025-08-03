import { BaseTool } from '../common/BaseTool';
import { ToolResponse, ToolStatus } from '../common/ToolResponse';
import { LLMQueryTool } from './LLMQueryTool';
import { VectorDatabaseTool } from './VectorDatabaseTool';
import { SQLDatabaseTool } from './SQLDatabaseTool';
import { FastReasoningEngine } from './FastReasoningEngine';
import { RAGPipelineTool } from './RAGPipelineTool';

export class UnifiedAgentSystem extends BaseTool {
  private readonly llm = new LLMQueryTool();
  private readonly vector = new VectorDatabaseTool();
  private readonly sql = new SQLDatabaseTool();
  private readonly reasoning = new FastReasoningEngine(this.llm);
  private readonly rag = new RAGPipelineTool(this.vector, this.llm);

  constructor() {
    super('unified_agent_system', 'Minimal unified agent wrapper (stub)', [
      'conversation',
      'memory_retrieval',
      'reasoning',
      'rag_query'
    ]);
  }

  async execute(params: Record<string, unknown>): Promise<ToolResponse> {
    const op = (params.operation as string) ?? 'conversation';
    switch (op) {
      case 'conversation':
        return this.conversation(params);
      case 'memory_retrieval':
        return this.vector.execute({ operation: 'search', query: params.query ?? '', limit: 5 });
      case 'reasoning':
        return this.reasoning.execute({ problem: params.problem ?? '' });
      case 'rag_query':
        return this.rag.execute({ query: params.query ?? '' });
      default:
        return { success: false, message: `Unknown op ${op}`, status: ToolStatus.FAILED };
    }
  }

  private async conversation(p: Record<string, unknown>): Promise<ToolResponse> {
    const prompt = p.message as string;
    return this.llm.execute({ operation: 'chat_completion', prompt });
  }

  getSchema(): Record<string, unknown> {
    return {
      type: 'object',
      properties: {
        operation: { type: 'string' },
        message: { type: 'string' },
        query: { type: 'string' },
        problem: { type: 'string' }
      }
    };
  }
}