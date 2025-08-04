/**
 * Memory Store System
 * Persistent memory storage with JSON format and advanced querying
 * Made by @Lucariolucario55 on Telegram
 */

import fs from 'fs-extra';
import path from 'path';
import { v4 as uuidv4 } from 'uuid';
import chalk from 'chalk';

export class MemoryStore {
    constructor() {
        this.memoryFile = 'data/json_memory.json';
        this.memoryData = null;
        this.maxEntries = 10000;
        this.autoBackup = true;
        this.backupInterval = 100;
        this.entryCount = 0;
        
        this.initialize();
    }
    
    async initialize() {
        try {
            // Ensure directory exists
            await fs.ensureDir(path.dirname(this.memoryFile));
            
            // Load or create memory
            this.memoryData = await this.loadMemory();
            
            console.log(chalk.green('✅ Memory Store initialized'));
            
        } catch (error) {
            console.error(chalk.red('❌ Failed to initialize Memory Store:'), error);
            throw error;
        }
    }
    
    async loadMemory() {
        try {
            if (await fs.pathExists(this.memoryFile)) {
                const data = await fs.readJson(this.memoryFile);
                console.log(chalk.cyan(`📖 Loaded ${Object.keys(data.entries || {}).length} memory entries`));
                return data;
            } else {
                // Initialize new memory structure
                const initialData = {
                    metadata: {
                        created: new Date().toISOString(),
                        version: '1.0',
                        total_entries: 0,
                        categories: [],
                        tags: []
                    },
                    entries: {},
                    indexes: {
                        by_category: {},
                        by_tag: {},
                        by_timestamp: {},
                        by_importance: {}
                    }
                };
                
                await this.saveMemory(initialData);
                return initialData;
            }
        } catch (error) {
            console.error(chalk.red('❌ Failed to load memory:'), error);
            return {
                metadata: { created: new Date().toISOString(), version: '1.0', total_entries: 0 },
                entries: {},
                indexes: { by_category: {}, by_tag: {}, by_timestamp: {}, by_importance: {} }
            };
        }
    }
    
    async saveMemory(data = null) {
        try {
            const dataToSave = data || this.memoryData;
            
            // Create backup if needed
            if (this.autoBackup && this.entryCount % this.backupInterval === 0) {
                await this.createBackup();
            }
            
            await fs.writeJson(this.memoryFile, dataToSave, { spaces: 2 });
            return true;
        } catch (error) {
            console.error(chalk.red('❌ Failed to save memory:'), error);
            return false;
        }
    }
    
    async createBackup() {
        try {
            const backupFile = this.memoryFile.replace('.json', `.backup_${new Date().toISOString().replace(/[:.]/g, '-')}.json`);
            await fs.copy(this.memoryFile, backupFile);
            console.log(chalk.yellow(`📋 Memory backup created: ${backupFile}`));
        } catch (error) {
            console.error(chalk.red('❌ Failed to create backup:'), error);
        }
    }
    
    async store(content, category = 'general', tags = [], importance = 1.0, embedding = null) {
        try {
            // Check if we're at capacity
            if (Object.keys(this.memoryData.entries).length >= this.maxEntries) {
                await this.removeLeastImportantEntry();
            }
            
            // Create memory entry
            const entry = {
                id: uuidv4(),
                content,
                category,
                tags,
                metadata: {},
                timestamp: new Date().toISOString(),
                embedding,
                importance,
                access_count: 0,
                last_accessed: null
            };
            
            // Store entry
            this.memoryData.entries[entry.id] = entry;
            
            // Update indexes
            this.updateIndexes(entry, 'add');
            
            // Update metadata
            this.memoryData.metadata.total_entries = Object.keys(this.memoryData.entries).length;
            if (!this.memoryData.metadata.categories.includes(category)) {
                this.memoryData.metadata.categories.push(category);
            }
            
            for (const tag of tags) {
                if (!this.memoryData.metadata.tags.includes(tag)) {
                    this.memoryData.metadata.tags.push(tag);
                }
            }
            
            // Save to file
            if (await this.saveMemory()) {
                this.entryCount++;
                return {
                    success: true,
                    entry_id: entry.id,
                    content,
                    category,
                    tags,
                    timestamp: entry.timestamp,
                    importance
                };
            } else {
                return {
                    success: false,
                    message: 'Failed to save memory to file'
                };
            }
        } catch (error) {
            console.error(chalk.red('❌ Memory storage error:'), error);
            return {
                success: false,
                message: error.message
            };
        }
    }
    
