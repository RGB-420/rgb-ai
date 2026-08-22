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
    raw_provider_response: dict[str, Any] | None
    metrics: dict[str, Any]
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
