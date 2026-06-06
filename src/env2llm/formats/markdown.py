"""Human-readable markdown summary for LLM decision-making."""

from __future__ import annotations

from env2llm.doql import DoqlTaskContext
from env2llm.ir import SystemMapIR


def render_markdown(ir: SystemMapIR, _ctx: DoqlTaskContext | None = None) -> str:
    lines: list[str] = [
        f"# Environment map — {ir.example_id}",
        "",
        f"- format: `{ir.format}`",
        f"- generated: {getattr(ir, 'generated_at', None) or ir.metadata.get('generated_at', 'unknown')}",
        "",
        "## Environment",
        "",
    ]
    for key, value in sorted((ir.environment or {}).items()):
        lines.append(f"- **{key}**: `{value}`")

    lines.extend(["", "## Runtimes", ""])
    for runtime in ir.runtimes:
        roles = ", ".join(runtime.roles or [])
        url = runtime.url or runtime.uri or ""
        lines.append(f"- `{runtime.id}` ({runtime.kind}, {runtime.status}) — {url}")
        if roles:
            lines.append(f"  - roles: {roles}")

    lines.extend(["", "## Commands", ""])
    for cmd in ir.commands:
        req = ", ".join(f.name for f in cmd.fields if f.required)
        lines.append(f"- `{cmd.name}` → runtime `{cmd.runtime or '?'}`")
        if cmd.description:
            lines.append(f"  - {cmd.description}")
        if req:
            lines.append(f"  - required: {req}")

    if ir.capabilities:
        lines.extend(["", "## Capabilities", "", ", ".join(f"`{c}`" for c in ir.capabilities)])

    if ir.artifacts:
        lines.extend(["", "## Artifacts", ""])
        for artifact in ir.artifacts:
            lines.append(f"- `{artifact.path}` ({artifact.kind or 'file'})")

    if ir.data:
        lines.extend(["", "## Data", ""])
        for key, value in sorted(ir.data.items()):
            lines.append(f"- `{key}`: {value!r}")

    return "\n".join(lines) + "\n"
