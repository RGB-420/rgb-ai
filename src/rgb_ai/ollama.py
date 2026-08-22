from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import httpx

NANOSECONDS_PER_SECOND = 1_000_000_000
NANOSECONDS_PER_MILLISECOND = 1_000_000


class OllamaError(Exception):
    """Base class for Ollama client errors."""


class OllamaConnectionError(OllamaError):
    """Raised when the configured Ollama server cannot be reached."""


class OllamaTimeoutError(OllamaError):
    """Raised when an Ollama request exceeds the configured timeout."""


class OllamaHTTPStatusError(OllamaError):
    """Raised when Ollama returns a non-success HTTP status."""

    def __init__(self, status_code: int, message: str):
        super().__init__(message)
        self.status_code = status_code


class OllamaMalformedResponseError(OllamaError):
    """Raised when Ollama returns JSON with an unexpected shape."""


@dataclass(frozen=True)
class GenerationMetrics:
    total_duration_ms: float | None
    load_duration_ms: float | None
    prompt_eval_duration_ms: float | None
    eval_duration_ms: float | None
    prompt_tokens: int | None
    output_tokens: int | None
    prompt_tokens_per_second: float | None
    output_tokens_per_second: float | None


@dataclass(frozen=True)
class GenerateResponse:
    model: str
    response_text: str
    done: bool | None
    metrics: GenerationMetrics
    raw_response: dict[str, Any]


@dataclass(frozen=True)
class OllamaModel:
    name: str
    modified_at: str | None
    size_bytes: int | None
    digest: str | None
    details: dict[str, Any]


class OllamaClient:
    def __init__(
        self,
        base_url: str,
        timeout_seconds: float,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._client = httpx.Client(
            base_url=base_url.rstrip("/"),
            timeout=timeout_seconds,
            transport=transport,
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "OllamaClient":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def generate(
        self,
        *,
        model: str,
        prompt: str,
        system: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> GenerateResponse:
        payload: dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }
        if system is not None:
            payload["system"] = system
        if options is not None:
            payload["options"] = options

        data = self._request_json(
            "POST",
            "/api/generate",
            content=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json; charset=utf-8"},
        )
        return parse_generate_response(data)

    def list_models(self) -> list[OllamaModel]:
        data = self._request_json("GET", "/api/tags")
        return parse_tags_response(data)

    def _request_json(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        try:
            response = self._client.request(method, path, **kwargs)
            response.raise_for_status()
            data = response.json()
        except httpx.TimeoutException as exc:
            raise OllamaTimeoutError(
                "Ollama request timed out at configured OLLAMA_BASE_URL"
            ) from exc
        except httpx.ConnectError as exc:
            raise OllamaConnectionError(
                "Unable to connect to Ollama at configured OLLAMA_BASE_URL"
            ) from exc
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code
            raise OllamaHTTPStatusError(
                status_code,
                f"Ollama returned HTTP {status_code}",
            ) from exc
        except ValueError as exc:
            raise OllamaMalformedResponseError(
                "Ollama returned a non-JSON response"
            ) from exc

        if not isinstance(data, dict):
            raise OllamaMalformedResponseError("Ollama response JSON must be an object")

        return data


def parse_generate_response(data: dict[str, Any]) -> GenerateResponse:
    model = data.get("model")
    response_text = data.get("response")
    done = data.get("done")

    if not isinstance(model, str) or not model:
        raise OllamaMalformedResponseError("Ollama generation response missing model")
    if not isinstance(response_text, str):
        raise OllamaMalformedResponseError(
            "Ollama generation response missing response text"
        )
    if done is not None and not isinstance(done, bool):
        raise OllamaMalformedResponseError("Ollama generation done field must be boolean")

    return GenerateResponse(
        model=model,
        response_text=response_text,
        done=done,
        metrics=parse_generation_metrics(data),
        raw_response=data,
    )


def parse_generation_metrics(data: dict[str, Any]) -> GenerationMetrics:
    prompt_tokens = _optional_int(data, "prompt_eval_count")
    output_tokens = _optional_int(data, "eval_count")
    prompt_eval_duration_ns = _optional_int(data, "prompt_eval_duration")
    output_eval_duration_ns = _optional_int(data, "eval_duration")

    return GenerationMetrics(
        total_duration_ms=_duration_ms(data, "total_duration"),
        load_duration_ms=_duration_ms(data, "load_duration"),
        prompt_eval_duration_ms=_duration_ms(data, "prompt_eval_duration"),
        eval_duration_ms=_duration_ms(data, "eval_duration"),
        prompt_tokens=prompt_tokens,
        output_tokens=output_tokens,
        prompt_tokens_per_second=_tokens_per_second(
            prompt_tokens,
            prompt_eval_duration_ns,
        ),
        output_tokens_per_second=_tokens_per_second(
            output_tokens,
            output_eval_duration_ns,
        ),
    )


def parse_tags_response(data: dict[str, Any]) -> list[OllamaModel]:
    models = data.get("models")
    if not isinstance(models, list):
        raise OllamaMalformedResponseError("Ollama tags response missing models list")

    parsed: list[OllamaModel] = []
    for item in models:
        if not isinstance(item, dict):
            raise OllamaMalformedResponseError("Ollama model entry must be an object")

        name = item.get("name") or item.get("model")
        if not isinstance(name, str) or not name:
            raise OllamaMalformedResponseError("Ollama model entry missing name")

        parsed.append(
            OllamaModel(
                name=name,
                modified_at=_optional_str(item, "modified_at"),
                size_bytes=_optional_int(item, "size"),
                digest=_optional_str(item, "digest"),
                details=_optional_dict(item, "details"),
            )
        )

    return parsed


def _duration_ms(data: dict[str, Any], key: str) -> float | None:
    value = _optional_int(data, key)
    if value is None:
        return None
    return value / NANOSECONDS_PER_MILLISECOND


def _tokens_per_second(tokens: int | None, duration_ns: int | None) -> float | None:
    if tokens is None or duration_ns is None or duration_ns <= 0:
        return None
    return tokens / (duration_ns / NANOSECONDS_PER_SECOND)


def _optional_int(data: dict[str, Any], key: str) -> int | None:
    value = data.get(key)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise OllamaMalformedResponseError(f"Ollama field {key} must be an integer")
    return value


def _optional_str(data: dict[str, Any], key: str) -> str | None:
    value = data.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise OllamaMalformedResponseError(f"Ollama field {key} must be a string")
    return value


def _optional_dict(data: dict[str, Any], key: str) -> dict[str, Any]:
    value = data.get(key)
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise OllamaMalformedResponseError(f"Ollama field {key} must be an object")
    return value
