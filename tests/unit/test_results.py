import json

import pytest

from rgb_ai.results import (
    BenchmarkResult,
    JsonlResultStore,
    ResultStorageError,
    estimate_output_token_split,
    load_jsonl_results,
)


def _result(result_id: str, response_text: str = "integración funcionando"):
    return BenchmarkResult(
        schema_version=1,
        result_id=result_id,
        run_id="run_1",
        timestamp="2026-08-22T00:00:00+00:00",
        test_id="TEST_001",
        category="instruction",
        variant="baseline",
        model_id="mdl_qwen3_06b",
        provider="ollama",
        provider_model="qwen3:0.6b",
        prompt="¿Qué día tendrá la revisión final?",
        formatted_prompt="TASK:\n¿Qué día tendrá la revisión final?",
        system_prompt="Responde sobre Nébula Azul.",
        context=[
            {
                "text": "Nébula Azul tendrá revisión en Terrassa.",
                "source_id": "src",
                "chunk_id": "c1",
            }
        ],
        examples=[],
        generation_options={},
        response_text=response_text,
        thinking_text="pensando en Nébula Azul",
        raw_provider_response={"response": response_text},
        metrics={"total_duration_ms": 1.0},
        estimated_token_split={"method": "character_ratio_v1", "available": True},
        evaluation={"status": "passed", "score": 1.0, "details": {}},
        error=None,
    )


def test_jsonl_result_store_appends_and_preserves_unicode(tmp_path) -> None:
    path = tmp_path / "nested" / "results.jsonl"
    store = JsonlResultStore(path)

    store.append(_result("res_1"))

    rows = load_jsonl_results(path)
    assert rows[0]["response_text"] == "integración funcionando"
    assert rows[0]["thinking_text"] == "pensando en Nébula Azul"
    assert rows[0]["prompt"] == "¿Qué día tendrá la revisión final?"
    assert rows[0]["system_prompt"] == "Responde sobre Nébula Azul."
    assert rows[0]["context"][0]["text"] == "Nébula Azul tendrá revisión en Terrassa."
    assert "integración funcionando" in path.read_text(encoding="utf-8")
    assert "¿Qué día tendrá la revisión final?" in path.read_text(encoding="utf-8")
    assert "Nébula Azul tendrá revisión en Terrassa." in path.read_text(encoding="utf-8")
    assert path.parent.exists()


def test_jsonl_result_store_does_not_overwrite_existing_results(tmp_path) -> None:
    path = tmp_path / "results.jsonl"
    store = JsonlResultStore(path)

    store.append(_result("res_1", "uno"))
    store.append(_result("res_2", "dos"))

    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    assert [row["result_id"] for row in rows] == ["res_1", "res_2"]
    assert [row["response_text"] for row in rows] == ["uno", "dos"]


def test_jsonl_result_store_reports_write_failure(tmp_path) -> None:
    directory_path = tmp_path / "as_directory"
    directory_path.mkdir()
    store = JsonlResultStore(directory_path)

    with pytest.raises(ResultStorageError, match="Unable to append"):
        store.append(_result("res_1"))


def test_estimated_split_for_thinking_and_response() -> None:
    split = estimate_output_token_split(
        thinking_text="aaaaaa",
        response_text="bb",
        output_tokens=80,
    )

    assert split["method"] == "character_ratio_v1"
    assert split["authoritative"] is False
    assert split["thinking_characters"] == 6
    assert split["response_characters"] == 2
    assert split["thinking_share"] == 0.75
    assert split["response_share"] == 0.25
    assert split["estimated_thinking_tokens"] == 60
    assert split["estimated_response_tokens"] == 20
    assert (
        split["estimated_thinking_tokens"] + split["estimated_response_tokens"]
        == 80
    )


def test_estimated_split_for_response_only() -> None:
    split = estimate_output_token_split(
        thinking_text=None,
        response_text="Terrassa",
        output_tokens=7,
    )

    assert split["thinking_share"] == 0
    assert split["response_share"] == 1
    assert split["estimated_thinking_tokens"] == 0
    assert split["estimated_response_tokens"] == 7


def test_estimated_split_for_thinking_only() -> None:
    split = estimate_output_token_split(
        thinking_text="razonamiento",
        response_text="",
        output_tokens=9,
    )

    assert split["thinking_share"] == 1
    assert split["response_share"] == 0
    assert split["estimated_thinking_tokens"] == 9
    assert split["estimated_response_tokens"] == 0


def test_estimated_split_for_empty_texts_is_unavailable() -> None:
    split = estimate_output_token_split(
        thinking_text="",
        response_text="",
        output_tokens=9,
    )

    assert split["available"] is False
    assert split["reason"] == "empty_texts"
    assert split["estimated_thinking_tokens"] is None
    assert split["estimated_response_tokens"] is None


def test_estimated_split_for_missing_output_tokens_is_unavailable() -> None:
    split = estimate_output_token_split(
        thinking_text="razonamiento",
        response_text="respuesta",
        output_tokens=None,
    )

    assert split["available"] is False
    assert split["reason"] == "missing_output_tokens"
    assert split["estimated_thinking_tokens"] is None
    assert split["estimated_response_tokens"] is None
