from rgb_ai.cases import parse_benchmark_case
from rgb_ai.prompting import PROMPT_FORMAT_VERSION, build_execution_request


def test_build_execution_request_for_baseline_prompt() -> None:
    case = parse_benchmark_case(
        {"test_id": "A", "category": "x", "prompt": "Say SI"}
    )

    request = build_execution_request(case)

    assert request.prompt == "TASK:\nSay SI"
    assert request.system_prompt is None
    assert request.generation_options == {}
    assert request.prompt_format_version == PROMPT_FORMAT_VERSION


def test_build_execution_request_keeps_system_prompt_separate() -> None:
    case = parse_benchmark_case(
        {
            "test_id": "A",
            "category": "x",
            "system_prompt": "Answer briefly.",
            "prompt": "Say SI",
        }
    )

    request = build_execution_request(case)

    assert request.system_prompt == "Answer briefly."
    assert "Answer briefly." not in request.prompt


def test_build_execution_request_formats_context_deterministically() -> None:
    case = parse_benchmark_case(
        {
            "test_id": "A",
            "category": "x",
            "prompt": "Where?",
            "context": [
                {
                    "text": "Marcelo Pepinillo nació en Terrassa.",
                    "source_id": "source_1",
                    "chunk_id": "chunk_1",
                }
            ],
        }
    )

    request = build_execution_request(case)

    assert request.prompt == (
        "CONTEXT:\n"
        "[Context 1; source=source_1; chunk=chunk_1]\n"
        "Marcelo Pepinillo nació en Terrassa.\n\n"
        "TASK:\n"
        "Where?"
    )


def test_build_execution_request_formats_examples_before_context() -> None:
    case = parse_benchmark_case(
        {
            "test_id": "A",
            "category": "x",
            "prompt": "Question",
            "examples": [{"prompt": "Example input", "response": "Example output"}],
            "context": [{"text": "Fact"}],
            "generation_options": {"temperature": 0},
        }
    )

    request = build_execution_request(case)

    assert request.prompt == (
        "EXAMPLES:\n"
        "[Example 1]\n"
        "Input: Example input\n"
        "Output: Example output\n\n"
        "CONTEXT:\n"
        "[Context 1]\n"
        "Fact\n\n"
        "TASK:\n"
        "Question"
    )
    assert request.generation_options == {"temperature": 0}
