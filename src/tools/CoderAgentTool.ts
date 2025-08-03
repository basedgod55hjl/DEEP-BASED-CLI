import { BaseTool } from '../common/BaseTool';
import { ToolResponse, ToolStatus } from '../common/ToolResponse';
import { LLMQueryTool } from './LLMQueryTool';

interface GenerateParams {
  language: string;
  description: string;
  style?: string;
}

export class CoderAgentTool extends BaseTool {
  private readonly llm = new LLMQueryTool();

  constructor() {
    super('coder_agent_tool', 'Generates code snippets/functions/classes', ['generate_code']);
  }

  async execute(params: Record<string, unknown>): Promise<ToolResponse> {
    const { language, description, style } = params as unknown as GenerateParams;
    if (!language || !description) {
      return { success: false, message: 'language and description required', status: ToolStatus.FAILED };
    }

    const prompt = `Write a ${language} ${style ?? ''} implementation for: ${description}`;
    const res = await this.llm.execute({ operation: 'chat_completion', prompt, model: language === 'typescript' ? 'deepseek-coder' : 'deepseek-chat', temperature: 0.3 });

    return {
      success: true,
      message: 'Code generated',
      status: ToolStatus.SUCCESS,
      data: { code: (res.data as any)?.response }
    };
  }

  getSchema(): Record<string, unknown> {
    return {
      type: 'object',
      properties: {
        language: { type: 'string' },
        description: { type: 'string' },
        style: { type: 'string' }
      },
      required: ['language', 'description']
    };
  }
}