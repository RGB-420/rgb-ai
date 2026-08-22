from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rgb_ai.ollama import OllamaModel


class ModelRegistryError(ValueError):
    """Raised when model registry data is invalid."""


@dataclass(frozen=True)
class ModelRegistryEntry:
    model_id: str
    provider: str
    provider_model: str
    role: str
    notes: str
    enabled: bool
    benchmark_eligible: bool


@dataclass(frozen=True)
class ModelDiscoveryStatus:
    model_id: str
    provider_model: str
    installed: bool
    provider_metadata: OllamaModel | None


def load_model_registry(path: str | Path) -> list[ModelRegistryEntry]:
    registry_path = Path(path)
    try:
        data = json.loads(registry_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ModelRegistryError(
            f"Invalid model registry JSON at {registry_path}: {exc.msg}"
        ) from exc

    return parse_model_registry(data)


def parse_model_registry(data: Any) -> list[ModelRegistryEntry]:
    if not isinstance(data, dict):
        raise ModelRegistryError("Model registry must be a JSON object")

    raw_models = data.get("models")
    if not isinstance(raw_models, list):
        raise ModelRegistryError("Model registry must contain a models list")

    entries: list[ModelRegistryEntry] = []
    seen_ids: set[str] = set()
    for index, raw_entry in enumerate(raw_models, start=1):
        if not isinstance(raw_entry, dict):
            raise ModelRegistryError(f"Model registry entry {index} must be an object")

        entry = _parse_registry_entry(raw_entry, index)
        if entry.model_id in seen_ids:
            raise ModelRegistryError(f"Duplicate model_id in registry: {entry.model_id}")
        seen_ids.add(entry.model_id)
        entries.append(entry)

    return entries


def validate_registry_against_ollama(
    registry: list[ModelRegistryEntry],
    discovered_models: list[OllamaModel],
) -> list[ModelDiscoveryStatus]:
    discovered_by_name = {model.name: model for model in discovered_models}
    return [
        ModelDiscoveryStatus(
            model_id=entry.model_id,
            provider_model=entry.provider_model,
            installed=entry.provider_model in discovered_by_name,
            provider_metadata=discovered_by_name.get(entry.provider_model),
        )
        for entry in registry
    ]


def _parse_registry_entry(raw_entry: dict[str, Any], index: int) -> ModelRegistryEntry:
    return ModelRegistryEntry(
        model_id=_required_str(raw_entry, "model_id", index),
        provider=_required_str(raw_entry, "provider", index),
        provider_model=_required_str(raw_entry, "provider_model", index),
        role=_required_str(raw_entry, "role", index),
        notes=_optional_str(raw_entry, "notes", index, default=""),
        enabled=_optional_bool(raw_entry, "enabled", index, default=True),
        benchmark_eligible=_optional_bool(
            raw_entry,
            "benchmark_eligible",
            index,
            default=True,
        ),
    )


def _required_str(raw_entry: dict[str, Any], field: str, index: int) -> str:
    value = raw_entry.get(field)
    if not isinstance(value, str) or not value:
        raise ModelRegistryError(
            f"Model registry entry {index} missing required string field {field}"
        )
    return value


def _optional_str(
    raw_entry: dict[str, Any],
    field: str,
    index: int,
    *,
    default: str,
) -> str:
    value = raw_entry.get(field, default)
    if not isinstance(value, str):
        raise ModelRegistryError(
            f"Model registry entry {index} field {field} must be a string"
        )
    return value


def _optional_bool(
    raw_entry: dict[str, Any],
    field: str,
    index: int,
    *,
    default: bool,
) -> bool:
    value = raw_entry.get(field, default)
    if not isinstance(value, bool):
        raise ModelRegistryError(
            f"Model registry entry {index} field {field} must be a boolean"
        )
    return value
