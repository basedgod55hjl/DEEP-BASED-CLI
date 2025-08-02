import { globby } from 'globby';
import { readFileSync, statSync } from 'fs';
import { extname } from 'path';
import ignoreLib from 'ignore';
import { CodebaseAnalysisOptions, FileInfo } from '../types/index.js';

const DEFAULT_IGNORE_PATTERNS = [
  'node_modules/**',
  '.git/**',
  'dist/**',
  'build/**',
  'coverage/**',
  '*.log',
  '.DS_Store',
  'package-lock.json',
  'yarn.lock',
  'pnpm-lock.yaml',
];

const DEFAULT_INCLUDE_PATTERNS = [
  '**/*.ts',
  '**/*.tsx',
  '**/*.js',
  '**/*.jsx',
  '**/*.py',
  '**/*.java',
  '**/*.go',
  '**/*.rs',
  '**/*.cpp',
  '**/*.c',
  '**/*.h',
  '**/*.hpp',
  '**/*.cs',
  '**/*.rb',
  '**/*.php',
  '**/*.swift',
  '**/*.kt',
  '**/*.md',
  '**/*.json',
  '**/*.yaml',
  '**/*.yml',
  '**/Dockerfile',
  '**/.env.example',
];

export class CodebaseAnalyzer {
  private options: CodebaseAnalysisOptions;
  private ig: any;

  constructor(options: CodebaseAnalysisOptions) {
    this.options = {
      includePatterns: DEFAULT_INCLUDE_PATTERNS,
      excludePatterns: DEFAULT_IGNORE_PATTERNS,
      maxFileSize: 1024 * 1024, // 1MB
      maxFiles: 500,
      ...options,
    };

    this.ig = ignoreLib.default();
    this.ig.add(this.options.excludePatterns || []);

    // Try to load .gitignore
    try {
      const gitignorePath = `${this.options.path}/.gitignore`;
      const gitignoreContent = readFileSync(gitignorePath, 'utf-8');
      this.ig.add(gitignoreContent);
    } catch {
      // .gitignore not found, continue
    }
  }

  async analyzeCodebase(): Promise<FileInfo[]> {
    const files = await globby(this.options.includePatterns || [], {
      cwd: this.options.path,
      ignore: this.options.excludePatterns,
      absolute: false,
      onlyFiles: true,
    });

    const fileInfos: FileInfo[] = [];
    let processedFiles = 0;

    for (const file of files) {
      if (processedFiles >= (this.options.maxFiles || Infinity)) {
        break;
      }

      if (this.ig.ignores(file)) {
        continue;
      }

      const fullPath = `${this.options.path}/${file}`;
      
      try {
        const stats = statSync(fullPath);
        
        if (stats.size > (this.options.maxFileSize || Infinity)) {
          continue;
        }

        const content = readFileSync(fullPath, 'utf-8');
        
        fileInfos.push({
          path: file,
          content,
          size: stats.size,
          extension: extname(file),
        });

        processedFiles++;
      } catch (error) {
        // Skip files that can't be read
        console.warn(`Skipping file ${file}:`, error);
      }
    }

    return fileInfos;
  }

  async generateSummary(): Promise<string> {
    const files = await this.analyzeCodebase();
    
    const extensions = new Map<string, number>();
    let totalSize = 0;
    let totalLines = 0;

    for (const file of files) {
      const ext = file.extension || 'no-extension';
      extensions.set(ext, (extensions.get(ext) || 0) + 1);
      totalSize += file.size;
      totalLines += file.content.split('\n').length;
    }

    const summary = [
      `## Codebase Analysis Summary`,
      ``,
      `**Total Files:** ${files.length}`,
      `**Total Size:** ${(totalSize / 1024 / 1024).toFixed(2)} MB`,
      `**Total Lines:** ${totalLines.toLocaleString()}`,
      ``,
      `### File Types:`,
    ];

    const sortedExtensions = Array.from(extensions.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10);

    for (const [ext, count] of sortedExtensions) {
      summary.push(`- ${ext}: ${count} files`);
    }

    return summary.join('\n');
  }

  async getContext(query: string, maxFiles: number = 10): Promise<string> {
    const files = await this.analyzeCodebase();
    
    // Simple relevance scoring based on query terms
    const queryTerms = query.toLowerCase().split(/\s+/);
    
    const scoredFiles = files.map(file => {
      let score = 0;
      const lowerPath = file.path.toLowerCase();
      const lowerContent = file.content.toLowerCase();
      
      for (const term of queryTerms) {
        if (lowerPath.includes(term)) score += 10;
        if (lowerContent.includes(term)) {
          score += (lowerContent.split(term).length - 1);
        }
      }
      
      return { file, score };
    });

    const relevantFiles = scoredFiles
      .filter(({ score }) => score > 0)
      .sort((a, b) => b.score - a.score)
      .slice(0, maxFiles)
      .map(({ file }) => file);

    if (relevantFiles.length === 0) {
      return 'No relevant files found for the query.';
    }

    const context = [`Found ${relevantFiles.length} relevant files:\n`];
    
    for (const file of relevantFiles) {
      context.push(`### ${file.path}`);
      context.push('```' + (file.extension.slice(1) || 'text'));
      context.push(file.content.slice(0, 1000));
      if (file.content.length > 1000) {
        context.push('... (truncated)');
      }
      context.push('```\n');
    }

    return context.join('\n');
  }
} 