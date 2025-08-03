import { BaseTool } from '../common/BaseTool';
import { ToolResponse, ToolStatus } from '../common/ToolResponse';
import axios from 'axios';

export class DatadogIntegrationTool extends BaseTool {
  constructor() {
    super('datadog_integration_tool', 'Sends custom metric to Datadog', ['metric']);
  }

  async execute(params: Record<string, unknown>): Promise<ToolResponse> {
    const apiKey = process.env.DATADOG_API_KEY;
    if (!apiKey) return { success: false, message: 'DATADOG_API_KEY missing', status: ToolStatus.FAILED };
    const metric = (params.metric as string) ?? 'deepcli.event';
    const value = params.value ?? 1;
    await axios.post('https://api.datadoghq.com/api/v1/series', {
      series: [{ metric, points: [[Date.now() / 1000, value]], type: 'count', interval: 1 }]
    }, { headers: { 'DD-API-KEY': apiKey, 'Content-Type': 'application/json' } });
    return { success: true, message: 'Metric sent', status: ToolStatus.SUCCESS };
  }

  getSchema(): Record<string, unknown> {
    return { type: 'object', properties: { metric: { type: 'string' }, value: { type: 'number' } } };
  }
}