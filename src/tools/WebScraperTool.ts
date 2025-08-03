import { BaseTool } from '../common/BaseTool';
import { ToolResponse, ToolStatus } from '../common/ToolResponse';
import { VisionTool } from './VisionTool';
import { SimpleEmbeddingTool } from './SimpleEmbeddingTool';
import { VectorDatabaseTool } from './VectorDatabaseTool';
import { LazyLoader } from './LazyLoader';
import { LightHttpClient, LightHTMLParser, PerformanceMonitor } from './LightweightAlternatives';

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

    return await PerformanceMonitor.measureAsync('web-scraping', async () => {
      // Try lightweight parser first, fallback to cheerio for complex pages
      let html: string;
      let $: any;
      let text: string;

      try {
        const response = await LightHttpClient.get(url);
        html = response.data;
        
        // Try lightweight parser
        const lightParser = LightHTMLParser.load(html);
        text = lightParser.text();
        
        // If text is too short, use cheerio for better parsing
        if (text.length < 100) {
          const cheerio = await LazyLoader.loadCheerio();
          $ = cheerio.load(html);
          text = $('body').text();
        } else {
          $ = lightParser;
        }
      } catch (error) {
        // Fallback to axios + cheerio for complex cases
        const axios = (await import('axios')).default;
        html = (await axios.get(url)).data as string;
        const cheerio = await LazyLoader.loadCheerio();
        $ = cheerio.load(html);
        text = $('body').text();
      }

      // process images (first 3) - handle both cheerio and light parser
      let images: string[] = [];
      if (typeof $.find === 'function') {
        // Cheerio parser
        images = $('img').slice(0, 3).map((_: any, el: any) => $(el).attr('src')).get();
      } else {
        // Light parser
        const imgElements = $.find('img');
        images = imgElements.slice(0, 3).map((el: any) => el.attr('src')).filter(Boolean);
      }

      const altProms: Promise<string>[] = images.map(async (src) => {
        try {
          const axios = (await import('axios')).default;
          const imgResp = await axios.get(src, { responseType: 'arraybuffer' });
          const buf = new Uint8Array(imgResp.data);
          const visionRes = await this.vision.execute({ image: buf });
          return (visionRes.data as any)?.description ?? '';
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
    });
  }

  getSchema(): Record<string, unknown> {
    return { type: 'object', properties: { url: { type: 'string' } }, required: ['url'] };
  }
}