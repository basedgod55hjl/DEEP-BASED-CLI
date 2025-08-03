#!/usr/bin/env node
import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import { ToolManager } from '../ToolManager.js';

const program = new Command();
const tm = new ToolManager();

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
    const res = await tm.executeTool('unifiedagentsystem', {
      operation: 'conversation',
      message: msg.join(' '),
      persona: opts.persona
    });
    spinner.stop();
    console.log(chalk.green(res.data?.response));
  });

program
  .command('scrape')
  .description('Scrape a webpage and store context')
  .argument('<url>', 'URL to scrape')
  .action(async (url) => {
    const res = await tm.executeTool('webscrapertool', { url });
    console.log(res.message, res.data);
  });

program
  .command('reason')
  .description('Chain-of-thought reasoning')
  .argument('<question...>', 'question')
  .action(async (q) => {
    const res = await tm.executeTool('fastreasoningengine', { problem: q.join(' ') });
    console.log(res.data?.reasoning);
  });

program
  .command('code')
  .description('Generate code via swarm pipeline')
  .argument('<spec...>', 'code spec')
  .action(async (spec) => {
    const res = await tm.executeTool('swarmtool', { task: spec.join(' ') });
    console.log(res.data?.code);
  });

program
  .command('exec')
  .description('Execute safe shell command (echo, ls)')
  .argument('<command...>', 'cmd')
  .action(async (cmdParts) => {
    const res = await tm.executeTool('commandexecutortool', { command: cmdParts.join(' ') });
    console.log(res.data?.stdout);
  });

program
  .command('heal')
  .description('Run test suite and report status')
  .action(async () => {
    const res = await tm.executeTool('selfhealertool', {});
    console.log(res.message);
  });

program
  .command('metric')
  .description('Send metric to Datadog')
  .argument('<name>', 'metric name')
  .argument('[value]', 'value', '1')
  .action(async (name, value) => {
    const res = await tm.executeTool('datadogintegrationtool', { metric: name, value: Number(value) });
    console.log(res.message);
  });

program.parseAsync();