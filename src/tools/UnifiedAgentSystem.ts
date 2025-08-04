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
    const prompt = (p.message as string) ?? '';
    const personaName = ((p.persona as string) ?? 'deanna').toLowerCase();

    // Attempt to load persona definition from data/memory folder
    let systemContent = '';
    try {
      const path = await import('node:path');
      const fs = await import('node:fs/promises');
      const personaPath = path.resolve('data', 'memory', `persona_${personaName}.json`);

      try {
        const raw = await fs.readFile(personaPath, 'utf8');
        const json = JSON.parse(raw);
        // Build a compact system prompt based on json fields
        systemContent = [
          json.description ?? '',
          json.personality_traits ? `Traits: ${json.personality_traits.join(', ')}` : '',
          json.conversation_style ? `Style guide: ${json.conversation_style}` : ''
        ]
          .filter(Boolean)
          .join('\n');
      } catch {
        /* ignore if file missing */
      }
    } catch {
      /* ignore dynamic import errors */
    }

    const messages = systemContent
      ? ([{ role: 'system', content: systemContent }, { role: 'user', content: prompt }])
      : undefined;

    return this.llm.execute(
      messages
        ? { operation: 'chat_completion', messages }
        : { operation: 'chat_completion', prompt }
    );
  }

  getSchema(): Record<string, unknown> {
    return {
      type: 'object',
      properties: {
        operation: { type: 'string' },
        message: { type: 'string' },
        persona: { type: 'string' },
        query: { type: 'string' },
        problem: { type: 'string' }
      }
    };
  }
}