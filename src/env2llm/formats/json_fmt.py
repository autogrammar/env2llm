"""JSON serialization of SystemMapIR."""

from __future__ import annotations

import json

from env2llm.doql import DoqlTaskContext
from env2llm.ir import SystemMapIR


def render_json(ir: SystemMapIR, _ctx: DoqlTaskContext | None = None) -> str:
    payload = ir.model_dump(mode="json", exclude_none=True)
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
