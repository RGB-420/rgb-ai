from __future__ import annotations

from dataclasses import dataclass

from rgb_ai.cases import BenchmarkCase

PROMPT_FORMAT_VERSION = "simple_context_v1"


@dataclass(frozen=True)
class ExecutionRequest:
    prompt: str
    system_prompt: str | None
    generation_options: dict[str, object]
    prompt_format_version: str


def build_execution_request(case: BenchmarkCase) -> ExecutionRequest:
    sections: list[str] = []

    if case.examples:
        sections.append(_format_examples(case))

    if case.context:
        sections.append(_format_context(case))

    sections.append(f"TASK:\n{case.prompt}")

    return ExecutionRequest(
        prompt="\n\n".join(sections),
        system_prompt=case.system_prompt,
        generation_options=dict(case.generation_options),
        prompt_format_version=PROMPT_FORMAT_VERSION,
    )


def _format_examples(case: BenchmarkCase) -> str:
    lines = ["EXAMPLES:"]
    for index, example in enumerate(case.examples, start=1):
        lines.extend(
            [
                f"[Example {index}]",
                f"Input: {example.prompt}",
                f"Output: {example.response}",
            ]
        )
    return "\n".join(lines)


def _format_context(case: BenchmarkCase) -> str:
    lines = ["CONTEXT:"]
    for index, item in enumerate(case.context, start=1):
        label_parts = [f"Context {index}"]
        if item.source_id is not None:
            label_parts.append(f"source={item.source_id}")
        if item.chunk_id is not None:
            label_parts.append(f"chunk={item.chunk_id}")
        lines.append(f"[{'; '.join(label_parts)}]")
        lines.append(item.text)
    return "\n".join(lines)
