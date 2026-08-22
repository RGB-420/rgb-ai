from pathlib import Path

import pytest

from rgb_ai.cases import (
    BenchmarkCaseError,
    load_benchmark_cases,
    parse_benchmark_case,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_load_benchmark_cases_from_jsonl(tmp_path) -> None:
    path = tmp_path / "cases.jsonl"
    path.write_text(
        '{"test_id":"A","category":"instruction","prompt":"Say SI",'
        '"expected":{"type":"exact_match","value":"SI"},"tags":["deterministic"],'
        '"difficulty":"trivial"}\n'
        '{"test_id":"B","category":"open","prompt":"Explain something"}\n',
        encoding="utf-8",
    )

    cases = load_benchmark_cases(path)

    assert len(cases) == 2
    assert cases[0].test_id == "A"
    assert cases[0].variant == "baseline"
    assert cases[0].expected == {"type": "exact_match", "value": "SI"}
    assert cases[0].tags == ["deterministic"]
    assert cases[1].expected is None
    assert cases[1].tags == []


def test_load_checked_in_benchmark_case_fixture() -> None:
    cases = load_benchmark_cases(REPO_ROOT / "benchmarks" / "cases.jsonl")

    assert [case.test_id for case in cases] == [
        "INSTRUCT_EXACT_001",
        "JSON_VALID_001",
        "ALLOWED_VALUE_001",
        "CONTEXT_FACT_001",
    ]
    assert [case.variant for case in cases] == [
        "baseline",
        "instructions",
        "baseline",
        "context",
    ]


def test_load_benchmark_cases_rejects_malformed_jsonl(tmp_path) -> None:
    path = tmp_path / "cases.jsonl"
    path.write_text('{"test_id":"A"\n', encoding="utf-8")

    with pytest.raises(BenchmarkCaseError, match="line 1"):
        load_benchmark_cases(path)


def test_load_benchmark_cases_rejects_duplicate_test_ids(tmp_path) -> None:
    path = tmp_path / "cases.jsonl"
    path.write_text(
        '{"test_id":"A","category":"x","prompt":"one"}\n'
        '{"test_id":"A","category":"x","prompt":"two"}\n',
        encoding="utf-8",
    )

    with pytest.raises(BenchmarkCaseError, match="Duplicate test_id"):
        load_benchmark_cases(path)


def test_parse_benchmark_case_rejects_missing_required_field() -> None:
    with pytest.raises(BenchmarkCaseError, match="prompt"):
        parse_benchmark_case({"test_id": "A", "category": "x"})


def test_parse_benchmark_case_rejects_invalid_options() -> None:
    with pytest.raises(BenchmarkCaseError, match="options"):
        parse_benchmark_case(
            {
                "test_id": "A",
                "category": "x",
                "prompt": "hello",
                "options": [],
            }
        )


def test_parse_benchmark_case_supports_execution_context_fields() -> None:
    case = parse_benchmark_case(
        {
            "test_id": "CTX_001",
            "category": "context_use",
            "variant": "few_shot",
            "system_prompt": "Use the supplied facts.",
            "context": [
                {
                    "text": "Marcelo Pepinillo nació en Terrassa.",
                    "source_id": "source_a",
                    "chunk_id": "chunk_1",
                }
            ],
            "examples": [
                {
                    "prompt": "¿Dónde nació Ana?",
                    "response": "Madrid",
                }
            ],
            "prompt": "¿Dónde nació Marcelo Pepinillo?",
            "generation_options": {"temperature": 0},
            "expected": {"type": "exact_match", "value": "Terrassa"},
        }
    )

    assert case.variant == "few_shot"
    assert case.system_prompt == "Use the supplied facts."
    assert case.context[0].text == "Marcelo Pepinillo nació en Terrassa."
    assert case.context[0].source_id == "source_a"
    assert case.context[0].chunk_id == "chunk_1"
    assert case.examples[0].prompt == "¿Dónde nació Ana?"
    assert case.examples[0].response == "Madrid"
    assert case.generation_options == {"temperature": 0}


def test_parse_benchmark_case_supports_legacy_system_and_options_aliases() -> None:
    case = parse_benchmark_case(
        {
            "test_id": "LEGACY_001",
            "category": "instruction",
            "system": "Old system field",
            "prompt": "hello",
            "options": {"temperature": 0},
        }
    )

    assert case.system_prompt == "Old system field"
    assert case.generation_options == {"temperature": 0}


def test_parse_benchmark_case_rejects_malformed_context_structures() -> None:
    with pytest.raises(BenchmarkCaseError, match="context"):
        parse_benchmark_case(
            {
                "test_id": "A",
                "category": "x",
                "prompt": "hello",
                "context": {"text": "not a list"},
            }
        )

    with pytest.raises(BenchmarkCaseError, match="missing text"):
        parse_benchmark_case(
            {
                "test_id": "A",
                "category": "x",
                "prompt": "hello",
                "context": [{"source_id": "source"}],
            }
        )


def test_parse_benchmark_case_rejects_malformed_examples() -> None:
    with pytest.raises(BenchmarkCaseError, match="examples"):
        parse_benchmark_case(
            {
                "test_id": "A",
                "category": "x",
                "prompt": "hello",
                "examples": {"prompt": "not a list"},
            }
        )

    with pytest.raises(BenchmarkCaseError, match="missing response"):
        parse_benchmark_case(
            {
                "test_id": "A",
                "category": "x",
                "prompt": "hello",
                "examples": [{"prompt": "question"}],
            }
        )


def test_parse_benchmark_case_rejects_invalid_generation_options() -> None:
    with pytest.raises(BenchmarkCaseError, match="generation_options"):
        parse_benchmark_case(
            {
                "test_id": "A",
                "category": "x",
                "prompt": "hello",
                "generation_options": [],
            }
        )


def test_parse_benchmark_case_rejects_non_string_tags() -> None:
    with pytest.raises(BenchmarkCaseError, match="tags"):
        parse_benchmark_case(
            {
                "test_id": "A",
                "category": "x",
                "prompt": "hello",
                "tags": ["ok", 1],
            }
        )
