import sys
from unittest.mock import patch

import deepseek_gemini_cli as cli
from deepseek_integration import DeepSeekModel


def test_chat_model_called(monkeypatch):
    with patch.object(cli, "DeepSeekClient") as mock_client:
        instance = mock_client.return_value
        instance.chat.return_value = "ok"
        cli.main(["hello"])  # default model chat
        instance.chat.assert_called_once_with("hello", model=DeepSeekModel.CHAT)


def test_reasoner_model_called(monkeypatch):
    with patch.object(cli, "DeepSeekClient") as mock_client:
        instance = mock_client.return_value
        instance.chat.return_value = "ok"
        cli.main(["hi", "--model", "reasoner"])
        instance.chat.assert_called_once_with("hi", model=DeepSeekModel.REASONER)