    async retrieve(entryId) {
        try {
            const entry = this.memoryData.entries[entryId];
            
            if (!entry) {
                return {
                    success: false,
                    message: `Memory entry not found: ${entryId}`
                };
            }
            
            // Update access count
            entry.access_count += 1;
            entry.last_accessed = new Date().toISOString();
            
            // Save changes
            await this.saveMemory();
            
            return {
                success: true,
                data: entry
            };
        } catch (error) {
            console.error(chalk.red('❌ Memory retrieval error:'), error);
            return {
                success: false,
                message: error.message
            };
        }
    }
    
    async search(query = '', category = null, tags = [], limit = 10, minImportance = 0.0) {
        try {
            const results = [];
            
            for (const [entryId, entry] of Object.entries(this.memoryData.entries)) {
                // Apply filters
                if (category && entry.category !== category) continue;
                if (tags.length > 0 && !tags.some(tag => entry.tags.includes(tag))) continue;
                if (entry.importance < minImportance) continue;
                
                // Text search
                if (query && !entry.content.toLowerCase().includes(query.toLowerCase())) continue;
                
                results.push({
                    id: entryId,
                    ...entry
                });
            }
            
            // Sort by importance and access count
            results.sort((a, b) => (b.importance - a.importance) || (b.access_count - a.access_count));
            
            // Apply limit
            const limitedResults = results.slice(0, limit);
            
            return {
                success: true,
                results: limitedResults,
                total_found: results.length,
                query,
                filters: { category, tags, minImportance }
            };
        } catch (error) {
            console.error(chalk.red('❌ Memory search error:'), error);
            return {
                success: false,
                message: error.message
            };
        }
    }
    
    async query(queryType, params) {
        try {
            let results = [];
            
            switch (queryType) {
                case 'by_category':
                    const category = params.category;
                    if (!category) {
                        return { success: false, message: 'Category is required' };
                    }
                    
                    const categoryEntryIds = this.memoryData.indexes.by_category[category] || [];
                    results = categoryEntryIds
                        .map(id => this.memoryData.entries[id])
                        .filter(Boolean);
                    break;
                    
                case 'by_tag':
                    const tag = params.tag;
                    if (!tag) {
                        return { success: false, message: 'Tag is required' };
                    }
                    
                    const tagEntryIds = this.memoryData.indexes.by_tag[tag] || [];
                    results = tagEntryIds
                        .map(id => this.memoryData.entries[id])
                        .filter(Boolean);
                    break;
                    
                case 'by_date_range':
                    const { startDate, endDate } = params;
                    if (!startDate || !endDate) {
                        return { success: false, message: 'Start date and end date are required' };
                    }
                    
                    results = Object.values(this.memoryData.entries).filter(entry => {
                        const entryDate = new Date(entry.timestamp);
                        return entryDate >= new Date(startDate) && entryDate <= new Date(endDate);
                    });
                    break;
                    
                case 'by_importance':
                    const { minImportance = 0.0, maxImportance = 10.0 } = params;
                    
                    results = Object.values(this.memoryData.entries).filter(entry => {
                        return entry.importance >= minImportance && entry.importance <= maxImportance;
                    });
                    break;
                    
                default:
                    return { success: false, message: `Unsupported query type: ${queryType}` };
            }
            
            return {
                success: true,
                results,
                query_type: queryType,
                total_found: results.length
            };
        } catch (error) {
            console.error(chalk.red('❌ Memory query error:'), error);
            return {
                success: false,
                message: error.message
            };
        }
    }
    
