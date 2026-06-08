"""LLM backend abstraction for env2llm.

Isolates litellm behind an injectable LLMComplete Protocol so generate.py
is not coupled to litellm at module load time.
"""

from __future__ import annotations

import os
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class LLMComplete(Protocol):
    """Single-turn system+user completion returning the assistant string."""

    def __call__(self, system: str, user: str) -> str:
        ...


class LitellmComplete:
    """Default implementation: litellm.completion with env-driven model."""

    def __call__(self, system: str, user: str) -> str:
        import litellm  # type: ignore

        model = os.getenv("LLM_MODEL", "openrouter/openai/gpt-5-mini")
        kwargs: dict[str, Any] = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": float(os.getenv("LLM_TEMPERATURE", "0")),
            "max_tokens": int(os.getenv("LLM_MAX_TOKENS", "4096")),
        }
        api_base = os.getenv("LLM_API_BASE")
        if api_base:
            kwargs["api_base"] = api_base
        response = litellm.completion(**kwargs)
        return str(response.choices[0].message.content or "")


def get_complete(complete: LLMComplete | None = None) -> LLMComplete:
    """Return provided callable or a LitellmComplete instance."""
    if complete is not None:
        return complete
    return LitellmComplete()


__all__ = ["LLMComplete", "LitellmComplete", "get_complete"]
