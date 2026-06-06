"""Collect and mask process environment variables for LLM context."""

from __future__ import annotations

import os
from datetime import UTC, datetime
from typing import Mapping

DEFAULT_ENV_KEYS: tuple[str, ...] = (
    "NLP2DSL_BACKEND_URL",
    "NLP2DSL_NLP_SERVICE_URL",
    "NLP2DSL_WORKER_URL",
    "NLP2DSL_TIMEOUT",
    "NLP_ENRICH_MISSING",
    "NLP2DSL_UTF8",
    "NLP_CHAT_MODE",
    "LLM_MODEL",
    "OPENROUTER_API_KEY",
    "LLM_API_BASE",
    "LLM_TEMPERATURE",
    "LLM_MAX_TOKENS",
    "NLP2CMD_INTEGRATION",
    "NLP2CMD_INTRACT_GATE",
    "ENV2LLM_PROJECT_DIR",
)


def mask_secret(value: str) -> str:
    if not value or len(value) < 8:
        return "***"
    return f"{value[:4]}…{value[-4:]}"


def collect_environment(
    *,
    extra_keys: tuple[str, ...] = (),
    include_all_prefixes: tuple[str, ...] = ("NLP2DSL_", "LLM_", "OPENROUTER_", "ENV2LLM_"),
) -> dict[str, str]:
    """Snapshot relevant env vars (secrets masked) for environment blocks."""
    keys = tuple(dict.fromkeys((*DEFAULT_ENV_KEYS, *extra_keys)))
    out: dict[str, str] = {}
    for key in keys:
        raw = os.environ.get(key)
        if raw is None:
            continue
        if any(token in key for token in ("KEY", "SECRET", "TOKEN", "PASSWORD")):
            out[key] = mask_secret(raw)
        else:
            out[key] = raw

    if include_all_prefixes:
        for key, raw in sorted(os.environ.items()):
            if key in out or raw is None:
                continue
            if not any(key.startswith(prefix) for prefix in include_all_prefixes):
                continue
            if any(token in key for token in ("KEY", "SECRET", "TOKEN", "PASSWORD")):
                out[key] = mask_secret(raw)
            else:
                out[key] = raw

    out["generated_at"] = datetime.now(UTC).isoformat()
    return out


def merge_environment(
    base: Mapping[str, str] | None,
    override: Mapping[str, str] | None,
) -> dict[str, str]:
    merged = dict(base or {})
    merged.update(dict(override or {}))
    return merged
