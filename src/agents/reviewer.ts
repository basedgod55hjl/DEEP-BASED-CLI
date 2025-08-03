/**
 * @license
 * Copyright 2025 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

export interface ReviewAgent {
  review(original: string, rewritten: string): Promise<boolean>;
}

export const reviewAgent: ReviewAgent = {
  async review(original, rewritten) {
    // Placeholder: DeepSeek could assess whether the rewrite meets expectations.
    return original !== rewritten;
  },
};
