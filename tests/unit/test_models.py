from pathlib import Path

import pytest

from rgb_ai.models import (
    ModelRegistryError,
    load_model_registry,
    parse_model_registry,
    validate_registry_against_ollama,
)
from rgb_ai.ollama import OllamaModel

REPO_ROOT = Path(__file__).resolve().parents[2]


def _registry_data():
    return {
        "models": [
            {
                "model_id": "mdl_qwen3_06b",
                "provider": "ollama",
                "provider_model": "qwen3:0.6b",
                "role": "small_generalist_candidate",
                "notes": "candidate",
                "enabled": True,
                "benchmark_eligible": True,
            }
        ]
    }


def test_load_model_registry_from_json_file(tmp_path) -> None:
    path = tmp_path / "models.json"
    path.write_text(
        """
        {
          "models": [
            {
              "model_id": "mdl_qwen3_06b",
              "provider": "ollama",
              "provider_model": "qwen3:0.6b",
              "role": "small_generalist_candidate"
            }
          ]
        }
        """,
        encoding="utf-8",
    )

    models = load_model_registry(path)

    assert len(models) == 1
    assert models[0].model_id == "mdl_qwen3_06b"
    assert models[0].provider_model == "qwen3:0.6b"
    assert models[0].enabled is True
    assert models[0].benchmark_eligible is True


def test_load_checked_in_model_registry_fixture() -> None:
    models = load_model_registry(REPO_ROOT / "configs" / "models.json")

    assert [model.model_id for model in models] == [
        "mdl_qwen3_06b",
        "mdl_qwen3_17b",
        "mdl_llama32_1b",
        "mdl_gemma3_1b",
        "mdl_qwen25_15b",
        "mdl_qwen25_coder_15b",
        "mdl_deepseek_r1_15b",
        "mdl_phi35_38b",
        "mdl_granite4_350m_h",
        "mdl_embeddinggemma_latest",
    ]
    assert [model.provider_model for model in models] == [
        "qwen3:0.6b",
        "qwen3:1.7b",
        "llama3.2:1b",
        "gemma3:1b",
        "qwen2.5:1.5b",
        "qwen2.5-coder:1.5b",
        "deepseek-r1:1.5b",
        "phi3.5:3.8b",
        "granite4:350m-h",
        "embeddinggemma:latest",
    ]
    assert [model.model_id for model in models if model.benchmark_eligible] == [
        "mdl_qwen3_06b",
        "mdl_qwen3_17b",
        "mdl_llama32_1b",
        "mdl_gemma3_1b",
        "mdl_qwen25_15b",
        "mdl_qwen25_coder_15b",
        "mdl_deepseek_r1_15b",
        "mdl_phi35_38b",
        "mdl_granite4_350m_h",
    ]
    assert [model.model_id for model in models if not model.benchmark_eligible] == [
        "mdl_embeddinggemma_latest"
    ]


def test_parse_model_registry_rejects_invalid_root() -> None:
    with pytest.raises(ModelRegistryError, match="JSON object"):
        parse_model_registry([])


def test_parse_model_registry_rejects_missing_models_list() -> None:
    with pytest.raises(ModelRegistryError, match="models list"):
        parse_model_registry({})


def test_parse_model_registry_rejects_duplicate_ids() -> None:
    data = _registry_data()
    data["models"].append(dict(data["models"][0]))

    with pytest.raises(ModelRegistryError, match="Duplicate model_id"):
        parse_model_registry(data)


def test_parse_model_registry_rejects_missing_required_field() -> None:
    data = _registry_data()
    del data["models"][0]["provider_model"]

    with pytest.raises(ModelRegistryError, match="provider_model"):
        parse_model_registry(data)


def test_parse_model_registry_rejects_invalid_enabled_type() -> None:
    data = _registry_data()
    data["models"][0]["enabled"] = "yes"

    with pytest.raises(ModelRegistryError, match="enabled"):
        parse_model_registry(data)


def test_validate_registry_against_ollama_reports_installed_and_missing() -> None:
    registry = parse_model_registry(
        {
            "models": [
                {
                    "model_id": "mdl_qwen3_06b",
                    "provider": "ollama",
                    "provider_model": "qwen3:0.6b",
                    "role": "small_generalist_candidate",
                },
                {
                    "model_id": "mdl_missing",
                    "provider": "ollama",
                    "provider_model": "missing:latest",
                    "role": "missing_candidate",
                },
            ]
        }
    )
    discovered = [
        OllamaModel(
            name="qwen3:0.6b",
            modified_at="2026-08-22T12:00:00Z",
            size_bytes=123,
            digest="abc",
            details={"family": "qwen3"},
        )
    ]

    statuses = validate_registry_against_ollama(registry, discovered)

    assert statuses[0].installed is True
    assert statuses[0].provider_metadata == discovered[0]
    assert statuses[1].installed is False
    assert statuses[1].provider_metadata is None
