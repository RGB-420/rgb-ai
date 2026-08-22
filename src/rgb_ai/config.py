from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_REQUEST_TIMEOUT_SECONDS = 120.0
DEFAULT_MODEL_REGISTRY_PATH = "configs/models.json"
DEFAULT_BENCHMARK_CASES_PATH = "benchmarks/cases.jsonl"
DEFAULT_RESULTS_PATH = "results/benchmark_results.jsonl"


@dataclass(frozen=True)
class Config:
    ollama_base_url: str
    request_timeout_seconds: float
    model_registry_path: Path
    benchmark_cases_path: Path
    results_path: Path


class ConfigError(ValueError):
    """Raised when runtime configuration is invalid."""


def load_config(environ: dict[str, str] | None = None) -> Config:
    env = environ if environ is not None else os.environ
    base_url = env.get("OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL).strip()
    timeout_raw = env.get(
        "RGB_AI_REQUEST_TIMEOUT_SECONDS",
        str(DEFAULT_REQUEST_TIMEOUT_SECONDS),
    )
    model_registry_path = env.get("RGB_AI_MODEL_REGISTRY", DEFAULT_MODEL_REGISTRY_PATH)
    benchmark_cases_path = env.get("RGB_AI_BENCHMARK_CASES", DEFAULT_BENCHMARK_CASES_PATH)
    results_path = env.get("RGB_AI_RESULTS_PATH", DEFAULT_RESULTS_PATH)

    if not base_url:
        raise ConfigError("OLLAMA_BASE_URL must not be empty")

    try:
        timeout_seconds = float(timeout_raw)
    except ValueError as exc:
        raise ConfigError("RGB_AI_REQUEST_TIMEOUT_SECONDS must be a number") from exc

    if timeout_seconds <= 0:
        raise ConfigError("RGB_AI_REQUEST_TIMEOUT_SECONDS must be greater than 0")

    return Config(
        ollama_base_url=base_url.rstrip("/"),
        request_timeout_seconds=timeout_seconds,
        model_registry_path=Path(model_registry_path),
        benchmark_cases_path=Path(benchmark_cases_path),
        results_path=Path(results_path),
    )
