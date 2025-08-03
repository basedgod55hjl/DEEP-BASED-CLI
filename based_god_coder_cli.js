// Import required modules
const OpenAI = require("openai");
const readline = require('readline');
const { stdin: input, stdout: output } = require('process');

// Setup DeepSeek API
const openai = new OpenAI({
  baseURL: 'https://api.deepseek.com/v1',
  apiKey: process.env.DEEPSEEK_API_KEY
});

if (!process.env.DEEPSEEK_API_KEY) {
  console.error('DEEPSEEK_API_KEY environment variable not set');
  process.exit(1);
}

// Create readline interface
const rl = readline.createInterface({ input, output });

// Conversation history
const history = [];

// Display banner
console.log(`
██████╗  █████╗ ███████╗███████╗██████╗      ██████╗  ██████╗ ██████╗ 
██╔══██╗██╔══██╗██╔════╝██╔════╝██╔══██╗    ██╔════╝ ██╔═══██╗██╔══██╗
██████╔╝███████║███████╗█████╗  ██║  ██║    ██║  ███╗██║   ██║██║  ██║
██╔══██╗██╔══██║╚════██║██╔══╝  ██║  ██║    ██║   ██║██║   ██║██║  ██║
██████╔╝██║  ██║███████║███████╗██████╔╝    ╚██████╔╝╚██████╔╝██████╔╝
╚═════╝ ╚═╝  ╚═╝╚══════╝╚══════╝╚═════╝      ╚═════╝  ╚═════╝ ╚═════╝ 
                                                                       
         ██████╗ ██████╗ ██████╗ ███████╗██████╗      ██████╗██╗     ██╗
        ██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔══██╗    ██╔════╝██║     ██║
        ██║     ██║   ██║██║  ██║█████╗  ██████╔╝    ██║     ██║     ██║
        ██║     ██║   ██║██║  ██║██╔══╝  ██╔══██╗    ██║     ██║     ██║
        ╚██████╗╚██████╔╝██████╔╝███████╗██║  ██║    ╚██████╗███████╗██║
         ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝     ╚═════╝╚══════╝╚═╝
`);

console.log('BASED GOD CODER CLI - Made by @Lucariolucario55 on Telegram');
console.log('\\nType "exit" to quit. Press Enter to send message.\\n');

// Chat function
async function chat() {
  rl.question('You: ', async (message) => {
    if (message.toLowerCase() === 'exit') {
      console.log('\\nStay based! 🔥');
      rl.close();
      return;
    }

    // Add user message to history
    history.push({ role: "user", content: message });

    try {
      const completion = await openai.chat.completions.create({
        model: "deepseek-chat",
        messages: [
          { role: "system", content: "You are a helpful assistant." },
          ...history
        ],
      });

      const response = completion.choices[0].message.content;
      console.log('\\nAI: ' + response + '\\n');

      // Add AI response to history
      history.push({ role: "assistant", content: response });

    } catch (error) {
      console.log('\\nError: ' + error.message + '\\n');
    }

    // Ask for next message
    chat();
  });
}

// Start chatting
chat(); 