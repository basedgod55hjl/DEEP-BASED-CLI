/**
 * @license
 * Copyright 2025 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import {readerAgent} from './reader.js';
import {planAgent} from './planner.js';
import {writeAgent} from './writer.js';
import {reviewAgent} from './reviewer.js';

/**
 * Rewrite a file using a set of DeepSeek-driven agents.
 */
export async function rewriteFile(path: string): Promise<boolean> {
  const original = await readerAgent.loadFile(path);
  const plan = await planAgent.plan(original);
  await writeAgent.rewrite(path, plan);
  const rewritten = await readerAgent.loadFile(path);
  return reviewAgent.review(original, rewritten);
}
