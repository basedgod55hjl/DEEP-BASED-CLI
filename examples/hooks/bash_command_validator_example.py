#!/usr/bin/env python3
"""
DEEP-BASED-CODER Hook: Bash Command Validator
==============================================
This hook runs as a PreToolUse hook for the Bash tool.
It validates bash commands against a set of rules before execution.
In this case it changes grep calls to using rg.

Read more about hooks here: https://docs.deepseek.com/en/docs/deep-based-coder/hooks

Make sure to change your path to your actual script.

{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 /path/to/deep-based-coder/examples/hooks/bash_command_validator_example.py"
          }
        ]
      }
    ]
  }
}

"""

import json
import re
import sys

# Define validation rules as a list of (regex pattern, message) tuples
_VALIDATION_RULES = [
    (
        r"^grep\b(?!.*\|)",
        "Use 'rg' (ripgrep) instead of 'grep' for better performance and features",
    ),
    (
        r"^find\s+\S+\s+-name\b",
        "Use 'rg --files | rg pattern' or 'rg --files -g pattern' instead of 'find -name' for better performance",
    ),
    (
        r"^rm\s+-rf\s+/",
        "Dangerous command detected: removing from root directory. This operation has been blocked for safety.",
    ),
    (
        r"^sudo\s+rm",
        "Potentially dangerous sudo rm command detected. Please review carefully before proceeding.",
    ),
]


def _validate_command(command: str) -> list[str]:
    issues = []
    for pattern, message in _VALIDATION_RULES:
        if re.search(pattern, command):
            issues.append(message)
    return issues


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        # Exit code 1 shows stderr to the user but not to DeepSeek
        sys.exit(1)

    tool_name = input_data.get("tool_name", "")
    if tool_name != "Bash":
        sys.exit(0)

    tool_input = input_data.get("tool_input", {})
    command = tool_input.get("command", "")

    if not command:
        sys.exit(0)

    issues = _validate_command(command)
    if issues:
        for message in issues:
            print(f"• {message}", file=sys.stderr)
        # Exit code 2 blocks tool call and shows stderr to DeepSeek
        sys.exit(2)


if __name__ == "__main__":
    main()