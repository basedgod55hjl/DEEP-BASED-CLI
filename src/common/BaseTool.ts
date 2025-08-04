import { ToolResponse } from './ToolResponse';

export abstract class BaseTool {
  public readonly name: string;
  public readonly description: string;
  public readonly capabilities: string[];

  protected constructor(name: string, description: string, capabilities: string[] = []) {
    this.name = name;
    this.description = description;
    this.capabilities = capabilities;
  }

  abstract execute(params: Record<string, unknown>): Promise<ToolResponse>;
  abstract getSchema(): Record<string, unknown>;
}