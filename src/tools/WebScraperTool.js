/**
 * Web Scraper Tool with DeepSeek Integration
 * Advanced web scraping with AI-powered content extraction
 * Made by @Lucariolucario55 on Telegram
 */

import puppeteer from 'puppeteer';
import cheerio from 'cheerio';
import axios from 'axios';
import osmosis from 'osmosis';
import { v4 as uuidv4 } from 'uuid';
import chalk from 'chalk';
import fs from 'fs-extra';
import path from 'path';

export class WebScraperTool {
    constructor() {
        this.name = 'web_scraper';
        this.description = 'Advanced web scraping with AI-powered content extraction';
        this.version = '1.0.0';
        
        // Configuration
        this.config = {
            userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            timeout: 30000,
            maxRetries: 3,
            delay: 1000,
            headless: true,
            viewport: { width: 1920, height: 1080 },
            maxConcurrent: 5
        };
        
        // Browser instance
        this.browser = null;
        this.activePages = new Set();
        
        // Cache
        this.cache = new Map();
        this.cacheDir = 'data/scraper_cache';
        
        // Initialize
        this.initialize();
    }
    
    async initialize() {
        try {
            // Ensure cache directory exists
            await fs.ensureDir(this.cacheDir);
            
            // Initialize browser
            await this.initializeBrowser();
            
            console.log(chalk.green('✅ Web Scraper Tool initialized'));
            
        } catch (error) {
            console.error(chalk.red('❌ Failed to initialize Web Scraper Tool:'), error);
            throw error;
        }
    }
    
    async initializeBrowser() {
        try {
            this.browser = await puppeteer.launch({
                headless: this.config.headless,
                args: [
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--single-process',
                    '--disable-gpu'
                ]
            });
            
            console.log(chalk.blue('🌐 Browser initialized'));
            
        } catch (error) {
            console.error(chalk.red('❌ Failed to initialize browser:'), error);
            throw error;
        }
    }
    
    async scrape(url, selectors = {}, config = {}) {
        const scrapeId = uuidv4();
        const startTime = Date.now();
        
        try {
            console.log(chalk.blue(`🔍 Scraping: ${url}`));
            
            // Check cache first
            const cached = await this.getCachedResult(url);
            if (cached) {
                console.log(chalk.yellow('📋 Using cached result'));
                return {
                    scrapeId,
                    url,
                    cached: true,
                    data: cached,
                    timestamp: new Date().toISOString(),
                    duration: Date.now() - startTime
                };
            }
            
            // Merge configs
            const finalConfig = { ...this.config, ...config };
            
            // Determine scraping method
            const method = this.determineScrapingMethod(url, selectors);
            
            let result;
            
            switch (method) {
                case 'puppeteer':
                    result = await this.scrapeWithPuppeteer(url, selectors, finalConfig);
                    break;
                case 'cheerio':
                    result = await this.scrapeWithCheerio(url, selectors, finalConfig);
                    break;
                case 'osmosis':
                    result = await this.scrapeWithOsmosis(url, selectors, finalConfig);
                    break;
                case 'ai_enhanced':
                    result = await this.scrapeWithAI(url, selectors, finalConfig);
                    break;
                default:
                    result = await this.scrapeWithPuppeteer(url, selectors, finalConfig);
            }
            
            // Cache result
            await this.cacheResult(url, result);
            
            const duration = Date.now() - startTime;
            
            console.log(chalk.green(`✅ Scraped successfully in ${duration}ms`));
            
            return {
                scrapeId,
                url,
                method,
                data: result,
                timestamp: new Date().toISOString(),
                duration
            };
            
        } catch (error) {
            console.error(chalk.red(`❌ Scraping failed for ${url}:`), error);
            
            return {
                scrapeId,
                url,
                error: error.message,
                timestamp: new Date().toISOString(),
                duration: Date.now() - startTime
            };
        }
    }
    
    determineScrapingMethod(url, selectors) {
        // Simple heuristic to determine best scraping method
        if (selectors.ai_enhanced || selectors.complex_extraction) {
            return 'ai_enhanced';
        }
        
        if (selectors.dynamic_content || selectors.javascript_required) {
            return 'puppeteer';
        }
        
        if (selectors.simple_structure) {
            return 'cheerio';
        }
        
        if (selectors.data_extraction) {
            return 'osmosis';
        }
        
        // Default to puppeteer for unknown cases
        return 'puppeteer';
    }
    
    async scrapeWithPuppeteer(url, selectors, config) {
        const page = await this.browser.newPage();
        this.activePages.add(page);
        
        try {
            // Set user agent
            await page.setUserAgent(config.userAgent);
            
            // Set viewport
            await page.setViewport(config.viewport);
            
            // Navigate to URL
            await page.goto(url, { 
                waitUntil: 'networkidle2', 
                timeout: config.timeout 
            });
            
            // Wait for content to load
            await page.waitForTimeout(config.delay);
            
            // Extract data based on selectors
            const data = await this.extractDataWithPuppeteer(page, selectors);
            
            return data;
            
        } finally {
            await page.close();
            this.activePages.delete(page);
        }
    }
    
