"""YAML serialization of SystemMapIR for tooling and LLM context."""

from __future__ import annotations

import yaml

from env2llm.doql import DoqlTaskContext
from env2llm.ir import SystemMapIR


def render_yaml(ir: SystemMapIR, _ctx: DoqlTaskContext | None = None) -> str:
    payload = ir.model_dump(mode="json", exclude_none=True)
    return yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)
