from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from rgb_ai.cases import BenchmarkCase
from rgb_ai.evaluator import evaluate_output
from rgb_ai.results import write_jsonl_rows

EVALUATION_SCHEMA_VERSION = 2


class ReEvaluationError(ValueError):
    """Raised when stored results cannot be re-evaluated."""


def reevaluate_results(
    rows: list[dict[str, Any]],
    cases: list[BenchmarkCase],
    *,
    source_file: str | Path,
    output_path: str | Path,
) -> list[dict[str, Any]]:
    cases_by_id = {case.test_id: case for case in cases}
    reevaluated: list[dict[str, Any]] = []
    timestamp = datetime.now(UTC).isoformat()

    for row in rows:
        derived = dict(row)
        test_id = row.get("test_id")
        if not isinstance(test_id, str) or test_id not in cases_by_id:
            raise ReEvaluationError(f"No benchmark case found for stored test_id: {test_id}")

        derived["reevaluation"] = {
            "schema_version": EVALUATION_SCHEMA_VERSION,
            "source_file": Path(source_file).name,
            "reevaluated_at": timestamp,
        }

        response_text = row.get("response_text")
        if row.get("error") is not None or not isinstance(response_text, str):
            derived["evaluation"] = {
                "status": "not_evaluated",
                "score": None,
                "task_correct": None,
                "format_compliant": None,
                "failure_type": None,
                "details": {
                    "reason": "Stored result has infrastructure error or no usable response_text"
                },
            }
            reevaluated.append(derived)
            continue

        evaluation = evaluate_output(response_text, cases_by_id[test_id].expected)
        derived["evaluation"] = {
            "status": evaluation.status,
            "score": evaluation.score,
            "task_correct": evaluation.task_correct,
            "format_compliant": evaluation.format_compliant,
            "failure_type": evaluation.failure_type,
            "details": evaluation.details,
        }
        reevaluated.append(derived)

    write_jsonl_rows(output_path, reevaluated)
    return reevaluated
