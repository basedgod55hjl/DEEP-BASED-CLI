/**
 * @license
 * Copyright 2025 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import {promises as fs} from 'node:fs';

export interface ReaderAgent {
  loadFile(path: string): Promise<string>;
}

export const readerAgent: ReaderAgent = {
  async loadFile(path) {
    return fs.readFile(path, 'utf8');
  },
};
