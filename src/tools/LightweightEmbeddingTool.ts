import { BaseTool } from '../common/BaseTool';
import { ToolResponse, ToolStatus } from '../common/ToolResponse';

export class LightweightEmbeddingTool extends BaseTool {
  constructor() {
    super('lightweight_embedding_tool', 'Lightweight embedding generator (no heavy deps)', [
      'generate_embedding',
      'similarity',
      'batch_embedding'
    ]);
  }

  async execute(params: Record<string, unknown>): Promise<ToolResponse> {
    const operation = params.operation as string;
    
    try {
      switch (operation) {
        case 'generate_embedding':
          return await this.generateEmbedding(params.text as string);
        case 'similarity':
          return await this.calculateSimilarity(params.text1 as string, params.text2 as string);
        case 'batch_embedding':
          return await this.batchEmbedding(params.texts as string[]);
        default:
          return {
            success: false,
            message: `Unsupported operation: ${operation}`,
            status: ToolStatus.FAILED
          };
      }
    } catch (err: any) {
      return {
        success: false,
        message: `Embedding error: ${err.message}`,
        status: ToolStatus.FAILED,
        data: { error: err }
      };
    }
  }

  private async generateEmbedding(text: string): Promise<ToolResponse> {
    // Simple hash-based embedding for lightweight use
    const embedding = this.simpleHashEmbedding(text);
    
    return {
      success: true,
      message: 'Embedding generated successfully',
      status: ToolStatus.SUCCESS,
      data: {
        embedding,
        dimension: embedding.length,
        text
      }
    };
  }

  private async calculateSimilarity(text1: string, text2: string): Promise<ToolResponse> {
    const embedding1 = this.simpleHashEmbedding(text1);
    const embedding2 = this.simpleHashEmbedding(text2);
    
    const similarity = this.cosineSimilarity(embedding1, embedding2);
    
    return {
      success: true,
      message: 'Similarity calculated successfully',
      status: ToolStatus.SUCCESS,
      data: {
        similarity,
        text1,
        text2
      }
    };
  }

  private async batchEmbedding(texts: string[]): Promise<ToolResponse> {
    const embeddings = texts.map(text => ({
      text,
      embedding: this.simpleHashEmbedding(text)
    }));
    
    return {
      success: true,
      message: `Generated ${embeddings.length} embeddings`,
      status: ToolStatus.SUCCESS,
      data: {
        embeddings
      }
    };
  }

  private simpleHashEmbedding(text: string): number[] {
    // Simple hash-based embedding (not as good as real embeddings but lightweight)
    const hash = this.hashString(text);
    const embedding = new Array(128).fill(0);
    
    for (let i = 0; i < 128; i++) {
      embedding[i] = Math.sin(hash + i) * 0.5 + 0.5;
    }
    
    return embedding;
  }

  private hashString(str: string): number {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return hash;
  }

  private cosineSimilarity(vec1: number[], vec2: number[]): number {
    if (vec1.length !== vec2.length) {
      throw new Error('Vectors must have same length');
    }
    
    let dotProduct = 0;
    let norm1 = 0;
    let norm2 = 0;
    
    for (let i = 0; i < vec1.length; i++) {
      dotProduct += vec1[i] * vec2[i];
      norm1 += vec1[i] * vec1[i];
      norm2 += vec2[i] * vec2[i];
    }
    
    return dotProduct / (Math.sqrt(norm1) * Math.sqrt(norm2));
  }

  getSchema(): Record<string, unknown> {
    return {
      type: 'object',
      properties: {
        operation: {
          type: 'string',
          enum: ['generate_embedding', 'similarity', 'batch_embedding'],
          description: 'Embedding operation type'
        },
        text: { type: 'string', description: 'Text to embed' },
        text1: { type: 'string', description: 'First text for similarity' },
        text2: { type: 'string', description: 'Second text for similarity' },
        texts: { 
          type: 'array', 
          items: { type: 'string' },
          description: 'Array of texts for batch embedding'
        }
      },
      required: ['operation']
    };
  }
}