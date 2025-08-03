/**
 * Lightweight alternatives to heavy dependencies
 */

// Lightweight HTTP client (alternative to axios for simple requests)
export class LightHttpClient {
  static async get(url: string, options: { timeout?: number; headers?: Record<string, string> } = {}) {
    const { timeout = 10000, headers = {} } = options;
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);
    
    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'User-Agent': 'DeepCLI/1.0',
          ...headers
        },
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      return {
        data: await response.text(),
        status: response.status,
        headers: Object.fromEntries(response.headers.entries())
      };
    } catch (error) {
      clearTimeout(timeoutId);
      throw error;
    }
  }

  static async post(url: string, data: any, options: { timeout?: number; headers?: Record<string, string> } = {}) {
    const { timeout = 10000, headers = {} } = options;
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);
    
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'User-Agent': 'DeepCLI/1.0',
          ...headers
        },
        body: JSON.stringify(data),
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      return {
        data: await response.json(),
        status: response.status,
        headers: Object.fromEntries(response.headers.entries())
      };
    } catch (error) {
      clearTimeout(timeoutId);
      throw error;
    }
  }
}

// Lightweight HTML parser (alternative to cheerio for simple parsing)
export class LightHTMLParser {
  private html: string;

  constructor(html: string) {
    this.html = html;
  }

  static load(html: string) {
    return new LightHTMLParser(html);
  }

  text(): string {
    // Remove script and style tags
    let cleaned = this.html.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
    cleaned = cleaned.replace(/<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>/gi, '');
    
    // Remove HTML tags
    cleaned = cleaned.replace(/<[^>]*>/g, ' ');
    
    // Clean up whitespace
    cleaned = cleaned.replace(/\s+/g, ' ').trim();
    
    return cleaned;
  }

  find(selector: string): { attr: (name: string) => string | null; text: () => string }[] {
    const results: { attr: (name: string) => string | null; text: () => string }[] = [];
    
    if (selector === 'img') {
      const imgRegex = /<img[^>]+>/gi;
      const matches = this.html.match(imgRegex) || [];
      
      for (const match of matches) {
        results.push({
          attr: (name: string) => {
            const attrRegex = new RegExp(`${name}=["']([^"']+)["']`, 'i');
            const attrMatch = match.match(attrRegex);
            return attrMatch ? attrMatch[1] : null;
          },
          text: () => ''
        });
      }
    }
    
    return results;
  }
}

// Lightweight embedding alternative (placeholder for @xenova/transformers)
export class LightEmbedding {
  static async embed(text: string): Promise<number[]> {
    // Simple hash-based embedding (not semantic, but lightweight)
    const hash = this.simpleHash(text);
    const embedding = new Array(384).fill(0); // Standard embedding size
    
    // Create pseudo-embedding from hash
    for (let i = 0; i < 384; i++) {
      embedding[i] = Math.sin(hash + i) * 0.1;
    }
    
    return embedding;
  }

  private static simpleHash(str: string): number {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return hash;
  }

  static cosineSimilarity(a: number[], b: number[]): number {
    if (a.length !== b.length) return 0;
    
    let dotProduct = 0;
    let normA = 0;
    let normB = 0;
    
    for (let i = 0; i < a.length; i++) {
      dotProduct += a[i] * b[i];
      normA += a[i] * a[i];
      normB += b[i] * b[i];
    }
    
    return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
  }
}

// Lightweight logging (alternative to pino for simple cases)
export class LightLogger {
  constructor(private name: string) {}

  info(message: string, ...args: any[]) {
    console.log(`[${new Date().toISOString()}] INFO [${this.name}]: ${message}`, ...args);
  }

  error(message: string, ...args: any[]) {
    console.error(`[${new Date().toISOString()}] ERROR [${this.name}]: ${message}`, ...args);
  }

  warn(message: string, ...args: any[]) {
    console.warn(`[${new Date().toISOString()}] WARN [${this.name}]: ${message}`, ...args);
  }

  debug(message: string, ...args: any[]) {
    if (process.env.DEBUG) {
      console.debug(`[${new Date().toISOString()}] DEBUG [${this.name}]: ${message}`, ...args);
    }
  }
}

// Performance monitoring utilities
export class PerformanceMonitor {
  private static timers = new Map<string, number>();

  static start(label: string) {
    this.timers.set(label, performance.now());
  }

  static end(label: string): number {
    const start = this.timers.get(label);
    if (!start) return 0;
    
    const duration = performance.now() - start;
    this.timers.delete(label);
    return duration;
  }

  static measure<T>(label: string, fn: () => T): T {
    this.start(label);
    try {
      const result = fn();
      const duration = this.end(label);
      console.log(`[PERF] ${label}: ${duration.toFixed(2)}ms`);
      return result;
    } catch (error) {
      this.end(label);
      throw error;
    }
  }

  static async measureAsync<T>(label: string, fn: () => Promise<T>): Promise<T> {
    this.start(label);
    try {
      const result = await fn();
      const duration = this.end(label);
      console.log(`[PERF] ${label}: ${duration.toFixed(2)}ms`);
      return result;
    } catch (error) {
      this.end(label);
      throw error;
    }
  }
}