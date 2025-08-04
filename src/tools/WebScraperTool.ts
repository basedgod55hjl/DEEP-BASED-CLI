import axios from 'axios';
import cheerio from 'cheerio';
import { BaseTool } from '../common/BaseTool';
import { ToolResponse, ToolStatus } from '../common/ToolResponse';
import { VisionTool } from './VisionTool';
import { SimpleEmbeddingTool } from './SimpleEmbeddingTool';
import { VectorDatabaseTool } from './VectorDatabaseTool';

export class WebScraperTool extends BaseTool {
  private readonly vision = new VisionTool();
  private readonly embedder = new SimpleEmbeddingTool();
  private readonly vector = new VectorDatabaseTool();

  constructor() {
    super('web_scraper_tool', 'Scrapes web pages and stores embeddings', ['scrape']);
  }

  async execute(params: Record<string, unknown>): Promise<ToolResponse> {
    const url = params.url as string;
    if (!url) return { success: false, message: 'url required', status: ToolStatus.FAILED };

    const html = (await axios.get(url)).data as string;
    const $ = cheerio.load(html);
    const text = $('body').text();

    // process images (first 3)
    const images = $('img').slice(0, 3).map((_, el) => $(el).attr('src')).get();
    const altProms: Promise<string>[] = images.map(async (src) => {
      try {
        const imgResp = await axios.get(src, { responseType: 'arraybuffer' });
        const buf = new Uint8Array(imgResp.data);
        const visionRes = await this.vision.execute({ image: buf });
        return visionRes.data?.description ?? '';
      } catch {
        return '';
      }
    });
    const alts = await Promise.all(altProms);

    // embed text
    const embRes = await this.embedder.execute({ text });
    await this.vector.execute({ operation: 'store', texts: [text], metadata: [{ url }] });

    return {
      success: true,
      message: 'Page scraped',
      status: ToolStatus.SUCCESS,
      data: { textLength: text.length, images: images.length, altTexts: alts }
    };
  }

  getSchema(): Record<string, unknown> {
    return { type: 'object', properties: { url: { type: 'string' } }, required: ['url'] };
  }
}