"""Merge MCP tool catalogs (Koru, …) into SystemMapIR."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from env2llm.ir import (
    AccessGrantIR,
    CommandSchemaIR,
    FieldSpec,
    ProtocolSpec,
    ResourceSpecIR,
    RuntimeSpecIR,
    SystemMapIR,
)
from env2llm.probes.mcp import collect_mcp_tools, is_koru_project, koru_mcp_available
from env2llm.runtimes import resolve_command_runtime


def mcp_probe_enabled(
    *,
    explicit: bool | None = None,
    project_dir: Path | str | None = None,
) -> bool:
    if explicit is not None:
        return explicit
    token = os.environ.get("ENV2LLM_MCP_PROBE", "").strip().lower()
    if token in ("0", "false", "no"):
        return False
    if token in ("1", "true", "yes"):
        return True
    if project_dir is not None and is_koru_project(project_dir) and koru_mcp_available():
        return True
    return False


def _tool_aliases(tool_name: str) -> list[str]:
    aliases = [tool_name.replace("_", " ")]
    for prefix in ("koru_", "nlp2uri_", "env2llm_"):
        if tool_name.startswith(prefix):
            aliases.append(tool_name[len(prefix) :].replace("_", " "))
    return list(dict.fromkeys(alias for alias in aliases if alias))


def _fields_from_schema(schema: dict[str, Any]) -> list[FieldSpec]:
    props = schema.get("properties") or {}
    if not isinstance(props, dict):
        return []
    required = {str(name) for name in (schema.get("required") or [])}
    fields: list[FieldSpec] = []
    for name, spec in props.items():
        if not isinstance(spec, dict):
            continue
        fields.append(
            FieldSpec(
                name=str(name),
                required=str(name) in required,
                description=str(spec.get("description") or ""),
            )
        )
    return fields


def _ensure_runtime(ir: SystemMapIR, *, runtime_id: str, title: str) -> None:
    existing = ir.runtime(runtime_id)
    if existing is not None:
        existing.status = "available"  # type: ignore[assignment]
        return
    ir.runtimes.append(
        RuntimeSpecIR(
            id=runtime_id,
            kind="external",
            uri=f"mcp://{runtime_id.split(':', 1)[-1]}",
            roles=["mcp_tools", "orchestration"],
            status="available",
        )
    )


def _ensure_resource(ir: SystemMapIR, *, resource_id: str, title: str) -> None:
    if any(resource.id == resource_id for resource in ir.resources):
        return
    ir.resources.append(
        ResourceSpecIR(
            id=resource_id,
            title=title,
            connector="mcp",
            uri_patterns=[f"mcp://{resource_id.split(':', 1)[-1]}/**", "command://**"],
        )
    )


def _ensure_access(ir: SystemMapIR, *, agent: str, resource_id: str, actions: list[str]) -> None:
    if any(grant.agent == agent and grant.resource_area == resource_id for grant in ir.access):
        return
    ir.access.append(
        AccessGrantIR(
            agent=agent,
            resource_area=resource_id,
            actions=actions,
            effect="allow",
        )
    )


def _record_mcp_tool_aliases(ir: SystemMapIR, name: str, aliases: list[str]) -> None:
    for alias in aliases:
        ir.data[f"mcp.commands[{name}].alias.{alias.replace(' ', '_')}"] = alias
    ir.data[f"mcp.commands[{name}].aliases"] = aliases


def _command_from_mcp_tool(
    tool: dict[str, Any],
    *,
    runtime_id: str,
    server_id: str,
) -> CommandSchemaIR | None:
    name = str(tool.get("name") or "").strip()
    if not name:
        return None
    schema = tool.get("inputSchema") or {}
    if not isinstance(schema, dict):
        schema = {}
    return CommandSchemaIR(
        name=name,
        description=str(tool.get("description") or ""),
        runtime=runtime_id,
        protocol=ProtocolSpec(name="mcp", transport="stdio", endpoint=f"mcp://{server_id}"),
        fields=_fields_from_schema(schema),
    )


def _merge_mcp_tools(
    ir: SystemMapIR,
    tools: list[dict[str, Any]],
    *,
    runtime_id: str,
    server_id: str,
) -> list[str]:
    existing = {cmd.name for cmd in ir.commands}
    added: list[str] = []
    for tool in tools:
        command = _command_from_mcp_tool(tool, runtime_id=runtime_id, server_id=server_id)
        if command is None or command.name in existing:
            continue
        ir.commands.append(command)
        existing.add(command.name)
        added.append(command.name)
        _record_mcp_tool_aliases(ir, command.name, _tool_aliases(command.name))
    return added


def _record_mcp_catalog_metadata(
    ir: SystemMapIR,
    *,
    server_id: str,
    runtime_id: str,
    resource_id: str,
    added: list[str],
) -> None:
    _ensure_access(ir, agent="mcp-agent", resource_id=resource_id, actions=added)
    catalog = dict(ir.metadata.get("mcp_catalog") or {})
    catalog.update(
        {
            "server_id": server_id,
            "runtime_id": runtime_id,
            "tool_count": len(added),
            "tools": added,
        }
    )
    ir.metadata["mcp_catalog"] = catalog
    ir.data["mcp.tool_count"] = len(added)
    ir.data["mcp.server"] = server_id
    if "mcp_orchestration" not in ir.capabilities:
        ir.capabilities.append("mcp_orchestration")


def _resolve_mcp_command_runtimes(ir: SystemMapIR, added: list[str]) -> None:
    for cmd in ir.commands:
        if cmd.name in added and not cmd.runtime:
            cmd.runtime = resolve_command_runtime(cmd.name)


def apply_mcp_catalog(
    ir: SystemMapIR,
    tools: list[dict[str, Any]],
    *,
    server_id: str = "koru",
    runtime_id: str = "mcp:koru",
    resource_id: str = "mcp:koru",
) -> SystemMapIR:
    """Attach MCP tool schemas as command:// entries addressable via nlp2uri."""
    if not tools:
        return ir

    _ensure_runtime(ir, runtime_id=runtime_id, title=f"{server_id} MCP")
    _ensure_resource(
        ir,
        resource_id=resource_id,
        title=f"{server_id} MCP tool surface",
    )

    added = _merge_mcp_tools(
        ir,
        tools,
        runtime_id=runtime_id,
        server_id=server_id,
    )
    if added:
        _record_mcp_catalog_metadata(
            ir,
            server_id=server_id,
            runtime_id=runtime_id,
            resource_id=resource_id,
            added=added,
        )

    _resolve_mcp_command_runtimes(ir, added)
    return ir


def apply_mcp_probe(
    ir: SystemMapIR,
    *,
    enabled: bool | None = None,
    project_dir: Path | str | None = None,
) -> SystemMapIR:
    """Attach live MCP tool catalog when Koru (or future servers) are available."""
    root = Path(project_dir) if project_dir is not None else None
    if not mcp_probe_enabled(explicit=enabled, project_dir=root):
        return ir

    tools = collect_mcp_tools(root)
    if not tools:
        return ir

    server_id = "koru" if any(str(t.get("name", "")).startswith("koru_") for t in tools) else "mcp"
    return apply_mcp_catalog(ir, tools, server_id=server_id)