    async extractDataWithPuppeteer(page, selectors) {
        const data = {};
        
        // Extract text content
        if (selectors.text) {
            data.text = await page.$eval(selectors.text, el => el.textContent.trim());
        }
        
        // Extract multiple text elements
        if (selectors.texts) {
            data.texts = await page.$$eval(selectors.texts, elements => 
                elements.map(el => el.textContent.trim())
            );
        }
        
        // Extract links
        if (selectors.links) {
            data.links = await page.$$eval(selectors.links, elements =>
                elements.map(el => ({
                    text: el.textContent.trim(),
                    href: el.href
                }))
            );
        }
        
        // Extract images
        if (selectors.images) {
            data.images = await page.$$eval(selectors.images, elements =>
                elements.map(el => ({
                    src: el.src,
                    alt: el.alt,
                    title: el.title
                }))
            );
        }
        
        // Extract tables
        if (selectors.tables) {
            data.tables = await page.$$eval(selectors.tables, tables =>
                tables.map(table => {
                    const rows = Array.from(table.querySelectorAll('tr'));
                    return rows.map(row => {
                        const cells = Array.from(row.querySelectorAll('td, th'));
                        return cells.map(cell => cell.textContent.trim());
                    });
                })
            );
        }
        
        // Extract JSON-LD structured data
        if (selectors.structured_data) {
            data.structuredData = await page.$$eval('script[type="application/ld+json"]', scripts =>
                scripts.map(script => {
                    try {
                        return JSON.parse(script.textContent);
                    } catch (e) {
                        return null;
                    }
                }).filter(Boolean)
            );
        }
        
        // Extract meta tags
        if (selectors.meta) {
            data.meta = await page.$$eval('meta', metas =>
                metas.reduce((acc, meta) => {
                    const name = meta.getAttribute('name') || meta.getAttribute('property');
                    const content = meta.getAttribute('content');
                    if (name && content) {
                        acc[name] = content;
                    }
                    return acc;
                }, {})
            );
        }
        
        // Extract custom selectors
        if (selectors.custom) {
            for (const [key, selector] of Object.entries(selectors.custom)) {
                try {
                    data[key] = await page.$eval(selector, el => el.textContent.trim());
                } catch (e) {
                    data[key] = null;
                }
            }
        }
        
        // Get page metadata
        data.metadata = {
            title: await page.title(),
            url: page.url(),
            timestamp: new Date().toISOString()
        };
        
        return data;
    }
    
    async scrapeWithCheerio(url, selectors, config) {
        try {
            const response = await axios.get(url, {
                headers: {
                    'User-Agent': config.userAgent
                },
                timeout: config.timeout
            });
            
            const $ = cheerio.load(response.data);
            const data = {};
            
            // Extract data using Cheerio
            if (selectors.text) {
                data.text = $(selectors.text).text().trim();
            }
            
            if (selectors.texts) {
                data.texts = $(selectors.texts).map((i, el) => $(el).text().trim()).get();
            }
            
            if (selectors.links) {
                data.links = $(selectors.links).map((i, el) => ({
                    text: $(el).text().trim(),
                    href: $(el).attr('href')
                })).get();
            }
            
            if (selectors.images) {
                data.images = $(selectors.images).map((i, el) => ({
                    src: $(el).attr('src'),
                    alt: $(el).attr('alt'),
                    title: $(el).attr('title')
                })).get();
            }
            
            // Extract meta tags
            data.meta = {};
            $('meta').each((i, el) => {
                const name = $(el).attr('name') || $(el).attr('property');
                const content = $(el).attr('content');
                if (name && content) {
                    data.meta[name] = content;
                }
            });
            
            data.metadata = {
                title: $('title').text().trim(),
                url: url,
                timestamp: new Date().toISOString()
            };
            
            return data;
            
        } catch (error) {
            throw new Error(`Cheerio scraping failed: ${error.message}`);
        }
    }
    
    async scrapeWithOsmosis(url, selectors, config) {
        return new Promise((resolve, reject) => {
            const data = [];
            
            osmosis
                .get(url)
                .set({
                    text: selectors.text || 'body',
                    title: 'title',
                    links: 'a',
                    images: 'img'
                })
                .data(result => {
                    data.push(result);
                })
                .done(() => {
                    resolve({
                        items: data,
                        metadata: {
                            url: url,
                            timestamp: new Date().toISOString(),
                            count: data.length
                        }
                    });
                })
                .error(error => {
                    reject(new Error(`Osmosis scraping failed: ${error.message}`));
                });
        });
    }
    
