"""Tests for TestQL catalog probe."""

from __future__ import annotations

from env2llm.ir import SystemMapIR
from env2llm.policy.testql import apply_testql_probe


def test_apply_testql_probe_adds_commands_when_testql_installed(tmp_path) -> None:
    try:
        import testql  # noqa: F401
    except ImportError:
        return

    scenario = tmp_path / "demo.testql.toon.yaml"
    scenario.write_text("# TYPE: gui\nNAVIGATE[1]{path, wait_ms}:\n  /, 100\n", encoding="utf-8")

    ir = SystemMapIR(example_id="demo")
    apply_testql_probe(ir, enabled=True, project_dir=tmp_path)

    assert ir.runtime("probe:testql") is not None
    assert ir.command("testql_run_scenario") is not None
    assert ir.command("testql_gui_click") is not None
    assert ir.command("testql_desktop_list") is not None
    assert ir.data.get("testql.scenario_count", 0) >= 1
