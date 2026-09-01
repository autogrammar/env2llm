"""Human-readable markdown summary for LLM decision-making."""

from __future__ import annotations

from env2llm.doql import DoqlTaskContext
from env2llm.ir import ArtifactSpecIR, CommandSchemaIR, RuntimeSpecIR, SystemMapIR


def _generated_at_line(ir: SystemMapIR) -> str:
    generated = getattr(ir, "generated_at", None) or ir.metadata.get("generated_at", "unknown")
    return f"- generated: {generated}"


def _render_environment_section(ir: SystemMapIR) -> list[str]:
    lines = ["## Environment", ""]
    for key, value in sorted((ir.environment or {}).items()):
        lines.append(f"- **{key}**: `{value}`")
    return lines


def _render_runtimes_section(ir: SystemMapIR) -> list[str]:
    lines = ["## Runtimes", ""]
    for runtime in ir.runtimes:
        lines.extend(_runtime_lines(runtime))
    return lines


def _runtime_lines(runtime: RuntimeSpecIR) -> list[str]:
    roles = ", ".join(runtime.roles or [])
    url = runtime.url or runtime.uri or ""
    lines = [f"- `{runtime.id}` ({runtime.kind}, {runtime.status}) — {url}"]
    if roles:
        lines.append(f"  - roles: {roles}")
    return lines


def _render_commands_section(ir: SystemMapIR) -> list[str]:
    lines = ["## Commands", ""]
    for cmd in ir.commands:
        lines.extend(_command_lines(cmd))
    return lines


def _command_lines(cmd: CommandSchemaIR) -> list[str]:
    required = ", ".join(field.name for field in cmd.fields if field.required)
    lines = [f"- `{cmd.name}` → runtime `{cmd.runtime or '?'}`"]
    if cmd.description:
        lines.append(f"  - {cmd.description}")
    if required:
        lines.append(f"  - required: {required}")
    return lines


def _render_capabilities_section(ir: SystemMapIR) -> list[str]:
    return ["## Capabilities", "", ", ".join(f"`{cap}`" for cap in ir.capabilities)]


def _render_artifacts_section(ir: SystemMapIR) -> list[str]:
    lines = ["## Artifacts", ""]
    for artifact in ir.artifacts:
        lines.append(_artifact_line(artifact))
    return lines


def _artifact_line(artifact: ArtifactSpecIR) -> str:
    return f"- `{artifact.path}` ({artifact.kind or 'file'})"


def _render_data_section(ir: SystemMapIR) -> list[str]:
    lines = ["## Data", ""]
    for key, value in sorted(ir.data.items()):
        lines.append(f"- `{key}`: {value!r}")
    return lines


def _append_section(lines: list[str], section: list[str]) -> None:
    lines.extend(["", *section])


def render_markdown(ir: SystemMapIR, _ctx: DoqlTaskContext | None = None) -> str:
    lines: list[str] = [
        f"# Environment map — {ir.example_id}",
        "",
        f"- format: `{ir.format}`",
        _generated_at_line(ir),
    ]

    _append_section(lines, _render_environment_section(ir))
    _append_section(lines, _render_runtimes_section(ir))
    _append_section(lines, _render_commands_section(ir))

    if ir.capabilities:
        _append_section(lines, _render_capabilities_section(ir))
    if ir.artifacts:
        _append_section(lines, _render_artifacts_section(ir))
    if ir.data:
        _append_section(lines, _render_data_section(ir))

    return "\n".join(lines) + "\n"
