"""Tests for MCP catalog probe (Koru tools)."""

from __future__ import annotations

from env2llm.ir import SystemMapIR
from env2llm.policy.mcp import apply_mcp_probe


def test_apply_mcp_probe_adds_koru_commands_when_available() -> None:
    try:
        from env2llm.probes.mcp import collect_koru_mcp_tools
    except ImportError:
        return

    tools = collect_koru_mcp_tools()
    if not tools:
        return

    ir = SystemMapIR(example_id="koru")
    apply_mcp_probe(ir, enabled=True, project_dir="/home/tom/github/semcod/koru")

    assert ir.runtime("mcp:koru") is not None
    assert ir.command("koru_list_tickets") is not None
    assert ir.command("koru_run_quality_gates") is not None
    assert ir.data.get("mcp.tool_count", 0) >= 10
