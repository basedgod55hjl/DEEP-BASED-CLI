import { ToolManager } from '../dist/ToolManager.js';

test('ToolManager lists tools', async () => {
  const tm = new ToolManager();
  expect(tm.listTools().length).toBeGreaterThan(0);
});