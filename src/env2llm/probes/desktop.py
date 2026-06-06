"""Desktop / GUI environment probe (Linux GNOME-first)."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone

from env2llm.ir import DesktopDisplayIR, DesktopProbeIR, DesktopWindowIR

_BROWSER_TITLE_RE = re.compile(
    r"\b(firefox|chrome|chromium|brave|edge|opera|vivaldi|safari)\b",
    re.IGNORECASE,
)
_WMCTRL_LINE_RE = re.compile(
    r"^(0x[0-9a-fA-F]+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(\d+)\s+(\d+)\s+\S+\s+(.+)$"
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


def _probe_display_geometry() -> list[DesktopDisplayIR]:
    if not shutil.which("xdotool"):
        return []
    out = _run_text(["xdotool", "getdisplaygeometry"])
    if not out:
        return []
    parts = out.split()
    if len(parts) < 2:
        return []
    try:
        width, height = int(parts[0]), int(parts[1])
    except ValueError:
        return []
    return [DesktopDisplayIR(id="primary", width=width, height=height)]


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


def collect_desktop_probe() -> DesktopProbeIR:
    """
    Snapshot the interactive desktop session when probe tools are available.

    Linux: prefers ``wmctrl -l -G`` for window geometry; ``xdotool`` for display
    size and active window. Safe on headless hosts — returns empty windows.
    """
    tools: list[str] = []
    windows: list[DesktopWindowIR] = []
    displays = _probe_display_geometry()
    if displays and "xdotool" not in tools:
        tools.append("xdotool")

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

    return DesktopProbeIR(
        platform=sys.platform,
        session=session,
        compositor=compositor,
        display_server=display_server,
        tools_used=sorted(set(tools)),
        displays=displays,
        windows=windows,
        probed_at=datetime.now(timezone.utc).isoformat(),
        status="available" if windows or displays else "unknown",
    )
