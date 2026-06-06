"""Tests for desktop/GUI environment probe."""

from __future__ import annotations

from env2llm.ir import DesktopProbeIR, DesktopWindowIR, SystemMapIR
from env2llm.policy.desktop import apply_desktop_probe
from env2llm.probes.desktop import parse_wmctrl_listing
from env2llm.render.doql.render import render_system_map_doql


_WMCTRL_SAMPLE = """\
0x01200004  0 1400 30   800 600  nvidia  Mozilla Firefox
0x03a00007  1 0 0 1920 1080 nvidia  Slack
"""


def test_parse_wmctrl_listing_detects_geometry_and_browser() -> None:
    windows = parse_wmctrl_listing(_WMCTRL_SAMPLE)
    assert len(windows) == 2
    assert windows[0].title == "Mozilla Firefox"
    assert windows[0].x == 1400
    assert windows[0].width == 800
    assert windows[0].is_browser is True
    assert windows[1].title == "Slack"
    assert windows[1].is_browser is False


def test_apply_desktop_probe_adds_runtime_commands_and_doql_block(monkeypatch) -> None:
    probe = DesktopProbeIR(
        platform="linux",
        session="GNOME",
        display_server="x11",
        tools_used=["wmctrl"],
        windows=[
            DesktopWindowIR(
                id="0x01200004",
                title="Mozilla Firefox",
                x=100,
                y=50,
                width=1200,
                height=800,
                is_browser=True,
                active=True,
            )
        ],
        probed_at="2026-06-06T12:00:00+00:00",
        status="available",
    )
    monkeypatch.setattr(
        "env2llm.policy.desktop.collect_desktop_probe",
        lambda: probe,
    )

    ir = SystemMapIR(example_id="demo")
    apply_desktop_probe(ir, enabled=True)

    assert ir.desktop is not None
    assert ir.runtime("probe:desktop") is not None
    assert ir.command("desktop_focus_window") is not None
    assert ir.data["desktop.window_count"] == 1
    assert ir.data["desktop.active_window"] == "Mozilla Firefox"

    doql = render_system_map_doql(ir)
    assert "desktop {" in doql
    assert 'session: "GNOME"' in doql
    assert "desktop_windows[0]" in doql
    assert 'title: "Mozilla Firefox"' in doql
    assert "probe:desktop" in doql or "desktop_focus_window" in doql
