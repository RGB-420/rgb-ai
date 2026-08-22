from rgb_ai.ollama import GenerateResponse, GenerationMetrics


def make_generate_response(response_text: str = "SI") -> GenerateResponse:
    return GenerateResponse(
        model="qwen3:0.6b",
        response_text=response_text,
        done=True,
        metrics=GenerationMetrics(
            total_duration_ms=1000.0,
            load_duration_ms=100.0,
            prompt_eval_duration_ms=50.0,
            eval_duration_ms=500.0,
            prompt_tokens=10,
            output_tokens=5,
            prompt_tokens_per_second=200.0,
            output_tokens_per_second=10.0,
        ),
        raw_response={
            "model": "qwen3:0.6b",
            "response": response_text,
            "done": True,
        },
    )
