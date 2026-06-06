"""Probe Koru OS-injector calibration profiles (``ide-os-injector.json``)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from env2llm.ir import DesktopDisplayIR, DesktopIdeCalibrationIR, DesktopPointerIR
from env2llm.probes.display_layout import resolve_pointer_display


def iter_ide_os_injector_paths(project_dir: Path | str | None = None) -> list[tuple[str, Path]]:
    """Return calibration files in precedence order (project overrides global)."""
    paths: list[tuple[str, Path]] = []
    if project_dir is not None:
        project_path = Path(project_dir).resolve() / ".koru" / "ide-os-injector.json"
        if project_path.is_file():
            paths.append(("project", project_path))
    global_path = Path.home() / ".koru" / "ide-os-injector.json"
    if global_path.is_file():
        paths.append(("global", global_path))
    return paths


def parse_ide_os_injector_file(path: Path) -> dict[str, tuple[int, int]]:
    """Parse ``{ "cursor": { "chat_x": 1, "chat_y": 2 }, ... }`` into coordinate pairs."""
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(raw, dict):
        return {}

    profiles: dict[str, tuple[int, int]] = {}
    for ide, entry in raw.items():
        if not isinstance(ide, str) or not isinstance(entry, dict):
            continue
        try:
            profiles[ide] = (int(entry["chat_x"]), int(entry["chat_y"]))
        except (KeyError, TypeError, ValueError):
            continue
    return profiles


def _calibrated_at(path: Path) -> str | None:
    try:
        stamp = path.stat().st_mtime
    except OSError:
        return None
    return datetime.fromtimestamp(stamp, tz=timezone.utc).isoformat()


def collect_ide_os_injector_calibrations(
    *,
    project_dir: Path | str | None = None,
    displays: list[DesktopDisplayIR] | None = None,
) -> list[DesktopIdeCalibrationIR]:
    """Load IDE chat anchors from Koru OS-injector profile files."""
    merged: dict[str, DesktopIdeCalibrationIR] = {}
    display_list = displays or []

    for source, path in iter_ide_os_injector_paths(project_dir):
        calibrated_at = _calibrated_at(path)
        for ide, (chat_x, chat_y) in parse_ide_os_injector_file(path).items():
            pointer = resolve_pointer_display(
                DesktopPointerIR(x=chat_x, y=chat_y),
                display_list,
            )
            merged[ide] = DesktopIdeCalibrationIR(
                ide=ide,
                chat_x=chat_x,
                chat_y=chat_y,
                config_path=str(path),
                source=source,
                display_id=pointer.display_id,
                display_output=pointer.display_output,
                display_x=pointer.display_x,
                display_y=pointer.display_y,
                calibrated_at=calibrated_at,
            )

    return [merged[key] for key in sorted(merged)]

