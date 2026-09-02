"""Markdown section renderers for SystemMapIR."""

from __future__ import annotations

from env2llm.ir import ArtifactSpecIR, CommandSchemaIR, RuntimeSpecIR, SystemMapIR


def generated_at_line(ir: SystemMapIR) -> str:
    generated = getattr(ir, "generated_at", None) or ir.metadata.get("generated_at", "unknown")
    return f"- generated: {generated}"


def render_environment_section(ir: SystemMapIR) -> list[str]:
    lines = ["## Environment", ""]
    for key, value in sorted((ir.environment or {}).items()):
        lines.append(f"- **{key}**: `{value}`")
    return lines


def runtime_lines(runtime: RuntimeSpecIR) -> list[str]:
    roles = ", ".join(runtime.roles or [])
    url = runtime.url or runtime.uri or ""
    lines = [f"- `{runtime.id}` ({runtime.kind}, {runtime.status}) — {url}"]
    if roles:
        lines.append(f"  - roles: {roles}")
    return lines


def render_runtimes_section(ir: SystemMapIR) -> list[str]:
    lines = ["## Runtimes", ""]
    for runtime in ir.runtimes:
        lines.extend(runtime_lines(runtime))
    return lines


def command_lines(cmd: CommandSchemaIR) -> list[str]:
    required = ", ".join(field.name for field in cmd.fields if field.required)
    lines = [f"- `{cmd.name}` → runtime `{cmd.runtime or '?'}`"]
    if cmd.description:
        lines.append(f"  - {cmd.description}")
    if required:
        lines.append(f"  - required: {required}")
    return lines


def render_commands_section(ir: SystemMapIR) -> list[str]:
    lines = ["## Commands", ""]
    for cmd in ir.commands:
        lines.extend(command_lines(cmd))
    return lines


def render_capabilities_section(ir: SystemMapIR) -> list[str]:
    return ["## Capabilities", "", ", ".join(f"`{cap}`" for cap in ir.capabilities)]


def artifact_line(artifact: ArtifactSpecIR) -> str:
    return f"- `{artifact.path}` ({artifact.kind or 'file'})"


def render_artifacts_section(ir: SystemMapIR) -> list[str]:
    lines = ["## Artifacts", ""]
    for artifact in ir.artifacts:
        lines.append(artifact_line(artifact))
    return lines


def render_data_section(ir: SystemMapIR) -> list[str]:
    lines = ["## Data", ""]
    for key, value in sorted(ir.data.items()):
        lines.append(f"- `{key}`: {value!r}")
    return lines


def append_section(lines: list[str], section: list[str]) -> None:
    lines.extend(["", *section])
