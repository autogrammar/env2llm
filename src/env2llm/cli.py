"""CLI for env2llm — generate environment maps for LLM context."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from env2llm.bootstrap import ensure_environment_map
from env2llm.formats import SUPPORTED_FORMATS, normalize_format


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="env2llm",
        description="Generate environment maps (services, artifacts, env) for LLM decision-making.",
    )
    parser.add_argument(
        "project_dir",
        nargs="?",
        default=".",
        help="Project or example directory (default: cwd)",
    )
    parser.add_argument(
        "--project-id",
        default=None,
        help="Logical project id (default: directory name)",
    )
    parser.add_argument(
        "--format",
        "-f",
        default="doql.less",
        help=f"Output format: {', '.join(sorted(SUPPORTED_FORMATS))}",
    )
    parser.add_argument(
        "--no-merge",
        action="store_true",
        help="Do not merge observations from an existing registry file",
    )
    parser.add_argument(
        "--probe-desktop",
        action="store_true",
        help="Attach live desktop/GUI snapshot (wmctrl/xdotool; Linux)",
    )
    parser.add_argument(
        "--probe-mcp",
        action="store_true",
        help="Attach MCP tool catalog (auto for Koru projects when koruapi installed)",
    )
    parser.add_argument(
        "--probe-host",
        action="store_true",
        help="Attach live host snapshot (cron, ports, examples test report)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    fmt = normalize_format(args.format)
    path = ensure_environment_map(
        Path(args.project_dir),
        project_id=args.project_id,
        output_format=fmt,
        merge_existing=not args.no_merge,
        probe_desktop=args.probe_desktop,
        probe_mcp=args.probe_mcp,
        probe_host=args.probe_host or None,
    )
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
