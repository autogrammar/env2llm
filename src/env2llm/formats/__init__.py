"""Output format registry for environment maps."""

from __future__ import annotations

from typing import Callable

from env2llm.doql import DoqlTaskContext
from env2llm.ir import SystemMapIR

from .doql_less import render_doql_less
from .json_fmt import render_json
from .markdown import render_markdown
from .yaml_fmt import render_yaml

FormatRenderer = Callable[[SystemMapIR, DoqlTaskContext | None], str]

SUPPORTED_FORMATS: dict[str, FormatRenderer] = {
    "doql": render_doql_less,
    "doql.less": render_doql_less,
    "less": render_doql_less,
    "yaml": render_yaml,
    "yml": render_yaml,
    "json": render_json,
    "md": render_markdown,
    "markdown": render_markdown,
}

DEFAULT_FORMAT = "doql.less"


def normalize_format(name: str) -> str:
    token = (name or DEFAULT_FORMAT).strip().lower().lstrip(".")
    aliases = {
        "environment.doql.less": "doql",
        "environment": "doql",
        "doql-less": "doql",
    }
    return aliases.get(token, token)


def render_format(
    ir: SystemMapIR,
    fmt: str,
    *,
    ctx: DoqlTaskContext | None = None,
) -> str:
    key = normalize_format(fmt)
    renderer = SUPPORTED_FORMATS.get(key)
    if renderer is None:
        supported = ", ".join(sorted(SUPPORTED_FORMATS))
        raise ValueError(f"Unsupported format {fmt!r}; choose one of: {supported}")
    return renderer(ir, ctx)


def default_output_name(fmt: str) -> str:
    key = normalize_format(fmt)
    if key in {"doql", "doql.less", "less"}:
        return "environment.doql.less"
    return f"environment.{key}"
