import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.DEEPSEEK_API_KEY,
  baseURL: "https://api.deepseek.com"
});

async function main() {
  const chat = await client.chat.completions.create({
    model: "deepseek-chat",
    messages: [{ role: "user", content: "Hello from DeepSeek chat" }]
  });
  console.log("Chat:", chat.choices[0].message.content);

  const reason = await client.chat.completions.create({
    model: "deepseek-reasoner",
    messages: [{ role: "user", content: "Explain the Pythagorean theorem" }]
  });
  console.log("Reasoner:", reason.choices[0].message.content);
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
