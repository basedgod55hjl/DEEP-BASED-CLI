#!/usr/bin/env python3
"""Minimal Gemini-style CLI for DeepSeek models.

Supports chat and simple tool-call examples using DeepSeek's
``deepseek-chat`` and ``deepseek-reasoner`` models. The interface is
inspired by Google's Gemini CLI but routed to DeepSeek APIs.

The API key is hard-coded at the user's request. For real deployments
consider using environment variables or secret management.
"""
import argparse
import httpx

API_KEY = "sk-9af038dd3bdd46258c4a9d02850c9a6d"
API_URL = "https://api.deepseek.com/v1/chat/completions"


def call_deepseek(model: str, messages, tools=None):
    """Call DeepSeek chat completion endpoint."""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {"model": model, "messages": messages}
    if tools:
        payload["tools"] = tools
    with httpx.Client(timeout=30.0) as client:
        resp = client.post(API_URL, headers=headers, json=payload)
        resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


def cmd_chat(args):
    messages = [{"role": "user", "content": args.prompt}]
    print(call_deepseek("deepseek-chat", messages))


def cmd_tool(args):
    messages = [{"role": "user", "content": args.prompt}]
    tools = [
        {
            "type": "function",
            "function": {
                "name": "echo",
                "description": "Echo back the supplied text",
                "parameters": {
                    "type": "object",
                    "properties": {"text": {"type": "string"}},
                    "required": ["text"],
                },
            },
        }
    ]
    print(call_deepseek("deepseek-reasoner", messages, tools=tools))


def main():
    parser = argparse.ArgumentParser(description="DeepSeek CLI")
    sub = parser.add_subparsers(dest="command")

    chat_p = sub.add_parser("chat", help="Chat with deepseek-chat model")
    chat_p.add_argument("prompt", help="Prompt to send")
    chat_p.set_defaults(func=cmd_chat)

    tool_p = sub.add_parser("tool", help="Example tool call using deepseek-reasoner")
    tool_p.add_argument("prompt", help="Prompt to send")
    tool_p.set_defaults(func=cmd_tool)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return
    args.func(args)


if __name__ == "__main__":
    main()
