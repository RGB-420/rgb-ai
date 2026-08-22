from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1


class ResultStorageError(OSError):
    """Raised when benchmark results cannot be written."""


@dataclass(frozen=True)
class BenchmarkError:
    type: str
    message: str


@dataclass(frozen=True)
class BenchmarkResult:
    schema_version: int
    result_id: str
    run_id: str
    timestamp: str
    test_id: str
    category: str
    variant: str
    model_id: str
    provider: str
    provider_model: str
    prompt: str
    formatted_prompt: str
    system_prompt: str | None
    context: list[dict[str, Any]]
    examples: list[dict[str, str]]
    generation_options: dict[str, Any]
    response_text: str | None
    thinking_text: str | None
    raw_provider_response: dict[str, Any] | None
    metrics: dict[str, Any]
    estimated_token_split: dict[str, Any]
    evaluation: dict[str, Any]
    error: dict[str, str] | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class JsonlResultStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def append(self, result: BenchmarkResult) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as file:
                json.dump(result.to_dict(), file, ensure_ascii=False, separators=(",", ":"))
                file.write("\n")
        except OSError as exc:
            raise ResultStorageError(
                f"Unable to append benchmark result to {self.path}"
            ) from exc


def load_jsonl_results(path: str | Path) -> list[dict[str, Any]]:
    results_path = Path(path)
    return [
        json.loads(line)
        for line in results_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def estimate_output_token_split(
    *,
    thinking_text: str | None,
    response_text: str | None,
    output_tokens: int | None,
) -> dict[str, Any]:
    thinking = thinking_text or ""
    response = response_text or ""
    thinking_characters = len(thinking)
    response_characters = len(response)

    base = {
        "method": "character_ratio_v1",
        "authoritative": False,
        "thinking_characters": thinking_characters,
        "response_characters": response_characters,
        "thinking_share": None,
        "response_share": None,
        "estimated_thinking_tokens": None,
        "estimated_response_tokens": None,
        "available": False,
        "reason": None,
    }

    if output_tokens is None:
        return {**base, "reason": "missing_output_tokens"}

    total_characters = thinking_characters + response_characters
    if total_characters == 0:
        return {**base, "reason": "empty_texts"}

    thinking_share = thinking_characters / total_characters
    response_share = response_characters / total_characters
    estimated_thinking_tokens = round(output_tokens * thinking_share)
    estimated_response_tokens = output_tokens - estimated_thinking_tokens

    return {
        **base,
        "thinking_share": thinking_share,
        "response_share": response_share,
        "estimated_thinking_tokens": estimated_thinking_tokens,
        "estimated_response_tokens": estimated_response_tokens,
        "available": True,
    }
