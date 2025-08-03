"""
Basic tests for DeepCLI
"""

import pytest
from deepcli import DeepSeekClient, DeepSeekModel, DeepCLIConfig


def test_import():
    """Test that imports work correctly"""
    assert DeepSeekClient is not None
    assert DeepSeekModel is not None
    assert DeepCLIConfig is not None


def test_model_enum():
    """Test model enum values"""
    assert DeepSeekModel.CHAT.value == "deepseek-chat"
    assert DeepSeekModel.REASONER.value == "deepseek-reasoner"


def test_config_creation():
    """Test config creation with defaults"""
    # This will fail without API key, which is expected
    with pytest.raises(ValueError):
        config = DeepCLIConfig()


def test_config_with_api_key(monkeypatch):
    """Test config creation with API key"""
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    config = DeepCLIConfig()
    assert config.api_key == "test-key"
    assert config.default_model == DeepSeekModel.CHAT
    assert config.temperature == 0.7