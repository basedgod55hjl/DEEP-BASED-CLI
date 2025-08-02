import { input, select } from '@inquirer/prompts';
import chalk from 'chalk';
import { ConfigManager } from '../utils/config.js';

export async function configCommand(options: { 
  key?: string; 
  value?: string;
  list?: boolean;
}) {
  const configManager = new ConfigManager();

  if (options.list) {
    const config = configManager.getConfig();
    console.log(chalk.cyan('Current Configuration:'));
    console.log(JSON.stringify(config, null, 2));
    return;
  }

  if (options.key && options.value !== undefined) {
    // Set a specific config value
    configManager.set(options.key as any, options.value);
    console.log(chalk.green(`✓ Set ${options.key} = ${options.value}`));
    return;
  }

  // Interactive configuration
  console.log(chalk.cyan('DeepSeek CLI Configuration'));
  console.log(chalk.gray('Press Ctrl+C to cancel\n'));

  const action = await select({
    message: 'What would you like to configure?',
    choices: [
      { name: 'API Key', value: 'apiKey' },
      { name: 'Model', value: 'model' },
      { name: 'API Endpoint', value: 'apiEndpoint' },
      { name: 'Max Tokens', value: 'maxTokens' },
      { name: 'Temperature', value: 'temperature' },
      { name: 'View Current Config', value: 'view' },
    ],
  });

  if (action === 'view') {
    const config = configManager.getConfig();
    console.log(chalk.cyan('\nCurrent Configuration:'));
    console.log(JSON.stringify(config, null, 2));
    return;
  }

  const currentValue = configManager.get(action as any);
  let newValue: string | number;

  switch (action) {
    case 'apiKey':
      newValue = await input({
        message: 'Enter your DeepSeek API key:',
        default: currentValue || '',
      });
      break;

    case 'model':
      newValue = await select({
        message: 'Select a model:',
        choices: [
          { name: 'DeepSeek Coder', value: 'deepseek-coder' },
          { name: 'DeepSeek Chat', value: 'deepseek-chat' },
          { name: 'Custom', value: 'custom' },
        ],
        default: currentValue || 'deepseek-coder',
      });
      
      if (newValue === 'custom') {
        newValue = await input({
          message: 'Enter custom model name:',
          default: currentValue || '',
        });
      }
      break;

    case 'apiEndpoint':
      newValue = await input({
        message: 'Enter API endpoint:',
        default: currentValue || 'https://api.deepseek.com/v1',
      });
      break;

    case 'maxTokens':
      const maxTokensStr = await input({
        message: 'Enter max tokens:',
        default: String(currentValue || 4096),
      });
      newValue = parseInt(maxTokensStr);
      break;

    case 'temperature':
      const tempStr = await input({
        message: 'Enter temperature (0.0-2.0):',
        default: String(currentValue || 0.7),
      });
      newValue = parseFloat(tempStr);
      break;

    default:
      return;
  }

  configManager.set(action as any, newValue);
  console.log(chalk.green(`\n✓ ${action} updated successfully!`));
}