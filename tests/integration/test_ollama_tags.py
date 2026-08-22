import os

import pytest

from rgb_ai.config import load_config
from rgb_ai.ollama import OllamaClient


def _integration_enabled() -> bool:
    return os.environ.get("RGB_AI_RUN_INTEGRATION_TESTS", "").lower() in {
        "1",
        "true",
        "yes",
    }


@pytest.mark.integration
@pytest.mark.skipif(
    not _integration_enabled(),
    reason="Set RGB_AI_RUN_INTEGRATION_TESTS=1 to run Ollama integration tests",
)
def test_list_models_against_real_ollama_server() -> None:
    config = load_config()

    with OllamaClient(
        base_url=config.ollama_base_url,
        timeout_seconds=config.request_timeout_seconds,
    ) as client:
        models = client.list_models()

    assert isinstance(models, list)
