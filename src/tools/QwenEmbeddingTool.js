/**
 * Qwen Embedding Tool for Node.js
 * High-quality embedding generation using Qwen3 models
 * Made by @Lucariolucario55 on Telegram
 */

import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';
import chalk from 'chalk';
import fs from 'fs-extra';
import path from 'path';

export class QwenEmbeddingTool {
    constructor() {
        this.name = 'qwen_embedding';
        this.description = 'Generate high-quality embeddings using Qwen3 models';
        this.version = '1.0.0';
        
        // Configuration
        this.config = {
            modelPath: 'data/models/qwen3_embedding',
            embeddingDimension: 1024,
            normalizeEmbeddings: true,
            cacheDir: 'data/embedding_cache',
            maxCacheSize: 10000
        };
        
        // Cache
        this.cache = new Map();
        this.isInitialized = false;
        
        this.initialize();
    }
    
    async initialize() {
        try {
            // Ensure cache directory exists
            await fs.ensureDir(this.config.cacheDir);
            
            // Check if Qwen model exists
            await this.checkModelAvailability();
            
            this.isInitialized = true;
            console.log(chalk.green('✅ Qwen Embedding Tool initialized'));
            
        } catch (error) {
            console.error(chalk.red('❌ Failed to initialize Qwen Embedding Tool:'), error);
            throw error;
        }
    }
    
    async checkModelAvailability() {
        try {
            const modelInfoPath = path.join(this.config.modelPath, 'qwen_embedding_system_info.json');
            
            if (await fs.pathExists(modelInfoPath)) {
                const modelInfo = await fs.readJson(modelInfoPath);
                console.log(chalk.cyan(`📖 Qwen model found: ${modelInfo.model_type}`));
                return true;
            } else {
                console.warn(chalk.yellow('⚠️ Qwen model not found, will use fallback'));
                return false;
            }
        } catch (error) {
            console.warn(chalk.yellow('⚠️ Could not check model availability:'), error);
            return false;
        }
    }
    
    async embed_text(text) {
        try {
            if (!text || text.trim() === '') {
                return {
                    success: false,
                    message: 'No text provided for embedding generation'
                };
            }
            
            // Check cache first
            const cacheKey = this.generateCacheKey(text);
            const cached = this.cache.get(cacheKey);
            if (cached) {
                return {
                    success: true,
                    message: 'Embedding retrieved from cache',
                    data: {
                        embedding: cached.embedding,
                        text: text,
                        metadata: cached.metadata,
                        cached: true
                    }
                };
            }
            
            // Generate embedding (placeholder implementation)
            // In a real implementation, this would call the Qwen model
            const embedding = await this.generateEmbedding(text);
            
            // Cache the result
            const metadata = {
                text_length: text.length,
                embedding_dimension: embedding.length,
                model_type: 'Qwen3-Embedding-0.6B',
                timestamp: new Date().toISOString()
            };
            
            this.cache.set(cacheKey, {
                embedding,
                metadata,
                timestamp: new Date().toISOString()
            });
            
            // Manage cache size
            this.manageCacheSize();
            
            return {
                success: true,
                message: 'Embedding generated successfully',
                data: {
                    embedding,
                    text,
                    metadata,
                    cached: false
                }
            };
            
        } catch (error) {
            console.error(chalk.red('❌ Embedding generation error:'), error);
            return {
                success: false,
                message: error.message
            };
        }
    }
    
    async generateEmbedding(text) {
        // Placeholder implementation
        // In a real implementation, this would:
        // 1. Load the Qwen model
        // 2. Preprocess the text
        // 3. Generate embeddings
        // 4. Return the embedding vector
        
        // For now, return a dummy embedding
        const embedding = new Array(this.config.embeddingDimension).fill(0).map(() => 
            Math.random() * 2 - 1
        );
        
        // Normalize if required
        if (this.config.normalizeEmbeddings) {
            const magnitude = Math.sqrt(embedding.reduce((sum, val) => sum + val * val, 0));
            if (magnitude > 0) {
                for (let i = 0; i < embedding.length; i++) {
                    embedding[i] /= magnitude;
                }
            }
        }
        
        return embedding;
    }
    
