from __future__ import annotations

import httpx
import pytest

from rgb_ai.ollama import (
    OllamaClient,
    OllamaConnectionError,
    OllamaHTTPStatusError,
    OllamaMalformedResponseError,
    OllamaTimeoutError,
    parse_generate_response,
    parse_tags_response,
)


def _client(handler) -> OllamaClient:
    return OllamaClient(
        base_url="http://ollama.test",
        timeout_seconds=5,
        transport=httpx.MockTransport(handler),
    )


def test_generate_posts_non_streaming_request_and_parses_metrics() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/api/generate"
        assert request.read()
        payload = request.content.decode()
        assert '"stream":false' in payload.replace(" ", "")
        return httpx.Response(
            200,
            json={
                "model": "qwen3:0.6b",
                "response": "SI",
                "done": True,
                "total_duration": 2_000_000_000,
                "load_duration": 500_000_000,
                "prompt_eval_count": 10,
                "prompt_eval_duration": 250_000_000,
                "eval_count": 4,
                "eval_duration": 1_000_000_000,
            },
        )

    with _client(handler) as client:
        result = client.generate(model="qwen3:0.6b", prompt="Responde SI")

    assert result.model == "qwen3:0.6b"
    assert result.response_text == "SI"
    assert result.done is True
    assert result.raw_response["response"] == "SI"
    assert result.metrics.total_duration_ms == 2000.0
    assert result.metrics.load_duration_ms == 500.0
    assert result.metrics.prompt_tokens == 10
    assert result.metrics.output_tokens == 4
    assert result.metrics.prompt_tokens_per_second == 40.0
    assert result.metrics.output_tokens_per_second == 4.0


def test_list_models_parses_tags_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/api/tags"
        return httpx.Response(
            200,
            json={
                "models": [
                    {
                        "name": "qwen3:0.6b",
                        "modified_at": "2026-08-21T12:00:00Z",
                        "size": 123,
                        "digest": "abc",
                        "details": {"family": "qwen3"},
                    }
                ]
            },
        )

    with _client(handler) as client:
        models = client.list_models()

    assert len(models) == 1
    assert models[0].name == "qwen3:0.6b"
    assert models[0].size_bytes == 123
    assert models[0].details == {"family": "qwen3"}


def test_generate_maps_timeout_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("slow", request=request)

    with _client(handler) as client:
        with pytest.raises(OllamaTimeoutError):
            client.generate(model="qwen3:0.6b", prompt="hello")


def test_generate_maps_connection_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("no route", request=request)

    with _client(handler) as client:
        with pytest.raises(OllamaConnectionError):
            client.generate(model="qwen3:0.6b", prompt="hello")


def test_generate_maps_http_status_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"error": "model not found"})

    with _client(handler) as client:
        with pytest.raises(OllamaHTTPStatusError) as exc_info:
            client.generate(model="missing", prompt="hello")

    assert exc_info.value.status_code == 404


def test_generate_maps_non_json_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"not json")

    with _client(handler) as client:
        with pytest.raises(OllamaMalformedResponseError, match="non-JSON"):
            client.generate(model="qwen3:0.6b", prompt="hello")


def test_parse_generate_response_rejects_missing_text() -> None:
    with pytest.raises(OllamaMalformedResponseError, match="response text"):
        parse_generate_response({"model": "qwen3:0.6b", "done": True})


def test_parse_generate_response_rejects_invalid_metric_type() -> None:
    with pytest.raises(OllamaMalformedResponseError, match="prompt_eval_count"):
        parse_generate_response(
            {
                "model": "qwen3:0.6b",
                "response": "hello",
                "prompt_eval_count": "10",
            }
        )


def test_parse_tags_response_accepts_model_key_fallback() -> None:
    models = parse_tags_response({"models": [{"model": "llama3.2:1b"}]})

    assert models[0].name == "llama3.2:1b"


def test_parse_tags_response_rejects_missing_models_list() -> None:
    with pytest.raises(OllamaMalformedResponseError, match="models list"):
        parse_tags_response({})
