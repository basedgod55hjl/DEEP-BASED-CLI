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

// Specific response interfaces for better type safety
export interface LLMResponse {
  response: string;
  raw?: unknown;
}

export interface CodeResponse {
  code: string;
  language?: string;
}

export interface ReasoningResponse {
  reasoning: string;
  steps?: string[];
}

export interface CommandResponse {
  stdout: string;
  stderr?: string;
  exitCode?: number;
}

export interface VisionResponse {
  description: string;
  confidence?: number;
}

export interface PlanResponse {
  plan: string;
  steps?: string[];
}