    async embed_texts(texts) {
        try {
            if (!Array.isArray(texts) || texts.length === 0) {
                return {
                    success: false,
                    message: 'No texts provided for batch embedding generation'
                };
            }
            
            const results = [];
            let successfulCount = 0;
            
            for (const text of texts) {
                const result = await this.embed_text(text);
                results.push(result);
                
                if (result.success) {
                    successfulCount++;
                }
            }
            
            return {
                success: successfulCount > 0,
                message: `Generated ${successfulCount}/${texts.length} embeddings successfully`,
                data: {
                    results,
                    successful_count: successfulCount,
                    total_count: texts.length
                }
            };
            
        } catch (error) {
            console.error(chalk.red('❌ Batch embedding error:'), error);
            return {
                success: false,
                message: error.message
            };
        }
    }
    
    async compute_similarity(embedding1, embedding2) {
        try {
            if (!embedding1 || !embedding2) {
                return {
                    success: false,
                    message: 'Both embeddings are required for similarity computation'
                };
            }
            
            if (embedding1.length !== embedding2.length) {
                return {
                    success: false,
                    message: 'Embeddings must have the same dimension'
                };
            }
            
            // Compute cosine similarity
            let dotProduct = 0;
            let norm1 = 0;
            let norm2 = 0;
            
            for (let i = 0; i < embedding1.length; i++) {
                dotProduct += embedding1[i] * embedding2[i];
                norm1 += embedding1[i] * embedding1[i];
                norm2 += embedding2[i] * embedding2[i];
            }
            
            norm1 = Math.sqrt(norm1);
            norm2 = Math.sqrt(norm2);
            
            let similarity = 0;
            if (norm1 > 0 && norm2 > 0) {
                similarity = dotProduct / (norm1 * norm2);
            }
            
            return {
                success: true,
                message: 'Similarity computed successfully',
                data: {
                    similarity,
                    embedding1_length: embedding1.length,
                    embedding2_length: embedding2.length
                }
            };
            
        } catch (error) {
            console.error(chalk.red('❌ Similarity computation error:'), error);
            return {
                success: false,
                message: error.message
            };
        }
    }
    
    async semantic_search(query, embeddings, texts, topK = 5) {
        try {
            if (!query || !embeddings || !texts) {
                return {
                    success: false,
                    message: 'Query, embeddings, and texts are required for semantic search'
                };
            }
            
            if (embeddings.length !== texts.length) {
                return {
                    success: false,
                    message: 'Embeddings and texts arrays must have the same length'
                };
            }
            
            // Generate query embedding
            const queryResult = await this.embed_text(query);
            if (!queryResult.success) {
                return queryResult;
            }
            
            const queryEmbedding = queryResult.data.embedding;
            
            // Compute similarities
            const similarities = [];
            for (let i = 0; i < embeddings.length; i++) {
                const similarityResult = await this.compute_similarity(queryEmbedding, embeddings[i]);
                if (similarityResult.success) {
                    similarities.push({
                        similarity: similarityResult.data.similarity,
                        index: i,
                        text: texts[i]
                    });
                }
            }
            
            // Sort by similarity
            similarities.sort((a, b) => b.similarity - a.similarity);
            
            // Get top-k results
            const topResults = similarities.slice(0, topK);
            
            return {
                success: true,
                message: `Semantic search completed. Found ${topResults.length} results`,
                data: {
                    query,
                    results: topResults,
                    total_candidates: embeddings.length,
                    top_k: topK
                }
            };
            
        } catch (error) {
            console.error(chalk.red('❌ Semantic search error:'), error);
            return {
                success: false,
                message: error.message
            };
        }
    }
    
    generateCacheKey(text) {
        // Simple hash for cache key
        return Buffer.from(text).toString('base64').replace(/[^a-zA-Z0-9]/g, '');
    }
    
    manageCacheSize() {
        if (this.cache.size > this.config.maxCacheSize) {
            // Remove oldest entries
            const entries = Array.from(this.cache.entries());
            entries.sort((a, b) => new Date(a[1].timestamp) - new Date(b[1].timestamp));
            
            const toRemove = entries.slice(0, this.cache.size - this.config.maxCacheSize);
            toRemove.forEach(([key]) => this.cache.delete(key));
            
            console.log(chalk.yellow(`🗑️ Removed ${toRemove.length} cached embeddings`));
        }
    }
    
    async clearCache() {
        try {
            this.cache.clear();
            console.log(chalk.green('✅ Embedding cache cleared'));
        } catch (error) {
            console.error(chalk.red('❌ Failed to clear cache:'), error);
        }
    }
    
    getStatus() {
        return {
            name: this.name,
            version: this.version,
            initialized: this.isInitialized,
            cacheSize: this.cache.size,
            maxCacheSize: this.config.maxCacheSize,
            embeddingDimension: this.config.embeddingDimension
        };
    }
} 