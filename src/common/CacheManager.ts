import * as fs from 'fs';
import * as path from 'path';
import * as crypto from 'crypto';

export interface CacheOptions {
  ttl?: number; // Time to live in milliseconds
  maxSize?: number; // Maximum cache size in MB
  diskCache?: boolean; // Enable disk caching
}

export interface CacheItem<T> {
  value: T;
  timestamp: number;
  ttl?: number;
  size?: number;
}

export class CacheManager {
  private memoryCache = new Map<string, CacheItem<any>>();
  private cacheDir: string;
  private maxMemorySize: number;
  private currentMemorySize = 0;

  constructor(private options: CacheOptions = {}) {
    this.maxMemorySize = (options.maxSize || 100) * 1024 * 1024; // Convert MB to bytes
    this.cacheDir = path.join(process.cwd(), '.cache');
    
    if (options.diskCache && !fs.existsSync(this.cacheDir)) {
      fs.mkdirSync(this.cacheDir, { recursive: true });
    }
  }

  /**
   * Generate a cache key from input parameters
   */
  private generateKey(input: string | object): string {
    const str = typeof input === 'string' ? input : JSON.stringify(input);
    return crypto.createHash('md5').update(str).digest('hex');
  }

  /**
   * Get item from cache
   */
  async get<T>(key: string): Promise<T | null> {
    const cacheKey = this.generateKey(key);
    
    // Check memory cache first
    const memItem = this.memoryCache.get(cacheKey);
    if (memItem && this.isValid(memItem)) {
      return memItem.value;
    }

    // Check disk cache if enabled
    if (this.options.diskCache) {
      const diskItem = await this.getDiskCache<T>(cacheKey);
      if (diskItem) {
        // Promote to memory cache
        this.setMemoryCache(cacheKey, diskItem);
        return diskItem.value;
      }
    }

    return null;
  }

  /**
   * Set item in cache
   */
  async set<T>(key: string, value: T, ttl?: number): Promise<void> {
    const cacheKey = this.generateKey(key);
    const item: CacheItem<T> = {
      value,
      timestamp: Date.now(),
      ttl: ttl || this.options.ttl,
      size: this.estimateSize(value)
    };

    // Set in memory cache
    this.setMemoryCache(cacheKey, item);

    // Set in disk cache if enabled
    if (this.options.diskCache) {
      await this.setDiskCache(cacheKey, item);
    }
  }

  /**
   * Cache a function result
   */
  async memoize<T>(
    key: string,
    fn: () => Promise<T>,
    ttl?: number
  ): Promise<T> {
    const cached = await this.get<T>(key);
    if (cached !== null) {
      return cached;
    }

    const result = await fn();
    await this.set(key, result, ttl);
    return result;
  }

  /**
   * Clear cache
   */
  clear(): void {
    this.memoryCache.clear();
    this.currentMemorySize = 0;
    
    if (this.options.diskCache && fs.existsSync(this.cacheDir)) {
      fs.rmSync(this.cacheDir, { recursive: true, force: true });
      fs.mkdirSync(this.cacheDir, { recursive: true });
    }
  }

  /**
   * Get cache statistics
   */
  getStats() {
    return {
      memoryItems: this.memoryCache.size,
      memorySize: this.currentMemorySize,
      maxMemorySize: this.maxMemorySize,
      memoryUsage: (this.currentMemorySize / this.maxMemorySize) * 100
    };
  }

  private isValid(item: CacheItem<any>): boolean {
    if (!item.ttl) return true;
    return (Date.now() - item.timestamp) < item.ttl;
  }

  private setMemoryCache<T>(key: string, item: CacheItem<T>): void {
    // Remove old item if exists
    const oldItem = this.memoryCache.get(key);
    if (oldItem?.size) {
      this.currentMemorySize -= oldItem.size;
    }

    // Add new item
    this.memoryCache.set(key, item);
    if (item.size) {
      this.currentMemorySize += item.size;
    }

    // Evict items if over memory limit
    this.evictIfNeeded();
  }

  private evictIfNeeded(): void {
    if (this.currentMemorySize <= this.maxMemorySize) return;

    // Sort by timestamp (LRU)
    const entries = Array.from(this.memoryCache.entries())
      .sort(([, a], [, b]) => a.timestamp - b.timestamp);

    for (const [key, item] of entries) {
      this.memoryCache.delete(key);
      if (item.size) {
        this.currentMemorySize -= item.size;
      }
      
      if (this.currentMemorySize <= this.maxMemorySize * 0.8) break;
    }
  }

  private async getDiskCache<T>(key: string): Promise<CacheItem<T> | null> {
    try {
      const filePath = path.join(this.cacheDir, `${key}.json`);
      if (!fs.existsSync(filePath)) return null;

      const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
      const item: CacheItem<T> = data;
      
      if (!this.isValid(item)) {
        fs.unlinkSync(filePath);
        return null;
      }

      return item;
    } catch {
      return null;
    }
  }

  private async setDiskCache<T>(key: string, item: CacheItem<T>): Promise<void> {
    try {
      const filePath = path.join(this.cacheDir, `${key}.json`);
      fs.writeFileSync(filePath, JSON.stringify(item));
    } catch {
      // Ignore disk cache errors
    }
  }

  private estimateSize(value: any): number {
    try {
      return JSON.stringify(value).length * 2; // Rough estimate
    } catch {
      return 1024; // Default size
    }
  }
}

// Global cache instance
export const globalCache = new CacheManager({
  ttl: 30 * 60 * 1000, // 30 minutes
  maxSize: 50, // 50MB
  diskCache: true
});