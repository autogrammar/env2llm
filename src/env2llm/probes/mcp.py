"""Discover MCP tool catalogs for env2llm registry enrichment."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def koru_mcp_available() -> bool:
    try:
        import koruapi.mcp_server_schema  # noqa: F401

        return True
    except ImportError:
        return False


def is_koru_project(project_dir: Path | str) -> bool:
    root = Path(project_dir).resolve()
    pyproject = root / "pyproject.toml"
    if pyproject.is_file():
        text = pyproject.read_text(encoding="utf-8", errors="replace")
        if 'name = "koru"' in text or "name = 'koru'" in text:
            return True
    return (root / "src" / "koruapi" / "mcp_server_schema.py").is_file()


def collect_koru_mcp_tools() -> list[dict[str, Any]]:
    """Load Koru MCP ``tools/list`` schemas when koruapi is installed."""
    try:
        from koruapi.mcp_server_schema import TOOLS
    except ImportError:
        return []
    return [dict(tool) for tool in TOOLS]


def collect_mcp_tools(project_dir: Path | str | None = None) -> list[dict[str, Any]]:
    """
    Collect MCP tool schemas for the current project.

    Today: Koru ``koruapi.mcp_server_schema.TOOLS`` when importable.
    """
    if project_dir is not None and not is_koru_project(project_dir) and not koru_mcp_available():
        return []
    if koru_mcp_available():
        return collect_koru_mcp_tools()
    return []
