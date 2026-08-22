from __future__ import annotations

import os
from dataclasses import dataclass


DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_REQUEST_TIMEOUT_SECONDS = 120.0


@dataclass(frozen=True)
class Config:
    ollama_base_url: str
    request_timeout_seconds: float


class ConfigError(ValueError):
    """Raised when runtime configuration is invalid."""


def load_config(environ: dict[str, str] | None = None) -> Config:
    env = environ if environ is not None else os.environ
    base_url = env.get("OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL).strip()
    timeout_raw = env.get(
        "RGB_AI_REQUEST_TIMEOUT_SECONDS",
        str(DEFAULT_REQUEST_TIMEOUT_SECONDS),
    )

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
    )
