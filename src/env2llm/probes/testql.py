"""Discover TestQL GUI/DOM automation capabilities for env2llm."""

from __future__ import annotations

from pathlib import Path
from typing import Any

_TESTQL_GUI_COMMANDS: tuple[tuple[str, str, list[str], list[str]], ...] = (
    ("testql_gui_start", "Start Playwright/Selenium session (GUI_START)", ["url"], ["app_path"]),
    ("testql_gui_navigate", "Navigate browser path (NAVIGATE)", ["path"], ["wait_ms"]),
    ("testql_gui_click", "Click DOM selector (CLICK)", ["selector"], []),
    ("testql_gui_input", "Type into selector (INPUT)", ["selector", "text"], []),
    ("testql_gui_assert_visible", "Assert element visible (ASSERT_VISIBLE)", ["selector"], []),
    ("testql_gui_assert_text", "Assert element text (ASSERT_TEXT)", ["selector", "expected"], []),
    ("testql_gui_capture", "Screenshot selector or page (GUI_CAPTURE)", ["file"], ["selector"]),
    ("testql_run_scenario", "Run .testql.toon.yaml scenario file", ["file_spec"], ["dry_run", "url"]),
    ("testql_inspect_url", "Browser inspect URL (Playwright DOM/network/console)", ["url"], ["out_dir"]),
    ("testql_generate_ir", "Generate scenario IR from source artifact", ["source", "artifact"], ["target"]),
)

# Fallback when testql.desktop.catalog is unavailable (older testql).
_TESTQL_DESKTOP_COMMANDS_FALLBACK: tuple[tuple[str, str, list[str], list[str]], ...] = (
    ("testql_desktop_list", "List open desktop windows (wmctrl or xdotool)", [], []),
    ("testql_desktop_focus", "Focus desktop window by title or window id", ["target"], []),
    ("testql_desktop_launch", "Launch native application executable", ["executable"], ["args"]),
    ("testql_desktop_click", "Click screen coordinates (ydotool/xdotool)", ["x", "y"], ["button"]),
    ("testql_desktop_type", "Type text into focused window (wtype/xdotool)", ["text"], []),
    ("testql_desktop_key", "Send key combo (Return, ctrl+s, …)", ["combo"], []),
    ("testql_desktop_capture", "Full-screen screenshot (grim/scrot)", ["file"], []),
    ("testql_desktop_assert_window", "Assert desktop window title exists", ["title"], []),
    ("testql_desktop_stop", "Stop apps launched in TestQL desktop session", [], []),
)


def _desktop_command_rows() -> list[tuple[str, str, list[str], list[str]]]:
    try:
        from testql.desktop.catalog import collect_desktop_catalog

        catalog = collect_desktop_catalog()
        return [
            (
                str(item["name"]),
                str(item["description"]),
                list(item.get("required") or []),
                list(item.get("optional") or []),
            )
            for item in catalog.get("commands") or []
        ]
    except ImportError:
        return list(_TESTQL_DESKTOP_COMMANDS_FALLBACK)


def _desktop_catalog_extra() -> dict[str, Any]:
    try:
        from testql.desktop.catalog import collect_desktop_catalog

        catalog = collect_desktop_catalog()
        return {
            "desktop": {
                "display_server": catalog.get("display_server"),
                "host_tools": catalog.get("host_tools") or [],
                "recommended_python_libs": catalog.get("recommended_python_libs") or [],
            },
        }
    except ImportError:
        return {}


def testql_available() -> bool:
    try:
        import testql  # noqa: F401

        return True
    except ImportError:
        return False


def discover_scenario_files(project_dir: Path | str) -> list[dict[str, Any]]:
    root = Path(project_dir).resolve()
    patterns = ("*.testql.toon.yaml", "*.testql.less", "*.oql", "*.tql")
    found: list[dict[str, Any]] = []
    for pattern in patterns:
        for path in sorted(root.rglob(pattern)):
            if any(part.startswith(".") for part in path.relative_to(root).parts):
                continue
            found.append(
                {
                    "path": str(path.relative_to(root)),
                    "format": path.suffixes[-2:] if path.name.endswith(".testql.toon.yaml") else [path.suffix],
                    "name": path.stem,
                }
            )
    return found[:64]


def collect_testql_catalog(project_dir: Path | str | None = None) -> dict[str, Any]:
    """Return TestQL capability catalog for registry enrichment."""
    scenarios: list[dict[str, Any]] = []
    if project_dir is not None:
        scenarios = discover_scenario_files(project_dir)

    playwright = False
    if testql_available():
        try:
            import playwright  # noqa: F401

            playwright = True
        except ImportError:
            playwright = False

    all_commands = list(_TESTQL_GUI_COMMANDS) + _desktop_command_rows()
    extra = _desktop_catalog_extra()

    return {
        "available": testql_available(),
        "playwright": playwright,
        "scenario_count": len(scenarios),
        "scenarios": scenarios,
        "gui_commands": [
            {
                "name": name,
                "description": description,
                "required": required,
                "optional": optional,
            }
            for name, description, required, optional in all_commands
        ],
        **extra,
    }
