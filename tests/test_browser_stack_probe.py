from __future__ import annotations

from env2llm.ir import SystemMapIR
from env2llm.policy.browser_stack import apply_browser_stack_probe


def test_apply_browser_stack_probe_adds_router_commands() -> None:
    ir = SystemMapIR(project_id="demo")
    apply_browser_stack_probe(ir, enabled=True)

    names = {cmd.name for cmd in ir.commands}
    assert "nlp2oql_run" in names
    assert "browser_automation" in ir.capabilities
