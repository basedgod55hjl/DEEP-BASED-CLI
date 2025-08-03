#!/usr/bin/env node
import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import { ToolManager } from '../ToolManager.js';

const program = new Command();
const tm = new ToolManager();

// Performance monitoring
const performanceMetrics = {
  toolLoadTimes: new Map<string, number>(),
  totalRequests: 0,
  cacheHits: 0
};

program
  .name('deep-cli')
  .description('Enhanced BASED GOD CLI (TypeScript)')
  .version('0.1.0');

program
  .command('chat')
  .description('Chat with the Unified Agent')
  .argument('<message...>', 'message')
  .option('-p, --persona <name>', 'persona name', 'deanna')
  .action(async (msg, opts) => {
    const spinner = ora('Thinking...').start();
    const startTime = Date.now();
    
    try {
      const res = await tm.executeTool('unifiedagentsystem', {
        operation: 'conversation',
        message: msg.join(' '),
        persona: opts.persona
      });
      
      const executionTime = Date.now() - startTime;
      performanceMetrics.totalRequests++;
      
      spinner.stop();
      console.log(chalk.green(res.data?.response));
      console.log(chalk.gray(`⏱️  Execution time: ${executionTime}ms`));
    } catch (error) {
      spinner.stop();
      console.error(chalk.red('Error:', error));
    }
  });

program
  .command('scrape')
  .description('Scrape a webpage and store context')
  .argument('<url>', 'URL to scrape')
  .action(async (url) => {
    const spinner = ora('Scraping...').start();
    const startTime = Date.now();
    
    try {
      const res = await tm.executeTool('webscrapertool', { url });
      const executionTime = Date.now() - startTime;
      performanceMetrics.totalRequests++;
      
      spinner.stop();
      console.log(res.message, res.data);
      console.log(chalk.gray(`⏱️  Execution time: ${executionTime}ms`));
    } catch (error) {
      spinner.stop();
      console.error(chalk.red('Error:', error));
    }
  });

program
  .command('reason')
  .description('Chain-of-thought reasoning')
  .argument('<question...>', 'question')
  .action(async (q) => {
    const spinner = ora('Reasoning...').start();
    const startTime = Date.now();
    
    try {
      const res = await tm.executeTool('fastreasoningengine', { problem: q.join(' ') });
      const executionTime = Date.now() - startTime;
      performanceMetrics.totalRequests++;
      
      spinner.stop();
      console.log(res.data?.reasoning);
      console.log(chalk.gray(`⏱️  Execution time: ${executionTime}ms`));
    } catch (error) {
      spinner.stop();
      console.error(chalk.red('Error:', error));
    }
  });

program
  .command('code')
  .description('Generate code via swarm pipeline')
  .argument('<spec...>', 'code spec')
  .action(async (spec) => {
    const spinner = ora('Generating code...').start();
    const startTime = Date.now();
    
    try {
      const res = await tm.executeTool('swarmtool', { task: spec.join(' ') });
      const executionTime = Date.now() - startTime;
      performanceMetrics.totalRequests++;
      
      spinner.stop();
      console.log(res.data?.code);
      console.log(chalk.gray(`⏱️  Execution time: ${executionTime}ms`));
    } catch (error) {
      spinner.stop();
      console.error(chalk.red('Error:', error));
    }
  });

program
  .command('exec')
  .description('Execute safe shell command (echo, ls)')
  .argument('<command...>', 'cmd')
  .action(async (cmdParts) => {
    const spinner = ora('Executing...').start();
    const startTime = Date.now();
    
    try {
      const res = await tm.executeTool('commandexecutortool', { command: cmdParts.join(' ') });
      const executionTime = Date.now() - startTime;
      performanceMetrics.totalRequests++;
      
      spinner.stop();
      console.log(res.data?.stdout);
      console.log(chalk.gray(`⏱️  Execution time: ${executionTime}ms`));
    } catch (error) {
      spinner.stop();
      console.error(chalk.red('Error:', error));
    }
  });

program
  .command('heal')
  .description('Run test suite and report status')
  .action(async () => {
    const spinner = ora('Running tests...').start();
    const startTime = Date.now();
    
    try {
      const res = await tm.executeTool('selfhealertool', {});
      const executionTime = Date.now() - startTime;
      performanceMetrics.totalRequests++;
      
      spinner.stop();
      console.log(res.message);
      console.log(chalk.gray(`⏱️  Execution time: ${executionTime}ms`));
    } catch (error) {
      spinner.stop();
      console.error(chalk.red('Error:', error));
    }
  });

program
  .command('metric')
  .description('Send metric to Datadog')
  .argument('<name>', 'metric name')
  .argument('[value]', 'value', '1')
  .action(async (name, value) => {
    const spinner = ora('Sending metric...').start();
    const startTime = Date.now();
    
    try {
      const res = await tm.executeTool('datadogintegrationtool', { metric: name, value: Number(value) });
      const executionTime = Date.now() - startTime;
      performanceMetrics.totalRequests++;
      
      spinner.stop();
      console.log(res.message);
      console.log(chalk.gray(`⏱️  Execution time: ${executionTime}ms`));
    } catch (error) {
      spinner.stop();
      console.error(chalk.red('Error:', error));
    }
  });

program
  .command('tools')
  .description('List available tools')
  .action(async () => {
    const spinner = ora('Loading tools...').start();
    try {
      const tools = await tm.listTools();
      spinner.stop();
      console.log(chalk.blue('Available tools:'));
      tools.forEach(tool => console.log(chalk.green(`  - ${tool}`)));
    } catch (error) {
      spinner.stop();
      console.error(chalk.red('Error:', error));
    }
  });

program
  .command('stats')
  .description('Show performance statistics')
  .action(() => {
    console.log(chalk.blue(tm.getPerformanceMetrics()));
  });

program.parseAsync();