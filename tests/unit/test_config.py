import pytest

from rgb_ai.config import (
    DEFAULT_OLLAMA_BASE_URL,
    ConfigError,
    load_config,
)


def test_load_config_uses_localhost_fallback() -> None:
    config = load_config({})

    assert config.ollama_base_url == DEFAULT_OLLAMA_BASE_URL
    assert config.request_timeout_seconds == 120.0


def test_load_config_reads_environment_values() -> None:
    config = load_config(
        {
            "OLLAMA_BASE_URL": "http://rgb-ai.local:11434/",
            "RGB_AI_REQUEST_TIMEOUT_SECONDS": "30",
        }
    )

    assert config.ollama_base_url == "http://rgb-ai.local:11434"
    assert config.request_timeout_seconds == 30.0


def test_load_config_rejects_empty_base_url() -> None:
    with pytest.raises(ConfigError, match="OLLAMA_BASE_URL"):
        load_config({"OLLAMA_BASE_URL": "   "})


def test_load_config_rejects_invalid_timeout() -> None:
    with pytest.raises(ConfigError, match="must be a number"):
        load_config({"RGB_AI_REQUEST_TIMEOUT_SECONDS": "soon"})


def test_load_config_rejects_non_positive_timeout() -> None:
    with pytest.raises(ConfigError, match="greater than 0"):
        load_config({"RGB_AI_REQUEST_TIMEOUT_SECONDS": "0"})
