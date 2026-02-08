import pytest
from app.services.model_router import ModelRouter, ModelConfig


def test_model_config_ollama():
    config = ModelConfig(provider="ollama", model_name="gemma4")
    assert config.provider == "ollama"
    assert config.base_url is None


def test_model_config_openrouter():
    config = ModelConfig(provider="openrouter", model_name="meta-llama/llama-3-70b", api_key="test-key")
    assert config.provider == "openrouter"
    assert config.api_key == "test-key"


def test_model_router_init():
    router = ModelRouter()
    assert router is not None


def test_model_router_set_config():
    router = ModelRouter()
    config = ModelConfig(provider="ollama", model_name="gemma4")
    router.set_config(config)
    assert router.config.provider == "ollama"


def test_format_messages():
    router = ModelRouter()
    messages = router.format_messages(
        system="You are a helpful assistant.",
        history=[{"role": "user", "content": "Hello"}],
    )
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert len(messages) == 2
