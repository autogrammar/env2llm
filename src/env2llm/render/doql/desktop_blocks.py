"""Render desktop-related DOQL blocks from SystemMapIR."""

from __future__ import annotations

from env2llm.ir import (
    DesktopDisplayIR,
    DesktopIdeCalibrationIR,
    DesktopPointerIR,
    DesktopProbeIR,
    DesktopWindowIR,
    SystemMapIR,
)
from .helpers import bool_lit, esc_str, esc_str_full, join_csv


def _render_desktop_summary(probe: DesktopProbeIR) -> list[str]:
    lines = ["desktop {"]
    lines.append(f'  platform: "{esc_str(probe.platform)}";')
    lines.append(f'  session: "{esc_str(probe.session)}";')
    lines.append(f'  status: "{probe.status}";')
    if probe.compositor:
        lines.append(f'  compositor: "{esc_str(probe.compositor)}";')
    if probe.display_server:
        lines.append(f'  display_server: "{esc_str(probe.display_server)}";')
    if probe.probed_at:
        lines.append(f'  probed_at: "{esc_str(probe.probed_at)}";')
    if probe.tools_used:
        lines.append(f"  tools_used: {join_csv(probe.tools_used)};")
    if probe.canvas_width is not None:
        lines.append(f"  canvas_width: {probe.canvas_width};")
    if probe.canvas_height is not None:
        lines.append(f"  canvas_height: {probe.canvas_height};")
    lines.extend(["}", ""])
    return lines


def _render_desktop_pointer_block(pointer: DesktopPointerIR) -> list[str]:
    lines = ["desktop_pointer {"]
    lines.append(f"  x: {pointer.x};")
    lines.append(f"  y: {pointer.y};")
    if pointer.screen is not None:
        lines.append(f"  screen: {pointer.screen};")
    if pointer.window_id:
        lines.append(f'  window_id: "{esc_str(pointer.window_id)}";')
    if pointer.display_id:
        lines.append(f'  display_id: "{esc_str(pointer.display_id)}";')
    if pointer.display_output:
        lines.append(f'  display_output: "{esc_str(pointer.display_output)}";')
    if pointer.display_x is not None:
        lines.append(f"  display_x: {pointer.display_x};")
    if pointer.display_y is not None:
        lines.append(f"  display_y: {pointer.display_y};")
    lines.extend(["}", ""])
    return lines


def _render_desktop_display_block(idx: int, display: DesktopDisplayIR) -> list[str]:
    lines = [f"desktop_displays[{idx}] {{"]
    lines.append(f'  id: "{esc_str(display.id)}";')
    lines.append(f"  width: {display.width};")
    lines.append(f"  height: {display.height};")
    lines.append(f"  left: {display.left};")
    lines.append(f"  top: {display.top};")
    lines.append(f"  is_primary: {bool_lit(display.is_primary)};")
    if display.output:
        lines.append(f'  output: "{esc_str(display.output)}";')
    if display.index is not None:
        lines.append(f"  index: {display.index};")
    lines.extend(["}", ""])
    return lines


def _render_desktop_ide_calibration_block(
    idx: int,
    calibration: DesktopIdeCalibrationIR,
) -> list[str]:
    lines = [f"desktop_ide_calibrations[{idx}] {{"]
    lines.append(f'  ide: "{esc_str(calibration.ide)}";')
    lines.append(f"  chat_x: {calibration.chat_x};")
    lines.append(f"  chat_y: {calibration.chat_y};")
    if calibration.config_path:
        lines.append(f'  config_path: "{esc_str_full(calibration.config_path)}";')
    if calibration.source:
        lines.append(f'  source: "{esc_str(calibration.source)}";')
    if calibration.display_id:
        lines.append(f'  display_id: "{esc_str(calibration.display_id)}";')
    if calibration.display_output:
        lines.append(f'  display_output: "{esc_str(calibration.display_output)}";')
    if calibration.display_x is not None:
        lines.append(f"  display_x: {calibration.display_x};")
    if calibration.display_y is not None:
        lines.append(f"  display_y: {calibration.display_y};")
    if calibration.window_id is not None:
        lines.append(f"  window_id: {calibration.window_id};")
    if calibration.calibrated_at:
        lines.append(f'  calibrated_at: "{esc_str(calibration.calibrated_at)}";')
    lines.extend(["}", ""])
    return lines


def _render_desktop_window_block(idx: int, window: DesktopWindowIR) -> list[str]:
    lines = [f"desktop_windows[{idx}] {{"]
    lines.append(f'  id: "{esc_str(window.id)}";')
    lines.append(f'  title: "{esc_str_full(window.title)}";')
    lines.append(f"  x: {window.x};")
    lines.append(f"  y: {window.y};")
    lines.append(f"  width: {window.width};")
    lines.append(f"  height: {window.height};")
    lines.append(f"  workspace: {window.workspace};")
    lines.append(f"  is_browser: {bool_lit(window.is_browser)};")
    lines.append(f"  active: {bool_lit(window.active)};")
    lines.extend(["}", ""])
    return lines


def render_desktop_block(ir: SystemMapIR) -> list[str]:
    if ir.desktop is None:
        return []
    probe = ir.desktop
    lines: list[str] = []
    lines.extend(_render_desktop_summary(probe))
    if probe.pointer is not None:
        lines.extend(_render_desktop_pointer_block(probe.pointer))
    for idx, display in enumerate(probe.displays):
        lines.extend(_render_desktop_display_block(idx, display))
    for idx, calibration in enumerate(probe.ide_calibrations):
        lines.extend(_render_desktop_ide_calibration_block(idx, calibration))
    for idx, window in enumerate(probe.windows):
        lines.extend(_render_desktop_window_block(idx, window))
    return lines
