import { createRequire } from 'module';

const require = createRequire(import.meta.url);
const markedTerminalModule = require('marked-terminal');

export const markedTerminal = markedTerminalModule.markedTerminal || markedTerminalModule.default;
export default markedTerminal;