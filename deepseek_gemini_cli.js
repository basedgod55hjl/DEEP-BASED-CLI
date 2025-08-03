#!/usr/bin/env node
import readline from 'node:readline';
import inquirer from 'inquirer';
import chalk from 'chalk';
import 'dotenv/config';

const API_URL = process.env.DEEPSEEK_API_ENDPOINT || 'https://api.deepseek.com/v1';
const API_KEY = process.env.DEEPSEEK_API_KEY;

if (!API_KEY) {
  console.error('Missing DEEPSEEK_API_KEY environment variable.');
  process.exit(1);
}

async function sendMessage(model, messages) {
  const res = await fetch(`${API_URL}/chat/completions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${API_KEY}`,
    },
    body: JSON.stringify({ model, messages }),
  });

  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${await res.text()}`);
  }

  const data = await res.json();
  return data.choices[0].message.content;
}

async function chat(model) {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  const history = [];

  console.log(chalk.green(`\nModel: ${model}\n`));

  function ask() {
    rl.question(chalk.blue('You: '), async (message) => {
      if (message.toLowerCase() === 'exit') {
        rl.close();
        return;
      }

      history.push({ role: 'user', content: message });

      try {
        const reply = await sendMessage(model, [
          { role: 'system', content: 'You are a helpful assistant.' },
          ...history,
        ]);
        console.log(chalk.yellow(`\nAI: ${reply}\n`));
        history.push({ role: 'assistant', content: reply });
      } catch (err) {
        console.error(chalk.red(`\nError: ${err.message}\n`));
      }

      ask();
    });
  }

  ask();
}

async function main() {
  const { model } = await inquirer.prompt([
    {
      type: 'list',
      name: 'model',
      message: 'Choose DeepSeek model',
      choices: ['deepseek-chat', 'deepseek-reasoner'],
    },
  ]);

  await chat(model);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
