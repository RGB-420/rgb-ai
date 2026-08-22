from __future__ import annotations

from dataclasses import asdict
from datetime import UTC, datetime
from typing import Protocol
from uuid import uuid4

from rgb_ai.cases import BenchmarkCase
from rgb_ai.evaluator import EvaluationResult, evaluate_output
from rgb_ai.models import ModelRegistryEntry
from rgb_ai.ollama import GenerateResponse, OllamaError
from rgb_ai.prompting import build_execution_request
from rgb_ai.results import (
    BenchmarkError,
    BenchmarkResult,
    JsonlResultStore,
    ResultStorageError,
    SCHEMA_VERSION,
    estimate_output_token_split,
)


class BenchmarkRunnerError(Exception):
    """Base class for benchmark runner errors."""


class ModelNotRunnableError(BenchmarkRunnerError):
    """Raised when a registry model is unavailable for benchmark execution."""


class OllamaLikeClient(Protocol):
    def generate(
        self,
        *,
        model: str,
        prompt: str,
        system: str | None = None,
        options: dict | None = None,
    ) -> GenerateResponse:
        ...


def new_run_id() -> str:
    return f"run_{uuid4().hex}"


def new_result_id() -> str:
    return f"res_{uuid4().hex}"


def run_benchmark_case(
    *,
    model: ModelRegistryEntry,
    case: BenchmarkCase,
    client: OllamaLikeClient,
    result_store: JsonlResultStore,
    run_id: str | None = None,
) -> BenchmarkResult:
    if not model.enabled:
        raise ModelNotRunnableError(f"Model is disabled: {model.model_id}")
    if not model.benchmark_eligible:
        raise ModelNotRunnableError(f"Model is not benchmark eligible: {model.model_id}")

    effective_run_id = run_id or new_run_id()
    request = build_execution_request(case)
    result_id = new_result_id()
    timestamp = _utc_timestamp()

    try:
        response = client.generate(
            model=model.provider_model,
            prompt=request.prompt,
            system=request.system_prompt,
            options=request.generation_options or None,
        )
    except OllamaError as exc:
        result = _build_result(
            result_id=result_id,
            run_id=effective_run_id,
            timestamp=timestamp,
            model=model,
            case=case,
            formatted_prompt=request.prompt,
            response=None,
            evaluation=_evaluation_error("infrastructure_error", str(exc)),
            error=BenchmarkError(type=type(exc).__name__, message=str(exc)),
        )
        result_store.append(result)
        return result

    evaluation = evaluate_output(response.response_text, case.expected)
    result = _build_result(
        result_id=result_id,
        run_id=effective_run_id,
        timestamp=timestamp,
        model=model,
        case=case,
        formatted_prompt=request.prompt,
        response=response,
        evaluation=evaluation,
        error=None,
    )
    result_store.append(result)
    return result


def _build_result(
    *,
    result_id: str,
    run_id: str,
    timestamp: str,
    model: ModelRegistryEntry,
    case: BenchmarkCase,
    formatted_prompt: str,
    response: GenerateResponse | None,
    evaluation: EvaluationResult,
    error: BenchmarkError | None,
) -> BenchmarkResult:
    return BenchmarkResult(
        schema_version=SCHEMA_VERSION,
        result_id=result_id,
        run_id=run_id,
        timestamp=timestamp,
        test_id=case.test_id,
        category=case.category,
        variant=case.variant,
        model_id=model.model_id,
        provider=model.provider,
        provider_model=model.provider_model,
        prompt=case.prompt,
        formatted_prompt=formatted_prompt,
        system_prompt=case.system_prompt,
        context=[asdict(item) for item in case.context],
        examples=[asdict(item) for item in case.examples],
        generation_options=dict(case.generation_options),
        response_text=response.response_text if response is not None else None,
        thinking_text=_thinking_text(response),
        raw_provider_response=response.raw_response if response is not None else None,
        metrics=asdict(response.metrics) if response is not None else {},
        estimated_token_split=estimate_output_token_split(
            thinking_text=_thinking_text(response),
            response_text=response.response_text if response is not None else None,
            output_tokens=response.metrics.output_tokens if response is not None else None,
        ),
        evaluation={
            "status": evaluation.status,
            "score": evaluation.score,
            "details": evaluation.details,
        },
        error=asdict(error) if error is not None else None,
    )


def _evaluation_error(error_type: str, message: str) -> EvaluationResult:
    return EvaluationResult(
        status="evaluation_error",
        passed=None,
        score=None,
        original_output="",
        details={"error_type": error_type, "message": message},
    )


def _utc_timestamp() -> str:
    return datetime.now(UTC).isoformat()


def _thinking_text(response: GenerateResponse | None) -> str | None:
    if response is None:
        return None
    thinking = response.raw_response.get("thinking")
    if isinstance(thinking, str):
        return thinking
    return None
