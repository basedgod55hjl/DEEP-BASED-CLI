#!/usr/bin/env node

import { Command } from 'commander';
import chalk from 'chalk';
import { chatCommand } from './commands/chat.js';
import { analyzeCommand } from './commands/analyze.js';
import { configCommand } from './commands/config.js';

const program = new Command();

program
  .name('deepseek')
  .description('DeepSeek CLI - AI-powered command-line tool for code analysis and generation')
  .version('0.1.0');

// Chat command
program
  .command('chat')
  .description('Start an interactive chat session with DeepSeek')
  .option('-m, --model <model>', 'Specify the model to use')
  .option('-s, --system <prompt>', 'Set a system prompt')
  .action(chatCommand);

// Analyze command
program
  .command('analyze <query>')
  .description('Analyze a codebase and answer questions about it')
  .option('-p, --path <path>', 'Path to the codebase to analyze', process.cwd())
  .option('-m, --model <model>', 'Specify the model to use')
  .option('--summary', 'Generate a summary of the codebase instead of answering a query')
  .action(analyzeCommand);

// Config command
program
  .command('config')
  .description('Configure DeepSeek CLI settings')
  .option('-k, --key <key>', 'Configuration key to set')
  .option('-v, --value <value>', 'Configuration value to set')
  .option('-l, --list', 'List current configuration')
  .action(configCommand);

// Quick query (default command)
program
  .argument('[query...]', 'Quick query to DeepSeek')
  .option('-m, --model <model>', 'Specify the model to use')
  .option('-c, --codebase', 'Include codebase context in the query')
  .action(async (queryParts: string[], options) => {
    if (queryParts.length === 0) {
      // No arguments provided, start interactive chat
      await chatCommand(options);
    } else {
      // Quick query mode
      const query = queryParts.join(' ');
      
      if (options.codebase) {
        await analyzeCommand(query, { model: options.model });
      } else {
        // Single query mode
        const { ConfigManager } = await import('./utils/config.js');
        const { DeepSeekAPI } = await import('./api/deepseek.js');
        const ora = (await import('ora')).default;
        const { marked } = await import('marked');
        const { markedTerminal } = await import('./utils/marked-terminal-wrapper.js');
        
        marked.use(markedTerminal() as any);

        const configManager = new ConfigManager();
        
        if (!configManager.isConfigured()) {
          console.error(chalk.red('Error: DeepSeek API key not configured'));
          console.log(chalk.yellow('Run "deepseek config" to set up your API key'));
          process.exit(1);
        }

        const spinner = ora('Thinking...').start();
        
        try {
          const api = new DeepSeekAPI(configManager.getConfig());
          const response = await api.createChatCompletion({
            model: options.model || configManager.get('model') || 'deepseek-coder',
            messages: [
              { role: 'user', content: query },
            ],
          });

          spinner.stop();
          
          const answer = response.choices[0]?.message?.content || 'No response generated';
          console.log(marked(answer));
        } catch (error) {
          spinner.stop();
          console.error(chalk.red('Error:'), error);
          process.exit(1);
        }
      }
    }
  });

// Error handling
program.exitOverride();

try {
  await program.parseAsync(process.argv);
} catch (error: any) {
  if (error.code === 'commander.unknownCommand') {
    console.error(chalk.red('Unknown command'));
    program.outputHelp();
  } else if (error.code === 'commander.help') {
    // Help was explicitly requested
  } else {
    console.error(chalk.red('Error:'), error.message);
  }
  process.exit(1);
} 