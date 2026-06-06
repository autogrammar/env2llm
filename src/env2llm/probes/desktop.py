"""Desktop / GUI environment probe (Linux GNOME-first)."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from env2llm.ir import DesktopDisplayIR, DesktopPointerIR, DesktopProbeIR, DesktopWindowIR
from env2llm.probes.display_layout import resolve_pointer_display
from env2llm.probes.ide_os_injector import collect_ide_os_injector_calibrations

_BROWSER_TITLE_RE = re.compile(
    r"\b(firefox|chrome|chromium|brave|edge|opera|vivaldi|safari)\b",
    re.IGNORECASE,
)
_WMCTRL_LINE_RE = re.compile(
    r"^(0x[0-9a-fA-F]+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(\d+)\s+(\d+)\s+\S+\s+(.+)$"
)
_XRANDR_SCREEN_RE = re.compile(
    r"^Screen \d+: .* current (\d+) x (\d+)",
    re.IGNORECASE,
)
_XRANDR_OUTPUT_RE = re.compile(
    r"^(\S+)\s+connected(?:\s+primary)?\s+(\d+)x(\d+)\+(-?\d+)\+(-?\d+)",
    re.IGNORECASE,
)


def _run_text(argv: list[str], *, timeout: float = 5.0) -> str | None:
    try:
        proc = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout.strip() or None


def _is_browser_title(title: str) -> bool:
    return bool(_BROWSER_TITLE_RE.search(title))


def parse_wmctrl_listing(text: str) -> list[DesktopWindowIR]:
    """Parse ``wmctrl -l -G`` output into window records."""
    windows: list[DesktopWindowIR] = []
    for line in text.splitlines():
        match = _WMCTRL_LINE_RE.match(line.strip())
        if not match:
            continue
        window_id, workspace, x, y, width, height, title = match.groups()
        windows.append(
            DesktopWindowIR(
                id=window_id,
                title=title.strip(),
                x=int(x),
                y=int(y),
                width=int(width),
                height=int(height),
                workspace=int(workspace),
                is_browser=_is_browser_title(title),
            ),
        )
    return windows


def parse_xrandr_query(text: str) -> tuple[int | None, int | None, list[DesktopDisplayIR]]:
    """Parse ``xrandr --query`` into canvas size and per-output display records."""
    canvas_width: int | None = None
    canvas_height: int | None = None
    displays: list[DesktopDisplayIR] = []

    for line in text.splitlines():
        screen_match = _XRANDR_SCREEN_RE.match(line.strip())
        if screen_match:
            canvas_width = int(screen_match.group(1))
            canvas_height = int(screen_match.group(2))
            continue

        output_match = _XRANDR_OUTPUT_RE.match(line.strip())
        if not output_match:
            continue

        output, width, height, left, top = output_match.groups()
        is_primary = " primary " in f" {line.lower()} "
        displays.append(
            DesktopDisplayIR(
                id=output,
                output=output,
                width=int(width),
                height=int(height),
                left=int(left),
                top=int(top),
                is_primary=is_primary,
                index=len(displays),
            ),
        )

    return canvas_width, canvas_height, displays


def _probe_displays_xrandr() -> tuple[int | None, int | None, list[DesktopDisplayIR]]:
    if not shutil.which("xrandr"):
        return None, None, []
    listing = _run_text(["xrandr", "--query"])
    if not listing:
        return None, None, []
    return parse_xrandr_query(listing)


def _probe_displays_mss() -> list[DesktopDisplayIR]:
    try:
        import mss  # type: ignore[import-untyped]
    except ImportError:
        return []

    displays: list[DesktopDisplayIR] = []
    try:
        with mss.MSS() as sct:
            for index, monitor in enumerate(sct.monitors[1:]):
                displays.append(
                    DesktopDisplayIR(
                        id=str(monitor.get("output") or f"monitor-{index}"),
                        output=str(monitor.get("output") or "") or None,
                        width=int(monitor["width"]),
                        height=int(monitor["height"]),
                        left=int(monitor["left"]),
                        top=int(monitor["top"]),
                        is_primary=bool(monitor.get("is_primary")),
                        index=index,
                    ),
                )
    except (OSError, KeyError, TypeError, ValueError):
        return []
    return displays


def _probe_display_geometry() -> tuple[int | None, int | None, list[DesktopDisplayIR]]:
    canvas_w, canvas_h, displays = _probe_displays_xrandr()
    if displays:
        return canvas_w, canvas_h, displays

    displays = _probe_displays_mss()
    if displays:
        max_right = max(d.left + d.width for d in displays)
        max_bottom = max(d.top + d.height for d in displays)
        return max_right, max_bottom, displays

    if not shutil.which("xdotool"):
        return None, None, []
    out = _run_text(["xdotool", "getdisplaygeometry"])
    if not out:
        return None, None, []
    parts = out.split()
    if len(parts) < 2:
        return None, None, []
    try:
        width, height = int(parts[0]), int(parts[1])
    except ValueError:
        return None, None, []
    return width, height, [DesktopDisplayIR(id="primary", width=width, height=height)]


def _probe_mouse_pointer() -> DesktopPointerIR | None:
    if not shutil.which("xdotool"):
        return None
    out = _run_text(["xdotool", "getmouselocation", "--shell"])
    if not out:
        return None

    values: dict[str, str] = {}
    for line in out.splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip().upper()] = value.strip()

    try:
        pointer = DesktopPointerIR(
            x=int(values["X"]),
            y=int(values["Y"]),
            screen=int(values["SCREEN"]) if "SCREEN" in values else None,
            window_id=values.get("WINDOW"),
        )
    except (KeyError, ValueError):
        return None
    return pointer


def _probe_active_window_id() -> str | None:
    if not shutil.which("xdotool"):
        return None
    out = _run_text(["xdotool", "getactivewindow"])
    if not out:
        return None
    window_id = out.strip()
    if window_id.isdigit():
        return f"0x{int(window_id):x}"
    return window_id


def collect_desktop_probe(*, project_dir: Path | str | None = None) -> DesktopProbeIR:
    """
    Snapshot the interactive desktop session when probe tools are available.

    Linux: ``xrandr`` / ``mss`` for multi-monitor layout; ``xdotool`` for pointer,
    display fallback, and active window; ``wmctrl -l -G`` for window geometry.
    Safe on headless hosts — returns empty windows.
    """
    tools: list[str] = []
    windows: list[DesktopWindowIR] = []

    canvas_width, canvas_height, displays = _probe_display_geometry()
    if displays:
        if shutil.which("xrandr"):
            tools.append("xrandr")
        elif any(display.left or display.top for display in displays):
            tools.append("mss")
        elif "xdotool" not in tools:
            tools.append("xdotool")

    pointer = _probe_mouse_pointer()
    if pointer is not None:
        tools.append("xdotool")
        pointer = resolve_pointer_display(pointer, displays)

    if shutil.which("wmctrl"):
        tools.append("wmctrl")
        listing = _run_text(["wmctrl", "-l", "-G"])
        if listing:
            windows = parse_wmctrl_listing(listing)

    active_id = _probe_active_window_id()
    if active_id:
        for window in windows:
            if window.id.lower() == active_id.lower():
                window.active = True

    session = (
        os.environ.get("XDG_CURRENT_DESKTOP")
        or os.environ.get("DESKTOP_SESSION")
        or "unknown"
    )
    compositor = os.environ.get("XDG_SESSION_TYPE") or None

    display_server: str | None = None
    if os.environ.get("WAYLAND_DISPLAY"):
        display_server = "wayland"
    elif os.environ.get("DISPLAY"):
        display_server = "x11"

    ide_calibrations = collect_ide_os_injector_calibrations(
        project_dir=project_dir,
        displays=displays,
    )
    if ide_calibrations and "ide-os-injector" not in tools:
        tools.append("ide-os-injector")

    has_geometry = bool(displays or pointer is not None or canvas_width or ide_calibrations)
    status: str
    if windows or has_geometry:
        status = "available"
    else:
        status = "unknown"

    return DesktopProbeIR(
        platform=sys.platform,
        session=session,
        compositor=compositor,
        display_server=display_server,
        tools_used=sorted(set(tools)),
        canvas_width=canvas_width,
        canvas_height=canvas_height,
        displays=displays,
        pointer=pointer,
        ide_calibrations=ide_calibrations,
        windows=windows,
        probed_at=datetime.now(timezone.utc).isoformat(),
        status=status,
    )
