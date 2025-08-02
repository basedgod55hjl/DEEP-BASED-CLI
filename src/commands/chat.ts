import { input } from '@inquirer/prompts';
import chalk from 'chalk';
import ora from 'ora';
import { marked } from 'marked';
import { markedTerminal } from 'marked-terminal';
import { DeepSeekAPI } from '../api/deepseek.js';
import { ConfigManager } from '../utils/config.js';
import { ChatMessage } from '../types/index.js';

// Configure marked to render markdown in terminal
marked.setOptions({
  renderer: new markedTerminal() as any,
});

export async function chatCommand(options: { model?: string; system?: string }) {
  const configManager = new ConfigManager();
  
  if (!configManager.isConfigured()) {
    console.error(chalk.red('Error: DeepSeek API key not configured'));
    console.log(chalk.yellow('Run "deepseek config" to set up your API key'));
    process.exit(1);
  }

  const api = new DeepSeekAPI(configManager.getConfig());
  const messages: ChatMessage[] = [];

  if (options.system) {
    messages.push({
      role: 'system',
      content: options.system,
    });
  }

  console.log(chalk.cyan('DeepSeek Chat'));
  console.log(chalk.gray('Type "exit" or press Ctrl+C to quit\n'));

  while (true) {
    try {
      const userInput = await input({
        message: chalk.green('You:'),
      });

      if (userInput.toLowerCase() === 'exit') {
        break;
      }

      messages.push({
        role: 'user',
        content: userInput,
      });

      const spinner = ora('Thinking...').start();
      let response = '';

      try {
        await api.streamChatCompletion(
          {
            model: options.model || configManager.get('model') || 'deepseek-coder',
            messages,
            stream: true,
          },
          (chunk) => {
            if (!response) {
              spinner.stop();
              console.log(chalk.blue('\nDeepSeek:'));
            }
            response += chunk;
            process.stdout.write(chunk);
          }
        );

        messages.push({
          role: 'assistant',
          content: response,
        });

        console.log('\n');
      } catch (error) {
        spinner.stop();
        console.error(chalk.red('\nError:'), error);
      }
    } catch (error) {
      if (error instanceof Error && error.message.includes('User force closed')) {
        break;
      }
      console.error(chalk.red('Error:'), error);
    }
  }

  console.log(chalk.cyan('\nGoodbye!'));
}