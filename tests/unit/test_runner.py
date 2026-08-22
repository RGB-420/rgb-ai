import pytest

from rgb_ai.cases import parse_benchmark_case
from rgb_ai.models import ModelRegistryEntry
from rgb_ai.ollama import OllamaConnectionError
from rgb_ai.results import JsonlResultStore, ResultStorageError, load_jsonl_results
from rgb_ai.runner import ModelNotRunnableError, run_benchmark_case

try:
    from helpers import make_generate_response
except ImportError:  # pragma: no cover
    from tests.unit.helpers import make_generate_response


class FakeClient:
    def __init__(
        self,
        response_text: str = "SI",
        error: Exception | None = None,
        thinking_text: str | None = None,
        output_tokens: int | None = 5,
    ) -> None:
        self.response_text = response_text
        self.error = error
        self.thinking_text = thinking_text
        self.output_tokens = output_tokens
        self.calls = []

    def generate(self, **kwargs):
        self.calls.append(kwargs)
        if self.error is not None:
            raise self.error
        return make_generate_response(
            self.response_text,
            thinking_text=self.thinking_text,
            output_tokens=self.output_tokens,
        )


def _model(**overrides) -> ModelRegistryEntry:
    values = {
        "model_id": "mdl_qwen3_06b",
        "provider": "ollama",
        "provider_model": "qwen3:0.6b",
        "role": "small_generalist_candidate",
        "notes": "",
        "enabled": True,
        "benchmark_eligible": True,
    }
    values.update(overrides)
    return ModelRegistryEntry(**values)


def _store(tmp_path) -> JsonlResultStore:
    return JsonlResultStore(tmp_path / "results.jsonl")


def test_run_benchmark_case_successful_exact_match(tmp_path) -> None:
    case = parse_benchmark_case(
        {
            "test_id": "EXACT_001",
            "category": "instruction",
            "prompt": "Say SI",
            "expected": {"type": "exact_match", "value": "SI"},
        }
    )
    client = FakeClient("SI")

    result = run_benchmark_case(
        model=_model(),
        case=case,
        client=client,
        result_store=_store(tmp_path),
        run_id="run_test",
    )

    assert result.evaluation["status"] == "passed"
    assert result.run_id == "run_test"
    assert result.response_text == "SI"
    assert result.thinking_text is None
    assert result.raw_provider_response == {"model": "qwen3:0.6b", "response": "SI", "done": True}
    assert result.metrics["total_duration_ms"] == 1000.0
    assert result.metrics["output_tokens"] == 5
    assert result.estimated_token_split["estimated_response_tokens"] == 5
    assert load_jsonl_results(tmp_path / "results.jsonl")[0]["result_id"] == result.result_id
    assert client.calls[0]["model"] == "qwen3:0.6b"
    assert client.calls[0]["prompt"] == "TASK:\nSay SI"


def test_run_benchmark_case_failed_evaluator_is_model_result(tmp_path) -> None:
    case = parse_benchmark_case(
        {
            "test_id": "EXACT_001",
            "category": "instruction",
            "prompt": "Say SI",
            "expected": {"type": "exact_match", "value": "SI"},
        }
    )

    result = run_benchmark_case(
        model=_model(),
        case=case,
        client=FakeClient("NO"),
        result_store=_store(tmp_path),
    )

    assert result.evaluation["status"] == "failed"
    assert result.error is None


def test_run_benchmark_case_open_ended_case_is_not_evaluated(tmp_path) -> None:
    case = parse_benchmark_case(
        {"test_id": "OPEN_001", "category": "open", "prompt": "Explain"}
    )

    result = run_benchmark_case(
        model=_model(),
        case=case,
        client=FakeClient("An answer"),
        result_store=_store(tmp_path),
    )

    assert result.evaluation["status"] == "not_evaluated"


