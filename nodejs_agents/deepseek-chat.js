/**
 * DeepSeek Chat Agent for Node.js
 * Supports chat, FIM (Fill-in-Middle), and prefix completions
 * Updated with new API key and beta API support
 */

const https = require('https');

class DeepSeekAgent {
  constructor(apiKey = 'sk-90e0dd863b8c4e0d879a02851a0ee194') {
    this.apiKey = apiKey;
    this.baseURL = 'api.deepseek.com';
    this.useBetaAPI = true; // Use beta API for FIM and prefix completion
  }

  /**
   * Make API request to DeepSeek
   */
  async makeRequest(endpoint, data) {
    return new Promise((resolve, reject) => {
      const requestData = JSON.stringify(data);
      
      // Use beta API for completions, regular API for chat
      const apiPath = this.useBetaAPI && (endpoint.includes('completions') || endpoint.includes('chat/completions')) 
        ? `/beta/${endpoint}` 
        : `/v1/${endpoint}`;
      
      const options = {
        hostname: this.baseURL,
        port: 443,
        path: apiPath,
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Length': Buffer.byteLength(requestData)
        }
      };

      const req = https.request(options, (res) => {
        let responseData = '';

        res.on('data', (chunk) => {
          responseData += chunk;
        });

        res.on('end', () => {
          try {
            const parsed = JSON.parse(responseData);
            if (res.statusCode === 200) {
              resolve(parsed);
            } else {
              reject(new Error(parsed.error?.message || `API error: ${res.statusCode}`));
            }
          } catch (e) {
            reject(new Error(`Failed to parse response: ${e.message}`));
          }
        });
      });

      req.on('error', (error) => {
        reject(error);
      });

      req.write(requestData);
      req.end();
    });
  }

  /**
   * Chat completion
   */
  async chat(messages, options = {}) {
    const data = {
      model: options.model || 'deepseek-chat',
      messages: messages,
      temperature: options.temperature || 0.7,
      max_tokens: options.max_tokens || 1000,
      top_p: options.top_p || 0.95,
      ...options
    };

    return await this.makeRequest('chat/completions', data);
  }

  /**
   * FIM (Fill-in-Middle) completion
   */
  async fimComplete(prefix, suffix = '', options = {}) {
    const fimPrompt = `<PRE>${prefix}<MID>${suffix}<SUF>`;
    
    const data = {
      model: options.model || 'deepseek-coder',
      prompt: fimPrompt,
      max_tokens: options.max_tokens || 1024,
      temperature: options.temperature || 0.3,
      stop: ["<PRE>", "<MID>", "<SUF>"],
      ...options
    };

    return await this.makeRequest('completions', data);
  }

  /**
   * Prefix completion
   */
  async prefixComplete(prefix, options = {}) {
    const messages = [
      {
        role: 'system',
        content: options.systemPrompt || 'Continue the following text naturally:'
      },
      {
        role: 'assistant',
        content: prefix,
        prefix: true
      }
    ];

    return await this.chat(messages, {
      model: options.model || 'deepseek-chat',
      temperature: options.temperature || 0.7,
      max_tokens: options.max_tokens || 512,
      ...options
    });
  }

  /**
   * Stream chat completion
   */
  async *streamChat(messages, options = {}) {
    const data = {
      model: options.model || 'deepseek-chat',
      messages: messages,
      temperature: options.temperature || 0.7,
      max_tokens: options.max_tokens || 1000,
      stream: true,
      ...options
    };

    const requestData = JSON.stringify(data);
    
    const apiPath = this.useBetaAPI ? '/beta/chat/completions' : '/v1/chat/completions';
    
    const streamOptions = {
      hostname: this.baseURL,
      port: 443,
      path: apiPath,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Length': Buffer.byteLength(requestData)
      }
    };

    let buffer = ''; // To handle partial lines

    await new Promise((resolve, reject) => {
      const req = https.request(streamOptions, (res) => {
        res.on('data', (chunk) => {
          buffer += chunk.toString();
          let newlineIndex;
          while ((newlineIndex = buffer.indexOf('\n')) !== -1) {
            const line = buffer.substring(0, newlineIndex).trim();
            buffer = buffer.substring(newlineIndex + 1);

            if (line.startsWith('data: ')) {
              const data = line.slice(6);
              if (data === '[DONE]') {
                resolve(); // End of stream
                return;
              }
              try {
                const parsed = JSON.parse(data);
                if (parsed.choices?.[0]?.delta?.content) {
                  // Yield the content directly
                  resolve(parsed.choices[0].delta.content);
                }
              } catch (e) {
                // Ignore parse errors, or log for debugging
                // console.error('Stream parse error:', e.message, 'Data:', data);
              }
            }
          }
        });

        res.on('end', () => {
          resolve(); // Stream ended
        });
      });

      req.on('error', (error) => {
        reject(error);
      });

      req.write(requestData);
      req.end();
    });
  }

  /**
   * Set API key
   */
  setApiKey(apiKey) {
    this.apiKey = apiKey;
  }

  /**
   * Toggle beta API usage
   */
  setUseBetaAPI(useBeta) {
    this.useBetaAPI = useBeta;
  }
}

// Export for use as module
module.exports = DeepSeekAgent;

// Example usage
async function main() {
  const agent = new DeepSeekAgent();

  try {
    // Example 1: Chat completion
    console.log('=== Chat Completion ===');
    const chatResponse = await agent.chat([
      { role: 'system', content: 'You are a helpful assistant.' },
      { role: 'user', content: 'What is the capital of France?' }
    ]);
    console.log('Chat:', chatResponse.choices[0].message.content);

    // Example 2: FIM completion
    console.log('\n=== FIM Completion ===');
    const fimResponse = await agent.fimComplete(
      'def fibonacci(n):\n    if n <= 1:\n        return n\n    ',
      '\n    return fib'
    );
    console.log('FIM:', fimResponse.choices[0].text);

    // Example 3: Prefix completion
    console.log('\n=== Prefix Completion ===');
    const prefixResponse = await agent.prefixComplete(
      'The meaning of life is'
    );
    console.log('Prefix:', prefixResponse.choices[0].message.content);

    // Example 4: Stream chat
    console.log('\n=== Stream Chat ===');
    console.log('Stream: ');
    for await (const chunk of agent.streamChat([
      { role: 'user', content: 'Tell me a short joke' }
    ])) {
      process.stdout.write(chunk);
    }
    console.log('\n');

  } catch (error) {
    console.error('Error:', error.message);
  }
}

// Run examples if called directly
if (require.main === module) {
  main();
} 