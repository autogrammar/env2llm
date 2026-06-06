"""Tests for Koru OS-injector calibration probe."""

from __future__ import annotations

import json
from pathlib import Path

from env2llm.ir import DesktopDisplayIR, DesktopProbeIR, SystemMapIR
from env2llm.policy.desktop import apply_desktop_probe
from env2llm.probes.ide_os_injector import (
    collect_ide_os_injector_calibrations,
    parse_ide_os_injector_file,
)
from env2llm.render.doql.render import render_system_map_doql


def test_parse_ide_os_injector_file_reads_chat_coordinates(tmp_path: Path) -> None:
    path = tmp_path / "ide-os-injector.json"
    path.write_text(
        json.dumps({"cursor": {"chat_x": 8151, "chat_y": 68}, "main": {"chat_x": 1, "chat_y": 2}}),
        encoding="utf-8",
    )
    profiles = parse_ide_os_injector_file(path)
    assert profiles == {"cursor": (8151, 68), "main": (1, 2)}


def test_collect_ide_os_injector_calibrations_resolves_display(
    tmp_path: Path,
    monkeypatch,
) -> None:
    koru_dir = tmp_path / ".koru"
    koru_dir.mkdir()
    config = koru_dir / "ide-os-injector.json"
    config.write_text(json.dumps({"cursor": {"chat_x": 8151, "chat_y": 68}}), encoding="utf-8")
    monkeypatch.setattr(
        "env2llm.probes.ide_os_injector.iter_ide_os_injector_paths",
        lambda project_dir=None: [("project", config)],
    )

    displays = [
        DesktopDisplayIR(
            id="DP-2",
            output="DP-2",
            width=4320,
            height=7680,
            left=4096,
            top=0,
            is_primary=True,
            index=1,
        )
    ]
    rows = collect_ide_os_injector_calibrations(project_dir=tmp_path, displays=displays)
    assert len(rows) == 1
    assert rows[0].ide == "cursor"
    assert rows[0].chat_x == 8151
    assert rows[0].display_id == "DP-2"
    assert rows[0].display_x == 4055
    assert rows[0].source == "project"
    assert rows[0].config_path == str(config)


def test_apply_desktop_probe_renders_ide_calibrations_in_doql(
    monkeypatch,
    tmp_path: Path,
) -> None:
    koru_dir = tmp_path / ".koru"
    koru_dir.mkdir()
    config = koru_dir / "ide-os-injector.json"
    config.write_text(
        json.dumps({"cursor": {"chat_x": 100, "chat_y": 200}}),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "env2llm.probes.ide_os_injector.iter_ide_os_injector_paths",
        lambda project_dir=None: [("project", config)],
    )

    probe = DesktopProbeIR(
        platform="linux",
        session="GNOME",
        status="available",
        ide_calibrations=collect_ide_os_injector_calibrations(project_dir=tmp_path),
    )
    monkeypatch.setattr("env2llm.policy.desktop.collect_desktop_probe", lambda **_: probe)

    ir = SystemMapIR(example_id="demo")
    apply_desktop_probe(ir, enabled=True, project_dir=tmp_path)

    assert ir.data["desktop.ide_calibration.cursor"]["chat_x"] == 100
    doql = render_system_map_doql(ir)
    assert "desktop_ide_calibrations[0]" in doql
    assert 'ide: "cursor"' in doql
    assert "chat_x: 100;" in doql