    async delete(entryId) {
        try {
            const entry = this.memoryData.entries[entryId];
            
            if (!entry) {
                return {
                    success: false,
                    message: `Memory entry not found: ${entryId}`
                };
            }
            
            // Remove from indexes
            this.updateIndexes(entry, 'remove');
            
            // Remove entry
            delete this.memoryData.entries[entryId];
            
            // Update metadata
            this.memoryData.metadata.total_entries = Object.keys(this.memoryData.entries).length;
            
            // Save changes
            if (await this.saveMemory()) {
                return {
                    success: true,
                    deleted_entry_id: entryId
                };
            } else {
                return {
                    success: false,
                    message: 'Failed to save changes after deletion'
                };
            }
        } catch (error) {
            console.error(chalk.red('❌ Memory deletion error:'), error);
            return {
                success: false,
                message: error.message
            };
        }
    }
    
    async update(entryId, updates) {
        try {
            const entry = this.memoryData.entries[entryId];
            
            if (!entry) {
                return {
                    success: false,
                    message: `Memory entry not found: ${entryId}`
                };
            }
            
            // Remove from indexes
            this.updateIndexes(entry, 'remove');
            
            // Update fields
            const updateableFields = ['content', 'category', 'tags', 'metadata', 'importance', 'embedding'];
            for (const field of updateableFields) {
                if (updates[field] !== undefined) {
                    entry[field] = updates[field];
                }
            }
            
            // Update timestamp
            entry.timestamp = new Date().toISOString();
            
            // Update indexes
            this.updateIndexes(entry, 'add');
            
            // Save changes
            if (await this.saveMemory()) {
                return {
                    success: true,
                    data: entry
                };
            } else {
                return {
                    success: false,
                    message: 'Failed to save changes after update'
                };
            }
        } catch (error) {
            console.error(chalk.red('❌ Memory update error:'), error);
            return {
                success: false,
                message: error.message
            };
        }
    }
    
    async getAnalytics() {
        try {
            const analytics = {
                total_entries: Object.keys(this.memoryData.entries).length,
                categories: {},
                tags: {},
                importance_distribution: {},
                access_patterns: {},
                recent_activity: {}
            };
            
            // Category distribution
            for (const entry of Object.values(this.memoryData.entries)) {
                analytics.categories[entry.category] = (analytics.categories[entry.category] || 0) + 1;
            }
            
            // Tag distribution
            for (const entry of Object.values(this.memoryData.entries)) {
                for (const tag of entry.tags) {
                    analytics.tags[tag] = (analytics.tags[tag] || 0) + 1;
                }
            }
            
            // Importance distribution
            for (const entry of Object.values(this.memoryData.entries)) {
                const importanceKey = entry.importance.toFixed(1);
                analytics.importance_distribution[importanceKey] = (analytics.importance_distribution[importanceKey] || 0) + 1;
            }
            
            // Access patterns
            const totalAccess = Object.values(this.memoryData.entries).reduce((sum, entry) => sum + entry.access_count, 0);
            analytics.access_patterns.total_accesses = totalAccess;
            analytics.access_patterns.average_access_per_entry = totalAccess / Object.keys(this.memoryData.entries).length || 0;
            
            // Recent activity (last 7 days)
            const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
            const recentEntries = Object.values(this.memoryData.entries).filter(entry => 
                new Date(entry.timestamp) >= weekAgo
            );
            analytics.recent_activity.entries_last_7_days = recentEntries.length;
            
            return {
                success: true,
                data: analytics
            };
        } catch (error) {
            console.error(chalk.red('❌ Memory analytics error:'), error);
            return {
                success: false,
                message: error.message
            };
        }
    }
    
