"""Merge live desktop probe into SystemMapIR (optional)."""

from __future__ import annotations

import os
from pathlib import Path

from env2llm.ir import (
    AccessGrantIR,
    CommandSchemaIR,
    DesktopProbeIR,
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


def _mirror_desktop_core(ir: SystemMapIR, probe: DesktopProbeIR) -> None:
    ir.data["desktop.session"] = probe.session
    ir.data["desktop.platform"] = probe.platform
    ir.data["desktop.display_count"] = len(probe.displays)


def _mirror_desktop_canvas(ir: SystemMapIR, probe: DesktopProbeIR) -> None:
    if probe.canvas_width is not None:
        ir.data["desktop.canvas_width"] = probe.canvas_width
    if probe.canvas_height is not None:
        ir.data["desktop.canvas_height"] = probe.canvas_height
    if probe.displays:
        ir.data["desktop.displays"] = [display.model_dump() for display in probe.displays]


def _mirror_desktop_pointer(ir: SystemMapIR, probe: DesktopProbeIR) -> None:
    if probe.pointer is None:
        return
    ir.data["desktop.pointer"] = probe.pointer.model_dump()
    ir.data["desktop.pointer_x"] = probe.pointer.x
    ir.data["desktop.pointer_y"] = probe.pointer.y
    if probe.pointer.display_id:
        ir.data["desktop.pointer_display"] = probe.pointer.display_id
    if probe.pointer.display_x is not None:
        ir.data["desktop.pointer_display_x"] = probe.pointer.display_x
    if probe.pointer.display_y is not None:
        ir.data["desktop.pointer_display_y"] = probe.pointer.display_y


def _mirror_desktop_ide_calibrations(ir: SystemMapIR, probe: DesktopProbeIR) -> None:
    if not probe.ide_calibrations:
        return
    ir.data["desktop.ide_calibrations"] = [
        entry.model_dump() for entry in probe.ide_calibrations
    ]
    ir.data["desktop.ide_calibration_count"] = len(probe.ide_calibrations)
    for entry in probe.ide_calibrations:
        ir.data[f"desktop.ide_calibration.{entry.ide}"] = entry.model_dump()


def _mirror_desktop_windows(ir: SystemMapIR, probe: DesktopProbeIR) -> None:
    ir.data["desktop.window_count"] = len(probe.windows)
    ir.data["desktop.browser_window_count"] = sum(1 for window in probe.windows if window.is_browser)
    if probe.windows:
        ir.data["desktop.window_titles"] = [window.title for window in probe.windows[:12]]
    active = next((window for window in probe.windows if window.active), None)
    if active is not None:
        ir.data["desktop.active_window"] = active.title
    browsers = [window.title for window in probe.windows if window.is_browser][:8]
    if browsers:
        ir.data["desktop.browser_windows"] = browsers


def _mirror_desktop_summary(ir: SystemMapIR) -> None:
    if ir.desktop is None:
        return
    probe = ir.desktop
    _mirror_desktop_core(ir, probe)
    _mirror_desktop_canvas(ir, probe)
    _mirror_desktop_pointer(ir, probe)
    _mirror_desktop_ide_calibrations(ir, probe)
    _mirror_desktop_windows(ir, probe)


def apply_desktop_probe(
    ir: SystemMapIR,
    *,
    enabled: bool | None = None,
    project_dir: Path | str | None = None,
) -> SystemMapIR:
    """Attach a live desktop snapshot and desktop automation catalog to *ir*."""
    if not desktop_probe_enabled(explicit=enabled):
        return ir

    probe = collect_desktop_probe(project_dir=project_dir)
    ir.desktop = probe
    ir.metadata["desktop_probe"] = {
        "tools": probe.tools_used,
        "window_count": len(probe.windows),
        "ide_calibration_count": len(probe.ide_calibrations),
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
