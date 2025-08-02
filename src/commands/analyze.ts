import chalk from 'chalk';
import ora from 'ora';
import { marked } from 'marked';
import { markedTerminal } from 'marked-terminal';
import { DeepSeekAPI } from '../api/deepseek.js';
import { ConfigManager } from '../utils/config.js';
import { CodebaseAnalyzer } from '../utils/codebase.js';

// Configure marked to render markdown in terminal
marked.setOptions({
  renderer: new markedTerminal() as any,
});

export async function analyzeCommand(query: string, options: { 
  path?: string; 
  model?: string;
  summary?: boolean;
}) {
  const configManager = new ConfigManager();
  
  if (!configManager.isConfigured()) {
    console.error(chalk.red('Error: DeepSeek API key not configured'));
    console.log(chalk.yellow('Run "deepseek config" to set up your API key'));
    process.exit(1);
  }

  const targetPath = options.path || process.cwd();
  const analyzer = new CodebaseAnalyzer({ path: targetPath });

  const spinner = ora('Analyzing codebase...').start();

  try {
    if (options.summary) {
      const summary = await analyzer.generateSummary();
      spinner.stop();
      console.log(marked(summary));
      return;
    }

    const context = await analyzer.getContext(query);
    spinner.text = 'Querying DeepSeek...';

    const api = new DeepSeekAPI(configManager.getConfig());
    
    const systemPrompt = `You are a helpful assistant that analyzes codebases and answers questions about them. 
    Be concise but thorough in your responses. Use markdown formatting for better readability.`;

    const userPrompt = `Based on the following codebase context, please answer this question: ${query}\n\n${context}`;

    const response = await api.createChatCompletion({
      model: options.model || configManager.get('model') || 'deepseek-coder',
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userPrompt },
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