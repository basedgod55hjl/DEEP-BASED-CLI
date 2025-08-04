import { BaseTool } from '../common/BaseTool';
import { ToolResponse, ToolStatus } from '../common/ToolResponse';
import { LLMQueryTool } from './LLMQueryTool';

export class FastReasoningEngine extends BaseTool {
  private readonly llm: LLMQueryTool;

  constructor(llm = new LLMQueryTool()) {
    super('fast_reasoning_engine', 'Simple chain-of-thought reasoning (stub)', ['reason']);
    this.llm = llm;
  }

  async execute(params: Record<string, unknown>): Promise<ToolResponse> {
    const question = (params.problem as string) ?? '';
    const start = Date.now();

    const res = await this.llm.execute({
      operation: 'chat_completion',
      model: 'deepseek-reasoner',
      messages: [
        { role: 'user', content: question },
        {
          role: 'assistant',
          prefix: true,
          content: "Let's reason step-by-step."
        }
      ],
      temperature: 0.2,
      maxTokens: 2048
    });

    return {
      success: true,
      message: 'Reasoning complete',
      status: ToolStatus.SUCCESS,
      executionTime: (Date.now() - start) / 1000,
      data: {
        reasoning: res.data?.response
      }
    };
  }

  getSchema(): Record<string, unknown> {
    return {
      type: 'object',
      properties: {
        problem: { type: 'string' }
      },
      required: ['problem']
    };
  }
}