    async scrapeWithAI(url, selectors, config) {
        // This would integrate with DeepSeek for AI-powered extraction
        // For now, use puppeteer and enhance with basic AI processing
        
        const basicData = await this.scrapeWithPuppeteer(url, selectors, config);
        
        // Enhance with AI processing if available
        if (selectors.ai_enhanced) {
            const enhancedData = await this.enhanceWithAI(basicData, selectors.ai_enhanced);
            return { ...basicData, ai_enhanced: enhancedData };
        }
        
        return basicData;
    }
    
    async enhanceWithAI(data, aiConfig) {
        // Placeholder for AI enhancement
        // This would use DeepSeek to analyze and extract structured information
        
        return {
            summary: "AI-enhanced extraction would be implemented here",
            entities: [],
            sentiment: "neutral",
            topics: [],
            confidence: 0.8
        };
    }
    
    async scrapeMultiple(urls, selectors, config = {}) {
        const results = [];
        const maxConcurrent = config.maxConcurrent || this.config.maxConcurrent;
        
        // Process URLs in batches
        for (let i = 0; i < urls.length; i += maxConcurrent) {
            const batch = urls.slice(i, i + maxConcurrent);
            const batchPromises = batch.map(url => this.scrape(url, selectors, config));
            
            const batchResults = await Promise.allSettled(batchPromises);
            
            batchResults.forEach((result, index) => {
                if (result.status === 'fulfilled') {
                    results.push(result.value);
                } else {
                    results.push({
                        url: batch[index],
                        error: result.reason.message,
                        timestamp: new Date().toISOString()
                    });
                }
            });
            
            // Delay between batches
            if (i + maxConcurrent < urls.length) {
                await new Promise(resolve => setTimeout(resolve, config.delay || this.config.delay));
            }
        }
        
        return {
            total: urls.length,
            successful: results.filter(r => !r.error).length,
            failed: results.filter(r => r.error).length,
            results
        };
    }
    
    async getCachedResult(url) {
        try {
            const cacheKey = this.generateCacheKey(url);
            const cachePath = path.join(this.cacheDir, `${cacheKey}.json`);
            
            if (await fs.pathExists(cachePath)) {
                const cached = await fs.readJson(cachePath);
                
                // Check if cache is still valid (24 hours)
                const cacheAge = Date.now() - new Date(cached.timestamp).getTime();
                if (cacheAge < 24 * 60 * 60 * 1000) {
                    return cached.data;
                }
            }
            
            return null;
            
        } catch (error) {
            console.warn(chalk.yellow('⚠️ Cache read failed:'), error);
            return null;
        }
    }
    
    async cacheResult(url, data) {
        try {
            const cacheKey = this.generateCacheKey(url);
            const cachePath = path.join(this.cacheDir, `${cacheKey}.json`);
            
            const cacheData = {
                url,
                data,
                timestamp: new Date().toISOString()
            };
            
            await fs.writeJson(cachePath, cacheData, { spaces: 2 });
            
        } catch (error) {
            console.warn(chalk.yellow('⚠️ Cache write failed:'), error);
        }
    }
    
    generateCacheKey(url) {
        // Simple hash for cache key
        return Buffer.from(url).toString('base64').replace(/[^a-zA-Z0-9]/g, '');
    }
    
    async clearCache() {
        try {
            await fs.emptyDir(this.cacheDir);
            console.log(chalk.green('✅ Cache cleared'));
        } catch (error) {
            console.error(chalk.red('❌ Failed to clear cache:'), error);
        }
    }
    
    async getCacheStats() {
        try {
            const files = await fs.readdir(this.cacheDir);
            const stats = await Promise.all(
                files.map(async file => {
                    const filePath = path.join(this.cacheDir, file);
                    const stat = await fs.stat(filePath);
                    return {
                        file,
                        size: stat.size,
                        modified: stat.mtime
                    };
                })
            );
            
            return {
                totalFiles: stats.length,
                totalSize: stats.reduce((sum, stat) => sum + stat.size, 0),
                files: stats
            };
            
        } catch (error) {
            console.error(chalk.red('❌ Failed to get cache stats:'), error);
            return null;
        }
    }
    
    async shutdown() {
        try {
            // Close all active pages
            for (const page of this.activePages) {
                await page.close();
            }
            this.activePages.clear();
            
            // Close browser
            if (this.browser) {
                await this.browser.close();
            }
            
            console.log(chalk.green('✅ Web Scraper Tool shutdown complete'));
            
        } catch (error) {
            console.error(chalk.red('❌ Error during shutdown:'), error);
        }
    }
    
    getStatus() {
        return {
            name: this.name,
            version: this.version,
            browserActive: !!this.browser,
            activePages: this.activePages.size,
            cacheSize: this.cache.size
        };
    }
} 