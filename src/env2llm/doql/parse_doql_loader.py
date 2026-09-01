"""Load DoqlTaskContext from environment.doql.less files."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .models import DoqlTaskContext
from .parse_entities import (
    ACCESS_RE,
    ARTIFACT_RE,
    BLOCK_RE,
    COMMAND_RE,
    PROCESS_BOOL_FIELDS,
    PROCESS_FLOAT_FIELDS,
    PROCESS_INT_FIELDS,
    PROCESS_STRING_FIELDS,
    RESOURCE_RE,
    RUNTIME_RE,
    VALIDATION_RE,
    parse_access_body,
    parse_artifact_body,
    parse_block_body,
    parse_command_body,
    parse_resource_body,
    parse_runtime_body,
    parse_validation_body,
    split_csv,
)


def _apply_context_metadata(ctx: DoqlTaskContext, text: str) -> None:
    name_match = re.search(r'environment\[name="([^"]+)"\]', text)
    if name_match:
        ctx.example_name = name_match.group(1)
    gen_match = re.search(r"//\s*generated:\s*(\S+)", text)
    if gen_match:
        ctx.generated_at = gen_match.group(1)


def _apply_conversation_block(ctx: DoqlTaskContext, kv: dict[str, Any]) -> None:
    ctx.autofill = bool(kv.get("autofill", True))
    ctx.sync_auto_execute = bool(kv.get("sync_auto_execute", False))
    ctx.attachment_required = bool(kv.get("attachment_required", False))
    ctx.generate_invoice_if_missing = bool(kv.get("generate_invoice_if_missing", True))
    ctx.strict_pdf = bool(kv.get("strict_pdf", False))


def _apply_capabilities_block(ctx: DoqlTaskContext, kv: dict[str, Any]) -> None:
    if "actions" in kv:
        raw = str(kv["actions"]).strip('"')
        ctx.capabilities = [action.strip() for action in raw.split(",") if action.strip()]
        return
    ctx.capabilities = sorted(str(key) for key in kv)


def _apply_process_block(ctx: DoqlTaskContext, kv: dict[str, Any]) -> None:
    for key, attr in PROCESS_STRING_FIELDS.items():
        if key in kv:
            setattr(ctx.process, attr, str(kv[key]))
    for key, attr in PROCESS_FLOAT_FIELDS.items():
        if key in kv:
            setattr(ctx.process, attr, float(kv[key]))
    for key, attr in PROCESS_INT_FIELDS.items():
        if key in kv:
            setattr(ctx.process, attr, int(kv[key]))
    for key, attr in PROCESS_BOOL_FIELDS.items():
        if key in kv:
            setattr(ctx.process, attr, bool(kv[key]))


def _apply_process_access_block(ctx: DoqlTaskContext, kv: dict[str, Any]) -> None:
    if "agent" in kv:
        ctx.process.agent = str(kv["agent"])
    if "allow_areas" in kv:
        ctx.process.allow_resource_areas = split_csv(str(kv["allow_areas"]))
    if "deny_areas" in kv:
        ctx.process.deny_resource_areas = split_csv(str(kv["deny_areas"]))


def _apply_paths_block(ctx: DoqlTaskContext, kv: dict[str, Any]) -> None:
    if "read" in kv:
        ctx.process.paths_read = split_csv(str(kv["read"]))
    if "write" in kv:
        ctx.process.paths_write = split_csv(str(kv["write"]))


def _apply_context_block(ctx: DoqlTaskContext, block_type: str, kv: dict[str, Any]) -> None:
    if block_type == "environment":
        ctx.environment = {str(k): str(v) for k, v in kv.items()}
    elif block_type == "data":
        ctx.data.update(kv)
    elif block_type == "conversation":
        _apply_conversation_block(ctx, kv)
    elif block_type == "capabilities":
        _apply_capabilities_block(ctx, kv)
    elif block_type == "workflow_history":
        ctx.workflow_history = dict(kv)
    elif block_type == "process":
        _apply_process_block(ctx, kv)
    elif block_type == "process_access":
        _apply_process_access_block(ctx, kv)
    elif block_type == "paths":
        _apply_paths_block(ctx, kv)


def _append_artifact_blocks(ctx: DoqlTaskContext, text: str) -> None:
    for body in ARTIFACT_RE.findall(text):
        ctx.artifacts.append(parse_artifact_body(body))


def _append_command_blocks(ctx: DoqlTaskContext, text: str) -> None:
    for body in COMMAND_RE.findall(text):
        cmd = parse_command_body(body)
        if cmd.name:
            ctx.commands.append(cmd)


def _append_resource_blocks(ctx: DoqlTaskContext, text: str) -> None:
    for body in RESOURCE_RE.findall(text):
        res = parse_resource_body(body)
        if res.id:
            ctx.resources.append(res)


def _append_access_blocks(ctx: DoqlTaskContext, text: str) -> None:
    for body in ACCESS_RE.findall(text):
        grant = parse_access_body(body)
        if grant.agent:
            ctx.access.append(grant)


def _append_runtime_blocks(ctx: DoqlTaskContext, text: str) -> None:
    for body in RUNTIME_RE.findall(text):
        rt = parse_runtime_body(body)
        if rt.id:
            ctx.runtimes.append(rt)


def _append_validation_blocks(ctx: DoqlTaskContext, text: str) -> None:
    for body in VALIDATION_RE.findall(text):
        spec = parse_validation_body(body)
        if spec.code:
            ctx.validations.append(spec)


def _append_collection_blocks(ctx: DoqlTaskContext, text: str) -> None:
    _append_artifact_blocks(ctx, text)
    _append_command_blocks(ctx, text)
    _append_resource_blocks(ctx, text)
    _append_access_blocks(ctx, text)
    _append_runtime_blocks(ctx, text)
    _append_validation_blocks(ctx, text)


def load_doql_context(path: Path | str) -> DoqlTaskContext:
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    ctx = DoqlTaskContext()
    _apply_context_metadata(ctx, text)
    for block_type, body in BLOCK_RE.findall(text):
        _apply_context_block(ctx, block_type, parse_block_body(body))
    _append_collection_blocks(ctx, text)
    return ctx