    async export(format = 'json', filters = {}) {
        try {
            // Apply filters
            let entriesToExport = Object.values(this.memoryData.entries);
            
            if (filters.category) {
                entriesToExport = entriesToExport.filter(entry => entry.category === filters.category);
            }
            
            if (filters.tags && filters.tags.length > 0) {
                entriesToExport = entriesToExport.filter(entry => 
                    filters.tags.some(tag => entry.tags.includes(tag))
                );
            }
            
            if (filters.minImportance !== undefined) {
                entriesToExport = entriesToExport.filter(entry => entry.importance >= filters.minImportance);
            }
            
            let exportData;
            
            if (format === 'json') {
                exportData = {
                    metadata: this.memoryData.metadata,
                    entries: entriesToExport,
                    export_timestamp: new Date().toISOString(),
                    total_exported: entriesToExport.length
                };
            } else if (format === 'csv') {
                exportData = entriesToExport.map(entry => ({
                    id: entry.id,
                    content: entry.content,
                    category: entry.category,
                    tags: entry.tags.join(','),
                    importance: entry.importance,
                    access_count: entry.access_count,
                    timestamp: entry.timestamp
                }));
            } else {
                return {
                    success: false,
                    message: `Unsupported export format: ${format}`
                };
            }
            
            return {
                success: true,
                data: {
                    export_data: exportData,
                    format,
                    total_exported: entriesToExport.length
                }
            };
        } catch (error) {
            console.error(chalk.red('❌ Memory export error:'), error);
            return {
                success: false,
                message: error.message
            };
        }
    }
    
    updateIndexes(entry, operation) {
        const indexes = this.memoryData.indexes;
        
        if (operation === 'add') {
            // Update category index
            if (!indexes.by_category[entry.category]) {
                indexes.by_category[entry.category] = [];
            }
            indexes.by_category[entry.category].push(entry.id);
            
            // Update tag index
            for (const tag of entry.tags) {
                if (!indexes.by_tag[tag]) {
                    indexes.by_tag[tag] = [];
                }
                indexes.by_tag[tag].push(entry.id);
            }
            
            // Update timestamp index (by day)
            const dayKey = new Date(entry.timestamp).toISOString().split('T')[0];
            if (!indexes.by_timestamp[dayKey]) {
                indexes.by_timestamp[dayKey] = [];
            }
            indexes.by_timestamp[dayKey].push(entry.id);
            
            // Update importance index
            const importanceKey = entry.importance.toFixed(1);
            if (!indexes.by_importance[importanceKey]) {
                indexes.by_importance[importanceKey] = [];
            }
            indexes.by_importance[importanceKey].push(entry.id);
            
        } else if (operation === 'remove') {
            // Remove from all indexes
            for (const [indexName, indexData] of Object.entries(indexes)) {
                for (const [key, entryIds] of Object.entries(indexData)) {
                    const index = entryIds.indexOf(entry.id);
                    if (index > -1) {
                        entryIds.splice(index, 1);
                        if (entryIds.length === 0) {
                            delete indexData[key];
                        }
                    }
                }
            }
        }
    }
    
    async removeLeastImportantEntry() {
        const entries = Object.entries(this.memoryData.entries);
        
        if (entries.length === 0) return;
        
        // Find least important entry
        const [leastImportantId] = entries.reduce((min, [id, entry]) => 
            entry.importance < min[1].importance ? [id, entry] : min
        );
        
        // Remove it
        await this.delete(leastImportantId);
        console.log(chalk.yellow(`🗑️ Removed least important entry: ${leastImportantId}`));
    }
    
    getStatus() {
        return {
            total_entries: Object.keys(this.memoryData.entries).length,
            categories: this.memoryData.metadata.categories.length,
            tags: this.memoryData.metadata.tags.length,
            max_entries: this.maxEntries,
            auto_backup: this.auto_backup
        };
    }
} 