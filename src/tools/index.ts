// REPLACE ENTIRE FILE WITH DYNAMIC FACTORY REGISTRY
// Auto-generated dynamic factory registry for tools. Each entry returns a promise
// resolving to a **constructed** tool instance. This allows lazy loading so that
// heavyweight dependencies (e.g. @xenova/transformers, onnxruntime-node) are only
// pulled into memory when the specific tool is actually executed.

import { BaseTool } from '../common/BaseTool';

export type ToolFactory = () => Promise<BaseTool>;

/**
 * Mapping from lower-cased class name to an async factory that constructs the
 * corresponding tool.  Keep the keys in sync with the concrete tool class
 * names because callers reference them via `ClassName.toLowerCase()`.
 */
export const toolFactories: Record<string, ToolFactory> = {
  llmquerytool: async () => new (await import('./LLMQueryTool.js')).LLMQueryTool(),
  vectordatabasetool: async () => new (await import('./VectorDatabaseTool.js')).VectorDatabaseTool(),
  simpleembeddingtool: async () => new (await import('./SimpleEmbeddingTool.js')).SimpleEmbeddingTool(),
  fastreasoningengine: async () => new (await import('./FastReasoningEngine.js')).FastReasoningEngine(),
  ragpipelinetool: async () => new (await import('./RAGPipelineTool.js')).RAGPipelineTool(),
  unifiedagentsystem: async () => new (await import('./UnifiedAgentSystem.js')).UnifiedAgentSystem(),
  plannertool: async () => new (await import('./PlannerTool.js')).PlannerTool(),
  readertool: async () => new (await import('./ReaderTool.js')).ReaderTool(),
  writertool: async () => new (await import('./WriterTool.js')).WriterTool(),
  reviewertool: async () => new (await import('./ReviewerTool.js')).ReviewerTool(),
  coderagenttool: async () => new (await import('./CoderAgentTool.js')).CoderAgentTool(),
  selfhealertool: async () => new (await import('./SelfHealerTool.js')).SelfHealerTool(),
  commandexecutortool: async () => new (await import('./CommandExecutorTool.js')).CommandExecutorTool(),
  debuggertool: async () => new (await import('./DebuggerTool.js')).DebuggerTool(),
  datadogintegrationtool: async () => new (await import('./DatadogIntegrationTool.js')).DatadogIntegrationTool(),
  visiontool: async () => new (await import('./VisionTool.js')).VisionTool(),
  webscrapertool: async () => new (await import('./WebScraperTool.js')).WebScraperTool(),
  memoryrankertool: async () => new (await import('./MemoryRankerTool.js')).MemoryRankerTool(),
  swarmtool: async () => new (await import('./SwarmTool.js')).SwarmTool()
};

// NOTE: If you add a new tool file, simply add one line above instead of having
// to touch the ToolManager logic. This preserves the lazy-loading behaviour.