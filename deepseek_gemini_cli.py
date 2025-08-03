#!/usr/bin/env python3
"""Minimal CLI similar to Gemini CLI using DeepSeek models.

This script provides a streamlined command-line interface that mirrors the
Gemini CLI's basic usage but routes all requests through the DeepSeek API.

Usage:
  python deepseek_gemini_cli.py "Hello" --model chat
  python deepseek_gemini_cli.py "Solve 2+2" --model reasoner

The API key must be provided via the DEEPSEEK_API_KEY environment variable.
"""

from __future__ import annotations

import argparse
import sys
from typing import Iterable

from deepseek_integration import DeepSeekClient, DeepSeekModel


def stream_print(chunks: Iterable[str]) -> None:
    """Print streaming chunks as they arrive."""
    for chunk in chunks:
        sys.stdout.write(chunk)
        sys.stdout.flush()
    print()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="DeepSeek Gemini-style CLI")
    parser.add_argument("prompt", help="Prompt to send to the model")
    parser.add_argument(
        "--model",
        choices=["chat", "reasoner"],
        default="chat",
        help="Select DeepSeek model to use",
    )
    parser.add_argument(
        "--stream", action="store_true", help="Stream output as it is generated"
    )
    args = parser.parse_args(argv)

    client = DeepSeekClient()
    model = DeepSeekModel.CHAT if args.model == "chat" else DeepSeekModel.REASONER

    if args.stream:
        stream_print(client.chat(args.prompt, model=model, stream=True))
    else:
        response = client.chat(args.prompt, model=model)
        print(response)


if __name__ == "__main__":
    main()