def test_run_benchmark_case_rejects_disabled_or_ineligible_model(tmp_path) -> None:
    case = parse_benchmark_case(
        {"test_id": "OPEN_001", "category": "open", "prompt": "Explain"}
    )

    with pytest.raises(ModelNotRunnableError, match="disabled"):
        run_benchmark_case(
            model=_model(enabled=False),
            case=case,
            client=FakeClient(),
            result_store=_store(tmp_path),
        )

    with pytest.raises(ModelNotRunnableError, match="not benchmark eligible"):
        run_benchmark_case(
            model=_model(benchmark_eligible=False),
            case=case,
            client=FakeClient(),
            result_store=_store(tmp_path),
        )


def test_run_benchmark_case_records_ollama_infrastructure_failure(tmp_path) -> None:
    case = parse_benchmark_case(
        {"test_id": "OPEN_001", "category": "open", "prompt": "Explain"}
    )

    result = run_benchmark_case(
        model=_model(),
        case=case,
        client=FakeClient(error=OllamaConnectionError("network down")),
        result_store=_store(tmp_path),
    )

    assert result.evaluation["status"] == "not_evaluated"
    assert result.error == {
        "type": "OllamaConnectionError",
        "message": "network down",
    }
    assert load_jsonl_results(tmp_path / "results.jsonl")[0]["error"]["type"] == "OllamaConnectionError"


def test_run_benchmark_case_records_evaluation_error(tmp_path) -> None:
    case = parse_benchmark_case(
        {
            "test_id": "BAD_EVAL_001",
            "category": "instruction",
            "prompt": "Say SI",
            "expected": {"type": "unknown"},
        }
    )

    result = run_benchmark_case(
        model=_model(),
        case=case,
        client=FakeClient("SI"),
        result_store=_store(tmp_path),
    )

    assert result.evaluation["status"] == "evaluation_error"
    assert result.error is None


def test_run_benchmark_case_preserves_execution_context(tmp_path) -> None:
    case = parse_benchmark_case(
        {
            "test_id": "CTX_001",
            "category": "context_use",
            "variant": "context",
            "system_prompt": "Use context.",
            "context": [{"text": "Fact", "source_id": "src", "chunk_id": "c1"}],
            "examples": [{"prompt": "Q", "response": "A"}],
            "prompt": "Question",
            "generation_options": {"temperature": 0},
        }
    )
    client = FakeClient("Answer")

    result = run_benchmark_case(
        model=_model(),
        case=case,
        client=client,
        result_store=_store(tmp_path),
    )

    assert result.variant == "context"
    assert result.system_prompt == "Use context."
    assert result.context == [{"text": "Fact", "source_id": "src", "chunk_id": "c1"}]
    assert result.examples == [{"prompt": "Q", "response": "A"}]
    assert result.generation_options == {"temperature": 0}
    assert client.calls[0]["system"] == "Use context."
    assert client.calls[0]["options"] == {"temperature": 0}
    assert "CONTEXT:" in client.calls[0]["prompt"]


def test_run_benchmark_case_preserves_thinking_and_estimated_split(tmp_path) -> None:
    case = parse_benchmark_case(
        {"test_id": "OPEN_001", "category": "open", "prompt": "Explain"}
    )

    result = run_benchmark_case(
        model=_model(),
        case=case,
        client=FakeClient(
            response_text="Terrassa",
            thinking_text="Estoy revisando Nébula Azul.",
            output_tokens=20,
        ),
        result_store=_store(tmp_path),
    )

    assert result.thinking_text == "Estoy revisando Nébula Azul."
    assert result.metrics["output_tokens"] == 20
    assert result.estimated_token_split["method"] == "character_ratio_v1"
    assert result.estimated_token_split["authoritative"] is False
    assert result.estimated_token_split["thinking_characters"] == len(
        "Estoy revisando Nébula Azul."
    )
    assert (
        result.estimated_token_split["estimated_thinking_tokens"]
        + result.estimated_token_split["estimated_response_tokens"]
        == 20
    )


def test_run_benchmark_case_propagates_result_storage_failure(tmp_path) -> None:
    case = parse_benchmark_case(
        {"test_id": "OPEN_001", "category": "open", "prompt": "Explain"}
    )
    bad_store = JsonlResultStore(tmp_path)

    with pytest.raises(ResultStorageError):
        run_benchmark_case(
            model=_model(),
            case=case,
            client=FakeClient("answer"),
            result_store=bad_store,
        )
