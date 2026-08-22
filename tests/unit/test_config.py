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
    assert str(config.model_registry_path) == "configs\\models.json"
    assert str(config.benchmark_cases_path) == "benchmarks\\cases.jsonl"
    assert str(config.results_path) == "results\\benchmark_results.jsonl"


def test_load_config_reads_environment_values() -> None:
    config = load_config(
        {
            "OLLAMA_BASE_URL": "http://rgb-ai.local:11434/",
            "RGB_AI_REQUEST_TIMEOUT_SECONDS": "30",
            "RGB_AI_MODEL_REGISTRY": "tmp/models.json",
            "RGB_AI_BENCHMARK_CASES": "tmp/cases.jsonl",
            "RGB_AI_RESULTS_PATH": "tmp/results.jsonl",
        }
    )

    assert config.ollama_base_url == "http://rgb-ai.local:11434"
    assert config.request_timeout_seconds == 30.0
    assert str(config.model_registry_path) == "tmp\\models.json"
    assert str(config.benchmark_cases_path) == "tmp\\cases.jsonl"
    assert str(config.results_path) == "tmp\\results.jsonl"


def test_load_config_rejects_empty_base_url() -> None:
    with pytest.raises(ConfigError, match="OLLAMA_BASE_URL"):
        load_config({"OLLAMA_BASE_URL": "   "})


def test_load_config_rejects_invalid_timeout() -> None:
    with pytest.raises(ConfigError, match="must be a number"):
        load_config({"RGB_AI_REQUEST_TIMEOUT_SECONDS": "soon"})


def test_load_config_rejects_non_positive_timeout() -> None:
    with pytest.raises(ConfigError, match="greater than 0"):
        load_config({"RGB_AI_REQUEST_TIMEOUT_SECONDS": "0"})
