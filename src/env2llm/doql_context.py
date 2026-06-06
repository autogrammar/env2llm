"""Backward-compatible re-exports (nlp2dsl_sdk.doql_context shim)."""

from env2llm.doql import *  # noqa: F403
from env2llm.doql import (
    autofill_entities,
    collect_task_context,
    context_inline_payload,
    enrich_task_context_from_client,
    load_doql_context,
    merge_inline_context,
    render_doql_context,
    resolve_doql_context_path,
    write_doql_context,
)

__all__ = [
    "autofill_entities",
    "collect_task_context",
    "context_inline_payload",
    "enrich_task_context_from_client",
    "load_doql_context",
    "merge_inline_context",
    "render_doql_context",
    "resolve_doql_context_path",
    "write_doql_context",
]
