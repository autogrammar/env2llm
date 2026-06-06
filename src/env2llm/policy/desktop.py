"""Merge live desktop probe into SystemMapIR (optional)."""

from __future__ import annotations

import os

from env2llm.ir import (
    AccessGrantIR,
    CommandSchemaIR,
    FieldSpec,
    ProtocolSpec,
    ResourceSpecIR,
    RuntimeSpecIR,
    SystemMapIR,
)
from env2llm.probes.desktop import collect_desktop_probe
from env2llm.runtimes import resolve_command_runtime

_DESKTOP_COMMANDS: tuple[tuple[str, str, list[str], list[str]], ...] = (
    (
        "desktop_focus_window",
        "Focus a window by title (desktop-window://focus)",
        ["title"],
        ["name"],
    ),
    (
        "desktop_move_window",
        "Move a window to a monitor (desktop-window://move)",
        ["title"],
        ["screen"],
    ),
    (
        "desktop_screenshot_screen",
        "Capture full screen (desktop-screenshot://screen)",
        [],
        [],
    ),
    (
        "desktop_screenshot_window",
        "Capture a window by title (desktop-screenshot://window)",
        ["title"],
        ["mode"],
    ),
    (
        "desktop_open_app",
        "Launch or open an application (app://{app}/open)",
        ["app"],
        ["path"],
    ),
)

_DESKTOP_RUNTIME = RuntimeSpecIR(
    id="probe:desktop",
    kind="external",
    uri="desktop://session",
    roles=["gui_automation", "window_focus", "screenshot", "app_launch"],
    status="unknown",
)

_DESKTOP_RESOURCE = ResourceSpecIR(
    id="desktop:gui",
    title="Interactive desktop session",
    connector="desktop",
    uri_patterns=["desktop://**", "app://**", "desktop-screenshot://**", "desktop-window://**"],
)


def desktop_probe_enabled(*, explicit: bool | None = None) -> bool:
    if explicit is not None:
        return explicit
    return os.environ.get("ENV2LLM_DESKTOP_PROBE", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )


def _ensure_desktop_runtime(ir: SystemMapIR, *, status: str) -> None:
    existing = ir.runtime("probe:desktop")
    if existing is not None:
        existing.status = status  # type: ignore[assignment]
        return
    ir.runtimes.append(
        _DESKTOP_RUNTIME.model_copy(update={"status": status}),
    )


def _ensure_desktop_resource(ir: SystemMapIR) -> None:
    if any(resource.id == _DESKTOP_RESOURCE.id for resource in ir.resources):
        return
    ir.resources.append(_DESKTOP_RESOURCE.model_copy(deep=True))


def _ensure_desktop_commands(ir: SystemMapIR) -> None:
    existing = {cmd.name for cmd in ir.commands}
    for name, description, required, optional in _DESKTOP_COMMANDS:
        if name in existing:
            continue
        fields = [FieldSpec(name=field, required=True) for field in required]
        fields.extend(FieldSpec(name=field, required=False) for field in optional)
        ir.commands.append(
            CommandSchemaIR(
                name=name,
                description=description,
                runtime="probe:desktop",
                protocol=ProtocolSpec(name="mcp", transport="nlp2uri"),
                fields=fields,
            )
        )
        existing.add(name)


def _ensure_desktop_access(ir: SystemMapIR) -> None:
    if any(
        grant.agent == "desktop-agent" and grant.resource_area == _DESKTOP_RESOURCE.id
        for grant in ir.access
    ):
        return
    ir.access.append(
        AccessGrantIR(
            agent="desktop-agent",
            resource_area=_DESKTOP_RESOURCE.id,
            actions=[cmd[0] for cmd in _DESKTOP_COMMANDS],
            effect="allow",
        )
    )


def _mirror_desktop_summary(ir: SystemMapIR) -> None:
    if ir.desktop is None:
        return
    probe = ir.desktop
    ir.data["desktop.session"] = probe.session
    ir.data["desktop.platform"] = probe.platform
    ir.data["desktop.window_count"] = len(probe.windows)
    ir.data["desktop.browser_window_count"] = sum(1 for w in probe.windows if w.is_browser)
    if probe.windows:
        titles = [w.title for w in probe.windows[:12]]
        ir.data["desktop.window_titles"] = titles
    active = next((w for w in probe.windows if w.active), None)
    if active is not None:
        ir.data["desktop.active_window"] = active.title
    browsers = [w.title for w in probe.windows if w.is_browser][:8]
    if browsers:
        ir.data["desktop.browser_windows"] = browsers


def apply_desktop_probe(ir: SystemMapIR, *, enabled: bool | None = None) -> SystemMapIR:
    """Attach a live desktop snapshot and desktop automation catalog to *ir*."""
    if not desktop_probe_enabled(explicit=enabled):
        return ir

    probe = collect_desktop_probe()
    ir.desktop = probe
    ir.metadata["desktop_probe"] = {
        "tools": probe.tools_used,
        "window_count": len(probe.windows),
        "probed_at": probe.probed_at,
    }

    status = probe.status
    _ensure_desktop_runtime(ir, status=status)
    _ensure_desktop_resource(ir)
    _ensure_desktop_commands(ir)
    _ensure_desktop_access(ir)
    _mirror_desktop_summary(ir)

    for cmd in ir.commands:
        if cmd.name.startswith("desktop_") and not cmd.runtime:
            cmd.runtime = resolve_command_runtime(cmd.name)

    if "desktop_automation" not in ir.capabilities:
        ir.capabilities.append("desktop_automation")

    return ir
