#!/usr/bin/env node

import { execSync } from 'child_process';
import { readFileSync, writeFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const projectRoot = join(__dirname, '..');

function analyzeDependencies() {
  console.log('🔍 Analyzing dependencies...');
  
  try {
    const packageJson = JSON.parse(readFileSync(join(projectRoot, 'package.json'), 'utf8'));
    const dependencies = { ...packageJson.dependencies, ...packageJson.devDependencies };
    
    console.log('\n📦 Dependency Analysis:');
    console.log('=======================');
    
    const largeDeps = [];
    const mediumDeps = [];
    const smallDeps = [];
    
    for (const [name, version] of Object.entries(dependencies)) {
      // Categorize by likely size (this is a rough estimate)
      if (['@xenova/transformers', 'onnxruntime-node', 'better-sqlite3'].includes(name)) {
        largeDeps.push({ name, version, category: 'Large (>10MB)' });
      } else if (['openai', 'axios', 'chalk', 'commander'].includes(name)) {
        mediumDeps.push({ name, version, category: 'Medium (1-10MB)' });
      } else {
        smallDeps.push({ name, version, category: 'Small (<1MB)' });
      }
    }
    
    console.log('\n🚨 Large Dependencies (Consider alternatives):');
    largeDeps.forEach(dep => {
      console.log(`  ${dep.name}@${dep.version} - ${dep.category}`);
    });
    
    console.log('\n⚠️  Medium Dependencies:');
    mediumDeps.forEach(dep => {
      console.log(`  ${dep.name}@${dep.version} - ${dep.category}`);
    });
    
    console.log('\n✅ Small Dependencies:');
    smallDeps.forEach(dep => {
      console.log(`  ${dep.name}@${dep.version} - ${dep.category}`);
    });
    
    return { largeDeps, mediumDeps, smallDeps };
  } catch (error) {
    console.error('Error analyzing dependencies:', error);
    return null;
  }
}

function generateOptimizationReport(deps) {
  console.log('\n💡 Optimization Recommendations:');
  console.log('================================');
  
  if (deps.largeDeps.length > 0) {
    console.log('\n1. Replace Heavy Dependencies:');
    deps.largeDeps.forEach(dep => {
      switch (dep.name) {
        case '@xenova/transformers':
          console.log(`   - Replace ${dep.name} with lighter alternatives or lazy load`);
          break;
        case 'onnxruntime-node':
          console.log(`   - Consider using ${dep.name} only when needed`);
          break;
        case 'better-sqlite3':
          console.log(`   - Consider using sqlite3 or sql.js for lighter SQLite support`);
          break;
      }
    });
  }
  
  console.log('\n2. Implement Code Splitting:');
  console.log('   - Use dynamic imports for heavy tools');
  console.log('   - Lazy load transformers and ML models');
  console.log('   - Split CLI and library code');
  
  console.log('\n3. Bundle Optimization:');
  console.log('   - Enable tree shaking in TypeScript config');
  console.log('   - Use ES modules for better tree shaking');
  console.log('   - Implement dead code elimination');
  
  console.log('\n4. Runtime Optimizations:');
  console.log('   - Implement connection pooling for APIs');
  console.log('   - Add request batching and caching');
  console.log('   - Use worker threads for CPU-intensive tasks');
}

async function checkBundleSize() {
  console.log('\n📊 Bundle Size Analysis:');
  console.log('========================');
  
  try {
    // Check if dist directory exists
    const distPath = join(projectRoot, 'dist');
    const fs = await import('fs');
    
    if (fs.existsSync(distPath)) {
      const { execSync } = await import('child_process');
      const size = execSync(`du -sh ${distPath}`, { encoding: 'utf8' }).trim();
      console.log(`Bundle size: ${size}`);
    } else {
      console.log('No dist directory found. Run "npm run build" first.');
    }
  } catch (error) {
    console.log('Could not analyze bundle size:', error.message);
  }
}

async function main() {
  console.log('🚀 Bundle Analysis Tool');
  console.log('=======================\n');
  
  const deps = analyzeDependencies();
  if (deps) {
    generateOptimizationReport(deps);
  }
  
  await checkBundleSize();
  
  console.log('\n✅ Analysis complete!');
}

main().catch(console.error);