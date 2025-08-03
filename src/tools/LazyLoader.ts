/**
 * Lazy loader for heavy dependencies to improve startup performance
 */
export class LazyLoader {
  private static cache = new Map<string, Promise<any>>();

  static async loadTransformers() {
    if (!this.cache.has('transformers')) {
      this.cache.set('transformers', import('@xenova/transformers'));
    }
    return this.cache.get('transformers');
  }

  static async loadOnnxRuntime() {
    if (!this.cache.has('onnxruntime')) {
      this.cache.set('onnxruntime', import('onnxruntime-node'));
    }
    return this.cache.get('onnxruntime');
  }

  static async loadBetterSqlite3() {
    if (!this.cache.has('better-sqlite3')) {
      this.cache.set('better-sqlite3', import('better-sqlite3' as any));
    }
    return this.cache.get('better-sqlite3');
  }

  static async loadCheerio() {
    if (!this.cache.has('cheerio')) {
      this.cache.set('cheerio', import('cheerio'));
    }
    return this.cache.get('cheerio');
  }

  /**
   * Preload critical dependencies in the background
   */
  static preloadCritical() {
    // Preload in background without blocking startup
    setTimeout(() => {
      this.loadCheerio().catch(() => {}); // Most likely to be used
    }, 100);
  }

  /**
   * Clear the cache (useful for testing)
   */
  static clearCache() {
    this.cache.clear();
  }
}