"""Human-readable markdown summary for LLM decision-making."""

from __future__ import annotations

from env2llm.doql import DoqlTaskContext
from env2llm.formats.markdown_sections import (
    append_section,
    generated_at_line,
    render_artifacts_section,
    render_capabilities_section,
    render_commands_section,
    render_data_section,
    render_environment_section,
    render_runtimes_section,
)
from env2llm.ir import SystemMapIR


def render_markdown(ir: SystemMapIR, _ctx: DoqlTaskContext | None = None) -> str:
    lines: list[str] = [
        f"# Environment map — {ir.example_id}",
        "",
        f"- format: `{ir.format}`",
        generated_at_line(ir),
    ]

    append_section(lines, render_environment_section(ir))
    append_section(lines, render_runtimes_section(ir))
    append_section(lines, render_commands_section(ir))

    if ir.capabilities:
        append_section(lines, render_capabilities_section(ir))
    if ir.artifacts:
        append_section(lines, render_artifacts_section(ir))
    if ir.data:
        append_section(lines, render_data_section(ir))

    return "\n".join(lines) + "\n"
