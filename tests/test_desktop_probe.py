"""Tests for desktop/GUI environment probe."""

from __future__ import annotations

from env2llm.ir import DesktopDisplayIR, DesktopPointerIR, DesktopProbeIR, DesktopWindowIR, SystemMapIR
from env2llm.policy.desktop import apply_desktop_probe
from env2llm.probes.desktop import parse_wmctrl_listing, parse_xrandr_query
from env2llm.probes.display_layout import resolve_pointer_display
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


_XRANDR_SAMPLE = """\
Screen 0: minimum 16 x 16, current 8416 x 7680, maximum 32767 x 32767
HDMI-1 connected 2048x1280+0+3864 (normal left inverted right x axis y axis) 300mm x 260mm
DP-2 connected primary 4320x7680+4096+0 left (normal left inverted right x axis y axis) 700mm x 390mm
DP-1 connected 4096x2560+0+1304 left (normal left inverted right x axis y axis) 700mm x 390mm
"""


def test_parse_xrandr_query_extracts_canvas_and_displays() -> None:
    canvas_w, canvas_h, displays = parse_xrandr_query(_XRANDR_SAMPLE)
    assert canvas_w == 8416
    assert canvas_h == 7680
    assert len(displays) == 3
    assert displays[1].id == "DP-2"
    assert displays[1].width == 4320
    assert displays[1].height == 7680
    assert displays[1].left == 4096
    assert displays[1].top == 0
    assert displays[1].is_primary is True
    assert displays[0].output == "HDMI-1"


def test_resolve_pointer_display_maps_local_coordinates() -> None:
    displays = parse_xrandr_query(_XRANDR_SAMPLE)[2]
    pointer = resolve_pointer_display(DesktopPointerIR(x=8151, y=68), displays)
    assert pointer.display_id == "DP-2"
    assert pointer.display_output == "DP-2"
    assert pointer.display_x == 4055
    assert pointer.display_y == 68


def test_apply_desktop_probe_adds_runtime_commands_and_doql_block(monkeypatch) -> None:
    probe = DesktopProbeIR(
        platform="linux",
        session="GNOME",
        display_server="x11",
        tools_used=["wmctrl", "xrandr", "xdotool"],
        canvas_width=8416,
        canvas_height=7680,
        displays=[
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
        ],
        pointer=DesktopPointerIR(
            x=8151,
            y=68,
            display_id="DP-2",
            display_output="DP-2",
            display_x=4055,
            display_y=68,
        ),
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
        lambda **_: probe,
    )

    ir = SystemMapIR(example_id="demo")
    apply_desktop_probe(ir, enabled=True)

    assert ir.desktop is not None
    assert ir.runtime("probe:desktop") is not None
    assert ir.command("desktop_focus_window") is not None
    assert ir.data["desktop.window_count"] == 1
    assert ir.data["desktop.active_window"] == "Mozilla Firefox"
    assert ir.data["desktop.display_count"] == 1
    assert ir.data["desktop.pointer_display"] == "DP-2"
    assert ir.data["desktop.pointer_display_x"] == 4055

    doql = render_system_map_doql(ir)
    assert "desktop {" in doql
    assert "canvas_width: 8416;" in doql
    assert "desktop_pointer {" in doql
    assert "display_x: 4055;" in doql
    assert 'session: "GNOME"' in doql
    assert "desktop_displays[0]" in doql
    assert "left: 4096;" in doql
    assert "desktop_windows[0]" in doql
    assert 'title: "Mozilla Firefox"' in doql
    assert "probe:desktop" in doql or "desktop_focus_window" in doql
