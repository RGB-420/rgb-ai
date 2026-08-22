from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class BenchmarkCaseError(ValueError):
    """Raised when benchmark case data is invalid."""


@dataclass(frozen=True)
class ContextItem:
    text: str
    source_id: str | None
    chunk_id: str | None


@dataclass(frozen=True)
class Example:
    prompt: str
    response: str


@dataclass(frozen=True)
class BenchmarkCase:
    test_id: str
    category: str
    variant: str
    prompt: str
    system_prompt: str | None
    context: list[ContextItem]
    examples: list[Example]
    generation_options: dict[str, Any]
    expected: dict[str, Any] | None
    tags: list[str]
    difficulty: str | None


def load_benchmark_cases(path: str | Path) -> list[BenchmarkCase]:
    cases_path = Path(path)
    cases: list[BenchmarkCase] = []
    seen_ids: set[str] = set()

    for line_number, line in enumerate(
        cases_path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        if not line.strip():
            continue

        try:
            raw_case = json.loads(line)
        except json.JSONDecodeError as exc:
            raise BenchmarkCaseError(
                f"Invalid JSONL in {cases_path} at line {line_number}: {exc.msg}"
            ) from exc

        case = parse_benchmark_case(raw_case, line_number=line_number)
        if case.test_id in seen_ids:
            raise BenchmarkCaseError(f"Duplicate test_id in benchmark cases: {case.test_id}")
        seen_ids.add(case.test_id)
        cases.append(case)

    return cases


def parse_benchmark_case(data: Any, *, line_number: int | None = None) -> BenchmarkCase:
    location = f" at line {line_number}" if line_number is not None else ""
    if not isinstance(data, dict):
        raise BenchmarkCaseError(f"Benchmark case{location} must be an object")

    test_id = _required_str(data, "test_id", location)
    category = _required_str(data, "category", location)
    variant = _optional_str(data, "variant", location) or "baseline"
    prompt = _required_str(data, "prompt", location)
    system_prompt = _optional_str(data, "system_prompt", location)
    if system_prompt is None:
        system_prompt = _optional_str(data, "system", location)
    context = _optional_context(data, location)
    examples = _optional_examples(data, location)
    generation_options = _optional_dict(data, "generation_options", location)
    if "generation_options" not in data:
        generation_options = _optional_dict(data, "options", location)
    expected = _optional_dict_or_none(data, "expected", location)
    tags = _optional_str_list(data, "tags", location)
    difficulty = _optional_str(data, "difficulty", location)

    return BenchmarkCase(
        test_id=test_id,
        category=category,
        variant=variant,
        prompt=prompt,
        system_prompt=system_prompt,
        context=context,
        examples=examples,
        generation_options=generation_options,
        expected=expected,
        tags=tags,
        difficulty=difficulty,
    )


def _required_str(data: dict[str, Any], field: str, location: str) -> str:
    value = data.get(field)
    if not isinstance(value, str) or not value:
        raise BenchmarkCaseError(
            f"Benchmark case{location} missing required string field {field}"
        )
    return value


def _optional_str(data: dict[str, Any], field: str, location: str) -> str | None:
    value = data.get(field)
    if value is None:
        return None
    if not isinstance(value, str):
        raise BenchmarkCaseError(f"Benchmark case{location} field {field} must be a string")
    return value


def _optional_dict(data: dict[str, Any], field: str, location: str) -> dict[str, Any]:
    value = data.get(field, {})
    if not isinstance(value, dict):
        raise BenchmarkCaseError(f"Benchmark case{location} field {field} must be an object")
    return value


def _optional_dict_or_none(
    data: dict[str, Any],
    field: str,
    location: str,
) -> dict[str, Any] | None:
    value = data.get(field)
    if value is None:
        return None
    if not isinstance(value, dict):
        raise BenchmarkCaseError(f"Benchmark case{location} field {field} must be an object")
    return value


def _optional_str_list(data: dict[str, Any], field: str, location: str) -> list[str]:
    value = data.get(field, [])
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise BenchmarkCaseError(
            f"Benchmark case{location} field {field} must be a list of strings"
        )
    return value


def _optional_context(data: dict[str, Any], location: str) -> list[ContextItem]:
    value = data.get("context", [])
    if not isinstance(value, list):
        raise BenchmarkCaseError(f"Benchmark case{location} field context must be a list")

    context: list[ContextItem] = []
    for index, item in enumerate(value, start=1):
        if not isinstance(item, dict):
            raise BenchmarkCaseError(
                f"Benchmark case{location} context item {index} must be an object"
            )
        text = item.get("text")
        if not isinstance(text, str) or not text:
            raise BenchmarkCaseError(
                f"Benchmark case{location} context item {index} missing text"
            )
        source_id = _optional_item_str(item, "source_id", "context", index, location)
        chunk_id = _optional_item_str(item, "chunk_id", "context", index, location)
        context.append(ContextItem(text=text, source_id=source_id, chunk_id=chunk_id))

    return context


def _optional_examples(data: dict[str, Any], location: str) -> list[Example]:
    value = data.get("examples", [])
    if not isinstance(value, list):
        raise BenchmarkCaseError(f"Benchmark case{location} field examples must be a list")

    examples: list[Example] = []
    for index, item in enumerate(value, start=1):
        if not isinstance(item, dict):
            raise BenchmarkCaseError(
                f"Benchmark case{location} example {index} must be an object"
            )
        prompt = item.get("prompt")
        response = item.get("response")
        if not isinstance(prompt, str) or not prompt:
            raise BenchmarkCaseError(
                f"Benchmark case{location} example {index} missing prompt"
            )
        if not isinstance(response, str) or not response:
            raise BenchmarkCaseError(
                f"Benchmark case{location} example {index} missing response"
            )
        examples.append(Example(prompt=prompt, response=response))

    return examples


def _optional_item_str(
    item: dict[str, Any],
    field: str,
    item_type: str,
    index: int,
    location: str,
) -> str | None:
    value = item.get(field)
    if value is None:
        return None
    if not isinstance(value, str):
        raise BenchmarkCaseError(
            f"Benchmark case{location} {item_type} item {index} field {field} must be a string"
        )
    return value
