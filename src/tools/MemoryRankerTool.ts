import { BaseTool } from '../common/BaseTool';
import { ToolResponse, ToolStatus } from '../common/ToolResponse';
import { GGUFEmbedder } from '../embeddings/GGUFEmbedder.js';

interface RankParams {
  query: string;
  texts: string[];
  topK?: number;
}

function cosine(a: number[], b: number[]): number {
  let dot = 0, na = 0, nb = 0;
  for (let i = 0; i < a.length; i++) {
    dot += a[i] * b[i];
    na += a[i] * a[i];
    nb += b[i] * b[i];
  }
  return dot / (Math.sqrt(na) * Math.sqrt(nb) + 1e-8);
}

export class MemoryRankerTool extends BaseTool {
  constructor() { super('memory_ranker_tool', 'Ranks texts by semantic similarity to query', ['rank']); }

  async execute(params: Record<string, unknown>): Promise<ToolResponse> {
    const { query, texts, topK = 5 } = params as unknown as RankParams;
    if (!query || !texts?.length) return { success: false, message: 'query and texts required', status: ToolStatus.FAILED };
    const embedder = await GGUFEmbedder.get();
    const qEmb = await embedder.embed(query);
    const scored = [] as Array<{ text: string; score: number }>;
    for (const t of texts) {
      const e = await embedder.embed(t);
      scored.push({ text: t, score: cosine(qEmb, e) });
    }
    scored.sort((a, b) => b.score - a.score);
    return { success: true, message: 'Ranked', status: ToolStatus.SUCCESS, data: { results: scored.slice(0, topK) } };
  }

  getSchema(): Record<string, unknown> {
    return { type: 'object', properties: { query: { type: 'string' }, texts: { type: 'array', items: { type: 'string' } }, topK: { type: 'number' } }, required: ['query', 'texts'] };
  }
}