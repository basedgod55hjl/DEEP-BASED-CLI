/**
 * @license
 * Copyright 2025 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

export interface PlanAgent {
  plan(content: string): Promise<string>;
}

export const planAgent: PlanAgent = {
  async plan(content) {
    // Placeholder: use DeepSeek to analyze file content and propose a rewrite plan.
    return `Rewrite plan for ${content.length} characters`;
  },
};
