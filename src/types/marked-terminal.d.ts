declare module 'marked-terminal' {
  import { Renderer } from 'marked';
  
  interface MarkedTerminalOptions {
    // Add any specific options if needed
  }
  
  class TerminalRenderer extends Renderer {
    constructor(options?: MarkedTerminalOptions);
  }
  
  export function markedTerminal(options?: MarkedTerminalOptions): TerminalRenderer;
}