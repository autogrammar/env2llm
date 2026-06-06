"""DOQL-flavored LESS output (primary LLM context format)."""

from __future__ import annotations

from env2llm.doql import DoqlTaskContext
from env2llm.ir import SystemMapIR
from env2llm.render.doql import render_system_map_doql


def render_doql_less(ir: SystemMapIR, _ctx: DoqlTaskContext | None = None) -> str:
    return render_system_map_doql(ir)
