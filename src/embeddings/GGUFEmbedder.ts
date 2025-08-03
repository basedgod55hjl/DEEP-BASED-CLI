import { pipeline } from '@xenova/transformers';
import { logger } from '../common/logger.js';

export class GGUFEmbedder {
  private static instance: GGUFEmbedder;
  private extractor: any;

  private constructor() {}

  static async get(): Promise<GGUFEmbedder> {
    if (!this.instance) {
      this.instance = new GGUFEmbedder();
      try {
        this.instance.extractor = await pipeline('feature-extraction', 'file://models/llama_embedding_model.gguf', { quantized: false });
      } catch (e) {
        logger.warn('GGUF model load failed, falling back to hash embeddings');
        this.instance.extractor = null;
      }
    }
    return this.instance;
  }

  async embed(text: string): Promise<number[]> {
    if (!this.extractor) {
      // fallback simple hash
      return Array.from(text).map((c) => (c.charCodeAt(0) % 37) / 37);
    }
    const out = await this.extractor(text, { pooling: 'mean' });
    return Array.from(out.data as Float32Array);
  }
}