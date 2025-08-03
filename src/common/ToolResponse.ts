export enum ToolStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  SUCCESS = 'success',
  FAILED = 'failed',
  TIMEOUT = 'timeout'
}

export interface ToolResponse<Data = unknown> {
  success: boolean;
  message: string;
  data?: Data;
  status?: ToolStatus;
  executionTime?: number;
  metadata?: Record<string, unknown>;
  breakLoop?: boolean;
}