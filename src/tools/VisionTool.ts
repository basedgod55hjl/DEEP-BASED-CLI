import { BaseTool } from '../common/BaseTool';
import { ToolResponse, ToolStatus } from '../common/ToolResponse';
import { GGUFVision } from '../vision/GGUFVision.js';

export class VisionTool extends BaseTool {
  constructor() {
    super('vision_tool', 'Generates alt-text for images', ['describe']);
  }

  async execute(params: Record<string, unknown>): Promise<ToolResponse> {
    const buffer = params.image as Uint8Array;
    if (!(buffer instanceof Uint8Array)) {
      return { success: false, message: 'image (Uint8Array) required', status: ToolStatus.FAILED };
    }
    const vision = await GGUFVision.get();
    const desc = await vision.describe(buffer);
    return { success: true, message: 'Image described', status: ToolStatus.SUCCESS, data: { description: desc } };
  }

  getSchema(): Record<string, unknown> {
    return { type: 'object', properties: { image: { type: 'string', description: 'base64' } }, required: ['image'] };
  }
}