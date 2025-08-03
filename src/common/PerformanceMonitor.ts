export interface PerformanceMetrics {
  totalRequests: number;
  averageResponseTime: number;
  cacheHitRate: number;
  memoryUsage: NodeJS.MemoryUsage;
  toolLoadTimes: Map<string, number>;
  errorRate: number;
}

export class PerformanceMonitor {
  private metrics: {
    totalRequests: number;
    totalResponseTime: number;
    cacheHits: number;
    cacheMisses: number;
    errors: number;
    toolLoadTimes: Map<string, number>;
  };

  constructor() {
    this.metrics = {
      totalRequests: 0,
      totalResponseTime: 0,
      cacheHits: 0,
      cacheMisses: 0,
      errors: 0,
      toolLoadTimes: new Map()
    };
  }

  recordRequest(responseTime: number, isCacheHit = false, isError = false): void {
    this.metrics.totalRequests++;
    this.metrics.totalResponseTime += responseTime;
    
    if (isCacheHit) {
      this.metrics.cacheHits++;
    } else {
      this.metrics.cacheMisses++;
    }
    
    if (isError) {
      this.metrics.errors++;
    }
  }

  recordToolLoad(toolName: string, loadTime: number): void {
    this.metrics.toolLoadTimes.set(toolName, loadTime);
  }

  getMetrics(): PerformanceMetrics {
    const totalCacheRequests = this.metrics.cacheHits + this.metrics.cacheMisses;
    const cacheHitRate = totalCacheRequests > 0 
      ? (this.metrics.cacheHits / totalCacheRequests) * 100 
      : 0;

    const averageResponseTime = this.metrics.totalRequests > 0
      ? this.metrics.totalResponseTime / this.metrics.totalRequests
      : 0;

    const errorRate = this.metrics.totalRequests > 0
      ? (this.metrics.errors / this.metrics.totalRequests) * 100
      : 0;

    return {
      totalRequests: this.metrics.totalRequests,
      averageResponseTime,
      cacheHitRate,
      memoryUsage: process.memoryUsage(),
      toolLoadTimes: new Map(this.metrics.toolLoadTimes),
      errorRate
    };
  }

  reset(): void {
    this.metrics = {
      totalRequests: 0,
      totalResponseTime: 0,
      cacheHits: 0,
      cacheMisses: 0,
      errors: 0,
      toolLoadTimes: new Map()
    };
  }

  formatMetrics(): string {
    const metrics = this.getMetrics();
    
    return `
📊 Performance Metrics
=====================
Total Requests: ${metrics.totalRequests}
Average Response Time: ${metrics.averageResponseTime.toFixed(2)}ms
Cache Hit Rate: ${metrics.cacheHitRate.toFixed(2)}%
Error Rate: ${metrics.errorRate.toFixed(2)}%
Memory Usage:
  - RSS: ${(metrics.memoryUsage.rss / 1024 / 1024).toFixed(2)}MB
  - Heap Used: ${(metrics.memoryUsage.heapUsed / 1024 / 1024).toFixed(2)}MB
  - Heap Total: ${(metrics.memoryUsage.heapTotal / 1024 / 1024).toFixed(2)}MB

Tool Load Times:
${Array.from(metrics.toolLoadTimes.entries())
  .map(([tool, time]) => `  - ${tool}: ${time}ms`)
  .join('\n')}
    `.trim();
  }
}