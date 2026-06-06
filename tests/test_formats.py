"""Tests for multi-format environment map output."""

from __future__ import annotations

from env2llm.formats import render_format
from env2llm.ir import CommandSchemaIR, RuntimeSpecIR, SystemMapIR


def test_render_json_yaml_markdown() -> None:
    ir = SystemMapIR(
        example_id="demo",
        environment={"LLM_MODEL": "test/model"},
        runtimes=[RuntimeSpecIR(id="executor:worker", kind="worker", status="available")],
        commands=[CommandSchemaIR(name="send_email", runtime="executor:worker")],
        capabilities=["send_email"],  # type: ignore[arg-type]
    )
    json_text = render_format(ir, "json")
    assert '"example_id": "demo"' in json_text
    yaml_text = render_format(ir, "yaml")
    assert "example_id: demo" in yaml_text
    md_text = render_format(ir, "markdown")
    assert "# Environment map — demo" in md_text
    assert "send_email" in md_text
