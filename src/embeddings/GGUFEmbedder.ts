import { pipeline } from '@xenova/transformers';

export class GGUFEmbedder {
  private static instance: GGUFEmbedder;
  private extractor: any;

  private constructor() {}

  static async get(): Promise<GGUFEmbedder> {
    if (!this.instance) {
      this.instance = new GGUFEmbedder();
      this.instance.extractor = await pipeline('feature-extraction', 'file://models/llama_embedding_model.gguf', {
        quantized: false
      });
    }
    return this.instance;
  }

  async embed(text: string): Promise<number[]> {
    const out = await this.extractor(text, { pooling: 'mean' });
    return Array.from(out.data as Float32Array);
  }
}