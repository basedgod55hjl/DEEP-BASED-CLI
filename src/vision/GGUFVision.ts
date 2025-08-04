import { pipeline } from '@xenova/transformers';

export class GGUFVision {
  private static instance: GGUFVision;
  private captioner: any;

  private constructor() {}
  static async get(): Promise<GGUFVision> {
    if (!this.instance) {
      this.instance = new GGUFVision();
      this.instance.captioner = await pipeline('image-to-text', 'file://models/vision_llm.gguf');
    }
    return this.instance;
  }

  async describe(buffer: Uint8Array): Promise<string> {
    const res = await this.captioner(buffer, { max_length: 64 });
    return res[0]?.generated_text ?? 'No description';
  }
}