import axios from 'axios';
import { BaseTool } from '../common/BaseTool';
import { ToolResponse, ToolStatus } from '../common/ToolResponse';

interface StoreParams extends Record<string, unknown> {
  operation: 'store';
  texts: string[];
  metadata?: Record<string, unknown>[];
}
interface SearchParams extends Record<string, unknown> {
  operation: 'search';
  query: string;
  limit?: number;
  scoreThreshold?: number;
}

export class VectorDatabaseTool extends BaseTool {
  private readonly host: string;
  private readonly port: number;
  private readonly collection: string;
  private readonly apiKey?: string;

  constructor(opts?: { host?: string; port?: number; collection?: string; apiKey?: string }) {
    super('vector_database_tool', 'Qdrant vector database wrapper', ['search', 'store', 'delete']);
    this.host = opts?.host ?? process.env.QDRANT_HOST ?? 'localhost';
    this.port = opts?.port ? Number(opts.port) : Number(process.env.QDRANT_PORT ?? '6333');
    this.collection = opts?.collection ?? 'deepcli_vectors';
    this.apiKey = opts?.apiKey ?? process.env.QDRANT_API_KEY;
  }

  async execute(params: Record<string, unknown>): Promise<ToolResponse> {
    const op = params.operation as string;
    if (op === 'store' && this.isStoreParams(params)) {
      return this.store(params);
    }
    if (op === 'search' && this.isSearchParams(params)) {
      return this.search(params);
    }
    return { success: false, message: `Unsupported op ${op}`, status: ToolStatus.FAILED };
  }

  private isStoreParams(params: Record<string, unknown>): params is StoreParams {
    return params.operation === 'store' && Array.isArray(params.texts);
  }

  private isSearchParams(params: Record<string, unknown>): params is SearchParams {
    return params.operation === 'search' && typeof params.query === 'string';
  }

  private async store({ texts, metadata = [] }: StoreParams): Promise<ToolResponse> {
    // minimal placeholder – no real embeddings
    return {
      success: true,
      message: `Pretended to store ${texts.length} embeddings`,
      status: ToolStatus.SUCCESS
    };
  }

  private async search({ query, limit = 10 }: SearchParams): Promise<ToolResponse> {
    // placeholder search returning empty list
    return {
      success: true,
      message: 'Search completed (placeholder)',
      data: { results: [] },
      status: ToolStatus.SUCCESS
    };
  }

  async ping(): Promise<boolean> {
    try {
      await axios.get(`http://${this.host}:${this.port}/collections`);
      return true;
    } catch {
      return false;
    }
  }

  getSchema(): Record<string, unknown> {
    return {
      type: 'object',
      properties: {
        operation: { type: 'string', enum: ['store', 'search'] }
      },
      required: ['operation']
    };
  }
}